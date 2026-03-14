"""GateToSovngarde CLI - Mod management tools for GateToSovngarde modding.

This module provides the main Typer application entry point for the GTS CLI.
It handles global options like --version and --help, and serves as the
central point for command registration.

The application structure:
- Global options: --version, --help
- Commands: import (P1), database (P2), config (future)
- Extensible registration: Use register_commands() to add new commands

Example usage:
    $ gts --help
    $ gts --version
    $ gts import GTSv101 /source /dest
"""

from typing import Optional

import typer

from . import __version__
from .commands import register_commands

# Create the Typer app with metadata
app = typer.Typer(
    help="GateToSovngarde CLI - Mod management tools",
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Display the CLI version when --version is specified.

    Args:
        value: Whether --version was passed
    """
    if value:
        typer.echo(f"GateToSovngarde CLI version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Show version and exit",
        is_eager=True,
    ),
) -> None:
    """GateToSovngarde CLI - Manage mods and modding resources.

    This CLI tool provides utilities for managing mods in GateToSovngarde,
    including importing mod databases, managing configurations, and other
    modding-related operations.

    Use --help with any command for more detailed information:
        $ gts --help
        $ gts import --help

    Start with the import command to load mod databases:
        $ gts import GTSv101 /path/to/source /path/to/dest
    """
    pass


# Register all commands with the app
register_commands(app)


if __name__ == "__main__":
    app()
