---
name: midtry
description: Inference-time reasoning enhancement using DeepSeek R1 GRPO scoring and mHC multi-path exploration. Use when the user asks to run MidTry, requests multi-path reasoning, or needs explicit verification scaffolding for a complex task.
---

# MidTry

## Overview

Apply the MidTry protocol to a user task: scaffold reflection, explore 4 reasoning paths, score with rule-based rewards, select by relative advantage, check consensus, and verify.

## Workflow

1. Read the user task; treat any `--quick` flag as an explicit request for Quick Mode.
2. Follow `references/protocol.md` phase-by-phase and keep the phase labels and result format exactly.
3. Keep reasoning concise and checkable; avoid hidden chain-of-thought. Use short summaries, explicit verification notes, and clear weaknesses.
4. Ensure at least one path considers trick wording or edge cases; score paths consistently with the rubric.

## Output requirements

- Include all six phases unless `--quick` is present.
- Compute mean, standard deviation, and advantages.
- Provide a RESULT block with selected path, advantage score, confidence, final answer, verification summary, and alternatives.

## References

- `references/protocol.md` for the full protocol, formatting, and scoring rubric.
