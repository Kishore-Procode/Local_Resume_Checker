# Local ATS Resume Checker & Job Match Analyzer

A complete, production-quality **ATS Resume Checker & Job Match Analyzer** web application that runs **100% locally on your machine**.

> 🔒 **100% Local & Private:** No API keys, no OpenAI, no Gemini, no Claude, no OpenRouter, or external LLM APIs required. All resume parsing, keyword extraction, and semantic matching run locally using open-source Python NLP libraries and local embedding models.

---

## 🎯 Key Features

- **📄 Document Parsing:** Supports PDF (`PyMuPDF`) and DOCX (`python-docx`) format parsing.
- **🔍 Hard & Soft Skill Extractor:** Taxonomy-driven skill extractor with alias resolution and fuzzy string matching (`RapidFuzz`).
- **🧠 Local Semantic Similarity:** Uses `sentence-transformers` (`all-MiniLM-L6-v2`) and `scikit-learn` cosine similarity to measure contextual alignment between resume experience and job descriptions.
- **🛡️ ATS Readability & Formatting Check:** Scans for non-standard tables, text boxes, page count, word count, section header completeness, and formatting warnings.
- **📊 8-Factor Weighted Scoring:**
  1. Exact Skill Match (25%)
  2. Semantic Context Match (25%)
  3. ATS Format Readability (15%)
  4. Hard Requirement Coverage (10%)
  5. Action Verb Density (10%)
  6. Bullet Point Quantification (5%)
  7. Section Completeness (5%)
  8. Phrase Repetition (5%)
- **🎨 Sleek Dark Blue Interface:** Modern React frontend built with Vite, Tailwind CSS, Lucide icons, and Recharts visualization charts.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React.js + Vite
- **Styling:** Tailwind CSS (Dark Blue Midnight Theme)
- **Icons:** Lucide React
- **Charts:** Recharts
- **HTTP Client:** Axios
- **Notifications:** React Hot Toast

### Backend
- **Framework:** Python + FastAPI + Uvicorn
- **Parsing:** PyMuPDF (`fitz`), python-docx
- **NLP & Text Processing:** spaCy, RapidFuzz, Regular Expressions
- **Semantic Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`), `scikit-learn`
- **Validation:** Pydantic v2

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.10+) & pip

### 1. Clone the Repository
```bash
git clone https://github.com/Kishore-Procode/Local_Resume_Checker.git
cd Local_Resume_Checker
```

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI backend will be available at: **http://127.0.0.1:8000** (Swagger API docs at `http://127.0.0.1:8000/docs`).

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
The Vite frontend will be available at: **http://localhost:5173/**

---

## 🔒 Privacy Guarantee
All processing is performed locally on your device. No candidate data, resume text, or job descriptions are transmitted over the internet or saved to external servers.

---

## 📜 License
MIT License. Free for personal and commercial use.
