# CLI Command Contracts

**Date**: 2026-03-14  
**Purpose**: Define the CLI command interface contracts for implementation and testing

---

## Contract: gts (Main Application)

**Entry Point**: `gts`  
**Type**: Main Typer Application  
**Help Command**: `gts --help`

### Command Structure
```
gts [COMMAND] [OPTIONS] [ARGUMENTS]
```

### Global Options
- `--version`: Display CLI version and exit
- `--help`, `-h`: Display help text

### Global Behavior
- Consistent error formatting with exit codes:
  - 0: Success
  - 1: Validation/argument error
  - 2: Runtime operation error
  - 127: Command not found
- All error messages prefixed with "Error: " (red text via Rich)
- Help text automatically generated from command descriptions and Typer decorators

### Expected Output Format

**Success Output** (stdout):
```
[Rich formatted success message]
[Operation summary with counts/stats]
```

**Error Output** (stderr):
```
Error: [Human-readable error message]
[Recovery suggestion if applicable]

Use 'gts [command] --help' for more information.
```

**Help Output**:
```
Usage: gts [OPTIONS] COMMAND [ARGS]...

GateToSovngarde CLI - Mod management tools

Options:
  --version         Show version
  --help, -h        Show this message and exit

Commands:
  import           Import mods from source to destination
  [future commands...]
```

---

## Contract: gts import

**Command Name**: `import`  
**Type**: CLI Command  
**Priority**: P1 (MVP)  
**Help Command**: `gts import --help`

### Signature
```bash
gts import VERSION SOURCE_PATH DEST_PATH [OPTIONS]
```

### Arguments

| Argument | Type | Required | Example | Validation |
|----------|------|----------|---------|-----------|
| VERSION | String | Yes | GTSv101 | Must match pattern `GTSv\d+`, must exist in databases |
| SOURCE_PATH | Path | Yes | /mnt/data/source | Must exist, must be readable directory |
| DEST_PATH | Path | Yes | /mnt/data/dest | Must be writable directory (created if needed) |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--force` | `-f` | Boolean | false | Overwrite existing files in destination |
| `--verbose` | `-v` | Boolean | false | Verbose output (shows detailed progress) |
| `--validate-only` | None | Boolean | false | Validate compatibility without importing |

### Exit Codes

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Import successful | All mods imported, no errors |
| 1 | Argument validation error | Invalid path, unknown version, missing argument |
| 2 | Runtime error | Permission denied, corrupted database, I/O error |

### Success Response

**Output Format** (stdout):
```
✓ Import complete
  Version:        GTSv101
  Source:         /mnt/data/source
  Destination:    /mnt/data/dest
  Mods imported:  15
  Files copied:   42
  Duration:       12.5 seconds
```

**With --verbose flag**:
```
✓ Importing from GTSv101 database
  Loading database... (0.1s)
  Validating paths... (0.05s)
  Importing mods:
    [====>                    ] 15/50 (30%) - quest_001.esp
  ✓ Import complete (12.5s)
```

### Error Responses

**Example 1: Invalid version**
```
Error: GTS version 'GTSv999' not found
Available versions: GTSv101, GTSv102

Use 'gts import --help' for more information.
```
Exit Code: 1

**Example 2: Source path doesn't exist**
```
Error: Source path does not exist: /mnt/data/source

Please verify the path and try again.
Use 'gts import --help' for more information.
```
Exit Code: 1

**Example 3: Permission denied**
```
Error: Permission denied when writing to destination: /mnt/data/dest

The directory is not writable. Please check permissions:
  sudo chmod u+w /mnt/data/dest

Use 'gts import --help' for more information.
```
Exit Code: 2

**Example 4: Partial failure with --force flag**
```
Error: Import completed with errors (42 successful, 3 failed)

Failed imports:
  - armor_001.esp: File already exists (use --force to overwrite)
  - quest_002.esp: Permission denied
  - weapons_001.esp: Corrupted file

Use 'gts import --help' for more information.
```
Exit Code: 2

### Help Output

**Command**: `gts import --help`

```
Usage: gts import [OPTIONS] VERSION SOURCE_PATH DEST_PATH

Import mods from source directory to destination using GTS version database.
All GTS version databases are bundled with this application and support
offline operation.

Arguments:
  VERSION         GTS version to import (e.g., GTSv101)
                  Use 'gts versions' to see available versions
  SOURCE_PATH     Source directory containing mod files
  DEST_PATH       Destination directory where mods will be imported

Options:
  -f, --force     Overwrite existing files in destination
  -v, --verbose   Show detailed progress during import
  --validate-only Check compatibility without importing
  --help          Show this message and exit

Examples:
  # Import using GTSv101 database
  gts import GTSv101 /mnt/source /mnt/dest
  
  # Import with verbose output
  gts import GTSv101 /mnt/source /mnt/dest --verbose
  
  # Import with overwrite enabled
  gts import GTSv101 /mnt/source /mnt/dest --force
  
  # Validate without importing
  gts import GTSv101 /mnt/source /mnt/dest --validate-only

Documentation:
  For more information, visit: https://github.com/TianaNanta/GateToSovngarde
```

### Implementation Constraints

1. **Path Handling**:
   - Accept both absolute and relative paths
   - Resolve `~` (home directory) properly
   - Handle symlinks safely

2. **Database Loading**:
   - Load database synchronously before validation
   - Fail immediately if database not found
   - Cache loaded database for efficiency

3. **Import Progress**:
   - Update progress every 5 seconds or after 10 files (whichever is first)
   - Show percentage, current file, files remaining
   - Handle long filenames with truncation in output

4. **Interruption Handling**:
   - Gracefully handle Ctrl+C (SIGINT)
   - Display status: "Interrupted by user after X seconds"
   - Do NOT delete partially imported files (user can resume with --force)

5. **Error Recovery**:
   - Try each file independently (don't stop on first error)
   - Collect all errors and report in final summary
   - Suggest recovery actions for each error type

---

## Contract: gts --help (Main Help)

**Command**: `gts --help` or `gts -h`

**Output Format**:
```
Usage: gts [OPTIONS] COMMAND [ARGS]...

GateToSovngarde CLI - Mod management tools

Options:
  --version             Show the application version and exit
  --help, -h            Show this message and exit

Commands:
  import                Import mods from source to destination (P1)
  [future-command]      [Future command description] (P2)

Use 'gts COMMAND --help' for more information about a command.

Examples:
  gts import GTSv101 /source /dest
  gts import --help
  gts --version
```

**Exit Code**: 0 (success)

---

## Contract: gts --version

**Command**: `gts --version`

**Output Format**:
```
GateToSovngarde CLI version 0.1.0
```

**Exit Code**: 0 (success)

---

## Future Command Template

New commands should follow this contract structure:

```markdown
## Contract: gts [command-name]

**Command Name**: `[command-name]`  
**Type**: CLI Command  
**Priority**: P[N]  
**Help Command**: `gts [command-name] --help`

### Signature
```bash
gts [command-name] ARGUMENT1 ARGUMENT2 [OPTIONS]
```

### Arguments
| Argument | Type | Required | Example | Validation |
|----------|------|----------|---------|-----------|
| ARG1 | Type | Yes/No | example | validation rule |

### Options
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--option` | `-o` | Type | default | What it does |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation error |
| 2 | Runtime error |

### Success Response
[Expected output on success]

### Error Responses
[Example error scenarios and outputs]

### Help Output
[Output from `--help` flag]
```

---

## Testing Contract Specifications

All commands MUST have passing contract tests:

**Contract Test Template**:
```python
def test_import_command_help_output():
    """Test that gts import --help displays correct interface."""
    runner = CliRunner()
    result = runner.invoke(app, ["import", "--help"])
    assert result.exit_code == 0
    assert "Import mods" in result.stdout
    assert "VERSION" in result.stdout
    assert "SOURCE_PATH" in result.stdout
    assert "DEST_PATH" in result.stdout

def test_import_command_success():
    """Test successful import operation."""
    runner = CliRunner()
    result = runner.invoke(app, [
        "import",
        "GTSv101",
        "/test/source",
        "/test/dest"
    ])
    assert result.exit_code == 0
    assert "Import complete" in result.stdout

def test_import_missing_argument():
    """Test validation error for missing argument."""
    runner = CliRunner()
    result = runner.invoke(app, ["import", "GTSv101"])
    assert result.exit_code == 1
    assert "Error:" in result.output
```

Each new command requires similar contract test coverage before implementation approval.

