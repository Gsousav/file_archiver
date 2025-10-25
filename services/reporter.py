"""
Reporter service.
Generates HTML reports for archive sessions.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..core import ArchiveSession, FileStatus
from ..core.config import REPORT_FILENAME
from ..utils import format_file_size, pluralize

logger = logging.getLogger(__name__)


class Reporter:
    """
    Generates reports for archive sessions.
    """

    def __init__(self):
        """Initialize the reporter."""
        self.template_dir = Path(__file__).parent / "templates"
        self.css_file = self.template_dir / "report_style.css"

    def generate_html_report(
        self, session: ArchiveSession, output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate an HTML report for an archive session.

        Args:
            session: Archive session to report on
            output_path: Optional custom output path

        Returns:
            Path to the generated report
        """
        logger.info(f"Generating HTML report for session {session.session_id}")

        if output_path is None:
            output_path = session.archive_path / REPORT_FILENAME

        # Generate HTML content
        html_content = self._build_html(session)

        # Write to file
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content, encoding="utf-8")
            logger.info(f"Report generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error writing report: {e}")
            raise

    def _build_html(self, session: ArchiveSession) -> str:
        """Build the HTML content for the report."""

        # Read CSS
        css_content = self._get_css_content()

        # Build HTML sections
        header = self._build_header(session)
        summary = self._build_summary(session)
        categories = self._build_categories(session)
        warnings = self._build_warnings(session)
        footer = self._build_footer()

        # Combine into full HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive Report - {session.session_id}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        {header}
        {summary}
        <div class="content">
            {warnings}
            {categories}
        </div>
        {footer}
    </div>
</body>
</html>"""

        return html

    def _get_css_content(self) -> str:
        """Read the CSS file content."""
        try:
            if self.css_file.exists():
                return self.css_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not read CSS file: {e}")

        # Return minimal fallback CSS
        return """
        body { font-family: sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        """

    def _build_header(self, session: ArchiveSession) -> str:
        """Build the header section."""
        status_text = (
            "DRY RUN - No files were moved"
            if session.dry_run
            else "LIVE RUN - Files were moved"
        )

        return f"""
        <div class="header">
            <h1>📁 File Archive Report</h1>
            <div class="session-info">
                <strong>Session:</strong> {session.session_id}<br>
                <strong>Date:</strong> {session.timestamp.strftime("%B %d, %Y at %I:%M %p")}<br>
                <strong>Status:</strong> {status_text}
            </div>
        </div>
        """

    def _build_summary(self, session: ArchiveSession) -> str:
        """Build the summary statistics section."""
        total_size = format_file_size(session.total_size)

        return f"""
        <div class="summary">
            <div class="stat-card">
                <div class="label">Total Files</div>
                <div class="value">{session.total_files}</div>
            </div>
            <div class="stat-card success">
                <div class="label">Moved</div>
                <div class="value">{session.success_count}</div>
            </div>
            <div class="stat-card warning">
                <div class="label">Skipped</div>
                <div class="value">{session.skipped_count}</div>
            </div>
            <div class="stat-card error">
                <div class="label">Errors</div>
                <div class="value">{session.error_count}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Size</div>
                <div class="value">{total_size}</div>
            </div>
            <div class="stat-card warning">
                <div class="label">Duplicates</div>
                <div class="value">{session.duplicate_count}</div>
            </div>
        </div>
        """

    def _build_categories(self, session: ArchiveSession) -> str:
        """Build the categories section."""
        files_by_category = session.files_by_category

        if not files_by_category:
            return '<div class="section"><p>No files to display.</p></div>'

        categories_html = []

        for category, files in sorted(files_by_category.items()):
            if not files:
                continue

            category_size = sum(f.size for f in files)

            files_html = self._build_file_list(files)

            category_html = f"""
            <div class="category-card">
                <div class="category-header">
                    <div class="category-name">📂 {category}</div>
                    <div class="category-count">{len(files)} {pluralize(len(files), 'file', 'files').split()[1]}</div>
                </div>
                <div class="category-files">
                    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.5rem;">
                        Total size: {format_file_size(category_size)}
                    </div>
                    {files_html}
                </div>
            </div>
            """

            categories_html.append(category_html)

        return f"""
        <div class="section">
            <h2 class="section-title">Files by Category</h2>
            <div class="category-grid">
                {"".join(categories_html)}
            </div>
        </div>
        """

    def _build_file_list(self, files: list, max_display: int = 100) -> str:
        """Build the file list HTML."""
        if not files:
            return "<p>No files</p>"

        # Show first N files
        display_files = files[:max_display]
        remaining = len(files) - len(display_files)

        files_html = ['<ul class="file-list">']

        for file in display_files:
            status_class = file.status.value
            status_text = file.status.value.upper()

            file_html = f"""
            <li class="file-item">
                <span class="file-name" title="{file.path}">{file.name}</span>
                <span class="file-size">{file.size_formatted}</span>
                <span class="file-status {status_class}">{status_text}</span>
            </li>
            """
            files_html.append(file_html)

        files_html.append("</ul>")

        if remaining > 0:
            files_html.append(
                f'<p style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">'
                f"... and {remaining} more files</p>"
            )

        return "".join(files_html)

    def _build_warnings(self, session: ArchiveSession) -> str:
        """Build the warnings/errors section."""
        warnings_html = []

        # Duplicate warnings
        if session.duplicate_count > 0:
            duplicate_list = []
            for file1, file2 in session.duplicates[:10]:  # Show first 10
                duplicate_list.append(
                    f"<li><strong>{file1.name}</strong> and <strong>{file2.name}</strong></li>"
                )

            remaining_duplicates = session.duplicate_count - min(
                10, session.duplicate_count
            )
            if remaining_duplicates > 0:
                duplicate_list.append(
                    f"<li>... and {remaining_duplicates} more duplicate pairs</li>"
                )

            warnings_html.append(
                f"""
            <div class="alert alert-warning">
                <strong>⚠️ Duplicates Found:</strong>
                <ul>
                    {"".join(duplicate_list)}
                </ul>
            </div>
            """
            )

        # Error warnings
        error_files = [f for f in session.files if f.status == FileStatus.ERROR]
        if error_files:
            error_list = []
            for file in error_files[:10]:  # Show first 10
                error_msg = file.error or "Unknown error"
                error_list.append(f"<li><strong>{file.name}</strong>: {error_msg}</li>")

            remaining_errors = len(error_files) - min(10, len(error_files))
            if remaining_errors > 0:
                error_list.append(f"<li>... and {remaining_errors} more errors</li>")

            warnings_html.append(
                f"""
            <div class="alert alert-error">
                <strong>❌ Errors:</strong>
                <ul>
                    {"".join(error_list)}
                </ul>
            </div>
            """
            )

        # Dry run notice
        if session.dry_run:
            warnings_html.append(
                """
            <div class="alert alert-info">
                <strong>ℹ️ Dry Run:</strong> This was a preview only. No files were actually moved.
                Run without --dry-run to execute the archive operation.
            </div>
            """
            )

        if not warnings_html:
            return ""

        return f"""
        <div class="section">
            <h2 class="section-title">Notices</h2>
            {"".join(warnings_html)}
        </div>
        """

    def _build_footer(self) -> str:
        """Build the footer section."""
        return f"""
        <div class="footer">
            Generated by File Archiver on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
        """

    def generate_text_summary(self, session: ArchiveSession) -> str:
        """
        Generate a plain text summary of the session.

        Args:
            session: Archive session

        Returns:
            Text summary
        """
        lines = [
            "=" * 60,
            f"File Archive Report: {session.session_id}",
            "=" * 60,
            f"Date: {session.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Status: {'DRY RUN' if session.dry_run else 'LIVE RUN'}",
            "",
            "Summary:",
            f"  Total files: {session.total_files}",
            f"  Moved: {session.success_count}",
            f"  Skipped: {session.skipped_count}",
            f"  Errors: {session.error_count}",
            f"  Duplicates: {session.duplicate_count}",
            f"  Total size: {format_file_size(session.total_size)}",
            "",
        ]

        # Categories
        files_by_category = session.files_by_category
        if files_by_category:
            lines.append("Files by Category:")
            for category, files in sorted(files_by_category.items()):
                size = sum(f.size for f in files)
                lines.append(
                    f"  {category}: {len(files)} files ({format_file_size(size)})"
                )
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
