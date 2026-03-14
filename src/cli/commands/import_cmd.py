"""Import command for the GateToSovngarde CLI.

This command allows users to import mod databases and manage mod installations.

Example usage:
    $ gts import GTSv101 /source /destination
    $ gts import GTSv101 /source /destination --force
    $ gts import GTSv101 /source /destination --verbose
    $ gts import  # Interactive mode - asks for parameters
"""

from pathlib import Path
from typing import Optional

import typer

from ..db import DatabaseLoader
from ..models.import_result import ImportResult
from ..services.import_service import ImportService
from ..utils.errors import ValidationError
from ..utils.output import success, error


def import_cmd(
    version: Optional[str] = typer.Argument(
        None,
        help="GTS version to import (e.g., GTSv101)",
    ),
    source_path: Optional[Path] = typer.Argument(
        None,
        help="Path to source directory with mod files",
    ),
    dest_path: Optional[Path] = typer.Argument(
        None,
        help="Path to destination directory for mods",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force import even if destination exists",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress information",
    ),
) -> None:
    """Import mod database and copy mods to destination.

    This command loads a GTS version database and imports mods from the
    source directory to the destination directory.

    The command validates:
    - The specified GTS version exists
    - The source directory exists and is readable
    - The destination directory exists or can be created

    When run without arguments, this command enters interactive mode and
    prompts you for each parameter with helpful examples and hints.

    Example:
        Import the GTSv101 database from /mods/source to /mods/dest:

            $ gts import GTSv101 /mods/source /mods/dest

        Interactive mode with prompts:

            $ gts import
            For what version of the modlist? (ex: GTSv101): GTSv101
            Path to source directory? (ex: /home/user/mods/source): /home/user/mods/source
            Path to destination? (ex: /home/user/mods/dest): /home/user/mods/dest

        Force import and show verbose progress:

            $ gts import GTSv101 /mods/source /mods/dest --force --verbose

    Args:
        version: The GTS version identifier (e.g., "GTSv101")
        source_path: Source directory containing mod files
        dest_path: Destination directory where mods will be imported
        force: Force import even if destination already exists
        verbose: Show detailed progress information during import
    """
    # Interactive mode: prompt for missing parameters
    if version is None:
        # Get available versions for reference
        loader = DatabaseLoader()
        available_versions = loader.list_versions()

        version_hint = available_versions[0] if available_versions else "GTSv101"
        version = typer.prompt(f"For what version of the modlist? (ex: {version_hint})")
        if not version:
            version = version_hint

    if source_path is None:
        source_path = Path(
            typer.prompt("Path to source directory? (ex: /home/user/mods/source)")
        )
    else:
        source_path = Path(source_path)

    if dest_path is None:
        dest_path = Path(
            typer.prompt("Path to destination? (ex: /home/user/mods/dest)")
        )
    else:
        dest_path = Path(dest_path)

    # Parameter validation
    try:
        _validate_parameters(version, source_path, dest_path)
    except ValidationError as e:
        error(str(e))
        raise typer.Exit(code=1)

    # Execute import
    try:
        service = ImportService()
        result = service.execute(version, source_path, dest_path, force)

        # Display results
        _display_results(result, version, verbose)

        # Set exit code based on results
        if result.success:
            raise typer.Exit(code=0)
        else:
            raise typer.Exit(code=2)

    except KeyboardInterrupt:
        error("\nImport interrupted by user")
        raise typer.Exit(code=2)
    except typer.Exit:
        # Re-raise typer.Exit exceptions without catching them
        raise
    except Exception as e:
        error(f"Import failed: {str(e)}")
        raise typer.Exit(code=2)


def _validate_parameters(
    version: str,
    source_path: Path,
    dest_path: Path,
) -> None:
    """Validate import parameters.

    Args:
        version: GTS version to validate
        source_path: Source directory to validate
        dest_path: Destination directory to validate

    Raises:
        ValidationError: If any parameter is invalid
    """
    # Validate version exists
    loader = DatabaseLoader()
    if not loader.validate_version_exists(version):
        available = ", ".join(loader.list_versions())
        raise ValidationError(
            f"Unknown version: {version}\nAvailable versions: {available}"
        )

    # Validate source directory exists
    if not source_path.exists():
        raise ValidationError(f"Source directory not found: {source_path}")

    if not source_path.is_dir():
        raise ValidationError(f"Source path is not a directory: {source_path}")

    # Validate source is readable
    try:
        list(source_path.iterdir())
    except PermissionError:
        raise ValidationError(f"Source directory not readable: {source_path}")

    # Validate destination is writable or creatable
    try:
        if dest_path.exists() and not dest_path.is_dir():
            raise ValidationError(
                f"Destination exists but is not a directory: {dest_path}"
            )

        # Try to create destination if needed
        dest_path.mkdir(parents=True, exist_ok=True)

        # Verify we can write to destination
        test_file = dest_path / ".write_test_12345"
        try:
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError):
            raise ValidationError(f"Destination directory not writable: {dest_path}")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Cannot create/access destination: {str(e)}")


def _display_results(result: ImportResult, version: str, verbose: bool) -> None:
    """Display import results to user.

    Args:
        result: The ImportResult object with statistics
        version: The GTS version that was imported
        verbose: Whether to show detailed output
    """
    # Display summary
    if result.success:
        success(
            f"✓ Import completed successfully ({version})\n"
            f"  Mods imported: {result.mods_imported}\n"
            f"  Files copied: {result.files_copied}\n"
            f"  Duration: {result.duration:.2f}s"
        )
    elif result.partial_success:
        typer.echo(
            f"⚠ Import completed with errors ({version})\n"
            f"  Mods imported: {result.mods_imported}\n"
            f"  Files copied: {result.files_copied}\n"
            f"  Errors: {len(result.errors)}\n"
            f"  Duration: {result.duration:.2f}s"
        )
    else:
        error(
            f"✗ Import failed ({version})\n"
            f"  Files copied: {result.files_copied}\n"
            f"  Errors: {len(result.errors)}"
        )

    # Display errors if any
    if result.errors:
        typer.echo("\nErrors encountered:")
        for err in result.errors:
            typer.echo(f"  [{err.error_type}] {err.mod_id}: {err.message}")
            if not verbose:
                continue
            typer.echo(f"    → {err.recovery_suggestion}")
