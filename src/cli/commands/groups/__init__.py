"""Database command group for GateToSovngarde CLI.

This module defines the 'database' command group which contains all
database-related operations such as importing mods and listing versions.

The database group uses Typer's sub-application pattern to organize
related commands under a logical hierarchy.

Example usage:
    $ gts database --help
    $ gts database import GTSv101 /source /dest
    $ gts database versions
"""

import typer

# Create the database sub-application
database_app = typer.Typer(
    help="Manage GateToSovngarde version databases",
    rich_markup_mode="rich",
)
