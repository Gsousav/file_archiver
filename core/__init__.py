"""
Core module for File Archiver.
Contains configuration, models, and data structures.
"""

from .config import (
    CATEGORIES,
    ARCHIVE_BASE_DIR,
    SESSION_PREFIX,
    get_category_for_extension,
    get_all_extensions,
)

from .models import (
    FileInfo,
    DirectoryScore,
    ArchiveSession,
    ArchivePlan,
    CollisionPolicy,
    FileStatus,
)

__all__ = [
    "CATEGORIES",
    "ARCHIVE_BASE_DIR",
    "SESSION_PREFIX",
    "get_category_for_extension",
    "get_all_extensions",
    "FileInfo",
    "DirectoryScore",
    "ArchiveSession",
    "ArchivePlan",
    "CollisionPolicy",
    "FileStatus",
]
