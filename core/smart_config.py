"""
Enhanced configuration with ML-powered smart categorization.
"""

from pathlib import Path
from typing import Dict, List

# ================================
# Smart Categorization Structure
# ================================

# Hierarchical category structure
SMART_CATEGORIES = {
    "work": {
        "documents": {
            "reports": ["pdf", "docx"],
            "presentations": ["pptx", "key"],
            "spreadsheets": ["xlsx", "xls", "csv"],
            "contracts": ["pdf", "docx"],
        },
        "code": {
            "python": ["py", "ipynb"],
            "javascript": ["js", "ts", "jsx", "tsx"],
            "web": ["html", "css", "scss"],
            "config": ["json", "yaml", "yml", "toml", "env"],
            "java": ["java", "class", "jar"],
            "cpp": ["cpp", "c", "h", "hpp"],
            "other": ["go", "rs", "php", "rb", "swift"],
        },
        "meetings": {
            "recordings": ["mp4", "mov", "webm"],
            "notes": ["md", "txt", "docx"],
        },
        "projects": {},
    },
    "personal": {
        "photos": {
            "2024": {},
            "2023": {},
            "screenshots": ["png", "jpg"],
        },
        "finance": {
            "receipts": ["pdf", "jpg", "png"],
            "invoices": ["pdf"],
            "statements": ["pdf", "csv"],
            "tax": ["pdf", "xlsx"],
        },
        "health": {
            "medical_records": ["pdf"],
            "insurance": ["pdf"],
        },
        "documents": {
            "resumes": ["pdf", "docx"],
            "legal": ["pdf", "docx"],
            "personal": ["pdf", "docx", "txt"],
        },
    },
    "media": {
        "music": {
            "albums": ["mp3", "flac", "wav"],
            "podcasts": ["mp3", "m4a"],
            "playlists": ["m3u", "pls"],
        },
        "videos": {
            "movies": ["mp4", "mkv", "avi"],
            "tv_shows": ["mp4", "mkv"],
            "tutorials": ["mp4", "webm"],
            "youtube": ["mp4", "webm"],
        },
        "books": {
            "technical": ["pdf", "epub", "mobi"],
            "fiction": ["epub", "mobi"],
            "audiobooks": ["m4b", "mp3"],
        },
        "images": {
            "wallpapers": ["jpg", "png"],
            "graphics": ["svg", "ai", "psd"],
            "icons": ["png", "svg", "ico"],
        },
    },
    "downloads": {
        "installers": {
            "mac": ["dmg", "pkg"],
            "windows": ["exe", "msi"],
            "linux": ["deb", "rpm", "appimage"],
        },
        "compressed": {
            "archives": ["zip", "rar", "7z"],
            "backups": ["tar", "gz", "bz2"],
        },
        "temporary": {},
    },
}

# ================================
# ML Classification Settings
# ================================

# Enable ML-powered classification
ENABLE_ML_CLASSIFICATION = True

# Use transformers for text classification
USE_TRANSFORMERS = True  # Requires: pip install transformers torch

# Use computer vision for image classification
USE_VISION_ML = False  # Requires: pip install opencv-python tensorflow

# Minimum confidence threshold for ML classification
ML_CONFIDENCE_THRESHOLD = 0.6

# ================================
# Smart Path Generation
# ================================

# Enable date-based organization for certain file types
DATE_BASED_ORGANIZATION = {
    "photos": True,
    "screenshots": True,
    "videos": True,
    "documents": False,
}

# Date format for organization
DATE_FORMAT = "{year}/{month}"  # e.g., 2024/January

# Enable content-based classification
ANALYZE_FILE_CONTENT = True

# Maximum file size to analyze content (in bytes)
MAX_CONTENT_ANALYSIS_SIZE = 10 * 1024 * 1024  # 10 MB

# ================================
# Pattern Recognition
# ================================

# Filename patterns for intelligent classification
INTELLIGENT_PATTERNS = {
    # Work patterns
    "work_report": r"(report|quarterly|annual|q[1-4]).*\d{4}",
    "invoice": r"(invoice|bill|receipt).*\d+",
    "contract": r"(contract|agreement|nda)",
    "presentation": r"(slides?|deck|presentation|pitch)",
    
    # Personal patterns
    "screenshot": r"screen\s*shot|capture.*\d{4}",
    "photo": r"(img|dsc|photo).*\d{4}|\d{4}[-_]\d{2}[-_]\d{2}",
    "resume": r"(cv|resume|curriculum)",
    
    # Code patterns
    "config": r"\.?config|\.env|settings|\..*rc$",
    "readme": r"readme|license|changelog",
    
    # Media patterns
    "music_album": r".*\d{4}.*album.*|.*-.*\d{4}",
    "podcast": r"podcast.*ep\d+|episode.*\d+",
    "tutorial": r"tutorial|how.*to|guide|course",
    
    # Download patterns
    "installer": r"setup|install|.*installer",
    "compressed": r"archive|backup",
}

# ================================
# Context Detection Keywords
# ================================

CONTEXT_KEYWORDS = {
    "work": [
        "work", "project", "client", "meeting", "presentation",
        "report", "invoice", "contract", "proposal", "business",
        "company", "office", "corporate", "sprint", "agile",
        "dashboard", "analytics", "metrics", "kpi",
    ],
    "personal": [
        "personal", "family", "vacation", "receipt", "bill",
        "medical", "insurance", "tax", "bank", "home",
        "birthday", "wedding", "travel", "hobby",
    ],
    "media": [
        "movie", "song", "album", "podcast", "video", "music",
        "episode", "season", "tutorial", "course", "book",
        "entertainment", "leisure", "watch", "listen",
    ],
}

# ================================
# Auto-Tagging
# ================================

# Enable automatic tagging based on content
ENABLE_AUTO_TAGGING = True

# Tags to extract from filename and content
AUTO_TAG_PATTERNS = {
    "urgent": r"urgent|asap|important|priority",
    "draft": r"draft|wip|work.?in.?progress",
    "final": r"final|approved|signed",
    "confidential": r"confidential|private|secret",
    "backup": r"backup|archive|copy",
}

# ================================
# Duplicate Handling (Enhanced)
# ================================

# Use perceptual hashing for images
USE_PERCEPTUAL_HASH = True  # Requires: pip install imagehash

# Similarity threshold for perceptual hash (0.0-1.0)
PERCEPTUAL_HASH_THRESHOLD = 0.95

# Keep best quality duplicate (based on resolution for images)
KEEP_BEST_QUALITY = True

# ================================
# Organization Rules
# ================================

# Organize by project (detect project folders)
DETECT_PROJECTS = True

# Project indicators
PROJECT_INDICATORS = [
    ".git", ".vscode", "package.json", "requirements.txt",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
]

# Keep project files together
PRESERVE_PROJECT_STRUCTURE = True

# ================================
# Smart Suggestions
# ================================

# Suggest merging similar categories
SUGGEST_CATEGORY_MERGE = True

# Suggest splitting large categories
SUGGEST_CATEGORY_SPLIT = True
CATEGORY_SPLIT_THRESHOLD = 100  # files

# Suggest archive old files
SUGGEST_ARCHIVE_OLD_FILES = True
OLD_FILE_THRESHOLD_DAYS = 365  # 1 year

# ================================
# UI Enhancements
# ================================

# Show preview of organized structure before execution
SHOW_TREE_PREVIEW = True

# Generate visual tree diagram
GENERATE_TREE_DIAGRAM = True

# Include file count in tree
SHOW_FILE_COUNTS = True

# ================================
# Performance
# ================================

# Use parallel processing for ML inference
USE_PARALLEL_ML = True
ML_WORKERS = 4

# Cache ML results
CACHE_ML_RESULTS = True
CACHE_TTL = 86400  # 24 hours

# ================================
# Helper Functions
# ================================

def get_smart_path(category: str, subcategory: str = None, 
                   context: str = None, date_info: dict = None) -> Path:
    """
    Generate smart path based on classification.
    
    Args:
        category: Primary category
        subcategory: Optional subcategory
        context: Optional context (work/personal/media)
        date_info: Optional date information
        
    Returns:
        Path object
    """
    parts = []
    
    # Add context if provided
    if context:
        parts.append(context.capitalize())
    
    # Add category
    parts.append(category.capitalize())
    
    # Add subcategory if provided
    if subcategory:
        parts.append(subcategory.capitalize())
    
    # Add date-based organization if applicable
    if date_info and category in ["photos", "screenshots", "videos"]:
        parts.append(date_info.get("year", "Unknown"))
        parts.append(date_info.get("month", "Unknown"))
    
    return Path(*parts)


def is_project_directory(directory: Path) -> bool:
    """Check if directory is a project."""
    for indicator in PROJECT_INDICATORS:
        if (directory / indicator).exists():
            return True
    return False


def get_file_age_days(file_path: Path) -> int:
    """Get file age in days."""
    from datetime import datetime
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = (datetime.now() - mtime).days
    return age


def should_archive(file_path: Path) -> bool:
    """Determine if file should be archived based on age."""
    if not SUGGEST_ARCHIVE_OLD_FILES:
        return False
    
    age = get_file_age_days(file_path)
    return age > OLD_FILE_THRESHOLD_DAYS


# ================================
# Export Settings
# ================================

__all__ = [
    "SMART_CATEGORIES",
    "ENABLE_ML_CLASSIFICATION",
    "INTELLIGENT_PATTERNS",
    "CONTEXT_KEYWORDS",
    "get_smart_path",
    "is_project_directory",
    "should_archive",
]
