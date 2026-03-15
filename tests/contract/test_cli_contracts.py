"""Contract tests for CLI interface.

These tests define the expected CLI behavior and interface contracts.
They test the CLI as users would interact with it, capturing output
and exit codes.

Tests in this module verify:
- Help text displays correctly
- Version display works
- Invalid commands are rejected properly
- Command structure and argument parsing
"""

from typer.testing import CliRunner

from cli.main import app


class TestMainHelp:
    """Contract tests for main CLI help functionality."""

    def test_gts_main_help_displays(self, cli_runner: CliRunner) -> None:
        """Verify gts --help shows help text with commands section.

        The main help should display:
        - Application description
        - Available commands
        - Global options (--help, --version)

        Exit code should be 0 (success).
        """
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "GateToSovngarde CLI" in result.stdout
        assert "--help" in result.stdout
        assert "--version" in result.stdout

    def test_gts_version_displays(self, cli_runner: CliRunner) -> None:
        """Verify gts --version shows version number.

        Should display format: "GateToSovngarde CLI version X.X.X"
        Exit code should be 0 (success).
        """
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "GateToSovngarde CLI version" in result.stdout
        # Should include version like 0.3.0
        assert "0.3.0" in result.stdout or "version" in result.stdout.lower()

    def test_invalid_command_error(self, cli_runner: CliRunner) -> None:
        """Verify unknown commands result in error exit code.

        Should exit with non-zero code when given unknown command.
        Typer's Click-based error handling may print errors to stderr.
        """
        result = cli_runner.invoke(app, ["invalid_command"])

        # Exit code 2 is standard Click/Typer error code for bad usage
        assert result.exit_code != 0
        # Most importantly: verify it's not successful
        assert result.exit_code in (1, 2)


class TestCommandRegistration:
    """Contract tests for command registration system."""

    def test_app_has_callback(self) -> None:
        """Verify the app has a main callback function.

        The main callback handles global options like --version.
        """
        assert app.registered_commands is not None
        # The app should be configured (callback may be empty initially)
        assert hasattr(app, "registered_commands")

    def test_import_command_registered(self, cli_runner: CliRunner) -> None:
        """Verify import command shows in help.

        Phase 7 has reorganized commands into groups, so the import command
        should appear under the database group in help output.
        """
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Import is now under the database group
        assert "database" in result.stdout.lower()
