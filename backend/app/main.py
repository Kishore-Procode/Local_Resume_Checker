"""
FastAPI application entry point.
Loads the sentence-transformers model once at startup.
"""
import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import (
    ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, SEMANTIC_MODEL_NAME
)
from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, HealthResponse,
    JobAnalysisRequest, JobAnalysisResponse, ResumeUploadResponse
)
from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx
from app.services.analysis_service import run_analysis

# ── In-memory resume store (keyed by resume_id) ───────────────────────────────
# Stores {resume_id: {raw_text, filename, parsing_issues, ats_safety_score}}
_resume_store: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the sentence-transformers model on startup."""
    print(f"[startup] Loading semantic model: {SEMANTIC_MODEL_NAME}")
    try:
        from sentence_transformers import SentenceTransformer
        app.state.semantic_model = SentenceTransformer(SEMANTIC_MODEL_NAME)
        print(f"[startup] Semantic model loaded successfully.")
    except Exception as e:
        print(f"[startup] WARNING: Could not load semantic model: {e}")
        print("[startup] Analysis will proceed without semantic matching.")
        app.state.semantic_model = None

    yield

    # Cleanup on shutdown (nothing to do for in-memory store)
    print("[shutdown] Application shutting down.")


app = FastAPI(
    title="ATS Resume Checker API",
    description="Local ATS Resume Analysis — No external APIs required.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Custom Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Never expose Python stack traces to the frontend."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        semantic_model_loaded=app.state.semantic_model is not None,
        semantic_model_name=SEMANTIC_MODEL_NAME,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Resume Upload & Parse
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume (PDF or DOCX).
    Returns parse metadata and ATS safety analysis.
    File is stored in memory temporarily until analysis is requested.
    """
    # Validate file extension
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Please upload a PDF or DOCX file.",
        )

    # Read file bytes
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size_mb:.1f} MB). Maximum allowed: {MAX_FILE_SIZE_MB} MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Parse
    if suffix == ".pdf":
        parse_result = parse_pdf(file_bytes, filename)
    else:
        parse_result = parse_docx(file_bytes, filename)

    if parse_result["parsing_status"] == "failed":
        raise HTTPException(
            status_code=422,
            detail=parse_result["parsing_issues"][0].message if parse_result["parsing_issues"]
                   else "Failed to parse the resume.",
        )

    # Store in memory (not persisted to disk)
    resume_id = str(uuid.uuid4())
    _resume_store[resume_id] = {
        "raw_text": parse_result["raw_text"],
        "filename": filename,
        "parsing_issues": parse_result["parsing_issues"],
        "ats_safety_score": parse_result["ats_safety_score"],
    }

    return ResumeUploadResponse(
        resume_id=resume_id,
        filename=filename,
        file_size_kb=round(len(file_bytes) / 1024, 1),
        file_type=suffix.lstrip(".").upper(),
        page_count=parse_result.get("page_count"),
        text_length=parse_result["text_length"],
        word_count=parse_result["word_count"],
        parsing_status=parse_result["parsing_status"],
        parsing_issues=parse_result["parsing_issues"],
        ats_safety_score=parse_result["ats_safety_score"],
        message="Resume parsed successfully." if parse_result["parsing_status"] == "success"
                else "Resume parsed with warnings.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Job Description Analysis
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/job/analyze", response_model=JobAnalysisResponse)
async def analyze_job(request: JobAnalysisRequest):
    """Analyze a job description and extract requirements."""
    from app.analyzers.job_analyzer import analyze_job_description
    return analyze_job_description(request.jd_text)


# ─────────────────────────────────────────────────────────────────────────────
# Full Analysis
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Run full ATS analysis: resume vs job description.
    Requires a previously uploaded resume (resume_id from /api/resume/upload).
    """
    if request.resume_id not in _resume_store:
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload the resume first.",
        )

    resume_data = _resume_store[request.resume_id]

    if not resume_data["raw_text"].strip():
        raise HTTPException(
            status_code=422,
            detail="Resume text is empty. The file could not be parsed.",
        )

    if len(request.jd_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please provide a complete job description.",
        )

    try:
        result = run_analysis(
            resume_id=request.resume_id,
            raw_text=resume_data["raw_text"],
            jd_text=request.jd_text,
            parsing_issues=resume_data["parsing_issues"],
            ats_safety_score=resume_data["ats_safety_score"],
            filename=resume_data["filename"],
            semantic_model=app.state.semantic_model,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please check the uploaded file and job description.",
        )

    # Store analysis result for retrieval
    _resume_store[f"analysis_{result.analysis_id}"] = result.model_dump()

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Retrieve Saved Analysis
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve a previously computed analysis by ID."""
    key = f"analysis_{analysis_id}"
    if key not in _resume_store:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _resume_store[key]


# ─────────────────────────────────────────────────────────────────────────────
# Delete Resume (Privacy)
# ─────────────────────────────────────────────────────────────────────────────

@app.delete("/api/resume/{resume_id}")
async def delete_resume(resume_id: str):
    """Remove resume data from memory."""
    if resume_id in _resume_store:
        del _resume_store[resume_id]
    return {"message": "Resume data removed."}
