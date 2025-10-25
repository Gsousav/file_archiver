"""
Command-line interface for File Archiver.
Provides interactive CLI for organizing files.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from ..core import DirectoryScore, ArchiveSession
from ..services import (
    DirectoryScanner,
    FileClassifier,
    FileMover,
    Reporter,
)
from ..utils import pluralize, format_file_size

logger = logging.getLogger(__name__)


class CLI:
    """
    Command-line interface for File Archiver.
    """

    def __init__(self):
        """Initialize the CLI."""
        self.scanner = DirectoryScanner()
        self.classifier = FileClassifier(enable_hashing=True)
        self.mover = FileMover()
        self.reporter = Reporter()

    def run(self):
        """Run the interactive CLI."""
        self.print_header()

        try:
            # Step 1: Get directories to scan
            directories = self.get_directories_input()
            if not directories:
                print("\n❌ No directories provided. Exiting.")
                return

            # Step 2: Scan and show recommendations
            recommendations = self.scanner.get_recommendations(directories, top_n=10)
            if not recommendations:
                print("\n📂 No directories found that need organization.")
                print("   (Directories must have at least 10 files)")
                return

            self.display_recommendations(recommendations)

            # Step 3: Let user select directories
            selected_dirs = self.select_directories(recommendations)
            if not selected_dirs:
                print("\n❌ No directories selected. Exiting.")
                return

            # Step 4: Classify files
            print(
                f"\n🔍 Analyzing files in {len(selected_dirs)} {pluralize(len(selected_dirs), 'directory', 'directories').split()[1]}..."
            )
            files = self.classifier.classify_multiple_directories(selected_dirs)

            if not files:
                print("❌ No files found to archive.")
                return

            print(f"✅ Found {len(files)} files to organize")

            # Step 5: Find duplicates
            duplicates = self.classifier.find_duplicates(files)
            if duplicates:
                print(f"⚠️  Found {len(duplicates)} duplicate file pairs")

            # Step 6: Create dry-run session
            print("\n📋 Creating archive plan...")
            session = self.mover.create_session(selected_dirs, files, dry_run=True)
            session.duplicates = duplicates

            plan = self.mover.plan_archive(session)

            # Step 7: Show dry-run
            self.display_dry_run(plan)

            # Step 8: Confirm execution
            if not self.confirm_execution():
                print("\n❌ Archive cancelled. No files were moved.")
                return

            # Step 9: Execute archive
            print("\n🚀 Executing archive operation...")
            live_session = self.mover.create_session(
                selected_dirs, files, dry_run=False
            )
            live_session.duplicates = duplicates

            # Plan again for live session
            self.mover.plan_archive(live_session)

            # Execute
            result_session = self.mover.execute_archive(live_session)

            # Step 10: Generate report
            print("\n📊 Generating report...")
            report_path = self.reporter.generate_html_report(result_session)

            # Step 11: Show summary
            self.display_summary(result_session, report_path)

        except KeyboardInterrupt:
            print("\n\n❌ Interrupted by user. Exiting.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
            sys.exit(1)

    def print_header(self):
        """Print the application header."""
        print("\n" + "=" * 60)
        print("📁 File Archiver - Smart File Organization")
        print("=" * 60)
        print()

    def get_directories_input(self) -> List[Path]:
        """
        Get directories from user input.

        Returns:
            List of directory paths
        """
        print("Enter directories to scan (comma-separated):")
        print("Example: ~/Downloads, ~/Desktop, ~/Documents")
        print()

        user_input = input("Directories: ").strip()

        if not user_input:
            return []

        # Parse input
        dir_strings = [d.strip() for d in user_input.split(",")]
        directories: List[Path] = []

        for dir_str in dir_strings:
            if not dir_str:
                continue

            # Expand user home directory
            path = Path(dir_str).expanduser().resolve()

            if not path.exists():
                print(f"⚠️  Directory not found: {path}")
                continue

            if not path.is_dir():
                print(f"⚠️  Not a directory: {path}")
                continue

            directories.append(path)

        return directories

    def display_recommendations(self, recommendations: List[DirectoryScore]):
        """Display directory recommendations."""
        print("\n" + "=" * 60)
        print("📊 Recommendations (Top Candidates for Organization)")
        print("=" * 60)
        print()

        if not recommendations:
            print("No recommendations available.")
            return

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.path}")
            print(f"   Score: {rec.score:.1f}/10")
            print(f"   Files: {rec.total_files}")
            print(f"   Types: {rec.file_types} different extensions")
            print(f"   Size: {rec.size_formatted}")
            print()

    def select_directories(self, recommendations: List[DirectoryScore]) -> List[Path]:
        """
        Let user select directories to organize.

        Args:
            recommendations: List of recommended directories

        Returns:
            List of selected directory paths
        """
        print("=" * 60)
        print("Select directories to organize:")
        print("  • Enter numbers (comma-separated): 1,2,3")
        print("  • Enter 'all' to select all")
        print("  • Press Enter to cancel")
        print()

        user_input = input("Selection: ").strip().lower()

        if not user_input:
            return []

        if user_input == "all":
            return [rec.path for rec in recommendations]

        # Parse numbers
        selected: List[Path] = []

        try:
            numbers = [int(n.strip()) for n in user_input.split(",")]

            for num in numbers:
                if 1 <= num <= len(recommendations):
                    selected.append(recommendations[num - 1].path)
                else:
                    print(f"⚠️  Invalid selection: {num}")

        except ValueError:
            print("⚠️  Invalid input. Please enter numbers separated by commas.")
            return []

        return selected

    def display_dry_run(self, plan):
        """Display the dry-run plan."""
        print("\n" + "=" * 60)
        print("🔍 DRY RUN - Preview of Changes")
        print("=" * 60)
        print()

        session = plan.session

        # Summary
        print(f"📁 Archive location: {session.archive_path}")
        print(f"📊 Total files: {session.total_files}")
        print(f"💾 Total size: {format_file_size(session.total_size)}")
        print()

        # Files by category
        files_by_category = session.files_by_category

        print("Files by category:")
        for category, files in sorted(files_by_category.items()):
            size = sum(f.size for f in files)
            print(f"  • {category}: {len(files)} files ({format_file_size(size)})")
        print()

        # Warnings
        if plan.warnings:
            print("⚠️  Warnings:")
            for warning in plan.warnings[:5]:  # Show first 5
                print(f"  • {warning}")
            if len(plan.warnings) > 5:
                print(f"  ... and {len(plan.warnings) - 5} more warnings")
            print()

        # Duplicates
        if session.duplicate_count > 0:
            print(f"⚠️  {session.duplicate_count} duplicate file pairs found")
            print()

    def confirm_execution(self) -> bool:
        """
        Ask user to confirm execution.

        Returns:
            True if confirmed, False otherwise
        """
        print("=" * 60)
        print("⚡ Ready to Execute")
        print("=" * 60)
        print()
        print("This will move files to the Archive directory.")
        print("Type 'yes' to proceed, or anything else to cancel.")
        print()

        user_input = input("Proceed? ").strip().lower()

        return user_input in ["yes", "y"]

    def display_summary(self, session: ArchiveSession, report_path: Path):
        """Display the final summary."""
        print("\n" + "=" * 60)
        print("✅ Archive Complete!")
        print("=" * 60)
        print()

        print(f"📁 Session: {session.session_id}")
        print(f"📊 Results:")
        print(f"  • Moved: {session.success_count} files")
        print(f"  • Skipped: {session.skipped_count} files")
        print(f"  • Errors: {session.error_count} files")
        print()

        print(f"📄 Report: {report_path}")
        print()

        # Show text summary
        text_summary = self.reporter.generate_text_summary(session)
        print(text_summary)


def main():
    """Main entry point for the CLI."""
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Run CLI
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
