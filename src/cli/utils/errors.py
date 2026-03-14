"""Custom exception classes for GateToSovngarde CLI."""


class CLIError(Exception):
    """Base exception for CLI errors."""

    pass


class ValidationError(CLIError):
    """Raised when argument or input validation fails."""

    pass


class DatabaseError(CLIError):
    """Raised when database loading or access fails."""

    pass


class OperationError(CLIError):
    """Raised when a CLI operation fails during execution."""

    pass
