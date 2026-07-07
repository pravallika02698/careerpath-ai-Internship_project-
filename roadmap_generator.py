"""
CareerPath AI - Resume Scorer
Scores a parsed resume on five dimensions: skills, projects,
certifications, education, and format quality.
Generates targeted improvement suggestions for low-scoring areas.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import EDUCATION_SCORES


# ─── Individual Scoring Functions ─────────────────────────────────────────────

def _score_skills(parsed_resume):
    """
    Score skills (max 30 points).
    Formula: min(30, number_of_skills * 3)

    Args:
        parsed_resume (dict): Parsed resume data.

    Returns:
        int: Skills score (0-30).
    """
    num_skills = len(parsed_resume.get("skills", []))
    return min(30, num_skills * 3)


def _score_projects(parsed_resume):
    """
    Score projects (max 25 points).
    Formula: min(25, number_of_projects * 6.25)

    Args:
        parsed_resume (dict): Parsed resume data.

    Returns:
        float: Projects score (0-25).
    """
    num_projects = len(parsed_resume.get("projects", []))
    return min(25, num_projects * 6.25)


def _score_certifications(parsed_resume):
    """
    Score certifications (max 20 points).
    Formula: min(20, number_of_certifications * 5)

    Args:
        parsed_resume (dict): Parsed resume data.

    Returns:
        int: Certifications score (0-20).
    """
    num_certs = len(parsed_resume.get("certifications", []))
    return min(20, num_certs * 5)


def _score_education(parsed_resume):
    """
    Score education based on highest detected degree (max 15 points).
    Uses EDUCATION_SCORES from config for degree-level mapping.

    Args:
        parsed_resume (dict): Parsed resume data.

    Returns:
        int: Education score (0-15).
    """
    degrees = parsed_resume.get("education", [])
    if not degrees:
        return 3  # Minimum score if education is detected but degree unknown

    best_score = 0
    for degree in degrees:
        degree_lower = degree.lower().replace(".", "").replace(" ", "")

        # Try direct lookup
        if degree_lower in EDUCATION_SCORES:
            best_score = max(best_score, EDUCATION_SCORES[degree_lower])
            continue

        # Fuzzy match against keys
        for key, score in EDUCATION_SCORES.items():
            if key in degree_lower or degree_lower in key:
                best_score = max(best_score, score)
                break

        # Category-level matching
        if best_score == 0:
            degree_up = degree.upper()
            if any(kw in degree_up for kw in ["PHD", "DOCTOR"]):
                best_score = max(best_score, 15)
            elif any(kw in degree_up for kw in ["MASTER", "M.TECH", "MSC", "MBA", "MCA"]):
                best_score = max(best_score, 12)
            elif any(kw in degree_up for kw in ["BACHELOR", "B.TECH", "BSC", "BCA", "BE"]):
                best_score = max(best_score, 10)
            elif "DIPLOMA" in degree_up:
                best_score = max(best_score, 7)
            else:
                best_score = max(best_score, 3)

    return best_score if best_score > 0 else 3


def _score_format(parsed_resume):
    """
    Score resume format quality (max 10 points).
    Checks: email (+2), phone (+2), adequate length (+2),
            has sections (+2), has LinkedIn (+2).

    Args:
        parsed_resume (dict): Parsed resume data.

    Returns:
        int: Format score (0-10).
    """
    score = 0

    # Email presence (+2)
    if parsed_resume.get("email"):
        score += 2

    # Phone presence (+2)
    if parsed_resume.get("phone"):
        score += 2

    # Proper length (+2) - between 200 and 5000 words is reasonable
    raw_text = parsed_resume.get("raw_text", "")
    word_count = len(raw_text.split())
    if 200 <= word_count <= 5000:
        score += 2

    # Has sections (+2)
    sections = parsed_resume.get("sections", {})
    if len(sections) >= 2:
        score += 2

    # Has LinkedIn (+2)
    if parsed_resume.get("linkedin"):
        score += 2

    return score


# ─── Suggestion Generator ────────────────────────────────────────────────────

def _generate_suggestions(parsed_resume, breakdown):
    """
    Generate improvement suggestions based on scoring breakdown.

    Args:
        parsed_resume (dict): Parsed resume data.
        breakdown (dict): Score breakdown by category.

    Returns:
        list[str]: List of actionable improvement suggestions.
    """
    suggestions = []

    # Skills suggestions
    num_skills = len(parsed_resume.get("skills", []))
    if breakdown["skills"] < 15:
        suggestions.append(
            f"🔧 Add more relevant technical skills. You currently have {num_skills} "
            f"recognized skill(s). Aim for at least 8-10 to strengthen your profile."
        )
    elif breakdown["skills"] < 24:
        suggestions.append(
            f"🔧 Consider adding more niche or trending skills. You have {num_skills} "
            f"skills — adding 2-3 more specialized ones could boost your score."
        )

    # Projects suggestions
    num_projects = len(parsed_resume.get("projects", []))
    if breakdown["projects"] < 12:
        suggestions.append(
            f"📁 Include more projects on your resume. You have {num_projects} "
            f"project(s) listed. Aim for at least 3-4 well-described projects."
        )
    elif breakdown["projects"] < 19:
        suggestions.append(
            f"📁 You have {num_projects} project(s). Adding 1-2 more impactful "
            f"projects with measurable outcomes would improve your score."
        )

    # Certifications suggestions
    num_certs = len(parsed_resume.get("certifications", []))
    if breakdown["certifications"] < 10:
        suggestions.append(
            f"📜 Add relevant certifications. You have {num_certs} certification(s). "
            f"Industry-recognized certifications (AWS, Google, Microsoft, etc.) "
            f"significantly boost ATS scores."
        )

    # Education suggestions
    if breakdown["education"] < 10:
        suggestions.append(
            "🎓 Ensure your education section clearly lists your degree type "
            "(e.g., B.Tech, M.Sc, MBA) and institution name."
        )

    # Format suggestions
    if not parsed_resume.get("email"):
        suggestions.append("📧 Add your email address to the resume header.")
    if not parsed_resume.get("phone"):
        suggestions.append("📱 Include a phone number for easy contact.")
    if not parsed_resume.get("linkedin"):
        suggestions.append("🔗 Add your LinkedIn profile URL to improve professional visibility.")

    sections = parsed_resume.get("sections", {})
    if len(sections) < 3:
        suggestions.append(
            "📋 Structure your resume with clear section headers "
            "(Education, Skills, Experience, Projects, Certifications)."
        )

    raw_text = parsed_resume.get("raw_text", "")
    word_count = len(raw_text.split())
    if word_count < 200:
        suggestions.append(
            f"📝 Your resume is too short ({word_count} words). "
            f"Aim for 400-800 words with detailed descriptions."
        )
    elif word_count > 5000:
        suggestions.append(
            f"📝 Your resume is quite long ({word_count} words). "
            f"Consider trimming to 1-2 pages for better readability."
        )

    if not suggestions:
        suggestions.append("✅ Great job! Your resume is well-structured and comprehensive.")

    return suggestions


# ─── Main Scoring Function ───────────────────────────────────────────────────

def score_resume(parsed_resume):
    """
    Calculate a comprehensive resume score with category breakdown
    and improvement suggestions.

    Args:
        parsed_resume (dict): Parsed resume data from resume_parser.parse_resume().

    Returns:
        dict: {
            total_score (float): Overall score out of 100,
            breakdown (dict): {skills, projects, certifications, education, format},
            suggestions (list[str]): Improvement suggestions
        }
    """
    if not parsed_resume:
        return {
            "total_score": 0,
            "breakdown": {
                "skills": 0,
                "projects": 0,
                "certifications": 0,
                "education": 0,
                "format": 0,
            },
            "suggestions": ["⚠️ No resume data found. Please upload a valid PDF resume."],
        }

    try:
        skills_score = _score_skills(parsed_resume)
        projects_score = _score_projects(parsed_resume)
        certs_score = _score_certifications(parsed_resume)
        edu_score = _score_education(parsed_resume)
        format_score = _score_format(parsed_resume)

        breakdown = {
            "skills": round(skills_score, 2),
            "projects": round(projects_score, 2),
            "certifications": round(certs_score, 2),
            "education": round(edu_score, 2),
            "format": round(format_score, 2),
        }

        total_score = round(
            skills_score + projects_score + certs_score + edu_score + format_score, 2
        )
        total_score = min(100, total_score)

        suggestions = _generate_suggestions(parsed_resume, breakdown)

        return {
            "total_score": total_score,
            "breakdown": breakdown,
            "suggestions": suggestions,
        }

    except Exception as e:
        print(f"[Resume Scorer] Error during scoring: {e}")
        return {
            "total_score": 0,
            "breakdown": {
                "skills": 0,
                "projects": 0,
                "certifications": 0,
                "education": 0,
                "format": 0,
            },
            "suggestions": [f"⚠️ Scoring error: {str(e)}"],
        }
