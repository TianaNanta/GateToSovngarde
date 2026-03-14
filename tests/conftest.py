"""Pytest configuration and fixtures for GateToSovngarde CLI tests.

This module provides reusable fixtures for testing the CLI application:
- temp_directories: Create temporary source/dest directories
- cli_runner: Typer CliRunner for testing CLI commands
- mock_database: Sample GTS database with test mods

All fixtures are automatically discovered by pytest through conftest.py.

Example usage in tests:
    def test_import_command(cli_runner, temp_directories):
        source_dir, dest_dir = temp_directories
        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])
        assert result.exit_code == 0
"""

import json
import tempfile
from pathlib import Path
from typing import Iterator, Tuple

import pytest
from typer.testing import CliRunner

from cli import __version__
from cli.db import DatabaseLoader


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CliRunner for testing CLI commands.

    The CliRunner allows simulating command-line invocations within tests,
    capturing output and exit codes for verification.

    Returns:
        CliRunner instance configured for testing

    Example:
        result = cli_runner.invoke(app, ["import", "GTSv101", "/src", "/dest"])
        assert result.exit_code == 0
    """
    return CliRunner()


@pytest.fixture
def temp_directories() -> Iterator[Tuple[str, str]]:
    """Create temporary source and destination directories for testing.

    Creates two temporary directories that can be used as source and
    destination paths in import command tests. Directories are automatically
    cleaned up after the test completes.

    Yields:
        Tuple of (source_path, dest_path) as strings

    Example:
        def test_import(temp_directories):
            source_dir, dest_dir = temp_directories
            # source_dir and dest_dir are empty directories ready for use
            create_test_file(source_dir / "test.esp")
    """
    with (
        tempfile.TemporaryDirectory() as source_dir,
        tempfile.TemporaryDirectory() as dest_dir,
    ):
        yield source_dir, dest_dir


@pytest.fixture
def mock_database() -> dict:
    """Provide a sample GTS database for unit testing.

    Returns a dictionary representing a GTS version database with
    3 sample mods. Useful for testing database-related functions
    without relying on bundled database files.

    Returns:
        Dictionary with keys:
        - version_id: "GTSv101"
        - version_name: "GateToSovngarde v1.01"
        - created_date: "2026-03-14"
        - mods: List of 3 sample mod dictionaries

    Example:
        def test_mod_count(mock_database):
            assert len(mock_database["mods"]) == 3
            assert mock_database["version_id"] == "GTSv101"
    """
    return {
        "version_id": "GTSv101",
        "version_name": "GateToSovngarde v1.01",
        "created_date": "2026-03-14",
        "mods": [
            {
                "id": "mod_quest_001",
                "name": "Quest Pack Alpha",
                "description": "First set of custom quests",
                "author": "Quest Maker",
                "version": "1.0.0",
                "required_files": ["quest_001.esp", "quest_001_dialogue.esm"],
                "conflicts_with": [],
                "tags": ["quest", "story"],
            },
            {
                "id": "mod_armor_001",
                "name": "Armor Collection",
                "description": "Enhanced armor set",
                "author": "Armor Designer",
                "version": "2.1.0",
                "required_files": ["armor_set.esp"],
                "conflicts_with": ["mod_armor_002"],
                "tags": ["armor", "equipment"],
            },
            {
                "id": "mod_weapons_001",
                "name": "Weapon Enhancement",
                "description": "New weapons and balance tweaks",
                "author": "Weapon Master",
                "version": "1.5.0",
                "required_files": ["weapons.esp", "weapons_textures.bsa"],
                "conflicts_with": [],
                "tags": ["weapons", "combat"],
            },
        ],
    }


@pytest.fixture
def database_loader() -> DatabaseLoader:
    """Provide a DatabaseLoader instance for testing.

    Returns a fresh DatabaseLoader instance with an empty cache,
    suitable for testing database loading and caching behavior.

    Returns:
        DatabaseLoader instance

    Example:
        def test_load_version(database_loader):
            db = database_loader.get_version("GTSv101")
            assert db["version_id"] == "GTSv101"
    """
    return DatabaseLoader()
