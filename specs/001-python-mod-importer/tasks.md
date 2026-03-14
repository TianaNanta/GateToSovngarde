---

description: "Task list for Python Mod Importer feature implementation"
---

# Tasks: Python Mod Importer

**Input**: Design documents from `/specs/001-python-mod-importer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are NOT required for this feature per Constitution (simple CLI script)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create src/ directory in repository root
- [X] T002 Install rich library: `pip install rich` or add to pyproject.toml
- [X] T003 Create logs/ directory in repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Create main script entry point at src/mod_importer.py
- [X] T005 [P] Implement logging configuration with Rich console and file handlers in src/mod_importer.py
- [X] T006 Create database/ directory and verify GTSv101.txt exists

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Runtime Input (Priority: P1) 🎯 MVP

**Goal**: User is prompted for source/destination directories at runtime

**Independent Test**: Run script and verify prompts appear for both directories

### Implementation for User Story 1

- [X] T007 [US1] Implement get_source_directory() function in src/mod_importer.py to prompt user for source path
- [X] T008 [US1] Implement get_destination_directory() function in src/mod_importer.py to prompt user for destination path
- [X] T009 [US1] Add path validation to ensure source directory exists and is readable
- [X] T010 [US1] Create destination directory if it does not exist

**Checkpoint**: User Story 1 should be functional - script prompts for paths and validates them

---

## Phase 4: User Story 2 - Import Mods from List (Priority: P1) 🎯 MVP

**Goal**: Read mod list, search for archives, copy to destination

**Independent Test**: Run with sample mod list and verify matching files are copied

### Implementation for User Story 2

- [X] T011 [P] [US2] Implement read_mod_list() function to read database/GTSv101.txt
- [X] T012 [P] [US2] Implement find_matching_archives() function to search source directory for .zip, .7z, .rar files
- [X] T013 [US2] Implement copy_mod_files() function to copy matching archives to destination
- [X] T014 [US2] Connect runtime input to mod import workflow in main()

**Checkpoint**: User Story 2 should be functional - mods are imported from list

---

## Phase 5: User Story 3 - Database Folder Organization (Priority: P2)

**Goal**: Verify GTSv101.txt is in database folder (already done in planning)

**Independent Test**: Verify database/GTSv101.txt exists and is readable

**Status**: COMPLETED - Already moved GTSv101.txt to database/ folder during planning phase

**Checkpoint**: User Story 3 is complete

---

## Phase 6: User Story 4 - Progress and Result Reporting (Priority: P3)

**Goal**: Beautiful console output and log file generation

**Independent Test**: Run script and verify beautiful Rich output and log file creation

### Implementation for User Story 4

- [X] T015 [P] [US4] Add Rich progress display during file search in src/mod_importer.py
- [X] T016 [P] [US4] Add Rich progress display during file copy in src/mod_importer.py
- [X] T017 [US4] Implement display_summary() function with Rich panel showing total files copied
- [X] T018 [US4] Configure file logging to write to logs/mod_importer_YYYYMMDD_HHMMSS.log

**Checkpoint**: User Story 4 should be complete - beautiful output and log files working

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T019 [P] Add error handling for edge cases (invalid paths, no files found, etc.)
- [X] T020 [P] Add user cancellation support at prompts (Ctrl+C handling)
- [X] T021 Add shebang and make script executable: chmod +x src/mod_importer.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Works independently from US1
- **User Story 3 (P2)**: ALREADY COMPLETE - Database folder created
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Can parallel with US1 and US2

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- T007-T010 (US1) can parallel with T011-T014 (US2) after foundation
- T015-T018 (US4) can parallel with other user stories
- Polish tasks T019-T020 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Runtime Input)
4. Complete Phase 4: User Story 2 (Import Mods)
5. **STOP and VALIDATE**: Test the core functionality
6. Deploy/demo if ready - basic import works!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo (Core functionality complete!)
4. Add User Story 4 → Beautiful logging complete
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
