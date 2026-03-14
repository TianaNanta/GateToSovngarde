"""Sample command demonstrating CLI extensibility.

This is a simple example command that lists available GTS versions
and can optionally show details about mods in a version.

It serves as:
1. A reference implementation for new command developers
2. A demonstration that commands can be added without framework changes
3. A test case for the extensibility framework

To use this command:
    gts versions --help
    gts versions
    gts versions --verbose
    gts versions GTSv101 --verbose
"""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..db import DatabaseLoader
from ..utils.errors import ValidationError, OperationError
from ..utils.output import success

# Initialize console for Rich output
console = Console()


def versions(
    version_filter: Optional[str] = typer.Argument(
        None,
        help="Optional: Show details for specific version (e.g., GTSv101)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information about mods"
    ),
) -> None:
    """List available GateToSovngarde modlist versions.

    Display all available GTS version databases that can be used with
    the import command. Optionally show detailed information about mods
    in a specific version.

    Example:
        $ gts versions
        Available versions:
        - GTSv101 (1954 mods)

        $ gts versions --verbose
        Shows mods in each version

        $ gts versions GTSv101
        Shows details for GTSv101 only

    Args:
        version_filter: Optional version ID to show details for
        verbose: Show detailed mod list for the version(s)
    """
    try:
        # Load available versions from database
        loader = DatabaseLoader()
        available_versions = loader.list_versions()

        if not available_versions:
            console.print("[yellow]⚠ No GTS versions found[/yellow]")
            raise typer.Exit(code=1)

        # If version_filter specified, validate it exists
        if version_filter:
            if version_filter not in available_versions:
                raise ValidationError(
                    f"Version not found: {version_filter}\n"
                    f"Available versions: {', '.join(available_versions)}"
                )
            # Show details for specific version
            display_version_details(loader, version_filter, verbose)
        else:
            # Show all versions
            display_all_versions(loader, available_versions, verbose)

        success("✓ Version listing complete")

    except ValidationError as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)

    except OperationError as e:
        console.print(f"[red]✗ Operation failed: {e}[/red]")
        raise typer.Exit(code=2)


def display_all_versions(
    loader: DatabaseLoader, versions: list[str], verbose: bool
) -> None:
    """Display all available versions with optional details.

    Args:
        loader: DatabaseLoader instance
        versions: List of available version IDs
        verbose: Whether to show detailed information
    """
    console.print("\n[bold]Available GateToSovngarde Versions[/bold]\n")

    if not verbose:
        # Simple list
        for version in versions:
            try:
                db = loader.get_version(version)
                mod_count = len(db.get("mods", []))
                console.print(f"  • {version:<10} ({mod_count:>4} mods)")
            except Exception:
                console.print(f"  • {version:<10} (error loading)")
    else:
        # Detailed table
        display_version_table(loader, versions)


def display_version_details(
    loader: DatabaseLoader, version: str, verbose: bool
) -> None:
    """Display detailed information about a specific version.

    Args:
        loader: DatabaseLoader instance
        version: Version ID to show details for
        verbose: Whether to show mod list
    """
    try:
        db = loader.get_version(version)

        console.print(f"\n[bold]{db.get('version_name', version)}[/bold]\n")
        console.print(f"  ID: {db.get('version_id')}")
        console.print(f"  Created: {db.get('created_date')}")

        mods = db.get("mods", [])
        console.print(f"  Total Mods: {len(mods)}")

        if verbose and mods:
            console.print("\n[bold cyan]First 10 Mods:[/bold cyan]")
            for i, mod in enumerate(mods[:10], 1):
                mod_name = mod.get("name", "Unknown")
                mod_id = mod.get("id", "Unknown")
                console.print(f"    {i:2}. [{mod_id}] {mod_name}")

            if len(mods) > 10:
                console.print(f"    ... and {len(mods) - 10} more")

    except Exception as e:
        raise OperationError(f"Failed to load version details: {e}")


def display_version_table(loader: DatabaseLoader, versions: list[str]) -> None:
    """Display versions in a formatted table.

    Args:
        loader: DatabaseLoader instance
        versions: List of version IDs
    """
    table = Table(title="GateToSovngarde Versions")

    table.add_column("Version ID", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Mod Count", justify="right", style="green")
    table.add_column("Created", style="yellow")

    for version in versions:
        try:
            db = loader.get_version(version)
            version_name = db.get("version_name", version)
            mod_count = len(db.get("mods", []))
            created_date = db.get("created_date", "Unknown")

            table.add_row(version, version_name, str(mod_count), created_date)
        except Exception:
            table.add_row(version, "[red]Error loading[/red]", "-", "-")

    console.print(table)
