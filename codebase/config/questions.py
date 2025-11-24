"""
Questions database management.
Loads and manages interview questions for all roles.
"""

import json
from pathlib import Path
from typing import Dict, List

QUESTIONS_PATH = Path(__file__).parent.parent / "data" / "questions.json"


def load_questions() -> Dict[str, Dict[str, List[str]]]:
    """
    Load interview questions from JSON file.
    
    Returns:
        Dict with structure: {role: {round_type: [questions]}}
    """
    # Return empty dict since we're generating questions dynamically
    return {}


def get_questions_for_role(role: str, round_type: str) -> List[str]:
    """
    Get questions for specific role and round type.
    
    Args:
        role: Role name (e.g., "Software Engineer")
        round_type: "Technical" or "Behavioral"
    
    Returns:
        List of question strings
    """
    questions = load_questions()
    return questions.get(role, {}).get(round_type, [])


def get_question_count(role: str, round_type: str) -> int:
    """Get total number of questions for role and round."""
    return len(get_questions_for_role(role, round_type))
