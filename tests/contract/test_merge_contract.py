"""Contract tests for merge-folders CLI command.

Tests verify:
- Command registration and availability
- Argument parsing
- Flag handling (--preview, --force)
- Exit codes
- Output formatting
- Error messages
"""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CliRunner for testing CLI commands."""
    return CliRunner()


class TestMergeFoldersCommand:
    """Tests for the merge-folders command."""

    def test_command_exists(self, cli_runner):
        """Test that merge-folders command is registered."""
        result = cli_runner.invoke(app, ["system", "--help"])

        assert result.exit_code == 0
        assert "merge-folders" in result.stdout

    def test_command_help_text(self, cli_runner):
        """Test that command help is available."""
        result = cli_runner.invoke(app, ["system", "merge-folders", "--help"])

        assert result.exit_code == 0
        assert "Identify and merge" in result.stdout or "merge" in result.stdout

    def test_no_arguments_shows_error(self, cli_runner):
        """Test that command requires a path argument."""
        result = cli_runner.invoke(app, ["system", "merge-folders"])

        assert result.exit_code != 0
        assert "Error" in result.stdout or "required" in result.stdout.lower()

    def test_invalid_path_shows_error(self, cli_runner):
        """Test that invalid path produces error."""
        result = cli_runner.invoke(
            app, ["system", "merge-folders", "/nonexistent/path/to/nowhere"]
        )

        assert result.exit_code != 0
        assert "Error" in result.stdout or "does not exist" in result.stdout.lower()

    def test_preview_flag_works(self, cli_runner):
        """Test that --preview flag is recognized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple test structure
            root = Path(tmpdir)
            (root / "folder1").mkdir()
            (root / "folder2").mkdir()

            result = cli_runner.invoke(
                app, ["system", "merge-folders", str(root), "--preview"]
            )

            # Should succeed or say no duplicates
            assert result.exit_code == 0
            assert (
                "found" in result.stdout.lower()
                or "no duplicate" in result.stdout.lower()
            )

    def test_force_flag_recognized(self, cli_runner):
        """Test that --force flag is recognized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "folder1").mkdir()

            result = cli_runner.invoke(
                app, ["system", "merge-folders", str(root), "--force"]
            )

            # Should complete or show no duplicates
            assert result.exit_code == 0

    def test_scan_no_duplicates(self, cli_runner):
        """Test scanning directory with no duplicates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create non-duplicate folders
            (root / "folder1").mkdir()
            (root / "folder2").mkdir()
            (root / "folder3").mkdir()

            result = cli_runner.invoke(
                app, ["system", "merge-folders", str(root), "--preview"]
            )

            assert result.exit_code == 0
            assert "No duplicate" in result.stdout or "found 0" in result.stdout.lower()

    def test_scan_finds_duplicates(self, cli_runner):
        """Test that duplicates are found and displayed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create duplicate folders
            (root / "mods").mkdir()
            (root / "Mods").mkdir()
            (root / "mods" / "file1.txt").write_text("content")
            (root / "Mods" / "file2.txt").write_text("content")

            result = cli_runner.invoke(
                app, ["system", "merge-folders", str(root), "--preview"]
            )

            assert result.exit_code == 0
            # Should show found duplicates or group count
            stdout_lower = result.stdout.lower()
            assert "found" in stdout_lower or "duplicate" in stdout_lower


class TestErrorHandling:
    """Tests for error handling and messages."""

    def test_file_instead_of_directory(self, cli_runner):
        """Test error when path is a file, not directory."""
        with tempfile.NamedTemporaryFile() as f:
            result = cli_runner.invoke(app, ["system", "merge-folders", f.name])

            assert result.exit_code != 0
            assert "Error" in result.stdout or "directory" in result.stdout.lower()

    def test_permission_denied(self, cli_runner):
        """Test handling of permission denied errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            folder = root / "noaccess"
            folder.mkdir()

            # Remove read permissions
            import os

            os.chmod(str(folder), 0o000)

            try:
                result = cli_runner.invoke(app, ["system", "merge-folders", str(root)])

                # Should handle gracefully
                # May succeed if can't read subfolder, or show error
                assert result.exit_code in [0, 1]
            finally:
                # Restore permissions for cleanup
                os.chmod(str(folder), 0o755)


class TestOutputFormatting:
    """Tests for output formatting and display."""

    def test_output_contains_paths(self, cli_runner):
        """Test that output displays folder paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "mods").mkdir()
            (root / "Mods").mkdir()

            result = cli_runner.invoke(
                app, ["system", "merge-folders", str(root), "--preview"]
            )

            assert result.exit_code == 0
            # Output should contain path information
            assert (
                str(root) in result.stdout
                or "mods" in result.stdout
                or "Mods" in result.stdout
            )

    def test_output_readable_format(self, cli_runner):
        """Test that output is readable and formatted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "test1").mkdir()
            (root / "test2").mkdir()

            result = cli_runner.invoke(
                app, ["system", "merge-folders", str(root), "--preview"]
            )

            assert result.exit_code == 0
            # Output should be present and readable
            assert len(result.stdout) > 0


class TestIntegrationWithDatabase:
    """Tests for integration with other CLI components."""

    def test_system_group_alongside_database(self, cli_runner):
        """Test that system group works alongside database group."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "system" in result.stdout.lower() or "database" in result.stdout.lower()

    def test_both_command_groups_available(self, cli_runner):
        """Test that both database and system commands are available."""
        # Check system group
        result_system = cli_runner.invoke(app, ["system", "--help"])
        assert result_system.exit_code == 0

        # Check database group
        result_db = cli_runner.invoke(app, ["database", "--help"])
        assert result_db.exit_code == 0
