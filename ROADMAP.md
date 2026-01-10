# MidTry Roadmap

> Generated via MidTry v2 dogfooding - 4 models (Claude, Gemini, Codex, Qwen) provided diverse perspectives on how to make MidTry successful. This roadmap synthesizes their consensus and unique insights.

## TL;DR Reframe

**Old positioning:** "Inference-time GRPO simulation"
**New positioning:** "Multi-perspective reasoning harness for coding decisions"

> "Why trust one model's opinion? MidTry queries Claude, Gemini, Codex, and Qwen in parallel and synthesizes the best answer."

---

## Priority 1: Zero-Friction Distribution (This Week)

### 1.1 Publish to PyPI
```bash
pip install midtry
# or
pipx install midtry
```

**Tasks:**
- [ ] Complete `pyproject.toml` with CLI entry point
- [ ] Add `[project.scripts]` for `midtry` command
- [ ] Configure PyPI trusted publishing in GitHub
- [ ] Cut first release (v0.1.0)
- [ ] Add PyPI badge to README

### 1.2 One-Command Experience
```bash
midtry "Fix the bug in this code: ..."
midtry --models claude,gemini "Explain this error"
midtry demo  # Works without API keys (mocked responses)
```

**Tasks:**
- [x] Create `midtry/cli.py` with Typer/Click
- [x] Add `demo` command with sample responses
- [x] Add `--models` flag to select which CLIs to use
- [x] Add `--quick` flag for 2-model mode

---

## Priority 2: Python Port (Week 1-2) ✅ COMPLETE

### 2.1 Replace Bash with Python
The bash script limits:
- Windows compatibility
- Error handling
- Rich terminal output
- Library usage

**Tasks:**
- [x] Create `midtry/runner.py` with asyncio subprocess handling
- [x] Port config.toml parsing to native Python
- [x] Add `rich` for live progress during parallel inference
- [x] Add proper timeout handling
- [x] Show which models succeeded/failed in output
- [ ] Add retry/backoff (backlog)

### 2.2 Expose as Library
```python
import midtry

result = midtry.solve(
    "Optimize this SQL query",
    clis=["claude", "gemini"],
)
print(result.perspectives)  # dict of perspective -> output
print(result.format_responses())  # formatted string
```

**Tasks:**
- [x] Define `MidTryResult` dataclass
- [x] Create async `run_multi_agent()` API
- [x] Add sync wrapper `solve()` for non-async usage
- [ ] Document library usage in README

---

## Priority 3: Prove Value with Benchmarks (Week 2-3)

### 3.1 Evaluation Suite
```bash
midtry eval --suite coding-basic
# Outputs: bench/report.md + bench/results.json
```

**Tasks:**
- [ ] Create `bench/` directory with 10 curated tasks
- [ ] Tasks should include: bug finding, code review, test generation
- [ ] Compare: baseline (single model) vs MidTry v1 vs MidTry v2
- [ ] Measure: accuracy, consensus rate, cost, latency
- [ ] Generate markdown report with charts

### 3.2 Showcase "MidTry Wins"
Document cases where multi-agent caught errors single-agent missed.

**Tasks:**
- [ ] Create `examples/wins/` directory
- [ ] Add 3-5 real examples with before/after
- [ ] Include: the problem, single-agent response, MidTry response, why it's better

---

## Priority 4: Developer Integrations (Week 3-4)

### 4.1 VSCode Extension
- Run MidTry on selected code
- Show 4 perspectives in panel
- One-click apply suggested fix

### 4.2 GitHub Action
```yaml
- uses: hmbown/midtry-action@v1
  with:
    task: "Review this PR for bugs and security issues"
    models: claude,gemini
```

### 4.3 Pre-commit Hook
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/hmbown/midtry
  hooks:
    - id: midtry-review
```

**Tasks:**
- [ ] Create basic VSCode extension skeleton
- [ ] Create GitHub Action wrapper
- [ ] Add pre-commit hook support
- [ ] Document all integrations

---

## Priority 5: Lower Barrier to Entry (Ongoing)

### 5.1 Address Adversarial Feedback
Qwen identified real pain points:

| Issue | Solution |
|-------|----------|
| Requires 4 CLIs installed | Graceful degradation: work with 1+ CLI |
| Windows incompatible (bash) | Python port solves this |
| High latency (parallel calls) | Add `--fast` mode (2 models only) |
| No value without multiple providers | Temperature variation for single-model diversity |

### 5.2 Single-Model Fallback
For users with only one CLI:
```bash
midtry --model claude --variations 4  # Same model, different framings
```

**Tasks:**
- [ ] Implement temperature/framing variation mode
- [ ] Auto-detect available CLIs and adjust strategy
- [ ] Add `--cheap` mode (fewer models, lower cost)

### 5.3 Cloud Option (Future)
Consider hosted service that routes to multiple models via API:
- No local CLI setup required
- Pay-per-use pricing
- Consistent availability

---

## Priority 6: Content & Community (Ongoing)

### 6.1 Launch Content
- [ ] **README GIF**: 30-second demo of parallel agents working
- [ ] **Blog post**: "Why prompt diversity beats single-agent confidence"
- [ ] **Launch post**: r/LocalLLaMA, r/MachineLearning, Hacker News
- [ ] **Demo video**: 60-second walkthrough

### 6.2 Community Building
- [ ] Create GitHub Discussions
- [ ] Add CONTRIBUTING.md with "good first issues"
- [ ] Weekly "best-of" thread for interesting MidTry outputs
- [ ] Public roadmap (this file!)

### 6.3 Social Proof
- [ ] Add testimonials/quotes as they come in
- [ ] Track: GitHub stars, PyPI downloads, mentions
- [ ] Create "Powered by MidTry" badge for projects using it

---

## Technical Improvements (Backlog)

### Reliability
- [ ] Retry/backoff for failed CLI calls
- [ ] Partial failure handling (continue with N-1 models)
- [ ] Per-model timeout configuration
- [ ] Health check before spawning

### Cost Controls
- [ ] Budget caps (`--max-cost 0.50`)
- [ ] Token counting and reporting
- [ ] `--cheap` mode preset

### Determinism
- [ ] Seedable ordering for reproducibility
- [ ] Cache responses for identical inputs
- [ ] Deterministic aggregation

### Plugin Architecture
- [ ] Formal adapter interface for new CLIs
- [ ] Ollama adapter for local models
- [ ] OpenAI API adapter (not just CLI)
- [ ] Anthropic API adapter

### Templates
- [ ] `--template code-review`
- [ ] `--template bug-triage`
- [ ] `--template test-generation`
- [ ] Custom template support

---

## Metrics to Track

| Metric | Target (3 months) |
|--------|-------------------|
| GitHub stars | 500+ |
| PyPI weekly downloads | 100+ |
| Contributors | 5+ |
| Integrations (VSCode, GH Action) | 2+ |
| Benchmark improvement vs baseline | Documented |

---

## Immediate Next Steps

1. **Today**: Publish to PyPI (trusted publishing configured)
2. **Today**: Add demo GIF to README
3. **This week**: Python CLI port (replace bash)
4. **This week**: 3 example "wins" documented
5. **Next week**: Basic benchmark suite
6. **Next week**: Launch post on Reddit/HN

---

## Meta: Dogfooding Strategy

Continue using MidTry to make decisions about MidTry:
- Run strategic questions through v2
- Document interesting multi-agent outputs
- Use disagreements as signal for uncertainty
- Build showcase from our own usage

> This roadmap was generated by asking 4 models: "How could MidTry become popular?" The consensus items are high-confidence priorities. The adversarial perspective (Qwen) caught blind spots about barrier to entry.

---

*Last updated: 2025-01-10*
*Generated via MidTry v2 multi-agent consensus*
