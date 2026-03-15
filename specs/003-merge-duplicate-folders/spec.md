# Feature Specification: Merge Duplicate Case-Insensitive Folders

**Feature Branch**: `003-merge-duplicate-folders`  
**Created**: 2026-03-14  
**Status**: Draft  
**Input**: Merge duplicate case-insensitive folders recursively with user confirmation and automatic cleanup

## User Scenarios & Testing

### User Story 1 - Discover Duplicate Folders (Priority: P1)

A user wants to identify all case-insensitive duplicate folders within a directory structure without taking action. They need a clear summary of what duplicates exist before deciding to proceed with merging.

**Why this priority**: This is the foundational feature. Users must first understand what will be merged before committing to changes. Without this, users cannot make informed decisions about their file structure.

**Independent Test**: Can be fully tested by scanning a directory with known case-insensitive duplicates and verifying the complete list is displayed without modifying any folders.

**Acceptance Scenarios**:

1. **Given** a directory with case-insensitive duplicate folders (e.g., `/mnt/data/Mods` and `/mnt/data/mods`), **When** user runs merge command, **Then** system displays all duplicate groups with their full paths before requesting confirmation
2. **Given** nested duplicate folders (e.g., `/data/video/PhOne` and `/data/video/phone`), **When** user scans the directory, **Then** system lists all duplicates recursively including their exact folder paths
3. **Given** a directory with no duplicates, **When** user scans the directory, **Then** system reports "No duplicate case-insensitive folders found"
4. **Given** multiple duplicate groups in the same directory scan (e.g., `Mods`/`mods` AND `PhOne`/`phone`), **When** user scans, **Then** system lists all groups clearly separated with folder counts

---

### User Story 2 - Merge Folders with Automatic Lowercase Preference (Priority: P1)

A user wants to merge duplicate case-insensitive folders automatically when one version is all lowercase. The system should merge contents into the lowercase folder and remove the variant with uppercase letters.

**Why this priority**: This handles the most common case (e.g., `Mods` → `mods`, `PhOne` → `phone`) and provides automatic resolution without requiring user input, improving efficiency and predictability.

**Independent Test**: Can be fully tested by creating duplicate folders where one is all lowercase, running merge, and verifying contents are consolidated into lowercase version and variant is deleted.

**Acceptance Scenarios**:

1. **Given** duplicate folders `/mnt/data/Mods` (with files) and `/mnt/data/mods` (empty or with files), **When** user confirms merge, **Then** all contents move to `/mnt/data/mods` and `/mnt/data/Mods` is deleted
2. **Given** `/data/video/PhOne` and `/data/video/phone`, **When** merge is confirmed, **Then** all files from `PhOne` move to `phone` and `PhOne` directory is removed
3. **Given** multiple files in the capitalized folder, **When** merge executes, **Then** all files are successfully transferred to lowercase folder
4. **Given** folders with subdirectories inside capitalized variant, **When** merge executes, **Then** entire directory tree (including subdirs) is moved to lowercase version

---

### User Story 3 - User Chooses Folder to Keep (Priority: P2)

A user encounters duplicate folders where neither is all lowercase (e.g., `Mods` and `moDs`). The system should prompt the user to choose which variant to keep and merge the other into it.

**Why this priority**: Handles edge cases where no clear "lowercase" preference exists. User control is necessary to avoid incorrect merges that could lose important distinctions.

**Independent Test**: Can be fully tested by creating duplicate folders with mixed case (neither all lowercase), running merge, answering the prompt, and verifying the chosen variant receives all contents from the other.

**Acceptance Scenarios**:

1. **Given** `/mnt/data/Mods` and `/mnt/data/moDs` both with content, **When** user runs merge, **Then** system prompts "Which folder should be the target: Mods or moDs?" with clear numbered options
2. **Given** user selects option for `Mods` as the target, **When** merge completes, **Then** all contents from `moDs` move to `Mods` and `moDs` is deleted
3. **Given** user selects option for `moDs` as the target, **When** merge completes, **Then** all contents from `Mods` move to `moDs` and `Mods` is deleted
4. **Given** user declines the prompt or presses Ctrl+C, **When** operation is canceled, **Then** no folders are modified and operation exits cleanly

---

### User Story 4 - Preview Merge Impact Before Committing (Priority: P2)

A user wants to see exactly what will happen during the merge (files affected, space impact) before confirming the operation.

**Why this priority**: Gives users confidence and allows them to identify potential issues (like conflicting files) before data is moved. Reduces accidental data loss.

**Independent Test**: Can be fully tested by running merge command, reviewing the preview output, then canceling and verifying no changes occurred.

**Acceptance Scenarios**:

1. **Given** duplicate folders with files, **When** user runs merge command, **Then** system shows preview: source folder, target folder, number of files to move, and estimated disk impact
2. **Given** preview information displayed, **When** user is prompted for confirmation, **Then** user can review and approve (yes/no) before any files are moved
3. **Given** user reviews preview and declines, **When** user selects "no" or cancels, **Then** no folders or files are modified

---

### User Story 5 - Handle File Conflicts Between Duplicates (Priority: P3)

A user has duplicate folders where both contain files with the same name. The system should detect and handle conflicts gracefully without losing data.

**Why this priority**: Prevents accidental data loss when merging folders with overlapping files. While less common, this is critical for safety and user confidence.

**Independent Test**: Can be fully tested by creating duplicate folders with same-named files, attempting merge, and verifying conflict handling behavior.

**Acceptance Scenarios**:

1. **Given** `/mnt/data/mods/file.txt` and `/mnt/data/Mods/file.txt` both exist with content, **When** merge is attempted, **Then** system detects conflict and warns user before proceeding
2. **Given** conflict warning displayed, **When** user is prompted for action, **Then** system offers options: keep target version (skip source file), rename source file (e.g., `file-mods-conflict.txt`), or cancel merge
3. **Given** user selects "keep target", **When** merge executes, **Then** target folder's version is preserved and source file is not moved

---

### Edge Cases

- What happens when the folder to scan doesn't exist? (System should display clear error message and exit)
- What happens when user lacks read permissions on a duplicate folder? (System should report specific folder and skip or fail gracefully)
- What happens when user lacks write permissions on the target folder for merge? (System should fail gracefully with clear permission error before attempting move)
- What happens when a folder name contains special characters or spaces? (System should handle correctly, no issues expected)
- What happens when merge is interrupted mid-operation (e.g., Ctrl+C, power loss)? (Operation stops, partially moved files remain in transition state - document in limitations)
- What happens when a duplicate group has more than 2 variants (e.g., `Mods`, `mods`, `MODS`)? (System merges all into lowercase variant if it exists, or prompts user to choose one)
- What happens with symbolic links or junctions? (Treat as regular folders - follow symlinks during scan)

## Requirements

### Functional Requirements

- **FR-001**: System MUST scan the provided directory recursively and identify all folders that are case-insensitive duplicates (same name, ignoring case)
- **FR-002**: System MUST group and display duplicate folders by their case-insensitive equivalence class (e.g., `Mods`, `mods`, `MODS` shown as one group)
- **FR-003**: System MUST display the complete file paths of all discovered duplicate folder groups before prompting for action
- **FR-004**: System MUST NOT list or display individual files - only folder structures should be shown in the scan results
- **FR-005**: System MUST prompt user for explicit confirmation before performing any merge operations
- **FR-006**: System MUST automatically select the all-lowercase folder variant as the merge target when one exists in a duplicate group
- **FR-007**: System MUST move all contents from non-target folders into the target folder using atomic file operations
- **FR-008**: System MUST delete the source folder(s) after successful content transfer, leaving only the target folder
- **FR-009**: System MUST prompt the user to choose a target folder when no all-lowercase variant exists (e.g., `Mods` vs `moDs`)
- **FR-010**: System MUST accept the folder to scan as a command-line argument (e.g., `gts merge-folders /mnt/data`)
- **FR-011**: System MUST provide a preview of each merge showing source folder path, target folder path, and number of files to be moved
- **FR-012**: System MUST detect file name conflicts between duplicate folders and warn the user before proceeding
- **FR-013**: System MUST provide clear, actionable error messages for permission issues, missing directories, or scan failures
- **FR-014**: System MUST support a `--preview` flag to show duplicates and merge plans without executing any moves
- **FR-015**: System MUST support a `--force` flag to skip user confirmation prompts and auto-merge using default rules (for scripting)

### Key Entities

- **Duplicate Folder Group**: A set of two or more folders in the same parent directory with identical names ignoring case sensitivity (e.g., `Mods`, `mods`, `MODS`)
- **Target Folder**: The designated folder that will receive all contents from other duplicates in its group (typically the all-lowercase variant)
- **Source Folder**: A folder whose entire contents will be transferred to the target folder and whose directory itself will be deleted
- **Merge Operation**: The atomic process of moving all files/subdirectories from source folder(s) to target folder and deleting the now-empty source folder(s)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can identify all case-insensitive duplicate folders in a directory structure with 1000+ subfolders within 10 seconds
- **SC-002**: Merge operation for a duplicate group with 100+ files completes successfully within 30 seconds
- **SC-003**: 100% of case-insensitive duplicate folders are correctly identified (zero false positives in controlled test scenarios)
- **SC-004**: Users report confidence in merge operations - preview clearly shows what folders will be merged and which is the target
- **SC-005**: System successfully detects duplicates at any nesting depth (minimum 10 levels of subdirectories tested)
- **SC-006**: Zero data loss - all files from source folders successfully transfer to target folders without corruption or silent overwrites
- **SC-007**: Users can complete full merge workflow (scan → review → resolve conflicts if any → confirm → execute) for 10 duplicate groups in under 3 minutes
- **SC-008**: All error scenarios (missing folders, permission issues, special characters) result in clear messages guiding user toward resolution within 1 minute

### Qualitative Outcomes

- Users feel confident that duplicate merging is safe before confirming
- Users understand which folder will be the keeper and which will be removed
- Error messages are clear enough that users need minimal external help

## Assumptions

1. **Case-insensitive comparison**: Folder name comparison uses case-insensitive logic (all uppercase/lowercase/mixed variants are treated as duplicates)
2. **Lowercase priority**: When multiple variants exist and one is all lowercase, it's automatically selected as merge target (predictable behavior)
3. **Atomic operations**: Move operations are atomic where possible (single filesystem preferred to minimize risk of partial moves)
4. **User confirmation**: Merges require explicit user approval unless `--force` flag is provided (safety first)
5. **Symbolic links**: Symlinks and shortcuts are treated as regular folders during scan (contents are followed)
6. **File conflict resolution**: When same-named files exist in both folders, target folder's version is preserved by default (non-destructive, requires user choice for alternatives)
7. **Empty folders**: Merging empty folders into targets succeeds immediately (zero files = successful operation)
8. **Permissions**: User is assumed to have necessary read/write permissions; errors are displayed clearly if not
9. **Single filesystem**: Operations stay within a single filesystem (cross-mount-point moves not supported initially)

## Out of Scope

- Moving duplicate folders across different mount points or filesystems
- Handling compressed archives (.zip, .7z, .rar) as special merge cases
- Scheduling or automation of recurring merge operations
- Integration with version control systems for conflict resolution
- Merging individual files (only folder-level merging)
- Deduplication of file contents (exact duplicate detection)

