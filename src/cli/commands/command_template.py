"""Template for creating new CLI commands.

INSTRUCTIONS:
1. Copy this file to your_new_cmd.py
2. Replace 'your_new_cmd' with your actual command name
3. Update the docstring and parameter descriptions
4. Implement your command logic
5. Register in __init__.py: app.command(name="your-cmd")(your_new_cmd)
6. Write tests in tests/unit/test_your_new_cmd.py
7. Test with: uv run gts your-cmd --help

See README.md in this directory for the complete command creation guide.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..utils.errors import ValidationError, OperationError
from ..utils.output import success, error

# Initialize console for Rich output
console = Console()


def your_new_cmd(
    required_arg: str = typer.Argument(
        ..., help="Description of required positional argument"
    ),
    optional_arg: Optional[str] = typer.Argument(
        None, help="Description of optional positional argument"
    ),
    option_flag: bool = typer.Option(
        False, "--force", "-f", help="Brief description of this option"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Brief description of your command (shown in help).

    This longer description explains what your command does, when to use it,
    and any important notes about behavior or requirements.

    The docstring becomes the help text, so write it for end users,
    not developers.

    Example:
        $ gts your-new-cmd /path/to/source
        $ gts your-new-cmd /path/to/source --force --verbose

    Args:
        required_arg: What this argument does and expects
        optional_arg: What this optional argument does, if provided
        option_flag: When to use this flag and what it changes
        verbose: Enable detailed progress output

    Raises:
        ValidationError: If arguments are invalid or missing required data
        OperationError: If the command execution fails due to system errors
    """
    try:
        # ===== STEP 1: VALIDATE INPUTS =====
        # Always validate user input first, before any operations

        if not required_arg:
            raise ValidationError("Required argument cannot be empty")

        # If working with file paths:
        if isinstance(required_arg, str):
            input_path = Path(required_arg)
            if not input_path.exists():
                raise ValidationError(f"Path not found: {required_arg}")

        # ===== STEP 2: LOAD DEPENDENCIES =====
        # Load databases, services, or other dependencies

        # Example: Load database
        # loader = DatabaseLoader()
        # if not loader.validate_version_exists("GTSv101"):
        #     raise ValidationError("Database version not found")
        # database = loader.get_version("GTSv101")

        # ===== STEP 3: PERFORM OPERATION =====
        # Execute your command logic

        if verbose:
            console.print("[dim]Starting operation...[/dim]")

        # Your actual implementation here
        # result = do_something(required_arg, optional_arg, option_flag)

        # ===== STEP 4: REPORT RESULTS =====
        # Display results using Rich output helpers

        success("✓ Command completed successfully")
        console.print(f"  Input: {required_arg}")
        if optional_arg:
            console.print(f"  Additional: {optional_arg}")
        console.print(f"  Mode: {'Force' if option_flag else 'Normal'}")

    except ValidationError as e:
        # Validation errors = user error (exit code 1)
        error("✗ Validation failed")
        console.print(f"  {e}")
        raise typer.Exit(code=1)

    except OperationError as e:
        # Operation errors = system error (exit code 2)
        error("✗ Operation failed")
        console.print(f"  {e}")
        raise typer.Exit(code=2)

    except KeyboardInterrupt:
        # User pressed Ctrl+C
        console.print("\n[yellow]⚠ Operation interrupted by user[/yellow]")
        raise typer.Exit(code=2)

    except Exception as e:
        # Unexpected errors
        error("✗ Unexpected error")
        console.print(f"  {type(e).__name__}: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=2)
