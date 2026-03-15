"""Full workflow integration test for GateToSovngarde CLI.

This test validates the complete user journey from installation through
successful command execution. It simulates real-world usage patterns.
"""

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from cli.main import app


class TestFullWorkflow:
    """End-to-end workflow tests."""

    def test_help_command_works(self) -> None:
        """Test: gts --help displays help without errors."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "GateToSovngarde" in result.stdout
        assert "database" in result.stdout.lower()

    def test_version_command_works(self) -> None:
        """Test: gts --version displays version."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()
        assert "0.3.1" in result.stdout

    def test_database_group_accessible(self) -> None:
        """Test: Database group is accessible and lists subcommands."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout
        assert "versions" in result.stdout

    def test_versions_command_lists_databases(self) -> None:
        """Test: gts database versions displays available versions."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "versions"])

        assert result.exit_code == 0
        # Should list GTSv101
        assert "GTSv101" in result.stdout
        # Should have success indicator
        assert "✓" in result.stdout

    def test_versions_verbose_displays_table(self) -> None:
        """Test: gts database versions --verbose shows detailed table."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "versions", "--verbose"])

        assert result.exit_code == 0
        # Verbose should show table formatting
        assert "GTSv101" in result.stdout

    def test_versions_specific_version_works(self) -> None:
        """Test: gts database versions GTSv101 shows specific version."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "versions", "GTSv101"])

        assert result.exit_code == 0
        assert "GTSv101" in result.stdout

    def test_import_help_available(self) -> None:
        """Test: gts database import --help shows command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout.lower()
        # Should show parameters
        assert "VERSION" in result.stdout or "version" in result.stdout.lower()

    def test_import_rejects_invalid_version(self) -> None:
        """Test: Import rejects invalid version with helpful error."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["database", "import", "InvalidVersion", "/src", "/dst"]
        )

        # Should fail with validation error
        assert result.exit_code == 1
        # Should show error message
        assert (
            "Error" in result.stdout
            or "Unknown" in result.stdout
            or "not found" in result.stdout.lower()
        )

    def test_import_rejects_missing_source(self) -> None:
        """Test: Import rejects non-existent source directory."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["database", "import", "GTSv101", "/nonexistent/path", "/dst"]
        )

        # Should fail with validation error
        assert result.exit_code == 1
        # Should show helpful error
        assert result.stdout or result.stderr

    def test_full_import_workflow(self, use_mock_database_for_tests) -> None:
        """Test: Complete import workflow with real files."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            dest = Path(temp_dir) / "dest"
            source.mkdir()

            # Create required mod archives for GTSv101
            (source / "Quest Pack Alpha.7z").write_text("archive content")
            (source / "Armor Collection.7z").write_text("archive content")
            (source / "Weapon Enhancement.7z").write_text("archive content")

            result = runner.invoke(
                app, ["database", "import", "GTSv101", str(source), str(dest)]
            )

            # Should succeed
            assert result.exit_code == 0
            # Should show success message
            assert "✓" in result.stdout or "success" in result.stdout.lower()

    def test_command_discovery_progression(self) -> None:
        """Test: User can discover commands progressively.

        This tests the user's journey:
        1. gts --help (shows groups)
        2. gts database --help (shows commands)
        3. gts database import --help (shows command details)
        """
        runner = CliRunner()

        # Step 1: Main help shows database group
        main_help = runner.invoke(app, ["--help"])
        assert main_help.exit_code == 0
        assert "database" in main_help.stdout.lower()

        # Step 2: Group help shows commands
        database_help = runner.invoke(app, ["database", "--help"])
        assert database_help.exit_code == 0
        assert "import" in database_help.stdout
        assert "versions" in database_help.stdout

        # Step 3: Command help shows details
        import_help = runner.invoke(app, ["database", "import", "--help"])
        assert import_help.exit_code == 0
        assert "import" in import_help.stdout.lower()

    def test_error_exit_codes_correct(self) -> None:
        """Test: Commands return correct exit codes.

        Exit codes should follow convention:
        - 0: Success
        - 1: Validation error (user error)
        - 2: Operation error (system error)
        """
        runner = CliRunner()

        # Success
        success = runner.invoke(app, ["database", "versions"])
        assert success.exit_code == 0

        # Validation error (invalid version)
        validation = runner.invoke(
            app, ["database", "import", "Invalid", "/src", "/dst"]
        )
        assert validation.exit_code == 1

    def test_all_groups_discoverable(self) -> None:
        """Test: All command groups are discoverable from help."""
        runner = CliRunner()

        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Should show database group
        assert "database" in result.stdout.lower()

    def test_help_text_consistent(self) -> None:
        """Test: Help text is consistent and professional."""
        runner = CliRunner()

        results = [
            runner.invoke(app, ["--help"]),
            runner.invoke(app, ["database", "--help"]),
            runner.invoke(app, ["database", "import", "--help"]),
            runner.invoke(app, ["database", "versions", "--help"]),
        ]

        for result in results:
            assert result.exit_code == 0
            # All should have help content
            assert "--help" in result.stdout or "help" in result.stdout.lower()

    def test_version_command_standalone(self) -> None:
        """Test: Version command works without other arguments."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()
        # Should not require any other arguments
        assert "Error" not in result.stdout or "error" not in result.stdout.lower()
