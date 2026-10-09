"""SkillGuard command-line interface."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from skillguard import __version__

app = typer.Typer(
    name="skillguard",
    help="Static security scanner for AI agent skills.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(
            Panel.fit(
                f"SkillGuard [bold cyan]v{__version__}[/]",
                border_style="cyan",
            )
        )
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the SkillGuard version and exit.",
    ),
) -> None:
    """SkillGuard — scan untrusted agent skills before you install them."""
