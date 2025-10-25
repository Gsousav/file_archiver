"""
Example tests for File Archiver.
Run with: pytest tests/
"""

import pytest
from pathlib import Path
from file_archiver.core import FileInfo, FileStatus
from file_archiver.core.config import get_category_for_extension
from file_archiver.utils import get_file_extension, format_file_size


class TestUtils:
    """Test utility functions."""

    def test_get_file_extension(self):
        """Test file extension extraction."""
        assert get_file_extension(Path("test.pdf")) == "pdf"
        assert get_file_extension(Path("document.docx")) == "docx"
        assert get_file_extension(Path("archive.tar.gz")) == "gz"
        assert get_file_extension(Path("noextension")) == ""

    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(500) == "500 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"


class TestConfig:
    """Test configuration."""

    def test_get_category_for_extension(self):
        """Test category classification."""
        assert get_category_for_extension("pdf") == "documents"
        assert get_category_for_extension("jpg") == "images"
        assert get_category_for_extension("mp4") == "videos"
        assert get_category_for_extension("py") == "code"
        assert get_category_for_extension("unknown") == "other"

    def test_category_case_insensitive(self):
        """Test that classification is case-insensitive."""
        assert get_category_for_extension("PDF") == "documents"
        assert get_category_for_extension("JPG") == "images"


class TestModels:
    """Test data models."""

    def test_file_info_creation(self):
        """Test FileInfo creation."""
        file_info = FileInfo(
            path=Path("/test/file.pdf"),
            size=1024,
            extension="pdf",
            category="documents",
        )

        assert file_info.name == "file.pdf"
        assert file_info.size == 1024
        assert file_info.status == FileStatus.PENDING
        assert file_info.size_formatted == "1.0 KB"

    def test_file_info_size_formatting(self):
        """Test file size formatting in FileInfo."""
        file_info = FileInfo(
            path=Path("/test/large.zip"),
            size=1024 * 1024 * 100,  # 100 MB
            extension="zip",
            category="archives",
        )

        assert file_info.size_mb == 100.0
        assert "MB" in file_info.size_formatted


# Example of how to create integration tests
@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create some test files
    (tmp_path / "document.pdf").write_text("test pdf content")
    (tmp_path / "image.jpg").write_text("test image content")
    (tmp_path / "code.py").write_text("print('hello')")

    return tmp_path


class TestScanner:
    """Test directory scanner."""

    def test_scan_directory(self, temp_test_dir):
        """Test scanning a directory."""
        from file_archiver.services import DirectoryScanner

        scanner = DirectoryScanner()
        score = scanner.scan_directory(temp_test_dir)

        assert score.total_files == 3
        assert score.file_types == 3  # pdf, jpg, py
        assert score.score > 0


class TestClassifier:
    """Test file classifier."""

    def test_classify_file(self, temp_test_dir):
        """Test file classification."""
        from file_archiver.services import FileClassifier

        classifier = FileClassifier(enable_hashing=False)
        file_path = temp_test_dir / "document.pdf"

        file_info = classifier.classify_file(file_path)

        assert file_info.extension == "pdf"
        assert file_info.category == "documents"
        assert file_info.size > 0

    def test_classify_directory(self, temp_test_dir):
        """Test classifying all files in a directory."""
        from file_archiver.services import FileClassifier

        classifier = FileClassifier(enable_hashing=False)
        files = classifier.classify_directory(temp_test_dir, recursive=False)

        assert len(files) == 3
        categories = {f.category for f in files}
        assert "documents" in categories
        assert "images" in categories
        assert "code" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
