#!/bin/bash
# File Archiver Launcher Script
# This script allows you to run file-archiver from anywhere

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Run the file archiver using the run.py script
python3 run.py "$@"
