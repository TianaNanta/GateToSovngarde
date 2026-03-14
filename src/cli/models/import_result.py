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
        error_type: Type of error (e.g., "file_not_found", "permission_denied")
        message: Human-readable error message
        recovery_suggestion: Suggestion on how to recover from this error
    """

    mod_id: str
    error_type: str
    message: str
    recovery_suggestion: str


@dataclass
class ImportResult:
    """Tracks the results of an import operation.

    Attributes:
        mods_imported: Number of mods successfully imported
        files_copied: Total number of files successfully copied
        duration: Time in seconds the import took
        errors: List of ImportError objects for any failures
    """

    mods_imported: int
    files_copied: int
    duration: float
    errors: List[ImportError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return True if import completed with no errors."""
        return len(self.errors) == 0

    @property
    def partial_success(self) -> bool:
        """Return True if some mods imported but some had errors."""
        return self.mods_imported > 0 and len(self.errors) > 0
