"""MidTry test fixtures."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from midtry.runner import (
    AgentResult,
    MidTryConfig,
    MidTryResult,
    Perspective,
)


@pytest.fixture
def sample_config():
    """Return a sample MidTryConfig."""
    return MidTryConfig(
        timeout=10.0,
        max_parallel=2,
        mode="ordered",
    )


@pytest.fixture
def sample_agent_result():
    """Return a sample AgentResult."""
    return AgentResult(
        cli="claude",
        perspective=Perspective.CONSERVATIVE,
        output="Test output",
        success=True,
        elapsed=1.5,
    )


@pytest.fixture
def sample_midtry_result(sample_agent_result):
    """Return a sample MidTryResult."""
    return MidTryResult(
        task="Test task",
        results=[sample_agent_result],
        mode="ordered",
    )


@pytest.fixture
def mock_subprocess():
    """Mock for asyncio subprocess."""
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        proc = MagicMock()
        proc.returncode = 0
        proc.communicate = AsyncMock(return_value=(b"Test output", b""))
        mock_exec.return_value = proc
        yield mock_exec
