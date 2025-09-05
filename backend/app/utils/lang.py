"""
Language utilities.

Provides functions for language detection and Malayalam text processing.
"""

import re
from typing import Optional


def detect_language(text: str) -> str:
    """
    Detect language of text.
    
    Args:
        text: Input text
        
    Returns:
        Language code (ml-IN, en-IN, etc.)
    """
    # Simple heuristic based on character sets
    malayalam_chars = re.findall(r'[\u0D00-\u0D7F]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)
    
    if len(malayalam_chars) > len(english_chars):
        return "ml-IN"
    else:
        return "en-IN"


def normalize_malayalam_text(text: str) -> str:
    """
    Normalize Malayalam text.
    
    Args:
        text: Malayalam text
        
    Returns:
        Normalized text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Normalize common variations
    text = text.replace('്', '്')  # Ensure proper chandrakkala
    
    return text


def is_malayalam(text: str) -> bool:
    """
    Check if text is in Malayalam.
    
    Args:
        text: Input text
        
    Returns:
        True if Malayalam, False otherwise
    """
    return detect_language(text) == "ml-IN"


def get_language_from_locale(locale: str) -> str:
    """
    Get language code from locale.
    
    Args:
        locale: Locale string (e.g., "ml-IN", "en-IN")
        
    Returns:
        Language code (e.g., "ml", "en")
    """
    return locale.split("-")[0] if "-" in locale else locale
