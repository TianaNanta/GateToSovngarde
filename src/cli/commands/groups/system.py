"""System command group definition and registration.

This module creates and configures the system command group sub-app,
then imports and registers all system-related commands into it.
"""

import typer

from ..system.merge_cmd import merge_cmd

# Create the system sub-application
system_app = typer.Typer(
    help="System utilities for file management",
    rich_markup_mode="rich",
)

# Register commands into the system group
system_app.command(name="merge-folders")(merge_cmd)
