"""Import result tracking and error models.

This module defines the data structures used to track import operation results
and any errors that occur during the import process.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ImportError:
    """Represents a single error that occurred during import.

    Attributes:
        mod_id: The ID of the mod that had the error
        mod_name: The name of the mod that had the error
        error_type: Type of error (e.g., "file_not_found", "permission_denied")
        message: Human-readable error message
        recovery_suggestion: Suggestion on how to recover from this error
    """

    mod_id: str
    mod_name: str
    error_type: str
    message: str
    recovery_suggestion: str


@dataclass
class ImportResult:
    """Tracks the results of an import operation.

    Attributes:
        total_mods: Total number of mods in the database
        mods_imported: Number of mods successfully imported
        mods_missing: List of mod names that were not found in source
        mods_errors: List of mod names that had errors during import
        files_copied: Total number of files successfully copied
        duration: Time in seconds the import took
        errors: List of ImportError objects for any failures
        operation_type: Type of operation ("copy" or "move")
    """

    total_mods: int
    mods_imported: int
    mods_missing: List[str] = field(default_factory=list)
    mods_errors: List[str] = field(default_factory=list)
    files_copied: int = 0
    duration: float = 0.0
    errors: List[ImportError] = field(default_factory=list)
    operation_type: str = "copy"

    @property
    def success(self) -> bool:
        """Return True if import completed with no errors."""
        return len(self.errors) == 0

    @property
    def partial_success(self) -> bool:
        """Return True if some mods imported but some had errors."""
        return self.mods_imported > 0 and len(self.errors) > 0
