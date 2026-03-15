"""Unit tests for MergeFoldersService.

Tests cover:
- Duplicate detection (case-insensitive grouping)
- Target folder selection (lowercase priority)
- File counting and size estimation
- Conflict detection
- Merge operations (atomic moves)
- Edge cases (missing folders, permissions, special characters)
"""

import tempfile
from pathlib import Path
from typing import Generator, Tuple

import pytest

from cli.services.merge_service import (
    MergeFoldersService,
    DuplicateGroup,
)


@pytest.fixture
def temp_merge_structure() -> Generator[Tuple[Path, dict], None, None]:
    """Create a temporary directory structure with duplicate folders.

    Returns:
        Generator yielding (root_path, groups_info)
        groups_info contains:
        - root: Root test directory
        - Mods_lower: /root/mods (lowercase)
        - Mods_upper: /root/Mods (uppercase)
        - Phone_mixed: /root/phone (lowercase)
        - Phone_upper: /root/PhOne (mixed)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create Mods and mods (case-insensitive duplicates)
        mods_lower = root / "mods"
        mods_upper = root / "Mods"
        mods_lower.mkdir()
        mods_upper.mkdir()

        # Add files to each
        (mods_lower / "mod1.txt").write_text("content1")
        (mods_lower / "mod2.txt").write_text("content2")
        (mods_upper / "mod3.txt").write_text("content3")

        # Create PhOne and phone (case-insensitive duplicates)
        phone_lower = root / "phone"
        phone_upper = root / "PhOne"
        phone_lower.mkdir()
        phone_upper.mkdir()

        (phone_lower / "file1.txt").write_text("data1")
        (phone_upper / "file2.txt").write_text("data2")

        # Create subdirectories in PhOne
        subdir = phone_upper / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested")

        groups_info = {
            "root": root,
            "mods_lower": mods_lower,
            "mods_upper": mods_upper,
            "phone_lower": phone_lower,
            "phone_upper": phone_upper,
        }

        yield root, groups_info


@pytest.fixture
def merge_service() -> MergeFoldersService:
    """Provide a MergeFoldersService instance."""
    return MergeFoldersService()


class TestScanDuplicates:
    """Tests for duplicate folder scanning."""

    def test_scan_duplicates_finds_basic_duplicates(
        self, temp_merge_structure, merge_service
    ):
        """Test that basic case-insensitive duplicates are detected."""
        root, _ = temp_merge_structure

        groups = merge_service.scan_duplicates(root)

        # Should find 2 groups: Mods/mods and PhOne/phone
        assert len(groups) == 2

        # Extract group names
        group_names = [set(g.variants) for g in groups]

        assert {"Mods", "mods"} in group_names
        assert {"PhOne", "phone"} in group_names

    def test_scan_duplicates_no_duplicates(self, merge_service):
        """Test scanning a directory with no duplicates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create non-duplicate folders
            (root / "folder1").mkdir()
            (root / "folder2").mkdir()
            (root / "folder3").mkdir()

            groups = merge_service.scan_duplicates(root)
            assert len(groups) == 0

    def test_scan_duplicates_nonexistent_path(self, merge_service):
        """Test scanning a path that doesn't exist."""
        with pytest.raises(ValueError):
            merge_service.scan_duplicates(Path("/nonexistent/path"))

    def test_scan_duplicates_not_a_directory(self, merge_service):
        """Test scanning a path that is not a directory."""
        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises(ValueError):
                merge_service.scan_duplicates(Path(f.name))

    def test_scan_duplicates_nested_structure(self, merge_service):
        """Test scanning with nested duplicate folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create nested structure
            level1 = root / "data"
            level1.mkdir()

            level2_dup1 = level1 / "configs"
            level2_dup2 = level1 / "Configs"
            level2_dup1.mkdir()
            level2_dup2.mkdir()

            groups = merge_service.scan_duplicates(root)

            # Should find the nested duplicates
            assert len(groups) == 1
            assert "configs" in groups[0].variants
            assert "Configs" in groups[0].variants

    def test_scan_duplicates_three_variants(self, merge_service):
        """Test scanning with 3+ case variants of same folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "mods").mkdir()
            (root / "Mods").mkdir()
            (root / "MODS").mkdir()

            groups = merge_service.scan_duplicates(root)

            assert len(groups) == 1
            assert set(groups[0].variants) == {"mods", "Mods", "MODS"}


class TestGetTargetFolder:
    """Tests for target folder selection."""

    def test_get_target_folder_prefers_lowercase(self, merge_service):
        """Test that lowercase variant is selected as target."""
        group = DuplicateGroup(parent_path=Path("/test"))
        group.add_variant("Mods", Path("/test/Mods"))
        group.add_variant("mods", Path("/test/mods"))
        group.add_variant("MODS", Path("/test/MODS"))

        target = merge_service.get_target_folder(group)

        assert target == "mods"

    def test_get_target_folder_only_lowercase(self, merge_service):
        """Test target selection with only one lowercase variant."""
        group = DuplicateGroup(parent_path=Path("/test"))
        group.add_variant("Mods", Path("/test/Mods"))
        group.add_variant("mods", Path("/test/mods"))

        target = merge_service.get_target_folder(group)
        assert target == "mods"

    def test_get_target_folder_no_lowercase(self, merge_service):
        """Test target selection with no lowercase variant (deterministic fallback)."""
        group = DuplicateGroup(parent_path=Path("/test"))
        group.add_variant("Mods", Path("/test/Mods"))
        group.add_variant("ModS", Path("/test/ModS"))
        group.add_variant("MODs", Path("/test/MODs"))

        target = merge_service.get_target_folder(group)

        # Should return first alphabetically
        assert target == "MODs"


class TestConflictDetection:
    """Tests for detecting file conflicts between folders."""

    def test_get_conflicts_no_conflicts(self, merge_service):
        """Test conflict detection when no conflicts exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            (source / "file1.txt").write_text("content")
            (target / "file2.txt").write_text("content")

            conflicts = merge_service.get_conflicts(source, target)
            assert conflicts == []

    def test_get_conflicts_with_conflicts(self, merge_service):
        """Test conflict detection when files have same names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Same-named files
            (source / "file.txt").write_text("source content")
            (target / "file.txt").write_text("target content")

            # Different files
            (source / "unique.txt").write_text("source")
            (target / "other.txt").write_text("target")

            conflicts = merge_service.get_conflicts(source, target)
            assert conflicts == ["file.txt"]

    def test_get_conflicts_nonexistent_target(self, merge_service):
        """Test conflict detection when target doesn't exist yet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            # target doesn't exist

            (source / "file.txt").write_text("content")

            conflicts = merge_service.get_conflicts(source, target)
            assert conflicts == []


class TestCountItems:
    """Tests for counting files and estimating size."""

    def test_count_items_empty_folder(self, merge_service):
        """Test counting items in empty folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            file_count, dir_count, size = merge_service.count_items(root)

            assert file_count == 0
            assert dir_count == 0
            assert size == 0

    def test_count_items_with_files_and_dirs(self, merge_service):
        """Test counting files, directories, and size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files
            (root / "file1.txt").write_text("content1")
            (root / "file2.txt").write_text("content2 extra")

            # Create subdirectories with files
            subdir = root / "subdir"
            subdir.mkdir()
            (subdir / "file3.txt").write_text("file3")

            file_count, dir_count, size = merge_service.count_items(root)

            assert file_count == 3
            assert dir_count == 1
            assert size > 0  # Has content

    def test_count_items_nested_structure(self, merge_service):
        """Test counting with deeply nested structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create nested structure
            current = root
            for i in range(5):
                current = current / f"level{i}"
                current.mkdir()
                (current / f"file{i}.txt").write_text("content")

            file_count, dir_count, size = merge_service.count_items(root)

            assert file_count == 5
            assert dir_count == 5
            assert size > 0


class TestPreviewMerge:
    """Tests for generating merge previews."""

    def test_preview_merge_basic(self, merge_service):
        """Test generating a merge preview."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            (source / "file1.txt").write_text("content")
            (source / "file2.txt").write_text("more content")

            operation = merge_service.preview_merge(source, target)

            assert operation.source == source
            assert operation.target == target
            assert operation.file_count == 2
            assert operation.dir_count == 0
            assert operation.estimated_size > 0

    def test_preview_merge_nonexistent_source(self, merge_service):
        """Test preview with nonexistent source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "nonexistent"
            target = root / "target"
            target.mkdir()

            with pytest.raises(ValueError):
                merge_service.preview_merge(source, target)


class TestExecuteMerge:
    """Tests for executing merge operations."""

    def test_execute_merge_simple(self, merge_service):
        """Test executing a simple merge."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Add files to source
            (source / "file1.txt").write_text("content1")
            (source / "file2.txt").write_text("content2")

            # Execute merge
            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation)

            # Verify: files moved to target
            assert (target / "file1.txt").exists()
            assert (target / "file2.txt").exists()
            assert (target / "file1.txt").read_text() == "content1"

            # Verify: source directory deleted
            assert not source.exists()

    def test_execute_merge_with_subdirs(self, merge_service):
        """Test merging folder with subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Create source structure
            subdir = source / "subdir"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("nested content")
            (source / "file.txt").write_text("top level")

            # Execute merge
            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation)

            # Verify structure preserved
            assert (target / "file.txt").exists()
            assert (target / "subdir" / "nested.txt").exists()
            assert (target / "subdir" / "nested.txt").read_text() == "nested content"

    def test_execute_merge_creates_target_if_missing(self, merge_service):
        """Test that merge creates target directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            # target doesn't exist

            (source / "file.txt").write_text("content")

            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation)

            assert (target / "file.txt").exists()
            assert not source.exists()


class TestFormatSize:
    """Tests for human-readable size formatting."""

    def test_format_size_bytes(self, merge_service):
        """Test formatting small sizes in bytes."""
        assert merge_service.format_size(512) == "512.0 B"
        assert merge_service.format_size(1023) == "1023.0 B"

    def test_format_size_kilobytes(self, merge_service):
        """Test formatting sizes in kilobytes."""
        assert merge_service.format_size(1024) == "1.0 KB"
        assert merge_service.format_size(2048) == "2.0 KB"

    def test_format_size_megabytes(self, merge_service):
        """Test formatting sizes in megabytes."""
        assert merge_service.format_size(1024 * 1024) == "1.0 MB"

    def test_format_size_gigabytes(self, merge_service):
        """Test formatting sizes in gigabytes."""
        result = merge_service.format_size(1024 * 1024 * 1024)
        assert "GB" in result


# =============================================================================
# USER STORY 2: AUTOMATIC MERGE WITH LOWERCASE PREFERENCE (P1)
# =============================================================================


class TestAutomaticTargetSelection:
    """Tests for automatic target selection with lowercase preference (US2)."""

    def test_automatic_target_prefers_lowercase(self, merge_service):
        """Test that get_target_folder selects lowercase when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            group = DuplicateGroup(parent_path=root, variants=["Mods", "mods", "MODS"])
            group.paths = {
                "Mods": root / "Mods",
                "mods": root / "mods",
                "MODS": root / "MODS",
            }
            target = merge_service.get_target_folder(group)
            assert target == "mods"

    def test_automatic_target_only_lowercase_exists(self, merge_service):
        """Test selection when only one lowercase variant exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            group = DuplicateGroup(
                parent_path=root, variants=["Config", "config", "CONFIG"]
            )
            group.paths = {
                "Config": root / "Config",
                "config": root / "config",
                "CONFIG": root / "CONFIG",
            }
            target = merge_service.get_target_folder(group)
            assert target == "config"

    def test_automatic_target_no_lowercase(self, merge_service):
        """Test selection when no all-lowercase variant exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            group = DuplicateGroup(parent_path=root, variants=["Mods", "moDs"])
            group.paths = {"Mods": root / "Mods", "moDs": root / "moDs"}
            target = merge_service.get_target_folder(group)
            assert target in ["Mods", "moDs"]


class TestMergeExecution:
    """Tests for merge execution with atomic operations (US2)."""

    def test_merge_moves_all_files_to_target(self, merge_service):
        """Test that all files from source are moved to target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            for i in range(5):
                (source / f"file{i}.txt").write_text(f"Content {i}")

            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation)

            for i in range(5):
                assert (target / f"file{i}.txt").exists()
            assert not source.exists()

    def test_merge_preserves_subdirectories(self, merge_service):
        """Test that subdirectories and their contents are moved correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()

            subdir = source / "subdir"
            subdir.mkdir()
            (subdir / "file.txt").write_text("Content")

            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation)

            assert (target / "subdir" / "file.txt").exists()
            assert not source.exists()


class TestMergeWithConflicts:
    """Tests for conflict handling during merge (US2 + US5)."""

    def test_merge_detects_conflicting_files(self, merge_service):
        """Test that same-named files are detected as conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            (source / "file.txt").write_text("Source")
            (target / "file.txt").write_text("Target")

            operation = merge_service.preview_merge(source, target)
            assert "file.txt" in operation.conflicts


# =============================================================================
# USER STORY 3: USER CHOOSES FOLDER TO KEEP (PRIORITY P2)
# =============================================================================


class TestUserChoiceTargetSelection:
    """Tests for user choice when no all-lowercase variant exists (US3)."""

    def test_get_target_folder_returns_first_when_no_lowercase(self, merge_service):
        """Test that get_target_folder returns first variant when no lowercase exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            group = DuplicateGroup(parent_path=root, variants=["Mods", "moDs", "MoDs"])
            group.paths = {
                "Mods": root / "Mods",
                "moDs": root / "moDs",
                "MoDs": root / "MoDs",
            }
            target = merge_service.get_target_folder(group)
            assert target in ["MoDs", "Mods", "moDs"]


class TestUserCancelOperation:
    """Tests for user cancellation (Ctrl+C) behavior."""

    def test_merge_does_not_modify_on_cancellation(self, merge_service):
        """Test that no files are modified if merge is cancelled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            (source / "file1.txt").write_text("Source")
            (target / "file2.txt").write_text("Target")
            assert (source / "file1.txt").exists()
            assert (target / "file2.txt").exists()


# =============================================================================
# USER STORY 4: PREVIEW MERGE IMPACT (PRIORITY P2)
# =============================================================================


class TestPreviewMergeImpact:
    """Tests for preview functionality (US4)."""

    def test_preview_calculates_file_count(self, merge_service):
        """Test that preview correctly calculates number of files to move."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            for i in range(10):
                (source / f"file{i}.txt").write_text(f"Content {i}")
            operation = merge_service.preview_merge(source, target)
            assert operation.file_count == 10

    def test_preview_calculates_size(self, merge_service):
        """Test that preview calculates estimated size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            content = "x" * 1000
            for i in range(5):
                (source / f"file{i}.txt").write_text(content)
            operation = merge_service.preview_merge(source, target)
            assert operation.estimated_size >= 5000

    def test_preview_does_not_modify_files(self, merge_service):
        """Test that preview does not modify any files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            (source / "file.txt").write_text("Original")
            merge_service.preview_merge(source, target)
            assert (source / "file.txt").exists()
            assert not (target / "file.txt").exists()

    def test_preview_detects_conflicts(self, merge_service):
        """Test that preview correctly identifies file conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()
            (source / "conflict.txt").write_text("Source")
            (target / "conflict.txt").write_text("Target")
            (source / "unique.txt").write_text("Unique")
            operation = merge_service.preview_merge(source, target)
            assert "conflict.txt" in operation.conflicts


# =============================================================================
# USER STORY 5: CONFLICT HANDLING (PRIORITY P3)
# =============================================================================


class TestConflictResolution:
    """Tests for conflict resolution options (US5)."""

    def test_conflict_detection_identifies_same_named_files(self, merge_service):
        """Test that conflict detection identifies files with same name in both folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()

            (source / "readme.txt").write_text("Source version")
            (target / "readme.txt").write_text("Target version")
            (source / "unique.txt").write_text("Only in source")

            conflicts = merge_service.get_conflicts(source, target)

            assert "readme.txt" in conflicts
            assert "unique.txt" not in conflicts

    def test_conflict_resolution_skip_handler(self, merge_service):
        """Test skip conflict resolution: keep target version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()

            (source / "conflict.txt").write_text("Source")
            (target / "conflict.txt").write_text("Target")
            (source / "unique.txt").write_text("Unique")

            def skip_handler(filename, is_dir):
                return "skip"

            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation, conflict_handler=skip_handler)

            assert (target / "conflict.txt").read_text() == "Target"
            assert (target / "unique.txt").exists()

    def test_conflict_resolution_rename_handler(self, merge_service):
        """Test rename conflict resolution: rename source file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "Mods"
            target = root / "mods"
            source.mkdir()
            target.mkdir()

            (source / "file.txt").write_text("Source version")
            (target / "file.txt").write_text("Target version")

            def rename_handler(filename, is_dir):
                return "rename"

            operation = merge_service.preview_merge(source, target)
            merge_service.execute_merge(operation, conflict_handler=rename_handler)

            assert (target / "file.txt").read_text() == "Target version"
            renamed_files = list(target.glob("file*.txt"))
            assert len(renamed_files) >= 2
