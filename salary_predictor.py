"""
CareerPath AI - Learning Roadmap Generator Module

Generates a structured, month-by-month learning roadmap for missing skills,
sorted by priority, with course recommendations from the courses database.
"""

import json
import os
import sys

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COURSES_DB_PATH


# ─── Priority Ordering ────────────────────────────────────
PRIORITY_ORDER = {
    "Critical": 0,
    "Important": 1,
    "Nice-to-have": 2,
}

# Default skills per month allocation
SKILLS_PER_MONTH = 2


def _load_courses():
    """Load the courses database from JSON file.

    Returns:
        dict: Courses data, or empty dict if file not found.
    """
    try:
        with open(COURSES_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Courses database not found at: {COURSES_DB_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in courses database: {COURSES_DB_PATH}")
        return {}


def _find_courses_for_skill(courses_data, skill_name):
    """Find course recommendations for a given skill.

    Searches the courses database for matching courses using
    case-insensitive partial matching.

    Args:
        courses_data (dict): The full courses database.
        skill_name (str): The skill to find courses for.

    Returns:
        list[dict]: List of matching courses with name, platform, url, type.
    """
    matched_courses = []
    skill_lower = skill_name.strip().lower()

    # Handle different database structures
    courses_list = courses_data.get("courses", [])
    if isinstance(courses_list, dict):
        # If courses are organized by skill/category
        for key, courses in courses_list.items():
            if skill_lower in key.lower() or key.lower() in skill_lower:
                if isinstance(courses, list):
                    for course in courses:
                        matched_courses.append({
                            "name": course.get("name", course.get("title", "Unknown Course")),
                            "platform": course.get("platform", "Online"),
                            "url": course.get("url", course.get("link", "#")),
                            "type": course.get("type", course.get("level", "Course")),
                        })
    elif isinstance(courses_list, list):
        # If courses are a flat list
        for course in courses_list:
            course_skills = course.get("skills", [])
            course_tags = course.get("tags", [])
            course_name = course.get("name", course.get("title", "")).lower()

            # Check if skill matches course skills, tags, or name
            skills_lower = [s.lower() for s in course_skills]
            tags_lower = [t.lower() for t in course_tags]

            if (skill_lower in skills_lower or
                    skill_lower in tags_lower or
                    skill_lower in course_name or
                    any(skill_lower in s for s in skills_lower)):
                matched_courses.append({
                    "name": course.get("name", course.get("title", "Unknown Course")),
                    "platform": course.get("platform", "Online"),
                    "url": course.get("url", course.get("link", "#")),
                    "type": course.get("type", course.get("level", "Course")),
                })

    # If no courses found, provide generic recommendations
    if not matched_courses:
        matched_courses = [
            {
                "name": f"{skill_name} - Complete Guide",
                "platform": "Udemy",
                "url": f"https://www.udemy.com/topic/{skill_name.replace(' ', '-').lower()}/",
                "type": "Course",
            },
            {
                "name": f"Learn {skill_name}",
                "platform": "Coursera",
                "url": f"https://www.coursera.org/search?query={skill_name.replace(' ', '%20')}",
                "type": "Course",
            },
        ]

    return matched_courses


def _sort_by_priority(missing_skills):
    """Sort missing skills by priority order.

    Args:
        missing_skills (list[dict]): List of skills with 'skill' and 'priority' keys.

    Returns:
        list[dict]: Sorted skills list (Critical first, then Important, then Nice-to-have).
    """
    return sorted(
        missing_skills,
        key=lambda x: PRIORITY_ORDER.get(x.get("priority", "Nice-to-have"), 99)
    )


def generate_roadmap(missing_skills, skills_per_month=SKILLS_PER_MONTH):
    """Generate a month-by-month learning roadmap for missing skills.

    Creates a structured learning plan that distributes skills across months,
    prioritizing Critical skills first, with course recommendations for each skill.

    Args:
        missing_skills (list[dict]): List of missing skills, each containing:
            - skill (str): The skill name
            - priority (str): 'Critical', 'Important', or 'Nice-to-have'
        skills_per_month (int, optional): Number of skills to learn per month.
            Defaults to 2.

    Returns:
        dict: Roadmap data containing:
            - total_months (int): Total months in the learning plan
            - roadmap (list[dict]): Month-by-month plan with skills and courses
    """
    if not missing_skills:
        return {
            "total_months": 0,
            "roadmap": [],
        }

    # Sort skills by priority
    sorted_skills = _sort_by_priority(missing_skills)

    # Load courses database
    courses_data = _load_courses()

    # Build the month-by-month roadmap
    roadmap = []
    current_month = 1

    for i in range(0, len(sorted_skills), skills_per_month):
        month_skills = sorted_skills[i:i + skills_per_month]
        month_entry = {
            "month": current_month,
            "skills": [],
        }

        for skill_info in month_skills:
            skill_name = skill_info.get("skill", "")
            priority = skill_info.get("priority", "Nice-to-have")

            # Find relevant courses
            courses = _find_courses_for_skill(courses_data, skill_name)

            month_entry["skills"].append({
                "name": skill_name,
                "priority": priority,
                "courses": courses,
            })

        roadmap.append(month_entry)
        current_month += 1

    total_months = len(roadmap)

    return {
        "total_months": total_months,
        "roadmap": roadmap,
    }
