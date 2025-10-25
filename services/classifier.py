"""
File classifier service.
Classifies files into categories based on extension and content.
"""

import logging
from pathlib import Path
from typing import List, Optional

from ..core import FileInfo, FileStatus
from ..core.config import get_category_for_extension
from ..utils import get_file_extension, get_file_size, get_file_hash

logger = logging.getLogger(__name__)


class FileClassifier:
    """
    Classifies files into categories.
    """

    def __init__(self, enable_hashing: bool = True):
        """
        Initialize the classifier.

        Args:
            enable_hashing: Whether to calculate file hashes
        """
        self.enable_hashing = enable_hashing

    def classify_file(self, file_path: Path) -> FileInfo:
        """
        Classify a single file.

        Args:
            file_path: Path to the file

        Returns:
            FileInfo object
        """
        try:
            extension = get_file_extension(file_path)
            category = get_category_for_extension(extension)
            size = get_file_size(file_path)

            file_hash = None
            if self.enable_hashing:
                file_hash = get_file_hash(file_path)

            file_info = FileInfo(
                path=file_path,
                size=size,
                extension=extension,
                category=category,
                hash=file_hash,
                status=FileStatus.PENDING,
            )

            logger.debug(f"Classified {file_path.name} as {category}")

            return file_info

        except Exception as e:
            logger.error(f"Error classifying file {file_path}: {e}")
            return FileInfo(
                path=file_path,
                size=0,
                extension="",
                category="other",
                status=FileStatus.ERROR,
                error=str(e),
            )

    def classify_directory(
        self, directory: Path, recursive: bool = True
    ) -> List[FileInfo]:
        """
        Classify all files in a directory.

        Args:
            directory: Directory to classify
            recursive: Whether to recurse into subdirectories

        Returns:
            List of FileInfo objects
        """
        logger.info(f"Classifying files in {directory}")

        files: List[FileInfo] = []

        try:
            pattern = "**/*" if recursive else "*"

            for item in directory.glob(pattern):
                if item.is_file():
                    file_info = self.classify_file(item)
                    files.append(file_info)

        except Exception as e:
            logger.error(f"Error classifying directory {directory}: {e}")

        logger.info(f"Classified {len(files)} files")

        return files

    def classify_multiple_directories(self, directories: List[Path]) -> List[FileInfo]:
        """
        Classify files from multiple directories.

        Args:
            directories: List of directories

        Returns:
            List of FileInfo objects
        """
        all_files: List[FileInfo] = []

        for directory in directories:
            files = self.classify_directory(directory)
            all_files.extend(files)

        logger.info(
            f"Classified {len(all_files)} files from " f"{len(directories)} directories"
        )

        return all_files

    def find_duplicates(self, files: List[FileInfo]) -> List[tuple[FileInfo, FileInfo]]:
        """
        Find duplicate files based on hash.

        Args:
            files: List of FileInfo objects with hashes

        Returns:
            List of tuples containing duplicate pairs
        """
        if not self.enable_hashing:
            logger.warning("Hashing disabled, cannot find duplicates")
            return []

        logger.info("Searching for duplicates...")

        # Group files by hash
        hash_map: dict[str, List[FileInfo]] = {}

        for file in files:
            if file.hash:
                if file.hash not in hash_map:
                    hash_map[file.hash] = []
                hash_map[file.hash].append(file)

        # Find groups with more than one file (duplicates)
        duplicates: List[tuple[FileInfo, FileInfo]] = []

        for file_hash, file_group in hash_map.items():
            if len(file_group) > 1:
                # Create pairs of duplicates
                for i in range(len(file_group) - 1):
                    for j in range(i + 1, len(file_group)):
                        duplicates.append((file_group[i], file_group[j]))
                        logger.debug(
                            f"Found duplicate: {file_group[i].name} "
                            f"and {file_group[j].name}"
                        )

        logger.info(f"Found {len(duplicates)} duplicate pairs")

        return duplicates

    def get_category_stats(self, files: List[FileInfo]) -> dict[str, int]:
        """
        Get statistics about file categories.

        Args:
            files: List of FileInfo objects

        Returns:
            Dictionary mapping category names to file counts
        """
        stats: dict[str, int] = {}

        for file in files:
            category = file.category
            stats[category] = stats.get(category, 0) + 1

        return stats

    def filter_by_category(
        self, files: List[FileInfo], category: str
    ) -> List[FileInfo]:
        """
        Filter files by category.

        Args:
            files: List of FileInfo objects
            category: Category to filter by

        Returns:
            Filtered list of FileInfo objects
        """
        return [f for f in files if f.category == category]

    def filter_by_extension(
        self, files: List[FileInfo], extension: str
    ) -> List[FileInfo]:
        """
        Filter files by extension.

        Args:
            files: List of FileInfo objects
            extension: Extension to filter by (without dot)

        Returns:
            Filtered list of FileInfo objects
        """
        return [f for f in files if f.extension.lower() == extension.lower()]
