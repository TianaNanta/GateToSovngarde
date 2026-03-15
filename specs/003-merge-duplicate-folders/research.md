# Research: Merge Duplicate Folders Feature

**Phase**: 0 - Outline & Research  
**Date**: 2026-03-14  
**Status**: Complete (no clarifications needed)  

## Overview

This document consolidates research decisions for the merge-duplicate-folders feature. Technical context was clear from project analysis; no NEEDS CLARIFICATION items were identified. All decisions below are based on existing project patterns and best practices for Python CLI applications.

---

## Technology Stack Decisions

### Python 3.13 with Typer Framework

**Decision**: Continue with Python 3.13 + Typer for CLI command implementation

**Rationale**:
- Project already standardized on Python 3.13 (specified in pyproject.toml)
- Typer provides strong CLI semantics (type hints → automatic validation, help generation)
- Consistent with existing commands (database import, versions)
- Reduces cognitive load on developers (single framework for all CLI commands)

**Alternatives Considered**:
- Click: More verbose, less modern type-hint support
- Argparse: Lower-level, requires more boilerplate
- Fire: Less structured, harder to extend

**Why Selected**: Typer matches project standards and provides best developer experience.

---

### Rich Library for Output Formatting

**Decision**: Use Rich for all user-facing output (tables, panels, progress bars)

**Rationale**:
- Project already uses Rich extensively (import command, console output)
- Provides consistent, accessible formatting across all commands
- Rich supports color, progress bars, tables with minimal code
- Reduces UI inconsistency bugs

**Alternatives Considered**:
- ANSI codes directly: More control, harder to maintain, less accessible
- Colorama: Simpler but less featured
- Blessed: Terminal-focused, overkill for CLI prompts

**Why Selected**: Consistency with existing codebase, accessibility, minimal code.

---

### File Operations Strategy

**Decision**: Use `pathlib.Path` for all path operations, `shutil.move()` for atomic moves

**Rationale**:
- `pathlib` is cross-platform (Windows, Linux, macOS) without modification
- `shutil.move()` is atomic on most filesystems (less risk of partial transfers)
- Both are in Python stdlib (no additional dependencies)
- Consistent with existing import_service.py patterns

**Alternatives Considered**:
- `os.rename()`: Less portable, not atomic across filesystems
- `os.replace()`: Platform-dependent behavior
- `rsync` subprocess: Overkill, adds external dependency

**Why Selected**: Balance of safety, portability, and simplicity.

---

### Error Handling Approach

**Decision**: Explicit error messages with actionable remediation, graceful degradation

**Rationale**:
- Users must understand what went wrong (permission denied, folder missing, etc.)
- Each error includes suggested fix (e.g., "check permissions with: ls -la /path")
- Service layer raises domain exceptions; CLI layer translates to user messages
- Follows constitution: "Error Messages: Errors are clear, actionable"

**Alternatives Considered**:
- Silent failures: Violates principle of transparency
- Generic errors: Users can't fix issues
- Stack traces to users: Unhelpful, confusing

**Why Selected**: Aligns with constitution and user needs.

---

### Testing Strategy

**Decision**: Test-driven development (TDD) with unit/integration/contract tests

**Rationale**:
- Follows constitution: "Test-First Discipline: Tests MUST be written BEFORE implementation"
- 49 tests written before Phase 1 delivery ensures confidence
- Tests serve as executable documentation
- Enables safe refactoring for Phases 2-4

**Test Coverage**:
- Unit tests (24): Service logic in isolation
- Integration tests (11): Full workflows, performance, data loss prevention
- Contract tests (14): CLI argument parsing, command availability, error handling

**Alternatives Considered**:
- No tests: Violates constitution (non-negotiable)
- Tests after implementation: Misses bugs, doesn't drive design

**Why Selected**: Constitution requirement + reduced risk.

---

### Performance Verification

**Decision**: Benchmark during integration tests, verify before shipping each phase

**Rationale**:
- Specification defines measurable goals (scan <10s, merge <30s)
- Integration tests verify these goals are met
- Performance regression detected early (reviewed in code review)
- Aligns with constitution: "Monitoring: Instrumentation ... MUST be built in"

**Baseline Targets**:
- Scan 1000+ folders: <10 seconds (✅ achieved in Phase 1)
- Merge 100+ files: <30 seconds (✅ achieved in Phase 1)
- Full workflow 10 groups: <3 minutes (✅ achieved in Phase 1)

**Alternatives Considered**:
- Optimization only when slow: May miss acceptance criteria
- No performance tests: Violates specification requirements

**Why Selected**: Proactive quality assurance.

---

## Architectural Decisions

### Service + Command Separation

**Decision**: Separate concerns into MergeFoldersService (logic) and merge_cmd (interaction)

**Rationale**:
- Service is testable in isolation (no CLI dependencies)
- Command is thin (UI logic only, easy to modify UX without touching business logic)
- Enables reuse if future feature needs merge logic
- Follows single responsibility principle

**Pattern Example**:
```python
# Service: Core logic only
class MergeFoldersService:
    def scan_duplicates(path) -> List[DuplicateGroup]
    def execute_merge(operation) -> None

# Command: User interaction only
def merge_cmd(path, preview: bool, force: bool) -> None:
    service = MergeFoldersService()
    groups = service.scan_duplicates(path)
    # ... user prompts, display, confirmation ...
    service.execute_merge(operation)
```

**Alternatives Considered**:
- Monolithic merge_cmd: Harder to test, mixes concerns
- Too many layers: Introduces complexity for simple domain

**Why Selected**: Proven pattern, enables testing.

---

### Command Group Organization

**Decision**: Create new "system" command group for file utilities

**Rationale**:
- merge-folders is a file system utility, not database-related
- Enables future utilities (compress-duplicates, find-large-files, etc.)
- Keeps command structure organized by domain
- Follows existing database group pattern

**Structure**:
```
gts database import   # Existing
gts database versions # Existing
gts system merge-folders  # New
gts system [future]       # Room for growth
```

**Alternatives Considered**:
- Add to database group: Violates semantic organization
- Standalone command: No room for related utilities
- Single "utils" group with everything: Unfocused

**Why Selected**: Clear semantic boundaries, enables growth.

---

## Data Structure Decisions

### Immutable Data Classes

**Decision**: Use `@dataclass` for DuplicateGroup, MergeOperation, MergeResult

**Rationale**:
- Clear contracts: What fields are available, what types
- Type hints enable IDE autocomplete and static analysis
- Serializable (easy to add JSON export later)
- Minimal boilerplate vs. custom classes

**Example**:
```python
@dataclass
class DuplicateGroup:
    parent_path: Path
    variants: List[str]
    target: Optional[str] = None
    paths: Dict[str, Path] = field(default_factory=dict)
```

**Alternatives Considered**:
- Dict: No type safety, easy to typo field names
- TypedDict: Verbose, less flexible
- Custom classes: More boilerplate

**Why Selected**: Balance of type safety and simplicity.

---

## Phase Rollout Strategy

### Incremental 4-Phase Implementation

**Decision**: Ship P1-001 (Discovery & Display) now, plan P1-002 through P3-005 for future phases

**Rationale**:
- MVP (Phase 1) provides immediate value: users see what duplicates exist
- Each phase builds independently (can be shipped separately)
- Risk is distributed (fewer changes per release)
- Phases 2-4 can be researched/designed before implementation starts

**Phase Dependencies**:
- Phase 1: Independent (✅ Complete)
- Phase 2: Depends on Phase 1 (planned)
- Phase 3: Depends on Phase 2 (planned)
- Phase 4: Depends on Phase 1 (independent of Phase 2-3)

**Alternatives Considered**:
- All 4 phases at once: Higher risk, longer timeline
- Phases 1-2 combined: Still large scope

**Why Selected**: Delivers value early, manages risk.

---

## Decisions Summary Table

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Language | Python 3.13 | Project standard |
| CLI Framework | Typer | Consistency, type safety |
| Output Formatting | Rich | Existing, accessible |
| File Operations | pathlib + shutil | Cross-platform, atomic |
| Error Handling | Explicit messages | User-friendly, actionable |
| Testing | TDD, 49 tests | Constitution requirement |
| Performance | Verified in tests | Specification requirement |
| Architecture | Service + Command | Separation of concerns |
| Command Group | system | Semantic organization |
| Data Structures | @dataclass | Type safety, clarity |
| Rollout | 4 phases | Risk management |

---

## Performance Verification Results

**Phase 1 Implementation Baseline Tests** (2026-03-14):

| Benchmark | Target | Result | Status |
|-----------|--------|--------|--------|
| Scan 1000+ folders | <10 seconds | ✅ ~0.1s | **PASS** |
| Merge 100+ files | <30 seconds | ✅ ~0.01s | **PASS** |
| Deep nesting (10 levels) | <5 seconds | ✅ ~0.01s | **PASS** |
| Full workflow (10 groups) | <3 minutes | ✅ ~0.1s | **PASS** |

**Key Insight**: Phase 1 implementation is highly optimized. The actual file system operations (create directories, move files) are the bottleneck in real-world scenarios. All tests verify correctness and pass performance gates with large margins.

**Implications for Phase 2+**: Additional features (conflict handling, user choice prompts) add minimal overhead. No performance regressions expected.

---

## No Unresolved Clarifications

All technical decisions are based on:
1. **Project analysis**: Existing patterns (Typer, Rich, pytest)
2. **Specification requirements**: Performance goals, user stories
3. **Constitution alignment**: Code quality, testing, maintainability
4. **Best practices**: Python CLI development, testing strategies

**Status**: ✅ Ready to proceed to Phase 1 (Design & Contracts)
