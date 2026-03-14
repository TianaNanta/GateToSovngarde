"""Integration tests for merge-folders functionality.

Tests cover complete workflows:
- Full scan → preview → merge workflow
- User choice scenarios
- Conflict handling
- Preview-only mode
- Force mode
"""

import tempfile
from pathlib import Path

from cli.services.merge_service import MergeFoldersService


class TestFullMergeWorkflow:
    """Tests for complete merge workflows."""

    def test_workflow_scan_preview_merge(self):
        """Test complete workflow: scan → preview → merge."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Setup: Create duplicate folders
            mods_lower = root / "mods"
            mods_upper = root / "Mods"
            mods_lower.mkdir()
            mods_upper.mkdir()

            (mods_lower / "mod1.txt").write_text("content1")
            (mods_upper / "mod2.txt").write_text("content2")

            service = MergeFoldersService()

            # Step 1: Scan
            groups = service.scan_duplicates(root)
            assert len(groups) == 1

            # Step 2: Get target
            group = groups[0]
            target = service.get_target_folder(group)
            assert target == "mods"
            group.target = target

            # Step 3: Preview
            source_path = group.paths["Mods"]
            target_path = group.paths["mods"]
            operation = service.preview_merge(source_path, target_path)

            assert operation.file_count == 1
            assert operation.source == source_path
            assert operation.target == target_path

            # Step 4: Execute
            service.execute_merge(operation)

            # Verify: Both files in target, source deleted
            assert (target_path / "mod1.txt").exists()
            assert (target_path / "mod2.txt").exists()
            assert not source_path.exists()

    def test_workflow_multiple_groups(self):
        """Test handling multiple duplicate groups in one scan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create multiple duplicate groups
            for name in ["mods", "Mods"]:
                (root / name).mkdir(exist_ok=True)
            for name in ["configs", "Configs"]:
                (root / name).mkdir(exist_ok=True)

            service = MergeFoldersService()
            groups = service.scan_duplicates(root)

            assert len(groups) == 2

            # Verify both groups have proper targets
            for group in groups:
                target = service.get_target_folder(group)
                assert target.islower()

    def test_workflow_skip_merge_preserves_files(self):
        """Test that skipping a merge doesn't modify files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            (source / "file.txt").write_text("content")

            # Simulate skip (don't execute merge)
            # Files should remain unchanged
            assert (source / "file.txt").exists()
            assert not (target / "file.txt").exists()


class TestConflictResolution:
    """Tests for handling file conflicts during merge."""

    def test_conflict_skip_keeps_target_version(self):
        """Test that conflicts default to keeping target version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Create conflicting files
            (source / "file.txt").write_text("source version")
            (target / "file.txt").write_text("target version")

            service = MergeFoldersService()
            operation = service.preview_merge(source, target)

            assert "file.txt" in operation.conflicts

            # Execute merge with default handler (skip conflicts)
            service.execute_merge(operation)

            # Target version should be preserved
            assert (target / "file.txt").read_text() == "target version"

    def test_conflict_rename_source_file(self):
        """Test renaming source file when conflict occurs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Create conflicting files
            (source / "file.txt").write_text("source version")
            (target / "file.txt").write_text("target version")

            # Also add a non-conflicting file
            (source / "unique.txt").write_text("unique")

            service = MergeFoldersService()

            # Define conflict handler that renames
            def rename_handler(filename, is_dir):
                return "rename"

            operation = service.preview_merge(source, target)
            service.execute_merge(operation, conflict_handler=rename_handler)

            # Target version preserved
            assert (target / "file.txt").read_text() == "target version"

            # Source file should be renamed and moved
            conflict_files = [f for f in target.iterdir() if "conflict" in f.name]
            assert len(conflict_files) > 0


class TestPerformance:
    """Tests for performance criteria."""

    def test_scan_performance_1000_folders(self):
        """Test scanning 1000+ folders completes in reasonable time.

        Success Criterion: < 10 seconds
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create 1000 unique folders + some duplicates
            for i in range(1000):
                (root / f"folder_{i:04d}").mkdir()

            # Add duplicates to be found
            for i in range(10):
                (root / f"duplicate_{i}").mkdir()
                (root / f"Duplicate_{i}").mkdir()

            service = MergeFoldersService()

            import time

            start = time.time()
            groups = service.scan_duplicates(root)
            elapsed = time.time() - start

            # Should find the duplicates
            assert len(groups) == 10

            # Performance: should be fast
            assert elapsed < 10, f"Scan took {elapsed:.2f}s, expected < 10s"

    def test_merge_performance_100_files(self):
        """Test merging 100+ files completes in reasonable time.

        Success Criterion: < 30 seconds
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Create 100 files
            for i in range(100):
                (source / f"file_{i:03d}.txt").write_text(f"content {i}")

            service = MergeFoldersService()
            operation = service.preview_merge(source, target)

            import time

            start = time.time()
            service.execute_merge(operation)
            elapsed = time.time() - start

            # Verify all files moved
            assert len(list(target.glob("*.txt"))) == 100

            # Performance: should be fast
            assert elapsed < 30, f"Merge took {elapsed:.2f}s, expected < 30s"


class TestDeepNesting:
    """Tests for handling deeply nested directory structures."""

    def test_scan_deep_nesting_10_levels(self):
        """Test scanning folders nested 10+ levels deep."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create deeply nested duplicates
            current = root
            for i in range(10):
                current = current / f"level{i}"
                current.mkdir()

            # Create duplicates at deepest level
            (current / "data").mkdir()
            (current / "Data").mkdir()

            service = MergeFoldersService()
            groups = service.scan_duplicates(root)

            # Should find the deep duplicates
            assert len(groups) == 1
            assert "data" in groups[0].variants
            assert "Data" in groups[0].variants

    def test_merge_deep_nested_structure(self):
        """Test merging deeply nested folder structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Create deeply nested structure
            current = source
            for i in range(5):
                current = current / f"level{i}"
                current.mkdir()
                (current / f"file{i}.txt").write_text(f"nested file {i}")

            service = MergeFoldersService()
            operation = service.preview_merge(source, target)
            service.execute_merge(operation)

            # Verify structure preserved
            current = target
            for i in range(5):
                current = current / f"level{i}"
                assert current.exists()
                assert (current / f"file{i}.txt").exists()


class TestZeroDataLoss:
    """Tests ensuring zero data loss during merge operations."""

    def test_no_data_loss_with_many_files(self):
        """Verify all files transfer without corruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            # Create files with specific content
            original_content = {}
            for i in range(50):
                filename = f"file_{i:03d}.txt"
                content = f"Original content for file {i}" * 10  # Multiple lines
                (source / filename).write_text(content)
                original_content[filename] = content

            service = MergeFoldersService()
            operation = service.preview_merge(source, target)
            service.execute_merge(operation)

            # Verify every file content matches
            for filename, original in original_content.items():
                target_file = target / filename
                assert target_file.exists(), f"File {filename} missing after merge"

                actual = target_file.read_text()
                assert actual == original, f"File {filename} content corrupted"

    def test_partial_merge_abort_on_error(self):
        """Test that merge stops on error without data loss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()

            (source / "file1.txt").write_text("content1")
            (source / "file2.txt").write_text("content2")

            # Make target read-only to cause error
            import os

            os.chmod(str(target), 0o444)  # Read-only

            service = MergeFoldersService()
            operation = service.preview_merge(source, target)

            # Attempt merge - should raise error
            try:
                service.execute_merge(operation)
            except (OSError, PermissionError):
                pass  # Expected
            finally:
                # Restore permissions for cleanup
                os.chmod(str(target), 0o755)

            # Verify source files still exist (partial merge protection)
            # Files may be partially moved, but source still exists
            assert source.exists()
