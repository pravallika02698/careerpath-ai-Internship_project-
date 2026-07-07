"""
CareerPath AI - Job Role Predictor
Predicts the most suitable job roles for a candidate based on their
resume skills using TF-IDF vectorisation and cosine similarity.
"""

import json
import os
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import JOB_ROLES_DB_PATH


# ─── Data Loading ─────────────────────────────────────────────────────────────

def _load_job_roles():
    """
    Load job roles from the database JSON file.

    Returns:
        list[dict]: List of job role dictionaries.
    """
    try:
        with open(JOB_ROLES_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Handle categorised format: {"category": [roles...], ...}
            roles = []
            for category, role_list in data.items():
                if isinstance(role_list, list):
                    for role in role_list:
                        if isinstance(role, dict):
                            role.setdefault("category", category)
                            roles.append(role)
            return roles
        return []
    except Exception as e:
        print(f"[Job Predictor] Failed to load job roles database: {e}")
        return []


def _build_role_document(role):
    """
    Build a text document from a job role's skills for TF-IDF vectorisation.

    Concatenates required_skills and preferred_skills into a single
    space-separated string.

    Args:
        role (dict): Job role dictionary.

    Returns:
        str: Combined skills text.
    """
    required = role.get("required_skills", [])
    preferred = role.get("preferred_skills", [])

    # Join all skill names into one text
    all_skills = required + preferred
    return " ".join(s.lower().replace("-", " ") for s in all_skills)


# ─── Main Prediction Function ────────────────────────────────────────────────

def predict_job_roles(parsed_resume, top_n=8):
    """
    Predict the best-matching job roles for a candidate.

    Uses TF-IDF vectorisation to convert both the resume skills and
    each job role's skill requirements into vectors, then computes
    cosine similarity to rank roles by relevance.

    Args:
        parsed_resume (dict): Parsed resume data from resume_parser.
        top_n (int): Number of top roles to return (default 8, range 5-8).

    Returns:
        list[dict]: Top matching roles sorted by similarity, each containing:
            - title (str)
            - match_percentage (float)
            - category (str)
            - required_skills (list[str])
            - description (str)
    """
    if not parsed_resume:
        return []

    top_n = max(5, min(top_n, 8))

    try:
        roles = _load_job_roles()
        if not roles:
            return []

        resume_skills = parsed_resume.get("skills", [])
        if not resume_skills:
            # Return top roles with 0% match if no skills detected
            results = []
            for role in roles[:top_n]:
                results.append({
                    "title": role.get("title") or role.get("name", "Unknown"),
                    "match_percentage": 0.0,
                    "category": role.get("category", "General"),
                    "required_skills": role.get("required_skills", []),
                    "description": role.get("description", ""),
                })
            return results

        # Build resume skills document
        resume_doc = " ".join(s.lower().replace("-", " ") for s in resume_skills)

        # Build role documents
        role_docs = []
        valid_roles = []
        for role in roles:
            doc = _build_role_document(role)
            if doc.strip():
                role_docs.append(doc)
                valid_roles.append(role)

        if not role_docs:
            return []

        # Combine: resume doc first, then all role docs
        all_docs = [resume_doc] + role_docs

        # TF-IDF vectorisation
        vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=r"(?u)\b\w[\w\+\#\.]*\b",  # Keep chars like C++, C#, .NET
            stop_words=None,  # Skills are domain-specific, don't remove stop words
        )
        tfidf_matrix = vectorizer.fit_transform(all_docs)

        # Cosine similarity: resume (index 0) vs all roles (index 1+)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Pair roles with similarity scores and sort descending
        role_scores = list(zip(valid_roles, similarities))
        role_scores.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results = []
        for role, sim_score in role_scores[:top_n]:
            match_pct = round(float(sim_score) * 100, 1)
            results.append({
                "title": role.get("title") or role.get("name", "Unknown"),
                "match_percentage": match_pct,
                "category": role.get("category", "General"),
                "required_skills": role.get("required_skills", []),
                "description": role.get("description", ""),
            })

        return results

    except Exception as e:
        print(f"[Job Predictor] Error during prediction: {e}")
        return []
