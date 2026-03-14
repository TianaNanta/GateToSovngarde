"""Database loading system for GTS version databases.

This module provides the DatabaseLoader class for loading and caching
GTS version databases bundled with the CLI package.

Example usage:
    loader = DatabaseLoader()
    gts_db = loader.get_version("GTSv101")
    print(gts_db["version_name"])  # "GateToSovngarde v1.01"

    versions = loader.list_versions()
    print(versions)  # ["GTSv101", ...]

    if loader.validate_version_exists("GTSv101"):
        # Safe to load
        pass
"""

import json
from pathlib import Path

from ..utils.errors import DatabaseError


class DatabaseLoader:
    """Load and cache GTS version databases from bundled data files.

    The DatabaseLoader handles loading mod database JSON files from the
    `databases/` directory bundled with the CLI package. It maintains an
    in-memory cache to avoid repeated disk I/O for the same databases.

    Attributes:
        _cache: Internal dictionary storing loaded databases by version ID
    """

    def __init__(self) -> None:
        """Initialize DatabaseLoader with empty cache."""
        self._cache: dict[str, dict] = {}

    def get_version(self, version_id: str) -> dict:
        """Load a GTS version database, using cache if available.

        Loads the JSON database file for the specified GTS version from
        the bundled `databases/VERSION_ID/mods.json` file. Results are
        cached to avoid repeated disk I/O.

        Args:
            version_id: The version identifier (e.g., "GTSv101")

        Returns:
            Dictionary containing the parsed JSON database with keys:
            - version_id: The version identifier
            - version_name: Human-readable version name
            - mods: List of mod dictionaries
            - created_date: When the database was created

        Raises:
            DatabaseError: If the version database cannot be found or loaded

        Example:
            >>> loader = DatabaseLoader()
            >>> db = loader.get_version("GTSv101")
            >>> len(db["mods"])
            3
        """
        # Return from cache if already loaded
        if version_id in self._cache:
            return self._cache[version_id]

        try:
            # Use importlib.resources to access bundled database files
            # Convert to lowercase for directory lookup (common convention)
            db_dir = version_id.lower()

            # Try to read the mods.json file from the databases package
            try:
                # For Python 3.13+ with importlib.resources API
                from importlib.resources import files

                db_package = files("cli").joinpath("databases", db_dir, "mods.json")

                if db_package.is_file():
                    db_content = db_package.read_text(encoding="utf-8")
                else:
                    raise FileNotFoundError(f"Database file not found for {version_id}")
            except (AttributeError, FileNotFoundError, TypeError):
                # Fallback for different importlib.resources implementations
                # Try direct path-based lookup
                import cli

                cli_path = Path(cli.__file__).parent
                db_file = cli_path / "databases" / db_dir / "mods.json"

                if not db_file.exists():
                    raise FileNotFoundError(f"Database file not found for {version_id}")

                db_content = db_file.read_text(encoding="utf-8")

            # Parse JSON content
            data = json.loads(db_content)

            # Validate structure
            if not isinstance(data, dict):
                raise DatabaseError(f"Invalid database format for {version_id}")

            if "mods" not in data:
                raise DatabaseError(f"Database missing 'mods' key for {version_id}")

            # Cache and return
            self._cache[version_id] = data
            return data

        except json.JSONDecodeError as e:
            raise DatabaseError(f"Invalid JSON in database {version_id}: {e}")
        except FileNotFoundError:
            raise DatabaseError(f"Database not found for version: {version_id}")
        except Exception as e:
            raise DatabaseError(f"Failed to load database {version_id}: {e}")

    def _normalize_version_id(self, dir_name: str) -> str:
        """Normalize directory name to proper version ID format.

        Converts lowercase directory names to proper GTS version IDs.
        Examples:
            "gtsv101" -> "GTSv101"
            "gtsv200" -> "GTSv200"

        Args:
            dir_name: The directory name (usually lowercase)

        Returns:
            Normalized version ID with proper casing
        """
        # Simple pattern: if it starts with "gts" and contains "v" and numbers,
        # normalize to "GTSvNNN" format
        if dir_name.lower().startswith("gts"):
            # Extract the numeric part and reconstruct
            lower_name = dir_name.lower()
            if "v" in lower_name:
                parts = lower_name.split("v")
                if len(parts) == 2 and parts[1].isdigit():
                    return f"GTSv{parts[1]}"

        # Fallback: return as-is (shouldn't happen with proper naming)
        return dir_name

    def list_versions(self) -> list[str]:
        """List all available GTS version databases.

        Scans the bundled `databases/` directory and returns a list of
        available version identifiers.

        Returns:
            List of version identifiers (e.g., ["GTSv101"])

        Example:
            >>> loader = DatabaseLoader()
            >>> versions = loader.list_versions()
            >>> "GTSv101" in versions
            True
        """
        try:
            # Use importlib.resources to list available databases
            try:
                from importlib.resources import files

                db_root = files("cli").joinpath("databases")

                # List directories in databases folder
                versions = []
                for item in db_root.iterdir():
                    if item.is_dir():
                        # Get directory name (already in proper case like "gtsv101")
                        dir_name = item.name
                        # Convert directory name to proper version ID format
                        version_id = self._normalize_version_id(dir_name)
                        versions.append(version_id)

                return sorted(versions)
            except (AttributeError, TypeError):
                # Fallback: direct path lookup
                import cli

                cli_path = Path(cli.__file__).parent
                db_root = cli_path / "databases"

                if not db_root.exists():
                    return []

                versions = []
                for item in db_root.iterdir():
                    if item.is_dir():
                        version_id = self._normalize_version_id(item.name)
                        versions.append(version_id)

                return sorted(versions)

        except Exception:
            # Return empty list if listing fails
            return []

    def validate_version_exists(self, version_id: str) -> bool:
        """Check if a GTS version database exists.

        Validates that a database for the given version ID exists
        without loading the full data.

        Args:
            version_id: The version identifier to check

        Returns:
            True if the version database exists, False otherwise

        Example:
            >>> loader = DatabaseLoader()
            >>> loader.validate_version_exists("GTSv101")
            True
            >>> loader.validate_version_exists("InvalidVersion")
            False
        """
        available_versions = self.list_versions()
        return version_id in available_versions
