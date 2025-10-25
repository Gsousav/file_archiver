"""
File Archiver - Smart File Organization System
"""

__version__ = "1.0.0"
__author__ = "File Archiver Team"

# Import main components
from .core import (
    FileInfo,
    ArchiveSession,
    ArchivePlan,
    DirectoryScore,
)

from .services import (
    DirectoryScanner,
    FileClassifier,
    FileMover,
    Reporter,
    ContentAnalyzer,
)

from .ui import BeautifulCLI

__all__ = [
    # Core
    'FileInfo',
    'ArchiveSession', 
    'ArchivePlan',
    'DirectoryScore',
    # Services
    'DirectoryScanner',
    'FileClassifier',
    'FileMover',
    'Reporter',
    'ContentAnalyzer',
    # UI
    'BeautifulCLI',
]
