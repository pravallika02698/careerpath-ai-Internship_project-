"""
CareerPath AI - Salary Predictor Module

Predicts salary ranges for target roles based on experience level,
skill count, education, and certifications with adjustment multipliers.
"""

import json
import os
import sys

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SALARY_DATA_PATH


# ─── Experience Level Thresholds ─────────────────────────
EXPERIENCE_THRESHOLDS = {
    "fresher": {"min": 0, "max": 1},
    "mid": {"min": 2, "max": 5},
    "senior": {"min": 6, "max": 99},
}

# ─── Bonus Multipliers ──────────────────────────────────
SKILL_BONUS_TIERS = {
    "low": {"max_skills": 5, "multiplier": 1.0, "label": "Basic skill set"},
    "medium": {"max_skills": 10, "multiplier": 1.10, "label": "Moderate skill set (+10%)"},
    "high": {"max_skills": 15, "multiplier": 1.20, "label": "Strong skill set (+20%)"},
    "expert": {"max_skills": 999, "multiplier": 1.30, "label": "Expert skill set (+30%)"},
}

CERTIFICATION_BONUS = {
    0: {"multiplier": 1.0, "label": "No certifications"},
    1: {"multiplier": 1.05, "label": "1 certification (+5%)"},
    2: {"multiplier": 1.08, "label": "2 certifications (+8%)"},
    3: {"multiplier": 1.12, "label": "3+ certifications (+12%)"},
}

EDUCATION_BONUS = {
    "high_school": {"multiplier": 0.90, "label": "High School (-10%)"},
    "diploma": {"multiplier": 0.95, "label": "Diploma (-5%)"},
    "bachelors": {"multiplier": 1.0, "label": "Bachelor's (baseline)"},
    "masters": {"multiplier": 1.10, "label": "Master's (+10%)"},
    "phd": {"multiplier": 1.20, "label": "PhD (+20%)"},
}


def _load_salary_data():
    """Load the salary data from JSON file.

    Returns:
        dict: Salary data, or empty dict if file not found.
    """
    try:
        with open(SALARY_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Salary data not found at: {SALARY_DATA_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in salary data: {SALARY_DATA_PATH}")
        return {}


def _determine_experience_level(experience_years):
    """Determine the experience level category from years of experience.

    Args:
        experience_years (int): Number of years of experience.

    Returns:
        str: Experience level ('fresher', 'mid', or 'senior').
    """
    experience_years = max(0, experience_years)

    for level, thresholds in EXPERIENCE_THRESHOLDS.items():
        if thresholds["min"] <= experience_years <= thresholds["max"]:
            return level

    return "senior"


def _get_skill_multiplier(skills_count):
    """Get the salary multiplier based on number of skills.

    Args:
        skills_count (int): Number of skills the candidate possesses.

    Returns:
        tuple: (multiplier: float, label: str) for the skill tier.
    """
    skills_count = max(0, skills_count)

    for tier_name, tier_data in SKILL_BONUS_TIERS.items():
        if skills_count <= tier_data["max_skills"]:
            return tier_data["multiplier"], tier_data["label"]

    # Fallback to expert tier
    return SKILL_BONUS_TIERS["expert"]["multiplier"], SKILL_BONUS_TIERS["expert"]["label"]


def _get_certification_multiplier(certifications_count):
    """Get the salary multiplier based on number of certifications.

    Args:
        certifications_count (int): Number of certifications.

    Returns:
        tuple: (multiplier: float, label: str) for the certification bonus.
    """
    certifications_count = max(0, certifications_count)

    if certifications_count >= 3:
        bonus = CERTIFICATION_BONUS[3]
    elif certifications_count in CERTIFICATION_BONUS:
        bonus = CERTIFICATION_BONUS[certifications_count]
    else:
        bonus = CERTIFICATION_BONUS[0]

    return bonus["multiplier"], bonus["label"]


def _get_education_multiplier(education_level):
    """Get the salary multiplier based on education level.

    Args:
        education_level (str): Education level of the candidate.

    Returns:
        tuple: (multiplier: float, label: str) for the education bonus.
    """
    edu_lower = education_level.strip().lower() if education_level else "bachelors"

    # Map common variations to standard keys
    edu_mapping = {
        "phd": "phd", "doctorate": "phd", "ph.d": "phd", "ph.d.": "phd",
        "masters": "masters", "master": "masters", "mtech": "masters",
        "m.tech": "masters", "msc": "masters", "m.sc": "masters",
        "mba": "masters", "m.s": "masters", "ms": "masters",
        "bachelors": "bachelors", "bachelor": "bachelors", "btech": "bachelors",
        "b.tech": "bachelors", "bsc": "bachelors", "b.sc": "bachelors",
        "bca": "bachelors", "be": "bachelors", "b.e": "bachelors",
        "bs": "bachelors", "b.s": "bachelors",
        "diploma": "diploma",
        "high_school": "high_school", "high school": "high_school",
        "12th": "high_school", "10+2": "high_school",
    }

    standard_level = edu_mapping.get(edu_lower, "bachelors")
    bonus = EDUCATION_BONUS.get(standard_level, EDUCATION_BONUS["bachelors"])
    return bonus["multiplier"], bonus["label"]


def _find_role_salary(salary_data, role_name, experience_level):
    """Find the base salary range for a role and experience level.

    Args:
        salary_data (dict): The full salary database.
        role_name (str): The role title to search for.
        experience_level (str): The experience level ('fresher', 'mid', 'senior').

    Returns:
        dict or None: Base salary range with 'min' and 'max', or None.
    """
    role_lower = role_name.strip().lower()

    # Handle different database structures
    salaries = salary_data.get("salaries", salary_data.get("roles", salary_data))

    if isinstance(salaries, list):
        for entry in salaries:
            entry_role = entry.get("role", entry.get("title", "")).strip().lower()
            if entry_role == role_lower or role_lower in entry_role or entry_role in role_lower:
                # Try to get experience-specific salary
                exp_data = entry.get(experience_level, entry.get("salary", {}))
                if isinstance(exp_data, dict):
                    return {
                        "min": exp_data.get("min", exp_data.get("low", 0)),
                        "max": exp_data.get("max", exp_data.get("high", 0)),
                    }
                # If salary is a flat range
                salary_range = entry.get("salary_range", entry.get("range", {}))
                if isinstance(salary_range, dict):
                    return {
                        "min": salary_range.get("min", salary_range.get("low", 0)),
                        "max": salary_range.get("max", salary_range.get("high", 0)),
                    }

    elif isinstance(salaries, dict):
        for key, value in salaries.items():
            if key.lower() == role_lower or role_lower in key.lower():
                if isinstance(value, dict):
                    exp_data = value.get(experience_level, value)
                    return {
                        "min": exp_data.get("min", exp_data.get("low", 0)),
                        "max": exp_data.get("max", exp_data.get("high", 0)),
                    }

    return None


def predict_salary(predicted_roles, skills_count, education_level,
                   certifications_count, experience_years):
    """Predict the salary range for a candidate based on multiple factors.

    Computes an adjusted salary range by applying multipliers for skills,
    certifications, and education level on top of the base salary for the
    top predicted role and experience level.

    Args:
        predicted_roles (list): List of predicted role names (top role used).
        skills_count (int): Number of skills the candidate has.
        education_level (str): Candidate's highest education level.
        certifications_count (int): Number of certifications held.
        experience_years (int): Years of professional experience.

    Returns:
        dict: Salary prediction containing:
            - role (str): The role used for prediction
            - experience_level (str): Determined experience level
            - base_range (dict): Base salary range {min, max}
            - adjusted_range (dict): Adjusted salary range {min, max}
            - unit (str): Currency unit ('LPA')
            - factors (list[dict]): Adjustment factors applied
    """
    if not predicted_roles:
        return {
            "role": "Unknown",
            "experience_level": "fresher",
            "base_range": {"min": 0, "max": 0},
            "adjusted_range": {"min": 0, "max": 0},
            "unit": "LPA",
            "factors": [],
            "error": "No predicted roles provided.",
        }

    # Use the top predicted role
    top_role = predicted_roles[0] if isinstance(predicted_roles, list) else str(predicted_roles)

    # Determine experience level
    experience_level = _determine_experience_level(experience_years)

    # Load salary data
    salary_data = _load_salary_data()

    # Get base salary range
    base_range = _find_role_salary(salary_data, top_role, experience_level)

    if not base_range:
        # Provide default ranges if role not found
        default_ranges = {
            "fresher": {"min": 3.0, "max": 6.0},
            "mid": {"min": 6.0, "max": 15.0},
            "senior": {"min": 15.0, "max": 35.0},
        }
        base_range = default_ranges.get(experience_level, {"min": 3.0, "max": 6.0})

    # Calculate multipliers
    skill_mult, skill_label = _get_skill_multiplier(skills_count)
    cert_mult, cert_label = _get_certification_multiplier(certifications_count)
    edu_mult, edu_label = _get_education_multiplier(education_level)

    # Combined multiplier
    combined_multiplier = skill_mult * cert_mult * edu_mult

    # Apply adjustments
    adjusted_min = round(base_range["min"] * combined_multiplier, 2)
    adjusted_max = round(base_range["max"] * combined_multiplier, 2)

    # Build factors list
    factors = [
        {
            "name": "Experience Level",
            "impact": f"{experience_level.capitalize()} ({experience_years} years)",
        },
        {
            "name": "Skills",
            "impact": skill_label,
        },
        {
            "name": "Certifications",
            "impact": cert_label,
        },
        {
            "name": "Education",
            "impact": edu_label,
        },
    ]

    return {
        "role": top_role,
        "experience_level": experience_level,
        "base_range": {
            "min": base_range["min"],
            "max": base_range["max"],
        },
        "adjusted_range": {
            "min": adjusted_min,
            "max": adjusted_max,
        },
        "unit": "LPA",
        "factors": factors,
    }
