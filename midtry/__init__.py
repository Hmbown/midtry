"""MidTry protocol helpers."""

from importlib.resources import files

__all__ = ["load_protocol", "__version__"]
__version__ = "0.1.0"


def load_protocol() -> str:
    """Return the MidTry protocol text."""
    return files("midtry.data").joinpath("protocol.md").read_text(encoding="utf-8")
