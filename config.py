"""
CareerPath AI - Configuration Constants
"""
import os

# ─── Paths ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ─── Data File Paths ─────────────────────────────────────
SKILLS_DB_PATH = os.path.join(DATA_DIR, "skills_database.json")
JOB_ROLES_DB_PATH = os.path.join(DATA_DIR, "job_roles_database.json")
COMPANIES_DB_PATH = os.path.join(DATA_DIR, "companies_database.json")
INTERVIEW_QUESTIONS_PATH = os.path.join(DATA_DIR, "interview_questions.json")
COURSES_DB_PATH = os.path.join(DATA_DIR, "courses_database.json")
SALARY_DATA_PATH = os.path.join(DATA_DIR, "salary_data.json")

# ─── Resume Scoring Weights ──────────────────────────────
SCORING_WEIGHTS = {
    "skills": 30,
    "projects": 25,
    "certifications": 20,
    "education": 15,
    "format": 10,
}

# ─── Education Scoring ───────────────────────────────────
EDUCATION_SCORES = {
    "phd": 15,
    "doctorate": 15,
    "masters": 12,
    "mtech": 12,
    "msc": 12,
    "mba": 12,
    "bachelors": 10,
    "btech": 10,
    "bsc": 10,
    "bca": 10,
    "be": 10,
    "diploma": 7,
    "associate": 5,
    "high_school": 3,
}

# ─── ATS Scoring Weights ─────────────────────────────────
ATS_WEIGHTS = {
    "keywords": 25,
    "skills_match": 25,
    "format": 20,
    "sections": 15,
    "length": 15,
}

# ─── App Theme Colors ────────────────────────────────────
THEME = {
    "primary": "#6C63FF",
    "secondary": "#FF6584",
    "accent": "#43E97B",
    "bg_dark": "#0F0F1A",
    "bg_card": "#1A1A2E",
    "bg_card_hover": "#252540",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0C8",
    "gradient_start": "#6C63FF",
    "gradient_end": "#43E97B",
    "success": "#43E97B",
    "warning": "#FFB347",
    "danger": "#FF6584",
    "info": "#63B3ED",
}

# ─── Streamlit Page Config ───────────────────────────────
PAGE_CONFIG = {
    "page_title": "CareerPath AI",
    "page_icon": "🚀",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ─── Experience Level Thresholds ─────────────────────────
EXPERIENCE_LEVELS = {
    "fresher": {"min_years": 0, "max_years": 1},
    "junior": {"min_years": 1, "max_years": 3},
    "mid": {"min_years": 3, "max_years": 6},
    "senior": {"min_years": 6, "max_years": 10},
    "lead": {"min_years": 10, "max_years": 99},
}
