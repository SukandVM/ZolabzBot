# import re
from typing import Dict


def parse_resume_text(text: str) -> Dict:
    """
    Very simple resume parser (good enough for demo)
    """

    skills_keywords = [
        "python",
        "java",
        "c++",
        "fastapi",
        "machine learning",
        "deep learning",
        "sql",
        "docker",
        "linux",
    ]

    found_skills = [skill.title() for skill in skills_keywords if skill in text.lower()]

    return {
        "skills": list(set(found_skills)),
        "raw_text": text[:2000],  # optional, useful for debugging
    }
