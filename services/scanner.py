# Create the missing scanner.py file
"""
Directory scanner service.
Scans directories and provides recommendations for archiving.
"""

import logging
from pathlib import Path
from typing import List, Set

from ..core import DirectoryScore
from ..core.config import (
    MIN_FILES_FOR_RECOMMENDATION,
    DIVERSITY_WEIGHT,
    COUNT_WEIGHT,
    IGNORE_HIDDEN_FILES,
    IGNORE_SYSTEM_DIRS,
    RECURSIVE_SCAN,
)
from ..utils import (
    is_hidden_file,
    is_system_directory,
    get_file_extension,
    validate_directory,
)

logger = logging.getLogger(__name__)


class DirectoryScanner:
    """
    Scans directories and provides archiving recommendations.
    """
    
    def __init__(self,
                 ignore_hidden: bool = IGNORE_HIDDEN_FILES,
                 ignore_system_dirs: Set[str] = IGNORE_SYSTEM_DIRS,
                 recursive: bool = None):
        """
        Initialize the scanner.
        
        Args:
            ignore_hidden: Whether to ignore hidden files
            ignore_system_dirs: Set of system directory names to ignore
            recursive: Whether to scan subdirectories recursively (None uses config default)
        """
        self.ignore_hidden = ignore_hidden
        self.ignore_system_dirs = ignore_system_dirs
        # Use config value if not explicitly specified
        self.recursive = recursive if recursive is not None else RECURSIVE_SCAN
    
    def scan_directory(self, directory: Path, recursive: bool = None) -> DirectoryScore:
        """
        Scan a directory and calculate its archiving score.
        
        Args:
            directory: Directory to scan
            recursive: Override the instance recursive setting for this scan
            
        Returns:
            DirectoryScore object
        """
        # Use parameter if provided, otherwise use instance setting
        scan_recursive = recursive if recursive is not None else self.recursive
        
        logger.info(f"Scanning directory: {directory} (recursive={scan_recursive})")
        
        # Validate directory
        is_valid, error = validate_directory(directory)
        if not is_valid:
            logger.warning(f"Invalid directory {directory}: {error}")
            return DirectoryScore(
                path=directory,
                total_files=0,
                file_types=0,
                total_size=0,
                score=0.0,
                recursive=scan_recursive
            )
        
        total_files = 0
        total_size = 0
        extensions: Set[str] = set()
        
        try:
            # Use rglob for recursive, glob for non-recursive
            pattern = "**/*" if scan_recursive else "*"
            iterator = directory.glob(pattern)
            
            for item in iterator:
                # Skip directories
                if item.is_dir():
                    if self._should_skip_directory(item):
                        continue
                    continue
                
                # Skip hidden files if configured
                if self.ignore_hidden and is_hidden_file(item):
                    continue
                
                # Skip if parent is a system directory (only relevant in recursive mode)
                if scan_recursive and self._is_in_system_directory(item):
                    continue
                
                # Count file
                total_files += 1
                
                try:
                    total_size += item.stat().st_size
                except Exception as e:
                    logger.warning(f"Could not get size of {item}: {e}")
                
                # Track extension
                ext = get_file_extension(item)
                if ext:
                    extensions.add(ext)
        
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        # Calculate score
        score = self._calculate_score(total_files, len(extensions))
        
        logger.info(
            f"Scanned {directory.name}: "
            f"{total_files} files, {len(extensions)} types, score={score:.2f}"
        )
        
        return DirectoryScore(
            path=directory,
            total_files=total_files,
            file_types=len(extensions),
            total_size=total_size,
            score=score,
            extensions=extensions,
            recursive=scan_recursive
        )
    
    def scan_multiple_directories(self, 
                                  directories: List[Path]) -> List[DirectoryScore]:
        """
        Scan multiple directories.
        
        Args:
            directories: List of directories to scan
            
        Returns:
            List of DirectoryScore objects
        """
        scores = []
        
        for directory in directories:
            score = self.scan_directory(directory)
            scores.append(score)
        
        return scores
    
    def get_recommendations(self, 
                           directories: List[Path],
                           top_n: int = 5) -> List[DirectoryScore]:
        """
        Get top N recommended directories for archiving.
        
        Args:
            directories: List of directories to evaluate
            top_n: Number of top recommendations to return
            
        Returns:
            List of DirectoryScore objects, sorted by score descending
        """
        logger.info(f"Generating recommendations for {len(directories)} directories")
        
        scores = self.scan_multiple_directories(directories)
        
        # Filter out directories with too few files
        filtered_scores = [
            s for s in scores 
            if s.total_files >= MIN_FILES_FOR_RECOMMENDATION
        ]
        
        # Sort by score descending
        sorted_scores = sorted(
            filtered_scores, 
            key=lambda x: x.score, 
            reverse=True
        )
        
        # Return top N
        result = sorted_scores[:top_n]
        
        logger.info(f"Generated {len(result)} recommendations")
        
        return result
    
    def _calculate_score(self, total_files: int, file_types: int) -> float:
        """
        Calculate archiving score for a directory.
        
        Args:
            total_files: Total number of files
            file_types: Number of distinct file types
            
        Returns:
            Score between 0 and 10
        """
        if total_files == 0:
            return 0.0
        
        # Normalize file count (logarithmic scale)
        import math
        normalized_count = min(1.0, math.log10(total_files + 1) / 3.0)
        
        # Normalize diversity
        normalized_diversity = min(1.0, file_types / 10.0)
        
        # Weighted score
        score = (
            DIVERSITY_WEIGHT * normalized_diversity +
            COUNT_WEIGHT * normalized_count
        ) * 10
        
        return round(score, 2)
    
    def _should_skip_directory(self, directory: Path) -> bool:
        """Check if a directory should be skipped."""
        return is_system_directory(directory, self.ignore_system_dirs)
    
    def _is_in_system_directory(self, file_path: Path) -> bool:
        """Check if a file is inside a system directory."""
        for parent in file_path.parents:
            if is_system_directory(parent, self.ignore_system_dirs):
                return True
        return False
