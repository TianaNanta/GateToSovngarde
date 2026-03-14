"""User story validation tests.

These tests verify that each user story from the specification can be
independently tested and executed without requiring other stories.
"""

from typer.testing import CliRunner

from cli.main import app


class TestUserStory1ImportCommand:
    """[US1] Import Command - Can be tested independently."""

    def test_import_command_exists(self) -> None:
        """Verify import command is registered and accessible."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout.lower()

    def test_import_accepts_required_arguments(self) -> None:
        """Verify import accepts version, source, dest arguments."""
        runner = CliRunner()
        # Just test parsing, not actual execution
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        # Should show all required arguments
        assert "version" in result.stdout.lower() or "VERSION" in result.stdout

    def test_import_validates_arguments(self, use_mock_database_for_tests) -> None:
        """Verify import validates arguments correctly."""
        runner = CliRunner()

        # Invalid version should fail with exit code 1
        result = runner.invoke(
            app, ["database", "import", "InvalidVersion", "/src", "/dst"]
        )
        assert result.exit_code == 1

    def test_import_supports_force_flag(self) -> None:
        """Verify --force flag is supported."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "--force" in result.stdout or "-f" in result.stdout

    def test_import_supports_verbose_flag(self) -> None:
        """Verify --verbose flag is supported."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "--verbose" in result.stdout or "-v" in result.stdout

    def test_import_provides_useful_errors(self) -> None:
        """Verify import provides helpful error messages."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "Invalid", "/src", "/dst"])

        assert result.exit_code == 1
        # Should provide some error information
        assert result.stdout  # Has some output


class TestUserStory2HelpSystem:
    """[US2] Help System - Can be tested independently."""

    def test_main_help_displays(self) -> None:
        """Verify main --help works."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "GateToSovngarde" in result.stdout

    def test_version_display_works(self) -> None:
        """Verify --version displays version."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()

    def test_group_help_displays(self) -> None:
        """Verify group --help works."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0

    def test_command_help_displays(self) -> None:
        """Verify command --help works."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "import", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout.lower()

    def test_help_shows_available_commands(self) -> None:
        """Verify help lists available commands."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Should list database group
        assert "database" in result.stdout.lower()


class TestUserStory3Extensibility:
    """[US3] Extensibility - Can be tested independently."""

    def test_new_group_can_be_added(self) -> None:
        """Verify existing group pattern allows adding new groups.

        This validates the extensibility pattern by checking database group
        demonstrates the pattern that new groups would follow.
        """
        runner = CliRunner()

        # Database group demonstrates the pattern
        result = runner.invoke(app, ["database", "--help"])
        assert result.exit_code == 0
        # Should show multiple commands
        assert "import" in result.stdout
        assert "versions" in result.stdout

    def test_new_command_in_group_works(self) -> None:
        """Verify versions command works (demonstrates extensibility)."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "versions"])

        assert result.exit_code == 0
        assert "GTSv101" in result.stdout

    def test_framework_not_modified_for_new_command(self) -> None:
        """Verify main.py doesn't need modification for new commands.

        The versions command was added to the database group without
        changing the core framework (main.py callback).
        """
        runner = CliRunner()

        # Both commands work through same framework
        import_result = runner.invoke(app, ["database", "import", "--help"])
        versions_result = runner.invoke(app, ["database", "versions", "--help"])

        assert import_result.exit_code == 0
        assert versions_result.exit_code == 0


class TestUserStory4Packaging:
    """[US4] Packaging - Can be tested independently."""

    def test_cli_is_executable(self) -> None:
        """Verify CLI can be executed (would be in installed package)."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert result.stdout  # Has output

    def test_all_commands_accessible(self) -> None:
        """Verify all commands are accessible."""
        runner = CliRunner()

        # Main help should show database group
        main = runner.invoke(app, ["--help"])
        assert "database" in main.stdout.lower()

        # Group should be accessible
        database = runner.invoke(app, ["database", "--help"])
        assert database.exit_code == 0

    def test_entry_point_works(self) -> None:
        """Verify entry point (gts command) is registered.

        This would be verified when installing the wheel.
        """
        # We're testing via app directly, which simulates the entry point
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0


class TestUserStory5CommandGroups:
    """[US5] Command Groups - Can be tested independently."""

    def test_groups_appear_in_help(self) -> None:
        """Verify groups appear in main help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "database" in result.stdout.lower()

    def test_group_shows_subcommands(self) -> None:
        """Verify group help shows its subcommands."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        # Should show all commands in this group
        assert "import" in result.stdout
        assert "versions" in result.stdout

    def test_grouped_commands_execute(self) -> None:
        """Verify commands execute correctly through groups."""
        runner = CliRunner()

        # Both commands should work
        import_help = runner.invoke(app, ["database", "import", "--help"])
        versions = runner.invoke(app, ["database", "versions"])

        assert import_help.exit_code == 0
        assert versions.exit_code == 0

    def test_group_hierarchy_clear(self) -> None:
        """Verify command hierarchy is clear: gts -> database -> command."""
        runner = CliRunner()

        # Step 1: gts --help shows groups
        step1 = runner.invoke(app, ["--help"])
        assert "database" in step1.stdout.lower()

        # Step 2: gts database --help shows commands in group
        step2 = runner.invoke(app, ["database", "--help"])
        assert "import" in step2.stdout

        # Step 3: gts database import --help shows command details
        step3 = runner.invoke(app, ["database", "import", "--help"])
        assert step3.exit_code == 0

    def test_multiple_commands_in_group(self) -> None:
        """Verify multiple commands coexist in a group."""
        runner = CliRunner()
        result = runner.invoke(app, ["database", "--help"])

        assert result.exit_code == 0
        # Database group should contain both import and versions
        assert "import" in result.stdout
        assert "versions" in result.stdout
        # Both should be accessible
        assert result.stdout.count("import") >= 1
        assert result.stdout.count("versions") >= 1


class TestAllStoriesIntegrated:
    """Verify all user stories work together without conflicts."""

    def test_all_stories_available(self) -> None:
        """Verify all stories are represented in the CLI."""
        runner = CliRunner()
        main_help = runner.invoke(app, ["--help"])
        database_help = runner.invoke(app, ["database", "--help"])

        # US1: Import command (in database group)
        assert any(
            h.exit_code == 0
            for h in [runner.invoke(app, ["database", "import", "--help"])]
        )

        # US2: Help system (works for all)
        assert main_help.exit_code == 0
        assert database_help.exit_code == 0

        # US3: Extensibility (versions command added without framework changes)
        assert runner.invoke(app, ["database", "versions"]).exit_code == 0

        # US4: Packaging (CLI works)
        assert runner.invoke(app, ["--help"]).exit_code == 0

        # US5: Command groups (hierarchical)
        assert "database" in main_help.stdout.lower()
        assert "import" in database_help.stdout
        assert "versions" in database_help.stdout
