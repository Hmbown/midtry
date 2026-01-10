"""Tests for midtry.runner module."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from midtry.runner import (
    AgentResult,
    CLIConfig,
    MidTryConfig,
    MidTryResult,
    Perspective,
    build_cli_command,
    detect_available_clis,
    filter_clis,
    run_cli,
    run_multi_agent,
    solve_sync,
)


class TestPerspective:
    """Test Perspective enum."""

    def test_perspective_values(self):
        assert Perspective.CONSERVATIVE == "conservative"
        assert Perspective.ANALYTICAL == "analytical"
        assert Perspective.CREATIVE == "creative"
        assert Perspective.ADVERSARIAL == "adversarial"


class TestCLIConfig:
    """Test CLIConfig dataclass."""

    def test_cli_config_defaults(self):
        config = CLIConfig(name="claude")
        assert config.name == "claude"
        assert config.timeout == 120.0
        assert config.model is None
        assert config.flags == []

    def test_cli_config_custom(self):
        config = CLIConfig(
            name="claude",
            timeout=60.0,
            model="claude-3-opus",
            flags=["--verbose"],
        )
        assert config.timeout == 60.0
        assert config.model == "claude-3-opus"
        assert config.flags == ["--verbose"]


class TestMidTryConfig:
    """Test MidTryConfig dataclass."""

    def test_config_defaults(self):
        config = MidTryConfig()
        assert config.timeout == 120.0
        assert config.max_parallel == 4
        assert config.mode == "ordered"
        assert len(config.sources) > 0
        assert len(config.perspective_order) > 0

    def test_config_custom(self):
        config = MidTryConfig(
            timeout=60.0,
            max_parallel=2,
            mode="random",
        )
        assert config.timeout == 60.0
        assert config.max_parallel == 2
        assert config.mode == "random"

    def test_from_toml_not_exists(self, tmp_path):
        config_path = tmp_path / "nonexistent.toml"
        config = MidTryConfig.from_toml(config_path)
        assert config.timeout == 120.0

    def test_from_toml_valid(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[midtry]
timeout_seconds = 90
max_parallel = 3
mode = "random"

[perspectives]
order = ["conservative", "analytical"]

[perspectives.prompts]
conservative = "Careful: {task}"
analytical = "Analyze: {task}"

[cli]
allow = ["claude"]
deny = ["codex"]

[cli.claude]
model = "claude-3-opus"
timeout_seconds = 100
        """)

        config = MidTryConfig.from_toml(config_file)
        assert config.timeout == 90
        assert config.max_parallel == 3
        assert config.mode == "random"
        assert config.allow == ["claude"]
        assert config.deny == ["codex"]
        assert "Careful: {task}" in config.prompts[Perspective.CONSERVATIVE]


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_agent_result_success(self):
        result = AgentResult(
            cli="claude",
            perspective=Perspective.CONSERVATIVE,
            output="Success",
            success=True,
            elapsed=1.0,
        )
        assert result.success
        assert result.error is None

    def test_agent_result_failure(self):
        result = AgentResult(
            cli="claude",
            perspective=Perspective.CONSERVATIVE,
            output="Error output",
            success=False,
            elapsed=1.0,
            error="Exit code 1",
        )
        assert not result.success
        assert result.error == "Exit code 1"


class TestMidTryResult:
    """Test MidTryResult dataclass."""

    def test_successful_results(self):
        results = [
            AgentResult("claude", Perspective.CONSERVATIVE, "A", True, 1.0),
            AgentResult("gemini", Perspective.ANALYTICAL, "B", False, 1.0),
            AgentResult("codex", Perspective.CREATIVE, "C", True, 1.0),
        ]
        result = MidTryResult(task="Test", results=results, mode="ordered")
        assert len(result.successful_results) == 2

    def test_perspectives(self):
        results = [
            AgentResult("claude", Perspective.CONSERVATIVE, "A", True, 1.0),
            AgentResult("gemini", Perspective.ANALYTICAL, "B", True, 1.0),
        ]
        result = MidTryResult(task="Test", results=results, mode="ordered")
        assert result.perspectives == {
            "conservative": "A",
            "analytical": "B",
        }

    def test_format_responses(self, sample_midtry_result):
        formatted = sample_midtry_result.format_responses()
        assert "=== RESPONSES ===" in formatted
        assert "Conservative" in formatted
        assert "=== END RESPONSES ===" in formatted


class TestDetectAvailableCLIs:
    """Test detect_available_clis function."""

    @patch("shutil.which")
    def test_detect_available_clis(self, mock_which):
        mock_which.side_effect = lambda x: x in ["claude", "gemini"]
        available = detect_available_clis()
        assert "claude" in available
        assert "gemini" in available
        assert "codex" not in available

    @patch("shutil.which")
    def test_detect_no_clis(self, mock_which):
        mock_which.return_value = None
        available = detect_available_clis()
        assert available == []


class TestFilterCLIs:
    """Test filter_clis function."""

    def test_filter_basic(self):
        available = ["claude", "gemini", "codex"]
        filtered = filter_clis(["claude", "codex"], available)
        assert filtered == ["claude", "codex"]

    def test_filter_allow(self):
        available = ["claude", "gemini", "codex"]
        filtered = filter_clis(
            ["claude", "gemini", "codex"],
            available,
            allow=["claude", "gemini"],
        )
        assert filtered == ["claude", "gemini"]

    def test_filter_deny(self):
        available = ["claude", "gemini", "codex"]
        filtered = filter_clis(
            ["claude", "gemini", "codex"],
            available,
            deny=["codex"],
        )
        assert filtered == ["claude", "gemini"]

    def test_filter_unavailable(self):
        available = ["claude"]
        filtered = filter_clis(["claude", "gemini"], available)
        assert filtered == ["claude"]

    def test_filter_cli_prefix(self):
        available = ["claude"]
        filtered = filter_clis(["cli:claude"], available)
        assert filtered == ["claude"]

    def test_filter_claude_task(self):
        available = ["claude-task"]
        filtered = filter_clis(["claude", "claude-task"], available)
        assert filtered == []

    def test_filter_empty(self):
        available = ["claude"]
        filtered = filter_clis([], available)
        assert filtered == []


class TestBuildCLICommand:
    """Test build_cli_command function."""

    def test_build_claude(self):
        config = CLIConfig(name="claude")
        cmd = build_cli_command("claude", "Test prompt", config)
        assert cmd == ["claude", "-p", "Test prompt"]

    def test_build_gemini(self):
        config = CLIConfig(name="gemini")
        cmd = build_cli_command("gemini", "Test prompt", config)
        assert cmd == ["gemini", "Test prompt"]

    def test_build_codex_default(self):
        config = CLIConfig(name="codex")
        cmd = build_cli_command("codex", "Test prompt", config)
        assert cmd == ["codex", "exec", "--color", "never", "Test prompt"]

    def test_build_codex_custom_flags(self):
        config = CLIConfig(name="codex", flags=["--verbose"])
        cmd = build_cli_command("codex", "Test prompt", config)
        assert cmd == ["codex", "exec", "--verbose", "Test prompt"]

    def test_build_qwen(self):
        config = CLIConfig(name="qwen")
        cmd = build_cli_command("qwen", "Test prompt", config)
        assert cmd == ["qwen", "Test prompt"]

    def test_build_opencode_default(self):
        config = CLIConfig(name="opencode")
        cmd = build_cli_command("opencode", "Test prompt", config)
        assert cmd == ["opencode", "run", "--model", "deepseek/deepseek-chat", "Test prompt"]

    def test_build_opencode_custom_model(self):
        config = CLIConfig(name="opencode", model="gpt-4")
        cmd = build_cli_command("opencode", "Test prompt", config)
        assert cmd == ["opencode", "run", "--model", "gpt-4", "Test prompt"]

    def test_build_copilot(self):
        config = CLIConfig(name="copilot")
        cmd = build_cli_command("copilot", "Test prompt", config)
        assert cmd == ["copilot", "-p", "Test prompt", "--allow-all-tools"]

    def test_build_unknown_cli(self):
        config = CLIConfig(name="unknown")
        with pytest.raises(ValueError, match="Unknown CLI"):
            build_cli_command("unknown", "Test prompt", config)


class TestRunCLI:
    """Test run_cli async function."""

    @pytest.mark.asyncio
    @patch("midtry.runner.asyncio.create_subprocess_exec")
    async def test_run_cli_success(self, mock_exec):
        proc = MagicMock()
        proc.returncode = 0
        proc.communicate = AsyncMock(return_value=(b"Output", b""))
        mock_exec.return_value = proc

        config = CLIConfig(name="claude")
        result = await run_cli("claude", "Test", Perspective.CONSERVATIVE, config, 10)

        assert result.success
        assert result.cli == "claude"
        assert result.output == "Output"
        assert result.elapsed > 0

    @pytest.mark.asyncio
    @patch("midtry.runner.asyncio.create_subprocess_exec")
    async def test_run_cli_failure(self, mock_exec):
        proc = MagicMock()
        proc.returncode = 1
        proc.communicate = AsyncMock(return_value=(b"Error", b""))
        mock_exec.return_value = proc

        config = CLIConfig(name="claude")
        result = await run_cli("claude", "Test", Perspective.CONSERVATIVE, config, 10)

        assert not result.success
        assert result.error == "Exit code 1"

    @pytest.mark.asyncio
    @patch("midtry.runner.asyncio.create_subprocess_exec")
    async def test_run_cli_timeout(self, mock_exec):
        proc = MagicMock()
        proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_exec.return_value = proc

        config = CLIConfig(name="claude")
        result = await run_cli("claude", "Test", Perspective.CONSERVATIVE, config, 10)

        assert not result.success
        assert result.error == "Timeout"

    @pytest.mark.asyncio
    @patch("midtry.runner.asyncio.create_subprocess_exec")
    async def test_run_cli_exception(self, mock_exec):
        mock_exec.side_effect = FileNotFoundError("Command not found")

        config = CLIConfig(name="claude")
        result = await run_cli("claude", "Test", Perspective.CONSERVATIVE, config, 10)

        assert not result.success
        assert result.error == "Command not found"


class TestRunMultiAgent:
    """Test run_multi_agent async function."""

    @pytest.mark.asyncio
    @patch("midtry.runner.detect_available_clis")
    @patch("midtry.runner.run_cli")
    async def test_run_multi_agent_basic(self, mock_run_cli, mock_detect, sample_config):
        mock_detect.return_value = ["claude", "gemini"]
        mock_run_cli.side_effect = [
            AgentResult("claude", Perspective.CONSERVATIVE, "A", True, 1.0),
            AgentResult("gemini", Perspective.ANALYTICAL, "B", True, 1.5),
        ]

        result = await run_multi_agent("Test task", sample_config)

        assert result.task == "Test task"
        assert len(result.results) == 2
        assert result.mode == "ordered"
        assert mock_run_cli.call_count == 2

    @pytest.mark.asyncio
    @patch("midtry.runner.detect_available_clis")
    @patch("midtry.runner.run_cli")
    async def test_run_multi_agent_callbacks(self, mock_run_cli, mock_detect):
        mock_detect.return_value = ["claude"]
        mock_run_cli.return_value = AgentResult("claude", Perspective.CONSERVATIVE, "A", True, 1.0)

        on_start_calls = []
        on_complete_calls = []

        def on_start(cli, perspective):
            on_start_calls.append((cli, perspective))

        def on_complete(result):
            on_complete_calls.append(result)

        await run_multi_agent("Test", None, None, on_start, on_complete)

        assert len(on_start_calls) == 1
        assert on_start_calls[0] == ("claude", Perspective.CONSERVATIVE)
        assert len(on_complete_calls) == 1

    @pytest.mark.asyncio
    @patch("midtry.runner.detect_available_clis")
    async def test_run_multi_agent_no_clis(self, mock_detect):
        mock_detect.return_value = []
        with pytest.raises(RuntimeError, match="No supported CLIs"):
            await run_multi_agent("Test", None, None)

    @pytest.mark.asyncio
    @patch("midtry.runner.detect_available_clis")
    @patch("midtry.runner.run_cli")
    async def test_run_multi_agent_random_mode(self, mock_run_cli, mock_detect):
        mock_detect.return_value = ["claude", "gemini"]
        mock_run_cli.side_effect = [
            AgentResult("claude", Perspective.CONSERVATIVE, "A", True, 1.0),
            AgentResult("gemini", Perspective.ANALYTICAL, "B", True, 1.5),
        ]

        config = MidTryConfig(mode="random")
        result = await run_multi_agent("Test", config)

        assert result.mode == "random"


class TestSolveSync:
    """Test solve_sync function."""

    @patch("asyncio.run")
    def test_solve_sync(self, mock_run):
        mock_result = MidTryResult(
            task="Test",
            results=[],
            mode="ordered",
        )
        mock_run.return_value = mock_result

        result = solve_sync("Test")
        assert result.task == "Test"
        mock_run.assert_called_once()
