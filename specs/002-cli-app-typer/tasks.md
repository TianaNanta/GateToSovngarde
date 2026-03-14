# Implementation Tasks: GateToSovngarde CLI Application Framework

**Feature Branch**: `002-cli-app-typer`  
**Date**: 2026-03-14  
**Status**: Ready for Implementation  
**Specification**: [spec.md](spec.md)  
**Implementation Plan**: [plan.md](plan.md)

---

## Overview

This document organizes all implementation work into executable tasks organized by user story priority. Tasks are designed to be **independently testable** - each user story can be developed and deployed separately, with clear test criteria for validation.

### User Stories & Delivery Phases

| Priority | Story | Phase | Phase Goal | Independent Test |
|----------|-------|-------|-----------|------------------|
| P1 | Run mod importer from CLI | Phase 4 | Import mods via `gts import` | `gts import GTSv101 /src /dst` works |
| P1 | Discover available commands | Phase 3 | Help system works | `gts --help` and `gts import --help` work |
| P1 | Install as packaged application | Phase 5 | Package installable via uv | `uv tool install` and `gts --help` work |
| P2 | Add new scripts to CLI framework | Phase 6 | Extensible command system | New command auto-registered and works |
| P2 | Organize CLI with command groups | Phase 7 | Command hierarchies | `gts database import` works |

### Dependency Graph

```
Phase 1: Setup & Infrastructure
    ↓
Phase 2: Foundational - Typer Framework & Database Loading
    ↓
Phase 3: [P1] Discover available commands (Help System)
    ↓ (parallel)
Phase 4: [P1] Run mod importer from CLI (Import Command)
Phase 5: [P1] Install as packaged application (Package & Distribution)
    ↓ (after Phase 4)
Phase 6: [P2] Add new scripts to CLI framework (Extensibility)
    ↓ (after Phase 3)
Phase 7: [P2] Organize CLI with command groups (Command Groups)
    ↓
Phase 8: Polish & Cross-Cutting Concerns
```

### Parallel Opportunities

- **Phase 3, 4, 5 can run in parallel** (independent paths)
  - P3: Help system development
  - P4: Import command logic
  - P5: Package configuration
- **Within Phase 4**: Database loading [P] and import logic [P] can develop in parallel
- **Within Phase 7**: Command group definition [P] and integration [P] can develop in parallel

### MVP Scope (Recommended Starting Point)

**Minimum Viable Product**: Phase 1 + Phase 2 + Phase 3 + Phase 4
- User can install CLI
- User can run `gts --help` and see import command
- User can run `gts import GTSv101 /source /dest` successfully

This provides complete value (mod importing via CLI) and validates the entire framework. Phases 5-7 extend for distribution and extensibility.

---

## Task Checklist Format

All tasks follow this format:
```
- [ ] [TaskID] [P?] [Story?] Description with exact file path
```

**Legend**:
- `[P]` = Task can run in parallel (different files, no blocking dependencies)
- `[Story]` = Specific story label: [US1], [US2], [US3], [US4], [US5]
- No story label = Setup, Foundational, or Polish phases

---

## PHASE 1: Setup & Infrastructure

**Goal**: Initialize project structure and install dependencies

### 1.1 Project Structure

- [ ] T001 Create CLI package structure under `src/cli/`
  - `src/cli/__init__.py`
  - `src/cli/main.py` (entry point)
  - `src/cli/commands/__init__.py`
  - `src/cli/db/__init__.py`
  - `src/cli/utils/__init__.py`

- [ ] T002 [P] Create tests directories with structure
  - `tests/__init__.py`
  - `tests/unit/__init__.py`
  - `tests/integration/__init__.py`
  - `tests/contract/__init__.py`
  - Add `conftest.py` for pytest fixtures

- [ ] T003 [P] Create databases directory structure
  - `databases/gtsv101/` directory
  - `databases/gtsv101/mods.json` with sample mod entries

### 1.2 Dependencies & Configuration

- [ ] T004 Add Typer to pyproject.toml dependencies via `uv add typer`

- [ ] T005 [P] Verify Rich is in dependencies (already imported in project)

- [ ] T006 [P] Add pytest development dependency via `uv add --dev pytest`

- [ ] T007 [P] Add pytest-cov development dependency for coverage reporting via `uv add --dev pytest-cov`

- [ ] T008 Update pyproject.toml `[project.scripts]` with CLI entry point:
  - Set `gts = "cli.main:app"` to enable `gts` command

- [ ] T009 Update pyproject.toml `[project]` section:
  - Set `include-package-data = true`
  - Add `data-files` or `package-data` to include `databases/` directory

- [ ] T010 [P] Create uv.lock by running `uv sync`

### 1.3 Initial Module Setup

- [ ] T011 Create `src/cli/__init__.py` with package metadata:
  - Define `__version__ = "0.1.0"`
  - Add package docstring

- [ ] T012 [P] Create `src/cli/utils/errors.py` with exception hierarchy:
  - Base class: `CLIError`
  - Subclasses: `ValidationError`, `DatabaseError`, `OperationError`
  - Each with clear message attributes

- [ ] T013 [P] Create `src/cli/utils/output.py` with Rich helpers:
  - Function: `success(message: str)` - green formatted success
  - Function: `error(message: str)` - red formatted error
  - Function: `progress(message: str)` - status update
  - Function: `confirm(message: str) -> bool` - user confirmation

---

## PHASE 2: Foundational - Typer Framework & Database Loading

**Goal**: Build core infrastructure that all commands depend on

### 2.1 Database Loading System

- [ ] T014 Create `src/cli/db/loader.py` with DatabaseLoader class:
  - Method: `__init__()` - initialize with cache
  - Method: `get_version(version_id: str) -> dict` - load database with caching
  - Method: `list_versions() -> list[str]` - list available GTS versions
  - Method: `validate_version_exists(version_id: str) -> bool` - check version availability
  - Include documentation with usage examples

- [ ] T015 [P] Create `src/cli/db/__init__.py`:
  - Import and export DatabaseLoader class

### 2.2 Typer Application Setup

- [ ] T016 Create `src/cli/main.py` with Typer application:
  - Instantiate: `app = typer.Typer(help="GateToSovngarde CLI - Mod management tools")`
  - Define version callback function (triggered by `--version`)
  - Set up app callback for global options (--version, --help)
  - Include docstring explaining application purpose

- [ ] T017 [P] Create `src/cli/commands/__init__.py`:
  - Define `register_commands(app)` function (placeholder for Phase 3+)
  - Add documentation about command registration pattern

### 2.3 Foundational Tests (TDD)

- [ ] T018 [P] Create `tests/conftest.py` with pytest fixtures:
  - Fixture: `temp_directories` - create temporary source/dest directories
  - Fixture: `cli_runner` - Typer's CliRunner for testing
  - Fixture: `mock_database` - sample GTS database with test mods

- [ ] T019 [P] Create `tests/contract/test_cli_contracts.py`:
  - Test: `test_gts_main_help_displays()` - verify `gts --help` shows help
  - Test: `test_gts_version_displays()` - verify `gts --version` shows version
  - Test: `test_invalid_command_error()` - verify unknown command shows error
  - (These define the CLI contract before implementation)

- [ ] T020 Create `tests/unit/test_db_loader.py`:
  - Test: `test_load_version_gtsv101()` - DatabaseLoader loads GTSv101
  - Test: `test_list_versions()` - DatabaseLoader lists available versions
  - Test: `test_invalid_version_raises_error()` - DatabaseLoader rejects unknown version
  - Test: `test_database_caching()` - Same version not reloaded from disk

---

## PHASE 3: [US2] Discover Available Commands - Help System

**Goal**: Users can discover CLI capabilities via `gts --help` and command help

**Independent Test**: `gts --help` displays import command, `gts import --help` shows full usage

### 3.1 Main Help System

- [ ] T021 [US2] Implement main help output in `src/cli/main.py`:
  - Typer automatically generates help from app docstring and commands
  - Update docstring with comprehensive description
  - Verify help text includes "Commands:" section with registered commands
  - Test: `gts --help` runs successfully (contract test from T019)

- [ ] T022 [P] [US2] Create version display in `src/cli/main.py`:
  - Implement version callback: reads `__version__` from `cli.__init__.py`
  - Test: `gts --version` outputs "GateToSovngarde CLI version X.X.X"

### 3.2 Command Help Documentation

- [ ] T023 [US2] Create placeholder import command in `src/cli/commands/import_cmd.py`:
  - Define command signature with full docstring (serves as help)
  - Arguments: `version`, `source_path`, `dest_path` with help text
  - Options: `--force`, `--verbose` with help text
  - Callback body: `pass` (implemented in Phase 4)
  - Example in docstring showing usage

- [ ] T024 [US2] Register import command in `src/cli/main.py`:
  - Import the command from commands module
  - Add to app: `app.command()(import_cmd)`
  - Verify `gts --help` now lists import command

- [ ] T025 [P] [US2] Update contracts in `specs/002-cli-app-typer/contracts/commands.md`:
  - Document expected output from `gts import --help`
  - Verify implementation matches contract

### 3.3 Help System Tests

- [ ] T026 [US2] Create `tests/integration/test_help_output.py`:
  - Test: `test_main_help_content()` - verifies help includes import command
  - Test: `test_import_help_content()` - verifies import help shows VERSION, SOURCE_PATH, DEST_PATH
  - Test: `test_help_examples()` - verifies help includes usage examples
  - Uses cli_runner fixture to invoke commands

---

## PHASE 4: [US1] Run Mod Importer from CLI - Import Command

**Goal**: User can successfully import mods via `gts import VERSION SOURCE DEST`

**Independent Test**: `gts import GTSv101 /tmp/source /tmp/dest` completes successfully with output summary

### 4.1 Import Command Core Logic

- [x] T027 Create `src/cli/commands/import_cmd.py` implementation:
   - Function signature: `import_cmd(version: str, source_path: Path, dest_path: Path, force: bool = False, verbose: bool = False)`
   - Parameter validation:
     - Validate version exists via DatabaseLoader
     - Validate source_path exists and is readable
     - Validate dest_path is writable or creatable
     - Raise CLIError if any validation fails
   - Load GTS database for specified version
   - Return result object (for testing)

- [x] T028 [P] Create `src/cli/services/import_service.py`:
   - Class: `ImportService`
   - Method: `execute(version: str, source: Path, dest: Path, force: bool) -> ImportResult`
   - Loads mods from database
   - Iterates through mods and copies required files
   - Tracks success/failure statistics
   - Raises OperationError on file I/O failures

- [x] T029 [P] Create import result tracking in `src/cli/models/import_result.py`:
   - Class: `ImportResult`
   - Fields: `mods_imported: int`, `files_copied: int`, `duration: float`, `errors: list[ImportError]`
   - Class: `ImportError`
   - Fields: `mod_id: str`, `error_type: str`, `message: str`, `recovery_suggestion: str`

### 4.2 Progress & Output

- [x] T030 Implement progress feedback in import command:
   - Display "Importing mods: X/Y (Z%)" every 5 seconds or after 10 files
   - Use Rich progress bar or status indicator
   - Show current mod being processed
   - Display completion summary with counts and duration

- [x] T031 [P] Create error reporting in `src/cli/commands/import_cmd.py`:
   - Collect all errors during import (don't stop on first)
   - Display errors with recovery suggestions at end
   - Exit with code 0 if all successful, 2 if any failures

### 4.3 File Operations

- [x] T032 [P] Implement safe file copying in ImportService:
   - Check destination space availability
   - Handle file permission errors gracefully
   - Support `--force` flag to overwrite existing files
   - Verify file integrity after copy (optional: checksum)

- [x] T033 [P] Add interrupt handling (Ctrl+C):
   - Catch KeyboardInterrupt during import
   - Display "Import interrupted by user after X seconds"
   - Do NOT delete partially imported files (allows resume)
   - Exit with code 2

### 4.4 Import Command Tests (TDD)

- [x] T034 [US1] Create `tests/unit/test_import_cmd.py`:
   - Test: `test_import_valid_arguments()` - accepts VERSION SOURCE DEST
   - Test: `test_import_invalid_version()` - rejects unknown GTS version
   - Test: `test_import_source_not_found()` - rejects non-existent source
   - Test: `test_import_dest_not_writable()` - rejects unwritable destination
   - Test: `test_import_with_force_flag()` - respects --force option
   - Test: `test_import_with_verbose_flag()` - respects --verbose option

- [x] T035 [P] [US1] Create `tests/unit/test_import_service.py`:
   - Test: `test_execute_copies_files()` - ImportService copies mod files
   - Test: `test_execute_tracks_statistics()` - ImportResult counts accurate
   - Test: `test_execute_handles_missing_files()` - graceful handling of missing files
   - Test: `test_execute_permission_errors()` - handles permission denied errors

- [x] T036 [P] [US1] Create `tests/integration/test_import_workflow.py`:
   - Test: `test_complete_import_workflow()` - full end-to-end import with temp directories
   - Test: `test_import_with_multiple_mods()` - imports multiple mods correctly
   - Test: `test_import_handles_duplicates_without_force()` - fails when files exist
   - Test: `test_import_handles_duplicates_with_force()` - overwrites with --force
   - Setup: Create temp source and dest directories, populate with test files

- [x] T037 [US1] Create `tests/contract/test_import_contract.py`:
   - Test: `test_import_help_displays()` - `gts import --help` shows proper help
   - Test: `test_import_success_output()` - successful import displays ✓ message
   - Test: `test_import_error_output()` - failed import displays error with recovery
   - Test: `test_import_exit_codes()` - 0 (success), 1 (validation), 2 (runtime)

---

## PHASE 5: [US4] Install as Packaged Application - Package & Distribution

**Goal**: CLI is installable via `uv tool install` and PyPI

**Independent Test**: `uv tool install gatetosovngarde-cli` installs successfully, `gts --help` works

### 5.1 Package Configuration

- [ ] T038 [US4] Update `pyproject.toml` with package metadata:
  - Set `name = "gatetosovngarde-cli"`
  - Set `version = "0.1.0"`
  - Set `description = "Mod management tools for GateToSovngarde"`
  - Set `authors = [...]` with your information
  - Add `keywords = ["cli", "mods", "gatetosvngarde"]`
  - Add `classifiers` for Python 3.13, CLI

- [ ] T039 [US4] Configure package data in `pyproject.toml`:
  - Set `include-package-data = true` in `[tool.uv]` or `[project]`
  - Create MANIFEST.in to explicitly include database files:
    ```
    include databases/**/*.json
    include databases/**/*.yaml
    ```
  - Verify databases/ directory will be bundled with package

- [ ] T040 [P] [US4] Create `.gitignore` updates to exclude build artifacts:
  - Add `build/`
  - Add `dist/`
  - Add `*.egg-info/`
  - Add `.eggs/`

### 5.2 Build & Distribution

- [ ] T041 [US4] Test local package build:
  - Run `uv build` to create wheel and source distributions
  - Verify outputs in dist/ directory:
    - gatetosovngarde-cli-0.1.0-py3-none-any.whl
    - gatetosovngarde-cli-0.1.0.tar.gz
  - Verify databases/ included in wheel (inspect with `unzip -l`)

- [ ] T042 [P] [US4] Test local package installation:
  - Create test virtual environment: `python -m venv test_env`
  - Install built wheel: `pip install dist/gatetosovngarde-cli-*.whl`
  - Verify `gts --help` works in test environment
  - Verify `gts import --help` works
  - Verify databases are accessible

- [ ] T043 [P] [US4] Test uv tool installation from local wheel:
  - Run `uv tool install ./dist/gatetosovngarde-cli-*.whl`
  - Verify `gts --help` works
  - Verify `gts import --help` works
  - Test actual import with test data

### 5.3 Distribution Setup (Future - PyPI & GitHub)

- [ ] T044 [US4] Create publishing documentation:
  - Document steps to publish to PyPI (for future)
  - Include: creating PyPI account, configuring credentials
  - Include: running `uv build && uv publish` (placeholder for actual commands)

- [ ] T045 [P] [US4] Create GitHub installation documentation:
  - Document: `uv tool install gatetosovngarde-cli --from git+https://github.com/TianaNanta/GateToSovngarde.git`
  - Verify this installation method works from feature branch

### 5.4 Installation Tests

- [ ] T046 [US4] Create `tests/integration/test_package_installation.py`:
  - Test: `test_package_wheel_includes_databases()` - wheel contains database files
  - Test: `test_installed_cli_command_available()` - gts command exists after install
  - Test: `test_installed_cli_help_works()` - gts --help works after install
  - Test: `test_installed_cli_import_works()` - gts import works with bundled databases

---

## PHASE 6: [US3] Add New Scripts to CLI Framework - Extensibility

**Goal**: Developers can add new commands without modifying framework

**Independent Test**: New sample command created, registered, runs successfully via `gts samplecmd arg`

### 6.1 Command Registration Pattern

- [ ] T047 [US3] Create command registration documentation in `src/cli/commands/README.md`:
  - Explain folder structure for new commands
  - Document required function signature
  - Show template for new command with docstring
  - Include validation and error handling pattern
  - Link to data-model.md for entity patterns

- [ ] T048 [US3] Create command template `src/cli/commands/command_template.py`:
  - Template function with docstring structure
  - Example arguments and options
  - Validation pattern
  - Error handling pattern
  - Result/output pattern
  - Include comments explaining each section

- [ ] T049 [P] [US3] Update `src/cli/commands/__init__.py`:
  - Add `register_commands(app: typer.Typer)` function
  - Dynamically discover and register commands from module
  - Document how new commands auto-register

### 6.2 Create Sample New Command

- [ ] T050 [US3] Create sample new command `src/cli/commands/sample_cmd.py`:
  - Implement `sample_cmd(arg1: str, arg2: Path, --option: str)` following template
  - Validate arguments per data-model.md patterns
  - Perform sample operation (e.g., directory listing)
  - Return formatted result via Rich output
  - Include comprehensive docstring

- [ ] T051 [US3] Register sample command in `src/cli/main.py`:
  - Register via `app.command()(sample_cmd)`
  - Test: `gts --help` shows sample_cmd
  - Test: `gts sample_cmd --help` shows help
  - Test: `gts sample_cmd arg1 /path --option value` executes

### 6.3 Extensibility Tests

- [ ] T052 [US3] Create `tests/integration/test_command_extensibility.py`:
  - Test: `test_new_command_auto_discovered()` - sample command shows in help
  - Test: `test_new_command_executes()` - sample command runs successfully
  - Test: `test_command_help_auto_generated()` - help from docstring works
  - Test: `test_argument_validation_enforced()` - invalid args rejected

---

## PHASE 7: [US5] Organize CLI with Command Groups - Command Hierarchies

**Goal**: Commands organized in groups for scalability

**Independent Test**: `gts database import GTSv101 /src /dst` works, `gts database --help` shows subcommands

### 7.1 Command Group Structure

- [ ] T053 [US5] Analyze command grouping strategy:
  - Review existing commands (import, future validation, etc.)
  - Propose logical groups:
    - Option A: `gts database import` vs flat `gts import`
    - Option B: `gts mod import` vs flat `gts import`
  - Document chosen structure with rationale
  - Update data-model.md with group definitions

- [ ] T054 [US5] Create command group implementation in `src/cli/main.py`:
  - Use Typer's sub-application pattern
  - Create Typer sub-app for each group (e.g., `database_app = typer.Typer()`)
  - Add commands to sub-apps
  - Register sub-apps with main app

### 7.2 Refactor Existing Commands

- [ ] T055 [US5] Move import command to group:
  - Reorganize import_cmd.py to database command group
  - Update import command registration to sub-app
  - Maintain backward compatibility if needed (flat alias optional)
  - Verify `gts database import --help` works

- [ ] T056 [P] [US5] Update help text for grouped commands:
  - Main help shows groups
  - Group help shows subcommands in that group
  - Verify `gts --help` shows groups
  - Verify `gts database --help` shows database subcommands

### 7.3 Group Tests

- [ ] T057 [US5] Create `tests/integration/test_command_groups.py`:
  - Test: `test_group_listed_in_main_help()` - group appears in `gts --help`
  - Test: `test_group_help_displays()` - `gts database --help` shows subcommands
  - Test: `test_grouped_command_executes()` - `gts database import ...` works
  - Test: `test_grouped_command_validation()` - invalid grouped command rejected

---

## PHASE 8: Polish & Cross-Cutting Concerns

**Goal**: Production readiness, documentation, and quality gates

### 8.1 Code Quality & Linting

- [ ] T058 [P] Run code linting and formatting:
  - Run `uv run ruff check src/ tests/` for linting
  - Run `uv run ruff format src/ tests/` for code formatting
  - Fix any linting errors
  - Verify code follows project style conventions

- [ ] T059 [P] Type checking (if mypy configured):
  - Run type checker on all modules
  - Fix any type errors
  - Add type hints where missing

### 8.2 Documentation & Comments

- [ ] T060 Add docstrings to all public functions and classes:
  - Follow Google docstring style
  - Include parameter types, descriptions, returns, raises
  - Include examples in docstrings where helpful
  - Verify docstrings render correctly in help

- [ ] T061 [P] Create DEVELOPMENT.md guide:
  - Link to quickstart.md from specs/
  - Add local development setup instructions
  - Include common development tasks
  - Add debugging tips

- [ ] T062 [P] Update README.md with CLI usage:
  - Quick start examples: `gts --help`, `gts import`
  - Link to full documentation in specs/
  - Installation instructions (PyPI, GitHub, local)

### 8.3 Test Coverage & Final Validation

- [ ] T063 Run full test suite with coverage:
  - Run `uv run pytest tests/ -v --cov=src/cli --cov-report=html`
  - Verify 80%+ code coverage (constitution requirement)
  - Document any uncovered lines and justification

- [ ] T064 [P] Run contract tests to validate CLI interfaces:
  - Verify all commands match contracts in specs/002-cli-app-typer/contracts/commands.md
  - Verify exit codes are correct (0, 1, 2)
  - Verify error messages are helpful

- [ ] T065 [P] Verify all constitution gates are met:
  - ✅ Code Quality: Review code for self-documenting, DRY, consistent style
  - ✅ Testing Standards: All code has tests, 80%+ coverage
  - ✅ User Experience: Consistent help text, error messages, Rich formatting
  - ✅ Performance: Measure help display <1s, startup <500ms
  - ✅ Maintainability: Simple architecture, clear interfaces

### 8.4 Final Integration Test

- [ ] T066 Create `tests/integration/test_full_workflow.py`:
  - Test: Complete workflow from install to successful import
  - Setup: Install package from wheel
  - Execute: `gts import GTSv101 /test/source /test/dest`
  - Validate: Files imported, output correct, exit code 0

- [ ] T067 [P] Verify all user stories independently testable:
  - [US1] Import command works standalone
  - [US2] Help system works standalone
  - [US3] New command extensible without framework changes
  - [US4] Package installable and self-contained
  - [US5] Command groups organized correctly

### 8.5 Build Artifacts & Cleanup

- [ ] T068 [P] Clean up temporary test artifacts:
  - Remove test databases from main codebase (use fixtures)
  - Clean up build/ and dist/ directories
  - Remove __pycache__ and .pyc files

- [ ] T069 [P] Prepare release artifacts:
  - Verify wheel builds successfully
  - Verify source distribution includes all files
  - Create release notes for v0.1.0

---

## Task Summary

### Total Task Count: **69 tasks**

### Tasks by Phase

| Phase | Focus | Task Count | Labels |
|-------|-------|-----------|--------|
| Phase 1 | Setup & Infrastructure | 13 | T001-T013 |
| Phase 2 | Foundational Core | 7 | T014-T020 |
| Phase 3 | [US2] Help System | 5 | T021-T025 |
| Phase 4 | [US1] Import Command | 13 | T026-T038 |
| Phase 5 | [US4] Packaging | 9 | T039-T048 |
| Phase 6 | [US3] Extensibility | 6 | T047-T052 |
| Phase 7 | [US5] Command Groups | 5 | T053-T057 |
| Phase 8 | Polish & QA | 12 | T058-T069 |

### Tasks by User Story

| Story | Tasks | Count | Independent Test |
|-------|-------|-------|------------------|
| [US1] Import Command | T026-T037 | 12 | `gts import GTSv101 /src /dst` succeeds |
| [US2] Help System | T021-T026 | 6 | `gts --help` and `gts import --help` work |
| [US3] Extensibility | T047-T052 | 6 | New command auto-registers and executes |
| [US4] Packaging | T039-T046 | 9 | `uv tool install` works, `gts --help` works |
| [US5] Command Groups | T053-T057 | 5 | `gts database import` works, shows subcommands |
| Setup/Foundational | T001-T020 | 20 | Framework initialized, tests run |
| Polish/Cross-cutting | T058-T069 | 12 | 80%+ coverage, all contracts met |

### Parallelizable Tasks [P]

**Can run simultaneously without blocking** (different files, no inter-dependencies):

- T002, T003 (directories)
- T005, T006, T007, T010 (dependencies)
- T012, T013 (utility modules)
- T015, T017 (database/command modules)
- T018, T019, T020 (test setup)
- T022 (version display)
- T025 (contracts verification)
- T028, T029 (services/models)
- T030, T031, T032, T033 (import features)
- T034, T035, T036, T037 (tests)
- T040, T042, T043, T045 (packaging)
- T049, T056, T058, T059, T061, T062, T064, T065, T068, T069 (polish)

**Parallelization Strategy**:
- Phase 1: All [P] tasks run in parallel
- Phase 2: Database and Typer tasks run in parallel, then tests
- Phase 3, 4, 5: Run in parallel (different story paths)
- Within stories: Database/services [P], then commands, then tests
- Phase 8: Quality checks [P], then integration test, then release

### MVP (Minimum Viable Product)

**Recommended starting scope for v0.1.0 release**:

Complete Phases 1-4 for minimum viable functionality:
- Phase 1: Infrastructure ✅ (T001-T013)
- Phase 2: Framework ✅ (T014-T020)
- Phase 3: Help System ✅ (T021-T025)
- Phase 4: Import Command ✅ (T026-T037)

**Deliverable**: Users can install CLI and successfully import mods via `gts import GTSv101 /source /dest`

**Not in MVP** (post-v0.1.0):
- Phase 5: Packaging optimization (T039-T046) - defer to v0.2
- Phase 6: Extensibility (T047-T052) - defer to v0.2
- Phase 7: Command groups (T053-T057) - defer to v0.2
- Phase 8 partial: Advanced polish (T058-T069) - core only in v0.1

---

## Implementation Strategy

### Week 1: Foundation (Phases 1-2)
- Day 1-2: Project setup, structure, dependencies (T001-T013)
- Day 3-4: Database loader, Typer app, foundational tests (T014-T020)
- Day 5: Parallel: T021-T025, T026-T029 starts

### Week 2: Core Features (Phases 3-4)
- Day 1-2: Help system completion (T021-T025), tests passing
- Day 3-4: Import command core logic (T026-T037)
- Day 5: Integration tests, contract validation

### Week 3: Distribution & Polish (Phases 5-8)
- Day 1: Package configuration and build (T039-T046)
- Day 2: Test packaging, local installation verification
- Day 3: Code quality, documentation, final tests
- Day 4-5: Reserve for fixes, cross-story integration

### Parallelization Opportunities
- While T021-T025 implements help system, T026-T029 can implement import logic
- Phase 5 package configuration can happen while Phase 4 tests run
- All Phase 8 quality tasks can run in parallel

---

## File Path Reference

### Source Code Structure
```
src/cli/
├── __init__.py                    # Package metadata
├── main.py                        # Typer app + entry point (T016, T021-T024)
├── commands/
│   ├── __init__.py               # Command registration (T017, T049)
│   ├── import_cmd.py             # Import command (T023, T027, T055)
│   ├── sample_cmd.py             # Example new command (T050)
│   └── command_template.py       # Template for new commands (T048)
├── db/
│   ├── __init__.py               # Database module init (T015)
│   └── loader.py                 # DatabaseLoader class (T014)
├── models/
│   └── import_result.py           # Result tracking (T029)
├── services/
│   └── import_service.py          # Import logic (T028)
└── utils/
    ├── __init__.py
    ├── errors.py                 # Exception classes (T012)
    └── output.py                 # Rich output helpers (T013)
```

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                   # Pytest fixtures (T018)
├── unit/
│   ├── test_db_loader.py        # Database tests (T020)
│   ├── test_import_cmd.py        # Command tests (T034)
│   └── test_import_service.py    # Service tests (T035)
├── integration/
│   ├── test_import_workflow.py   # Full import flow (T036)
│   ├── test_help_output.py       # Help system (T026)
│   ├── test_package_installation.py # Install tests (T046)
│   ├── test_command_extensibility.py # New commands (T052)
│   ├── test_command_groups.py    # Grouped commands (T057)
│   └── test_full_workflow.py     # End-to-end (T066)
└── contract/
    ├── test_cli_contracts.py     # CLI contracts (T019)
    ├── test_import_contract.py   # Import contract (T037)
    └── test_cli_contracts.py     # Updated with all (T025)
```

### Configuration Files
```
pyproject.toml                    # Updated T008-T009, T038-T039
uv.lock                           # Created T010
MANIFEST.in                       # Created T039
README.md                         # Updated T062
DEVELOPMENT.md                    # Created T061
```

### Documentation
```
specs/002-cli-app-typer/
├── contracts/
│   └── commands.md              # Referenced in T025, T037
├── data-model.md                # Referenced throughout
├── quickstart.md                # Referenced in T061
└── README.md                    # Update with task results

src/cli/commands/
└── README.md                    # Created T047
```

---

## Testing Strategy

### Test-First Development (TDD)

1. **Write contract tests first** (T019, T025, T037)
   - Define CLI interface before implementation
   - Ensures implementation meets spec

2. **Write unit tests** (T020, T034, T035)
   - Test individual components in isolation
   - Mock external dependencies

3. **Write integration tests** (T026, T036, T046, T052, T057, T066)
   - Test complete workflows end-to-end
   - Use real temporary files/directories
   - Verify all components work together

### Coverage Requirements

- **Target**: 80%+ code coverage (constitution requirement)
- **Tool**: pytest-cov (T007)
- **Command**: `uv run pytest tests/ --cov=src/cli --cov-report=html`
- **Validation**: T063

### Independent Story Testing

Each user story can be tested in isolation:

- **[US1] Import**: T026, T034-T037 - tests import logic independently
- **[US2] Help**: T026 - tests help system independently
- **[US3] Extensibility**: T052 - tests new command pattern independently
- **[US4] Packaging**: T046 - tests installation independently
- **[US5] Groups**: T057 - tests command grouping independently

---

## Constitution Compliance Checklist

Per `.specify/memory/constitution.md`:

### ✅ Code Quality (Non-Negotiable)
- [ ] T058: Linting passes (ruff check)
- [ ] T059: Type checking passes (mypy)
- [ ] T060: Docstrings complete and clear
- [ ] Code review: Self-documenting, DRY, consistent
- Validation: T065

### ✅ Testing Standards (Non-Negotiable)
- [ ] T019-T020: Contract and unit tests written first (TDD)
- [ ] T034-T037: Comprehensive test coverage
- [ ] T046: Installation tests
- [ ] T052, T057: Extension and integration tests
- [ ] T063: 80%+ coverage achieved and documented
- Validation: T064, T065

### ✅ User Experience Consistency
- [ ] T022: Version display clear
- [ ] T021-T025: Help system complete and consistent
- [ ] T013: Rich output helpers for formatting
- [ ] T026: Help text verified in tests
- [ ] T064: Contract validation confirms UX
- Validation: T065

### ✅ Performance Requirements
- [ ] T021-T022: Help display targets measured
- [ ] T030: Progress feedback at appropriate intervals
- [ ] T014: Database caching for performance
- [ ] T065: Performance targets verified
- Validation: Profiling during T066

### ✅ Maintainability & Architectural Simplicity
- [ ] T016-T017: Single Typer app, modular commands
- [ ] T047-T049: Clear extensibility pattern
- [ ] T054: Command grouping pattern documented
- [ ] T047, T048: New command template and guide
- [ ] T061, T062: Development documentation
- Validation: T065, architecture review

---

## Next Steps After Task Completion

1. **Commit changes**: `git add . && git commit -m "Implement GateToSovngarde CLI v0.1.0"`
2. **Run full test suite**: `uv run pytest tests/ -v --cov=src/cli`
3. **Verify coverage**: Check coverage report is 80%+
4. **Build package**: `uv build`
5. **Test installation**: Install from wheel, verify `gts --help` works
6. **Create pull request** to main branch
7. **Code review**: Verify against constitution gates
8. **Merge and tag**: Create v0.1.0 release

---

## Questions & Clarifications

For task details, refer to:
- **Data Models**: [data-model.md](data-model.md)
- **CLI Contracts**: [contracts/commands.md](contracts/commands.md)
- **Development Setup**: [quickstart.md](quickstart.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Technical Decisions**: [research.md](research.md)

Each task is designed to be independently executable with sufficient context from the specification documents.

