import sys
from pathlib import Path

# Add the parent directory to sys.path so file_archiver is importable as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import from the package properly
from file_archiver.ui.cli_beautiful import main

if __name__ == "__main__":
    main()
