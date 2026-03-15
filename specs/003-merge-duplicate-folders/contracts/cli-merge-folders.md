# CLI Contract: merge-folders Command

**Interface Type**: Command-line interface (Typer CLI)  
**Module**: `src/cli/commands/system/merge_cmd.py`  
**Registration**: System command group (`gts system merge-folders`)  

---

## Command Schema

### Signature

```
gts system merge-folders [PATH] [OPTIONS]
```

### Arguments

| Argument | Type | Required | Example | Description |
|----------|------|----------|---------|-------------|
| `PATH` | string (directory) | Yes | `/home/user/data` | Directory to scan for duplicate folders |

### Options

| Option | Type | Short | Default | Description |
|--------|------|-------|---------|-------------|
| `--preview` | boolean flag | - | False | Show duplicates without modifying any files |
| `--force` / `-f` | boolean flag | `-f` | False | Skip confirmation prompts and auto-merge |

### Help Text

```
Usage: gts system merge-folders [OPTIONS] PATH

  Identify and merge case-insensitive duplicate folders.

  This command scans a directory for case-insensitive duplicate folders
  and helps merge them together. It provides a safe workflow with preview,
  user confirmation, and conflict detection.

Options:
  --preview          Show duplicate folders and merge plans without executing
  -f, --force        Skip confirmation prompts and auto-merge using default rules
  --help             Show this message and exit.

Examples:
  gts system merge-folders /data --preview
  gts system merge-folders /data
  gts system merge-folders /data --force
```

---

## Exit Codes

| Code | Meaning | Example Scenario |
|------|---------|------------------|
| 0 | Success | Scan complete, merge executed, or no duplicates found |
| 1 | Error | Invalid path, permission denied, merge failed |
| 2 | Invalid usage | Missing required argument, invalid flag |

---

## Output Specification

### Output Modes

#### Mode 1: Preview Mode (`--preview` flag)

**When**: User runs with `--preview`  
**Output**: Display duplicate groups without prompting

```
ℹ Scanning for duplicate case-insensitive folders in /home/data...

Found 2 duplicate group(s):

┌─────────────────────────────────────────────────────────────────────┐
│ Group 1: Mods                                                       │
├─────────────────────────────────────────────────────────────────────┤
│ /home/data/mods                                                     │
│ /home/data/Mods                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Group 2: configs                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ /home/data/configs                                                  │
│ /home/data/Configs                                                  │
└─────────────────────────────────────────────────────────────────────┘

ℹ Preview mode: no changes were made
```

**Output Components**:
- Progress indicator: "Scanning..."
- Summary: "Found N duplicate group(s)"
- Per-group table showing all variants and paths
- Confirmation: "Preview mode: no changes were made"

#### Mode 2: Interactive Merge Mode (default)

**When**: User runs without flags  
**Output**: Display duplicates, prompt for confirmation, show progress

```
ℹ Scanning for duplicate case-insensitive folders in /home/data...

Found 1 duplicate group(s):

┌─────────────────────────────────────────────────────────────────────┐
│ Group 1/1                                                           │
├─────────────────────────────────────────────────────────────────────┤
│ Source: /home/data/Mods (152 files, 2.3 GB)                        │
│ Target: /home/data/mods (already exists)                           │
│ Files:  152                                                         │
│ Size:   2.3 GB                                                      │
└─────────────────────────────────────────────────────────────────────┘

Proceed with this merge? [y/N]: y

✓ Merged Mods into mods

┌─────────────────────────────────────────────────────────────────────┐
│ Merge Summary                                                       │
├─────────────────────────────────────────────────────────────────────┤
│ ✓ Merged: 1                                                         │
│ ⊘ Skipped: 0                                                        │
│ Total groups: 1                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output Components**:
- Progress indicator
- Duplicate groups display
- Merge preview (source, target, file count, size)
- User prompt (y/N)
- Success messages per merge
- Summary panel

#### Mode 3: Force Mode (`--force` flag)

**When**: User runs with `--force`  
**Output**: Display duplicates and merges, skip all prompts

Same structure as Mode 2, but without "Proceed with this merge?" prompts. Merges happen automatically.

#### Mode 4: No Duplicates

**When**: Scan finds no case-insensitive duplicates  
**Output**: Simple success message

```
✓ No duplicate case-insensitive folders found
```

---

## Error Output Specification

### Error Format

All errors use this format:

```
Error: {description}
```

Example:
```
Error: Path does not exist: /nonexistent/path
```

### Error Messages by Scenario

| Scenario | Exit Code | Message |
|----------|-----------|---------|
| Missing path argument | 2 | Path argument is required. Usage: gts system merge-folders /path/to/scan |
| Path doesn't exist | 1 | Error: Path does not exist: /path |
| Path is a file | 1 | Error: Path is not a directory: /file.txt |
| Permission denied | 1 | Error: Failed to scan directory: Permission denied: /path/to/folder |
| Merge failed | 1 | Error: Failed to merge Mods: [reason] |

### Error Message Examples

```
Error: Path does not exist: /home/user/nonexistent
```

```
Error: Path is not a directory: /etc/passwd
```

```
Error: Failed to scan directory: Permission denied when reading /private/folder
```

---

## Input Validation

### Path Validation

1. Check path argument provided (non-empty string)
2. Convert to Path object
3. Verify exists: `path.exists()`
4. Verify is directory: `path.is_dir()`
5. Raise error with clear message if any check fails

### Flag Validation

- `--preview` and `--force` are boolean flags (Typer handles validation)
- Cannot use `--preview` and `--force` together (no conflict, both valid but different behavior)

---

## User Interaction Contract

### Prompts

**Merge Confirmation Prompt**:
```
Proceed with this merge? [y/N]:
```
- Default (empty input): No
- Valid responses: y, yes, Y, YES, n, no, N, NO
- Invalid input: Re-prompt
- Ctrl+C: Exit cleanly with code 1

**Target Selection Prompt** (when multiple non-lowercase variants):
```
No all-lowercase variant found for: Mods, moDs, ModS
Which folder should be the target?

  1. Mods
  2. moDs
  3. ModS

Select (1-3) or press Ctrl+C to cancel:
```
- Valid responses: 1-N (where N = number of variants)
- Invalid input: Re-prompt
- Ctrl+C: Exit cleanly with code 1

### User Control

- Users can press Ctrl+C at any prompt to cancel operation
- Cancellation should not modify filesystem
- Exit message on cancel: "Operation cancelled by user" (info level, not error)

---

## Data Flow Contract

### Input to Output

```
User Input (PATH, FLAGS)
    ↓
Validation
    ↓
Scan Filesystem
    ↓
Create DuplicateGroup objects
    ↓
Display & Prompt
    ↓
Create MergeOperation objects (if continuing)
    ↓
Execute Merges (if not preview mode)
    ↓
Display Summary
    ↓
Exit with appropriate code
```

### Example Flow with Data

```
Input:  gts system merge-folders /home/data --preview
↓
Validation: ✓ Path exists, is directory
↓
Scan: Found 2 duplicate groups
↓
Groups: [
  DuplicateGroup(parent=/home/data, variants=["mods", "Mods"]),
  DuplicateGroup(parent=/home/data, variants=["configs", "Configs"])
]
↓
Display: Show both groups
↓
Exit Code: 0 (success)
```

---

## Testing Implications

### Contract Tests (test_merge_contract.py)

- ✅ Command registered and available via `gts system merge-folders`
- ✅ `--help` displays usage information
- ✅ PATH argument required; error if missing
- ✅ Invalid path produces appropriate error message
- ✅ `--preview` flag works without prompts
- ✅ `--force` flag works without prompts
- ✅ Merge confirmation prompt appears in interactive mode
- ✅ Target selection prompt appears when no lowercase variant
- ✅ Exit code 0 on success
- ✅ Exit code 1 on error
- ✅ Ctrl+C handled gracefully

### Output Format Tests

- ✅ Duplicate groups displayed in table format
- ✅ Error messages include "Error:" prefix
- ✅ Success messages include "✓" checkmark
- ✅ Info messages include "ℹ" icon
- ✅ Summary panel displays statistics correctly

---

## Backward Compatibility

This is a new command; no backward compatibility concerns.

---

## Future API Extensions

### Phase 2+: Dry-Run Output

Potential future flag:
```
gts system merge-folders /path --dry-run
```
Would show what would be done without prompting (different from `--preview` which shows discovery only).

### Phase 3+: JSON Output

Potential future flag:
```
gts system merge-folders /path --json
```
Would output all results as JSON for scripting/integration.

---

## Contract Validation Checklist

- ✅ Command schema matches Typer conventions
- ✅ Arguments and options match specification
- ✅ Help text is clear and actionable
- ✅ Exit codes are standard (0/1/2)
- ✅ Output uses Rich formatting for consistency
- ✅ Error messages are actionable
- ✅ User prompts are clear and responsive
- ✅ Data flow is documented and testable
- ✅ Tests can verify all aspects of contract
- ✅ Graceful error handling (no stack traces to users)

**Status**: ✅ CLI contract complete and ready for implementation
