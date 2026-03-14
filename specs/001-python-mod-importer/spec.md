# Feature Specification: Python Mod Importer

**Feature Branch**: `001-python-mod-importer`  
**Created**: 2026-03-10  
**Status**: Draft  
**Input**: User description: "I want you to translate the shell script copy_mods.sh from the current directory to a python script and all variable should be entered manually by the user during runtime and the GTSv101.txt, arrange it inside a database folder or what suit the most for the current situation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Mod Importer with Runtime Input (Priority: P1)

As a user, I want to run the Python script and be prompted for all required directories so that I can easily configure the mod import process without editing any files.

**Why this priority**: This is the core functionality - without runtime input, the translation would not meet the user's requirement of entering variables manually.

**Independent Test**: Can be tested by running the script with mock input and verifying it prompts for each required path.

**Acceptance Scenarios**:

1. **Given** the script is executed without arguments, **When** the user is prompted for source directory, **Then** the user can enter a valid directory path
2. **Given** the script is executed without arguments, **When** the user is prompted for destination directory, **Then** the user can enter a valid directory path
3. **Given** valid directories are provided, **When** the user confirms, **Then** the import process begins

---

### User Story 2 - Import Mods from List (Priority: P1)

As a user, I want the script to read the mod list from the database folder and search for matching archive files so that I can efficiently gather all required mods.

**Why this priority**: This replaces the core functionality of the original shell script - searching and copying mod archives.

**Independent Test**: Can be tested by providing a sample mod list and verifying matching files are identified and copied.

**Acceptance Scenarios**:

1. **Given** a mod list exists in the database folder, **When** the script runs, **Then** it reads each mod name from the list
2. **Given** a mod name from the list, **When** the script searches the source directory, **Then** it finds all archive files (.zip, .7z, .rar) containing that name
3. **Given** matching archives are found, **When** the copy operation runs, **Then** files are copied to the destination directory

---

### User Story 3 - Database Folder Organization (Priority: P2)

As a user, I want the GTSv101.txt file to be stored in a database folder so that the mod list is organized properly within the project structure.

**Why this priority**: The user specifically requested the mod list be arranged in a database folder for better organization.

**Independent Test**: Can be verified by checking that the database folder contains the mod list file.

**Acceptance Scenarios**:

1. **Given** the project structure exists, **When** the database folder is created, **Then** it should contain the GTSv101.txt file
2. **Given** the database folder contains the mod list, **When** the script runs, **Then** it reads from the correct path in the database folder

---

### User Story 4 - Progress and Result Reporting (Priority: P3)

As a user, I want to see clear progress and final results so that I know what files were copied and if any errors occurred.

**Why this priority**: User experience is important - the user should know what happened during the import process.

**Independent Test**: Can be tested by running the script and verifying output messages are clear and informative.

**Acceptance Scenarios**:

1. **Given** the import process is running, **When** a mod match is found, **Then** the script displays the filename being copied
2. **Given** the import process completes, **When** finished, **Then** the script displays a summary of total files copied
3. **Given** an error occurs during copy, **When** it happens, **Then** the script displays an error message and continues with remaining mods

---

### Edge Cases

- What happens when the source directory does not exist?
- What happens when the destination directory cannot be created?
- What happens when no matching files are found for a mod name?
- What happens when the mod list file is empty?
- What happens when there are duplicate files in the destination?
- What happens when the user cancels at a prompt?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST prompt the user for the source directory path at runtime
- **FR-002**: The system MUST prompt the user for the destination directory path at runtime
- **FR-003**: The system MUST read mod names from the mod list file stored in the database folder
- **FR-004**: The system MUST search for archive files (.zip, .7z, .rar) matching each mod name from the list
- **FR-005**: The system MUST copy matching archive files to the destination directory
- **FR-006**: The system MUST create the destination directory if it does not exist
- **FR-007**: The system MUST display progress information during the import process
- **FR-008**: The system MUST provide a summary of files copied after completion
- **FR-009**: The system MUST handle errors gracefully and continue processing remaining mods
- **FR-010**: The system MUST validate that entered paths are valid directories
- **FR-011**: The system MUST support canceling the operation at any prompt

### Key Entities

- **ModEntry**: Represents a single mod name from the mod list file (string identifier)
- **SourceDirectory**: The directory path where mod archives will be searched (user input)
- **DestinationDirectory**: The directory path where matching mods will be copied (user input)
- **ModListFile**: The file containing mod names to search for, stored in database folder
- **ArchiveFile**: A mod archive file with extension .zip, .7z, or .rar

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the mod import process by entering paths at runtime without modifying any source files
- **SC-002**: All archive files matching mod names from GTSv101.txt are successfully copied to the destination directory
- **SC-003**: The mod list file is properly organized in the database folder as requested
- **SC-004**: Users receive clear feedback about the import progress and final results
- **SC-005**: Error conditions are handled gracefully without crashing the application
