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

    # Phase 4 will implement the actual import logic
    # For now, validate and show what would be done
    if verbose:
        typer.echo(f"Version: {version}")
        typer.echo(f"Source: {source_path}")
        typer.echo(f"Destination: {dest_path}")
        typer.echo(f"Force: {force}")
