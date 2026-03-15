# Data Model: Merge Duplicate Folders

**Phase**: 1 - Design & Contracts  
**Date**: 2026-03-14  
**Status**: Complete  

## Entity Definitions

### 1. DuplicateGroup

**Purpose**: Represents a set of case-insensitive duplicate folders discovered during a scan.

**Fields**:
- `parent_path: Path` - Parent directory containing all duplicates (e.g., `/home/user/data`)
- `variants: List[str]` - Folder names that are duplicates (e.g., `["mods", "Mods", "MODS"]`)
- `target: Optional[str]` - Folder selected as merge target (e.g., `"mods"`)
- `paths: Dict[str, Path]` - Mapping of folder name → full path (e.g., `{"mods": Path("/data/mods"), "Mods": Path("/data/Mods")}`)

**Validation Rules**:
- `parent_path` must exist and be a directory
- `variants` must have 2+ items (otherwise not a duplicate)
- All variants must have identical names when lowercased
- `target` must be one of the `variants` (if set)
- `paths` keys must match `variants` entries

**State Transitions**:
```
Created → (target selected) → (merge executed) → Resolved
```

**Methods**:
- `sources()`: Returns list of folders to merge INTO target (all except target)
- `add_variant(name, path)`: Add a discovered duplicate variant

**Example**:
```python
group = DuplicateGroup(
    parent_path=Path("/home/data"),
    variants=["mods", "Mods"],
    target="mods",
    paths={"mods": Path("/home/data/mods"), "Mods": Path("/home/data/Mods")}
)
assert group.sources == ["Mods"]  # Only Mods will be merged into mods
```

---

### 2. MergeOperation

**Purpose**: Represents a single merge action: moving files from source folder into target folder.

**Fields**:
- `source: Path` - Folder being merged (e.g., `/home/data/Mods`)
- `target: Path` - Folder receiving contents (e.g., `/home/data/mods`)
- `file_count: int` - Number of files to transfer
- `dir_count: int` - Number of subdirectories to transfer
- `estimated_size: int` - Total size in bytes
- `conflicts: List[str]` - Files with same name in both source and target

**Validation Rules**:
- `source` must exist and be a directory (different from target)
- `target` may or may not exist
- `file_count` and `dir_count` must be ≥ 0
- `estimated_size` must be ≥ 0
- `conflicts` list must contain only filenames (not paths)

**State Transitions**:
```
Preview → (user confirms) → Executing → Completed
        → (user cancels) → Cancelled
```

**Methods**:
- None (data container only)

**Example**:
```python
operation = MergeOperation(
    source=Path("/home/data/Mods"),
    target=Path("/home/data/mods"),
    file_count=42,
    dir_count=5,
    estimated_size=2_500_000_000,  # 2.5 GB
    conflicts=["readme.txt"]  # File exists in both
)
```

---

### 3. MergeResult

**Purpose**: Summary of completed merge operations for a batch.

**Fields**:
- `total_groups: int` - Total duplicate groups found
- `groups_merged: int` - Groups successfully merged
- `groups_skipped: int` - Groups user chose not to merge
- `total_files_moved: int` - Total files successfully transferred
- `conflicts_resolved: int` - Number of conflicts handled
- `conflicts_unresolved: int` - Number of conflicts not resolved
- `errors: List[str]` - Error messages from failed operations
- `operation_type: str` - Type of operation ("preview" or "merge")

**Validation Rules**:
- `total_groups ≥ groups_merged + groups_skipped`
- `total_files_moved ≥ 0`
- `conflicts_resolved + conflicts_unresolved ≥ 0`
- `operation_type` in ("preview", "merge")

**Example**:
```python
result = MergeResult(
    total_groups=3,
    groups_merged=2,
    groups_skipped=1,
    total_files_moved=156,
    conflicts_resolved=2,
    conflicts_unresolved=0,
    errors=[],
    operation_type="merge"
)
```

---

## Relationships

```
MergeFolder Workflow:
    ┌─────────────────────────────────────────────────────┐
    │                                                       │
    │  Scan Directory → [DuplicateGroup, ...]             │
    │       ↓                                               │
    │  [For Each DuplicateGroup]                           │
    │       ↓                                               │
    │  Get Target → (lowercase preferred)                  │
    │       ↓                                               │
    │  Create MergeOperation(s) → Preview                  │
    │       ↓                                               │
    │  User Confirmation?                                  │
    │       ├─→ YES → Execute MergeOperation               │
    │       │          Update target with source contents  │
    │       │          Delete source folder                │
    │       └─→ NO → Skip Group                           │
    │                                                       │
    └─────────────────────────────────────────────────────┘
        ↓
    Return MergeResult with summary
```

**Key Relationships**:
- **DuplicateGroup → MergeOperation(s)**: Each duplicate group may have multiple operations (one per source folder)
- **MergeOperation → File System**: Operates on actual files during execution
- **Multiple Groups → MergeResult**: All operations summarized in single result

---

## Validation Rules by Entity

### DuplicateGroup Validation

| Rule | When | Action |
|------|------|--------|
| parent_path exists | Construction | Raise ValueError if missing |
| parent_path is directory | Construction | Raise ValueError if file |
| 2+ variants | Construction | Only create if 2+ duplicates |
| Case-insensitive match | Construction | Verify all variants same when lowercased |
| target ∈ variants | Set target | Raise ValueError if not valid |

### MergeOperation Validation

| Rule | When | Construction |
|------|------|--------------|
| source exists | Preview | Raise ValueError if missing |
| source ≠ target | Preview | Raise ValueError if same |
| target can be created | Execute | Create if missing |
| file_count accurate | Preview | Count via os.walk() |
| Size calculation correct | Preview | Sum all file sizes |
| Conflicts detected | Preview | Compare os.listdir() |

### MergeResult Validation

| Rule | When | Action |
|------|------|--------|
| total = merged + skipped | Completion | Verify invariant |
| errors populated | Any failure | Append error message |
| operation_type set | Construction | Require valid type |

---

## State Management

### Merge Workflow States

```python
# Phase 1: Discovery
groups: List[DuplicateGroup] = service.scan_duplicates(path)
# Each group: target = None

# Phase 2: Decision
for group in groups:
    group.target = service.get_target_folder(group)  # Auto or user choice
    # target now set to folder name (e.g., "mods")

# Phase 3: Preview
operation = service.preview_merge(source, target)
# operation includes file_count, conflicts, estimated_size
# No state changes in filesystem

# Phase 4: Execution
service.execute_merge(operation)  # Atomically moves files
# Filesystem modified: source contents → target, source deleted

# Phase 5: Summary
result: MergeResult = build_result(groups, operations, errors)
```

---

## Type Safety

All entities use type hints for IDE support:

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class DuplicateGroup:
    parent_path: Path
    variants: List[str] = field(default_factory=list)
    target: Optional[str] = None
    paths: Dict[str, Path] = field(default_factory=dict)
```

**Type Benefits**:
- IDE autocomplete (hover shows available fields)
- Static analysis (mypy catches type errors before runtime)
- Self-documenting (readers know field types without inspection)
- JSON serialization ready (can add .to_dict() methods)

---

## Testing Implications

### Unit Tests per Entity

**DuplicateGroup**:
- Construction with valid variants
- Adding variants
- Getting source folders (non-target)
- Validation (reject mismatched case)

**MergeOperation**:
- Construction with real directory structure
- File/dir counting accuracy
- Conflict detection
- Size estimation accuracy

**MergeResult**:
- Building from completed operations
- Error aggregation
- Invariant checks (merged + skipped = total)

### Integration Tests per Workflow

- Full scan → decision → preview → execute workflow
- Multiple groups in one batch
- Skip logic (preview only, no execution)
- Conflict handling paths

---

## Design Decisions

### Why @dataclass?

- **Immutability**: Fields are set at construction; modified carefully
- **Type Safety**: Type hints enable static analysis
- **Minimal Boilerplate**: No __init__, __repr__, __eq__ to write
- **Serializable**: Easy to add JSON export later (e.g., for logs)

### Why Separate MergeOperation?

- **Reusability**: Same data structure used for preview and execution
- **Testability**: Can test preview independently from execution
- **Clarity**: Separate concepts: "what will happen" vs. "what did happen"

### Why MergeResult?

- **Batch Summary**: One result object for entire session
- **Error Aggregation**: All failures in one place
- **Future Export**: Can serialize to JSON for audit logs
- **Type Safety**: Structured summary vs. unstructured print()

---

## Future Extensions

### Phase 2+: Conflict Resolution

Add to MergeOperation:
```python
@dataclass
class ConflictResolution:
    filename: str
    action: str  # "skip", "rename", "overwrite"
    resolved: bool
```

### Phase 3+: Dry-Run Reporting

Add to MergeResult:
```python
dry_run_executed: bool
would_delete_source: bool  # Important for user understanding
```

### Phase 4+: Audit Log

Add to MergeResult:
```python
timestamp: datetime
user: str  # For multi-user systems
detailed_moves: List[Tuple[Path, Path]]  # Each file moved
```

---

## Schema Completeness Check

- ✅ All user stories can be represented with these entities
- ✅ All 15 functional requirements can be tested against entities
- ✅ All 7 edge cases can be modeled (conflicts, permissions, missing folders)
- ✅ All performance metrics can be measured (file_count, estimated_size)
- ✅ Type safety enabled for IDE/static analysis
- ✅ Test coverage strategy clear for each entity

**Status**: ✅ Data model complete and ready for implementation
