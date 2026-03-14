"""Commands module for GateToSovngarde CLI.

This module handles registration of all CLI commands. The register_commands()
function is called from main.py to add commands to the Typer app instance.

Command Registration Pattern:
1. Create a new command file in this directory (e.g., import_cmd.py)
2. Define the command function with @app.command() or similar
3. Import the command in this __init__.py
4. Register it in register_commands() function

This approach allows commands to be added without modifying main.py,
maintaining clean separation of concerns.

Example:
    # In import_cmd.py
    def import_cmd(version: str, source_path: str, dest_path: str) -> None:
        '''Import mods from source to destination'''
        pass

    # In __init__.py register_commands()
    app.command(name="import")(import_cmd)
"""

import typer

from .import_cmd import import_cmd
from .versions_cmd import versions


def register_commands(app: typer.Typer) -> None:
    """Register all CLI commands with the Typer application.

    This function is called during app initialization to register all
    available commands. Commands are imported and added to the app here.

    Args:
        app: The Typer application instance to register commands with

    Note:
        Commands are registered with custom names here. Each command is
        a separate function that can be tested and maintained independently.
        Adding new commands doesn't require modifying the framework.
    """
    # Register the import command
    app.command(name="import")(import_cmd)

    # Register the versions command (sample extensibility command)
    app.command(name="versions")(versions)
