#!/usr/bin/env python3
"""
Mod Importer - Gate To Sovngarde
A Python script to import mods from a list file with beautiful Rich logging.
"""

import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

ARCHIVE_EXTENSIONS = (".zip", ".7z", ".rar")
DATABASE_PATH = Path(__file__).parent.parent / "database" / "GTSv101.txt"
LOGS_DIR = Path(__file__).parent.parent / "logs"


def setup_logging() -> logging.Logger:
    """Configure logging with Rich console and file handlers."""
    LOGS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"mod_importer_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
            ),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    logger = logging.getLogger("mod_importer")
    console.print(f"[dim]Log file: {log_file}[/dim]")

    return logger


def display_banner() -> None:
    """Display the application banner."""
    console.print(
        Panel.fit(
            "[bold cyan]🎮[/bold cyan] [bold]Mod Importer[/bold] - [bold green]Gate To Sovngarde[/bold green]",
            border_style="cyan",
        )
    )
    console.print()


def get_source_directory() -> Path:
    """Prompt user for source directory path."""
    while True:
        path_str = Prompt.ask(
            "[cyan]Enter source directory[/cyan]\n[dim](where mod archives are located)[/dim]",
            default="/run/media/nanta/Nanta/Skyrim/skyrimse",
        )

        if not path_str:
            console.print("[red]Source directory cannot be empty.[/red]")
            continue

        source_path = Path(path_str)

        if not source_path.exists():
            console.print(f"[red]Directory does not exist: {source_path}[/red]")
            if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                sys.exit(0)
            continue

        if not source_path.is_dir():
            console.print(f"[red]Not a directory: {source_path}[/red]")
            if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                sys.exit(0)
            continue

        console.print(f"[green]✓[/green] Source directory: [bold]{source_path}[/bold]")
        return source_path


def get_destination_directory() -> Path:
    """Prompt user for destination directory path."""
    while True:
        path_str = Prompt.ask(
            "[cyan]Enter destination directory[/cyan]\n[dim](where mods will be copied to)[/dim]",
            default="/mnt/data/Mods",
        )

        if not path_str:
            console.print("[red]Destination directory cannot be empty.[/red]")
            continue

        dest_path = Path(path_str)

        try:
            dest_path.mkdir(parents=True, exist_ok=True)
            console.print(
                f"[green]✓[/green] Destination directory: [bold]{dest_path}[/bold]"
            )
            return dest_path
        except PermissionError:
            console.print(f"[red]Permission denied: {dest_path}[/red]")
            if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                sys.exit(0)
        except Exception as e:
            console.print(f"[red]Error creating directory: {e}[/red]")
            if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                sys.exit(0)


def read_mod_list() -> list[str]:
    """Read mod from the database names file."""
    console.print(
        "[cyan]📂[/cyan] Reading mod list from [bold]database/GTSv101.txt[/bold]..."
    )

    if not DATABASE_PATH.exists():
        console.print(f"[red]✗[/red] Mod list file not found: {DATABASE_PATH}")
        sys.exit(1)

    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        mod_names = [line.strip() for line in f if line.strip()]

    console.print(
        f"[green]✓[/green] Found [bold]{len(mod_names)}[/bold] mods to search"
    )
    return mod_names


def find_matching_archives(
    source_dir: Path, mod_names: list[str], logger: logging.Logger
) -> list[tuple[Path, str]]:
    """Search source directory for archive files matching mod names."""
    matches: list[tuple[Path, str]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Searching for mods...", total=len(mod_names))

        for mod_name in mod_names:
            for archive_ext in ARCHIVE_EXTENSIONS:
                for file_path in source_dir.rglob(f"*{mod_name}*{archive_ext}"):
                    matches.append((file_path, mod_name))
                    logger.info(f"Found: {file_path.name}")

            progress.update(task, advance=1)

    return matches


def copy_mod_files(
    matches: list[tuple[Path, str]],
    dest_dir: Path,
    logger: logging.Logger,
) -> tuple[int, int]:
    """Copy matching archive files to destination directory."""
    copied = 0
    errors = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Copying mods...", total=len(matches))

        for file_path, mod_name in matches:
            try:
                dest_path = dest_dir / file_path.name
                shutil.copy2(file_path, dest_path)
                copied += 1
                logger.info(f"Copied: {file_path.name}")
            except Exception as e:
                errors += 1
                logger.error(f"Failed to copy {file_path.name}: {e}")
                console.print(f"[red]✗[/red] Failed: {file_path.name}")

            progress.update(task, advance=1)

    return copied, errors


def display_summary(copied: int, errors: int, duration: float) -> None:
    """Display final summary with Rich formatting."""
    table = Table(title="📊 Summary", show_header=False, box=None)
    table.add_column("Label", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Total files copied", f"[green]{copied}[/green]")
    table.add_row("Errors", f"[red]{errors}[/red]" if errors else "[green]0[/green]")
    table.add_row("Duration", f"{duration:.2f}s")

    console.print()
    console.print(Panel(table, border_style="green"))


def main() -> None:
    """Main entry point for the mod importer."""
    try:
        logger = setup_logging()

        display_banner()

        console.print("[dim]Press Ctrl+C to cancel at any prompt[/dim]\n")

        source_dir = get_source_directory()
        dest_dir = get_destination_directory()

        if not Confirm.ask("\n[bold]Start import?[/bold]", default=True):
            console.print("[yellow]Import cancelled.[/yellow]")
            sys.exit(0)

        mod_names = read_mod_list()

        console.print()
        console.print("[cyan]🔍[/cyan] Searching for mods...")

        matches = find_matching_archives(source_dir, mod_names, logger)

        if not matches:
            console.print("[yellow]⚠[/yellow] No matching archives found!")
            sys.exit(0)

        console.print(
            f"[green]✓[/green] Found [bold]{len(matches)}[/bold] matching archives"
        )

        start_time = datetime.now()

        copied, errors = copy_mod_files(matches, dest_dir, logger)

        duration = (datetime.now() - start_time).total_seconds()

        display_summary(copied, errors, duration)

        console.print("\n[green]✓[/green] Import complete!")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow] Import cancelled by user.")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
