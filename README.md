# GateToSovngarde CLI

A comprehensive command-line interface for managing the Gate To Sovngarde modlist. Import mods efficiently from archived sources to your destination directory with version management, error recovery, and duplicate folder merging.

## Features

✨ **Mod Management**
- Import mods from multiple archive formats (.7z, .rar, .zip, .tar.xz, .tar.gz, .tar, .iso)
- Version-specific mod databases for different GateToSovngarde versions
- Flexible archive format detection with fallback support

🔄 **Duplicate Folder Management**
- Scan directories for case-insensitive duplicate folders (e.g., `mods`, `Mods`, `MODS`)
- Automatic merge with lowercase preference
- Interactive user choice when no lowercase variant exists
- Preview merge impact before committing
- Handle file conflicts gracefully

🛡️ **Robust Operation**
- Comprehensive error reporting with recovery suggestions
- Permission and access validation
- Graceful handling of missing or corrupted files
- Force overwrite mode for existing files
- Atomic file operations (no data loss)

📊 **User-Friendly**
- Interactive mode with helpful prompts
- Rich console output with progress tracking
- Detailed help system
- Verbose mode for debugging

## Installation

### Via PyPI
```bash
pip install gatetosovngarde-cli
```

### Via UV Package Manager
```bash
uv tool install gatetosovngarde-cli
```

### From Source
```bash
git clone https://github.com/TianaNanta/GateToSovngarde.git
cd GateToSovngarde
uv sync
uv run gts --help
```

## Quick Start

### Get Help
```bash
gts --help
gts import --help
```

### Import Mods (Interactive Mode)
```bash
gts import
# Follow prompts for version, source, and destination
```

### Import Mods (Direct)
```bash
gts import GTSv101 /path/to/mod/source /path/to/mod/destination
```

### Import with Options
```bash
# Force overwrite existing files
gts import GTSv101 /source /dest --force

# Show detailed progress
gts import GTSv101 /source /dest --verbose

# Combine options
gts import GTSv101 /source /dest -f -v
```

## Usage Examples

### Basic Import
```bash
gts import GTSv101 ~/Mods/source ~/Mods/imported
```

**Output:**
```
✓ Import complete (GTSv101)
  Mods imported: 1954
  Files copied: 1954
  Duration: 2m 34s
```

### Handling Errors
If some mod files are missing:
```bash
gts import GTSv101 ~/Mods/source ~/Mods/imported
```

**Output:**
```
✗ Import failed (GTSv101)
  Files copied: 1950
  Errors: 4

Errors encountered:
  [file_not_found] mod_123: Required archive file not found
    → Ensure ModName archive exists in ~/Mods/source

  [permission_denied] mod_456: Permission denied accessing file
    → Check write permissions for ~/Mods/imported
```

### Force Overwrite
```bash
gts import GTSv101 ~/Mods/source ~/Mods/imported --force
```

## System Utilities

### Merge Duplicate Case-Insensitive Folders
```bash
# Preview duplicates (safe, no changes)
gts system merge-folders /path/to/scan --preview

# Interactive merge (with confirmation)
gts system merge-folders /path/to/scan

# Force merge (no prompts, auto-merge using default rules)
gts system merge-folders /path/to/scan --force
```

**Examples:**
```bash
# Find and preview duplicates in Mods folder
gts system merge-folders ~/Mods --preview

# Merge duplicates with user confirmation
gts system merge-folders ~/Mods

# Auto-merge all duplicates (useful for scripts)
gts system merge-folders ~/Mods --force
```

**How it works:**
1. Scans directory for case-insensitive duplicate folders
2. Auto-selects lowercase variant as target (e.g., `mods` over `Mods`)
3. Shows preview of what will be merged
4. Prompts for confirmation (or uses --force to skip)
5. Moves all files and deletes source folders

## Supported GTS Versions

| Version | Database | Mods | Release |
|---------|----------|------|---------|
| GTSv101 | ✅ | 1954 | Mar 2026 |

## Archive Formats Supported

- `.7z` - 7-Zip
- `.rar` - RAR
- `.zip` - ZIP
- `.tar.xz` - TAR LZMA
- `.tar.gz` - TAR gzip
- `.tar` - TAR uncompressed
- `.iso` - ISO image

## Architecture

The CLI is built with:
- **Typer** - Modern CLI framework with auto-generated help
- **Rich** - Beautiful console output and formatting
- **Python 3.13** - Latest Python features
- **UV** - Fast Python package manager

For more details, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Local development setup
- Running tests
- Code quality checks
- Contributing guidelines
- Debugging tips

### Quick Dev Setup
```bash
git clone https://github.com/TianaNanta/GateToSovngarde.git
cd GateToSovngarde
uv sync
uv run pytest tests/ -v
```

## Project Status

**Current Release**: v0.3.0 (Alpha)
- ✅ Phase 1-4: Core CLI framework and import functionality
- ✅ Phase 5: Package configuration and distribution
- ✅ Phase 6-7: Extensibility and command organization
- ✅ Phase 8: Polish and production hardening
- ✅ Feature 003: Merge duplicate case-insensitive folders

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please see [DEVELOPMENT.md](DEVELOPMENT.md) for guidelines.

## Credits

- **Author**: TianaNanta
- **Framework**: Typer + Rich + Python 3.13
- **Package Manager**: UV

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in specs/
- See DEVELOPMENT.md for troubleshooting

## Changelog

### v0.3.0 (Mar 2026)
- ✨ **New Feature**: Merge duplicate case-insensitive folders
  - Scan directories for duplicate folders (mods, Mods, MODS)
  - Automatic merge with lowercase preference
  - Interactive user choice when no lowercase variant exists
  - Preview merge impact before committing
  - Handle file conflicts gracefully
- 🔄 Added system command group for file utilities
- 🧪 Added comprehensive test suite (202 tests)
- ⚙️ Added GitHub Actions for CI/CD

### v0.1.0 (Mar 2026)
- Initial release with import command
- Support for GTSv101 mod database
- Archive format detection and handling
- Interactive mode support
- Comprehensive error reporting
