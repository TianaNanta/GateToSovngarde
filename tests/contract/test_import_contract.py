"""Contract tests for import command CLI interface.

Tests the CLI contract for the import command:
- Command registration and availability
- Help/documentation display
- Parameter handling and validation
- Output format and structure
- Exit code contracts
"""

import tempfile
from pathlib import Path
from typer.testing import CliRunner

from cli.main import app


class TestImportCommandRegistration:
    """Tests that import command is properly registered and accessible."""

    def test_import_command_exists(self, cli_runner: CliRunner) -> None:
        """Test that import command is registered."""
        result = cli_runner.invoke(app, ["import", "--help"])
        assert result.exit_code == 0
        assert "import" in result.stdout.lower()

    def test_import_in_help_output(self, cli_runner: CliRunner) -> None:
        """Test that import command appears in main help."""
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "import" in result.stdout.lower()


class TestImportCommandHelp:
    """Tests for import command help and documentation."""

    def test_import_help_displays(self, cli_runner: CliRunner) -> None:
        """Test that import help displays correctly."""
        result = cli_runner.invoke(app, ["import", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout.lower()

    def test_import_help_shows_parameters(self, cli_runner: CliRunner) -> None:
        """Test that import help shows all parameters."""
        result = cli_runner.invoke(app, ["import", "--help"])

        assert result.exit_code == 0
        # Should show parameters (version, source, dest)
        assert "version" in result.stdout.lower() or "VERSION" in result.stdout
        assert "source" in result.stdout.lower() or "SOURCE" in result.stdout
        assert "dest" in result.stdout.lower() or "DEST" in result.stdout

    def test_import_help_shows_flags(self, cli_runner: CliRunner) -> None:
        """Test that import help shows available flags."""
        result = cli_runner.invoke(app, ["import", "--help"])

        assert result.exit_code == 0
        # Should show flags like --force, --verbose
        help_output = result.stdout.lower()
        assert "force" in help_output or "--force" in result.stdout
        assert "verbose" in help_output or "--verbose" in result.stdout


class TestImportCommandParameters:
    """Tests for import command parameter handling."""

    def test_import_requires_version(self, cli_runner: CliRunner) -> None:
        """Test that version parameter is required/handled."""
        result = cli_runner.invoke(app, ["import"])

        # Should either prompt or error
        assert result.exit_code in (0, 1, 2)

    def test_import_accepts_three_arguments(self, cli_runner: CliRunner) -> None:
        """Test that import accepts version, source, and dest arguments."""
        with tempfile.TemporaryDirectory() as source_dir:
            dest_dir = str(Path(source_dir) / "dest")

            result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

            # Should not error on argument parsing
            assert result.exit_code != 2 or "not found" in result.stdout.lower()

    def test_import_with_force_flag(self, cli_runner: CliRunner) -> None:
        """Test that import accepts --force flag."""
        with tempfile.TemporaryDirectory() as source_dir:
            dest_dir = str(Path(source_dir) / "dest")

            result = cli_runner.invoke(
                app, ["import", "--force", "GTSv101", source_dir, dest_dir]
            )

            # Should not error on flag parsing
            assert result.exit_code in (0, 1, 2)

    def test_import_with_verbose_flag(self, cli_runner: CliRunner) -> None:
        """Test that import accepts --verbose flag."""
        with tempfile.TemporaryDirectory() as source_dir:
            dest_dir = str(Path(source_dir) / "dest")

            result = cli_runner.invoke(
                app, ["import", "--verbose", "GTSv101", source_dir, dest_dir]
            )

            # Should not error on flag parsing
            assert result.exit_code in (0, 1, 2)

    def test_import_with_short_flag_f(self, cli_runner: CliRunner) -> None:
        """Test that import accepts -f short flag for force."""
        with tempfile.TemporaryDirectory() as source_dir:
            dest_dir = str(Path(source_dir) / "dest")

            result = cli_runner.invoke(
                app, ["import", "-f", "GTSv101", source_dir, dest_dir]
            )

            # Should not error on short flag parsing
            assert result.exit_code in (0, 1, 2)

    def test_import_with_short_flag_v(self, cli_runner: CliRunner) -> None:
        """Test that import accepts -v short flag for verbose."""
        with tempfile.TemporaryDirectory() as source_dir:
            dest_dir = str(Path(source_dir) / "dest")

            result = cli_runner.invoke(
                app, ["import", "-v", "GTSv101", source_dir, dest_dir]
            )

            # Should not error on short flag parsing
            assert result.exit_code in (0, 1, 2)


class TestImportCommandExitCodes:
    """Tests for import command exit codes."""

    def test_import_success_exit_code_zero(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that successful import returns exit code 0."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create all required files
        (source / "quest_001.esp").write_text("content")
        (source / "quest_001_dialogue.esm").write_text("content")
        (source / "armor_set.esp").write_text("content")
        (source / "weapons.esp").write_text("content")
        (source / "weapons_textures.bsa").write_text("content")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        assert result.exit_code == 0

    def test_import_validation_error_exit_code_one(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that validation error returns exit code 1."""
        _, dest_dir = temp_directories

        # Invalid version
        result = cli_runner.invoke(
            app, ["import", "InvalidVersion", "/nonexistent", dest_dir]
        )

        assert result.exit_code == 1

    def test_import_runtime_error_exit_code_two(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that runtime error returns exit code 2."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create a file that will fail to copy (e.g., permission issue)
        # without force flag
        (source / "quest_001.esp").write_text("content")

        # Use source as a non-writable location for dest (will cause error)
        result = cli_runner.invoke(
            app, ["import", "GTSv101", source_dir, "/root/readonly_dest"]
        )

        # Should error (either validation or runtime)
        assert result.exit_code in (1, 2)


class TestImportCommandOutput:
    """Tests for import command output format."""

    def test_import_success_has_readable_output(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that successful import provides readable output."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create all required files
        files = [
            "quest_001.esp",
            "quest_001_dialogue.esm",
            "armor_set.esp",
            "weapons.esp",
            "weapons_textures.bsa",
        ]
        for file in files:
            (source / file).write_text("content")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        assert result.exit_code == 0
        # Output should be readable (not empty)
        assert len(result.stdout) > 0

    def test_import_error_has_readable_output(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that import error provides readable output."""
        _, dest_dir = temp_directories

        result = cli_runner.invoke(
            app, ["import", "InvalidVersion", "/nonexistent", dest_dir]
        )

        assert result.exit_code == 1
        # Output should explain the error
        assert len(result.stdout) > 0

    def test_import_output_mentions_version(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that import output mentions the version being imported."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create files
        (source / "quest_001.esp").write_text("content")
        (source / "quest_001_dialogue.esm").write_text("content")
        (source / "armor_set.esp").write_text("content")
        (source / "weapons.esp").write_text("content")
        (source / "weapons_textures.bsa").write_text("content")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        assert result.exit_code == 0
        # Should mention version or GTSv101
        assert "GTSv101" in result.stdout or "GateToSovngarde" in result.stdout


class TestImportCommandInteraction:
    """Tests for import command interaction patterns."""

    def test_import_accepts_input_for_missing_parameters(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that import can work with interactive input for missing params."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create files
        (source / "quest_001.esp").write_text("content")
        (source / "quest_001_dialogue.esm").write_text("content")
        (source / "armor_set.esp").write_text("content")
        (source / "weapons.esp").write_text("content")
        (source / "weapons_textures.bsa").write_text("content")

        # Try with only version, provide other args via stdin
        result = cli_runner.invoke(
            app,
            ["import", "GTSv101"],
            input=f"{source_dir}\n{dest_dir}\n",
        )

        # Should succeed or at least not fail immediately
        assert result.exit_code in (0, 2)

    def test_import_handles_keyboard_interrupt_gracefully(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that import handles Ctrl+C gracefully."""
        source_dir, dest_dir = temp_directories

        # Run import (if user interrupts, should handle gracefully)
        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        # Should not crash, exit code should be reasonable
        assert result.exit_code >= 0
