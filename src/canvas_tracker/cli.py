from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .calendar import fetch_assignments
from .config import get_config, save_config

console = Console()


def _urgency_color(due: datetime) -> str:
    hours = (due - datetime.now(timezone.utc)).total_seconds() / 3600
    if hours < 24:
        return "red"
    if hours < 72:
        return "yellow"
    return "green"


def _format_due(due: datetime) -> str:
    local = due.astimezone()
    now = datetime.now(local.tzinfo)
    days = (local - now).days
    if days == 0:
        label = "today"
    elif days == 1:
        label = "tomorrow"
    else:
        label = f"in {days} days"
    return f"{local.strftime('%a %b %d, %I:%M %p')} ({label})"


def _show_upcoming(course_filter: str | None) -> None:
    config = get_config()
    if not config.get("ical_url"):
        console.print("[red]Not configured.[/red] Run [bold]canvas-tracker configure[/bold] first.")
        raise SystemExit(1)

    with console.status("[bold blue]Fetching from Canvas…[/bold blue]"):
        assignments = fetch_assignments(config["ical_url"], course_filter=course_filter)

    if not assignments:
        console.print("[yellow]No upcoming assignments found.[/yellow]")
        return

    table = Table(
        title="📚  Upcoming Assignments",
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold cyan",
    )
    table.add_column("Course", style="bold cyan", no_wrap=True)
    table.add_column("Assignment")
    table.add_column("Due", no_wrap=True)

    for a in assignments:
        color = _urgency_color(a["due"])
        table.add_row(
            a["course"],
            a["name"],
            Text(_format_due(a["due"]), style=color),
        )

    console.print()
    console.print(table)
    console.print(f"[dim]  {len(assignments)} assignment(s) upcoming[/dim]\n")


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Track your upcoming Canvas assignments from the terminal."""
    if ctx.invoked_subcommand is None:
        _show_upcoming(course_filter=None)


@main.command()
@click.option("--url", prompt="Canvas iCal URL", help="Your Canvas calendar feed URL")
def configure(url: str) -> None:
    """Save your Canvas iCal feed URL."""
    save_config(url)
    console.print("[green]✓ Configuration saved.[/green]")


@main.command()
@click.option("--course", default=None, help="Filter by course code (e.g. DSC190)")
def upcoming(course: str | None) -> None:
    """Show all upcoming assignments."""
    _show_upcoming(course_filter=course)


@main.command("setup-autorun")
def setup_autorun() -> None:
    """Add canvas-tracker to your shell startup so it runs on every new terminal."""
    shell = Path(os.environ.get("SHELL", "")).name
    rc_map = {"zsh": Path.home() / ".zshrc", "bash": Path.home() / ".bashrc"}
    rc_file = rc_map.get(shell, Path.home() / ".bashrc")
    snippet = "\n# canvas-tracker: show upcoming assignments on terminal open\ncanvas-tracker\n"

    if rc_file.exists() and "canvas-tracker" in rc_file.read_text():
        console.print(f"[yellow]Already in {rc_file}.[/yellow]")
        return

    with open(rc_file, "a") as f:
        f.write(snippet)

    console.print(f"[green]✓ Added to {rc_file}[/green]")
    console.print(f"[dim]Run [bold]source {rc_file}[/bold] or open a new terminal to apply.[/dim]")