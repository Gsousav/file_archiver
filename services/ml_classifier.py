"""
Enhanced ML-powered file classifier.
Uses multiple techniques to intelligently categorize files.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class MLFileClassifier:
    """
    Intelligent file classifier using ML and heuristics.
    """
    
    def __init__(self):
        """Initialize the ML classifier."""
        self._load_patterns()
        self._init_ml_models()
    
    def _load_patterns(self):
        """Load regex patterns for file classification."""
        self.patterns = {
            # Work documents
            'work_report': [
                r'report.*\d{4}',
                r'quarterly.*report',
                r'annual.*report',
                r'(q[1-4]|fy).*\d{4}',
            ],
            'invoice': [
                r'invoice.*\d+',
                r'bill.*\d+',
                r'receipt.*\d+',
                r'inv[-_]\d+',
            ],
            'contract': [
                r'contract.*',
                r'agreement.*',
                r'nda.*',
                r'terms.*conditions',
            ],
            'presentation': [
                r'(slides?|deck|presentation).*',
                r'.*pitch.*',
            ],
            
            # Personal
            'screenshot': [
                r'screen\s*shot.*',
                r'screenshot.*',
                r'capture.*\d{4}',
                r'recording.*\d{4}',
            ],
            'photo': [
                r'img.*\d{4}',
                r'dsc.*\d{4}',
                r'photo.*\d{4}',
                r'\d{4}[-_]\d{2}[-_]\d{2}',  # Date format
            ],
            'resume': [
                r'(cv|resume|curriculum).*',
                r'.*resume.*',
            ],
            
            # Code
            'config': [
                r'\.?config',
                r'\.env.*',
                r'settings.*',
                r'\..*rc$',  # .vimrc, .bashrc, etc.
            ],
            'readme': [
                r'readme.*',
                r'license.*',
                r'changelog.*',
            ],
            
            # Media
            'music_album': [
                r'.*\d{4}.*album.*',
                r'.*-.*\d{4}',  # Artist - Album 2024
            ],
            'podcast': [
                r'podcast.*ep\d+',
                r'episode.*\d+',
            ],
            'tutorial': [
                r'tutorial.*',
                r'how.*to.*',
                r'guide.*',
                r'.*course.*',
            ],
            
            # Downloads
            'installer': [
                r'setup.*',
                r'install.*',
                r'.*installer.*',
            ],
            'compressed': [
                r'.*\.(zip|rar|7z|tar|gz)$',
                r'archive.*',
                r'backup.*',
            ],
        }
    
    def _init_ml_models(self):
        """Initialize ML models for classification."""
        # Check for optional ML dependencies
        self.has_transformers = False
        self.has_opencv = False
        
        try:
            # Text classification model (optional)
            from transformers import pipeline
            self.text_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            self.has_transformers = True
            logger.info("Loaded transformers model for text classification")
        except ImportError:
            logger.debug("transformers not available, using heuristic classification")
        
        try:
            # Image classification (optional)
            import cv2
            self.has_opencv = True
            logger.info("OpenCV available for image analysis")
        except ImportError:
            logger.debug("OpenCV not available")
    
    def classify_intelligent(self, file_path: Path, content: Optional[str] = None) -> Dict[str, any]:
        """
        Intelligently classify a file using multiple techniques.
        
        Args:
            file_path: Path to the file
            content: Optional file content for text analysis
            
        Returns:
            Classification result with category, subcategory, and confidence
        """
        result = {
            'primary_category': 'uncategorized',
            'subcategory': None,
            'context': None,  # work/personal/media
            'date_category': None,  # Year/Month for time-based organization
            'confidence': 0.0,
            'tags': [],
            'suggested_path': None,
        }
        
        # 1. Filename pattern matching
        filename_result = self._classify_by_filename(file_path)
        if filename_result['confidence'] > 0.7:
            result.update(filename_result)
        
        # 2. Extension-based classification
        ext_result = self._classify_by_extension(file_path)
        if result['confidence'] < 0.5:
            result.update(ext_result)
        
        # 3. Date extraction for time-based organization
        date_info = self._extract_date_info(file_path)
        if date_info:
            result['date_category'] = date_info
        
        # 4. Content-based classification (if content provided)
        if content and self.has_transformers:
            content_result = self._classify_by_content(content)
            if content_result['confidence'] > result['confidence']:
                result.update(content_result)
        
        # 5. Context detection (work vs personal)
        result['context'] = self._detect_context(file_path, content)
        
        # 6. Generate suggested path
        result['suggested_path'] = self._generate_smart_path(result)
        
        return result
    
    def _classify_by_filename(self, file_path: Path) -> Dict[str, any]:
        """Classify based on filename patterns."""
        filename = file_path.name.lower()
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    return {
                        'primary_category': category,
                        'confidence': 0.8,
                        'tags': [category],
                    }
        
        return {'confidence': 0.0}
    
    def _classify_by_extension(self, file_path: Path) -> Dict[str, any]:
        """Classify based on file extension."""
        ext = file_path.suffix.lower().lstrip('.')
        
        # Enhanced category mapping
        category_map = {
            # Documents - Work
            'pdf': ('documents', 'work', 0.6),
            'docx': ('documents', 'work', 0.7),
            'doc': ('documents', 'work', 0.7),
            'xlsx': ('spreadsheets', 'work', 0.8),
            'xls': ('spreadsheets', 'work', 0.8),
            'pptx': ('presentations', 'work', 0.8),
            'ppt': ('presentations', 'work', 0.8),
            
            # Code
            'py': ('code', 'work', 0.7),
            'js': ('code', 'work', 0.7),
            'ts': ('code', 'work', 0.7),
            'java': ('code', 'work', 0.7),
            'cpp': ('code', 'work', 0.7),
            'go': ('code', 'work', 0.7),
            'rs': ('code', 'work', 0.7),
            'html': ('code', 'work', 0.6),
            'css': ('code', 'work', 0.6),
            'json': ('config', 'work', 0.7),
            'yaml': ('config', 'work', 0.7),
            'yml': ('config', 'work', 0.7),
            
            # Images - Personal
            'jpg': ('photos', 'personal', 0.5),
            'jpeg': ('photos', 'personal', 0.5),
            'png': ('photos', 'personal', 0.4),  # Could be screenshot
            'heic': ('photos', 'personal', 0.8),
            'raw': ('photos', 'personal', 0.9),
            
            # Media
            'mp3': ('music', 'media', 0.7),
            'wav': ('music', 'media', 0.7),
            'flac': ('music', 'media', 0.8),
            'mp4': ('videos', 'media', 0.6),
            'mov': ('videos', 'media', 0.7),
            'avi': ('videos', 'media', 0.7),
            'mkv': ('videos', 'media', 0.7),
            
            # Downloads
            'zip': ('compressed', 'downloads', 0.8),
            'rar': ('compressed', 'downloads', 0.8),
            '7z': ('compressed', 'downloads', 0.8),
            'tar': ('compressed', 'downloads', 0.8),
            'gz': ('compressed', 'downloads', 0.8),
            'dmg': ('installers', 'downloads', 0.9),
            'exe': ('installers', 'downloads', 0.9),
            'msi': ('installers', 'downloads', 0.9),
            
            # Books
            'epub': ('books', 'media', 0.9),
            'mobi': ('books', 'media', 0.9),
        }
        
        if ext in category_map:
            category, context, confidence = category_map[ext]
            return {
                'primary_category': category,
                'context': context,
                'confidence': confidence,
                'tags': [category],
            }
        
        return {'confidence': 0.0}
    
    def _extract_date_info(self, file_path: Path) -> Optional[Dict[str, str]]:
        """Extract date information from filename or metadata."""
        filename = file_path.name
        
        # Try to extract date from filename
        date_patterns = [
            r'(\d{4})[-_](\d{2})[-_](\d{2})',  # 2024-01-15
            r'(\d{2})[-_](\d{2})[-_](\d{4})',  # 15-01-2024
            r'(\d{4})(\d{2})(\d{2})',          # 20240115
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    groups = match.groups()
                    # Try to parse as date
                    if len(groups[0]) == 4:  # Year first
                        year, month, day = groups
                    else:  # Day first
                        day, month, year = groups
                    
                    date = datetime(int(year), int(month), int(day))
                    return {
                        'year': str(date.year),
                        'month': date.strftime('%B'),
                        'month_num': date.strftime('%m'),
                    }
                except (ValueError, IndexError):
                    continue
        
        # Try file modification time as fallback
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            # Only use if file is less than 2 years old
            if (datetime.now() - mtime).days < 730:
                return {
                    'year': str(mtime.year),
                    'month': mtime.strftime('%B'),
                    'month_num': mtime.strftime('%m'),
                }
        except Exception:
            pass
        
        return None
    
    def _classify_by_content(self, content: str) -> Dict[str, any]:
        """Classify based on file content using ML."""
        if not self.has_transformers or not content:
            return {'confidence': 0.0}
        
        # Truncate content for ML model
        content_sample = content[:500]
        
        candidate_labels = [
            "work document", "personal document", "code", 
            "financial document", "medical document", "legal document",
            "tutorial", "notes", "communication"
        ]
        
        try:
            result = self.text_classifier(content_sample, candidate_labels)
            top_label = result['labels'][0]
            confidence = result['scores'][0]
            
            # Map ML labels to our categories
            label_map = {
                'work document': ('documents', 'work'),
                'personal document': ('documents', 'personal'),
                'code': ('code', 'work'),
                'financial document': ('finance', 'personal'),
                'medical document': ('health', 'personal'),
                'legal document': ('legal', 'work'),
                'tutorial': ('tutorials', 'media'),
                'notes': ('notes', 'personal'),
                'communication': ('communications', 'personal'),
            }
            
            if top_label in label_map and confidence > 0.6:
                category, context = label_map[top_label]
                return {
                    'primary_category': category,
                    'context': context,
                    'confidence': confidence,
                    'tags': [top_label],
                }
        except Exception as e:
            logger.error(f"ML classification error: {e}")
        
        return {'confidence': 0.0}
    
    def _detect_context(self, file_path: Path, content: Optional[str] = None) -> str:
        """Detect if file is work, personal, or media related."""
        filename = file_path.name.lower()
        
        # Work indicators
        work_keywords = [
            'work', 'project', 'client', 'meeting', 'presentation',
            'report', 'invoice', 'contract', 'proposal', 'business',
            'company', 'office', 'corporate'
        ]
        
        # Personal indicators
        personal_keywords = [
            'personal', 'family', 'vacation', 'receipt', 'bill',
            'medical', 'insurance', 'tax', 'bank', 'home'
        ]
        
        # Media indicators
        media_keywords = [
            'movie', 'song', 'album', 'podcast', 'video', 'music',
            'episode', 'season', 'tutorial', 'course', 'book'
        ]
        
        # Check filename
        for keyword in work_keywords:
            if keyword in filename:
                return 'work'
        
        for keyword in personal_keywords:
            if keyword in filename:
                return 'personal'
        
        for keyword in media_keywords:
            if keyword in filename:
                return 'media'
        
        # Default based on file type
        ext = file_path.suffix.lower().lstrip('.')
        if ext in ['py', 'js', 'java', 'cpp', 'go', 'rs', 'docx', 'xlsx', 'pptx']:
            return 'work'
        elif ext in ['jpg', 'png', 'heic', 'mp3', 'mp4']:
            return 'personal'
        
        return 'uncategorized'
    
    def _generate_smart_path(self, classification: Dict[str, any]) -> Path:
        """Generate intelligent file path based on classification."""
        parts = []
        
        # 1. Context level (Work/Personal/Media/Downloads)
        context = classification.get('context', 'uncategorized')
        if context and context != 'uncategorized':
            parts.append(context.capitalize())
        
        # 2. Primary category
        category = classification.get('primary_category', 'other')
        if category and category != 'uncategorized':
            parts.append(category.capitalize())
        
        # 3. Subcategory (if exists)
        subcategory = classification.get('subcategory')
        if subcategory:
            parts.append(subcategory.capitalize())
        
        # 4. Date-based organization for certain categories
        if category in ['photos', 'screenshots', 'videos']:
            date_info = classification.get('date_category')
            if date_info:
                parts.append(date_info['year'])
                parts.append(date_info['month'])
        
        # Build path
        if not parts:
            parts = ['Uncategorized']
        
        return Path(*parts)


# Usage example
if __name__ == "__main__":
    classifier = MLFileClassifier()
    
    test_files = [
        Path("Q4_2024_Report.pdf"),
        Path("IMG_20240115_vacation.jpg"),
        Path("setup_installer.dmg"),
        Path("main.py"),
    ]
    
    for file in test_files:
        result = classifier.classify_intelligent(file)
        print(f"\n{file.name}:")
        print(f"  Category: {result['primary_category']}")
        print(f"  Context: {result['context']}")
        print(f"  Path: {result['suggested_path']}")
        print(f"  Confidence: {result['confidence']:.2f}")
