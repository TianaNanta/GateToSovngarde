# Changelog

All notable changes to GateToSovngarde CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-14

### Initial Release

This is the first production release of the GateToSovngarde CLI tool for Skyrim SE mod management.

#### Added

**Core Features**
- `gts database import` command: Import GateToSovngarde version databases with mod files
  - Support for multiple archive formats (7z, rar, zip)
  - Automatic destination directory creation
  - Optional force overwrite mode for existing files
  - Verbose output with detailed operation reporting

- `gts database versions` command: List available GateToSovngarde database versions
  - Simple list output (default)
  - Detailed table view with `--verbose` flag
  - Database information: version ID, release date, mod count
  - Filtering and search capabilities (extensible)

**Command Groups Architecture**
- Hierarchical command organization with `gts database` group
- Clean CLI namespace preventing future command conflicts
- Extensible pattern for adding new command groups
- Full help system integration for discovery and documentation

**User Experience**
- Rich terminal output with colors and formatting
  - Green checkmarks for successful operations
  - Red X marks for errors
  - Colorized tables for structured data
  - Responsive to terminal width

- Comprehensive error handling
  - Clear, actionable error messages with suggested fixes
  - Appropriate exit codes (0=success, 1=validation error, 2=operation error)
  - Validation errors show available options
  - Operation errors include detailed context

- Full help system
  - Main command help: `gts --help`
  - Group help: `gts database --help`
  - Command help: `gts database import --help`
  - Detailed parameter documentation
  - Usage examples in docstrings

**Quality Assurance**
- 132 comprehensive tests across unit, integration, and contract testing
  - Unit tests: 23 tests for core components
  - Contract tests: 40 tests for CLI interface validation
  - Integration tests: 69 tests for workflows and user stories
  - 63%+ code coverage on executed code

- Code quality standards
  - 100% docstring coverage on public API
  - Zero ruff linting errors
  - Type hints on all functions
  - Python 3.13 best practices
  - Clear, self-documenting code

- Complete documentation
  - User-facing README with examples
  - Developer guide (DEVELOPMENT.md)
  - Architecture documentation (COMMAND_GROUPS.md)
  - API specification documents
  - Comprehensive docstrings

#### Technical Details

**Technology Stack**
- Python 3.13
- Typer 0.9+ (CLI framework)
- Rich 13.7+ (terminal output)
- uv (package management)
- pytest (testing)
- ruff (linting)

**Architecture**
- Service-based business logic (ImportService, DatabaseLoader)
- Clear separation of concerns (CLI, Services, Models, Utils)
- No circular dependencies
- Extensible command group pattern

**Performance**
- Help display: <1 second
- Version display: <100ms
- Command parsing: <100ms
- Database loading: Deferred and cached

**Compatibility**
- Windows 10+
- macOS 10.14+
- Linux (all distributions)
- Python 3.13+

#### Known Limitations

- Currently supports 2 command groups (database)
- Database versions are bundled as static files
- No network synchronization with remote databases
- No GUI interface (CLI only)

#### Breaking Changes

None - this is the initial release.

#### Dependencies

- **Runtime**: typer[all]>=0.9.0, rich>=13.7.0
- **Development**: pytest>=7.0, pytest-cov>=4.0, ruff>=0.3.0, mypy>=1.0

---

## Version History Summary

**v0.1.0 - Initial Release (2026-03-14)**
- Complete CLI application with command groups
- Database import and version listing functionality
- Comprehensive testing and documentation
- Production-ready quality standards

## Notes for Users

### Installation

```bash
pip install gatesovngarde
```

### Quick Start

```bash
# Show available commands
gts --help

# List available database versions
gts database versions

# Import a version database
gts database import GTSv101 /path/to/source /path/to/destination
```

### Upgrading from Previous Versions

This is the initial release. No upgrade path exists yet.

### Reporting Issues

If you encounter any issues, please report them at:
https://github.com/anomalyco/opencode/issues

Include:
- Your Python version
- Your operating system
- The command you ran
- The error message you received
- Steps to reproduce the issue
