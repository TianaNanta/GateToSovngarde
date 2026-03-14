# Data Model: Python Mod Importer

## Entities

### ModEntry
Represents a single mod name from the mod list file.

| Field | Type | Description |
|-------|------|-------------|
| name | string | The mod name/identifier from the list file |

**Validation**: Non-empty string, stripped of whitespace

---

### SourceDirectory
The directory path where mod archives will be searched.

| Field | Type | Description |
|-------|------|-------------|
| path | string | Absolute or relative path to source directory |

**Validation**: Must be a valid, accessible directory

---

### DestinationDirectory
The directory path where matching mods will be copied.

| Field | Type | Description |
|-------|------|-------------|
| path | string | Absolute or relative path to destination directory |

**Validation**: Will be created if it doesn't exist

---

### ModListFile
The file containing mod names to search for.

| Field | Type | Description |
|-------|------|-------------|
| path | string | Path to the mod list file |
| format | string | Plain text, one mod name per line |

**Location**: `database/GTSv101.txt`

**Validation**: Must exist and be readable

---

### ArchiveFile
A mod archive file found during search.

| Field | Type | Description |
|-------|------|-------------|
| filename | string | Full filename with extension |
| path | string | Full path to the file |
| extension | string | .zip, .7z, or .rar |
| mod_match | string | The mod name from list that matched this file |

---

### LogFile
The log file created during script execution.

| Field | Type | Description |
|-------|------|-------------|
| path | string | Full path to log file |
| timestamp | datetime | When the log was created |
| format | string | Text format with timestamps |

**Naming Convention**: `mod_importer_YYYYMMDD_HHMMSS.log`

---

## Relationships

```
User Input (runtime)
    │
    ├──► SourceDirectory ──► ArchiveFile (search)
    │                              │
    │                              ▼
    ├──► DestinationDirectory ◄─── Copy Operation
    │
    └──► ModListFile ──► ModEntry (read)
                              │
                              ▼
                         ArchiveFile (match)
```

## State Flow

1. **INIT** - Script starts, logging initialized
2. **GET_INPUT** - User prompted for source/destination paths
3. **READ_LIST** - Mod list loaded from database folder
4. **SEARCH** - Source directory scanned for matching archives
5. **COPY** - Matching files copied to destination
6. **COMPLETE** - Summary displayed, log file written
7. **ERROR** - Error occurred, logged and displayed

## Validation Rules

- Source directory must exist and be readable
- Destination directory will be created if needed
- Mod list file must exist in database folder
- Archive files must have extensions: .zip, .7z, .rar
