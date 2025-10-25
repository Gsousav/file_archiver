"""
File Archiver - Smart File Organization Tool

A maintainable, OOP Python file archiver that organizes files from messy
folders into timestamped Archive sessions.
"""

__version__ = "1.0.0"
__author__ = "File Archiver Team"

from .core import (
    FileInfo,
    DirectoryScore,
    ArchiveSession,
    ArchivePlan,
    CollisionPolicy,
    FileStatus,
)

from .services import (
    DirectoryScanner,
    FileClassifier,
    ContentAnalyzer,
    FileMover,
    Reporter,
)

from .ui import CLI

__all__ = [
    # Core
    "FileInfo",
    "DirectoryScore",
    "ArchiveSession",
    "ArchivePlan",
    "CollisionPolicy",
    "FileStatus",
    # Services
    "DirectoryScanner",
    "FileClassifier",
    "ContentAnalyzer",
    "FileMover",
    "Reporter",
    # UI
    "CLI",
]
