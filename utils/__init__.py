"""
Utility module for File Archiver.
Contains helper functions and utilities.
"""

from .helpers import (
    get_file_hash,
    get_file_size,
    format_timestamp,
    safe_filename,
    ensure_unique_path,
    create_directory_safe,
    is_hidden_file,
    is_system_directory,
    get_file_extension,
    format_file_size,
    truncate_string,
    pluralize,
    validate_directory,
    setup_logging,
)

__all__ = [
    "get_file_hash",
    "get_file_size",
    "format_timestamp",
    "safe_filename",
    "ensure_unique_path",
    "create_directory_safe",
    "is_hidden_file",
    "is_system_directory",
    "get_file_extension",
    "format_file_size",
    "truncate_string",
    "pluralize",
    "validate_directory",
    "setup_logging",
]
