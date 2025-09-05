"""
Media utilities.

Provides functions for file handling and media processing.
"""

import uuid
from pathlib import Path
from typing import Optional

from app.config import settings


def generate_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate unique filename.
    
    Args:
        original_filename: Original filename
        prefix: Optional prefix
        
    Returns:
        Generated filename
    """
    extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    
    if prefix:
        return f"{prefix}_{unique_id}{extension}"
    else:
        return f"{unique_id}{extension}"


def get_media_path(filename: str, subdirectory: str = "") -> Path:
    """
    Get full path for media file.
    
    Args:
        filename: Filename
        subdirectory: Optional subdirectory
        
    Returns:
        Full path to media file
    """
    media_root = settings.media_path
    
    if subdirectory:
        return media_root / subdirectory / filename
    else:
        return media_root / filename


def create_media_directory(subdirectory: str = "") -> Path:
    """
    Create media directory if it doesn't exist.
    
    Args:
        subdirectory: Optional subdirectory
        
    Returns:
        Path to directory
    """
    if subdirectory:
        directory = settings.media_path / subdirectory
    else:
        directory = settings.media_path
    
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return file_path.stat().st_size if file_path.exists() else 0


def is_valid_audio_format(filename: str) -> bool:
    """
    Check if file is valid audio format.
    
    Args:
        filename: Filename
        
    Returns:
        True if valid audio format
    """
    extension = Path(filename).suffix.lower().lstrip('.')
    return extension in settings.allowed_audio_formats


def is_valid_image_format(filename: str) -> bool:
    """
    Check if file is valid image format.
    
    Args:
        filename: Filename
        
    Returns:
        True if valid image format
    """
    extension = Path(filename).suffix.lower().lstrip('.')
    return extension in settings.allowed_image_formats
