"""Import command for the GateToSovngarde CLI.

This command allows users to import mod databases and manage mod installations.

Example usage:
    $ gts import GTSv101 /source /destination
    $ gts import GTSv101 /source /destination --force
    $ gts import GTSv101 /source /destination --verbose
"""

from pathlib import Path
from typing import Optional

import typer


def import_cmd(
    version: str = typer.Argument(..., help="GTS version to import (e.g., GTSv101)"),
    source_path: Path = typer.Argument(
        ..., help="Path to source directory with mod files"
    ),
    dest_path: Path = typer.Argument(
        ..., help="Path to destination directory for mods"
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

    Example:
        Import the GTSv101 database from /mods/source to /mods/dest:

            $ gts import GTSv101 /mods/source /mods/dest

        Force import and show verbose progress:

            $ gts import GTSv101 /mods/source /mods/dest --force --verbose

    Args:
        version: The GTS version identifier (e.g., "GTSv101")
        source_path: Source directory containing mod files
        dest_path: Destination directory where mods will be imported
        force: Force import even if destination already exists
        verbose: Show detailed progress information during import
    """
    # Phase 4 will implement the actual import logic
    pass
