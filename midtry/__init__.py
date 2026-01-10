"""MidTry - Multi-perspective reasoning harness for coding decisions."""

from importlib.resources import files

from .runner import (
    AgentResult,
    CLIConfig,
    MidTryConfig,
    MidTryResult,
    Perspective,
    detect_available_clis,
    run_multi_agent,
    solve_sync,
)

__all__ = [
    "AgentResult",
    "CLIConfig",
    "MidTryConfig",
    "MidTryResult",
    "Perspective",
    "__version__",
    "detect_available_clis",
    "load_protocol",
    "run_multi_agent",
    "solve",
    "solve_sync",
]
__version__ = "0.1.0"


def load_protocol() -> str:
    """Return the MidTry protocol text."""
    return files("midtry.data").joinpath("protocol.md").read_text(encoding="utf-8")


# Alias for cleaner API
solve = solve_sync
