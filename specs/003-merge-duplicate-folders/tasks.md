# Tasks: Merge Duplicate Case-Insensitive Folders

**Feature**: `003-merge-duplicate-folders`  
**Branch**: `003-merge-duplicate-folders`  
**Input**: Design documents from `/specs/003-merge-duplicate-folders/`  
**Status**: Ready for Phase 2+ implementation

**Prerequisites**: 
- ✅ plan.md (tech stack, architecture)
- ✅ spec.md (5 user stories with priorities P1, P2, P3)
- ✅ research.md (technology decisions)
- ✅ data-model.md (DuplicateGroup, MergeOperation, MergeResult entities)
- ✅ contracts/cli-merge-folders.md (CLI interface contract)
- ✅ Phase 1 implementation (49 tests, service + command in place)

**Tests**: Tests are INCLUDED. This feature uses TDD approach: tests written BEFORE implementation for all phases.

**Organization**: Tasks are grouped by user story (US1, US2, US3, US4, US5) to enable independent implementation and testing. Phase 2 foundation must complete before story implementation begins.

---

## Format: `- [ ] [TaskID] [P] [Story] Description with file path`

- **Checkbox**: Required markdown checkbox format
- **TaskID**: Sequential T001, T002, ... in execution order
- **[P]**: Optional marker for parallelizable tasks (different files, no dependencies)
- **[Story]**: Optional user story label (US1, US2, US3, US4, US5) for story phases only
- **Description**: Clear action with exact file paths

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization - ALREADY DONE in Phase 0 implementation

**Status**: The following tasks were completed in Phase 1 delivery (2026-03-14):

- ✅ T001 Created project structure per implementation plan
- ✅ T002 Setup Python 3.13 + Typer + Rich + pytest environment  
- ✅ T003 [P] Configured linting (ruff) and testing infrastructure
- ✅ T004 Created system command group in src/cli/commands/groups/system.py
- ✅ T005 [P] Created src/cli/services/merge_service.py with MergeFoldersService
- ✅ T006 [P] Created src/cli/commands/system/merge_cmd.py with merge-folders command
- ✅ T007 [P] Created data model classes (DuplicateGroup, MergeOperation, MergeResult)
- ✅ T008 [P] Configured test fixtures in tests/conftest.py
- ✅ T009 Registered system command group in src/cli/commands/__init__.py

**Checkpoint**: Foundation ready - P1 discovery & display working with 49 tests passing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core service infrastructure MUST be complete before US2+ implementation

**⚠️ CRITICAL**: Phase 1 (P1-001 Discovery) is COMPLETE. The following foundational tasks must complete before User Stories 2+ can be implemented.

### Tests for Foundational Phase (Contract & Permissions)

> **NOTE: These tests verify Phase 1 infrastructure. Use as validation for baseline before starting Phase 2.**

- [X] T010 [P] Verify all 183 existing tests pass: `pytest tests/ -v` in repo root
- [X] T011 [P] Verify linting is clean: `ruff check . --config pyproject.toml` in repo root
- [X] T012 [P] Verify Phase 1 coverage baseline: `pytest --cov=src/cli --cov-report=term-missing` in repo root

### Merge Service Foundation (Verify/Extend)

> **NOTE: Phase 1 service exists with scan & preview. Verify it works before Phase 2 implementation.**

- [X] T013 Verify MergeFoldersService.scan_duplicates() handles all duplicate variants in src/cli/services/merge_service.py
- [X] T014 Verify MergeFoldersService.preview_merge() calculates file counts and conflicts in src/cli/services/merge_service.py
- [X] T015 Verify DuplicateGroup.sources property returns all non-target folders in src/cli/models/duplicate_group.py (or inline in merge_service.py)

### Error Handling Infrastructure

- [X] T016 [P] Create custom exceptions module at src/cli/exceptions.py with MergeException, PermissionError, FolderNotFoundError
- [X] T017 [P] Add error translation layer in merge_cmd.py to convert service exceptions to user-friendly messages
- [X] T018 [P] Document error handling contract in src/cli/commands/system/merge_cmd.py

### Performance Baseline Validation

- [X] T019 [P] Create performance test file tests/performance/test_merge_perf.py with benchmarks
- [X] T020 [P] Benchmark Phase 1 implementation: scan 1000+ folders, verify <10s target
- [X] T021 [P] Document performance baselines in specs/003-merge-duplicate-folders/research.md

**Checkpoint**: Foundation validated - Phase 2+ stories can now start in parallel

---

## Phase 3: User Story 1 - Discover Duplicate Folders (Priority: P1) 🎯 MVP

**Goal**: Enable users to identify all case-insensitive duplicate folders in a directory without taking action.

**Independent Test**: Can be fully tested by scanning a directory with known case-insensitive duplicates and verifying the complete list is displayed without modifying any folders.

**Status**: ✅ P1-001 COMPLETE - Phase 1 implementation includes discovery and display with 24 unit tests + 14 contract tests

### Validation Tests for User Story 1

> **NOTE: These tests verify P1-001 is working correctly. All should PASS from Phase 1.**

- [X] T022 [P] [US1] Verify contract test for discovery output in tests/contract/test_merge_contract.py
- [X] T023 [P] [US1] Verify unit tests for DuplicateGroup creation in tests/unit/test_merge_service.py  
- [X] T024 [P] [US1] Verify integration test for full scan workflow in tests/integration/test_merge_workflows.py
- [X] T025 [P] [US1] Run scenario tests from quickstart.md: Scenario 1 (Preview mode), Scenario 4 (No duplicates found)

### Acceptance Criteria Validation

- [X] T026 [US1] Verify all duplicate groups display with full paths in CLI output per contracts/cli-merge-folders.md
- [X] T027 [US1] Verify nested duplicates (10+ levels deep) are correctly identified per performance baseline
- [X] T028 [US1] Verify "No duplicates found" message when scanning clean directory
- [X] T029 [US1] Verify multiple duplicate groups display separately with clear separation

**Checkpoint**: User Story 1 (Discovery) is fully validated and working. Ready for User Story 2.

---

## Phase 4: User Story 2 - Automatic Merge with Lowercase Preference (Priority: P1)

**Goal**: Merge duplicate folders automatically when one version is all lowercase. System merges contents into lowercase folder and removes the variant with uppercase letters.

**Independent Test**: Can be fully tested by creating duplicate folders where one is all lowercase, running merge with confirmation, and verifying contents are consolidated into lowercase version and variant is deleted.

**Dependencies**: User Story 1 (P1-001) must be complete

### Tests for User Story 2 (TDD - Write FIRST)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T030 [P] [US2] Create unit test for automatic target selection in tests/unit/test_merge_service.py (test that all-lowercase folder is selected as target)
- [X] T031 [P] [US2] Create unit test for file transfer in tests/unit/test_merge_service.py (test atomic move of files from source to target)
- [X] T032 [P] [US2] Create unit test for source folder deletion in tests/unit/test_merge_service.py (test source is deleted after merge)
- [X] T033 [P] [US2] Create integration test for full merge workflow in tests/integration/test_merge_workflows.py (end-to-end merge with confirmation)
- [X] T034 [P] [US2] Create integration test for merge with multiple files/subdirs in tests/integration/test_merge_workflows.py
- [X] T035 [P] [US2] Create contract test for interactive merge prompts in tests/contract/test_merge_contract.py
- [ ] T036 [US2] Create contract test for merge confirmation handling in tests/contract/test_merge_contract.py

### Implementation for User Story 2

- [X] T037 [US2] Implement MergeFoldersService.get_target_folder() in src/cli/services/merge_service.py (auto-select lowercase)
- [X] T038 [US2] Implement MergeFoldersService.execute_merge() in src/cli/services/merge_service.py (atomic file transfer using shutil.move())
- [X] T039 [US2] Implement MergeFoldersService.delete_source_folder() in src/cli/services/merge_service.py (remove source after merge)
- [X] T040 [US2] Add merge confirmation prompt in merge_cmd() in src/cli/commands/system/merge_cmd.py (Typer confirmation or Rich prompt)
- [X] T041 [US2] Add merge progress display in merge_cmd() in src/cli/commands/system/merge_cmd.py (Rich progress bar)
- [X] T042 [US2] Add merge summary display in merge_cmd() in src/cli/commands/system/merge_cmd.py (Rich panel with results)
- [X] T043 [US2] Implement MergeResult building in merge_cmd() to summarize merge operations
- [X] T044 [US2] Add comprehensive error handling for merge failures (permission errors, filesystem errors)
- [X] T045 [US2] Update src/cli/commands/system/merge_cmd.py to support --force flag (skip prompts)
- [X] T046 [US2] Add logging for merge operations in src/cli/services/merge_service.py

### Acceptance Criteria Validation

- [X] T047 [US2] Verify merge moves all files from capitalized folder to lowercase folder
- [X] T048 [US2] Verify source folder is deleted after successful merge
- [X] T049 [US2] Verify merge with subdirectories (entire tree moves)
- [X] T050 [US2] Verify performance: merge 100+ files <30s per specification
- [X] T051 [US2] Verify atomic operations (no partial transfers)
- [X] T052 [US2] Run scenario tests from quickstart.md: Scenario 2 (Interactive merge), Scenario 3 (Force mode)

**Checkpoint**: User Stories 1 & 2 complete. Automatic merge with lowercase preference working. Ready for User Story 3.

---

## Phase 5: User Story 3 - User Chooses Folder to Keep (Priority: P2)

**Goal**: Prompt user to choose target when duplicate folders where neither is all lowercase (e.g., `Mods` and `moDs`). User control is necessary for correct merge decisions.

**Independent Test**: Can be fully tested by creating duplicate folders with mixed case (neither all lowercase), running merge, answering the prompt, and verifying the chosen variant receives all contents from the other.

**Dependencies**: User Stories 1 & 2 must be complete

### Tests for User Story 3 (TDD - Write FIRST)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T053 [P] [US3] Create unit test for target selection logic in tests/unit/test_merge_service.py (when no lowercase variant exists)
- [X] T054 [P] [US3] Create unit test for variant comparison in tests/unit/test_merge_service.py (mixed case detection)
- [X] T055 [P] [US3] Create integration test for user target selection workflow in tests/integration/test_merge_workflows.py
- [X] T056 [P] [US3] Create contract test for target selection prompt in tests/contract/test_merge_contract.py
- [X] T057 [US3] Create contract test for user input validation (valid/invalid options) in tests/contract/test_merge_contract.py
- [X] T058 [US3] Create contract test for Ctrl+C cancellation during prompt in tests/contract/test_merge_contract.py

### Implementation for User Story 3

- [X] T059 [US3] Extend MergeFoldersService.get_target_folder() to detect mixed-case variants in src/cli/services/merge_service.py
- [X] T060 [US3] Add user choice prompt function in merge_cmd() in src/cli/commands/system/merge_cmd.py (Rich numbered options)
- [X] T061 [US3] Implement prompt validation (reject invalid options, re-prompt on error) in merge_cmd()
- [X] T062 [US3] Handle Ctrl+C gracefully (exit cleanly without modifying files) in merge_cmd()
- [X] T063 [US3] Update MergeResult to track user-selected vs auto-selected targets in src/cli/models/merge_result.py (or dataclass)
- [X] T064 [US3] Update merge summary display to show which target was chosen in merge_cmd()

### Acceptance Criteria Validation

- [X] T065 [US3] Verify prompt appears when neither variant is all lowercase
- [X] T066 [US3] Verify user can select any variant as target
- [X] T067 [US3] Verify merge respects user's target choice
- [X] T068 [US3] Verify Ctrl+C cancels without modifying files
- [X] T069 [US3] Run scenario tests from quickstart.md: Scenario 7 (Multiple duplicate groups with choices)

**Checkpoint**: User Stories 1, 2, & 3 complete. Users can manually select merge targets for mixed-case duplicates.

---

## Phase 6: User Story 4 - Preview Merge Impact Before Committing (Priority: P2)

**Goal**: Let users see exactly what will happen during merge (files affected, space impact) before confirming the operation. Gives confidence and allows identifying issues before data is moved.

**Independent Test**: Can be fully tested by running merge command, reviewing preview output, then canceling and verifying no changes occurred.

**Dependencies**: User Stories 1, 2, & 3 should be complete (but can work independently once Phase 2 foundation is done)

### Tests for User Story 4 (TDD - Write FIRST)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T070 [P] [US4] Create unit test for merge preview calculation in tests/unit/test_merge_service.py (file counts, sizes, conflicts)
- [X] T070a [P] [US4] Create unit test for file size estimation in tests/unit/test_merge_service.py
- [X] T071 [P] [US4] Create integration test for preview workflow in tests/integration/test_merge_workflows.py (preview without execution)
- [X] T072 [P] [US4] Create contract test for --preview flag in tests/contract/test_merge_contract.py
- [X] T073 [US4] Create contract test for preview display format in tests/contract/test_merge_contract.py (verify output components)
- [X] T074 [US4] Create contract test for preview mode (no file modifications) in tests/contract/test_merge_contract.py

### Implementation for User Story 4

- [X] T075 [US4] Verify MergeFoldersService.preview_merge() is fully implemented in src/cli/services/merge_service.py (exists from Phase 1)
- [X] T076 [US4] Enhance preview to calculate estimated disk space impact in merge_service.py
- [X] T077 [US4] Update merge_cmd() to display detailed preview panel before confirmation in src/cli/commands/system/merge_cmd.py
- [X] T078 [US4] Add preview panel formatting with Rich (source, target, file count, size estimate) in merge_cmd()
- [X] T079 [US4] Ensure --preview flag skips merge execution (display only) in merge_cmd()
- [X] T080 [US4] Add "Preview mode: no changes were made" confirmation message in merge_cmd()

### Acceptance Criteria Validation

- [X] T081 [US4] Verify preview shows source folder path
- [X] T082 [US4] Verify preview shows target folder path  
- [X] T083 [US4] Verify preview shows number of files to move
- [X] T084 [US4] Verify preview shows estimated disk impact
- [X] T085 [US4] Verify --preview flag prevents any file modifications
- [X] T086 [US4] Verify preview can be canceled without changes
- [X] T087 [US4] Run scenario tests from quickstart.md: Scenario 1 (Preview mode - verified)

**Checkpoint**: User Stories 1, 2, 3, & 4 complete. Users have full visibility into merge impact before confirming.

---

## Phase 7: User Story 5 - Handle File Conflicts Between Duplicates (Priority: P3)

**Goal**: Detect and handle conflicts gracefully when duplicate folders have files with same names. Prevents accidental data loss.

**Independent Test**: Can be fully tested by creating duplicate folders with same-named files, attempting merge, and verifying conflict handling behavior.

**Dependencies**: User Stories 1 & 2 should be complete (conflict handling builds on merge foundation)

### Tests for User Story 5 (TDD - Write FIRST)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T088 [P] [US5] Create unit test for conflict detection in tests/unit/test_merge_service.py (identify same-named files in both folders)
- [X] T089 [P] [US5] Create unit test for conflict resolution options in tests/unit/test_merge_service.py (skip, rename, overwrite)
- [X] T090 [P] [US5] Create integration test for merge with conflicts in tests/integration/test_merge_workflows.py (full workflow with conflict handling)
- [X] T091 [P] [US5] Create contract test for conflict warning in tests/contract/test_merge_contract.py
- [X] T092 [US5] Create contract test for conflict resolution prompt in tests/contract/test_merge_contract.py
- [X] T093 [US5] Create contract test for file preservation (no silent overwrites) in tests/contract/test_merge_contract.py

### Implementation for User Story 5

- [X] T094 [US5] Extend MergeOperation to track conflicts in src/cli/models/merge_operation.py (or dataclass)
- [X] T095 [US5] Implement conflict detection in MergeFoldersService.preview_merge() in src/cli/services/merge_service.py
- [X] T096 [US5] Add conflict warning display in merge_cmd() when conflicts detected in src/cli/commands/system/merge_cmd.py
- [X] T097 [US5] Implement conflict resolution prompt in merge_cmd() with options: keep target, rename source, cancel
- [X] T098 [US5] Add ConflictResolution data structure in src/cli/models/ to track resolution choices
- [X] T099 [US5] Implement file renaming logic in MergeFoldersService (e.g., rename source file to avoid collision) in src/cli/services/merge_service.py
- [X] T100 [US5] Update MergeFoldersService.execute_merge() to apply conflict resolutions in src/cli/services/merge_service.py
- [X] T101 [US5] Add conflict resolution to merge summary display in merge_cmd()
- [X] T102 [US5] Add logging for conflict detection and resolution in merge_service.py

### Acceptance Criteria Validation

- [X] T103 [US5] Verify conflicts are detected before merge
- [X] T104 [US5] Verify conflict warning is displayed to user
- [X] T105 [US5] Verify user can choose to keep target version (skip source file)
- [X] T106 [US5] Verify user can choose to rename source file (preserve both)
- [X] T107 [US5] Verify user can cancel merge due to conflicts
- [X] T108 [US5] Verify no silent overwrites (target protected by default)
- [X] T109 [US5] Verify merged summary shows conflicts resolved/unresolved
- [X] T110 [US5] Run scenario tests from quickstart.md: Scenario 8 (Deeply nested duplicates with potential conflicts)

**Checkpoint**: User Stories 1-5 complete. Full merge workflow with conflict handling is implemented.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, documentation, and release preparation

**Dependencies**: All user stories (US1-US5) should be substantially complete

### Code Quality & Maintainability

- [X] T111 [P] Review all service methods in src/cli/services/merge_service.py for code quality, docstrings, type hints
- [X] T112 [P] Review all CLI code in src/cli/commands/system/merge_cmd.py for clarity, error handling, user experience
- [X] T113 [P] Verify all custom exceptions are properly defined in src/cli/exceptions.py with clear messages
- [X] T114 [P] Refactor any complex functions >50 lines for readability in merge_service.py and merge_cmd.py
- [X] T115 [P] Add comprehensive docstrings (Google style) to all public methods

### Testing & Coverage

- [X] T116 [P] Run full test suite: `pytest tests/ -v --tb=short` and verify all tests pass
- [X] T117 [P] Generate coverage report: `pytest --cov=src/cli/services/merge_service --cov=src/cli/commands/system/merge_cmd --cov-report=html`
- [X] T118 [P] Verify minimum 80% code coverage for merge functionality
- [X] T119 [P] Add edge case tests (symlinks, special characters, deep nesting) in tests/ if not already covered
- [X] T120 [P] Run performance tests from tests/performance/test_merge_perf.py and verify all targets met

### Documentation

- [X] T121 [P] Update quickstart.md with complete walkthrough of all 8 scenarios
- [X] T122 [P] Update specifications in contracts/cli-merge-folders.md if any changes were made
- [X] T123 [P] Create or update TROUBLESHOOTING.md in specs/003-merge-duplicate-folders/ with common issues and solutions
- [X] T124 [P] Add inline code comments for complex logic in merge_service.py and merge_cmd.py
- [X] T125 Verify all error messages in merge_cmd.py match contracts/cli-merge-folders.md specification

### Linting & Formatting

- [X] T126 [P] Run ruff check on all modified files: `ruff check src/cli/services/merge_service.py src/cli/commands/system/ --config pyproject.toml`
- [X] T127 [P] Run ruff format (if configured): `ruff format src/cli/`
- [X] T128 [P] Verify type hints with mypy (if available): `mypy src/cli/services/merge_service.py`

### Integration Testing

- [X] T129 [P] Test full merge workflow end-to-end with real directory structure
- [X] T130 [P] Test merge with real permission scenarios (read-only folders, etc.)
- [X] T131 [P] Test merge with special characters in folder names
- [X] T132 [P] Test merge with symlinks and junctions (per specification assumptions)
- [X] T133 Validate all scenarios from quickstart.md run without errors

### Performance Validation

- [X] T134 [P] Benchmark: Scan 1000+ folders - verify <10s target
- [X] T135 [P] Benchmark: Merge 100+ files - verify <30s target
- [X] T136 [P] Benchmark: Deep nesting (10+ levels) - verify fast traversal
- [X] T137 [P] Benchmark: Full workflow 10 groups - verify <3 min total

### Final Checklist

- [X] T138 [P] Verify all 183+ tests pass
- [X] T139 [P] Verify zero linting errors (ruff)
- [X] T140 [P] Verify minimum 80% coverage
- [X] T141 [P] Verify all performance targets met
- [X] T142 [P] Verify no stack traces shown to users (graceful error handling)
- [X] T143 [P] Verify all user scenarios from quickstart.md work
- [ ] T144 Create final test report with all metrics
- [ ] T145 Create changelog/release notes for feature

**Checkpoint**: Feature is polished, tested, documented, and ready for code review.

---

## Final Step: Code Review & Release

- [ ] T146 Submit code review on GitHub (PR to main branch)
- [ ] T147 Address any review feedback
- [ ] T148 Verify all CI/CD checks pass (tests, linting)
- [ ] T149 Merge PR to main when approved
- [ ] T150 Tag release version (e.g., v1.0-003-merge-folders)

**Final Status**: ✅ Feature complete and merged to main branch

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ COMPLETE - Foundation already in place
- **Foundational (Phase 2)**: Must complete first - validates Phase 1, sets up error handling and performance testing
- **User Stories (Phase 3+)**: Can proceed in parallel after Foundational:
  - US1 (Discovery): ✅ COMPLETE - validation only
  - US2 (Automatic merge): Next priority - builds on US1
  - US3 (User choice): Can follow US2 or work in parallel
  - US4 (Preview): Can work in parallel with US2-US3
  - US5 (Conflict handling): Last priority - depends on US1-US2
- **Polish (Phase 8)**: Final phase - after all stories substantially complete

### Parallel Opportunities (After Phase 2 Foundational)

**Developer 1 - User Story 2 (Automatic Merge)**:
- T030-T037: Write and implement automatic merge
- Depends on: Phase 2 foundation

**Developer 2 - User Story 3 & 4 (User Choice + Preview)**:
- T053-T080: Write tests and implement choice/preview features
- Depends on: Phase 2 foundation (can work with US2 in progress)

**Developer 3 - User Story 5 (Conflict Handling)**:
- T088-T102: Write tests and implement conflict detection/resolution
- Depends on: US1-US2 mostly complete

**All Developers - Polish (Phase 8)**:
- T111-T145: Run quality checks, tests, documentation, code review
- Can start once US2 is done (don't wait for US3-US5 if time is critical)

### Within Each User Story

1. **Write Tests First (TDD)**:
   - Create test file with failing tests
   - Tests capture requirements from acceptance scenarios
   - All tests must fail before implementation

2. **Implement Model/Entity Changes**:
   - Extend data classes if needed
   - Add validation rules
   - Update type hints

3. **Implement Service Layer Logic**:
   - MergeFoldersService methods
   - Core business logic
   - Error handling

4. **Implement CLI Layer**:
   - merge_cmd() prompts and display
   - User interaction
   - Error message translation

5. **Verify Tests Pass**:
   - Run entire test suite
   - Check coverage
   - Verify acceptance criteria

---

## Implementation Strategy

### MVP First (Recommended)

✅ Phase 1 (Discovery) - COMPLETE
→ Phase 2 (Foundational) - Validation + Error Handling - **START HERE**
→ Phase 3 (US1 Validation) - Verify P1-001 is correct
→ Phase 4 (US2 Automatic Merge) - **First new feature to implement**
→ STOP and VALIDATE - Test US2 independently before shipping
→ Deploy/Demo if satisfied with automatic merge feature

### Incremental Delivery (Full Feature)

1. **Weeks 1-2**: Phase 2 Foundational (validation, error handling)
2. **Weeks 2-3**: Phase 4 US2 (automatic merge implementation)
3. **Weeks 3-4**: Phase 5 US3 + Phase 6 US4 (user choice + preview) - can work in parallel
4. **Weeks 4-5**: Phase 7 US5 (conflict handling)
5. **Weeks 5-6**: Phase 8 Polish (code review, docs, release prep)

### Parallel Team Strategy (Recommended)

With 3 developers:

1. **All Together**: Complete Phase 2 Foundational (2-3 days)
2. **Split Up**:
   - Developer 1: Phase 4 US2 (automatic merge)
   - Developer 2: Phase 5-6 US3+US4 (user choice + preview)
   - Developer 3: Phase 7 US5 (conflict handling)
3. **Together Again**: Phase 8 Polish (1 week) + Code Review + Release

---

## Task Counts & Metrics

### By Phase

| Phase | Tasks | Tests | Status |
|-------|-------|-------|--------|
| Phase 1 (Setup) | 9 | - | ✅ Complete |
| Phase 2 (Foundational) | 12 | 8 | ⏳ Next |
| Phase 3 (US1 Validation) | 8 | 4 | ⏳ After P2 |
| Phase 4 (US2 Merge) | 18 | 7 | ⏳ After US1 |
| Phase 5 (US3 Choice) | 15 | 6 | ⏳ After US2 |
| Phase 6 (US4 Preview) | 11 | 6 | ⏳ After US3 |
| Phase 7 (US5 Conflicts) | 19 | 6 | ⏳ After US2 |
| Phase 8 (Polish) | 35 | - | ⏳ Last |
| **TOTAL** | **150+** | **37+** | **Ready** |

### By User Story

| Story | Title | Priority | Tasks | Tests | Parallel? |
|-------|-------|----------|-------|-------|-----------|
| US1 | Discover Duplicates | P1 | 8 | 4 | ✅ Validation |
| US2 | Automatic Merge | P1 | 18 | 7 | ✅ Yes (TDD first) |
| US3 | User Chooses | P2 | 15 | 6 | ✅ Yes (with US2) |
| US4 | Preview Impact | P2 | 11 | 6 | ✅ Yes (with US2-US3) |
| US5 | Handle Conflicts | P3 | 19 | 6 | ⏳ After US2 |

### Key Milestones

- ✅ T001-T009: Phase 1 Setup Complete
- ⏳ T010-T021: Phase 2 Foundational (Next: START HERE)
- ⏳ T022-T029: US1 Validation
- ⏳ T030-T052: US2 Implementation (Parallel start after US1)
- ⏳ T053-T087: US3 Implementation (Can start with US2)
- ⏳ T070-T087: US4 Implementation (Can start with US3)
- ⏳ T088-T110: US5 Implementation (After US2)
- ⏳ T111-T145: Polish & Release
- ⏳ T146-T150: Code Review & Merge

---

## Success Criteria Per User Story

### US1 - Discovery (✅ COMPLETE)
- [ ] All 1000+ folder scan completes <10s
- [ ] All case-insensitive duplicates identified correctly
- [ ] Duplicate groups displayed with full paths
- [ ] No filesystem modifications

### US2 - Automatic Merge (⏳ NEXT)
- [ ] Lowercase variant auto-selected as target
- [ ] All files transferred to target
- [ ] Source folder deleted after merge
- [ ] Merge operates atomically (no partial transfers)
- [ ] 100+ file merge completes <30s
- [ ] User confirmation required (unless --force)

### US3 - User Choice (⏳ NEXT)
- [ ] Prompt appears when no lowercase variant exists
- [ ] User can select any variant as target
- [ ] Merge respects user's choice
- [ ] Ctrl+C cancels without filesystem changes

### US4 - Preview (⏳ NEXT)
- [ ] Preview shows source, target, file count, size impact
- [ ] --preview flag prevents any modifications
- [ ] Preview can be reviewed and canceled

### US5 - Conflict Handling (⏳ NEXT)
- [ ] Conflicts detected before merge
- [ ] User warned about conflicts
- [ ] User can choose resolution (keep, rename, cancel)
- [ ] No silent overwrites

---

## Notes

- Tests marked [P] can run in parallel (different files, no order dependencies)
- [Story] labels map tasks to specific user stories for traceability
- Each user story should be independently completable and testable
- Verify tests FAIL before implementing (TDD discipline)
- Commit after each task or logical group for clean history
- Stop at any checkpoint to validate story independently
- Phase 2 MUST complete before any user story work begins (it's blocking)
- Phase 1 is already done - don't redo those tasks
