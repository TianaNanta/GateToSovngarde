"""Custom exceptions for GateToSovngarde CLI applications.

This module defines domain-specific exceptions used throughout the CLI
to provide clear, actionable error messages to users.
"""


class GSException(Exception):
    """Base exception for all GateToSovngarde CLI errors."""

    def __init__(self, message: str, suggestion: str | None = None):
        """Initialize exception with message and optional suggestion.

        Args:
            message: Clear description of what went wrong
            suggestion: Optional actionable fix for the user
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self) -> str:
        """Format exception message for CLI display."""
        msg = f"Error: {self.message}"
        if self.suggestion:
            msg += f"\n  Suggestion: {self.suggestion}"
        return msg


class MergeException(GSException):
    """Base exception for merge operations."""

    pass


class FolderNotFoundError(MergeException):
    """Raised when a folder to scan does not exist."""

    def __init__(self, path: str):
        message = f"Path does not exist: {path}"
        suggestion = f"Verify the path exists: ls -la {path}"
        super().__init__(message, suggestion)


class NotADirectoryError(MergeException):
    """Raised when provided path is not a directory."""

    def __init__(self, path: str):
        message = f"Path is not a directory: {path}"
        suggestion = "Check the path is a directory, not a file"
        super().__init__(message, suggestion)


class PermissionDeniedError(MergeException):
    """Raised when user lacks read/write permissions."""

    def __init__(self, path: str, operation: str = "access"):
        message = f"Permission denied when trying to {operation}: {path}"
        suggestion = f"Check permissions with: ls -la {path}"
        super().__init__(message, suggestion)


class MergeOperationError(MergeException):
    """Raised when merge operation fails."""

    def __init__(self, source: str, target: str, reason: str):
        message = f"Failed to merge {source} into {target}: {reason}"
        super().__init__(message)


class ConflictDetectedError(MergeException):
    """Raised when conflicts detected and user needs to decide."""

    def __init__(self, conflicts: list[str]):
        file_list = ", ".join(conflicts[:3]) + (
            f", +{len(conflicts) - 3} more" if len(conflicts) > 3 else ""
        )
        message = f"File conflicts detected: {file_list}"
        suggestion = "You can choose to skip, rename, or overwrite these files"
        super().__init__(message, suggestion)


class ScanError(MergeException):
    """Raised when directory scan fails."""

    def __init__(self, path: str, reason: str):
        message = f"Failed to scan directory {path}: {reason}"
        super().__init__(message)


class OperationCancelledError(GSException):
    """Raised when user cancels operation (e.g., Ctrl+C)."""

    def __init__(self):
        super().__init__("Operation cancelled by user")
