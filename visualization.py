"""
Text cleaning and preprocessing utilities for CareerPath AI.

Provides functions for text normalization, tokenization, stopword removal,
keyword extraction, and skill name normalization used across the resume
parsing and analysis pipeline.
"""

import re
import string
import unicodedata
from collections import Counter


# ── Skill alias map ────────────────────────────────────────────────────────────

def get_skill_aliases():
    """Return a dictionary of skill aliases/abbreviations.

    Maps common shorthand notations to their canonical full-form names
    so that downstream matching is consistent regardless of how a skill
    was written on a resume.
    """
    return {
        'ml': 'machine learning',
        'dl': 'deep learning',
        'ai': 'artificial intelligence',
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'k8s': 'kubernetes',
        'tf': 'tensorflow',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
        'ci/cd': 'ci/cd',
        'dsa': 'data structures',
        'oop': 'object oriented programming',
        'dbms': 'database management',
        'os': 'operating systems',
        'cn': 'computer networks',
        'html5': 'html',
        'css3': 'css',
        'nosql': 'mongodb',
        'rdbms': 'sql',
        'aws': 'aws',
        'gcp': 'gcp',
    }


# ── Common English stopwords (self-contained, no nltk needed) ──────────────────

_STOPWORDS = frozenset({
    'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am',
    'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because',
    'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can',
    'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn',
    "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few',
    'for', 'from', 'further', 'get', 'got', 'had', 'hadn', "hadn't", 'has',
    'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her',
    'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if',
    'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself',
    'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most',
    'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor',
    'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
    'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same',
    'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn',
    "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll",
    'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
    'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
    'use', 'used', 'using', 've', 'very', 'was', 'wasn', "wasn't", 'we',
    'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while',
    'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'would', 'wouldn',
    "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've", 'your',
    'yours', 'yourself', 'yourselves',
    # Resume-specific noise words
    'experience', 'work', 'worked', 'working', 'responsible', 'also',
    'including', 'well', 'various', 'etc', 'new', 'based', 'team',
    'project', 'projects', 'company', 'role', 'development', 'developed',
})


# ── Core text utilities ───────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Remove extra whitespace, special characters, and normalize text.

    Steps:
    1. Normalize unicode characters (NFKD → strip accents → NFKC).
    2. Remove non-printable / control characters.
    3. Replace ligatures & special dashes with ASCII equivalents.
    4. Collapse multiple whitespace into single spaces.
    5. Strip leading / trailing whitespace.

    Parameters
    ----------
    text : str
        Raw input text (e.g. from a parsed PDF).

    Returns
    -------
    str
        Cleaned, normalized text.
    """
    if not text:
        return ""

    # Normalize unicode (decompose → strip combining marks → recompose)
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(
        ch for ch in text
        if not unicodedata.combining(ch)
    )
    text = unicodedata.normalize('NFKC', text)

    # Remove non-printable / control characters (keep newlines & tabs)
    text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)

    # Replace common special dashes / bullets with standard equivalents
    text = re.sub(r'[–—―]', '-', text)
    text = re.sub(r'[•·▪▸►]', ' ', text)

    # Collapse runs of whitespace (including mixed tabs/spaces/newlines)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def tokenize(text: str) -> list[str]:
    """Simple word tokenization.

    Splits on whitespace and punctuation boundaries while keeping
    tokens like ``C++``, ``C#``, ``CI/CD``, and version numbers
    (e.g. ``3.11``) intact.

    Parameters
    ----------
    text : str
        Input text to tokenize.

    Returns
    -------
    list[str]
        Lowercased tokens.
    """
    if not text:
        return []

    text = text.lower()

    # Keep compound tokens like C++, C#, CI/CD, .NET, Node.js
    # by matching them first, then falling back to word chars
    pattern = r"""
        \b[a-z][\+\#]{1,2}\b      |   # C++, C#
        \b\w+(?:[./]\w+)+\b       |   # CI/CD, Node.js, 3.11
        \.\w+\b                    |   # .NET, .js
        \b\w+\b                        # regular words
    """
    tokens = re.findall(pattern, text, re.VERBOSE)
    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove common English stopwords from a token list.

    Uses a self-contained stopword set (no external download required)
    that also includes resume-specific noise words like 'responsible',
    'various', 'worked', etc.

    Parameters
    ----------
    tokens : list[str]
        List of lowercased word tokens.

    Returns
    -------
    list[str]
        Filtered tokens with stopwords removed.
    """
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def extract_keywords(text: str, top_n: int = 20) -> list[tuple[str, int]]:
    """Extract the most frequent keywords from *text*.

    Pipeline: clean → tokenize → remove stopwords → frequency count.

    Parameters
    ----------
    text : str
        Raw input text.
    top_n : int, optional
        Number of top keywords to return (default ``20``).

    Returns
    -------
    list[tuple[str, int]]
        List of ``(keyword, count)`` pairs sorted by descending frequency.
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    filtered = remove_stopwords(tokens)
    counter = Counter(filtered)
    return counter.most_common(top_n)


def normalize_skill(skill: str) -> str:
    """Normalize a skill name for comparison.

    Lowercases, strips whitespace, and resolves common abbreviations
    via the alias map returned by :func:`get_skill_aliases`.

    Parameters
    ----------
    skill : str
        Raw skill string (e.g. from a resume or job description).

    Returns
    -------
    str
        Canonical lowercase skill name.
    """
    if not skill:
        return ""

    normalized = skill.strip().lower()

    # Remove trailing punctuation (commas, periods, semicolons)
    normalized = normalized.rstrip('.,;:')

    # Strip redundant parenthetical notes – e.g. "Python (3.x)"
    normalized = re.sub(r'\s*\(.*?\)\s*', ' ', normalized).strip()

    # Resolve aliases
    aliases = get_skill_aliases()
    if normalized in aliases:
        return aliases[normalized]

    return normalized
