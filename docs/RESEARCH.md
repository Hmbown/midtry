# Research Foundation

MidTry externalizes training-time techniques from DeepSeek research for inference-time use.

## DeepSeek-R1 (arXiv:2501.12948)

### Key Techniques Externalized

#### 1. GRPO (Group Relative Policy Optimization)

**Training-time**: Trains models by computing advantages relative to group mean:
```
A_i = (r_i - mean(r)) / std(r)
```

**Inference-time (MidTry)**: Generate multiple candidates, score them, select using relative advantage rather than absolute score. This prevents over-optimization on any single metric.

#### 2. Rule-Based Rewards

**Training-time**: R1 explicitly avoids neural reward models due to reward hacking. Uses:
- Accuracy rewards (correct answer)
- Format rewards (proper structure)

**Inference-time (MidTry)**: Score responses on:
- Verification steps present (+0.4)
- Structured reasoning (+0.3)
- Edge cases addressed (+0.2)
- Format correctness (+0.1)

#### 3. Self-Reflection Emergence

**Training-time**: Through RL, R1 models spontaneously developed:
- `<think>...</think>` tags for reasoning
- "Wait, let me reconsider..." patterns
- Self-verification before answering

**Inference-time (MidTry)**: We scaffold these patterns explicitly, prompting the model to:
- Restate problems
- Check initial approaches
- Verify before finalizing

### R1 "Aha Moment"

The paper describes models developing "aha moments"—sudden realizations of errors mid-reasoning. MidTry's Phase 6 (Final Verification) explicitly triggers this pattern.

## mHC: Manifold-Constrained Hyper-Connections (arXiv:2512.24880)

### Key Techniques Externalized

#### 1. Multi-Stream Residual (n=4)

**Training-time**: Expands residual stream width by factor n=4, enabling richer information flow through the network.

**Inference-time (MidTry)**: Generate 4 parallel reasoning paths with controlled diversity (temperatures 0.7-1.0). Each path represents a distinct "stream" of reasoning.

#### 2. Doubly Stochastic Mixing

**Training-time**: Uses Sinkhorn-Knopp projection to create doubly stochastic mixing matrices, ensuring stable signal propagation.

**Inference-time (MidTry)**: Aggregate paths using weighted voting where weights derive from advantage scores. Consensus checking prevents any single path from dominating unfairly.

#### 3. Norm Preservation

**Training-time**: Bounds signal propagation to prevent gradient issues.

**Inference-time (MidTry)**: Confidence scoring based on path agreement. High consensus = high confidence, divergent paths = investigate further.

### mHC Benchmark Improvements

The paper reports 2-3% improvements on:
- BBH (Big Bench Hard)
- DROP (reading comprehension)
- Other reasoning benchmarks

## Why This Works at Inference Time

### The Core Insight

Both R1 and mHC reveal: **structured exploration with verification produces superior reasoning**.

At training time, this emerges from:
- Thousands of RL iterations
- Exposure to millions of examples
- Architectural innovations

At inference time, we can approximate this by:
- Explicitly scaffolding the exploration structure
- Generating diverse candidates
- Applying the same selection criteria

### Limitations

Inference-time techniques cannot fully replicate training-time improvements:
- No weight updates occur
- Exploration is limited to generation capacity
- Verification is limited to rule-based checks

But they can capture significant gains:
- Better problem decomposition
- Reduced premature convergence
- Explicit verification steps
- Multiple perspective consideration

## References

1. DeepSeek-AI. (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. arXiv:2501.12948

2. DeepSeek-AI. (2024). DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models. arXiv:2402.03300

3. mHC Authors. (2025). Manifold-Constrained Hyper-Connections. arXiv:2512.24880

4. DeepSeek-AI. (2024). DeepSeek-V3 Technical Report. arXiv:2412.19437
