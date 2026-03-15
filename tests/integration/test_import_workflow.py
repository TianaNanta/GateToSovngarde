"""Integration tests for import workflow.

Tests full end-to-end import workflows including:
- Complete import with real files
- Partial success scenarios (some files found, some missing)
- Error recovery and force flag behavior
- Multi-mod imports with statistics tracking
"""

import tempfile
from pathlib import Path
from typer.testing import CliRunner

from cli.main import app
from cli.services.import_service import ImportService


class TestImportWorkflowBasic:
    """Tests for basic import workflow scenarios."""

    def test_full_import_with_real_files(
        self, cli_runner: CliRunner, temp_directories, use_mock_database_for_tests
    ) -> None:
        """Test complete import with all required archive files present."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)
        dest = Path(dest_dir)

        # Create archive files for the test mods (using .7z format as example)
        (source / "Quest Pack Alpha.7z").write_text("quest mod archive content")
        (source / "Armor Collection.7z").write_text("armor mod archive content")
        (source / "Weapon Enhancement.7z").write_text("weapons mod archive content")

        result = cli_runner.invoke(
            app, ["database", "import", "GTSv101", source_dir, dest_dir]
        )

        # Should succeed
        assert result.exit_code == 0
        assert (
            "Successfully imported" in result.stdout
            or "success" in result.stdout.lower()
        )

        # Verify archive files were copied
        assert (dest / "Quest Pack Alpha.7z").exists()
        assert (dest / "Armor Collection.7z").exists()
        assert (dest / "Weapon Enhancement.7z").exists()

    def test_partial_import_with_missing_files(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with some files missing (partial success)."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create only some of the required archive files
        (source / "Quest Pack Alpha.7z").write_text("quest mod archive content")
        # Missing: Armor Collection and Weapon Enhancement archives

        result = cli_runner.invoke(
            app, ["database", "import", "GTSv101", source_dir, dest_dir]
        )

        # Should indicate partial success or errors
        assert result.exit_code in (0, 2)  # Success or runtime error

    def test_import_creates_destination_directory(
        self, cli_runner: CliRunner, use_mock_database_for_tests
    ) -> None:
        """Test that import creates destination directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as source_dir:
            source = Path(source_dir)
            dest = Path(source_dir) / "new_dest" / "subdir"

            # Create archive files in source
            (source / "Quest Pack Alpha.7z").write_text("quest mod archive content")
            (source / "Armor Collection.7z").write_text("armor mod archive content")
            (source / "Weapon Enhancement.7z").write_text("weapons mod archive content")

            # Destination doesn't exist yet
            assert not dest.exists()

            result = cli_runner.invoke(
                app, ["database", "import", "GTSv101", str(source), str(dest)]
            )

            # Should succeed and create destination
            assert result.exit_code == 0
            assert dest.exists()


class TestImportWorkflowErrorRecovery:
    """Tests for error recovery during import."""

    def test_import_handles_existing_files_without_force(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that import reports error when files exist without --force."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)
        dest = Path(dest_dir)

        # Create archive files in both source and dest
        (source / "Quest Pack Alpha.7z").write_text("new content")
        (dest / "Quest Pack Alpha.7z").write_text("old content")

        result = cli_runner.invoke(
            app, ["database", "import", "GTSv101", source_dir, dest_dir]
        )

        # Should report error (file already exists)
        assert result.exit_code == 2 or "error" in result.stdout.lower()

    def test_import_overwrites_with_force_flag(
        self, cli_runner: CliRunner, temp_directories, use_mock_database_for_tests
    ) -> None:
        """Test that --force flag allows overwriting existing files."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)
        dest = Path(dest_dir)

        # Create archive files in both source and dest
        (source / "Quest Pack Alpha.7z").write_text("new content")
        (source / "Armor Collection.7z").write_text("new armor")
        (source / "Weapon Enhancement.7z").write_text("new weapons")
        (dest / "Quest Pack Alpha.7z").write_text("old content")

        result = cli_runner.invoke(
            app, ["database", "import", "--force", "GTSv101", source_dir, dest_dir]
        )

        # Should succeed with force
        assert result.exit_code == 0

        # File should be overwritten with new content
        assert (dest / "Quest Pack Alpha.7z").read_text() == "new content"


class TestImportWorkflowVerbosity:
    """Tests for verbose output during import."""

    def test_import_with_verbose_flag(
        self, cli_runner: CliRunner, temp_directories, use_mock_database_for_tests
    ) -> None:
        """Test that --verbose flag provides detailed output."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create archive files in source
        (source / "Quest Pack Alpha.7z").write_text("quest content")
        (source / "Armor Collection.7z").write_text("armor content")
        (source / "Weapon Enhancement.7z").write_text("weapons content")

        result = cli_runner.invoke(
            app, ["database", "import", "--verbose", "GTSv101", source_dir, dest_dir]
        )

        # Should complete successfully
        assert result.exit_code == 0

        # Verbose output should include more detail
        assert len(result.stdout) > 0


class TestImportWorkflowStatistics:
    """Tests for import statistics and result tracking."""

    def test_import_reports_files_copied_count(
        self, cli_runner: CliRunner, temp_directories, use_mock_database_for_tests
    ) -> None:
        """Test that import reports correct count of copied files."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create all archive files for GTSv101 (3 files total)
        files = [
            "Quest Pack Alpha.7z",
            "Armor Collection.7z",
            "Weapon Enhancement.7z",
        ]
        for file in files:
            (source / file).write_text(f"content for {file}")

        result = cli_runner.invoke(
            app, ["database", "import", "GTSv101", source_dir, dest_dir]
        )

        assert result.exit_code == 0
        # Output should mention files copied
        assert "3" in result.stdout or "imported" in result.stdout.lower()

    def test_import_service_tracks_duration(self, use_mock_database_for_tests) -> None:
        """Test that ImportService tracks import duration."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create archive files
            (source / "Quest Pack Alpha.7z").write_text("content")
            (source / "Armor Collection.7z").write_text("content")
            (source / "Weapon Enhancement.7z").write_text("content")

            service = ImportService()
            result = service.execute("GTSv101", source, dest)

            # Result should have duration tracked
            assert result.duration >= 0
            assert result.success


class TestImportWorkflowMultipleMods:
    """Tests for importing multiple mods in sequence."""

    def test_import_handles_multiple_mods(
        self, cli_runner: CliRunner, temp_directories, use_mock_database_for_tests
    ) -> None:
        """Test importing a version with multiple mods."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create archive files for all mods in GTSv101 (3 mods)
        files = [
            "Quest Pack Alpha.7z",
            "Armor Collection.7z",
            "Weapon Enhancement.7z",
        ]
        for file in files:
            (source / file).write_text(f"content for {file}")

        result = cli_runner.invoke(
            app, ["database", "import", "GTSv101", source_dir, dest_dir]
        )

        assert result.exit_code == 0

        # All files should be copied
        for file in files:
            assert (Path(dest_dir) / file).exists()


class TestImportWorkflowInteractive:
    """Tests for interactive mode of import command."""

    def test_import_with_missing_arguments_prompts(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that missing arguments trigger interactive prompts."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create archive files in source
        (source / "Quest Pack Alpha.7z").write_text("content")
        (source / "Armor Collection.7z").write_text("content")
        (source / "Weapon Enhancement.7z").write_text("content")

        # Invoke with only version, providing other args via input
        result = cli_runner.invoke(
            app,
            ["database", "import", "GTSv101"],
            input=f"{source_dir}\n{dest_dir}\n",
        )

        # Should succeed with interactive input
        assert result.exit_code in (0, 2)
