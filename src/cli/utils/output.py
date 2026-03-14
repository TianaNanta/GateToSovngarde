"""Rich console output helpers for formatted CLI output."""

from rich.console import Console
from rich.panel import Panel
from rich.status import Status

# Initialize global console for Rich output
console = Console()


def success(message: str) -> None:
    """Display a success message in green."""
    console.print(f"✓ {message}", style="bold green")


def error(message: str) -> None:
    """Display an error message in red."""
    console.print(f"Error: {message}", style="bold red")


def warning(message: str) -> None:
    """Display a warning message in yellow."""
    console.print(f"⚠ {message}", style="bold yellow")


def info(message: str) -> None:
    """Display an info message."""
    console.print(f"ℹ {message}", style="blue")


def progress(message: str) -> None:
    """Display a progress/status message."""
    console.print(message, style="cyan")


def confirm(message: str) -> bool:
    """Ask user for confirmation (yes/no)."""
    from rich.prompt import Confirm

    return Confirm.ask(message)


def panel(title: str, message: str, style: str = "blue") -> None:
    """Display a message in a panel."""
    console.print(Panel(message, title=title, style=style))
