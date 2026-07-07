"""
CareerPath AI - Resume Parser
Parses extracted resume text into structured data including contact info,
skills, education, projects, certifications, and experience sections.
Uses regex for structured extraction and spaCy NER as fallback for name detection.
"""

import json
import os
import re

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import SKILLS_DB_PATH


# ─── Skills Database ──────────────────────────────────────────────────────────

def _load_skills_database():
    """
    Load the skills database from JSON file.

    Returns:
        list[str]: List of known skill names (lowercase).
    """
    try:
        with open(SKILLS_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        skills = []
        if isinstance(data, list):
            # Flat list of skill strings or dicts
            for item in data:
                if isinstance(item, str):
                    skills.append(item.lower())
                elif isinstance(item, dict):
                    # e.g. {"name": "Python", "category": "..."}
                    name = item.get("name") or item.get("skill") or ""
                    if name:
                        skills.append(name.lower())
        elif isinstance(data, dict):
            # Categorised: {"Programming": ["Python", "Java"], ...}
            for category, entries in data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, str):
                            skills.append(entry.lower())
                        elif isinstance(entry, dict):
                            name = entry.get("name") or entry.get("skill") or ""
                            if name:
                                skills.append(name.lower())
        return list(set(skills))
    except Exception as e:
        print(f"[Resume Parser] Failed to load skills database: {e}")
        return []


SKILLS_DB = _load_skills_database()


# ─── Section Detection ────────────────────────────────────────────────────────

SECTION_PATTERNS = {
    "education": r"(?i)(?:^|\n)\s*(?:education|academic\s*background|qualifications?|academic\s*details?)\s*[:\-]?\s*\n",
    "skills": r"(?i)(?:^|\n)\s*(?:skills?|technical\s*skills?|core\s*competenc(?:ies|y)|key\s*skills?|proficienc(?:ies|y))\s*[:\-]?\s*\n",
    "experience": r"(?i)(?:^|\n)\s*(?:experience|work\s*experience|professional\s*experience|employment\s*history|work\s*history)\s*[:\-]?\s*\n",
    "projects": r"(?i)(?:^|\n)\s*(?:projects?|academic\s*projects?|personal\s*projects?|key\s*projects?)\s*[:\-]?\s*\n",
    "certifications": r"(?i)(?:^|\n)\s*(?:certifications?|certificates?|professional\s*certifications?|licenses?\s*(?:&|and)\s*certifications?)\s*[:\-]?\s*\n",
    "summary": r"(?i)(?:^|\n)\s*(?:summary|profile|objective|about\s*me|professional\s*summary|career\s*objective)\s*[:\-]?\s*\n",
    "achievements": r"(?i)(?:^|\n)\s*(?:achievements?|accomplishments?|awards?|honors?|honours?)\s*[:\-]?\s*\n",
    "interests": r"(?i)(?:^|\n)\s*(?:interests?|hobbies|extracurricular|activities)\s*[:\-]?\s*\n",
    "languages": r"(?i)(?:^|\n)\s*(?:languages?|language\s*proficiency)\s*[:\-]?\s*\n",
    "references": r"(?i)(?:^|\n)\s*(?:references?|referees?)\s*[:\-]?\s*\n",
}


def _detect_sections(text):
    """
    Detect resume section boundaries using regex patterns.

    Args:
        text (str): Full resume text.

    Returns:
        dict: Mapping of section name → section text content.
    """
    section_positions = []

    for section_name, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            section_positions.append((match.start(), section_name))

    # Sort by position in the document
    section_positions.sort(key=lambda x: x[0])

    sections = {}
    for i, (start_pos, section_name) in enumerate(section_positions):
        if i + 1 < len(section_positions):
            end_pos = section_positions[i + 1][0]
        else:
            end_pos = len(text)

        section_text = text[start_pos:end_pos].strip()
        # Remove the header line itself
        lines = section_text.split("\n", 1)
        sections[section_name] = lines[1].strip() if len(lines) > 1 else ""

    return sections


# ─── Contact Information ──────────────────────────────────────────────────────

def _extract_email(text):
    """Extract email address from text."""
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def _extract_phone(text):
    """Extract phone number from text."""
    patterns = [
        r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}",
        r"(?:\+?\d{1,3}[\s\-]?)?\d{5}[\s\-]?\d{5}",
        r"(?:\+?\d{1,3}[\s\-]?)?\d{10,12}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ""


def _extract_linkedin(text):
    """Extract LinkedIn profile URL from text."""
    pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-/]+"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else ""


def _extract_name_regex(text):
    """
    Extract candidate name from the top of the resume using heuristics.
    Assumes the name is one of the first non-empty lines that is NOT
    an email, phone, URL, or section header.
    """
    lines = text.strip().split("\n")
    for line in lines[:8]:
        line = line.strip()
        if not line or len(line) < 2:
            continue
        # Skip lines that are clearly not names
        if re.search(r"@|http|www\.|linkedin|github|\d{5,}", line, re.IGNORECASE):
            continue
        if re.match(r"(?i)^(education|skills|experience|projects|summary|objective|phone|email|address|resume|curriculum)", line):
            continue
        # A name line typically has 2-5 words, mostly alpha
        words = line.split()
        if 1 <= len(words) <= 5 and all(re.match(r"^[A-Za-z.\-']+$", w) for w in words):
            return line
    return ""


def _extract_name_spacy(text):
    """
    Extract candidate name using spaCy Named Entity Recognition.
    Searches the first 500 characters for PERSON entities.

    Returns:
        str: Detected name or empty string.
    """
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return ""

        # Only process the header portion
        header_text = text[:500]
        doc = nlp(header_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                if len(name.split()) >= 2:
                    return name
        # Return first PERSON entity even if single word
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
        return ""
    except Exception:
        return ""


def _extract_contact_info(text):
    """
    Extract all contact information from resume text.

    Returns:
        dict: {name, email, phone, linkedin}
    """
    email = _extract_email(text)
    phone = _extract_phone(text)
    linkedin = _extract_linkedin(text)

    # Try regex name first, fallback to spaCy
    name = _extract_name_regex(text)
    if not name:
        name = _extract_name_spacy(text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
    }


# ─── Skills Extraction ───────────────────────────────────────────────────────

def _extract_skills(text, sections):
    """
    Extract skills by matching resume text against the skills database.
    Prioritises the 'skills' section if available, but also scans full text.

    Args:
        text (str): Full resume text.
        sections (dict): Detected resume sections.

    Returns:
        list[str]: Unique list of matched skills (original casing from DB).
    """
    search_text = text.lower()

    # Build a lookup for original casing
    skills_original = {}
    try:
        with open(SKILLS_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    skills_original[item.lower()] = item
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("skill") or ""
                    if name:
                        skills_original[name.lower()] = name
        elif isinstance(data, dict):
            for category, entries in data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, str):
                            skills_original[entry.lower()] = entry
                        elif isinstance(entry, dict):
                            name = entry.get("name") or entry.get("skill") or ""
                            if name:
                                skills_original[name.lower()] = name
    except Exception:
        pass

    matched = set()
    for skill_lower in SKILLS_DB:
        # Use word boundary matching for short skills to avoid false positives
        if len(skill_lower) <= 2:
            pattern = r"(?<![a-zA-Z])" + re.escape(skill_lower) + r"(?![a-zA-Z])"
            if re.search(pattern, search_text, re.IGNORECASE):
                matched.add(skills_original.get(skill_lower, skill_lower))
        else:
            if skill_lower in search_text:
                matched.add(skills_original.get(skill_lower, skill_lower))

    return sorted(matched)


# ─── Education Extraction ────────────────────────────────────────────────────

DEGREE_PATTERNS = [
    (r"(?i)\bph\.?d\.?\b", "PhD"),
    (r"(?i)\bdoctorate\b", "PhD"),
    (r"(?i)\bm\.?\s?tech\.?\b", "M.Tech"),
    (r"(?i)\bm\.?\s?sc\.?\b", "M.Sc"),
    (r"(?i)\bm\.?\s?b\.?\s?a\.?\b", "MBA"),
    (r"(?i)\bm\.?\s?c\.?\s?a\.?\b", "MCA"),
    (r"(?i)\bmaster(?:s|'s)?\b", "Masters"),
    (r"(?i)\bb\.?\s?tech\.?\b", "B.Tech"),
    (r"(?i)\bb\.?\s?e\.?\b", "B.E"),
    (r"(?i)\bb\.?\s?sc\.?\b", "B.Sc"),
    (r"(?i)\bb\.?\s?c\.?\s?a\.?\b", "BCA"),
    (r"(?i)\bbachelor(?:s|'s)?\b", "Bachelors"),
    (r"(?i)\bdiploma\b", "Diploma"),
    (r"(?i)\bassociate(?:s|'s)?\s*degree\b", "Associate"),
    (r"(?i)\bhigh\s*school\b", "High School"),
    (r"(?i)\b(?:10\+2|12th|hsc|intermediate)\b", "High School"),
]


def _extract_education(text, sections):
    """
    Extract education details from resume text.

    Args:
        text (str): Full resume text.
        sections (dict): Detected resume sections.

    Returns:
        list[str]: List of detected degree types.
    """
    search_text = sections.get("education", "") or text
    found_degrees = []

    for pattern, degree_label in DEGREE_PATTERNS:
        if re.search(pattern, search_text):
            if degree_label not in found_degrees:
                found_degrees.append(degree_label)

    return found_degrees


# ─── Projects Extraction ─────────────────────────────────────────────────────

def _extract_projects(text, sections):
    """
    Extract and count projects from resume text.

    Args:
        text (str): Full resume text.
        sections (dict): Detected resume sections.

    Returns:
        list[str]: List of project titles or bullet-point descriptions.
    """
    projects_text = sections.get("projects", "")
    if not projects_text:
        return []

    projects = []
    lines = projects_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect project title lines (bullet points, numbered, or standalone titles)
        is_title = False

        # Bullet point or numbered item
        if re.match(r"^[\u2022\u2023\u25E6\u2043•\-\*\>]\s+", line):
            clean = re.sub(r"^[\u2022\u2023\u25E6\u2043•\-\*\>]\s+", "", line).strip()
            if clean:
                is_title = True
                projects.append(clean)
        elif re.match(r"^\d+[\.\)]\s+", line):
            clean = re.sub(r"^\d+[\.\)]\s+", "", line).strip()
            if clean:
                is_title = True
                projects.append(clean)
        # Title-case or short line that looks like a title (≤ 80 chars, not a description)
        elif len(line) <= 80 and not line.endswith("."):
            # Check if it looks like a title (starts with uppercase, not too descriptive)
            if re.match(r"^[A-Z]", line) and ":" not in line:
                projects.append(line)
                is_title = True

    return projects


# ─── Certifications Extraction ───────────────────────────────────────────────

def _extract_certifications(text, sections):
    """
    Extract certifications from resume text.

    Args:
        text (str): Full resume text.
        sections (dict): Detected resume sections.

    Returns:
        list[str]: List of certification names/descriptions.
    """
    certs_text = sections.get("certifications", "")
    if not certs_text:
        # Try to find certifications mentioned inline
        cert_patterns = [
            r"(?i)(?:certified|certification|certificate)\s+(?:in\s+)?([^\n,;]{5,60})",
            r"(?i)(AWS\s+(?:Certified|Solutions?\s+Architect)[^\n,;]{0,40})",
            r"(?i)(Google\s+(?:Cloud|Professional)[^\n,;]{0,40})",
            r"(?i)(Azure\s+(?:Certified|Administrator|Developer)[^\n,;]{0,40})",
            r"(?i)(PMP|SCRUM|CISSP|CompTIA[^\n,;]{0,30})",
        ]
        found = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                cert = m.strip().rstrip(".")
                if cert and cert not in found:
                    found.append(cert)
        return found

    certs = []
    lines = certs_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Clean bullet points
        clean = re.sub(r"^[\u2022\u2023\u25E6\u2043•\-\*\>\d+\.\)]\s*", "", line).strip()
        if clean and len(clean) > 3:
            certs.append(clean)

    return certs


# ─── Experience Extraction ───────────────────────────────────────────────────

def _extract_experience(text, sections):
    """
    Extract work experience entries from resume text.

    Args:
        text (str): Full resume text.
        sections (dict): Detected resume sections.

    Returns:
        list[str]: List of experience entries/lines.
    """
    exp_text = sections.get("experience", "")
    if not exp_text:
        return []

    entries = []
    lines = exp_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line:
            entries.append(line)

    return entries


# ─── Main Parse Function ─────────────────────────────────────────────────────

def parse_resume(text):
    """
    Parse resume text into a structured dictionary.

    This is the main entry point for resume parsing. It orchestrates
    contact extraction, section detection, skill matching, education
    parsing, project counting, and certification extraction.

    Args:
        text (str): Extracted resume text (from pdf_extractor).

    Returns:
        dict: Structured resume data with keys:
            - name (str)
            - email (str)
            - phone (str)
            - linkedin (str)
            - skills (list[str])
            - education (list[str])
            - projects (list[str])
            - certifications (list[str])
            - experience (list[str])
            - raw_text (str)
            - sections (dict)
    """
    if not text or not text.strip():
        return {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "skills": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "experience": [],
            "raw_text": "",
            "sections": {},
        }

    try:
        # 1. Detect sections
        sections = _detect_sections(text)

        # 2. Extract contact info
        contact = _extract_contact_info(text)

        # 3. Extract structured data
        skills = _extract_skills(text, sections)
        education = _extract_education(text, sections)
        projects = _extract_projects(text, sections)
        certifications = _extract_certifications(text, sections)
        experience = _extract_experience(text, sections)

        return {
            "name": contact["name"],
            "email": contact["email"],
            "phone": contact["phone"],
            "linkedin": contact["linkedin"],
            "skills": skills,
            "education": education,
            "projects": projects,
            "certifications": certifications,
            "experience": experience,
            "raw_text": text,
            "sections": sections,
        }

    except Exception as e:
        print(f"[Resume Parser] Unexpected error during parsing: {e}")
        return {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "skills": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "experience": [],
            "raw_text": text,
            "sections": {},
        }
