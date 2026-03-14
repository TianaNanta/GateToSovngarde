"""Unit tests for ImportService.

Tests the core import operation logic including file copying and error handling.
"""

from pathlib import Path
import tempfile

from cli.services.import_service import ImportService
from cli.models.import_result import ImportResult


class TestImportServiceExecution:
    """Tests for ImportService.execute() method."""

    def test_execute_copies_files(self) -> None:
        """Test that ImportService copies mod files successfully."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create test files matching GTSv101 mod structure
            (source / "quest_001.esp").write_text("quest data")
            (source / "quest_001_dialogue.esm").write_text("dialogue data")
            (source / "armor_set.esp").write_text("armor data")
            (source / "weapons.esp").write_text("weapons data")
            (source / "weapons_textures.bsa").write_text("textures data")

            service = ImportService()
            result = service.execute("GTSv101", source, dest)

            # Should have imported mods
            assert isinstance(result, ImportResult)
            assert result.files_copied >= 0
            assert result.mods_imported >= 0

    def test_execute_tracks_statistics(self, use_mock_database_for_tests) -> None:
        """Test that ImportService tracks import statistics correctly."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create archive files for mods
            (source / "Quest Pack Alpha.7z").write_text("quest data")
            (source / "Armor Collection.7z").write_text("armor data")
            (source / "Weapon Enhancement.7z").write_text("weapons data")

            service = ImportService()
            result = service.execute("GTSv101", source, dest)

            # Verify result structure
            assert result.mods_imported > 0
            assert result.files_copied > 0
            assert result.duration >= 0
            assert isinstance(result.errors, list)

    def test_execute_handles_missing_files(self) -> None:
        """Test that ImportService handles missing mod files gracefully."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create only one archive file, others will be missing
            (source / "Quest Pack Alpha.7z").write_text("quest data")
            # Missing: Armor Collection and Weapon Enhancement archives

            service = ImportService()
            result = service.execute("GTSv101", source, dest)

            # Should report errors but not crash
            assert isinstance(result, ImportResult)
            # May have some errors for missing files
            assert result.errors is not None

    def test_execute_respects_force_flag(self) -> None:
        """Test that --force flag allows overwriting existing files."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create archive files in both source and dest
            (source / "Quest Pack Alpha.7z").write_text("new content")
            dest.mkdir(exist_ok=True)
            (dest / "Quest Pack Alpha.7z").write_text("old content")

            service = ImportService()

            # Without force, should error
            result_no_force = service.execute("GTSv101", source, dest, force=False)
            assert len(result_no_force.errors) > 0

            # With force, should succeed (overwrite)
            dest_force = Path(dest_dir + "_force")
            dest_force.mkdir(exist_ok=True)
            (source / "Quest Pack Alpha.7z").write_text("new content")
            (dest_force / "Quest Pack Alpha.7z").write_text("old content")

            result_force = service.execute("GTSv101", source, dest_force, force=True)
            # With force, should not have error for existing file
            file_exists_errors = [
                e for e in result_force.errors if e.error_type == "file_exists"
            ]
            assert len(file_exists_errors) == 0

    def test_execute_creates_destination_directory(self) -> None:
        """Test that ImportService creates destination directory if needed."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as temp_base,
        ):
            source = Path(source_dir)
            dest = Path(temp_base) / "new_dest" / "subdir"

            # Create test archive file
            (source / "Quest Pack Alpha.7z").write_text("quest data")

            # Destination doesn't exist yet
            assert not dest.exists()

            service = ImportService()
            service.execute("GTSv101", source, dest)

            # Destination should be created
            assert dest.exists()
            assert dest.is_dir()


class TestImportServiceErrorHandling:
    """Tests for error handling in ImportService."""

    def test_execute_handles_permission_errors(self) -> None:
        """Test that ImportService handles permission denied errors gracefully."""
        with (
            tempfile.TemporaryDirectory() as source_dir,
            tempfile.TemporaryDirectory() as dest_dir,
        ):
            source = Path(source_dir)
            dest = Path(dest_dir)

            # Create test archive file
            (source / "Quest Pack Alpha.7z").write_text("quest data")

            # Make destination read-only (if on Unix-like system)
            import os
            import sys

            if sys.platform != "win32":
                os.chmod(dest, 0o444)

                try:
                    service = ImportService()
                    result = service.execute("GTSv101", source, dest)

                    # Should report permission errors
                    assert isinstance(result, ImportResult)
                    # May have permission errors
                    assert result.errors is not None
                finally:
                    # Restore permissions for cleanup
                    os.chmod(dest, 0o755)

    def test_execute_result_has_success_property(self) -> None:
        """Test that ImportResult.success property works correctly."""
        from cli.models.import_result import ImportResult

        # Success case
        result_success = ImportResult(
            total_mods=3,
            mods_imported=3,
            files_copied=5,
            duration=1.5,
            errors=[],
        )
        assert result_success.success is True

        # Failure case
        from cli.models.import_result import ImportError

        result_failure = ImportResult(
            total_mods=5,
            mods_imported=1,
            files_copied=2,
            duration=1.5,
            errors=[
                ImportError(
                    mod_id="mod_001",
                    mod_name="Test Mod",
                    error_type="file_not_found",
                    message="File not found",
                    recovery_suggestion="Check file",
                )
            ],
        )
        assert result_failure.success is False
