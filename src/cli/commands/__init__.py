"""Commands module for GateToSovngarde CLI.

This module handles registration of all CLI command groups. The register_commands()
function is called from main.py to add command groups to the Typer app instance.

Command Group Registration Pattern:
1. Create a new group file in groups/ (e.g., database.py)
2. Define a Typer sub-app and register commands into it
3. Import the group in this __init__.py
4. Register it with app.add_typer() in register_commands()

This approach allows command groups to be added without modifying main.py,
maintaining clean separation of concerns.

Command Hierarchy:
- Main app (gts)
  ├── database group (gts database)
  │   ├── import command (gts database import)
  │   └── versions command (gts database versions)
  └── [Future groups]

Example:
    # In groups/database.py
    database_app = typer.Typer(help="Manage databases")
    database_app.command()(import_cmd)
    database_app.command()(versions)

    # In __init__.py register_commands()
    app.add_typer(database_app, name="database")
"""

import typer

from .groups.database import database_app


def register_commands(app: typer.Typer) -> None:
    """Register all command groups with the Typer application.

    This function is called during app initialization to register all
    available command groups. Groups are imported and added to the app here.

    Args:
        app: The Typer application instance to register groups with

    Note:
        Command groups are registered with custom names here. Each group
        contains multiple related commands that can be tested and maintained
        independently. Adding new groups doesn't require modifying the framework.
    """
    # Register the database group
    app.add_typer(database_app, name="database")
