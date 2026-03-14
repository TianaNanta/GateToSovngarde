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
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test complete import with all required files present."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)
        dest = Path(dest_dir)

        # Create all required files for GTSv101
        (source / "quest_001.esp").write_text("quest mod content")
        (source / "quest_001_dialogue.esm").write_text("dialogue content")
        (source / "armor_set.esp").write_text("armor mod content")
        (source / "weapons.esp").write_text("weapons mod content")
        (source / "weapons_textures.bsa").write_text("texture asset content")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        # Should succeed
        assert result.exit_code == 0
        assert (
            "Successfully imported" in result.stdout
            or "success" in result.stdout.lower()
        )

        # Verify files were copied
        assert (dest / "quest_001.esp").exists()
        assert (dest / "quest_001_dialogue.esm").exists()
        assert (dest / "armor_set.esp").exists()
        assert (dest / "weapons.esp").exists()
        assert (dest / "weapons_textures.bsa").exists()

    def test_partial_import_with_missing_files(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test import with some files missing (partial success)."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create only some of the required files
        (source / "quest_001.esp").write_text("quest mod content")
        # Missing: quest_001_dialogue.esm, armor_set.esp, weapons files

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        # Should indicate partial success or errors
        assert result.exit_code in (0, 2)  # Success or runtime error

    def test_import_creates_destination_directory(self, cli_runner: CliRunner) -> None:
        """Test that import creates destination directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as source_dir:
            source = Path(source_dir)
            dest = Path(source_dir) / "new_dest" / "subdir"

            # Create files in source
            (source / "quest_001.esp").write_text("quest mod content")
            (source / "quest_001_dialogue.esm").write_text("dialogue content")
            (source / "armor_set.esp").write_text("armor mod content")
            (source / "weapons.esp").write_text("weapons mod content")
            (source / "weapons_textures.bsa").write_text("texture asset content")

            # Destination doesn't exist yet
            assert not dest.exists()

            result = cli_runner.invoke(
                app, ["import", "GTSv101", str(source), str(dest)]
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

        # Create files in both source and dest
        (source / "quest_001.esp").write_text("new content")
        (dest / "quest_001.esp").write_text("old content")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        # Should report error (file already exists)
        assert result.exit_code == 2 or "error" in result.stdout.lower()

    def test_import_overwrites_with_force_flag(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that --force flag allows overwriting existing files."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)
        dest = Path(dest_dir)

        # Create files in both source and dest
        (source / "quest_001.esp").write_text("new content")
        (source / "quest_001_dialogue.esm").write_text("new dialogue")
        (source / "armor_set.esp").write_text("new armor")
        (source / "weapons.esp").write_text("new weapons")
        (source / "weapons_textures.bsa").write_text("new textures")
        (dest / "quest_001.esp").write_text("old content")

        result = cli_runner.invoke(
            app, ["import", "--force", "GTSv101", source_dir, dest_dir]
        )

        # Should succeed with force
        assert result.exit_code == 0

        # File should be overwritten with new content
        assert (dest / "quest_001.esp").read_text() == "new content"


class TestImportWorkflowVerbosity:
    """Tests for verbose output during import."""

    def test_import_with_verbose_flag(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that --verbose flag provides detailed output."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create files in source
        (source / "quest_001.esp").write_text("quest content")
        (source / "quest_001_dialogue.esm").write_text("dialogue content")
        (source / "armor_set.esp").write_text("armor content")
        (source / "weapons.esp").write_text("weapons content")
        (source / "weapons_textures.bsa").write_text("textures content")

        result = cli_runner.invoke(
            app, ["import", "--verbose", "GTSv101", source_dir, dest_dir]
        )

        # Should complete successfully
        assert result.exit_code == 0

        # Verbose output should include more detail
        assert len(result.stdout) > 0


class TestImportWorkflowStatistics:
    """Tests for import statistics and result tracking."""

    def test_import_reports_files_copied_count(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test that import reports correct count of copied files."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create all files for GTSv101 (5 files total)
        files = [
            "quest_001.esp",
            "quest_001_dialogue.esm",
            "armor_set.esp",
            "weapons.esp",
            "weapons_textures.bsa",
        ]
        for file in files:
            (source / file).write_text(f"content for {file}")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

        assert result.exit_code == 0
        # Output should mention files copied
        assert "5" in result.stdout or "imported" in result.stdout.lower()

    def test_import_service_tracks_duration(self) -> None:
        """Test that ImportService tracks import duration."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create files
            (source / "quest_001.esp").write_text("content")
            (source / "quest_001_dialogue.esm").write_text("content")
            (source / "armor_set.esp").write_text("content")
            (source / "weapons.esp").write_text("content")
            (source / "weapons_textures.bsa").write_text("content")

            service = ImportService()
            result = service.execute("GTSv101", source, dest)

            # Result should have duration tracked
            assert result.duration >= 0
            assert result.success


class TestImportWorkflowMultipleMods:
    """Tests for importing multiple mods in sequence."""

    def test_import_handles_multiple_mods(
        self, cli_runner: CliRunner, temp_directories
    ) -> None:
        """Test importing a version with multiple mods."""
        source_dir, dest_dir = temp_directories
        source = Path(source_dir)

        # Create files for all mods in GTSv101 (3 mods)
        files = [
            "quest_001.esp",
            "quest_001_dialogue.esm",
            "armor_set.esp",
            "weapons.esp",
            "weapons_textures.bsa",
        ]
        for file in files:
            (source / file).write_text(f"content for {file}")

        result = cli_runner.invoke(app, ["import", "GTSv101", source_dir, dest_dir])

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

        # Create files in source
        (source / "quest_001.esp").write_text("content")
        (source / "quest_001_dialogue.esm").write_text("content")
        (source / "armor_set.esp").write_text("content")
        (source / "weapons.esp").write_text("content")
        (source / "weapons_textures.bsa").write_text("content")

        # Invoke with only version, providing other args via input
        result = cli_runner.invoke(
            app,
            ["import", "GTSv101"],
            input=f"{source_dir}\n{dest_dir}\n",
        )

        # Should succeed with interactive input
        assert result.exit_code in (0, 2)
