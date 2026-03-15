"""Performance tests for merge-folders feature.

These tests verify that the merge-folders implementation meets the
performance targets defined in the specification:
- Scan 1000+ folders in <10 seconds
- Merge 100+ files in <30 seconds
- Full workflow with 10 groups in <3 minutes
"""

import time
import tempfile
from pathlib import Path

import pytest

from src.cli.services.merge_service import MergeFoldersService


class TestScanPerformance:
    """Performance benchmarks for directory scanning."""

    def test_scan_1000_folders_under_10_seconds(self):
        """Verify scanning 1000+ folders completes in <10 seconds.

        This test creates a directory with 1000+ case-insensitive
        duplicate folders and measures scan time.

        Target: <10 seconds (per specification SC-001)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create 1000+ folders with various case-insensitive duplicates
            # Structure: base/
            #   ├── group0/mods, group0/Mods, group0/MODS, ... (3-5 variants each)
            #   ├── group1/configs, group1/Configs, ...
            #   └── groupN/...

            folders_created = 0
            for i in range(100):  # 100 groups
                group_dir = base / f"group_{i}"
                group_dir.mkdir()

                # Create 3-5 variants per group
                variants = ["lowercase", "Lowercase", "LOWERCASE"]
                if i % 2 == 0:
                    variants.append("lOwErCaSe")
                if i % 3 == 0:
                    variants.append("LoWeRcAsE")

                for variant in variants:
                    (group_dir / variant).mkdir()
                    folders_created += len(variants)

            # Measure scan time
            service = MergeFoldersService()
            start = time.time()
            groups = service.scan_duplicates(base)
            elapsed = time.time() - start

            # Verify results
            assert len(groups) > 0, "Should find duplicate groups"
            assert elapsed < 10.0, (
                f"Scan of {folders_created} folders took {elapsed:.2f}s, target is <10s"
            )

            # Report performance
            print(
                f"\n✓ Scan performance: {folders_created} folders in {elapsed:.2f}s "
                f"({folders_created / elapsed:.0f} folders/sec)"
            )

    def test_scan_deep_nesting_10_levels(self):
        """Verify scanning works with deeply nested directories (10+ levels).

        Target: <5 seconds (per specification SC-005)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create deeply nested structure: a/b/c/.../j/mods, a/b/c/.../j/Mods
            current = base
            depth_names = "abcdefghij"
            for i, letter in enumerate(depth_names):
                current = current / letter
                current.mkdir()

            # Add duplicates at the deepest level
            (current / "mods").mkdir()
            (current / "Mods").mkdir()
            (current / "MODS").mkdir()

            # Measure scan time
            service = MergeFoldersService()
            start = time.time()
            groups = service.scan_duplicates(base)
            elapsed = time.time() - start

            # Verify results
            assert len(groups) == 1, "Should find one duplicate group"
            assert elapsed < 5.0, (
                f"Deep nesting scan took {elapsed:.2f}s, target is <5s"
            )

            print(f"\n✓ Deep nesting (10 levels) scan: {elapsed:.2f}s")


class TestMergePerformance:
    """Performance benchmarks for merge operations."""

    def test_merge_100_files_under_30_seconds(self):
        """Verify merging 100+ files completes in <30 seconds.

        This test creates a duplicate group with 100+ files and measures
        merge time.

        Target: <30 seconds (per specification SC-002)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create source folder with 100+ files
            source = base / "Mods"
            source.mkdir()
            for i in range(100):
                (source / f"file_{i}.txt").write_text(f"Content {i}")

            # Add subdirectories with files
            for i in range(10):
                subdir = source / f"subdir_{i}"
                subdir.mkdir()
                for j in range(5):
                    (subdir / f"nested_{j}.txt").write_text(f"Nested {i}_{j}")

            # Create target folder (empty)
            target = base / "mods"
            target.mkdir()

            # Measure merge time
            service = MergeFoldersService()
            start = time.time()
            operation = service.preview_merge(source, target)
            service.execute_merge(operation)
            elapsed = time.time() - start

            # Verify results
            assert not source.exists(), "Source should be deleted after merge"
            assert (target / "file_0.txt").exists(), "Files should be in target"
            assert (target / "subdir_0").exists(), "Subdirs should be in target"
            assert elapsed < 30.0, (
                f"Merge of {operation.file_count} files took {elapsed:.2f}s, "
                f"target is <30s"
            )

            # Report performance
            print(
                f"\n✓ Merge performance: {operation.file_count} files in {elapsed:.2f}s "
                f"({operation.file_count / elapsed:.0f} files/sec)"
            )


class TestFullWorkflowPerformance:
    """Performance benchmarks for end-to-end workflows."""

    def test_full_workflow_10_groups_under_3_minutes(self):
        """Verify full workflow with 10 groups completes in <3 minutes.

        This test runs the complete scan→preview→merge workflow for
        10 duplicate groups.

        Target: <3 minutes (per specification SC-007)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create 10 duplicate groups
            for group_num in range(10):
                group_dir = base / f"group_{group_num}"
                group_dir.mkdir()

                # Create variants with files
                for variant_name in ["target", "Target", "TARGET"]:
                    variant_dir = group_dir / variant_name
                    variant_dir.mkdir()

                    # Add files (scale up to create work)
                    for i in range(20):
                        (variant_dir / f"file_{i}.txt").write_text(f"Content {i}")

            # Measure full workflow
            service = MergeFoldersService()
            start = time.time()

            # Scan all groups
            groups = service.scan_duplicates(base)
            assert len(groups) == 10, f"Expected 10 groups, got {len(groups)}"

            # Preview and merge all groups
            merged = 0
            for group in groups:
                # Auto-select lowercase target
                target_name = service.get_target_folder(group)
                group.target = target_name
                target_path = group.paths[target_name]

                # Merge each source into target
                for source_name in group.sources:
                    source_path = group.paths[source_name]
                    operation = service.preview_merge(source_path, target_path)
                    service.execute_merge(operation)
                    merged += 1

            elapsed = time.time() - start

            # Verify results
            assert merged > 0, "Should have merged at least one folder"
            assert elapsed < 180.0, (
                f"Full workflow took {elapsed:.2f}s, target is <180s (3 min)"
            )

            # Report performance
            print(
                f"\n✓ Full workflow: 10 groups with {merged} merges in {elapsed:.2f}s"
            )


# Mark tests as needing dedicated time
pytestmark = pytest.mark.performance
