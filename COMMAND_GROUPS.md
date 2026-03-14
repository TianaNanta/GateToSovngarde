# Command Groups Architecture

## Overview

The GateToSovngarde CLI uses **hierarchical command groups** to organize functionality into logical categories. This document describes the grouping strategy, implementation approach, and extension patterns.

## Grouping Strategy (Selected: Option A)

### Command Groups

#### Database Group (`gts database ...`)
Manages database operations related to GateToSovngarde version databases.

**Rationale**:
- Both import and versions commands operate on GTS version databases
- Provides clear logical separation for future database-related commands
- Maintains semantic clarity: "gts database import" vs generic "gts import"

**Commands**:
- `gts database import` - Import mods from a GTS version database
- `gts database versions` - List available GTS version databases
- Future: `gts database validate`, `gts database update`, etc.

### Future Groups (Deferred)

- **Config Group** (`gts config ...`): Configuration management commands
- **Mod Group** (`gts mod ...`): Individual mod operations

## Implementation Architecture

### Structure Overview

```
src/cli/
├── main.py                    # Entry point, version handling
├── commands/
│   ├── __init__.py           # Command registration (manages groups)
│   ├── groups/
│   │   ├── __init__.py       # Group initialization
│   │   ├── database.py       # Database group definition
│   │   └── README.md         # Group extension guide
│   ├── database/
│   │   ├── __init__.py
│   │   ├── import_cmd.py     # Import command
│   │   └── versions_cmd.py   # Versions command
│   └── README.md             # Overall extension guide
```

### Typer Sub-App Pattern

Each group uses a **Typer sub-application** (sub-app) pattern:

```python
# groups/database.py
database_app = typer.Typer(help="Manage GateToSovngarde version databases")

@database_app.command()
def import_cmd(...):
    """Import mods from database"""
    pass

@database_app.command(name="versions")
def versions(...):
    """List available versions"""
    pass

# In commands/__init__.py
register_commands(app):
    app.add_typer(database_app, name="database")
```

Result:
```
$ gts database --help
$ gts database import GTSv101 /src /dst
$ gts database versions
```

### Registration Flow

1. **Tier 1: Groups** (`commands/__init__.py`)
   - Creates group sub-apps
   - Registers groups with main app

2. **Tier 2: Commands** (`commands/groups/database.py`)
   - Defines group-specific commands
   - Imports commands from group modules

3. **Tier 3: Implementation** (`commands/database/import_cmd.py`)
   - Individual command implementations
   - Business logic and validation

## Help Text Output

### Main Help
```
$ gts --help
 Usage: gts [OPTIONS] COMMAND [ARGS]...

 GateToSovngarde CLI - Mod management tools

╭─ Commands ────────────────────────────────────────╮
│ database    Manage GateToSovngarde version...     │
╰───────────────────────────────────────────────────╯
```

### Group Help
```
$ gts database --help
 Usage: gts database [OPTIONS] COMMAND [ARGS]...

 Manage GateToSovngarde version databases

╭─ Commands ────────────────────────────────────────╮
│ import      Import mods from database version    │
│ versions    List available GTS versions           │
╰───────────────────────────────────────────────────╯
```

### Command Help
```
$ gts database import --help
 Usage: gts database import [OPTIONS] VERSION SOURCE DEST

 Import mods from a GTS version database...
 
 Arguments:
  VERSION     [required]
  SOURCE      [required]
  DEST        [required]
```

## Exit Codes

The grouped commands maintain consistent exit code behavior:

- **0**: Success
- **1**: Validation error (user error)
- **2**: Operation error (system error)

## Backward Compatibility

In this implementation, **no backward compatibility aliases are maintained**. The previous flat `gts import` command is fully replaced by `gts database import`.

If backward compatibility is needed in the future, flat aliases can be added at the main app level without affecting the grouped structure.

## Extension Guide for New Groups

### Creating a New Group

1. **Create group definition** (`commands/groups/mygroup.py`):
```python
import typer
from mygroup import cmd1, cmd2

mygroup_app = typer.Typer(help="Group description")

@mygroup_app.command()
def cmd1(...):
    """Command 1 description"""
    pass

@mygroup_app.command()
def cmd2(...):
    """Command 2 description"""
    pass
```

2. **Update registration** (`commands/__init__.py`):
```python
from .groups.mygroup import mygroup_app

def register_commands(app: typer.Typer) -> None:
    app.add_typer(database_app, name="database")
    app.add_typer(mygroup_app, name="mygroup")
```

3. **Create command module** (`commands/mygroup/cmd1.py`):
```python
def cmd1(...):
    """Full docstring for help text"""
    pass
```

4. **Add tests** (`tests/integration/test_mygroup_commands.py`)

## Migration Path

### Current State (Before Refactoring)
```
gts import         # Flat command
gts versions       # Flat command
```

### New State (After Refactoring)
```
gts database import    # Grouped command
gts database versions  # Grouped command
```

### Future Extensibility
```
gts database import
gts database versions
gts database validate  # New command (easy to add)
gts config set        # New group with new commands
gts mod list          # New group with new commands
```

## Implementation Details

### Command Ordering
- Groups appear in help in registration order
- Commands within groups appear in registration order
- Alphabetical ordering is not enforced (allows semantic ordering)

### Name Mapping
- Group name: `database` (in `add_typer(app, name="database")`)
- Command function name: `import_cmd`, `versions`
- Command CLI name: `import`, `versions` (in `@app.command(name="...")`)

This separation allows:
- Unique Python function names (no collisions)
- Clean CLI names
- Flexible group organization

### Help Auto-Generation
- Group help: From `typer.Typer(help="...")` parameter
- Command help: From command function docstring
- Argument descriptions: From type hints and `typer.Argument/Option` help parameters

## Testing Strategy

### Test Organization
```
tests/
├── integration/
│   ├── test_command_groups.py        # Group structure tests
│   ├── test_database_commands.py     # Database group tests
│   └── test_*_commands.py            # Other group tests
```

### Test Coverage
- Group discovery and help
- Command execution within groups
- Argument validation
- Error handling
- Exit codes

## Performance Considerations

- Sub-apps are lazy-loaded by Typer only when needed
- No performance overhead for grouping structure
- Registration happens once at app startup

## Future Enhancements

### Nested Groups (Typer-supported)
If deeper hierarchy is needed:
```
gts database import      # Current: 2 levels
gts database set key     # Current: 2 levels
gts config db set        # Future: 3 levels (database within config)
```

### Aliases (Custom implementation)
For backward compatibility or convenience:
```
gts import               # Alias for `gts database import`
```

### Command Ordering
Future: Accept configuration to reorder groups/commands in help.
