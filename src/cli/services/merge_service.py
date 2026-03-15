"""Service for discovering and merging case-insensitive duplicate folders.

This module provides functionality to:
1. Recursively scan directories for case-insensitive duplicate folders
2. Group duplicates by equivalence class
3. Determine merge targets and preview merge operations
4. Execute atomic merge operations with conflict detection
5. Handle user confirmations and conflict resolution

The service is designed to be safe by default, always previewing changes
before execution and providing clear feedback on conflicts.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
import os
import shutil
import logging

logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    """Represents a group of case-insensitive duplicate folders.

    Attributes:
        parent_path: Parent directory containing all duplicate variants
        variants: List of duplicate folder names as they appear on disk
        target: The selected target folder name to merge into
        paths: Mapping of folder names to their full Path objects
    """

    parent_path: Path
    variants: List[str] = field(default_factory=list)
    target: Optional[str] = None
    paths: Dict[str, Path] = field(default_factory=dict)

    @property
    def sources(self) -> List[str]:
        """Get list of source folders (all variants except target)."""
        return [v for v in self.variants if v != self.target]

    def add_variant(self, name: str, path: Path) -> None:
        """Add a variant to this group."""
        if name not in self.variants:
            self.variants.append(name)
        self.paths[name] = path


@dataclass
class MergeOperation:
    """Represents a single merge operation between folders.

    Attributes:
        source: Path to folder being merged (will be deleted after merge)
        target: Path to folder receiving the contents
        file_count: Number of files to be moved
        dir_count: Number of directories to be moved
        estimated_size: Estimated total size in bytes
        conflicts: List of filenames that exist in both source and target
    """

    source: Path
    target: Path
    file_count: int = 0
    dir_count: int = 0
    estimated_size: int = 0
    conflicts: List[str] = field(default_factory=list)


class MergeFoldersService:
    """Service for managing case-insensitive folder merges.

    This service provides methods to:
    - Scan directories for case-insensitive duplicates
    - Generate merge previews with conflict detection
    - Execute safe merge operations
    - Handle user interactions for conflict resolution
    """

    def __init__(self) -> None:
        """Initialize the MergeFoldersService."""
        self.logger = logger

    def scan_duplicates(self, path: Path) -> List[DuplicateGroup]:
        """Scan a directory recursively for case-insensitive duplicate folders.

        This method walks the directory tree and identifies all folders that
        have the same name when case is ignored. Folders at the same level
        with matching case-insensitive names are grouped together.

        Args:
            path: Root directory to scan for duplicates

        Returns:
            List of DuplicateGroup objects, one per set of case-insensitive
            duplicates. Empty list if no duplicates found.

        Raises:
            ValueError: If path does not exist or is not a directory
            PermissionError: If path is not readable
        """
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        duplicates_by_parent: Dict[Path, Dict[str, List[Tuple[str, Path]]]] = {}

        # Walk directory tree
        for root, dirs, _ in os.walk(path):
            root_path = Path(root)

            # Group subdirectories by case-insensitive name
            case_insensitive_groups: Dict[str, List[Tuple[str, Path]]] = {}

            for dir_name in dirs:
                dir_path = root_path / dir_name
                # Use lowercase as grouping key
                lower_name = dir_name.lower()

                if lower_name not in case_insensitive_groups:
                    case_insensitive_groups[lower_name] = []

                case_insensitive_groups[lower_name].append((dir_name, dir_path))

            # Store groups with more than one variant
            duplicates = {
                k: v for k, v in case_insensitive_groups.items() if len(v) > 1
            }

            if duplicates:
                duplicates_by_parent[root_path] = duplicates

        # Convert to DuplicateGroup objects
        result: List[DuplicateGroup] = []

        for parent_path, groups in duplicates_by_parent.items():
            for lower_name, variants in groups.items():
                group = DuplicateGroup(parent_path=parent_path)

                for actual_name, full_path in variants:
                    group.add_variant(actual_name, full_path)

                result.append(group)

        return result

    def get_target_folder(self, group: DuplicateGroup) -> str:
        """Determine the target folder for a duplicate group.

        Priority:
        1. All-lowercase variant (if exists): Most common case
        2. First variant alphabetically (fallback): Deterministic

        This method does not modify the group; it returns what the target
        should be. The caller can then prompt user if no lowercase exists.

        Args:
            group: The DuplicateGroup to analyze

        Returns:
            Name of the folder that should be the merge target
        """
        # Find all-lowercase variant
        for variant in group.variants:
            if variant.islower():
                return variant

        # Fallback: first alphabetically (deterministic)
        return sorted(group.variants)[0]

    def get_conflicts(self, source: Path, target: Path) -> List[str]:
        """Detect file name conflicts between source and target folders.

        A conflict occurs when both source and target contain a file or
        folder with the same name (case-sensitive).

        Args:
            source: Path to source folder
            target: Path to target folder

        Returns:
            List of filenames that exist in both folders
        """
        if not target.exists():
            # No conflicts if target doesn't exist yet
            return []

        source_items = set(os.listdir(source))
        target_items = set(os.listdir(target))

        return sorted(list(source_items & target_items))

    def count_items(self, path: Path) -> Tuple[int, int, int]:
        """Count files, directories, and total size in a folder.

        Args:
            path: Path to folder to count

        Returns:
            Tuple of (file_count, dir_count, total_size_bytes)
        """
        file_count = 0
        dir_count = 0
        total_size = 0

        for root, dirs, files in os.walk(path):
            dir_count += len(dirs)
            file_count += len(files)

            for file_name in files:
                file_path = Path(root) / file_name
                try:
                    total_size += file_path.stat().st_size
                except (OSError, FileNotFoundError):
                    # File may have been deleted or become inaccessible
                    pass

        return file_count, dir_count, total_size

    def preview_merge(
        self,
        source: Path,
        target: Path,
    ) -> MergeOperation:
        """Generate a preview of what will happen during a merge.

        This method does not modify any files. It provides information
        about the merge operation including file counts, size, and conflicts.

        Args:
            source: Path to folder being merged (source)
            target: Path to folder receiving contents (target)

        Returns:
            MergeOperation object with detailed preview information

        Raises:
            ValueError: If source doesn't exist
        """
        if not source.exists():
            raise ValueError(f"Source folder does not exist: {source}")

        file_count, dir_count, size = self.count_items(source)
        conflicts = self.get_conflicts(source, target)

        return MergeOperation(
            source=source,
            target=target,
            file_count=file_count,
            dir_count=dir_count,
            estimated_size=size,
            conflicts=conflicts,
        )

    def execute_merge(
        self,
        operation: MergeOperation,
        conflict_handler: Optional[Callable] = None,
    ) -> None:
        """Execute a merge operation, moving files from source to target.

        This method performs the actual merge:
        1. Creates target directory if it doesn't exist
        2. Moves all contents from source to target
        3. Deletes the now-empty source directory

        The operation is designed to be as atomic as possible using
        filesystem-level move operations.

        Args:
            operation: MergeOperation object describing what to merge
            conflict_handler: Optional callable to handle conflicts.
                             Takes (source_file_name, is_dir) -> str
                             Returns action: "skip", "rename", "overwrite"

        Raises:
            OSError: If move operations fail
            PermissionError: If insufficient permissions
        """
        source = operation.source
        target = operation.target

        self.logger.debug(f"Starting merge: {source} -> {target}")

        # Create target directory if needed
        target.mkdir(parents=True, exist_ok=True)

        # Move all contents
        for item in os.listdir(source):
            src_item = source / item
            dst_item = target / item

            # Handle conflicts based on handler or default behavior
            if dst_item.exists():
                if conflict_handler:
                    action = conflict_handler(item, src_item.is_dir())
                    if action == "skip":
                        self.logger.debug(f"Skipping conflicting item: {item}")
                        continue
                    elif action == "rename":
                        # Rename source file before moving
                        base_name = item
                        suffix = ""
                        if "." in item:
                            base, ext = item.rsplit(".", 1)
                            base_name = base
                            suffix = f".{ext}"

                        counter = 1
                        new_name = f"{base_name}-conflict{suffix}"
                        while (target / new_name).exists():
                            new_name = f"{base_name}-conflict-{counter}{suffix}"
                            counter += 1

                        dst_item = target / new_name
                        self.logger.debug(f"Renaming {item} to {new_name}")
                else:
                    # Default: skip target file (keep target version)
                    self.logger.debug(f"Skipping conflicting item (default): {item}")
                    continue

            # Move the item
            try:
                shutil.move(str(src_item), str(dst_item))
                self.logger.debug(f"Moved: {src_item.name} -> {dst_item}")
            except (OSError, shutil.Error) as e:
                self.logger.error(f"Failed to move {src_item}: {e}")
                raise

        # Delete source directory (should be empty now)
        try:
            source.rmdir()
            self.logger.debug(f"Deleted source directory: {source}")
        except OSError as e:
            self.logger.error(f"Failed to delete source directory {source}: {e}")
            # Don't raise - operation mostly succeeded

    def format_size(self, size_bytes: int) -> str:
        """Format byte size to human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "2.3 GB")
        """
        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} PB"
