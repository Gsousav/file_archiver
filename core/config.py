"""
Configuration file for File Archiver.
Contains category definitions, policies, and settings.
"""

from pathlib import Path
from typing import Dict, List

# ================================
# Archive Settings
# ================================

# Base archive directory (Desktop for easy access)
ARCHIVE_BASE_DIR = Path.home() / "Desktop"

# Session folder prefix (more descriptive)
SESSION_PREFIX = "Files_Organized"

# ================================
# File Categories
# ================================

# User-friendly names for category folders
CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    "documents": "📄 Documents",
    "spreadsheets": "📊 Spreadsheets",
    "presentations": "📽️ Presentations",
    "images": "🖼️ Images",
    "videos": "🎬 Videos",
    "audio": "🎵 Audio",
    "archives": "📦 Archives",
    "code": "💻 Code",
    "executables": "⚙️ Executables",
    "fonts": "🔤 Fonts",
    "ebooks": "📚 Ebooks",
    "design": "🎨 Design",
    "databases": "💾 Databases",
    "other": "📁 Other",
}

CATEGORIES: Dict[str, List[str]] = {
    "documents": [
        "pdf",
        "doc",
        "docx",
        "txt",
        "rtf",
        "odt",
        "md",
        "tex",
        "pages",
        "epub",
        "mobi",
    ],
    "spreadsheets": ["xls", "xlsx", "csv", "ods", "numbers"],
    "presentations": ["ppt", "pptx", "key", "odp"],
    "images": [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "svg",
        "tiff",
        "tif",
        "webp",
        "ico",
        "heic",
        "raw",
    ],
    "videos": [
        "mp4",
        "avi",
        "mkv",
        "mov",
        "wmv",
        "flv",
        "webm",
        "m4v",
        "mpg",
        "mpeg",
        "3gp",
    ],
    "audio": ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "opus", "alac", "ape"],
    "archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso", "dmg", "pkg"],
    "code": [
        "py",
        "js",
        "ts",
        "java",
        "c",
        "cpp",
        "h",
        "hpp",
        "cs",
        "go",
        "rs",
        "php",
        "rb",
        "swift",
        "kt",
        "scala",
        "sh",
        "bash",
        "zsh",
        "sql",
        "html",
        "css",
        "scss",
        "sass",
        "jsx",
        "tsx",
        "vue",
        "json",
        "xml",
        "yaml",
        "yml",
        "toml",
    ],
    "executables": [
        "exe",
        "app",
        "dmg",
        "deb",
        "rpm",
        "apk",
        "msi",
        "bat",
        "sh",
        "command",
    ],
    "fonts": ["ttf", "otf", "woff", "woff2", "eot"],
    "ebooks": ["epub", "mobi", "azw", "azw3", "pdf"],
    "design": [
        "psd",
        "ai",
        "sketch",
        "fig",
        "xd",
        "indd",
        "blend",
        "3ds",
        "max",
        "obj",
        "fbx",
    ],
    "databases": ["db", "sqlite", "sqlite3", "sql", "mdb", "accdb"],
    "other": [],  # Catch-all for unclassified files
}

# ================================
# Scanner Settings
# ================================

# Minimum number of files to recommend a directory
MIN_FILES_FOR_RECOMMENDATION = 10

# Weight for file type diversity in scoring (0-1)
DIVERSITY_WEIGHT = 0.7

# Weight for total file count in scoring (0-1)
COUNT_WEIGHT = 0.3

# Ignore hidden files (starting with .)
IGNORE_HIDDEN_FILES = True

# Ignore system directories
IGNORE_SYSTEM_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "venv",
    ".venv",
    "env",
    ".env",
    "Library",
    "System",
    "Applications",
}

# Recursive scanning behavior
# When False: Only scans files directly in the specified directory (not subdirectories)
# When True: Recursively scans all subdirectories
# Setting this to False (default) ensures consistency between scanning and classification
# and prevents the "directory appears messy but has no files" issue
RECURSIVE_SCAN = False

# ================================
# Duplicate Detection
# ================================

# Enable duplicate detection
ENABLE_DUPLICATE_DETECTION = True

# Hash algorithm for duplicate detection
HASH_ALGORITHM = "sha256"  # Options: md5, sha1, sha256

# Minimum file size for duplicate checking (in bytes)
# Files smaller than this will be compared by content directly
MIN_SIZE_FOR_HASHING = 1024  # 1 KB

# ================================
# Collision Handling
# ================================

# Available policies: "suffix", "hash", "skip", "overwrite"
DEFAULT_COLLISION_POLICY = "suffix"

# Suffix format for collision policy "suffix"
# {name} = original filename without extension
# {ext} = file extension
# {counter} = incremental number
COLLISION_SUFFIX_FORMAT = "{name}_{counter}{ext}"

# ================================
# Content Analysis
# ================================

# Enable content-based analysis
ENABLE_CONTENT_ANALYSIS = False

# Extract metadata from supported file types
EXTRACT_METADATA = True

# Supported file types for content analysis
CONTENT_ANALYSIS_TYPES = {
    "pdf": True,
    "image": False,  # Requires Pillow
    "video": False,  # Requires ffmpeg
}

# ================================
# Reporting
# ================================

# Generate HTML report after archiving
GENERATE_HTML_REPORT = True

# Report filename
REPORT_FILENAME = "archive_report.html"

# Include file thumbnails in report (for images)
INCLUDE_THUMBNAILS = False

# ================================
# Dry Run Settings
# ================================

# Always show dry run before execution
REQUIRE_DRY_RUN = True

# Show detailed file list in dry run
DRY_RUN_SHOW_ALL_FILES = False  # Set to True to see every file

# Maximum files to show per category in dry run
MAX_FILES_PER_CATEGORY_PREVIEW = 5

# ================================
# Performance
# ================================

# Maximum number of files to process in one session
MAX_FILES_PER_SESSION = 10000

# Use multiprocessing for hashing large files
ENABLE_MULTIPROCESSING = False

# Number of worker processes (None = auto-detect)
NUM_WORKERS = None

# ================================
# Logging
# ================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log file location (None = console only)
LOG_FILE = None  # Or: ARCHIVE_BASE_DIR / "archiver.log"

# ================================
# Helper Functions
# ================================


def get_category_for_extension(ext: str) -> str:
    """
    Get the category name for a given file extension.

    Args:
        ext: File extension (without dot)

    Returns:
        Category name, or "other" if not found
    """
    ext_lower = ext.lower().lstrip(".")

    for category, extensions in CATEGORIES.items():
        if ext_lower in extensions:
            return category

    return "other"


def get_all_extensions() -> List[str]:
    """
    Get a list of all registered file extensions.

    Returns:
        List of extensions (without dots)
    """
    extensions = []
    for exts in CATEGORIES.values():
        extensions.extend(exts)
    return list(set(extensions))  # Remove duplicates


def validate_config() -> bool:
    """
    Validate configuration settings.

    Returns:
        True if valid, raises ValueError otherwise
    """
    if DIVERSITY_WEIGHT + COUNT_WEIGHT != 1.0:
        raise ValueError(
            f"DIVERSITY_WEIGHT ({DIVERSITY_WEIGHT}) + "
            f"COUNT_WEIGHT ({COUNT_WEIGHT}) must equal 1.0"
        )

    if DEFAULT_COLLISION_POLICY not in ["suffix", "hash", "skip", "overwrite"]:
        raise ValueError(f"Invalid collision policy: {DEFAULT_COLLISION_POLICY}")

    if HASH_ALGORITHM not in ["md5", "sha1", "sha256"]:
        raise ValueError(f"Invalid hash algorithm: {HASH_ALGORITHM}")

    return True


# Validate on import
validate_config()
