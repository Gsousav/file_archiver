"""
Utility functions for File Archiver.
Contains helper functions used across the application.
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def get_file_hash(file_path: Path, algorithm: str = "sha256") -> Optional[str]:
    """
    Calculate the hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hexadecimal hash string, or None if error
    """
    try:
        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return None


def get_file_size(file_path: Path) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes, or 0 if error
    """
    try:
        return file_path.stat().st_size
    except Exception as e:
        logger.error(f"Error getting size of {file_path}: {e}")
        return 0


def format_timestamp(dt: datetime, format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Format a datetime object as a string.

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def safe_filename(filename: str) -> str:
    """
    Make a filename safe by removing/replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Characters to replace
    invalid_chars = '<>:"/\\|?*'

    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, "_")

    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(". ")

    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"

    return safe_name


def ensure_unique_path(path: Path, suffix_format: str = "_{counter}") -> Path:
    """
    Ensure a path is unique by adding a counter if needed.

    Args:
        path: Desired path
        suffix_format: Format string for suffix (must contain {counter})

    Returns:
        Unique path
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1

    while True:
        new_stem = stem + suffix_format.format(counter=counter)
        new_path = parent / f"{new_stem}{suffix}"

        if not new_path.exists():
            return new_path

        counter += 1

        # Safety check to avoid infinite loops
        if counter > 9999:
            # Add timestamp to make it unique
            timestamp = format_timestamp(datetime.now())
            new_stem = f"{stem}_{timestamp}"
            return parent / f"{new_stem}{suffix}"


def create_directory_safe(path: Path) -> bool:
    """
    Create a directory, including parents, if it doesn't exist.

    Args:
        path: Directory path to create

    Returns:
        True if successful, False otherwise
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def is_hidden_file(path: Path) -> bool:
    """
    Check if a file or directory is hidden.

    Args:
        path: Path to check

    Returns:
        True if hidden, False otherwise
    """
    return path.name.startswith(".")


def is_system_directory(path: Path, system_dirs: set) -> bool:
    """
    Check if a directory is a system directory to ignore.

    Args:
        path: Directory path
        system_dirs: Set of system directory names

    Returns:
        True if system directory, False otherwise
    """
    return path.name in system_dirs


def get_file_extension(path: Path) -> str:
    """
    Get the file extension without the dot.

    Args:
        path: File path

    Returns:
        Extension without dot, or empty string if no extension
    """
    suffix = path.suffix.lstrip(".")
    return suffix.lower()


def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Return singular or plural form based on count.

    Args:
        count: Number of items
        singular: Singular form
        plural: Plural form (defaults to singular + 's')

    Returns:
        Formatted string with count and correct form
    """
    if plural is None:
        plural = singular + "s"

    form = singular if count == 1 else plural
    return f"{count} {form}"


def validate_directory(path: Path) -> tuple[bool, Optional[str]]:
    """
    Validate that a path is a valid, accessible directory.

    Args:
        path: Path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path.exists():
        return False, f"Directory does not exist: {path}"

    if not path.is_dir():
        return False, f"Path is not a directory: {path}"

    if not path.is_absolute():
        return False, f"Path must be absolute: {path}"

    try:
        # Try to list directory to check read permissions
        list(path.iterdir())
        return True, None
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error accessing directory: {e}"


def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
