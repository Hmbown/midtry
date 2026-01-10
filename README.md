# MidTry

**Inference-Time Reasoning Enhancement for Claude Code**

MidTry is a Claude Code skill that externalizes DeepSeek R1 and mHC research techniques to dramatically improve LLM reasoning quality at inference time—no model retraining required.

## What It Does

MidTry applies two breakthrough research insights to every reasoning task:

1. **DeepSeek R1's GRPO Selection**: Generate multiple reasoning paths, score them with rule-based rewards, select the best using group-relative advantage
2. **mHC Multi-Path Reasoning**: Explore 4 parallel reasoning streams with controlled diversity, aggregate results with confidence weighting

**Result**: Significantly better reasoning on complex tasks, math problems, code challenges, and analytical questions.

## Installation

### Quick Install (Recommended)

```bash
# Create the Claude Code commands directory if it doesn't exist
mkdir -p ~/.claude/commands

# Download midtry.md directly
curl -o ~/.claude/commands/midtry.md https://raw.githubusercontent.com/Hmbown/midtry/main/midtry.md
```

### Manual Install

1. Download `midtry.md` from this repository
2. Copy it to `~/.claude/commands/midtry.md`
3. Restart Claude Code

## Usage

Once installed, invoke MidTry with any reasoning task:

```
/midtry What is the probability of getting exactly 3 heads in 5 fair coin flips?
```

```
/midtry Debug this code: [paste code]
```

```
/midtry Explain the tradeoffs between microservices and monolithic architecture
```

### Quick Mode

For simpler tasks, add `--quick` to skip multi-path exploration:

```
/midtry --quick What is 17 * 23?
```

## How It Works

MidTry implements a 6-phase reasoning protocol:

### Phase 1: Scaffold (R1 Reflection Triggers)
Adds explicit self-reflection structure that R1 models developed through RL training:
- Problem restatement
- Initial approach
- "Wait, let me verify..." triggers
- Error checking

### Phase 2: Multi-Path Exploration (mHC-Inspired)
Generates 4 distinct reasoning paths with varying "temperatures":
- **Conservative (T=0.7)**: Careful, obvious approach
- **Standard (T=0.8)**: Balanced reasoning
- **Creative (T=0.9)**: Alternative framing
- **Divergent (T=1.0)**: Contrarian perspective

### Phase 3: GRPO Scoring
Scores each path using rule-based rewards (avoiding neural reward model hacking):
- Verification steps present: +0.4
- Structured reasoning: +0.3
- Edge cases addressed: +0.2
- Format correctness: +0.1

### Phase 4: GRPO Selection
Selects the best path using **relative advantage**:
```
Advantage(path_i) = (score_i - mean(all_scores)) / std(all_scores)
```

### Phase 5: mHC Aggregation
Checks consensus across paths to determine confidence level.

### Phase 6: Final Verification
R1's "aha moment" pattern—one last check for errors before finalizing.

## Research Foundation

MidTry externalizes techniques from these papers:

### DeepSeek-R1 (arXiv:2501.12948)
- **Key Insight**: GRPO with rule-based rewards produces dramatically better reasoning
- **Externalized**: Multi-candidate scoring + relative advantage selection
- **Result**: The "wait, let me check" patterns that emerge from RL training

### mHC: Manifold-Constrained Hyper-Connections (arXiv:2512.24880)
- **Key Insight**: 4 parallel residual streams improve information flow
- **Externalized**: Multi-path reasoning with weighted aggregation
- **Result**: 2-3% improvement on benchmarks like BBH and DROP

### Core Principle
Both papers reveal: **structured exploration with verification produces superior reasoning**. MidTry brings this to inference time.

## Expected Impact

Based on the underlying research:

| Task Type | Improvement |
|-----------|-------------|
| Math (AIME-style) | Significant improvement on multi-step problems |
| Code debugging | Better error identification through multiple perspectives |
| Analytical reasoning | Higher confidence through consensus checking |
| Complex decisions | More thorough consideration of alternatives |

## Examples

### Math Problem
```
/midtry A bag contains 5 red balls and 3 blue balls. If 3 balls are drawn without replacement, what is the probability that exactly 2 are red?
```

MidTry will:
1. Scaffold the problem with verification triggers
2. Generate 4 solution approaches (combinatorial, tree diagram, simulation logic, edge case analysis)
3. Score each for verification steps and structure
4. Select the highest-advantage path
5. Report confidence based on path agreement

### Code Review
```
/midtry Review this function for bugs:
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n)
```

MidTry will:
1. Restate what the code should do
2. Analyze from 4 perspectives (logic flow, edge cases, performance, style)
3. Identify the recursion bug (should be `n-1`)
4. Report with high confidence due to path consensus

## Configuration

MidTry uses sensible defaults, but you can customize by editing `~/.claude/commands/midtry.md`:

- **Number of paths**: Default 4 (mHC optimal)
- **Scoring weights**: Adjustable verification/structure/edge/format weights
- **Quick mode threshold**: When to skip multi-path

## Contributing

Contributions welcome! Areas of interest:
- Additional verification criteria
- Domain-specific scoring rubrics (math, code, writing)
- Integration with code execution for automated verification
- Benchmark results on standard datasets

## License

MIT License - see [LICENSE](LICENSE)

## Citation

If you use MidTry in research, please cite the underlying papers:

```bibtex
@article{deepseek-r1,
  title={DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning},
  author={DeepSeek-AI},
  journal={arXiv preprint arXiv:2501.12948},
  year={2025}
}

@article{mhc,
  title={Manifold-Constrained Hyper-Connections for Multi-Stream Information Flow},
  author={...},
  journal={arXiv preprint arXiv:2512.24880},
  year={2025}
}
```

---

**Built with insights from DeepSeek research. Reasoning, enhanced.**
