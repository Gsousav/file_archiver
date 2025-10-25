"""
Data models for File Archiver.
Contains dataclasses and types used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from enum import Enum


class CollisionPolicy(Enum):
    """File collision handling policies."""

    SUFFIX = "suffix"  # Add numeric suffix: file_1.txt
    HASH = "hash"  # Add hash suffix: file_a3b2c1.txt
    SKIP = "skip"  # Skip the file, don't move
    OVERWRITE = "overwrite"  # Overwrite existing file


class FileStatus(Enum):
    """Status of a file in the archive process."""

    PENDING = "pending"
    MOVED = "moved"
    SKIPPED = "skipped"
    DUPLICATE = "duplicate"
    ERROR = "error"


@dataclass
class FileInfo:
    """
    Represents a file to be archived with its metadata.
    """

    path: Path
    size: int
    extension: str
    category: str
    hash: Optional[str] = None
    status: FileStatus = FileStatus.PENDING
    destination: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        """Get the filename."""
        return self.path.name

    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size / (1024 * 1024)

    @property
    def size_formatted(self) -> str:
        """Get human-readable file size."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"

    def __repr__(self) -> str:
        return f"FileInfo({self.name}, {self.size_formatted}, {self.category})"
    
    def __hash__(self) -> int:
        """Make FileInfo hashable based on its path."""
        return hash(self.path)
    
    def __eq__(self, other) -> bool:
        """Check equality based on path."""
        if not isinstance(other, FileInfo):
            return False
        return self.path == other.path


@dataclass
class DirectoryScore:
    """
    Represents a directory's archiving recommendation score.
    """

    path: Path
    total_files: int
    file_types: int
    total_size: int
    score: float
    extensions: Set[str] = field(default_factory=set)

    @property
    def size_formatted(self) -> str:
        """Get human-readable total size."""
        if self.total_size < 1024 * 1024:
            return f"{self.total_size / 1024:.1f} KB"
        elif self.total_size < 1024 * 1024 * 1024:
            return f"{self.total_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.total_size / (1024 * 1024 * 1024):.1f} GB"

    def __repr__(self) -> str:
        return (
            f"DirectoryScore({self.path.name}, "
            f"score={self.score:.2f}, "
            f"files={self.total_files}, "
            f"types={self.file_types})"
        )


@dataclass
class ArchiveSession:
    """
    Represents a complete archiving session.
    """

    session_id: str
    timestamp: datetime
    source_directories: List[Path]
    archive_path: Path
    files: List[FileInfo] = field(default_factory=list)
    duplicates: List[tuple[FileInfo, FileInfo]] = field(default_factory=list)
    collisions: List[FileInfo] = field(default_factory=list)
    dry_run: bool = True

    @property
    def total_files(self) -> int:
        """Get total number of files."""
        return len(self.files)

    @property
    def total_size(self) -> int:
        """Get total size of all files in bytes."""
        return sum(f.size for f in self.files)

    @property
    def files_by_category(self) -> Dict[str, List[FileInfo]]:
        """Get files grouped by category."""
        result: Dict[str, List[FileInfo]] = {}
        for file in self.files:
            if file.category not in result:
                result[file.category] = []
            result[file.category].append(file)
        return result

    @property
    def files_by_status(self) -> Dict[FileStatus, List[FileInfo]]:
        """Get files grouped by status."""
        result: Dict[FileStatus, List[FileInfo]] = {}
        for file in self.files:
            if file.status not in result:
                result[file.status] = []
            result[file.status].append(file)
        return result

    @property
    def success_count(self) -> int:
        """Get number of successfully moved files."""
        return len([f for f in self.files if f.status == FileStatus.MOVED])

    @property
    def error_count(self) -> int:
        """Get number of files with errors."""
        return len([f for f in self.files if f.status == FileStatus.ERROR])

    @property
    def skipped_count(self) -> int:
        """Get number of skipped files."""
        return len([f for f in self.files if f.status == FileStatus.SKIPPED])

    @property
    def duplicate_count(self) -> int:
        """Get number of duplicate files."""
        return len(self.duplicates)

    def get_summary(self) -> Dict[str, any]:
        """Get a summary of the session."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "dry_run": self.dry_run,
            "source_directories": [str(d) for d in self.source_directories],
            "archive_path": str(self.archive_path),
            "total_files": self.total_files,
            "total_size": self.total_size,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "skipped_count": self.skipped_count,
            "duplicate_count": self.duplicate_count,
            "categories": {
                cat: len(files) for cat, files in self.files_by_category.items()
            },
        }

    def __repr__(self) -> str:
        return (
            f"ArchiveSession({self.session_id}, "
            f"files={self.total_files}, "
            f"dry_run={self.dry_run})"
        )


@dataclass
class ArchivePlan:
    """
    Represents a plan for archiving (dry-run results).
    """

    session: ArchiveSession
    operations: List[Dict[str, any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_operation(
        self, operation_type: str, file_info: FileInfo, details: Optional[str] = None
    ):
        """Add an operation to the plan."""
        self.operations.append(
            {
                "type": operation_type,
                "file": file_info,
                "details": details,
                "source": str(file_info.path),
                "destination": (
                    str(file_info.destination) if file_info.destination else None
                ),
            }
        )

    def add_warning(self, message: str):
        """Add a warning to the plan."""
        self.warnings.append(message)

    @property
    def total_operations(self) -> int:
        """Get total number of operations."""
        return len(self.operations)

    @property
    def move_count(self) -> int:
        """Get number of move operations."""
        return len([op for op in self.operations if op["type"] == "move"])

    @property
    def skip_count(self) -> int:
        """Get number of skip operations."""
        return len([op for op in self.operations if op["type"] == "skip"])

    def __repr__(self) -> str:
        return (
            f"ArchivePlan({self.total_operations} operations, "
            f"{len(self.warnings)} warnings)"
        )
