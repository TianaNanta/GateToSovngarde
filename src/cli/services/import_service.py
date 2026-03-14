"""Import service for handling mod file copying and tracking.

This module provides the ImportService class which executes the actual
import operation: copying mod files from source to destination while
tracking progress and errors.
"""

import shutil
import time
from pathlib import Path
from typing import List

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

    def execute(
        self,
        version: str,
        source: Path,
        dest: Path,
        force: bool = False,
    ) -> ImportResult:
        """Execute the import operation.

        Loads the GTS version database and copies mod files from source
        to destination directory.

        Args:
            version: GTS version identifier (e.g., "GTSv101")
            source: Source directory containing mod files
            dest: Destination directory for imports
            force: Whether to overwrite existing files

        Returns:
            ImportResult with statistics and any errors

        Raises:
            OperationError: If critical operation fails (e.g., dest not writable)
        """
        start_time = time.time()
        mods_imported = 0
        files_copied = 0
        errors: List[ImportError] = []

        try:
            # Load the mod database
            database = self.loader.get_version(version)
            mods = database.get("mods", [])

            # Ensure destination directory exists
            dest.mkdir(parents=True, exist_ok=True)

            # Process each mod
            for mod in mods:
                mod_id = mod.get("id", "unknown")
                required_files = mod.get("required_files", [])

                # Skip mods with no files
                if not required_files:
                    mods_imported += 1
                    continue

                # Try to copy each required file
                mod_success = True
                for file_name in required_files:
                    source_file = source / file_name
                    dest_file = dest / file_name

                    try:
                        # Check if source file exists
                        if not source_file.exists():
                            errors.append(
                                ImportError(
                                    mod_id=mod_id,
                                    error_type="file_not_found",
                                    message=f"Required file not found: {file_name}",
                                    recovery_suggestion=f"Ensure {file_name} exists in {source}",
                                )
                            )
                            mod_success = False
                            continue

                        # Check if destination exists and force is not set
                        if dest_file.exists() and not force:
                            errors.append(
                                ImportError(
                                    mod_id=mod_id,
                                    error_type="file_exists",
                                    message=f"File already exists: {file_name}",
                                    recovery_suggestion="Use --force to overwrite existing files",
                                )
                            )
                            mod_success = False
                            continue

                        # Copy the file
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
                        files_copied += 1

                    except PermissionError:
                        errors.append(
                            ImportError(
                                mod_id=mod_id,
                                error_type="permission_denied",
                                message=f"Permission denied copying {file_name}",
                                recovery_suggestion=f"Check write permissions for {dest}",
                            )
                        )
                        mod_success = False
                    except Exception as e:
                        errors.append(
                            ImportError(
                                mod_id=mod_id,
                                error_type="io_error",
                                message=f"Error copying {file_name}: {str(e)}",
                                recovery_suggestion="Check disk space and file permissions",
                            )
                        )
                        mod_success = False

                # Count as imported if at least one file succeeded
                if mod_success or (required_files and files_copied > 0):
                    mods_imported += 1

            duration = time.time() - start_time
            return ImportResult(
                mods_imported=mods_imported,
                files_copied=files_copied,
                duration=duration,
                errors=errors,
            )

        except Exception as e:
            duration = time.time() - start_time
            raise OperationError(f"Import operation failed: {str(e)}")
