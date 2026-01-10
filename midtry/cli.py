"""MidTry CLI - Multi-agent reasoning harness."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, TypedDict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from . import __version__
from .runner import (
    AgentResult,
    MidTryConfig,
    MidTryResult,
    Perspective,
    detect_available_clis,
    run_multi_agent,
)

app = typer.Typer(
    name="midtry",
    help="Multi-perspective reasoning harness for coding decisions.",
    add_completion=False,
    invoke_without_command=True,
)

console = Console()


class AgentInfo(TypedDict):
    """Information about a running agent."""

    perspective: Perspective
    status: str
    elapsed: float | None


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold]midtry[/bold] version {__version__}")
        raise typer.Exit()


class AgentTracker:
    """Track running agents and their status for rich display."""

    def __init__(self) -> None:
        self.agents: dict[str, AgentInfo] = {}
        self.completed: list[AgentResult] = []

    def start(self, cli: str, perspective: Perspective) -> None:
        self.agents[cli] = {
            "perspective": perspective,
            "status": "running",
            "elapsed": None,
        }

    def complete(self, result: AgentResult) -> None:
        self.agents[result.cli]["status"] = "done" if result.success else "failed"
        self.agents[result.cli]["elapsed"] = result.elapsed
        self.completed.append(result)

    def make_table(self) -> Table:
        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("CLI", width=12)
        table.add_column("Perspective", width=14)
        table.add_column("Status", width=12)
        table.add_column("Time", width=8, justify="right")

        for cli, info in self.agents.items():
            perspective = info["perspective"].value.title()
            status = info["status"]
            elapsed = info.get("elapsed", 0) or 0

            if status == "running":
                status_text = Text("[spinner]", style="yellow")
            elif status == "done":
                status_text = Text("Done", style="green")
            else:
                status_text = Text("Failed", style="red")

            time_str = f"{elapsed:.1f}s" if elapsed else "-"
            table.add_row(cli, perspective, status_text, time_str)

        return table


async def run_with_progress(
    task: str,
    config: MidTryConfig,
    clis: list[str] | None,
) -> MidTryResult:
    """Run multi-agent with live progress display."""
    tracker = AgentTracker()

    console.print()
    console.print(Panel(task, title="[bold]Task[/bold]", border_style="blue"))
    console.print()

    available = detect_available_clis()
    if not available:
        console.print("[red]Error:[/red] No supported CLIs found.")
        console.print("Install one of: claude, gemini, codex, qwen, opencode, copilot")
        raise typer.Exit(1)

    console.print(f"[dim]CLIs available:[/dim] {', '.join(available)}")
    console.print(f"[dim]Mode:[/dim] {config.mode.upper()}")
    console.print(f"[dim]Timeout:[/dim] {config.timeout}s per call")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        main_task = progress.add_task("Running agents...", total=None)

        def on_start(cli: str, perspective: Perspective) -> None:
            tracker.start(cli, perspective)
            progress.update(main_task, description=f"Running {cli} ({perspective.value})...")

        def on_complete(result: AgentResult) -> None:
            tracker.complete(result)
            status = "[green]done[/green]" if result.success else "[red]failed[/red]"
            console.print(
                f"  {result.cli} ({result.perspective.value}): {status} ({result.elapsed:.1f}s)"
            )

        result = await run_multi_agent(
            task=task,
            config=config,
            clis=clis,
            on_start=on_start,
            on_complete=on_complete,
        )

    return result


def print_results(result: MidTryResult, show_full: bool = True) -> None:
    """Print formatted results."""
    console.print()
    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print("[bold cyan]RESPONSES[/bold cyan]")
    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print()

    for i, agent_result in enumerate(result.results, 1):
        status = "" if agent_result.success else " [red][FAILED][/red]"
        title = (
            f"Response {i}: {agent_result.perspective.value.title()} ({agent_result.cli}){status}"
        )
        console.print(f"[bold]--- {title} ---[/bold]")

        if agent_result.success:
            if show_full:
                console.print(agent_result.output)
            else:
                lines = agent_result.output.strip().split("\n")
                preview = "\n".join(lines[:10])
                if len(lines) > 10:
                    preview += f"\n[dim]... ({len(lines) - 10} more lines)[/dim]"
                console.print(preview)
        else:
            console.print(f"[red]Error: {agent_result.error or 'Unknown error'}[/red]")

        console.print()

    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print("[bold cyan]END RESPONSES[/bold cyan]")
    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print()

    # Summary
    success_count = len([r for r in result.results if r.success])
    total_count = len(result.results)
    console.print(f"[dim]Completed: {success_count}/{total_count} agents[/dim]")
    console.print()
    console.print("[bold]Aggregate these responses to determine the best answer.[/bold]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    task: Annotated[str | None, typer.Argument(help="The task/question for the agents")] = None,
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "-c",
            help="Path to config TOML file",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
    models: Annotated[
        str | None,
        typer.Option(
            "--models",
            "-m",
            help="Comma-separated list of CLIs to use (e.g., claude,gemini)",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="Timeout per CLI call in seconds",
        ),
    ] = 120,
    max_parallel: Annotated[
        int,
        typer.Option(
            "--max-parallel",
            "-p",
            help="Maximum number of CLIs to run in parallel",
        ),
    ] = 4,
    random_mode: Annotated[
        bool,
        typer.Option(
            "--random/--ordered",
            help="Shuffle CLI and perspective assignments",
        ),
    ] = False,
    quick: Annotated[
        bool,
        typer.Option(
            "--quick",
            "-q",
            help="Quick mode: use only 2 fastest CLIs",
        ),
    ] = False,
    output_full: Annotated[
        bool,
        typer.Option(
            "--full/--preview",
            help="Show full output or just preview",
        ),
    ] = True,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    MidTry: Multi-perspective reasoning harness.

    Spawns parallel CLI calls to get diverse perspectives on a task.
    Auto-detects available CLIs: claude, gemini, codex, qwen, opencode, copilot.

    Example:
        midtry "Fix the bug in this code: ..."
        midtry --models claude,gemini "Explain this error"
        midtry --random "What's the best approach for..."
    """
    # If a subcommand is invoked, skip this callback's logic
    if ctx.invoked_subcommand is not None:
        return

    # If no task provided, show help
    if task is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Load config
    config_path = config
    if config_path is None:
        # Look for config.toml in current directory or script directory
        candidates = [
            Path.cwd() / "config.toml",
            Path(__file__).parent.parent / "config.toml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                break

    midtry_config = MidTryConfig.from_toml(config_path) if config_path else MidTryConfig()

    # Override from CLI args
    midtry_config.timeout = timeout
    midtry_config.max_parallel = max_parallel
    midtry_config.mode = "random" if random_mode else "ordered"

    if quick:
        midtry_config.max_parallel = 2

    # Parse models list
    clis = None
    if models:
        clis = [m.strip() for m in models.split(",")]

    # Run
    try:
        result = asyncio.run(run_with_progress(task, midtry_config, clis))
        print_results(result, show_full=output_full)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise typer.Exit(130) from None
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@app.command()
def detect() -> None:
    """Detect and list available CLIs."""
    console.print("[bold]Detecting available CLIs...[/bold]")
    console.print()

    available = detect_available_clis()

    if not available:
        console.print("[red]No supported CLIs found.[/red]")
        console.print()
        console.print("Install one of:")
        console.print("  - claude (Claude Code)")
        console.print("  - gemini (Gemini CLI)")
        console.print("  - codex (OpenAI Codex)")
        console.print("  - qwen (Qwen CLI)")
        console.print("  - opencode (OpenCode)")
        console.print("  - copilot (GitHub Copilot)")
        raise typer.Exit(1)

    console.print("[green]Found:[/green]")
    for cli in available:
        console.print(f"  [bold]{cli}[/bold]")

    console.print()
    console.print(f"[dim]Total: {len(available)} CLI(s) available[/dim]")


@app.command()
def demo() -> None:
    """Run a demo with sample output (no API calls)."""
    console.print("[bold]MidTry Demo Mode[/bold]")
    console.print()
    console.print("This shows what MidTry output looks like without making real API calls.")
    console.print()

    sample_task = "What is 2 + 2?"

    console.print(Panel(sample_task, title="[bold]Task[/bold]", border_style="blue"))
    console.print()

    # Simulated responses
    responses = [
        (
            "claude",
            "Conservative",
            "Let me solve this step by step:\n\n1. We start with 2\n2. We add 2 to it\n3. 2 + 2 = 4\n\nThe answer is **4**.",
        ),
        (
            "gemini",
            "Analytical",
            "Breaking down the problem:\n\n- Input: Two integers (2 and 2)\n- Operation: Addition\n- Edge cases: None (simple integers)\n\nResult: 4",
        ),
        (
            "codex",
            "Creative",
            "While 2 + 2 = 4 in base 10, in other bases:\n- Base 3: 2 + 2 = 11\n- Base 4: 2 + 2 = 10\n\nAssuming standard decimal: **4**",
        ),
        (
            "qwen",
            "Adversarial",
            "The obvious answer is 4, but let me challenge this:\n\n- Are we certain these are integers?\n- What if it's string concatenation? '2' + '2' = '22'\n\nIn arithmetic: 4. In programming contexts: depends on types.",
        ),
    ]

    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print("[bold cyan]RESPONSES (DEMO)[/bold cyan]")
    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print()

    for i, (cli, perspective, output) in enumerate(responses, 1):
        console.print(f"[bold]--- Response {i}: {perspective} ({cli}) ---[/bold]")
        console.print(output)
        console.print()

    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print()
    console.print("[dim]This was a demo. Run 'midtry <task>' to query real models.[/dim]")


def cli_entry() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli_entry()
