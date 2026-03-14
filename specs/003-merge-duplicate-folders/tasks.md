# Phase 2 Implementation Plan: Merge Duplicate Folders Feature

**Feature Branch**: `003-merge-duplicate-folders`  
**Created**: 2026-03-14  
**Planning Phase**: Active  
**Implementation Complexity**: Medium  
**Estimated Duration**: 2-3 days  

---

## Feature Overview

This feature enables users to identify and merge case-insensitive duplicate folders within a directory structure. The implementation follows a 4-phase rollout strategy, progressively adding features from discovery to conflict handling.

---

## Architecture & Design

### 1. Service Layer: `MergeFoldersService`

**File**: `src/cli/services/merge_service.py`

**Responsibilities**:
- Scan directories recursively and identify case-insensitive duplicate folders
- Group duplicates and determine merge targets
- Execute merge operations with proper error handling
- Support preview mode (no modifications)

**Key Classes**:

```python
class DuplicateGroup:
    """Represents a group of case-insensitive duplicate folders."""
    parent_path: str           # Parent directory containing duplicates
    variants: List[str]        # List of duplicate folder names
    paths: Dict[str, Path]     # Folder name -> full path mapping
    target: str                # Target folder to merge into
    
class MergeOperation:
    """Represents a single merge operation."""
    source: Path               # Folder being merged
    target: Path               # Target folder
    file_count: int            # Number of files to move
    estimated_size: int        # Estimated disk space
    conflicts: List[str]       # Files with conflicts
    
class MergeFoldersService:
    """Main service for merge operations."""
    def scan_duplicates(path: Path) -> List[DuplicateGroup]
    def get_target_folder(group: DuplicateGroup) -> str
    def preview_merge(group: DuplicateGroup) -> MergeOperation
    def execute_merge(operation: MergeOperation, force: bool) -> None
    def handle_conflict(source_file, target_file) -> str
```

**Implementation Notes**:
- Use `pathlib.Path` for cross-platform compatibility
- Implement case-insensitive comparison: `path.name.lower()`
- Group detection using dict with lowercase keys
- Atomic operations using `shutil.move()` for files/folders
- Track conflicts by comparing file lists before merge

### 2. CLI Command: `merge-folders`

**File Structure**:
```
src/cli/commands/system/
├── __init__.py
└── merge_cmd.py
```

**Command Structure**:
```
gts system merge-folders [PATH] [OPTIONS]
```

**Parameters**:
- `PATH`: Directory to scan (required, argument)
- `--preview`: Show duplicates without merging (flag)
- `--force`: Skip confirmations, auto-merge (flag)

**Implementation Pattern** (following import_cmd.py):
1. Parse arguments and validate path exists
2. Call MergeFoldersService.scan_duplicates()
3. Display duplicate groups using Rich formatting
4. Loop through each group:
   - Generate merge preview
   - Display source → target with file count
   - Handle user choice (auto vs prompt)
   - Execute merge if confirmed
5. Display summary statistics

### 3. Result Models: `MergeResult`

**File**: `src/cli/models/merge_result.py` (if needed) OR add to existing models

**Data Structure**:
```python
class MergeResult:
    total_groups: int              # Total duplicate groups found
    groups_merged: int             # Successfully merged groups
    groups_skipped: int            # User-skipped groups
    total_files_moved: int         # Total files transferred
    conflicts_resolved: int        # Conflicts handled
    conflicts_unresolved: int      # User cancelled conflicts
    errors: List[str]              # Error messages
    operation_type: str            # "preview" | "merge"
```

---

## Implementation Phases

### Phase 1: Discovery & Display (P1-001)

**User Story**: Discover Duplicate Folders

**Tasks**:
1. Create `MergeFoldersService` with `scan_duplicates()` method
2. Implement recursive directory scanning
3. Implement case-insensitive duplicate detection
4. Group duplicates by equivalence class
5. Create `merge_cmd.py` with basic display
6. Register new `system` command group
7. Write unit tests for scanning logic
8. Write integration tests for display output

**Requirements Covered**: FR-001, FR-002, FR-003, FR-004, FR-010

**Success Criteria**: 
- SC-001: Scan 1000+ folders in 10 seconds
- SC-003: 100% accuracy in duplicate detection
- SC-005: Handle 10+ nesting levels

**Expected Output**:
```
Scanning for duplicate case-insensitive folders...
Found 3 duplicate groups:

Group 1: Mods
  • /path/to/Mods
  • /path/to/mods

Group 2: PhOne
  • /path/to/data/PhOne
  • /path/to/data/phone

Group 3: ModS
  • /path/to/ModS
  • /path/to/mods
```

---

### Phase 2: Automatic Merge (P1-002)

**User Story**: Merge with Automatic Lowercase Preference

**Tasks**:
1. Implement `get_target_folder()` - auto-select lowercase
2. Implement `preview_merge()` - show file count and impact
3. Add file counting logic to MergeFoldersService
4. Implement `execute_merge()` - atomic move operations
5. Add folder deletion after merge
6. Update `merge_cmd.py` to show previews and request confirmation
7. Implement `--force` flag for auto-merge without prompt
8. Write tests for merge operations

**Requirements Covered**: FR-005, FR-006, FR-007, FR-008, FR-011, FR-015

**Success Criteria**:
- SC-002: Merge 100+ files in 30 seconds
- SC-004: Clear preview output
- SC-006: Zero data loss

**Expected Output**:
```
Merge Preview:
  Source: /path/to/Mods (152 files, 2.3 GB)
  Target: /path/to/mods (already exists)
  Action: Move 152 files from Mods into mods, delete Mods

Proceed with merge? [y/N]:
```

---

### Phase 3: User Choice (P2-003)

**User Story**: User Chooses Folder to Keep

**Tasks**:
1. Modify `get_target_folder()` to handle non-lowercase cases
2. Implement user choice prompt with numbered options
3. Handle cancellation (Ctrl+C, N response)
4. Update `merge_cmd.py` with choice logic
5. Write tests for user choice scenarios

**Requirements Covered**: FR-009

**Expected Output**:
```
No all-lowercase variant found for: Mods, moDs, ModS
Which folder should be the target?
  1. Mods
  2. moDs
  3. ModS

Select (1-3) or press Ctrl+C to cancel: 
```

---

### Phase 4: Conflict Handling (P3-005)

**User Story**: Handle File Conflicts Between Duplicates

**Tasks**:
1. Implement conflict detection in `preview_merge()`
2. Implement `handle_conflict()` with options: skip, rename, cancel
3. Add conflict resolution prompts to `merge_cmd.py`
4. Handle partial merges (some files moved, some skipped)
5. Write comprehensive conflict test scenarios

**Requirements Covered**: FR-012

**Expected Output**:
```
Conflict detected: file.txt exists in both Mods and mods

Options:
  1. Keep target version (skip source file)
  2. Rename source file (e.g., file-mods-conflict.txt)
  3. Cancel merge

Select (1-3): 
```

---

## File Structure Changes

### New Files to Create
```
src/cli/
├── services/
│   └── merge_service.py              # MergeFoldersService class
├── models/
│   └── merge_result.py               # MergeResult data class (optional)
└── commands/system/
    ├── __init__.py                   # System group module
    └── merge_cmd.py                  # merge-folders command

tests/
├── unit/
│   └── test_merge_service.py         # Service logic tests
├── integration/
│   └── test_merge_workflows.py       # End-to-end workflows
└── contract/
    └── test_merge_contract.py        # CLI contract tests
```

### Files to Modify
```
src/cli/
├── commands/__init__.py              # Register system group
├── commands/groups/
│   ├── __init__.py                   # Add system_app import
│   └── system.py                     # NEW: Create system group

tests/
└── conftest.py                       # Add merge test fixtures if needed
```

---

## Command Registration Flow

### Step 1: Create System Group (`src/cli/commands/groups/system.py`)
```python
import typer
from ..system.merge_cmd import merge_cmd

system_app = typer.Typer(
    help="System utilities for file management",
    rich_markup_mode="rich",
)

system_app.command(name="merge-folders")(merge_cmd)
```

### Step 2: Update Command Init (`src/cli/commands/__init__.py`)
```python
from .groups.database import database_app
from .groups.system import system_app  # Add this line

def register_commands(app: typer.Typer) -> None:
    app.add_typer(database_app, name="database")
    app.add_typer(system_app, name="system")  # Add this line
```

### Step 3: Update Groups Init (`src/cli/commands/groups/__init__.py`)
```python
# Add exports if using __all__
from .database import database_app
from .system import system_app

__all__ = ["database_app", "system_app"]
```

---

## Testing Strategy

### Unit Tests (`tests/unit/test_merge_service.py`)
- **Duplicate Detection**: Test case-insensitive grouping
- **Target Selection**: Test lowercase priority, multi-variant handling
- **File Counting**: Test accurate file counts and size estimation
- **Conflict Detection**: Test same-name file detection
- **Edge Cases**: Missing folders, permission issues, special characters

**Test Fixtures**:
```python
@pytest.fixture
def temp_merge_structure():
    """Create test directory with duplicate folders."""
    # Create /Mods and /mods with test files
    # Return paths and expected groups
```

### Integration Tests (`tests/integration/test_merge_workflows.py`)
- **Full Workflow**: Scan → Preview → Merge (auto)
- **User Choice**: Scan → Preview → Choose → Merge
- **Conflict Resolution**: Scan → Conflict → Resolve → Merge
- **Preview Mode**: Verify no files are modified with `--preview`
- **Force Mode**: Verify auto-merge with `--force`

### Contract Tests (`tests/contract/test_merge_contract.py`)
- **CLI Arguments**: Validate path argument and flags
- **Output Format**: Verify Rich output formatting
- **Error Messages**: Verify clear error messages
- **Exit Codes**: Verify proper exit codes (0=success, 1=error)

---

## Development Checklist

### Phase 1: Discovery & Display
- [ ] Create `src/cli/services/merge_service.py`
  - [ ] Implement `DuplicateGroup` class
  - [ ] Implement `scan_duplicates()` method
  - [ ] Implement case-insensitive comparison logic
  - [ ] Test with various directory structures
- [ ] Create `src/cli/commands/system/` directory
- [ ] Create `src/cli/commands/system/merge_cmd.py`
  - [ ] Parse path argument
  - [ ] Call scan_duplicates()
  - [ ] Display results with Rich formatting
- [ ] Register system command group
  - [ ] Create `src/cli/commands/groups/system.py`
  - [ ] Update `src/cli/commands/__init__.py`
- [ ] Create unit tests for scanning
- [ ] Create integration tests for display
- [ ] Verify 100% test pass rate
- [ ] Verify 0 linting errors

### Phase 2: Automatic Merge
- [ ] Implement `get_target_folder()` for lowercase selection
- [ ] Implement `preview_merge()` with file counting
- [ ] Implement `execute_merge()` with atomic operations
- [ ] Add `--force` flag support
- [ ] Update merge_cmd.py with confirmation prompts
- [ ] Handle folder deletion after merge
- [ ] Create merge operation tests
- [ ] Create merge execution tests
- [ ] Verify performance (30s for 100+ files)
- [ ] Verify all tests pass

### Phase 3: User Choice
- [ ] Modify `get_target_folder()` for non-lowercase cases
- [ ] Implement user choice prompt
- [ ] Handle cancellation scenarios
- [ ] Create user choice tests
- [ ] Verify prompt interaction
- [ ] Verify all tests pass

### Phase 4: Conflict Handling
- [ ] Implement conflict detection
- [ ] Implement `handle_conflict()` method
- [ ] Add conflict resolution options
- [ ] Create conflict test scenarios
- [ ] Verify all tests pass
- [ ] Verify zero data loss

### Final Steps
- [ ] Run full test suite
- [ ] Verify zero linting errors
- [ ] Create feature commit
- [ ] Push to feature branch
- [ ] Prepare for merge to main

---

## Key Implementation Notes

### Performance Optimization
- **Recursive Scan**: Use `os.walk()` or `pathlib.glob()` for efficiency
- **Case Comparison**: Cache lowercase names in dict to avoid repeated conversions
- **File Counting**: Use `os.scandir()` for fast directory listing
- **Atomic Moves**: Use `shutil.move()` which is atomic on most filesystems

### Error Handling
- **Permission Errors**: Catch `PermissionError`, report specific folder, allow continue
- **Missing Folders**: Check existence before scanning, clear error message
- **Path Validation**: Ensure target directory exists before operations
- **Interrupted Operations**: Document in limitations (Assumption 5 edge case)

### User Experience
- **Progress Feedback**: Show scanning progress for large directories
- **Clear Prompts**: Use numbered options for choices
- **Safe Defaults**: Preview by default, merge only on explicit confirmation
- **Helpful Errors**: Include remediation suggestions in error messages

### Code Quality
- **Type Hints**: Full type hints on all functions
- **Docstrings**: Comprehensive docstrings (Google style)
- **Error Messages**: Clear, actionable error messages using Rich
- **Logging**: Use Python logging for debug information

---

## Success Metrics

### Code Quality
- ✅ All tests passing (aim for 95%+ coverage on merge_service.py)
- ✅ Zero linting errors (ruff check .)
- ✅ All type hints present and valid (mypy)
- ✅ Comprehensive docstrings

### Functional Completeness
- ✅ All 5 user stories implemented
- ✅ All 15 functional requirements met
- ✅ All 7 edge cases handled
- ✅ All 9 assumptions documented

### Performance
- ✅ Scan 1000+ folders in <10 seconds
- ✅ Merge 100+ files in <30 seconds
- ✅ Preview generation in <5 seconds

### User Experience
- ✅ Clear duplicate group display
- ✅ Informative merge previews
- ✅ Easy user choice prompts
- ✅ Helpful error messages

---

## Next Steps

1. **Start Phase 1 Implementation**
   - Create MergeFoldersService with scan_duplicates()
   - Create merge_cmd.py with basic display
   - Register system command group
   - Write and pass unit tests

2. **Proceed to Phase 2**
   - Add merge execution logic
   - Add preview generation
   - Add confirmation prompts

3. **Complete Phases 3 & 4**
   - Add user choice handling
   - Add conflict detection and resolution

4. **Final Validation**
   - All tests passing
   - Zero linting errors
   - Feature commit and push

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data loss during merge | Atomic operations, preview before merge, conflict detection |
| Incomplete merges | Use `shutil.move()`, verify all files transferred before deletion |
| Performance issues | Lazy evaluation, caching, early termination for large scans |
| User confusion | Clear prompts, numbered options, preview output, helpful errors |
| Permission issues | Check permissions before operations, clear error messages |

---

**Status**: Ready for Phase 1 Implementation  
**Approval**: ✅ Planning Complete

