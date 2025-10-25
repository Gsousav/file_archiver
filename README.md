# File Archiver

A maintainable, OOP Python file archiver that organizes files from messy folders into timestamped Archive sessions.

## Features

- 🔍 **Smart Recommendations**: Scans candidate directories and recommends which to organize based on file diversity
- 👀 **Dry-Run Mode**: Preview all changes before making them
- 📂 **File Classification**: Automatic categorization by extension with hooks for content analysis
- 🔒 **Duplicate Detection**: Uses file hashing to identify duplicates (configurable)
- ⚠️ **Collision Handling**: Multiple policies (suffix/hash/skip) for file conflicts
- 📊 **Beautiful Reports**: HTML reports with separated CSS for each archiving session

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Archiver

```bash
python -m file_archiver
```

### 3. Follow CLI Prompts

1. Enter directories to scan (comma-separated)
2. Review recommendations
3. Select folders to organize
4. Review dry-run plan
5. Confirm execution

## Project Structure

```
file_archiver/
├── __init__.py
├── __main__.py              # Entry point
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuration & categories
│   └── models.py            # Data models
├── services/
│   ├── __init__.py
│   ├── scanner.py           # Directory scanning
│   ├── classifier.py        # File classification
│   ├── content_analyzer.py  # Content-based analysis
│   ├── mover.py             # File moving logic
│   └── reporter.py          # Report generation
├── ui/
│   ├── __init__.py
│   └── cli.py               # Command-line interface
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Utility functions
└── requirements.txt
```

## Configuration

Edit `core/config.py` to customize:

- File categories and extensions
- Duplicate detection settings
- Collision handling policies
- Archive directory location

## Extending

### Add New Categories

```python
# In core/config.py
CATEGORIES = {
    "my_category": ["ext1", "ext2"],
    # ...
}
```

### Add Content Analysis

```python
# In services/content_analyzer.py
class ContentAnalyzer:
    def analyze_custom_type(self, file_path: Path) -> Dict[str, Any]:
        # Your custom logic
        pass
```

### Build a GUI

The `FileArchiverApp` class is UI-agnostic. Create a GUI wrapper:

```python
from file_archiver.services.scanner import DirectoryScanner
from file_archiver.services.classifier import FileClassifier
# ... use the same services with your GUI
```

## Design Philosophy

### Why This Architecture?

- **OOP + Single Responsibility**: Each class does one job (scan, classify, move, report)
- **Dry-Run by Default**: Users see what will happen before committing
- **Recommendation Engine**: Scores folders by file diversity and size
- **Separation of Concerns**: Content analyzer is separate for future paid features (OCR, ML)
- **Session-Based**: Everything for a run goes into `Archive/Align_<timestamp>` for easy rollback

## Dependencies

- **PyPDF2**: PDF metadata extraction
- **python-magic**: File type detection (optional)
- **Pillow**: Image processing (optional)
- **imagehash**: Perceptual image hashing (optional)

## Examples

### Basic Usage

```bash
$ python -m file_archiver
📁 File Archiver - Smart File Organization
==========================================

Enter directories to scan (comma-separated): ~/Downloads, ~/Desktop
Scanning directories...

📊 Recommendations (Top 3):
1. ~/Downloads (Score: 8.5) - 127 files, 15 types
2. ~/Desktop (Score: 6.2) - 43 files, 8 types

Select folders to organize (comma-separated, or 'all'): 1
```

### Dry-Run Output

```
🔍 DRY RUN - No files will be moved yet
========================================

Documents/
  ├── report.pdf (2.3 MB)
  ├── notes.txt (15 KB)
  └── ...

Images/
  ├── photo1.jpg (4.1 MB) [DUPLICATE of photo1_copy.jpg]
  ├── ...

⚠️  3 duplicates found
⚠️  1 collision will be renamed
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Roadmap

- [ ] GUI interface (PyQt/Tkinter)
- [ ] OCR for document text extraction
- [ ] ML-based smart categorization
- [ ] Cloud storage integration
- [ ] Undo/rollback functionality
- [ ] Scheduling/automation support
