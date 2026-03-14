"""Import service for handling mod file copying and tracking.

This module provides the ImportService class which executes the actual
import operation: copying mod files from source to destination while
tracking progress and errors.
"""

import shutil
import time
from pathlib import Path
from typing import Callable, List, Optional

from ..db import DatabaseLoader
from ..models.import_result import ImportError, ImportResult
from ..utils.errors import OperationError


class ImportService:
    """Service for executing mod imports.

    Handles loading mod databases, copying files, and tracking results.

    Attributes:
        loader: DatabaseLoader instance for accessing mod databases
    """

    def __init__(self) -> None:
        """Initialize the import service."""
        self.loader = DatabaseLoader()

    def _find_archive_file(self, source: Path, base_name: str) -> Path | None:
        """Find an archive file with any supported extension.

        For archived mods, tries to find the file with common archive
        extensions (.7z, .rar, .zip, .tar.xz, .tar.gz, .tar, .iso).

        Handles filenames with version/timestamp suffixes like:
        "ModName-123456-1-0-1234567890.7z" when looking for "ModName"

        Args:
            source: Source directory to search in
            base_name: Base name of the file (before extension)

        Returns:
            Path to the found archive file, or None if not found
        """
        import re

        archive_extensions = [
            ".7z",
            ".rar",
            ".zip",
            ".tar.xz",
            ".tar.gz",
            ".tar",
            ".iso",
        ]

        # First, try exact match (most common case)
        for ext in archive_extensions:
            archive_path = source / f"{base_name}{ext}"
            if archive_path.exists():
                return archive_path

        # If no exact match, search for files that START with the base_name
        # This handles cases where files have version/timestamp suffixes
        # e.g., looking for "ModName" might find "ModName-12345-1-0-1234567890.7z"
        for ext in archive_extensions:
            pattern = re.compile(
                rf"^{re.escape(base_name)}(?:-\d+)*(?:-\d+\.\d+)*(?:-\d+)?{re.escape(ext)}$"
            )
            for file in source.iterdir():
                if file.is_file() and pattern.match(file.name):
                    return file

        return None

    def execute(
        self,
        version: str,
        source: Path,
        dest: Path,
        force: bool = False,
        operation_type: str = "copy",
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> ImportResult:
        """Execute the import operation.

        Loads the GTS version database and copies mod files from source
        to destination directory. For archived mods, searches for any
        supported archive format.

        Args:
            version: GTS version identifier (e.g., "GTSv101")
            source: Source directory containing mod files
            dest: Destination directory for imports
            force: Whether to overwrite existing files
            operation_type: Type of operation ("copy" or "move")
            progress_callback: Optional callback for progress updates (current, total, mod_name)

        Returns:
            ImportResult with statistics and any errors

        Raises:
            OperationError: If critical operation fails (e.g., dest not writable)
        """
        start_time = time.time()
        mods_imported = 0
        mods_missing: List[str] = []
        mods_errors: List[str] = []
        files_copied = 0
        errors: List[ImportError] = []

        try:
            # Load the mod database
            database = self.loader.get_version(version)
            mods = database.get("mods", [])
            total_mods = len(mods)

            # Ensure destination directory exists
            dest.mkdir(parents=True, exist_ok=True)

            # Process each mod
            for mod_index, mod in enumerate(mods):
                mod_id = mod.get("id", "unknown")
                mod_name = mod.get("name", "unknown")
                required_files = mod.get("required_files", [])

                # Update progress
                if progress_callback:
                    progress_callback(mod_index + 1, total_mods, mod_name)

                # Skip mods with no files
                if not required_files:
                    mods_imported += 1
                    continue

                # Try to find and copy the mod file
                mod_success = False
                actual_file_found = None

                # For archived mods, try to find any matching archive format
                if required_files and len(required_files) > 0:
                    # Get the base name (without extension) from the first required file
                    first_file = required_files[0]
                    base_name = (
                        first_file.rsplit(".", 1)[0]
                        if "." in first_file
                        else first_file
                    )

                    # Search for the archive file
                    actual_file_found = self._find_archive_file(source, base_name)

                    if actual_file_found:
                        source_file = actual_file_found
                        dest_file = dest / actual_file_found.name

                        try:
                            # Check if destination exists and force is not set
                            if dest_file.exists() and not force:
                                errors.append(
                                    ImportError(
                                        mod_id=mod_id,
                                        mod_name=mod_name,
                                        error_type="file_exists",
                                        message=f"File already exists: {actual_file_found.name}",
                                        recovery_suggestion="Use --force to overwrite existing files",
                                    )
                                )
                                mods_errors.append(mod_name)
                            else:
                                # Copy or move the file
                                dest_file.parent.mkdir(parents=True, exist_ok=True)

                                if operation_type == "move":
                                    shutil.move(str(source_file), str(dest_file))
                                else:  # copy
                                    shutil.copy2(source_file, dest_file)

                                files_copied += 1
                                mod_success = True

                        except PermissionError:
                            errors.append(
                                ImportError(
                                    mod_id=mod_id,
                                    mod_name=mod_name,
                                    error_type="permission_denied",
                                    message=f"Permission denied copying {actual_file_found.name}",
                                    recovery_suggestion=f"Check write permissions for {dest}",
                                )
                            )
                            mods_errors.append(mod_name)
                        except Exception as e:
                            errors.append(
                                ImportError(
                                    mod_id=mod_id,
                                    mod_name=mod_name,
                                    error_type="io_error",
                                    message=f"Error copying {actual_file_found.name}: {str(e)}",
                                    recovery_suggestion="Check disk space and file permissions",
                                )
                            )
                            mods_errors.append(mod_name)
                    else:
                        # No archive file found with any extension
                        errors.append(
                            ImportError(
                                mod_id=mod_id,
                                mod_name=mod_name,
                                error_type="file_not_found",
                                message=f"Required archive file not found: {base_name}.<7z|rar|zip|tar.xz|tar.gz|tar|iso>",
                                recovery_suggestion=f"Ensure {mod_name} archive exists in {source}",
                            )
                        )
                        mods_missing.append(mod_name)

                # Count as imported if file was successfully copied
                if mod_success:
                    mods_imported += 1

            duration = time.time() - start_time
            return ImportResult(
                total_mods=total_mods,
                mods_imported=mods_imported,
                mods_missing=mods_missing,
                mods_errors=mods_errors,
                files_copied=files_copied,
                duration=duration,
                errors=errors,
                operation_type=operation_type,
            )

        except Exception as e:
            duration = time.time() - start_time
            raise OperationError(f"Import operation failed: {str(e)}")
