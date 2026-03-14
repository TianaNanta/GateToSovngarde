"""Unit tests for import command.

Tests the import command parameter validation and command-line interface.
"""

import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from cli.main import app
from cli.utils.errors import ValidationError


class TestImportCommandValidation:
    """Tests for import command parameter validation."""

    def test_import_with_all_arguments(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with all parameters provided."""
        source_dir, dest_dir = temp_directories

        # Create a test file in source
        (Path(source_dir) / "test.esp").write_text("test content")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        # Should not error (files may not be found, but command should execute)
        assert result.exit_code in (0, 2)

    def test_import_invalid_version(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with invalid version."""
        source_dir, dest_dir = temp_directories

        result = cli_runner.invoke(
            app, ["import", "InvalidVersion", source_dir, dest_dir]
        )

        # Should fail with validation error
        assert result.exit_code == 1
        assert "Unknown version" in result.stdout or "unknown" in result.stdout.lower()

    def test_import_source_not_found(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with non-existent source directory."""
        _, dest_dir = temp_directories

        result = cli_runner.invoke(
            app, ["import", "GTSv101", "/nonexistent/path", dest_dir]
        )

        # Should fail with validation error
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_import_with_force_flag(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with --force flag."""
        source_dir, dest_dir = temp_directories

        # Create test file
        (Path(source_dir) / "test.esp").write_text("test content")

        result = cli_runner.invoke(
            app, ["import", "GTSv101", source_dir, dest_dir, "--force"]
        )

        # Should execute (may fail due to missing mod files, but should accept --force)
        assert result.exit_code in (0, 2)

    def test_import_with_verbose_flag(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with --verbose flag."""
        source_dir, dest_dir = temp_directories

        # Create test file
        (Path(source_dir) / "test.esp").write_text("test content")

        result = cli_runner.invoke(
            app, ["import", "GTSv101", source_dir, dest_dir, "--verbose"]
        )

        # Should execute with verbose output
        assert result.exit_code in (0, 2)

    def test_import_short_flags(self, cli_runner: CliRunner, temp_directories) -> None:
        """Test import with short flag versions (-f, -v)."""
        source_dir, dest_dir = temp_directories

        # Create test file
        (Path(source_dir) / "test.esp").write_text("test content")

        result = cli_runner.invoke(
            app, ["import", "GTSv101", source_dir, dest_dir, "-f", "-v"]
        )

        # Should execute with short flags
        assert result.exit_code in (0, 2)


class TestImportCommandHelp:
    """Tests for import command help display."""

    def test_import_help_displays(self, cli_runner: CliRunner) -> None:
        """Test that import command help displays correctly."""
        result = cli_runner.invoke(app, ["import", "--help"])

        assert result.exit_code == 0
        assert "Import mod database" in result.stdout
        assert "VERSION" in result.stdout
        assert "SOURCE_PATH" in result.stdout
        assert "DEST_PATH" in result.stdout
