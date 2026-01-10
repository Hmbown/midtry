# midtry

Query multiple LLM CLIs in parallel and compare their responses.

```bash
pip install midtry
midtry "Explain the tradeoffs between REST and GraphQL"
```

## What it does

MidTry spawns parallel calls to available AI CLIs (Claude, Gemini, Codex, etc.), each with a different reasoning perspective, and returns all responses for comparison.

```
$ midtry "Debug this function"

╭─────────────────────── Task ───────────────────────╮
│ Debug this function                                │
╰────────────────────────────────────────────────────╯

CLIs available: claude, gemini, codex, qwen
Mode: ORDERED
Timeout: 120s per call

  claude (conservative): done (12.3s)
  gemini (analytical): done (18.1s)
  codex (creative): done (15.7s)
  qwen (adversarial): done (22.4s)

=== RESPONSES ===
--- Response 1: Conservative (claude) ---
[methodical step-by-step analysis]

--- Response 2: Analytical (gemini) ---
[edge case focused breakdown]

--- Response 3: Creative (codex) ---
[alternative framing]

--- Response 4: Adversarial (qwen) ---
[challenges assumptions]
=== END RESPONSES ===
```

## Install

```bash
pip install midtry
```

Requires at least one supported CLI installed:

| CLI | Install |
|-----|---------|
| claude | [Claude Code](https://claude.ai/code) |
| gemini | [Gemini CLI](https://github.com/google-gemini/gemini-cli) |
| codex | [OpenAI Codex](https://github.com/openai/codex) |
| qwen | Qwen CLI |
| opencode | [OpenCode](https://github.com/opencode-ai/opencode) |
| copilot | GitHub Copilot CLI |

Check what's available:

```bash
midtry detect
```

## Usage

```bash
# Basic usage
midtry "Your question or task"

# Select specific models
midtry --models claude,gemini "Question"

# Quick mode (2 models only)
midtry --quick "Question"

# Random perspective assignment
midtry --random "Question"

# Demo mode (no API calls)
midtry demo
```

## Python API

```python
import midtry

result = midtry.solve("Optimize this SQL query", clis=["claude", "gemini"])

for r in result.results:
    print(f"{r.cli} ({r.perspective.value}): {r.output[:100]}...")
```

## Perspectives

Each CLI receives the task with a different framing:

| Perspective | Prompt style |
|-------------|--------------|
| Conservative | Careful, methodical, prioritizes correctness |
| Analytical | Systematic, considers edge cases |
| Creative | Alternative approaches, simpler reframings |
| Adversarial | Challenges obvious answers, looks for tricks |

## Configuration

Create `config.toml` in your working directory:

```toml
[midtry]
timeout_seconds = 120
max_parallel = 4
mode = "random"  # or "ordered"

[perspectives]
sources = ["claude", "gemini", "codex", "qwen"]

[perspectives.prompts]
conservative = "Solve carefully. Double-check each step. Task: {task}"
analytical = "Break down systematically. Consider edge cases. Task: {task}"
creative = "Consider unconventional approaches. Task: {task}"
adversarial = "Challenge the obvious answer. Task: {task}"
```

Or use environment variables:

```bash
MIDTRY_TIMEOUT=60 midtry "Question"
MIDTRY_CLIS="claude gemini" midtry "Question"
```

## Limitations

- Requires external CLI tools installed and authenticated
- Latency scales with slowest model
- No automatic synthesis of responses (you aggregate manually)
- Quality depends on underlying models

## When to use

- Complex problems where multiple viewpoints help
- Code review, debugging, architectural decisions
- When you want to see how different models approach a problem
- Building confidence through diverse perspectives

## When not to use

- Simple factual questions
- Time-sensitive queries
- Problems with obvious single solutions

## Background

MidTry applies ideas from DeepSeek-R1 (structured reasoning with verification) and mHC (multi-stream exploration) at inference time. The diversity comes from querying different models, not from training-time optimization.

## License

MIT

---

*Built with multi-agent consensus.*
