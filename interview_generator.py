"""
CareerPath AI - Company Recommender
Recommends companies that best match a candidate's skill profile
using TF-IDF vectorisation and cosine similarity.
"""

import json
import os
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import COMPANIES_DB_PATH


# ─── Data Loading ─────────────────────────────────────────────────────────────

def _load_companies():
    """
    Load companies from the database JSON file.

    Returns:
        list[dict]: List of company dictionaries.
    """
    try:
        with open(COMPANIES_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Handle categorised format: {"category": [companies...], ...}
            companies = []
            for category, company_list in data.items():
                if isinstance(company_list, list):
                    for company in company_list:
                        if isinstance(company, dict):
                            company.setdefault("domains", [category])
                            companies.append(company)
            return companies
        return []
    except Exception as e:
        print(f"[Company Recommender] Failed to load companies database: {e}")
        return []


def _build_company_document(company):
    """
    Build a text document from a company's required skills for TF-IDF.

    Joins all skill names into a single space-separated string.

    Args:
        company (dict): Company dictionary.

    Returns:
        str: Combined skills text.
    """
    skills = company.get("required_skills", [])
    if not skills:
        # Fallback to other possible fields
        skills = company.get("skills", []) or company.get("technologies", [])

    return " ".join(s.lower().replace("-", " ") for s in skills)


# ─── Main Recommendation Function ────────────────────────────────────────────

def recommend_companies(parsed_resume, top_n=15):
    """
    Recommend companies that best match the candidate's skills.

    Uses TF-IDF vectorisation to convert both the resume skills and
    each company's required skills into vectors, then computes
    cosine similarity to rank companies by relevance.

    Args:
        parsed_resume (dict): Parsed resume data from resume_parser.
        top_n (int): Number of top companies to return (default 15, range 10-15).

    Returns:
        list[dict]: Top matching companies sorted by similarity, each containing:
            - name (str): Short company name
            - full_name (str): Full company name
            - match_percentage (float): Similarity percentage
            - domains (list[str]): Company domain areas
            - career_url (str): Career page URL
            - required_skills (list[str]): Skills the company looks for
    """
    if not parsed_resume:
        return []

    top_n = max(10, min(top_n, 15))

    try:
        companies = _load_companies()
        if not companies:
            return []

        resume_skills = parsed_resume.get("skills", [])
        if not resume_skills:
            # Return top companies with 0% match if no skills detected
            results = []
            for company in companies[:top_n]:
                results.append({
                    "name": company.get("name") or company.get("short_name", "Unknown"),
                    "full_name": company.get("full_name") or company.get("name", "Unknown"),
                    "match_percentage": 0.0,
                    "domains": company.get("domains", []),
                    "career_url": company.get("career_url") or company.get("careers_url", ""),
                    "required_skills": company.get("required_skills", []),
                })
            return results

        # Build resume skills document
        resume_doc = " ".join(s.lower().replace("-", " ") for s in resume_skills)

        # Build company documents
        company_docs = []
        valid_companies = []
        for company in companies:
            doc = _build_company_document(company)
            if doc.strip():
                company_docs.append(doc)
                valid_companies.append(company)

        if not company_docs:
            return []

        # Combine: resume doc first, then all company docs
        all_docs = [resume_doc] + company_docs

        # TF-IDF vectorisation
        vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=r"(?u)\b\w[\w\+\#\.]*\b",  # Preserve C++, C#, .NET etc.
            stop_words=None,
        )
        tfidf_matrix = vectorizer.fit_transform(all_docs)

        # Cosine similarity: resume (index 0) vs all companies (index 1+)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Pair companies with similarity scores and sort descending
        company_scores = list(zip(valid_companies, similarities))
        company_scores.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results = []
        for company, sim_score in company_scores[:top_n]:
            match_pct = round(float(sim_score) * 100, 1)
            results.append({
                "name": company.get("name") or company.get("short_name", "Unknown"),
                "full_name": company.get("full_name") or company.get("name", "Unknown"),
                "match_percentage": match_pct,
                "domains": company.get("domains", []),
                "career_url": company.get("career_url") or company.get("careers_url", ""),
                "required_skills": company.get("required_skills", []),
            })

        return results

    except Exception as e:
        print(f"[Company Recommender] Error during recommendation: {e}")
        return []
