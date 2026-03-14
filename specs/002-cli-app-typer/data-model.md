# Phase 1: Data Model & Entities

**Date**: 2026-03-14  
**Phase**: Design & Contracts  
**Based on**: [spec.md](spec.md) + [research.md](research.md)

## Core Entities

### 1. Command

**Purpose**: Represents a CLI command that can be executed by users

**Attributes**:
- `name` (string): Unique command identifier (e.g., "import", "validate")
- `description` (string): Short one-line description for help text
- `help_text` (string): Detailed help documentation shown with `--help`
- `arguments` (list[Argument]): Required and optional arguments
- `options` (list[Option]): Optional flags and settings
- `callback` (function): Callable that executes command logic
- `group` (string, optional): Command group for hierarchy (e.g., "database", "mod")

**Validation Rules**:
- `name`: Must be lowercase alphanumeric with hyphens, unique across all commands
- `description`: Must be non-empty, under 80 characters
- `arguments`: Required arguments must precede optional ones
- `help_text`: Should include usage examples and common error scenarios

**State Transitions**:
- REGISTERED → READY (after Typer decorators applied)
- READY → EXECUTING (when user invokes command)
- EXECUTING → COMPLETED (successful execution)
- EXECUTING → FAILED (error during execution)

**Relationships**:
- Composed of: Argument(s), Option(s)
- Belongs to: CommandGroup (optional)
- Executes: Business logic (e.g., ImportLogic)

**Example Usage**:
```python
Command(
    name="import",
    description="Import mods from source to destination",
    help_text="gts import VERSION SOURCE DEST\n\nExample: gts import GTSv101 /mnt/source /mnt/dest",
    arguments=[
        Argument(name="version", type=str, description="GTS version ID"),
        Argument(name="source_path", type=str, description="Source directory path"),
        Argument(name="dest_path", type=str, description="Destination directory path"),
    ],
    options=[
        Option(name="--force", type=bool, description="Overwrite existing files"),
    ]
)
```

---

### 2. Argument

**Purpose**: Represents a required or optional positional argument to a command

**Attributes**:
- `name` (string): Argument name
- `type` (Type): Python type (str, int, Path, etc.)
- `description` (string): Help text for this argument
- `required` (boolean): Whether argument is required
- `default` (any, optional): Default value if optional
- `validator` (callable, optional): Custom validation function

**Validation Rules**:
- `name`: Must be lowercase alphanumeric, unique within command
- `type`: Must be a valid Python type or Typer type
- `description`: Must be non-empty
- If `required=False`, must have `default` value
- `validator` function must return True/raise ValueError

**Example**:
```python
Argument(
    name="version",
    type=str,
    description="GTS version identifier (e.g., GTSv101)",
    required=True,
    validator=DatabaseLoader.validate_version_exists  # Check DB availability
)

Argument(
    name="source_path",
    type=Path,
    description="Source directory path",
    required=True,
    validator=lambda p: p.exists() or error("Path does not exist")
)
```

---

### 3. Option

**Purpose**: Represents optional command-line flags

**Attributes**:
- `name` (string): Option name with dashes (e.g., "--force", "-f")
- `type` (Type): Python type (bool, str, int, etc.)
- `description` (string): Help text
- `short` (string, optional): Single-character short form (e.g., "-f")
- `default` (any): Default value when option not provided

**Validation Rules**:
- `name`: Must start with "--", be lowercase with hyphens
- `short`: If provided, must be single character with "-"
- No duplicate names within command

**Example**:
```python
Option(name="--force", type=bool, default=False, description="Overwrite existing files")
Option(name="--verbose", short="-v", type=bool, default=False, description="Verbose output")
```

---

### 4. GTS Version Database

**Purpose**: Contains metadata about available mods for a specific GTS version

**Structure** (stored as JSON/YAML file):
```json
{
  "version_id": "GTSv101",
  "version_name": "GateToSovngarde v1.01",
  "created_date": "2026-03-14",
  "mods": [
    {
      "id": "mod_123",
      "name": "Example Mod",
      "description": "What this mod does",
      "author": "Author Name",
      "version": "1.0.0",
      "required_files": ["file1.esp", "file2.esm"],
      "conflicts_with": ["mod_456"],
      "tags": ["quest", "armor"]
    }
  ]
}
```

**Attributes**:
- `version_id` (string): Unique identifier (e.g., "GTSv101")
- `version_name` (string): Human-readable version name
- `created_date` (ISO date): When database was created
- `mods` (list[ModEntry]): List of mod metadata entries

**Validation Rules**:
- `version_id`: Must match format `GTSv\d+` (e.g., GTSv101, GTSv200)
- `mods`: Must not be empty
- Each ModEntry must have unique `id` within database
- `required_files`: Must be non-empty list
- File paths must be relative

---

### 5. Mod Entry

**Purpose**: Metadata for a single mod in the database

**Attributes**:
- `id` (string): Unique mod identifier
- `name` (string): Display name
- `description` (string): What the mod does
- `author` (string): Creator name
- `version` (string): Semantic version
- `required_files` (list[string]): Files that must be copied/installed
- `conflicts_with` (list[string], optional): MOD IDs that conflict
- `tags` (list[string], optional): Categorization tags

**Validation Rules**:
- `id`: Lowercase alphanumeric with underscores, unique per database
- `version`: Must follow semantic versioning (X.Y.Z)
- `required_files`: Non-empty, all must be relative paths
- `conflicts_with`: List of known conflicting mod IDs

---

### 6. Import Operation

**Purpose**: Encapsulates a mod import execution with state tracking

**Attributes**:
- `id` (UUID): Unique operation identifier
- `version` (string): GTS version being used
- `source_path` (Path): Source directory
- `dest_path` (Path): Destination directory
- `status` (enum): PENDING, IN_PROGRESS, COMPLETED, FAILED
- `mods_imported` (int): Count of successfully imported mods
- `errors` (list[ImportError]): Failed operations with reasons
- `started_at` (datetime): When operation began
- `completed_at` (datetime, optional): When operation finished
- `duration_seconds` (float, optional): Total execution time

**Validation Rules**:
- `source_path` must exist and be readable
- `dest_path` must exist or be creatable
- `dest_path` parent must be writable
- `version` must exist in database

**State Transitions**:
```
PENDING → IN_PROGRESS → COMPLETED
              ↓
            FAILED
```

**Progress Tracking**:
- Report progress every N files (or 5-second interval)
- Include: files processed, files remaining, current file being processed
- Format: "Importing mods: 45/100 (45%) - [current_mod]"

---

### 7. Import Error

**Purpose**: Records a specific error during import operation

**Attributes**:
- `mod_id` (string): Which mod caused error
- `error_type` (enum): FILE_NOT_FOUND, PERMISSION_DENIED, VALIDATION_FAILED, etc.
- `message` (string): Human-readable error message
- `file_path` (Path, optional): Which file caused the error
- `recovery_suggestion` (string): How user can fix the issue

**Example**:
```python
ImportError(
    mod_id="mod_quest_01",
    error_type=ErrorType.FILE_NOT_FOUND,
    message="Required file 'quests.esp' not found in source",
    file_path=Path("/source/quests.esp"),
    recovery_suggestion="Verify source directory contains all mod files"
)
```

---

### 8. CLI Application Context

**Purpose**: Holds CLI-wide configuration and state

**Attributes**:
- `version` (string): CLI application version
- `db_loader` (DatabaseLoader): Shared database access instance
- `logger` (Logger): Configured logging instance
- `console` (Rich Console): Formatted output handler
- `config` (dict): Runtime configuration (verbose, output format, etc.)

**Initialization**:
- Creates logger with project-standard configuration
- Initializes database loader (deferred database loading)
- Configures Rich console with appropriate styling

---

## Data Flow Diagram

```
User Input (CLI)
    ↓
[Command Parser - Typer]
    ↓
[Argument Validator]
    ├→ Path validation
    ├→ Type validation
    └→ Database version check
    ↓
[ImportCommand]
    ├→ Load GTS Database
    ├→ Validate source/dest
    └→ Execute import
    ↓
[Import Operation]
    ├→ Process each mod
    ├→ Copy/move files
    ├→ Track progress
    └→ Record errors
    ↓
[Result Output - Rich]
    ├→ Success message
    ├→ Error list (if any)
    ├→ Statistics (files imported, duration)
    └→ Recovery suggestions (if errors)
```

---

## Validation Rules Summary

### Path Validation
- Must exist (or parent exists if being created)
- Must be readable (source) or writable (destination)
- Must not exceed filesystem path length limits

### Version Validation
- Format: `GTSv\d+` (e.g., GTSv101)
- Must exist in bundled databases
- Database file must be readable

### Argument Validation (Pre-Execution)
- All required arguments provided
- All paths valid and accessible
- Database version available
- Source contains expected files

### Operation Validation (During Execution)
- File copy permissions verified per-file
- Destination space available
- Handle interruption gracefully (Ctrl+C)
- Atomic operations where possible

---

## Extension Points for Future Scripts

Future commands (beyond import) will follow same entity patterns:

```python
# Example: Future validation command
Command(
    name="validate",
    description="Validate mod compatibility",
    arguments=[
        Argument(name="version", type=str),
        Argument(name="mod_path", type=Path),
    ]
)

# Example: Future list command  
Command(
    name="list",
    description="List available mods",
    arguments=[
        Argument(name="version", type=str),
    ],
    options=[
        Option(name="--filter", type=str, default=""),
        Option(name="--format", type=str, default="table"),
    ]
)
```

Each new command registers itself with the main Typer app without framework changes.

---

## Testing Entities

### Test Fixtures
- **mock_database**: Sample GTS database with test mods
- **temp_paths**: Temporary source/dest directories for testing
- **cli_runner**: Typer CliRunner instance for command testing
- **mock_logger**: Capture log output for verification

### Contract Test Matrix
Each command must define:
- Command name and help text
- Required arguments and their types
- Optional arguments and defaults
- Expected exit codes: 0 (success), 1 (validation error), 2 (operation error)
- Expected output format (JSON, table, text)

