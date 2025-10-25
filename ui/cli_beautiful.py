
"""
Beautiful, Apple-style CLI interface for File Archiver.
Clean, minimal, and delightful to use.
"""

import logging
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.tree import Tree
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich import box
from rich.style import Style

from ..core import DirectoryScore, ArchiveSession
from ..services import (
    DirectoryScanner,
    FileClassifier,
    FileMover,
    Reporter,
)
from ..utils import pluralize, format_file_size, create_directory_safe

logger = logging.getLogger(__name__)

# Disable verbose logging for clean output
logging.getLogger().setLevel(logging.ERROR)


class BeautifulCLI:
    """
    Apple-style CLI with rich formatting.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.scanner = DirectoryScanner()
        self.classifier = FileClassifier(enable_hashing=True)
        self.mover = None  # Will be initialized after getting save location
        self.reporter = Reporter()
        
        # Apple-inspired color scheme
        self.colors = {
            'primary': '#007AFF',    # Apple blue
            'success': '#34C759',    # Apple green
            'warning': '#FF9500',    # Apple orange
            'error': '#FF3B30',      # Apple red
            'secondary': '#8E8E93',  # Apple gray
            'background': '#F2F2F7', # Apple light gray
        }
    
    def run(self):
        """Run the beautiful CLI."""
        try:
            self._show_welcome()
            
            # Step 1: Ask what user wants to do
            mode = self._ask_mode()
            
            # Step 2: Get directories based on mode
            if mode == "smart":
                directories = self._smart_scan()
            elif mode == "quick":
                directories = [Path.home() / "Downloads"]
            else:  # manual
                directories = self._get_directories()
            
            if not directories:
                self.console.print("\n[dim]No directories selected. Goodbye! 👋[/dim]")
                return
            
            # Step 2: Scan with progress
            recommendations = self._scan_directories(directories)
            if not recommendations:
                self._show_no_recommendations()
                return
            
            # Step 3: Show recommendations
            self._show_recommendations(recommendations)
            
            # Step 4: Select directories
            selected_dirs = self._select_directories(recommendations)
            if not selected_dirs:
                self.console.print("\n[dim]No directories selected. Goodbye! 👋[/dim]")
                return
            
            # Step 4.5: Ask where to save the organized files
            use_source_parent = self._ask_save_location(selected_dirs)
            self.mover = FileMover(use_source_parent=use_source_parent)
            
            # Step 5: Analyze files
            files = self._analyze_files(selected_dirs)
            if not files:
                self.console.print("\n[yellow]No files found to organize.[/yellow]")
                return
            
            # Step 6: Find duplicates
            duplicates = self._find_duplicates(files)
            
            # Step 7: Create session and show preview
            session = self.mover.create_session(selected_dirs, files, dry_run=True)
            session.duplicates = duplicates
            plan = self.mover.plan_archive(session)
            
            self._show_beautiful_preview(plan)
            
            # Step 8: Confirm
            if not self._confirm_execution():
                self.console.print("\n[dim]Operation cancelled. No files were moved. 👋[/dim]")
                return
            
            # Step 9: Execute with progress
            result_session = self._execute_with_progress(selected_dirs, files, duplicates)
            
            # Step 10: Show success
            self._show_success(result_session)
            
        except KeyboardInterrupt:
            self.console.print("\n\n[dim]Operation cancelled. Goodbye! 👋[/dim]")
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
    
    def _show_welcome(self):
        """Show beautiful welcome screen."""
        self.console.clear()
        
        welcome = Panel.fit(
            "[bold]File Archiver[/bold]\n"
            "[dim]Intelligent file organization with AI[/dim]",
            border_style="blue",
            padding=(1, 4)
        )
        
        self.console.print("\n")
        self.console.print(welcome)
        self.console.print()
    
    def _ask_mode(self) -> str:
        """Ask user which mode they want."""
        self.console.print("[bold]What would you like to do?[/bold]\n")
        
        options_table = Table(
            show_header=False,
            border_style="dim",
            box=None,
            padding=(0, 2)
        )
        
        options_table.add_column(style="blue", width=3)
        options_table.add_column(style="")
        
        options_table.add_row("1", "🔍 Smart Scan - Find messy folders automatically")
        options_table.add_row("2", "📁 Manual - Choose specific folders")
        options_table.add_row("3", "⚡ Quick - Just ~/Downloads")
        
        self.console.print(options_table)
        self.console.print()
        
        choice = Prompt.ask(
            "[blue]›[/blue] Choice",
            choices=["1", "2", "3"],
            default="1"
        )
        
        mode_map = {"1": "smart", "2": "manual", "3": "quick"}
        return mode_map[choice]
    
    def _smart_scan(self) -> List[Path]:
        """Perform smart scan to find messy directories."""
        self.console.print("\n[bold]Smart Scan[/bold]\n")
        
        # Ask scope
        scope_table = Table(
            show_header=False,
            border_style="dim",
            box=None,
            padding=(0, 2)
        )
        
        scope_table.add_column(style="blue", width=3)
        scope_table.add_column(style="")
        
        scope_table.add_row("1", "🏠 Entire Home folder")
        scope_table.add_row("2", "📂 Common locations (Downloads, Desktop, Documents)")
        scope_table.add_row("3", "💼 Work folders (Projects, Code, Work)")
        scope_table.add_row("4", "🎯 Custom locations")
        
        self.console.print(scope_table)
        self.console.print()
        
        scope = Prompt.ask(
            "[blue]›[/blue] Scan scope",
            choices=["1", "2", "3", "4"],
            default="2"
        )
        
        # Get directories to scan based on scope
        scan_dirs = []
        home = Path.home()
        
        if scope == "1":
            # Entire home
            scan_dirs = [home]
        elif scope == "2":
            # Common locations
            common = ["Downloads", "Desktop", "Documents", "Pictures"]
            scan_dirs = [home / d for d in common if (home / d).exists()]
        elif scope == "3":
            # Work folders
            work = ["Projects", "Code", "Work", "dev", "Development"]
            scan_dirs = [home / d for d in work if (home / d).exists()]
        else:
            # Custom
            return self._get_directories()
        
        # Perform deep scan
        self.console.print("\n[bold]Scanning your Mac...[/bold]")
        
        all_directories = []
        scanned_count = 0
        
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="blue"),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Finding folders...", total=None)
            
            for scan_dir in scan_dirs:
                try:
                    for item in scan_dir.rglob("*"):
                        if item.is_dir() and not self._should_skip_dir(item):
                            all_directories.append(item)
                            scanned_count += 1
                            
                            if scanned_count % 50 == 0:
                                progress.update(task, description=f"Checked {scanned_count:,} folders...")
                except PermissionError:
                    continue
            
            progress.update(task, description=f"Checked {scanned_count:,} folders")
        
        # Scan all found directories
        self.console.print(f"[green]✓[/green] Found {len(all_directories)} folders\n")
        
        # Now scan them for messiness
        recommendations = self._scan_directories(all_directories)
        
        if not recommendations:
            self.console.print("[green]✓[/green] All folders are clean!\n")
            return []
        
        self.console.print(f"[yellow]Found {len(recommendations)} messy folders![/yellow] 🎯\n")
        
        return [rec.path for rec in recommendations]
    
    def _should_skip_dir(self, directory: Path) -> bool:
        """Check if directory should be skipped during scan."""
        skip_names = {
            '.git', 'node_modules', '.venv', 'venv', '__pycache__',
            '.cache', 'Library', '.Trash', '.npm', '.cargo',
            'Applications', 'System', '.local', '.config'
        }
        
        # Skip hidden dirs (except user home)
        if directory.name.startswith('.') and directory != Path.home():
            return True
        
        # Skip system dirs
        if directory.name in skip_names:
            return True
        
        # Skip if no read permission
        try:
            next(directory.iterdir(), None)
            return False
        except PermissionError:
            return True
    
    def _get_directories(self) -> List[Path]:
        """Get directories from user with beautiful prompt."""
        self.console.print("[bold]Select Folders to Organize[/bold]")
        self.console.print("[dim]Examples: ~/Downloads, ~/Desktop, ~/Documents[/dim]\n")
        
        user_input = Prompt.ask(
            "[blue]›[/blue] Folders",
            default="~/Downloads"
        )
        
        if not user_input or user_input.strip() == "":
            return []
        
        directories = []
        for dir_str in user_input.split(","):
            path = Path(dir_str.strip()).expanduser().resolve()
            if path.exists() and path.is_dir():
                directories.append(path)
            else:
                self.console.print(f"[dim]  ⚠ Skipping {path} (not found)[/dim]")
        
        return directories
    
    def _scan_directories(self, directories: List[Path]) -> List[DirectoryScore]:
        """Scan directories with beautiful progress."""
        self.console.print("\n[bold]Analyzing Folders[/bold]")
        
        recommendations = []
        
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="blue", finished_style="green"),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task(
                f"Scanning {len(directories)} folders...",
                total=len(directories)
            )
            
            for directory in directories:
                score = self.scanner.scan_directory(directory)
                recommendations.append(score)
                progress.advance(task)
        
        # Filter and sort
        filtered = [r for r in recommendations if r.total_files >= 10]
        sorted_recs = sorted(filtered, key=lambda x: x.score, reverse=True)
        
        return sorted_recs[:10]
    
    def _show_no_recommendations(self):
        """Show message when no folders need organization."""
        panel = Panel(
            "[green]✓[/green] All folders are already organized!\n"
            "[dim]No folders need attention right now.[/dim]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print("\n")
        self.console.print(panel)
    
    def _show_recommendations(self, recommendations: List[DirectoryScore]):
        """Show recommendations in beautiful table."""
        self.console.print("\n[bold]Recommendations[/bold]")
        self.console.print("[dim]Folders that need organization[/dim]\n")
        
        table = Table(
            show_header=True,
            header_style="bold",
            border_style="dim",
            box=box.SIMPLE,
            padding=(0, 1)
        )
        
        table.add_column("#", style="dim", width=3)
        table.add_column("Folder", style="cyan")
        table.add_column("Files", justify="right", style="blue")
        table.add_column("Types", justify="right", style="magenta")
        table.add_column("Size", justify="right", style="yellow")
        table.add_column("Score", justify="right")
        
        for i, rec in enumerate(recommendations, 1):
            # Score with emoji
            score_display = self._score_emoji(rec.score)
            
            table.add_row(
                str(i),
                rec.path.name,
                str(rec.total_files),
                str(rec.file_types),
                rec.size_formatted,
                score_display
            )
        
        self.console.print(table)
        self.console.print()
    
    def _score_emoji(self, score: float) -> str:
        """Get emoji representation of score."""
        if score >= 8:
            return f"[red]{score:.1f}/10 🔥[/red]"
        elif score >= 6:
            return f"[yellow]{score:.1f}/10 ⚠️[/yellow]"
        else:
            return f"[green]{score:.1f}/10 ✓[/green]"
    
    def _select_directories(self, recommendations: List[DirectoryScore]) -> List[Path]:
        """Let user select directories with beautiful prompt."""
        self.console.print("[bold]Select Folders[/bold]")
        self.console.print("[dim]Enter numbers (e.g., 1,2,3) or 'all'[/dim]\n")
        
        choice = Prompt.ask(
            "[blue]›[/blue] Selection",
            default="1"
        )
        
        if not choice or choice.strip() == "":
            return []
        
        if choice.lower() == "all":
            return [rec.path for rec in recommendations]
        
        selected = []
        try:
            numbers = [int(n.strip()) for n in choice.split(",")]
            for num in numbers:
                if 1 <= num <= len(recommendations):
                    selected.append(recommendations[num - 1].path)
        except ValueError:
            self.console.print("[red]Invalid selection[/red]")
            return []
        
        return selected
    
    def _ask_save_location(self, selected_dirs: List[Path]) -> bool:
        """Ask user where to save the organized files."""
        self.console.print("\n[bold]Where should we save the organized files?[/bold]\n")
        
        location_table = Table(
            show_header=False,
            border_style="dim",
            box=None,
            padding=(0, 2)
        )
        
        location_table.add_column(style="blue", width=3)
        location_table.add_column(style="")
        
        # Show options based on selected directories
        if len(selected_dirs) == 1:
            parent = selected_dirs[0].parent
            location_table.add_row("1", f"💻 Desktop (~/Desktop)")
            location_table.add_row("2", f"📂 Next to source folder ({parent})")
        else:
            location_table.add_row("1", f"💻 Desktop (~/Desktop)")
            location_table.add_row("2", f"📂 Next to first source folder")
        
        self.console.print(location_table)
        self.console.print()
        
        choice = Prompt.ask(
            "[blue]›[/blue] Location",
            choices=["1", "2"],
            default="1"
        )
        
        use_source_parent = (choice == "2")
        
        if use_source_parent:
            if len(selected_dirs) == 1:
                save_location = selected_dirs[0].parent
            else:
                save_location = selected_dirs[0].parent
            self.console.print(f"[green]✓[/green] Will save to: {save_location}\n")
        else:
            self.console.print(f"[green]✓[/green] Will save to: ~/Desktop\n")
        
        return use_source_parent
    
    def _analyze_files(self, directories: List[Path]) -> List:
        """Analyze files with progress."""
        self.console.print("\n[bold]Analyzing Files[/bold]")
        
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Classifying files...", total=None)
            files = self.classifier.classify_multiple_directories(directories)
            progress.update(task, completed=True)
        
        self.console.print(f"[green]✓[/green] Found {len(files)} files\n")
        return files
    
    def _find_duplicates(self, files: List) -> List:
        """Find duplicates with progress."""
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Finding duplicates...", total=None)
            duplicates = self.classifier.find_duplicates(files)
            progress.update(task, completed=True)
        
        if duplicates:
            self.console.print(f"[yellow]⚠[/yellow] Found {len(duplicates)} duplicates\n")
        
        return duplicates
    
    def _show_beautiful_preview(self, plan):
        """Show beautiful preview of what will happen."""
        session = plan.session
        
        self.console.print("\n[bold]Preview[/bold]")
        self.console.print("[dim]Here's what will happen[/dim]\n")
        
        # Summary stats
        summary_table = Table(
            show_header=False,
            border_style="dim",
            box=box.SIMPLE,
            padding=(0, 2)
        )
        
        summary_table.add_column(style="dim")
        summary_table.add_column(style="bold")
        
        summary_table.add_row("📁 Archive", session.archive_path.name)
        summary_table.add_row("📊 Total Files", str(session.total_files))
        summary_table.add_row("💾 Total Size", format_file_size(session.total_size))
        if session.duplicate_count > 0:
            summary_table.add_row("⚠️  Duplicates", str(session.duplicate_count))
        
        self.console.print(summary_table)
        self.console.print()
        
        # Category breakdown
        self.console.print("[bold]Categories[/bold]\n")
        
        category_table = Table(
            show_header=False,
            border_style="dim",
            box=box.SIMPLE,
            padding=(0, 1)
        )
        
        category_table.add_column(style="cyan", width=20)
        category_table.add_column(justify="right", style="blue", width=10)
        category_table.add_column(justify="right", style="yellow")
        
        files_by_category = session.files_by_category
        for category, files in sorted(files_by_category.items()):
            size = sum(f.size for f in files)
            category_table.add_row(
                f"📂 {category.capitalize()}",
                f"{len(files)} files",
                format_file_size(size)
            )
        
        self.console.print(category_table)
        self.console.print()
    
    def _confirm_execution(self) -> bool:
        """Ask for confirmation with beautiful prompt."""
        return Confirm.ask(
            "\n[bold]Ready to organize?[/bold]",
            default=True
        )
    
    def _execute_with_progress(self, selected_dirs, files, duplicates):
        """Execute with beautiful progress bar."""
        self.console.print("\n[bold]Organizing Files[/bold]\n")
        
        # Create live session
        live_session = self.mover.create_session(selected_dirs, files, dry_run=False)
        live_session.duplicates = duplicates
        
        # Plan
        self.mover.plan_archive(live_session)
        
        # Execute with progress
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="blue", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Moving files...", total=len(files))
            
            # Create session directory
            create_directory_safe(live_session.archive_path)
            
            # Move files
            for file_info in live_session.files:
                if file_info.status.value == "error":
                    continue
                
                try:
                    self.mover._move_file(file_info, live_session.archive_path)
                except Exception as e:
                    logger.error(f"Error moving {file_info.path}: {e}")
                
                progress.advance(task)
        
        # Generate report
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Generating report...", total=None)
            report_path = self.reporter.generate_html_report(live_session)
            progress.update(task, completed=True)
        
        live_session.report_path = report_path
        return live_session
    
    def _show_success(self, session):
        """Show beautiful success message."""
        self.console.print()
        
        # Success panel
        success_text = (
            f"[green]✓ Successfully organized {session.success_count} files[/green]\n\n"
            f"[dim]Archive:[/dim] [cyan]{session.archive_path}[/cyan]\n"
            f"[dim]Report:[/dim] [blue]{session.report_path}[/blue]"
        )
        
        if session.error_count > 0:
            success_text += f"\n\n[yellow]⚠ {session.error_count} files had errors[/yellow]"
        
        panel = Panel(
            success_text,
            title="[bold]Complete[/bold]",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
        
        # Quick stats
        stats_table = Table(
            show_header=False,
            border_style="dim",
            box=None,
            padding=(0, 2)
        )
        
        stats_table.add_column(style="dim")
        stats_table.add_column(style="bold green")
        
        stats_table.add_row("✓ Moved", str(session.success_count))
        if session.skipped_count > 0:
            stats_table.add_row("⊘ Skipped", str(session.skipped_count))
        if session.error_count > 0:
            stats_table.add_row("✗ Errors", str(session.error_count))
        
        self.console.print(stats_table)
        self.console.print()


def main():
    """Main entry point."""
    cli = BeautifulCLI()
    cli.run()


if __name__ == "__main__":
    main()
