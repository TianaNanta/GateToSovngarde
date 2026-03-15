"""Import command for the GateToSovngarde CLI.

This command allows users to import mod databases and manage mod installations.

Example usage:
    $ gts database import GTSv101 /source /destination
    $ gts database import GTSv101 /source /destination --force
    $ gts database import GTSv101 /source /destination --verbose
    $ gts database import GTSv101 /source /destination --move
    $ gts database import  # Interactive mode - asks for parameters
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from ...db import DatabaseLoader
from ...models.import_result import ImportResult
from ...services.import_service import ImportService
from ...utils.errors import ValidationError
from ...utils.output import success, error

console = Console()


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
    move: bool = typer.Option(
        False,
        "--move",
        "-m",
        help="Move mods instead of copying (delete from source after import)",
    ),
) -> None:
    """Import mod database and copy/move mods to destination.

    This command loads a GTS version database and imports mods from the
    source directory to the destination directory. You can choose to either
    copy (leaving source files intact) or move (removing source files after import).

    The command validates:
    - The specified GTS version exists
    - The source directory exists and is readable
    - The destination directory exists or can be created

    When run without arguments, this command enters interactive mode and
    prompts you for each parameter with helpful examples and hints.

    Example:
        Import the GTSv101 database from /mods/source to /mods/dest:

            $ gts database import GTSv101 /mods/source /mods/dest

        Move mods instead of copying (removes from source after import):

            $ gts database import GTSv101 /mods/source /mods/dest --move

        Interactive mode with prompts:

            $ gts database import
            For what version of the modlist? (ex: GTSv101): GTSv101
            Path to source directory? (ex: /home/user/mods/source): /home/user/mods/source
            Path to destination? (ex: /home/user/mods/dest): /home/user/mods/dest
            Move mods instead of copying? [y/N]: y

        Force import and show verbose progress:

            $ gts database import GTSv101 /mods/source /mods/dest --force --verbose

    Args:
        version: The GTS version identifier (e.g., "GTSv101")
        source_path: Source directory containing mod files
        dest_path: Destination directory where mods will be imported
        force: Force import even if destination already exists
        verbose: Show detailed progress information during import
        move: Move mods instead of copying (delete from source after import)
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

    # Ask for move/copy in interactive mode
    if version is None or source_path is None or dest_path is None:
        move_prompt = typer.confirm("Move mods instead of copying?", default=False)
        if move_prompt:
            move = True

    # Parameter validation
    try:
        _validate_parameters(version, source_path, dest_path)
    except ValidationError as e:
        error(str(e))
        raise typer.Exit(code=1)

    # Determine operation type
    operation_type = "move" if move else "copy"

    # Execute import with progress bar
    try:
        service = ImportService()

        # Use progress bar to track import progress
        with Progress() as progress:
            task = progress.add_task("[cyan]Importing mods...", total=None)

            def progress_callback(current: int, total: int, mod_name: str) -> None:
                """Update progress bar with current status."""
                progress.update(
                    task,
                    completed=current,
                    total=total,
                    description=f"[cyan]Importing mods... [{current}/{total}] {mod_name}",
                )

            result = service.execute(
                version,
                source_path,
                dest_path,
                force,
                operation_type,
                progress_callback,
            )

        # Display results
        _display_results(result, version, verbose, operation_type)

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


def _display_results(
    result: ImportResult, version: str, verbose: bool, operation_type: str
) -> None:
    """Display import results to user.

    Args:
        result: The ImportResult object with statistics
        version: The GTS version that was imported
        verbose: Whether to show detailed output
        operation_type: Type of operation ("copy" or "move")
    """
    operation_word = "moved" if operation_type == "move" else "copied"

    # Display summary
    if result.success:
        success(
            f"✓ Import completed successfully ({version})\n"
            f"  Total mods in database: {result.total_mods}\n"
            f"  Mods {operation_word}: {result.mods_imported}\n"
            f"  Files {operation_word}: {result.files_copied}\n"
            f"  Duration: {result.duration:.2f}s"
        )
    elif result.partial_success:
        console.print(
            f"\n⚠ Import completed with issues ({version})\n"
            f"  Total mods in database: {result.total_mods}\n"
            f"  Mods {operation_word}: {result.mods_imported}\n"
            f"  Files {operation_word}: {result.files_copied}\n"
            f"  Mods missing: {len(result.mods_missing)}\n"
            f"  Mods with errors: {len(result.mods_errors)}\n"
            f"  Duration: {result.duration:.2f}s",
            style="yellow",
        )
    else:
        error(
            f"✗ Import failed ({version})\n"
            f"  Files {operation_word}: {result.files_copied}\n"
            f"  Errors: {len(result.errors)}"
        )

    # Display missing mods summary
    if result.mods_missing:
        console.print("\n[bold yellow]Missing Mods:[/bold yellow]")
        for mod_name in result.mods_missing:
            console.print(f"  • {mod_name}")

    # Display error mods summary
    if result.mods_errors:
        console.print("\n[bold red]Mods with Errors:[/bold red]")
        for mod_name in result.mods_errors:
            console.print(f"  • {mod_name}")

    # Display detailed errors if verbose mode
    if result.errors:
        if verbose:
            console.print("\n[bold red]Error Details:[/bold red]")

            # Create a table for errors
            table = Table(title="Import Errors", show_header=True, header_style="bold")
            table.add_column("Mod ID", style="cyan")
            table.add_column("Mod Name", style="magenta")
            table.add_column("Error Type", style="yellow")
            table.add_column("Message", style="red")

            for err in result.errors:
                table.add_row(
                    err.mod_id,
                    err.mod_name,
                    err.error_type,
                    err.message,
                )

            console.print(table)

            # Print recovery suggestions
            console.print("\n[bold cyan]Recovery Suggestions:[/bold cyan]")
            for err in result.errors:
                console.print(f"  • [{err.error_type}] {err.recovery_suggestion}")
        else:
            console.print(
                f"\n[yellow]{len(result.errors)} error(s) occurred. Use --verbose to see details.[/yellow]"
            )
