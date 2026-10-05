"""
Semantic Matcher: uses sentence-transformers for semantic similarity matching.
Loaded once at app startup and injected; gracefully degrades if unavailable.
"""
from typing import List, Optional, Tuple

import numpy as np

from app.config import SEMANTIC_THRESHOLD, SEMANTIC_TOP_K
from app.models.schemas import MatchedRequirement, MatchType, Confidence
from app.utils.text_utils import split_into_sentences


def compute_semantic_matches(
    unmatched: List[MatchedRequirement],
    resume_sentences: List[str],
    model,  # sentence_transformers.SentenceTransformer or None
) -> Tuple[List[MatchedRequirement], List[MatchedRequirement], float]:
    """
    Perform semantic matching for unmatched requirements.

    Args:
        unmatched: list of requirements not matched by keyword/fuzzy
        resume_sentences: list of resume sentences to compare against
        model: loaded SentenceTransformer model or None

    Returns:
        (newly_matched, still_unmatched, avg_semantic_score)
    """
    if not resume_sentences or not unmatched:
        return [], unmatched, 0.0

    try:
        req_texts = [r.requirement for r in unmatched]

        if model is not None:
            # Encode resume sentences with SentenceTransformer
            resume_embeddings = model.encode(resume_sentences, convert_to_numpy=True, show_progress_bar=False)
            req_embeddings = model.encode(req_texts, convert_to_numpy=True, show_progress_bar=False)

            # Normalize for cosine similarity
            resume_norms = np.linalg.norm(resume_embeddings, axis=1, keepdims=True)
            req_norms = np.linalg.norm(req_embeddings, axis=1, keepdims=True)
            resume_normalized = resume_embeddings / np.maximum(resume_norms, 1e-8)
            req_normalized = req_embeddings / np.maximum(req_norms, 1e-8)

            # Cosine similarity matrix: (n_reqs, n_sentences)
            similarity_matrix = req_normalized @ resume_normalized.T
        else:
            # Fallback: TF-IDF vector cosine similarity using scikit-learn
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            corpus = resume_sentences + req_texts
            tfidf_matrix = vectorizer.fit_transform(corpus)

            resume_tfidf = tfidf_matrix[:len(resume_sentences)]
            req_tfidf = tfidf_matrix[len(resume_sentences):]

            similarity_matrix = cosine_similarity(req_tfidf, resume_tfidf)

        newly_matched = []
        still_unmatched = []
        semantic_scores = []

        for i, req in enumerate(unmatched):
            sims = similarity_matrix[i]
            top_indices = np.argsort(sims)[::-1][:SEMANTIC_TOP_K]
            best_score = float(sims[top_indices[0]])

            if best_score >= SEMANTIC_THRESHOLD:
                evidence = resume_sentences[top_indices[0]]
                confidence = (
                    Confidence.HIGH if best_score >= 0.80
                    else Confidence.MEDIUM if best_score >= 0.70
                    else Confidence.LOW
                )
                semantic_scores.append(best_score)
                newly_matched.append(MatchedRequirement(
                    requirement=req.requirement,
                    category=req.category,
                    importance=req.importance,
                    match_type=MatchType.SEMANTIC,
                    confidence=confidence,
                    score=round(best_score, 3),
                    evidence_text=evidence,
                    evidence_snippet=evidence[:150],
                    semantic_score=round(best_score, 3),
                ))
            else:
                # Mark as WEAK if close to threshold
                if best_score >= SEMANTIC_THRESHOLD * 0.75:
                    evidence = resume_sentences[top_indices[0]]
                    still_unmatched.append(MatchedRequirement(
                        requirement=req.requirement,
                        category=req.category,
                        importance=req.importance,
                        match_type=MatchType.WEAK,
                        confidence=Confidence.LOW,
                        score=round(best_score, 3),
                        evidence_text=evidence,
                        evidence_snippet=evidence[:150],
                        semantic_score=round(best_score, 3),
                    ))
                else:
                    still_unmatched.append(req)

        avg_score = float(np.mean(semantic_scores)) if semantic_scores else 0.0
        return newly_matched, still_unmatched, avg_score

    except Exception as e:
        # Graceful fallback: return unmatched as-is
        return [], unmatched, 0.0


def get_resume_sentences(resume_text: str) -> List[str]:
    """Extract meaningful sentences from resume text for semantic encoding."""
    sentences = split_into_sentences(resume_text)
    # Filter out very short or header-like lines
    return [s for s in sentences if len(s.split()) >= 5 and len(s) < 300]


def compute_overall_semantic_score(
    all_matched: List[MatchedRequirement],
    total_requirements: int,
    model,
) -> float:
    """
    Compute an overall semantic coverage score.
    Returns 0.0 if model not available.
    """
    if model is None or total_requirements == 0:
        return 0.0

    semantic_matches = [r for r in all_matched if r.match_type == MatchType.SEMANTIC]
    if not semantic_matches:
        return 0.0

    avg_similarity = np.mean([r.semantic_score or 0 for r in semantic_matches])
    coverage = len(semantic_matches) / total_requirements
    return float(avg_similarity * coverage)
