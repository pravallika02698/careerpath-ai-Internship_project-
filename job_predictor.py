"""
CareerPath AI - Interview Question Generator Module

Generates interview preparation questions organized by skill and difficulty
level (beginner, intermediate, advanced) from the questions database.
"""

import json
import os
import sys

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVIEW_QUESTIONS_PATH


def _load_interview_questions():
    """Load the interview questions database from JSON file.

    Returns:
        dict: Interview questions data, or empty dict if file not found.
    """
    try:
        with open(INTERVIEW_QUESTIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Interview questions database not found at: {INTERVIEW_QUESTIONS_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in interview questions database: {INTERVIEW_QUESTIONS_PATH}")
        return {}


def _generate_generic_questions(skill):
    """Generate generic interview questions for a skill not found in the database.

    Provides a set of universally applicable questions that cover
    fundamentals, best practices, and practical application.

    Args:
        skill (str): The skill name.

    Returns:
        dict: Questions organized by difficulty level.
    """
    skill_title = skill.strip().title()

    return {
        "beginner": [
            f"What is {skill_title} and why is it important?",
            f"Explain the fundamentals of {skill_title}.",
            f"What are the key concepts a beginner should know about {skill_title}?",
            f"How would you describe {skill_title} to someone new to the field?",
            f"What are the common use cases for {skill_title}?",
        ],
        "intermediate": [
            f"What are the best practices for {skill_title}?",
            f"Describe a project where you used {skill_title} effectively.",
            f"What are common challenges when working with {skill_title} and how do you overcome them?",
            f"Compare {skill_title} with its alternatives. What are the trade-offs?",
            f"How do you stay updated with the latest developments in {skill_title}?",
        ],
        "advanced": [
            f"How would you architect a large-scale system using {skill_title}?",
            f"What are the performance optimization techniques for {skill_title}?",
            f"Explain advanced patterns or techniques in {skill_title}.",
            f"How would you debug a complex issue involving {skill_title}?",
            f"What are the security considerations when using {skill_title}?",
        ],
    }


def _find_skill_questions(questions_data, skill):
    """Find questions for a specific skill in the database.

    Performs case-insensitive matching to find questions associated
    with the given skill.

    Args:
        questions_data (dict): The full interview questions database.
        skill (str): The skill name to search for.

    Returns:
        dict or None: Questions organized by difficulty, or None if not found.
    """
    skill_lower = skill.strip().lower()

    # Handle different database structures
    questions_list = questions_data.get("questions", questions_data)

    if isinstance(questions_list, dict):
        # Structure: {"python": {"beginner": [...], ...}, ...}
        for key, value in questions_list.items():
            if key.lower() == skill_lower or skill_lower in key.lower():
                if isinstance(value, dict):
                    return {
                        "beginner": value.get("beginner", value.get("easy", [])),
                        "intermediate": value.get("intermediate", value.get("medium", [])),
                        "advanced": value.get("advanced", value.get("hard", [])),
                    }

    elif isinstance(questions_list, list):
        # Structure: [{"skill": "python", "questions": {...}}, ...]
        for entry in questions_list:
            entry_skill = entry.get("skill", entry.get("name", "")).strip().lower()
            if entry_skill == skill_lower or skill_lower in entry_skill:
                qs = entry.get("questions", entry)
                return {
                    "beginner": qs.get("beginner", qs.get("easy", [])),
                    "intermediate": qs.get("intermediate", qs.get("medium", [])),
                    "advanced": qs.get("advanced", qs.get("hard", [])),
                }

    return None


def generate_interview_questions(skills):
    """Generate interview questions for a list of skills.

    For each skill, pulls questions from the database organized by difficulty.
    If a skill isn't found in the database, generates generic but relevant
    interview questions.

    Args:
        skills (list[str]): List of skill names to generate questions for.

    Returns:
        dict: Interview preparation data containing:
            - total_questions (int): Total number of questions generated
            - skills_covered (int): Number of skills with questions
            - questions (list[dict]): Questions per skill, each containing:
                - skill (str): Skill name
                - beginner (list[str]): Beginner-level questions
                - intermediate (list[str]): Intermediate-level questions
                - advanced (list[str]): Advanced-level questions
    """
    if not skills:
        return {
            "total_questions": 0,
            "skills_covered": 0,
            "questions": [],
        }

    # Load interview questions database
    questions_data = _load_interview_questions()

    all_questions = []
    total_count = 0

    for skill in skills:
        if not skill or not skill.strip():
            continue

        skill_name = skill.strip()

        # Try to find questions in the database
        db_questions = _find_skill_questions(questions_data, skill_name)

        if db_questions:
            questions_entry = {
                "skill": skill_name,
                "beginner": db_questions.get("beginner", []),
                "intermediate": db_questions.get("intermediate", []),
                "advanced": db_questions.get("advanced", []),
            }
        else:
            # Generate generic questions for skills not in the database
            generic = _generate_generic_questions(skill_name)
            questions_entry = {
                "skill": skill_name,
                "beginner": generic["beginner"],
                "intermediate": generic["intermediate"],
                "advanced": generic["advanced"],
            }

        # Count total questions for this skill
        skill_total = (
            len(questions_entry["beginner"])
            + len(questions_entry["intermediate"])
            + len(questions_entry["advanced"])
        )
        total_count += skill_total

        all_questions.append(questions_entry)

    return {
        "total_questions": total_count,
        "skills_covered": len(all_questions),
        "questions": all_questions,
    }
