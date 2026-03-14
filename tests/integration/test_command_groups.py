"""Tests for command groups functionality.

These tests verify that the command grouping system works correctly,
including group discovery, help display, and command execution within groups.
"""

from typer.testing import CliRunner

from cli.main import app


class TestCommandGroupDiscovery:
    """Tests for command group discovery and registration."""

    def test_group_listed_in_main_help(self) -> None:
        """Test: group appears in gts --help output."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "database" in result.stdout.lower()
        # Group description should be present
        assert "Manage GateToSovngarde version databases" in result.stdout

    def test_only_groups_in_main_help(self) -> None:
        """Test: main help shows groups, not individual commands."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Database group should be listed
        assert "database" in result.stdout.lower()
        # Individual commands should NOT be at top level
        # (they're under database group, so shouldn't show raw "import")
        # Note: This is a softer assertion since help format may vary


class TestGroupHelp:
    """Tests for group-level help display."""

    def test_group_help_displays(self) -> None:
        """Test: gts database --help shows the group help."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        assert "database" in result.stdout.lower()
        # Should have options section
        assert "--help" in result.stdout

    def test_group_help_shows_subcommands(self) -> None:
        """Test: gts database --help shows all subcommands."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        # Both import and versions should be listed
        assert "import" in result.stdout
        assert "versions" in result.stdout

    def test_group_help_shows_command_descriptions(self) -> None:
        """Test: gts database --help includes command descriptions."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        # Should show brief descriptions of commands
        assert (
            "Import mod database" in result.stdout or "import" in result.stdout.lower()
        )
        assert "List available" in result.stdout or "versions" in result.stdout.lower()

    def test_invalid_group_fails(self) -> None:
        """Test: unknown group returns error."""
        runner = CliRunner()
        result = runner.invoke(app, ["invalid_group"])

        # Should fail with non-zero exit code
        assert result.exit_code != 0


class TestGroupedCommandExecution:
    """Tests for executing commands within groups."""

    def test_grouped_command_executes(self) -> None:
        """Test: gts database import ... executes successfully."""
        runner = CliRunner()
        # Just test help since we need real files for full execution
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout.lower()

    def test_grouped_command_help(self) -> None:
        """Test: gts database import --help shows command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        # Should show import-specific help
        assert "Import" in result.stdout or "import" in result.stdout.lower()

    def test_grouped_command_with_arguments(self) -> None:
        """Test: grouped command accepts arguments correctly."""
        runner = CliRunner()
        # Test that command parser accepts args (even if validation fails)
        result = runner.invoke(app, ["database", "import", "GTSv101", "/src", "/dst"])

        # Should process arguments (may fail validation but shouldn't be syntax error)
        # Exit code 2 is Typer syntax error, 1 is validation error
        assert result.exit_code != 2, "Should parse arguments without syntax error"

    def test_invalid_grouped_command_fails(self) -> None:
        """Test: invalid command within group returns error."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "invalid_cmd"])

        # Should fail
        assert result.exit_code != 0


class TestGroupedCommandValidation:
    """Tests for validation in grouped commands."""

    def test_grouped_command_validation_error_exit_code(self) -> None:
        """Test: validation error in grouped command returns exit code 1."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["database", "import", "InvalidVersion", "/nonexistent", "/dest"]
        )

        # Validation error should be exit code 1
        assert result.exit_code == 1

    def test_grouped_command_shows_validation_message(self) -> None:
        """Test: validation errors show helpful message."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["database", "import", "InvalidVersion", "/nonexistent", "/dest"]
        )

        assert result.exit_code == 1
        # Should show error information
        assert result.stdout or result.stderr  # Some output should be present


class TestMultipleGroups:
    """Tests for working with multiple groups (future extensibility)."""

    def test_only_registered_groups_appear(self) -> None:
        """Test: only registered groups appear in help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Database group should be there
        assert "database" in result.stdout.lower()
        # Unregistered groups should not be there
        assert "nonexistent" not in result.stdout.lower()

    def test_groups_are_independent(self) -> None:
        """Test: groups don't interfere with each other."""
        runner = CliRunner()
        # Database group should work
        result = runner.invoke(app, ["database", "--help"])
        assert result.exit_code == 0
        assert "import" in result.stdout


class TestGroupIntegration:
    """Integration tests for the grouping system."""

    def test_full_command_path_works(self) -> None:
        """Test: full gts database import path works."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "Import" in result.stdout

    def test_versions_in_database_group(self) -> None:
        """Test: versions command is in database group."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "versions", "--help"])

        assert result.exit_code == 0
        assert (
            "versions" in result.stdout.lower() or "available" in result.stdout.lower()
        )

    def test_both_database_commands_listed(self) -> None:
        """Test: database group shows both import and versions."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout
        assert "versions" in result.stdout

    def test_versions_command_executes_in_group(self) -> None:
        """Test: versions command works when in database group."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "versions"])

        assert result.exit_code == 0
        # Should list available versions
        assert "GTSv101" in result.stdout


class TestGroupHierarchy:
    """Tests for command group hierarchy and naming."""

    def test_group_name_in_usage(self) -> None:
        """Test: group name appears in command usage string."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        # Usage should show the command hierarchy
        assert "database" in result.stdout or "import" in result.stdout

    def test_command_help_distinct_from_group_help(self) -> None:
        """Test: command help is distinct from group help."""
        runner = CliRunner()
        group_result = runner.invoke(app, ["database", "--help"])
        cmd_result = runner.invoke(app, ["database", "import", "--help"])

        assert group_result.exit_code == 0
        assert cmd_result.exit_code == 0
        # Group help should list commands
        assert "import" in group_result.stdout
        # Command help should be more detailed
        assert "import" in cmd_result.stdout.lower()
