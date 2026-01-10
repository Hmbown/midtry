"""MidTry v2 Multi-Agent Runner - Async subprocess handling."""

from __future__ import annotations

import asyncio
import random
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python 3.10 fallback


class Perspective(str, Enum):
    CONSERVATIVE = "conservative"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    ADVERSARIAL = "adversarial"


DEFAULT_PROMPTS = {
    Perspective.CONSERVATIVE: "Solve this carefully and methodically. Double-check each step. Prioritize correctness over creativity. Task: {task}",
    Perspective.ANALYTICAL: "Break this down systematically. Consider edge cases. What could go wrong? Task: {task}",
    Perspective.CREATIVE: "Consider unconventional approaches. Is there a simpler reframing? Task: {task}",
    Perspective.ADVERSARIAL: "Challenge the obvious answer. What if the common interpretation is wrong? Look for tricks: {task}",
}

SUPPORTED_CLIS = ["claude", "gemini", "codex", "qwen", "opencode", "copilot"]


@dataclass
class CLIConfig:
    """Configuration for a specific CLI."""

    name: str
    timeout: float = 120.0
    model: str | None = None
    flags: list[str] = field(default_factory=list)


@dataclass
class MidTryConfig:
    """Full MidTry configuration."""

    timeout: float = 120.0
    max_parallel: int = 4
    mode: str = "ordered"  # "ordered" or "random"
    sources: list[str] = field(default_factory=lambda: SUPPORTED_CLIS.copy())
    perspective_order: list[Perspective] = field(
        default_factory=lambda: list(Perspective)
    )
    prompts: dict[Perspective, str] = field(
        default_factory=lambda: DEFAULT_PROMPTS.copy()
    )
    allow: list[str] = field(default_factory=list)
    deny: list[str] = field(default_factory=list)
    cli_configs: dict[str, CLIConfig] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: Path) -> MidTryConfig:
        """Load config from TOML file."""
        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        midtry = data.get("midtry", {})
        perspectives = data.get("perspectives", {})
        cli_section = data.get("cli", {})

        # Parse perspective order
        order_strs = perspectives.get("order", [])
        perspective_order = []
        for name in order_strs:
            try:
                perspective_order.append(Perspective(name))
            except ValueError:
                pass
        if not perspective_order:
            perspective_order = list(Perspective)

        # Parse custom prompts
        prompts = DEFAULT_PROMPTS.copy()
        custom_prompts = perspectives.get("prompts", {})
        for key, value in custom_prompts.items():
            try:
                prompts[Perspective(key)] = value
            except ValueError:
                pass

        # Parse CLI configs
        cli_configs = {}
        for cli_name in SUPPORTED_CLIS:
            cli_data = cli_section.get(cli_name, {})
            cli_configs[cli_name] = CLIConfig(
                name=cli_name,
                timeout=cli_data.get(
                    "timeout_seconds",
                    cli_section.get("timeout_seconds", midtry.get("timeout_seconds", 120.0)),
                ),
                model=cli_data.get("model"),
                flags=cli_data.get("flags", []),
            )

        return cls(
            timeout=midtry.get("timeout_seconds", 120.0),
            max_parallel=midtry.get("max_parallel", 4),
            mode=midtry.get("mode", "ordered"),
            sources=perspectives.get("sources", SUPPORTED_CLIS.copy()),
            perspective_order=perspective_order,
            prompts=prompts,
            allow=cli_section.get("allow", []),
            deny=cli_section.get("deny", []),
            cli_configs=cli_configs,
        )


@dataclass
class AgentResult:
    """Result from a single agent run."""

    cli: str
    perspective: Perspective
    output: str
    success: bool
    elapsed: float
    error: str | None = None


@dataclass
class MidTryResult:
    """Combined result from all agents."""

    task: str
    results: list[AgentResult]
    mode: str

    @property
    def successful_results(self) -> list[AgentResult]:
        return [r for r in self.results if r.success]

    @property
    def perspectives(self) -> dict[str, str]:
        return {r.perspective.value: r.output for r in self.successful_results}

    def format_responses(self) -> str:
        """Format all responses for display."""
        lines = ["", "=== RESPONSES ===", ""]
        for i, result in enumerate(self.results, 1):
            status = "" if result.success else " [FAILED]"
            lines.append(f"--- Response {i}: {result.perspective.value.title()} ({result.cli}){status} ---")
            if result.success:
                lines.append(result.output)
            else:
                lines.append(f"Error: {result.error or 'Unknown error'}")
            lines.append("")
        lines.append("=== END RESPONSES ===")
        lines.append("")
        lines.append("Aggregate these responses to determine the best answer.")
        return "\n".join(lines)


def detect_available_clis() -> list[str]:
    """Detect which CLIs are available on the system."""
    available = []
    for cli in SUPPORTED_CLIS:
        if shutil.which(cli):
            available.append(cli)
    return available


def filter_clis(
    requested: list[str],
    available: list[str],
    allow: list[str] | None = None,
    deny: list[str] | None = None,
) -> list[str]:
    """Filter CLIs by availability and allow/deny lists."""
    filtered = []
    for cli in requested:
        cli = cli.removeprefix("cli:")
        if cli == "claude-task":
            continue
        if cli not in available:
            continue
        if allow and cli not in allow:
            continue
        if deny and cli in deny:
            continue
        filtered.append(cli)
    return filtered


def build_cli_command(cli: str, prompt: str, config: CLIConfig) -> list[str]:
    """Build the command for a specific CLI."""
    if cli == "claude":
        return ["claude", "-p", prompt]
    elif cli == "gemini":
        return ["gemini", prompt]
    elif cli == "codex":
        flags = config.flags or ["--color", "never"]
        return ["codex", "exec", *flags, prompt]
    elif cli == "qwen":
        return ["qwen", prompt]
    elif cli == "opencode":
        model = config.model or "deepseek/deepseek-chat"
        return ["opencode", "run", "--model", model, prompt]
    elif cli == "copilot":
        return ["copilot", "-p", prompt, "--allow-all-tools"]
    else:
        raise ValueError(f"Unknown CLI: {cli}")


async def run_cli(
    cli: str,
    prompt: str,
    perspective: Perspective,
    config: CLIConfig,
    timeout: float,
) -> AgentResult:
    """Run a single CLI call asynchronously."""
    import time

    start = time.monotonic()
    cmd = build_cli_command(cli, prompt, config)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        elapsed = time.monotonic() - start
        output = stdout.decode("utf-8", errors="replace")

        if proc.returncode == 0:
            return AgentResult(
                cli=cli,
                perspective=perspective,
                output=output,
                success=True,
                elapsed=elapsed,
            )
        else:
            return AgentResult(
                cli=cli,
                perspective=perspective,
                output=output,
                success=False,
                elapsed=elapsed,
                error=f"Exit code {proc.returncode}",
            )
    except asyncio.TimeoutError:
        elapsed = time.monotonic() - start
        return AgentResult(
            cli=cli,
            perspective=perspective,
            output="",
            success=False,
            elapsed=elapsed,
            error="Timeout",
        )
    except Exception as e:
        elapsed = time.monotonic() - start
        return AgentResult(
            cli=cli,
            perspective=perspective,
            output="",
            success=False,
            elapsed=elapsed,
            error=str(e),
        )


async def run_multi_agent(
    task: str,
    config: MidTryConfig | None = None,
    clis: list[str] | None = None,
    on_start: Any = None,  # Callback: (cli, perspective) -> None
    on_complete: Any = None,  # Callback: (result) -> None
) -> MidTryResult:
    """Run multiple CLI agents in parallel with different perspectives."""
    if config is None:
        config = MidTryConfig()

    # Detect and filter CLIs
    available = detect_available_clis()
    requested = clis or config.sources
    filtered_clis = filter_clis(requested, available, config.allow, config.deny)

    if not filtered_clis:
        raise RuntimeError(
            f"No supported CLIs found. Install one of: {', '.join(SUPPORTED_CLIS)}"
        )

    # Limit to max_parallel
    filtered_clis = filtered_clis[: config.max_parallel]

    # Get perspectives and prompts
    perspectives = list(config.perspective_order)
    prompts = config.prompts.copy()

    # Apply random mode
    if config.mode == "random":
        random.shuffle(filtered_clis)
        random.shuffle(perspectives)

    # Build tasks
    tasks = []
    assignments = []  # Track (cli, perspective) pairs

    for i, cli in enumerate(filtered_clis):
        perspective = perspectives[i % len(perspectives)]
        prompt = prompts[perspective].format(task=task)
        cli_config = config.cli_configs.get(cli, CLIConfig(name=cli))

        if on_start:
            on_start(cli, perspective)

        tasks.append(run_cli(cli, prompt, perspective, cli_config, config.timeout))
        assignments.append((cli, perspective))

    # Run all tasks in parallel
    results = await asyncio.gather(*tasks)

    # Fire completion callbacks
    if on_complete:
        for result in results:
            on_complete(result)

    return MidTryResult(task=task, results=list(results), mode=config.mode)


def solve_sync(
    task: str,
    config: MidTryConfig | None = None,
    clis: list[str] | None = None,
) -> MidTryResult:
    """Synchronous wrapper for run_multi_agent."""
    return asyncio.run(run_multi_agent(task, config, clis))
