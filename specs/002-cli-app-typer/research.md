# Phase 0 Research: GateToSovngarde CLI Implementation

**Date**: 2026-03-14  
**Purpose**: Resolve implementation unknowns for CLI framework and GTS database bundling strategy

## Research Areas

### 1. GTS Database Implementation Strategy

**Decision: File-based JSON/YAML database bundled as package data**

**Rationale**: 
- User stated uncertainty about database implementation ("I don't have a clue on how to implement it")
- Current project uses file-based approach (no external database dependencies)
- JSON/YAML provides human-readable, versioned database format suitable for mod metadata
- Pre-bundling databases ensures offline capability and eliminates runtime downloads
- Follows Python packaging best practices for including non-code files

**Alternatives Considered**:
1. **SQLite Database**: Pros - efficient binary format, queryable. Cons - overkill for static mod metadata, adds dependency complexity
2. **Dynamic Download at Runtime**: Pros - smaller package size. Cons - requires internet, adds installation complexity, violates offline capability requirement
3. **Git Submodule**: Pros - separate version control. Cons - complex setup, increased maintenance burden
4. **Package Data Directory**: ✅ SELECTED - Standard Python approach, simple, effective for static content

**Implementation Details**:
- Create `databases/` directory at package root containing versioned subdirectories (e.g., `databases/gtsv101/`)
- Each version directory contains `mods.json` or equivalent with mod metadata
- Use Python's `importlib.resources` or `pkg_resources` to locate database files at runtime
- Database files included in `pyproject.toml` via `[project]` section with `include-package-data = true`
- Alternative: Use `MANIFEST.in` to explicitly include database files

**Build Configuration**:
```toml
# In pyproject.toml
[project]
name = "gatetosovngarde-cli"
include-package-data = true

[tool.uv]
# Ensures databases are included when building
```

### 2. Python Package Distribution & uv Tool Installation

**Decision: Distribute as both PyPI package and uv tool, using `scripts` entry point**

**Rationale**:
- User wants: `uv tool install gatetosovngarde-cli --from git+https://github.com/...`
- uv tools require a console script entry point defined in `pyproject.toml`
- PyPI distribution enables `pip install` and `uv add` for library usage
- Single codebase supports both distribution methods

**Alternatives Considered**:
1. **PyPI-only with pip**: Pros - standard. Cons - loses uv tool convenience
2. **GitHub-only build**: Pros - flexible. Cons - no package registry, harder to discover
3. **Docker image**: Pros - isolated. Cons - unnecessary overhead for CLI tool
4. ✅ SELECTED - PyPI + direct git installation via uv

**Implementation Details**:
```toml
# In pyproject.toml [project.scripts]
[project.scripts]
gts = "cli.main:app"  # Entry point: module.submodule:typer_app_instance
```

**Build Steps**:
1. `uv build` creates wheel distribution (includes database files via `include-package-data`)
2. Published to PyPI as `gatetosovngarde-cli`
3. Also installable directly from git: `uv tool install gatetosovngarde-cli --from git+https://github.com/TianaNanta/GateToSovngarde.git`
4. After installation, `gts` command available in user's environment

### 3. Typer Application Structure

**Decision: Single Typer app instance in `cli/main.py` with command registration via Python modules**

**Rationale**:
- Typer supports command groups and sub-commands natively
- Single app instance enables centralized help, version, and configuration
- Command registration via decorators keeps code organized
- Matches Typer best practices for growing CLI applications

**Alternatives Considered**:
1. **Plugin system with discovery**: Pros - maximum flexibility. Cons - overkill for current scope, adds complexity
2. **Subcommand factories**: Pros - dynamic. Cons - harder to maintain
3. ✅ SELECTED - Simple decorator-based registration with future extensibility

**Implementation Pattern**:
```python
# src/cli/main.py
import typer

app = typer.Typer(help="GateToSovngarde CLI - Mod management tools")

@app.command()
def import_cmd(
    version: str,
    source_path: str,
    dest_path: str,
):
    """Import mods from source to destination."""
    # Implementation
    
if __name__ == "__main__":
    app()
```

### 4. Database Access Pattern

**Decision: Single DatabaseLoader class with cached version index, lazy-loaded per-version databases**

**Rationale**:
- Avoids loading all databases into memory at startup (performance)
- Version validation happens at command start (fail fast)
- Caching prevents repeated disk reads during single command execution
- Thread-safe for potential future concurrent operations

**Alternatives Considered**:
1. **Load all databases at startup**: Pros - simple. Cons - slower startup, higher memory
2. **Dynamic git fetch**: Pros - no bundling. Cons - violates offline requirement
3. ✅ SELECTED - Lazy loading with caching

**Implementation Pattern**:
```python
# src/cli/db/loader.py
class DatabaseLoader:
    _cache = {}
    
    @classmethod
    def get_version(cls, version_id: str) -> Dict:
        """Load GTS version database, using cache if available."""
        if version_id in cls._cache:
            return cls._cache[version_id]
        
        db = cls._load_from_disk(version_id)
        cls._cache[version_id] = db
        return db
```

### 5. Testing Strategy for CLI

**Decision: Three-tier testing approach with unit, integration, and contract tests**

**Rationale**:
- Constitution requires test-first discipline and 80%+ coverage
- CLI requires testing at multiple levels: command logic, argument parsing, end-to-end flows
- Contract tests ensure command interface consistency for extensibility

**Test Pyramid**:
- **Unit Tests** (60%): Command logic, argument validation, database loading, error scenarios
- **Integration Tests** (30%): Full command flows (import with various inputs), output verification
- **Contract Tests** (10%): CLI command interface definitions (command names, argument types, help text)

**Testing Tools**:
- pytest for test execution
- `typer.testing.CliRunner` for CLI testing (built into Typer)
- pytest fixtures for database mocks and test data

### 6. Error Handling & User Feedback

**Decision: Structured exceptions with helpful user messages, Rich formatting for output**

**Rationale**:
- Constitution requires clear, actionable error messages
- Rich library already in project, provides beautiful formatting
- Structured exceptions enable consistent error handling across commands

**Exception Hierarchy**:
```
CLIError (base)
├── ValidationError (invalid arguments/paths)
├── DatabaseError (missing or corrupted database)
└── OperationError (operation failed with reason)
```

### 7. Logging & Observability

**Decision: Integrate with project's existing Python logging infrastructure**

**Rationale**:
- Project already uses Python logging (per AGENTS.md)
- No new dependencies required
- Consistent logging across CLI and existing scripts

**Logging Levels**:
- DEBUG: Database loading operations, argument parsing details
- INFO: Command execution start/completion, progress updates
- WARNING: Non-critical issues (e.g., missing optional files)
- ERROR: Failed operations (logged before exception to user)

### 8. Performance Optimization

**Decision: Lazy load databases, measure startup time, profile import operations**

**Rationale**:
- Constitution requires defined performance targets
- Success criteria require help display <1s, command startup <500ms

**Profiling Points**:
1. Time to first help output (target: <1s)
2. Command startup before first operation (target: <500ms)
3. Database loading time per version (measure to establish baseline)
4. Import progress feedback interval (5s between progress updates)

### Summary of Decisions

| Area | Decision | Key Benefits |
|------|----------|--------------|
| Database Format | JSON/YAML files bundled as package data | Offline-capable, simple, versioned, human-readable |
| Package Distribution | PyPI + direct git install via uv | Maximum flexibility, standard Python practices |
| CLI Framework | Single Typer app with command modules | Clean, maintainable, extensible |
| Database Access | Lazy-loaded with caching | Performance, memory efficiency |
| Testing | Unit/Integration/Contract three-tier | Comprehensive coverage, contract-first design |
| Error Handling | Structured exceptions + Rich formatting | User-friendly, consistent |
| Logging | Python logging integration | Consistency, no new dependencies |
| Performance | Measured with profiling targets | Data-driven optimization |

## Implementation Readiness

✅ All unknowns resolved  
✅ Technical decisions documented with rationale  
✅ Alternatives evaluated and justified  
✅ Ready for Phase 1 design work
