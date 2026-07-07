"""
CareerPath AI - ATS Analyzer
Evaluates resume compatibility with Applicant Tracking Systems.
Scores based on keywords, skills match, format cleanliness,
section presence, and document length.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ATS_WEIGHTS, JOB_ROLES_DB_PATH


# ─── Industry Keywords ───────────────────────────────────────────────────────

INDUSTRY_KEYWORDS = [
    "developed", "implemented", "designed", "managed", "led",
    "built", "created", "optimized", "improved", "automated",
    "deployed", "integrated", "analyzed", "maintained", "collaborated",
    "achieved", "increased", "reduced", "delivered", "launched",
    "architected", "streamlined", "mentored", "coordinated", "resolved",
    "agile", "scrum", "ci/cd", "devops", "cloud",
    "api", "database", "testing", "debugging", "performance",
    "scalable", "microservices", "full-stack", "frontend", "backend",
    "machine learning", "data analysis", "algorithms", "data structures",
    "version control", "git", "restful", "sql", "nosql",
]

# Standard ATS-friendly section headers
STANDARD_SECTIONS = [
    "education", "skills", "experience", "projects",
    "certifications", "summary", "objective",
    "work experience", "professional experience",
    "technical skills", "achievements",
]


def _load_job_roles():
    """
    Load job roles database for skills matching.

    Returns:
        list[dict]: List of job role dictionaries.
    """
    try:
        with open(JOB_ROLES_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            roles = []
            for category, role_list in data.items():
                if isinstance(role_list, list):
                    roles.extend(role_list)
            return roles
        return []
    except Exception as e:
        print(f"[ATS Analyzer] Failed to load job roles: {e}")
        return []


def _get_role_skills(roles, target_role=None):
    """
    Get required skills for a target role. If no target_role is specified,
    returns a combined set of common skills across all roles.

    Args:
        roles (list): Job roles data.
        target_role (str|None): Optional target role title.

    Returns:
        set: Set of required skill names (lowercase).
    """
    if target_role:
        target_lower = target_role.lower().strip()
        for role in roles:
            title = (role.get("title") or role.get("name") or "").lower()
            if target_lower in title or title in target_lower:
                required = role.get("required_skills", [])
                preferred = role.get("preferred_skills", [])
                return set(s.lower() for s in required + preferred)

    # Fallback: aggregate common skills
    all_skills = set()
    for role in roles[:10]:  # Top 10 roles
        for skill in role.get("required_skills", []):
            all_skills.add(skill.lower())
    return all_skills


# ─── Scoring Components ──────────────────────────────────────────────────────

def _score_keywords(text):
    """
    Score presence of industry action keywords (max 25).

    Args:
        text (str): Resume text.

    Returns:
        tuple: (score, found_keywords, missing_keywords)
    """
    text_lower = text.lower()
    found = []
    missing = []

    for keyword in INDUSTRY_KEYWORDS:
        if keyword.lower() in text_lower:
            found.append(keyword)
        else:
            missing.append(keyword)

    # Score: proportion of keywords found, scaled to max points
    max_score = ATS_WEIGHTS["keywords"]
    ratio = len(found) / len(INDUSTRY_KEYWORDS) if INDUSTRY_KEYWORDS else 0
    score = round(ratio * max_score, 2)

    return score, found, missing


def _score_skills_match(resume_skills, target_role=None):
    """
    Score how well resume skills match target role requirements (max 25).

    Args:
        resume_skills (list): Skills extracted from resume.
        target_role (str|None): Optional target role.

    Returns:
        tuple: (score, matched_skills, missing_skills)
    """
    roles = _load_job_roles()
    role_skills = _get_role_skills(roles, target_role)

    if not role_skills:
        # Cannot score without role data — give partial credit
        return ATS_WEIGHTS["skills_match"] * 0.5, list(resume_skills), []

    resume_skills_lower = set(s.lower() for s in resume_skills)
    matched = role_skills & resume_skills_lower
    missing = role_skills - resume_skills_lower

    max_score = ATS_WEIGHTS["skills_match"]
    ratio = len(matched) / len(role_skills) if role_skills else 0
    score = round(ratio * max_score, 2)

    return score, sorted(matched), sorted(missing)


def _score_format(text):
    """
    Score format ATS-friendliness (max 20).
    Penalises special characters, checks for standard headers.

    Args:
        text (str): Resume text.

    Returns:
        tuple: (score, problems)
    """
    max_score = ATS_WEIGHTS["format"]
    score = max_score
    problems = []

    # Penalise excessive special characters (tables, graphics markers)
    special_chars = re.findall(r"[│┃┆╎║═─━┄┈┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬]", text)
    if len(special_chars) > 5:
        penalty = min(8, len(special_chars) // 2)
        score -= penalty
        problems.append("Resume contains table/box-drawing characters that ATS may not parse correctly")

    # Check for standard section headers
    text_lower = text.lower()
    has_standard_headers = False
    for section in STANDARD_SECTIONS:
        if section in text_lower:
            has_standard_headers = True
            break

    if not has_standard_headers:
        score -= 5
        problems.append("No standard section headers detected (Education, Experience, Skills, etc.)")

    # Check for excessive use of symbols that confuse ATS
    symbol_count = len(re.findall(r"[★☆●◆◇▪▫♦♠♣♥♢]", text))
    if symbol_count > 10:
        score -= 3
        problems.append("Excessive decorative symbols may confuse ATS parsers")

    # Check for images/graphics indicators
    if re.search(r"(?i)\[image\]|\[graphic\]|\[logo\]|\.png|\.jpg|\.jpeg", text):
        score -= 4
        problems.append("Images or graphics detected — ATS cannot read image content")

    return max(0, score), problems


def _score_sections(sections):
    """
    Score presence of key resume sections (max 15).

    Args:
        sections (dict): Detected section mapping.

    Returns:
        tuple: (score, present_sections, missing_sections)
    """
    max_score = ATS_WEIGHTS["sections"]
    required_sections = ["education", "skills", "experience", "projects"]

    present = []
    missing = []

    for section in required_sections:
        if section in sections:
            present.append(section)
        else:
            missing.append(section)

    ratio = len(present) / len(required_sections)
    score = round(ratio * max_score, 2)

    return score, present, missing


def _score_length(text):
    """
    Score resume length (max 15).
    Optimal: 400-1000 words = full marks.
    Too short (< 200) or too long (> 1500) = heavy penalty.

    Args:
        text (str): Resume text.

    Returns:
        tuple: (score, word_count, length_assessment)
    """
    max_score = ATS_WEIGHTS["length"]
    word_count = len(text.split())

    if 400 <= word_count <= 1000:
        score = max_score
        assessment = "Optimal length"
    elif 300 <= word_count < 400:
        score = max_score * 0.8
        assessment = "Slightly short — consider adding more detail"
    elif 1000 < word_count <= 1200:
        score = max_score * 0.8
        assessment = "Slightly long — consider condensing"
    elif 200 <= word_count < 300:
        score = max_score * 0.5
        assessment = "Too short — add more relevant content"
    elif 1200 < word_count <= 1500:
        score = max_score * 0.5
        assessment = "Too long — focus on key achievements"
    elif word_count < 200:
        score = max_score * 0.2
        assessment = "Very short — significantly more content needed"
    else:
        score = max_score * 0.3
        assessment = "Very long — strongly recommend trimming to 1-2 pages"

    return round(score, 2), word_count, assessment


# ─── Main ATS Analysis Function ──────────────────────────────────────────────

def analyze_ats(parsed_resume, target_role=None):
    """
    Perform comprehensive ATS compatibility analysis on a parsed resume.

    Args:
        parsed_resume (dict): Parsed resume data from resume_parser.
        target_role (str|None): Optional target job role for skills matching.

    Returns:
        dict: {
            ats_score (float): Overall ATS score out of 100,
            breakdown (dict): Score by category,
            problems (list[dict]): Issues found [{icon, message}],
            recommendations (list[dict]): Improvements [{icon, message}]
        }
    """
    if not parsed_resume:
        return {
            "ats_score": 0,
            "breakdown": {k: 0 for k in ATS_WEIGHTS},
            "problems": [{"icon": "❌", "message": "No resume data to analyse."}],
            "recommendations": [
                {"icon": "✅", "message": "Upload a valid PDF resume to begin."}
            ],
        }

    try:
        raw_text = parsed_resume.get("raw_text", "")
        skills = parsed_resume.get("skills", [])
        sections = parsed_resume.get("sections", {})

        # ── Score each dimension ──────────────────────────────────
        kw_score, kw_found, kw_missing = _score_keywords(raw_text)
        sm_score, sm_matched, sm_missing = _score_skills_match(skills, target_role)
        fmt_score, fmt_problems = _score_format(raw_text)
        sec_score, sec_present, sec_missing = _score_sections(sections)
        len_score, word_count, len_assessment = _score_length(raw_text)

        breakdown = {
            "keywords": round(kw_score, 2),
            "skills_match": round(sm_score, 2),
            "format": round(fmt_score, 2),
            "sections": round(sec_score, 2),
            "length": round(len_score, 2),
        }

        ats_score = round(sum(breakdown.values()), 2)
        ats_score = min(100, ats_score)

        # ── Build problems list ───────────────────────────────────
        problems = []

        for problem_msg in fmt_problems:
            problems.append({"icon": "❌", "message": problem_msg})

        for section in sec_missing:
            problems.append(
                {"icon": "❌", "message": f"Missing '{section.title()}' section"}
            )

        # Report top missing skills (up to 5)
        for skill in sm_missing[:5]:
            problems.append({"icon": "❌", "message": f"Missing skill: {skill}"})

        if word_count < 300:
            problems.append(
                {"icon": "❌", "message": f"Resume too short ({word_count} words). {len_assessment}"}
            )
        elif word_count > 1500:
            problems.append(
                {"icon": "❌", "message": f"Resume too long ({word_count} words). {len_assessment}"}
            )

        # ── Build recommendations list ────────────────────────────
        recommendations = []

        if sm_missing:
            top_missing = ", ".join(sm_missing[:5])
            recommendations.append(
                {"icon": "✅", "message": f"Add these skills: {top_missing}"}
            )

        if kw_score < ATS_WEIGHTS["keywords"] * 0.5:
            sample_kw = ", ".join(kw_missing[:5])
            recommendations.append(
                {"icon": "✅", "message": f"Use action verbs like: {sample_kw}"}
            )

        for section in sec_missing:
            recommendations.append(
                {"icon": "✅", "message": f"Add a '{section.title()}' section"}
            )

        if not parsed_resume.get("email"):
            recommendations.append(
                {"icon": "✅", "message": "Include your email address"}
            )

        if not parsed_resume.get("linkedin"):
            recommendations.append(
                {"icon": "✅", "message": "Add your LinkedIn profile URL"}
            )

        if 200 <= word_count < 400:
            recommendations.append(
                {"icon": "✅", "message": "Expand your resume with more detailed descriptions"}
            )

        if not recommendations:
            recommendations.append(
                {"icon": "✅", "message": "Your resume is well-optimised for ATS!"}
            )

        return {
            "ats_score": ats_score,
            "breakdown": breakdown,
            "problems": problems,
            "recommendations": recommendations,
        }

    except Exception as e:
        print(f"[ATS Analyzer] Error during analysis: {e}")
        return {
            "ats_score": 0,
            "breakdown": {k: 0 for k in ATS_WEIGHTS},
            "problems": [{"icon": "❌", "message": f"Analysis error: {str(e)}"}],
            "recommendations": [],
        }
