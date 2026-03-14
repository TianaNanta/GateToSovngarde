# GateToSovngarde CLI Development Guide

This guide provides instructions for setting up the development environment and contributing to the GateToSovngarde CLI application.

## Quick Start

### Prerequisites
- Python 3.13 or higher
- `uv` package manager (https://docs.astral.sh/uv/)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/TianaNanta/GateToSovngarde.git
   cd GateToSovngarde
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Verify installation**
   ```bash
   uv run gts --help
   ```

### Running Tests

Run the full test suite:
```bash
uv run pytest tests/ -v
```

Run with coverage:
```bash
uv run pytest tests/ --cov=src/cli --cov-report=html
```

Run specific test file:
```bash
uv run pytest tests/unit/test_import_service.py -v
```

Run tests matching pattern:
```bash
uv run pytest tests/ -k "import" -v
```

## Code Quality

### Linting with Ruff

Check for linting issues:
```bash
uv run ruff check src/ tests/
```

Auto-fix linting issues:
```bash
uv run ruff check --fix src/ tests/
```

Format code:
```bash
uv run ruff format src/ tests/
```

## Project Structure

```
GateToSovngarde/
├── src/cli/                          # Main CLI application package
│   ├── __init__.py                   # Package metadata (__version__)
│   ├── main.py                       # Typer app entry point
│   ├── commands/                     # CLI commands
│   │   ├── __init__.py              # Command registration
│   │   └── import_cmd.py            # Import command implementation
│   ├── db/                           # Database loading
│   │   ├── __init__.py
│   │   └── loader.py                # DatabaseLoader class
│   ├── services/                     # Business logic
│   │   └── import_service.py        # Import operation logic
│   ├── models/                       # Data models
│   │   └── import_result.py         # Import result tracking
│   ├── utils/                        # Utility modules
│   │   ├── errors.py                # Exception classes
│   │   └── output.py                # Rich output helpers
│   └── databases/                    # Bundled GTS databases
│       └── gtsv101/
│           └── mods.json            # GTS v1.01 mod database
├── tests/                            # Test suite
│   ├── conftest.py                   # Pytest fixtures
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── contract/                     # Contract tests (CLI interface)
├── pyproject.toml                    # Project configuration
├── MANIFEST.in                       # Package data specification
└── README.md                         # Project overview
```

## Common Development Tasks

### Running the CLI Locally

```bash
uv run gts --help
uv run gts import --help
uv run gts import GTSv101 /source/path /dest/path
```

### Adding a New Command

1. Create new file: `src/cli/commands/newcmd.py`
   ```python
   def newcmd(arg1: str, arg2: str) -> None:
       """Your command description."""
       # Implementation here
       pass
   ```

2. Register in `src/cli/commands/__init__.py`:
   ```python
   from .newcmd import newcmd
   
   def register_commands(app: typer.Typer) -> None:
       app.command(name="newcmd")(newcmd)
   ```

3. Create tests in `tests/unit/test_newcmd.py`

4. Test the command:
   ```bash
   uv run gts newcmd arg1 arg2
   ```

### Building the Package

```bash
# Build wheel and source distribution
uv build

# Outputs to dist/ directory:
# - gatetosovngarde-cli-0.1.0-py3-none-any.whl
# - gatetosovngarde-cli-0.1.0.tar.gz
```

### Testing Package Installation

```bash
# Create test virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/gatetosovngarde-cli-0.1.0-py3-none-any.whl

# Test commands
gts --help
gts import --help
```

## Debugging Tips

### Enable verbose output
```bash
uv run gts import --verbose /source /dest
```

### View test output with print statements
```bash
uv run pytest tests/unit/test_import_service.py -v -s
```

### Debug a specific test
```bash
uv run pytest tests/unit/test_import_service.py::TestImportServiceExecution::test_execute_copies_files -v -s
```

### Check coverage for specific file
```bash
uv run pytest tests/ --cov=src/cli/services --cov-report=term-missing
```

## Git Workflow

1. **Create feature branch** from `002-cli-app-typer`:
   ```bash
   git checkout 002-cli-app-typer
   git pull origin 002-cli-app-typer
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**:
   ```bash
   uv run pytest tests/ -v
   uv run ruff check --fix src/ tests/
   ```

3. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing Standards

- **TDD approach**: Write tests first, then implementation
- **Test levels**: Unit → Integration → Contract tests
- **Coverage target**: 80%+ code coverage
- **Fixtures**: Use pytest fixtures for reusable test setup
- **Mocking**: Mock external dependencies (database, file I/O)

## Documentation

- **Code docstrings**: Google-style docstrings for all public functions
- **Type hints**: Use full type hints for function parameters and returns
- **Module docstrings**: Describe module purpose at the top of each file
- **README**: Update README.md with new features or commands

## Performance Targets

- Command help display: < 1 second
- CLI startup: < 500ms
- Import command: < 5 seconds for 100 files
- Test suite: < 60 seconds total

## Troubleshooting

### ImportError: No module named 'cli'
- Ensure you're using `uv run` to execute Python with proper environment
- Run `uv sync` to install all dependencies

### Database not found when running from source
- Ensure database files are in `src/cli/databases/gtsv101/mods.json`
- The importlib.resources loader looks for bundled databases

### Tests fail with "mock database" issues
- Ensure tests explicitly request `use_mock_database_for_tests` fixture
- Never use autouse fixtures that monkey-patch DatabaseLoader for all tests

### Permission denied during installation
- Ensure virtual environment has write permissions
- Try using a fresh virtual environment

## Getting Help

- Check specs/002-cli-app-typer/ for design decisions and plans
- Review existing tests for usage patterns
- See data-model.md for data structure documentation
- Check contracts/commands.md for CLI interface specifications
