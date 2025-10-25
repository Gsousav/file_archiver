"""
File mover service.
Handles file moving operations with collision detection and handling.
"""

import logging
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..core import FileInfo, FileStatus, CollisionPolicy, ArchiveSession, ArchivePlan, CATEGORY_DISPLAY_NAMES
from ..core.config import (
    ARCHIVE_BASE_DIR,
    SESSION_PREFIX,
    DEFAULT_COLLISION_POLICY,
    COLLISION_SUFFIX_FORMAT,
)
from ..utils import (
    create_directory_safe,
    ensure_unique_path,
    format_timestamp,
)

logger = logging.getLogger(__name__)


class FileMover:
    """
    Handles file moving operations with collision and duplicate handling.
    """

    def __init__(
        self,
        archive_base: Path = ARCHIVE_BASE_DIR,
        collision_policy: str = DEFAULT_COLLISION_POLICY,
        use_source_parent: bool = False,
    ):
        """
        Initialize the file mover.

        Args:
            archive_base: Base directory for archives
            collision_policy: How to handle file collisions
            use_source_parent: If True, save archive in the source directory's parent folder
        """
        self.archive_base = archive_base
        self.collision_policy = CollisionPolicy(collision_policy)
        self.use_source_parent = use_source_parent

    def create_session(
        self,
        source_directories: List[Path],
        files: List[FileInfo],
        dry_run: bool = True,
    ) -> ArchiveSession:
        """
        Create a new archive session.

        Args:
            source_directories: List of source directories
            files: List of files to archive
            dry_run: Whether this is a dry run

        Returns:
            ArchiveSession object
        """
        timestamp = datetime.now()
        
        # Create a descriptive session name with source folder info
        if len(source_directories) == 1:
            source_name = source_directories[0].name
            session_id = f"{source_name}_{SESSION_PREFIX}_{format_timestamp(timestamp)}"
        else:
            session_id = f"Multiple_Folders_{SESSION_PREFIX}_{format_timestamp(timestamp)}"
        
        # Determine archive base directory
        if self.use_source_parent and source_directories:
            # Save in the parent directory of the first source
            archive_base = source_directories[0].parent
        else:
            archive_base = self.archive_base

        # Create session directory path
        session_path = archive_base / session_id

        session = ArchiveSession(
            session_id=session_id,
            timestamp=timestamp,
            source_directories=source_directories,
            archive_path=session_path,
            files=files,
            dry_run=dry_run,
        )

        logger.info(f"Created {'dry-run' if dry_run else 'live'} session: {session_id}")
        logger.info(f"Archive location: {session_path}")

        return session

    def plan_archive(self, session: ArchiveSession) -> ArchivePlan:
        """
        Create a plan for archiving files (dry-run).

        Args:
            session: Archive session

        Returns:
            ArchivePlan object with planned operations
        """
        logger.info("Creating archive plan...")

        plan = ArchivePlan(session=session)

        # Plan destination for each file
        for file_info in session.files:
            try:
                destination = self._get_destination_path(
                    file_info, session.archive_path
                )

                file_info.destination = destination

                # Check for collisions
                if destination.exists():
                    plan.add_warning(
                        f"Collision: {file_info.name} -> "
                        f"{destination.relative_to(session.archive_path)}"
                    )
                    plan.add_operation(
                        "move_with_collision",
                        file_info,
                        f"Will handle collision using {self.collision_policy.value} policy",
                    )
                else:
                    plan.add_operation("move", file_info)

            except Exception as e:
                logger.error(f"Error planning for {file_info.path}: {e}")
                file_info.status = FileStatus.ERROR
                file_info.error = str(e)
                plan.add_warning(f"Error planning {file_info.name}: {e}")

        logger.info(f"Plan created: {plan.total_operations} operations")

        return plan

    def execute_archive(self, session: ArchiveSession) -> ArchiveSession:
        """
        Execute the archive operation (move files).

        Args:
            session: Archive session with planned destinations

        Returns:
            Updated ArchiveSession object
        """
        if session.dry_run:
            logger.warning("Cannot execute a dry-run session")
            return session

        logger.info(f"Executing archive session: {session.session_id}")

        # Create base session directory
        if not create_directory_safe(session.archive_path):
            logger.error(f"Failed to create session directory: {session.archive_path}")
            return session

        # Move each file
        for file_info in session.files:
            if file_info.status == FileStatus.ERROR:
                continue

            try:
                self._move_file(file_info, session.archive_path)

            except Exception as e:
                logger.error(f"Error moving {file_info.path}: {e}")
                file_info.status = FileStatus.ERROR
                file_info.error = str(e)

        success_count = len([f for f in session.files if f.status == FileStatus.MOVED])
        logger.info(
            f"Archive complete: {success_count}/{len(session.files)} files moved"
        )

        return session

    def _get_destination_path(self, file_info: FileInfo, session_path: Path) -> Path:
        """
        Get the destination path for a file.

        Args:
            file_info: File information
            session_path: Base session path

        Returns:
            Destination path
        """
        # Create category subdirectory with display name
        category_display = CATEGORY_DISPLAY_NAMES.get(file_info.category, file_info.category)
        category_dir = session_path / category_display

        # Destination file path
        destination = category_dir / file_info.name

        return destination

    def _move_file(self, file_info: FileInfo, session_path: Path):
        """
        Move a file to its destination.

        Args:
            file_info: File information with destination set
            session_path: Base session path
        """
        if not file_info.destination:
            file_info.destination = self._get_destination_path(file_info, session_path)

        destination = file_info.destination

        # Create category directory if needed
        category_dir = destination.parent
        if not create_directory_safe(category_dir):
            raise IOError(f"Failed to create directory: {category_dir}")

        # Handle collision if file exists
        if destination.exists():
            destination = self._handle_collision(file_info, destination)
            file_info.destination = destination

        # Move the file
        try:
            shutil.move(str(file_info.path), str(destination))
            file_info.status = FileStatus.MOVED
            logger.debug(f"Moved: {file_info.name} -> {destination}")

        except Exception as e:
            file_info.status = FileStatus.ERROR
            file_info.error = str(e)
            raise

    def _handle_collision(self, file_info: FileInfo, destination: Path) -> Path:
        """
        Handle file collision based on policy.

        Args:
            file_info: File information
            destination: Intended destination

        Returns:
            Final destination path
        """
        logger.warning(f"Collision detected for {file_info.name}")

        if self.collision_policy == CollisionPolicy.SKIP:
            file_info.status = FileStatus.SKIPPED
            logger.info(f"Skipped (collision): {file_info.name}")
            return destination

        elif self.collision_policy == CollisionPolicy.OVERWRITE:
            logger.info(f"Will overwrite: {destination}")
            return destination

        elif self.collision_policy == CollisionPolicy.SUFFIX:
            # Add numeric suffix
            stem = destination.stem
            suffix = destination.suffix
            parent = destination.parent
            counter = 1

            while True:
                new_name = f"{stem}_{counter}{suffix}"
                new_destination = parent / new_name

                if not new_destination.exists():
                    logger.info(f"Renamed to: {new_name}")
                    return new_destination

                counter += 1

        elif self.collision_policy == CollisionPolicy.HASH:
            # Add hash suffix
            if file_info.hash:
                hash_suffix = file_info.hash[:8]
                stem = destination.stem
                suffix = destination.suffix
                parent = destination.parent

                new_name = f"{stem}_{hash_suffix}{suffix}"
                new_destination = parent / new_name

                logger.info(f"Renamed with hash: {new_name}")
                return new_destination
            else:
                # Fallback to suffix if no hash
                return self._handle_collision(file_info, destination)

        return destination

    def rollback_session(self, session: ArchiveSession) -> bool:
        """
        Rollback an archive session (move files back).

        This is a placeholder for future undo functionality.

        Args:
            session: Archive session to rollback

        Returns:
            True if successful, False otherwise
        """
        if session.dry_run:
            logger.warning("Cannot rollback a dry-run session")
            return False

        logger.info(f"Rolling back session: {session.session_id}")

        success_count = 0

        for file_info in session.files:
            if file_info.status != FileStatus.MOVED:
                continue

            if not file_info.destination:
                continue

            try:
                # Move file back to original location
                shutil.move(str(file_info.destination), str(file_info.path))
                success_count += 1
                logger.debug(f"Rolled back: {file_info.name}")

            except Exception as e:
                logger.error(f"Error rolling back {file_info.name}: {e}")

        logger.info(f"Rollback complete: {success_count} files restored")

        return success_count == session.success_count
