# Quick Start Guide

Get up and running with File Archiver in 5 minutes!

## Installation

### Method 1: Direct Run (No Installation)

```bash
# 1. Clone or download the project
cd file_archiver

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run!
python -m file_archiver
```

### Method 2: Install as Package

```bash
# Install in development mode
pip install -e .

# Or install from PyPI (when published)
pip install file-archiver

# Run from anywhere
file-archiver
```

## First Run

### Step 1: Start the Program

```bash
python -m file_archiver
```

You'll see:
```
============================================================
📁 File Archiver - Smart File Organization
============================================================

Enter directories to scan (comma-separated):
Example: ~/Downloads, ~/Desktop, ~/Documents
```

### Step 2: Enter Directories

Type the directories you want to scan:

```
Directories: ~/Downloads, ~/Desktop
```

### Step 3: Review Recommendations

The program analyzes your directories and shows recommendations:

```
============================================================
📊 Recommendations (Top Candidates for Organization)
============================================================

1. /Users/you/Downloads
   Score: 8.5/10
   Files: 127
   Types: 15 different extensions
   Size: 2.3 GB

2. /Users/you/Desktop
   Score: 6.2/10
   Files: 43
   Types: 8 different extensions
   Size: 890.5 MB
```

### Step 4: Select Directories

Choose which directories to organize:

```
Select directories to organize:
  • Enter numbers (comma-separated): 1,2,3
  • Enter 'all' to select all
  • Press Enter to cancel

Selection: 1
```

### Step 5: Review Dry-Run

See what will happen before any files are moved:

```
============================================================
🔍 DRY RUN - Preview of Changes
============================================================

📁 Archive location: /Users/you/Archive/Align_20250125_143022
📊 Total files: 127
💾 Total size: 2.3 GB

Files by category:
  • documents: 45 files (850.2 MB)
  • images: 32 files (1.1 GB)
  • videos: 15 files (300.5 MB)
  • code: 20 files (15.3 MB)
  • other: 15 files (50.1 MB)

⚠️  3 duplicate file pairs found
```

### Step 6: Confirm Execution

Decide whether to proceed:

```
============================================================
⚡ Ready to Execute
============================================================

This will move files to the Archive directory.
Type 'yes' to proceed, or anything else to cancel.

Proceed? yes
```

### Step 7: View Results

```
============================================================
✅ Archive Complete!
============================================================

📁 Session: Align_20250125_143022
📊 Results:
  • Moved: 124 files
  • Skipped: 3 files
  • Errors: 0 files

📄 Report: /Users/you/Archive/Align_20250125_143022/archive_report.html
```

## What Gets Created

After running, you'll have:

```
~/Archive/
└── Align_20250125_143022/          # Session folder
    ├── documents/                   # Files organized by category
    │   ├── report.pdf
    │   ├── notes.txt
    │   └── ...
    ├── images/
    │   ├── photo1.jpg
    │   ├── screenshot.png
    │   └── ...
    ├── videos/
    │   └── ...
    ├── code/
    │   └── ...
    └── archive_report.html         # Beautiful HTML report
```

## Important: Understanding Scanning Behavior

**By default, File Archiver scans only files directly in each directory (non-recursive).** 

This means if you scan `~/Desktop`, it will only look at files directly on your Desktop, not files inside `~/Desktop/Projects` or other subdirectories.

### Why Non-Recursive by Default?

- ✅ **Consistency**: What you see in recommendations is exactly what gets organized
- ✅ **No Surprises**: Avoids the "Desktop looks messy but has no files" problem
- ✅ **Precision**: You know exactly which directory level you're cleaning

### Want to Scan Subdirectories Too?

If you want to include all subdirectories, change this in `core/config.py`:

```python
# Change from False to True
RECURSIVE_SCAN = True
```

Then both scanning and organizing will work recursively through all subdirectories.

## Pro Tips

### 1. Test First with Dry-Run

Always review the dry-run before confirming. It shows:
- What files will be moved
- Where they'll go
- Any duplicates or collisions
- Potential errors

### 2. Keep Multiple Sessions

Each run creates a timestamped session folder. This means:
- Easy rollback if needed
- Historical record of what was organized
- No risk of mixing up different archiving runs

### 3. Customize Categories

Edit `core/config.py` to add your own categories:

```python
CATEGORIES = {
    "work_docs": ["docx", "xlsx", "pptx"],
    "personal_photos": ["jpg", "png", "heic"],
    # ... add your own
}
```

### 4. Handle Duplicates

The program detects duplicates automatically using file hashing. Review the warnings to decide which copies to keep.

### 5. View the HTML Report

Open `archive_report.html` in your browser for:
- Visual overview of what was archived
- File lists by category
- Duplicate detection results
- Any errors or warnings

## Common Use Cases

### Cleaning Downloads Folder

```bash
$ python -m file_archiver
Directories: ~/Downloads
Selection: 1
Proceed? yes
```

### Organizing Multiple Folders

```bash
$ python -m file_archiver
Directories: ~/Downloads, ~/Desktop, ~/Documents/Temp
Selection: all
Proceed? yes
```

### Programmatic Usage

```python
from file_archiver import DirectoryScanner, FileClassifier, FileMover

scanner = DirectoryScanner()
classifier = FileClassifier()
mover = FileMover()

# Your custom logic here
```

## Troubleshooting

### Permission Errors

If you see permission errors:
```bash
# Make sure you have read/write access to directories
chmod -R u+rw ~/Downloads
```

### No Recommendations

If no directories are recommended:
- They might have fewer than 10 files
- Try scanning different directories
- Adjust `MIN_FILES_FOR_RECOMMENDATION` in `core/config.py`

### Missing Dependencies

```bash
# Install all optional dependencies
pip install -e ".[full]"
```

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to extend the tool
- Run tests: `pytest tests/`
- Customize `core/config.py` for your needs

## Need Help?

- Check the logs in the Archive folder
- Open an issue on GitHub
- Read the source code - it's well-documented!

Happy organizing! 🎉
