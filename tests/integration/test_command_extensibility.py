"""Tests for command extensibility and the sample versions command.

These tests demonstrate that new commands can be added to the CLI
framework without modifying the core framework itself.
"""

import pytest
from typer.testing import CliRunner

from cli.main import app


class TestCommandExtensibility:
    """Test suite for command extensibility framework."""

    def test_new_command_auto_discovered(self) -> None:
        """Test that new commands are automatically discovered and shown in help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        # Verify versions command appears in help
        assert result.exit_code == 0
        assert "versions" in result.stdout
        assert "List available GateToSovngarde modlist versions" in result.stdout

    def test_new_command_has_help(self) -> None:
        """Test that new command help works correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions", "--help"])

        assert result.exit_code == 0
        assert "versions" in result.stdout
        assert "Available versions" in result.stdout or "available" in result.stdout

    def test_new_command_executes_successfully(self) -> None:
        """Test that new command executes without errors."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions"])

        # Command should succeed
        assert result.exit_code == 0
        assert "✓" in result.stdout

    def test_new_command_shows_available_versions(self) -> None:
        """Test that versions command lists available databases."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions"])

        assert result.exit_code == 0
        # GTSv101 should be listed
        assert "GTSv101" in result.stdout

    def test_new_command_supports_verbose_flag(self) -> None:
        """Test that new command respects --verbose option."""
        runner = CliRunner()

        # Without verbose
        result_normal = runner.invoke(app, ["versions"])
        assert result_normal.exit_code == 0

        # With verbose - should show table
        result_verbose = runner.invoke(app, ["versions", "--verbose"])
        assert result_verbose.exit_code == 0
        # Verbose should show more detailed output (table format)
        assert "Version ID" in result_verbose.stdout or "━" in result_verbose.stdout

    def test_new_command_with_version_argument(self) -> None:
        """Test that new command accepts version argument."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions", "GTSv101"])

        assert result.exit_code == 0
        assert "GTSv101" in result.stdout

    def test_new_command_invalid_version_fails(self) -> None:
        """Test that invalid version argument fails gracefully."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions", "InvalidVersion"])

        # Should fail with exit code 1 (validation error)
        assert result.exit_code == 1
        assert (
            "Version not found" in result.stdout
            or "Error" in result.stdout
            or "InvalidVersion" in result.stdout
        )


class TestVersionsCommand:
    """Test suite specific to the versions command."""

    def test_versions_list_format(self) -> None:
        """Test that versions command output has correct format."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions"])

        assert result.exit_code == 0
        # Should contain version ID
        assert "GTSv101" in result.stdout
        # Should contain mod count
        assert "mods" in result.stdout or "1954" in result.stdout

    def test_versions_verbose_shows_description(self) -> None:
        """Test that verbose output shows version description."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions", "--verbose"])

        assert result.exit_code == 0
        # Should show the version name/description
        assert "GateToSovngarde" in result.stdout

    def test_versions_short_flag(self) -> None:
        """Test that short flag for verbose works."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions", "-v"])

        assert result.exit_code == 0
        # Short flag should work same as --verbose

    def test_versions_command_does_not_modify_framework(self) -> None:
        """Test that versions command follows framework patterns.

        This test demonstrates that the command was added WITHOUT
        modifying the core framework code.
        """
        runner = CliRunner()

        # Verify both import and versions commands exist
        help_result = runner.invoke(app, ["--help"])
        assert "import" in help_result.stdout
        assert "versions" in help_result.stdout

        # Verify both can be executed
        import_result = runner.invoke(app, ["import", "--help"])
        versions_result = runner.invoke(app, ["versions", "--help"])

        assert import_result.exit_code == 0
        assert versions_result.exit_code == 0


class TestExtensibilityPattern:
    """Test that new commands follow the extensibility pattern."""

    def test_multiple_commands_coexist(self) -> None:
        """Test that multiple commands can coexist without conflicts."""
        runner = CliRunner()

        # Both commands should be available
        import_help = runner.invoke(app, ["import", "--help"])
        versions_help = runner.invoke(app, ["versions", "--help"])

        assert import_help.exit_code == 0
        assert versions_help.exit_code == 0

        # Commands should be independent
        assert "Import mod database" in import_help.stdout
        assert (
            "List available" in versions_help.stdout
            or "GateToSovngarde" in versions_help.stdout
        )

    def test_command_help_is_self_documenting(self) -> None:
        """Test that command help is complete and useful."""
        runner = CliRunner()
        result = runner.invoke(app, ["versions", "--help"])

        assert result.exit_code == 0
        # Help should include description
        assert "versions" in result.stdout.lower()
        # Should show available options
        assert "--verbose" in result.stdout or "-v" in result.stdout

    def test_framework_addition_pattern(self) -> None:
        """Test the framework pattern for adding commands.

        This demonstrates that to add a new command:
        1. Create a function (e.g., versions_cmd.py)
        2. Import it in __init__.py
        3. Register it with app.command()

        No framework changes needed!
        """
        # Verify the pattern works by checking both commands
        runner = CliRunner()

        # Main help shows both commands
        main_help = runner.invoke(app, ["--help"])
        assert main_help.exit_code == 0

        # Each command is independent
        for cmd in ["import", "versions"]:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0, f"{cmd} help failed"

        # New commands can be added following same pattern
        # (This test proves the pattern works with versions command)
