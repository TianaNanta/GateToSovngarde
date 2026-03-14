# Quickstart: Python Mod Importer

## Prerequisites

- Python 3.13 or higher
- Rich library for beautiful logging

## Installation

```bash
# Install dependencies
pip install rich

# Or if using uv
uv pip install rich
```

## Project Structure

```
GateToSovngarde/
├── database/
│   └── GTSv101.txt          # Mod list file
├── src/
│   └── mod_importer.py      # Main script
└── logs/                    # Created automatically
```

## Usage

1. **Run the script:**
   ```bash
   python src/mod_importer.py
   ```

2. **Enter source directory** when prompted (e.g., `/run/media/nanta/Nanta/Skyrim/skyrimse`)

3. **Enter destination directory** when prompted (e.g., `/mnt/data/Mods`)

4. **Watch the beautiful progress** as mods are copied

5. **Check the log file** in the `logs/` folder after completion

## Log Output

- **Console**: Beautiful colored output with Rich formatting
- **File**: Timestamped log file in `logs/` directory

## Example Output

```
╭──────────────────────────────────────────────────╮
│  🎮 Mod Importer - Gate To Sovngarde            │
╰──────────────────────────────────────────────────╯

✓ Reading mod list from database/GTSv101.txt
✓ Found 987 mods to search

🔍 Searching for mods...
  ✓ Found: 00 - Skyrim Horse Overhaul SE
  ✓ Found: 1.2.1-1668-1-2-1
  ...

╭──────────────────────────────────────────────────╮
│  📊 Summary                                      │
│   • Total mods searched: 987                     │
│   • Files copied: 245                           │
│   • Duration: 45.2s                             │
╰──────────────────────────────────────────────────╯

✓ Log saved to: logs/mod_importer_20260310_143022.log
```

## Troubleshooting

- **Source directory not found**: Check the path and try again
- **No files found**: Verify mods exist in source directory
- **Permission errors**: Ensure write access to destination directory
