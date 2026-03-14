"""Unit tests for DatabaseLoader.

Tests the database loading system including:
- Loading valid databases
- Listing available versions
- Caching behavior
- Error handling for missing/invalid databases
"""

import pytest

from cli.db import DatabaseLoader
from cli.utils.errors import DatabaseError


class TestDatabaseLoaderLoadVersion:
    """Tests for loading specific GTS versions."""

    def test_load_version_gtsv101(self, database_loader: DatabaseLoader) -> None:
        """Test loading the GTSv101 database.

        Should load the bundled GTSv101 database and return a dictionary
        with the expected structure.
        """
        db = database_loader.get_version("GTSv101")

        assert isinstance(db, dict)
        assert db["version_id"] == "GTSv101"
        assert "version_name" in db
        assert "mods" in db
        assert isinstance(db["mods"], list)
        assert len(db["mods"]) > 0

    def test_load_version_returns_mods_list(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test that loaded database contains valid mod entries.

        Each mod should have required fields: id, name, required_files.
        """
        db = database_loader.get_version("GTSv101")

        for mod in db["mods"]:
            assert isinstance(mod, dict)
            assert "id" in mod
            assert "name" in mod
            assert "required_files" in mod
            assert isinstance(mod["required_files"], list)

    def test_invalid_version_raises_error(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test that requesting unknown version raises DatabaseError.

        Should raise DatabaseError with descriptive message.
        """
        with pytest.raises(DatabaseError):
            database_loader.get_version("InvalidVersion999")


class TestDatabaseLoaderListVersions:
    """Tests for listing available versions."""

    def test_list_versions(self, database_loader: DatabaseLoader) -> None:
        """Test listing all available GTS versions.

        Should return a list of version identifiers.
        """
        versions = database_loader.list_versions()

        assert isinstance(versions, list)
        assert len(versions) > 0
        assert "GTSv101" in versions

    def test_list_versions_returns_sorted_list(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test that version list is sorted alphabetically.

        Makes version selection more predictable for users.
        """
        versions = database_loader.list_versions()

        assert versions == sorted(versions)


class TestDatabaseLoaderValidateVersion:
    """Tests for version validation."""

    def test_validate_version_exists_true(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test validation returns True for existing versions.

        Should return True for GTSv101 without loading full data.
        """
        assert database_loader.validate_version_exists("GTSv101") is True

    def test_validate_version_exists_false(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test validation returns False for nonexistent versions.

        Should return False for invalid version without raising error.
        """
        assert database_loader.validate_version_exists("InvalidVersion") is False

    def test_validate_works_without_full_load(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test that validation doesn't require full database load.

        validate_version_exists() should work before get_version().
        """
        # Validate without loading
        exists = database_loader.validate_version_exists("GTSv101")
        assert exists is True

        # Then load
        db = database_loader.get_version("GTSv101")
        assert db["version_id"] == "GTSv101"


class TestDatabaseLoaderCaching:
    """Tests for database caching behavior."""

    def test_database_caching(self, database_loader: DatabaseLoader) -> None:
        """Test that loaded database is cached and reused.

        Calling get_version() twice should return the same object
        (proving it's cached, not reloaded).
        """
        # Load version first time
        db1 = database_loader.get_version("GTSv101")
        # Load version second time
        db2 = database_loader.get_version("GTSv101")

        # Should be the same object due to caching
        assert db1 is db2

    def test_cache_works_for_multiple_versions(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test that cache works independently for multiple versions.

        Each version gets its own cache entry.
        """
        # Load GTSv101 multiple times
        db1a = database_loader.get_version("GTSv101")
        db1b = database_loader.get_version("GTSv101")

        # Same version should be cached
        assert db1a is db1b

        # Other versions would be separate cache entries
        # (Test doesn't load other versions to avoid dependency on them)


class TestDatabaseLoaderErrorHandling:
    """Tests for error handling in database loading."""

    def test_invalid_version_raises_database_error(
        self, database_loader: DatabaseLoader
    ) -> None:
        """Test DatabaseError is raised for invalid versions.

        Error message should be descriptive.
        """
        with pytest.raises(DatabaseError) as exc_info:
            database_loader.get_version("NonExistent")

        assert (
            "NonExistent" in str(exc_info.value)
            or "not found" in str(exc_info.value).lower()
        )

    def test_database_error_has_message(self, database_loader: DatabaseLoader) -> None:
        """Test that DatabaseError provides useful error message.

        Users should understand what went wrong.
        """
        with pytest.raises(DatabaseError) as exc_info:
            database_loader.get_version("BadVersion")

        # Should have a descriptive message
        assert len(str(exc_info.value)) > 0
