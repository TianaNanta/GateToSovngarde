# Quickstart: GateToSovngarde CLI Development

**Date**: 2026-03-14  
**Purpose**: Get developers up and running with CLI development and testing  
**Audience**: Contributors implementing CLI commands and features

---

## Prerequisites

- Python 3.13+ (check: `python --version`)
- uv package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git (for repository access)

---

## Initial Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/TianaNanta/GateToSovngarde.git
cd GateToSovngarde
git checkout 002-cli-app-typer
```

### 2. Install Development Environment

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies using uv
uv sync

# Verify installation
uv run python --version  # Should show Python 3.13.x
```

### 3. Install Development Tools

```bash
# Add development dependencies (already in uv.lock)
uv add --dev pytest pytest-cov typer rich

# Verify Typer installation
uv run python -c "import typer; print(typer.__version__)"
```

---

## Project Structure Overview

```
src/
├── cli/                          # CLI package (main entry point)
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Typer app and entry point
│   ├── commands/                # Individual command modules
│   │   ├── __init__.py
│   │   └── import_cmd.py        # Mod importer command
│   ├── db/                      # Database access
│   │   ├── __init__.py
│   │   └── loader.py            # Database loader class
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── errors.py            # Custom exceptions
│       └── output.py            # Rich output helpers

tests/
├── unit/                        # Unit tests
│   ├── test_cli_main.py
│   ├── test_import_cmd.py
│   └── test_db_loader.py
├── integration/                 # Integration tests
│   └── test_import_workflow.py
└── contract/                    # Contract tests
    └── test_cli_contracts.py

databases/                       # Bundled GTS databases
├── gtsv101/
│   └── mods.json               # Mod metadata for GTSv101
└── [other_versions]/

pyproject.toml                  # Package configuration
uv.lock                         # Dependency lock file
```

---

## Running the CLI

### As Installed Command

After building and installing the package:

```bash
# Display help
gts --help

# Show version
gts --version

# Run import command
gts import GTSv101 /mnt/data/source /mnt/data/dest

# Import with verbose output
gts import GTSv101 /mnt/data/source /mnt/data/dest --verbose

# Validate without importing
gts import GTSv101 /mnt/data/source /mnt/data/dest --validate-only
```

### During Development (via uv run)

```bash
# Display help
uv run gts --help

# Or run main.py directly
uv run python -m src.cli.main --help

# With arguments
uv run gts import GTSv101 /test/source /test/dest
```

---

## Testing

### Running All Tests

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=src/cli --cov-report=html

# Run tests from specific file
uv run pytest tests/unit/test_import_cmd.py -v

# Run only integration tests
uv run pytest tests/integration/ -v
```

### Writing Tests

**Unit Test Example** (`tests/unit/test_import_cmd.py`):
```python
import pytest
from typer.testing import CliRunner
from src.cli.main import app

runner = CliRunner()

def test_import_with_valid_version():
    """Test import command with valid GTS version."""
    result = runner.invoke(app, [
        "import",
        "GTSv101",
        "/tmp/source",
        "/tmp/dest"
    ])
    assert result.exit_code == 0
    assert "Import complete" in result.stdout

def test_import_with_invalid_version():
    """Test import command rejects non-existent version."""
    result = runner.invoke(app, [
        "import",
        "GTSv999",
        "/tmp/source",
        "/tmp/dest"
    ])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()
```

**Integration Test Example** (`tests/integration/test_import_workflow.py`):
```python
import pytest
from pathlib import Path
import tempfile
from typer.testing import CliRunner
from src.cli.main import app

runner = CliRunner()

def test_import_complete_workflow():
    """Test complete import workflow with temporary directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "source"
        dest = Path(tmpdir) / "dest"
        source.mkdir()
        dest.mkdir()
        
        # Create test file in source
        (source / "test_mod.esp").write_text("dummy content")
        
        result = runner.invoke(app, [
            "import",
            "GTSv101",
            str(source),
            str(dest)
        ])
        
        assert result.exit_code == 0
        assert (dest / "test_mod.esp").exists()
```

**Contract Test Example** (`tests/contract/test_cli_contracts.py`):
```python
from typer.testing import CliRunner
from src.cli.main import app

runner = CliRunner()

def test_main_help_contains_import_command():
    """Contract: Main help must list 'import' command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "import" in result.stdout.lower()
    assert "Import mods" in result.stdout

def test_import_help_shows_all_arguments():
    """Contract: Import help must document all arguments."""
    result = runner.invoke(app, ["import", "--help"])
    assert result.exit_code == 0
    assert "VERSION" in result.stdout
    assert "SOURCE_PATH" in result.stdout
    assert "DEST_PATH" in result.stdout
```

---

## Common Development Tasks

### Adding a New Command

1. **Create command module** (`src/cli/commands/newcmd.py`):
```python
import typer
from typing import Optional
from pathlib import Path

def newcmd(
    arg1: str = typer.Argument(..., help="First argument"),
    arg2: Path = typer.Argument(..., help="Second argument"),
    opt1: Optional[str] = typer.Option(None, help="Optional flag"),
):
    """Brief description of newcmd."""
    typer.echo(f"Running newcmd with {arg1}, {arg2}")
```

2. **Register in main app** (`src/cli/main.py`):
```python
from src.cli.commands.newcmd import newcmd

app = typer.Typer()
app.command()(import_cmd)
app.command()(newcmd)  # Add new command
```

3. **Write tests** (`tests/unit/test_newcmd.py`):
```python
from typer.testing import CliRunner
from src.cli.main import app

runner = CliRunner()

def test_newcmd_basic():
    result = runner.invoke(app, ["newcmd", "value1", "/path/to/arg2"])
    assert result.exit_code == 0
```

4. **Verify help**:
```bash
uv run gts newcmd --help
```

### Adding Database Version

1. **Create version directory**:
```bash
mkdir -p databases/gtsv102
```

2. **Add mods.json**:
```bash
cat > databases/gtsv102/mods.json << 'EOF'
{
  "version_id": "GTSv102",
  "version_name": "GateToSovngarde v1.02",
  "created_date": "2026-03-14",
  "mods": [
    {
      "id": "mod_001",
      "name": "Example Mod",
      "author": "Author Name",
      "version": "1.0.0",
      "required_files": ["file.esp"],
      "tags": ["quest"]
    }
  ]
}
EOF
```

3. **Update package** (in `pyproject.toml`, include-package-data):
```bash
# Rebuild package to include new database
uv build
```

### Running Linting and Type Checks

```bash
# Run Ruff linter (already configured)
uv run ruff check src/ tests/

# Run type checking with mypy (if added)
uv run mypy src/cli/

# Format code
uv run ruff format src/ tests/
```

---

## Building the Package

### Local Build

```bash
# Build wheel and source distributions
uv build

# Output will be in dist/
# - gatetosovngarde-cli-0.1.0-py3-none-any.whl
# - gatetosovngarde-cli-0.1.0.tar.gz
```

### Testing Built Package

```bash
# Create virtual environment and install built wheel
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install dist/gatetosovngarde-cli-0.1.0-py3-none-any.whl

# Test installed command
gts --help
gts import --help
gts import GTSv101 /tmp/source /tmp/dest
```

---

## Installation Methods

### Method 1: Via PyPI (Production)

Once published to PyPI:
```bash
# Install as user tool
uv tool install gatetosovngarde-cli

# Test
gts --help
```

### Method 2: Via GitHub (Development)

Install directly from repository:
```bash
# As uv tool
uv tool install gatetosovngarde-cli --from git+https://github.com/TianaNanta/GateToSovngarde.git

# As package in project
uv add gatetosovngarde-cli @ git+https://github.com/TianaNanta/GateToSovngarde.git

# Test
gts --help
```

### Method 3: Development Install

```bash
# Clone repo
git clone https://github.com/TianaNanta/GateToSovngarde.git
cd GateToSovngarde

# Install in development mode (editable)
uv sync

# Run directly
uv run gts --help
```

---

## Troubleshooting

### "Command not found: gts"

**Solution**: Package not installed. Use development approach:
```bash
uv run gts --help
```

### "ModuleNotFoundError: No module named 'typer'"

**Solution**: Dependencies not installed:
```bash
uv sync
uv add typer
```

### "GTS version 'GTSv101' not found"

**Solution**: Database not bundled. Check:
```bash
ls -la databases/gtsv101/
```

Database files must exist in `databases/` directory and be included in package.

### Test failures after changes

**Solution**: Run full test suite:
```bash
uv run pytest tests/ -v --tb=short
```

Check test output for specific failures and review data-model.md for entity contracts.

---

## Next Steps

1. **Review contracts**: Read [contracts/commands.md](contracts/commands.md) for CLI interface definitions
2. **Review data model**: Read [data-model.md](data-model.md) for entity specifications
3. **Start implementation**: Begin with unit tests (TDD approach)
4. **Regular testing**: Run tests frequently during development
5. **Add new commands**: Follow the "Adding a New Command" section above

---

## Useful Links

- **Typer Documentation**: https://typer.tiangolo.com/
- **uv Package Manager**: https://docs.astral.sh/uv/
- **Rich Documentation**: https://rich.readthedocs.io/
- **pytest Documentation**: https://docs.pytest.org/
- **Project Repository**: https://github.com/TianaNanta/GateToSovngarde

---

## Questions?

Check the specification and implementation plan:
- Feature Spec: [spec.md](spec.md)
- Implementation Plan: [plan.md](plan.md)
- Research & Decisions: [research.md](research.md)
- Data Models: [data-model.md](data-model.md)
- Command Contracts: [contracts/commands.md](contracts/commands.md)

