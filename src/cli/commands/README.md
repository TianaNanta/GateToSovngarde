# Command Registration Guide

This guide explains how to add new commands to the GateToSovngarde CLI framework without modifying the core framework code.

## Quick Start

1. **Create a new command file** in this directory
2. **Implement your command function** with proper docstring
3. **Register it** in `__init__.py`
4. **Test it** with pytest
5. **Run it** with `gts your-command`

## Command Structure

### File Organization

```
src/cli/commands/
├── __init__.py              # Command registration (modify here)
├── import_cmd.py            # Existing import command (example)
├── your_new_cmd.py          # Your new command
└── another_cmd.py           # Another new command
```

### Anatomy of a Command

```python
# src/cli/commands/your_cmd.py
"""Brief description of what your command does.

More detailed explanation of functionality, use cases, and examples.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..db import DatabaseLoader
from ..models.import_result import ImportResult
from ..utils.errors import ValidationError, OperationError
from ..utils.output import success, error

# Reusable console instance
console = Console()


def your_cmd(
    required_arg: str = typer.Argument(..., help="Description of required argument"),
    optional_arg: str = typer.Argument(None, help="Description of optional argument"),
    source_path: Path = typer.Argument(..., help="Path to source directory"),
    option_flag: bool = typer.Option(False, "--force", "-f", help="Force operation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Your command description (shown in help text).

    This appears in the help system and should be clear and concise.
    Typer automatically generates help from this docstring.

    The command loads data, validates inputs, performs operation,
    and reports results with appropriate error handling.

    Example:
        $ gts your-cmd /path/to/source --force --verbose

    Args:
        required_arg: Description with type hint
        optional_arg: Optional with default None
        source_path: File path for directory
        option_flag: Boolean flag for optional behavior
        verbose: Enable detailed output

    Raises:
        ValidationError: If arguments are invalid
        OperationError: If operation fails
    """
    try:
        # 1. VALIDATE INPUTS
        if not source_path.exists():
            raise ValidationError(f"Source path not found: {source_path}")

        if not source_path.is_dir():
            raise ValidationError(f"Source path is not a directory: {source_path}")

        # 2. LOAD DEPENDENCIES (if needed)
        loader = DatabaseLoader()
        # db = loader.get_version("GTSv101")

        # 3. PERFORM OPERATION
        console.print(f"Processing {required_arg}...")

        # Do actual work here
        result_count = 5  # Example result

        # 4. REPORT SUCCESS
        success(f"✓ Operation complete")
        console.print(f"  Processed: {result_count} items")

    except ValidationError as e:
        error(f"✗ Validation failed: {e}")
        raise typer.Exit(code=1)

    except OperationError as e:
        error(f"✗ Operation failed: {e}")
        raise typer.Exit(code=2)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Operation interrupted by user[/yellow]")
        raise typer.Exit(code=2)
```

## Registration Pattern

### Step 1: Create Your Command File

Create `src/cli/commands/your_cmd.py` with the function above.

### Step 2: Register in `__init__.py`

Edit `src/cli/commands/__init__.py`:

```python
"""Commands module for GateToSovngarde CLI."""

import typer

from .import_cmd import import_cmd
from .your_cmd import your_cmd  # ← Add this line


def register_commands(app: typer.Typer) -> None:
    """Register all CLI commands with the Typer application."""
    
    # Existing command
    app.command(name="import")(import_cmd)
    
    # Your new command
    app.command(name="your-cmd")(your_cmd)  # ← Add this line
```

### Step 3: Verify Command Registration

```bash
uv run gts --help
# Should now show: your-cmd  Your command description
```

### Step 4: Run Your Command

```bash
uv run gts your-cmd --help
uv run gts your-cmd /path/to/source
```

## Best Practices

### 1. Argument Validation

Always validate arguments before performing operations:

```python
def your_cmd(source_path: Path) -> None:
    # ✓ GOOD: Validate early
    if not source_path.exists():
        raise ValidationError(f"Path not found: {source_path}")
    
    # ✓ GOOD: Check type/format
    if not source_path.is_dir():
        raise ValidationError(f"Expected directory, got file: {source_path}")
    
    # Now safe to proceed
    process_directory(source_path)
```

### 2. Error Handling

Use the exception hierarchy for proper error handling:

```python
from ..utils.errors import ValidationError, OperationError

try:
    # Validation errors: code 1 (user input issue)
    if invalid_input:
        raise ValidationError("Invalid input")
    
    # Operation errors: code 2 (system/IO issue)
    result = perform_operation()
    
except ValidationError as e:
    error(f"Validation failed: {e}")
    raise typer.Exit(code=1)
    
except OperationError as e:
    error(f"Operation failed: {e}")
    raise typer.Exit(code=2)
```

### 3. User Output

Use Rich for beautiful, consistent output:

```python
from ..utils.output import success, error, progress
from rich.console import Console

console = Console()

# Success messages
success("✓ Operation complete")

# Error messages
error("✗ Operation failed")

# Progress updates
progress("Processing files...")

# Detailed output
console.print(f"Processed: {count} items")
console.print(f"[green]Success[/green] and [red]Failure[/red]")
```

### 4. Option Naming

Follow Unix conventions for options:

```python
# ✓ GOOD: Single letter for common options
option_flag: bool = typer.Option(False, "--force", "-f")
verbose: bool = typer.Option(False, "--verbose", "-v")
quiet: bool = typer.Option(False, "--quiet", "-q")

# ✓ GOOD: Descriptive names with hyphens
output_format: str = typer.Option("json", "--output-format")
max_workers: int = typer.Option(4, "--max-workers")

# ✗ AVOID: Unclear abbreviations
weird_opt: bool = typer.Option(False, "--wxyz")
```

### 5. Docstrings

Use Google-style docstrings with all sections:

```python
def your_cmd(arg: str) -> None:
    """One-line description.
    
    Longer description with more details about what the command
    does, when to use it, and any important notes.
    
    The docstring is used by Typer to generate help text,
    so make it clear and user-focused.
    
    Example:
        $ gts your-cmd /path/to/source
        Output: Result of operation
    
    Args:
        arg: Description of the argument
    
    Raises:
        ValidationError: If argument is invalid
        OperationError: If operation fails
    """
    pass
```

## Testing Your Command

Create tests in `tests/unit/test_your_cmd.py`:

```python
"""Tests for your command."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app


class TestYourCommand:
    """Test suite for your command."""

    def test_your_cmd_with_valid_input(self) -> None:
        """Test command with valid input."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(app, ["your-cmd", temp_dir])
            assert result.exit_code == 0
            assert "✓" in result.stdout

    def test_your_cmd_invalid_path(self) -> None:
        """Test command with invalid path."""
        runner = CliRunner()
        result = runner.invoke(app, ["your-cmd", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "✗" in result.stdout

    def test_your_cmd_help_displays(self) -> None:
        """Test that help works."""
        runner = CliRunner()
        result = runner.invoke(app, ["your-cmd", "--help"])
        assert result.exit_code == 0
        assert "Description" in result.stdout
```

Run tests:

```bash
uv run pytest tests/unit/test_your_cmd.py -v
```

## Common Patterns

### Pattern: Database Operations

```python
def db_cmd(version: str) -> None:
    """Command that uses database."""
    try:
        loader = DatabaseLoader()
        
        # Validate version exists
        if not loader.validate_version_exists(version):
            raise ValidationError(f"Version not found: {version}")
        
        # Load database
        db = loader.get_version(version)
        
        # Use database
        mods = db.get("mods", [])
        success(f"✓ Found {len(mods)} mods")
        
    except ValidationError as e:
        error(f"Invalid version: {e}")
        raise typer.Exit(code=1)
```

### Pattern: File Operations

```python
def file_cmd(source: Path, dest: Path) -> None:
    """Command that operates on files."""
    try:
        # Validate inputs
        if not source.exists():
            raise ValidationError(f"Source not found: {source}")
        
        if dest.exists():
            raise ValidationError(f"Destination already exists: {dest}")
        
        # Perform operation
        import shutil
        shutil.copy2(source, dest)
        
        success(f"✓ File copied")
        
    except (ValidationError, IOError) as e:
        error(f"File operation failed: {e}")
        raise typer.Exit(code=2)
```

### Pattern: Multiple Files

```python
def batch_cmd(directory: Path) -> None:
    """Command that processes multiple files."""
    try:
        if not directory.is_dir():
            raise ValidationError("Must provide directory")
        
        # Process files
        count = 0
        for file in directory.glob("*.json"):
            process_file(file)
            count += 1
        
        success(f"✓ Processed {count} files")
        
    except ValidationError as e:
        error(f"Batch operation failed: {e}")
        raise typer.Exit(code=1)
```

## Framework Architecture

The command framework ensures:
- **Consistency**: All commands follow the same pattern
- **Maintainability**: New commands don't require framework changes
- **Testability**: Commands can be tested independently
- **User Experience**: Consistent help, errors, and output

### Framework Components

1. **Typer** - CLI framework and auto-generated help
2. **Rich** - Beautiful console output
3. **Error Hierarchy** - Consistent error handling
4. **Output Helpers** - Consistent formatting (success, error, progress)
5. **Database Loader** - Access to GTS databases
6. **Models** - Data structures (ImportResult, etc.)

### Extension Points

To add new functionality, extend:
- **Commands** - Add new `your_cmd.py` files
- **Services** - Add business logic to `services/`
- **Models** - Add data classes to `models/`
- **Utilities** - Add helpers to `utils/`
- **Tests** - Add test files to `tests/`

All while keeping the framework core unchanged!

## Next Steps

1. Copy `command_template.py` to create your command
2. Modify it for your specific needs
3. Register it in `__init__.py`
4. Write tests in `tests/unit/`
5. Test locally with `uv run gts your-cmd`
6. Commit and submit PR

See [DEVELOPMENT.md](../../DEVELOPMENT.md) for more development guidelines.
