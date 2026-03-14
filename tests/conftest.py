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

import tempfile
from typing import Iterator, Tuple

import pytest
from typer.testing import CliRunner

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
    """Provide a sample GTS database for unit testing with archived mods.

    Returns a dictionary representing a GTS version database with
    3 sample archived mods. Useful for testing database-related functions
    without relying on bundled database files.

    Returns:
        Dictionary with keys:
        - version_id: "GTSv101"
        - version_name: "GateToSovngarde v1.01 - Archived Mods"
        - created_date: "2026-03-14"
        - mods: List of 3 sample mod dictionaries with archive file support

    Example:
        def test_mod_count(mock_database):
            assert len(mock_database["mods"]) == 3
            assert mock_database["version_id"] == "GTSv101"
    """
    return {
        "version_id": "GTSv101",
        "version_name": "GateToSovngarde v1.01 - Archived Mods",
        "created_date": "2026-03-14",
        "mods": [
            {
                "id": "mod_1",
                "name": "Quest Pack Alpha",
                "description": "Archived mod: Quest Pack Alpha",
                "author": "Unknown",
                "version": "1.0",
                "required_files": [
                    "Quest Pack Alpha.7z",
                    "Quest Pack Alpha.rar",
                    "Quest Pack Alpha.zip",
                    "Quest Pack Alpha.tar.xz",
                    "Quest Pack Alpha.tar.gz",
                    "Quest Pack Alpha.tar",
                    "Quest Pack Alpha.iso",
                ],
                "conflicts_with": [],
                "tags": ["archived"],
            },
            {
                "id": "mod_2",
                "name": "Armor Collection",
                "description": "Archived mod: Armor Collection",
                "author": "Unknown",
                "version": "1.0",
                "required_files": [
                    "Armor Collection.7z",
                    "Armor Collection.rar",
                    "Armor Collection.zip",
                    "Armor Collection.tar.xz",
                    "Armor Collection.tar.gz",
                    "Armor Collection.tar",
                    "Armor Collection.iso",
                ],
                "conflicts_with": [],
                "tags": ["archived"],
            },
            {
                "id": "mod_3",
                "name": "Weapon Enhancement",
                "description": "Archived mod: Weapon Enhancement",
                "author": "Unknown",
                "version": "1.0",
                "required_files": [
                    "Weapon Enhancement.7z",
                    "Weapon Enhancement.rar",
                    "Weapon Enhancement.zip",
                    "Weapon Enhancement.tar.xz",
                    "Weapon Enhancement.tar.gz",
                    "Weapon Enhancement.tar",
                    "Weapon Enhancement.iso",
                ],
                "conflicts_with": [],
                "tags": ["archived"],
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


@pytest.fixture
def mock_database_loader(mock_database) -> DatabaseLoader:
    """Provide a DatabaseLoader with a pre-populated mock database.

    Returns a DatabaseLoader configured to return the mock database
    for test version lookups, useful for testing import workflows
    without loading real large databases.

    Args:
        mock_database: The mock database fixture

    Returns:
        DatabaseLoader instance with mock data

    Example:
        def test_import_with_mock_db(mock_database_loader):
            db = mock_database_loader.get_version("GTSv101")
            assert len(db["mods"]) == 3
    """
    loader = DatabaseLoader()
    # Pre-populate the cache with mock data
    loader._cache["GTSv101"] = mock_database
    return loader


@pytest.fixture
def use_mock_database_for_tests(monkeypatch, mock_database) -> None:
    """Use mock database for a specific test.

    This fixture monkeypatches the DatabaseLoader to return mock data
    for the test, preventing tests from loading the large real database.
    This speeds up tests and makes them more isolated.

    This is NOT autouse - individual tests must opt-in by requesting this fixture.

    Args:
        monkeypatch: Pytest monkeypatch fixture
        mock_database: The mock database fixture

    Example:
        def test_import_with_mock_db(use_mock_database_for_tests):
            # Test code that uses mocked GTSv101 database
            pass
    """
    from cli.db import DatabaseLoader

    original_get_version = DatabaseLoader.get_version

    def mock_get_version(self, version_id: str) -> dict:
        """Return mock database for testing."""
        if version_id == "GTSv101":
            return mock_database
        # Fall back to original for other versions
        return original_get_version(self, version_id)

    monkeypatch.setattr(DatabaseLoader, "get_version", mock_get_version)
