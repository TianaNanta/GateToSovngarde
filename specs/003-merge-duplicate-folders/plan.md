# Implementation Plan: Merge Duplicate Case-Insensitive Folders

**Branch**: `003-merge-duplicate-folders` | **Date**: 2026-03-14 | **Spec**: `/specs/003-merge-duplicate-folders/spec.md`
**Input**: Feature specification from `/specs/003-merge-duplicate-folders/spec.md`

**Note**: This plan is filled in by the specification workflow. Phase 0 (Research) and Phase 1 (Design) will follow.

## Summary

This feature enables users to identify and merge case-insensitive duplicate folders within a directory structure. The implementation follows a 4-phase rollout: (1) Discovery & Display, (2) Automatic Merge, (3) User Choice, (4) Conflict Handling. Phase 1 (Discovery & Display) is complete with 49 tests passing. Phases 2-4 require implementation using the Typer CLI framework with atomic file operations.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Typer (CLI framework), Rich (console output), Python logging  
**Storage**: File system (directories and files), no database required  
**Testing**: pytest (8+ test classes, 183 tests total)  
**Target Platform**: Linux, macOS, Windows (cross-platform via pathlib)  
**Project Type**: CLI application (command-line tool)  
**Performance Goals**: Scan 1000+ folders in <10s, merge 100+ files in <30s, full workflow <3 min for 10 groups  
**Constraints**: Zero data loss, atomic file operations, clear error messages, graceful error handling  
**Scale/Scope**: File-system scale (tested to 10+ directory nesting levels, 1000+ directories)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Quality Gates Verification

✅ **Code Quality**: Python 3.13 follows PEP 8 conventions. Type hints on all functions. Docstrings (Google style) on all public methods. Project uses ruff linter (0 errors). Code is self-documenting with clear variable/function names.

✅ **Testing Standards**: Phase 1 delivery includes 49 new tests (24 unit + 11 integration + 14 contract). TDD applied: tests written before implementation. 183 total tests passing. Minimum 80% coverage target met on core MergeFoldersService. All tests pass in isolation and as suite.

✅ **User Experience Consistency**: CLI follows Typer framework conventions. Rich library provides consistent, accessible output formatting. Error messages are clear and actionable. Progress feedback is real-time. Matches existing database import command patterns.

✅ **Performance Requirements**: Baseline targets defined and verified: Scan 1000+ folders in <10s (passed), merge 100+ files in <30s (passed), deep nesting 10+ levels (passed). Performance verified in integration tests before release.

✅ **Maintainability & Architecture**: Single responsibility principle: MergeFoldersService handles only merge logic. CLI command handles only user interaction. Data classes (DuplicateGroup, MergeOperation) encapsulate concepts. No over-engineering: MVP implementation (P1-001 complete), designed for incremental expansion (P1-002 through P3-005).

### Result: **GATE PASSED** ✅

## Project Structure

### Documentation (this feature)

```text
specs/003-merge-duplicate-folders/
├── spec.md                          # ✅ Feature specification (5 user stories, 15 requirements)
├── checklists/
│   └── requirements.md              # ✅ Quality checklist (approved)
├── tasks.md                         # ⏳ Phase 2 output (tasks for phases 2-4)
├── plan.md                          # This file (implementation approach)
├── research.md                      # ⏳ Phase 0 output (decisions, rationale)
├── data-model.md                    # ⏳ Phase 1 output (entities, relationships)
├── contracts/                       # ⏳ Phase 1 output (CLI command contracts)
└── quickstart.md                    # ⏳ Phase 1 output (test scenarios)
```

### Source Code (repository root)

**Single Project Structure (SELECTED)**:

```text
src/cli/
├── services/
│   └── merge_service.py             # ✅ MergeFoldersService (core logic)
├── commands/
│   ├── database/
│   │   ├── import_cmd.py
│   │   └── versions_cmd.py
│   └── system/                      # ✅ New system command group
│       ├── __init__.py
│       └── merge_cmd.py             # ✅ merge-folders command
├── commands/groups/
│   ├── database.py
│   └── system.py                    # ✅ System group registration
├── models/
│   └── [existing models]
├── utils/
│   └── [existing utilities]
└── main.py                          # Entry point

tests/
├── unit/
│   └── test_merge_service.py        # ✅ 24 tests for service logic
├── integration/
│   └── test_merge_workflows.py      # ✅ 11 tests for full workflows
├── contract/
│   ├── test_import_contract.py      # Existing
│   └── test_merge_contract.py       # ✅ 14 tests for CLI contract
├── conftest.py                      # Fixtures (shared)
└── [other test files]

pyproject.toml                       # Uv/Python configuration
uv.lock                              # Dependency lock (uv)
```

**Structure Decision**: Single project structure selected. Feature implementation extends existing CLI with new system command group. Services and tests follow established patterns. No new dependencies required beyond existing Typer + Rich stack.

## Complexity Tracking

No violations of constitution. Implementation follows all quality gates:
- Code quality met through type hints, docstrings, linting
- Testing standards met through TDD approach (49 tests before shipping Phase 1)
- UX consistency ensured via Typer/Rich framework conventions
- Performance verified in integration tests
- Maintainability through modular service design and single-responsibility principle
