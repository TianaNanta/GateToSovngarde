"""Database command group definition and registration.

This module creates and configures the database command group sub-app,
then imports and registers all database-related commands into it.
"""

import typer

from ..database.import_cmd import import_cmd
from ..database.versions_cmd import versions

# Create the database sub-application
database_app = typer.Typer(
    help="Manage GateToSovngarde version databases",
    rich_markup_mode="rich",
)

# Register commands into the database group
database_app.command(name="import")(import_cmd)
database_app.command(name="versions")(versions)
