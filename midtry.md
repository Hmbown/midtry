# MidTry: Inference-Time Reasoning Enhancement

> **Research Foundation**: DeepSeek R1 (GRPO) + mHC (Multi-path reasoning)
>
> This skill externalizes training-time techniques for inference-time use:
> - **R1 Pattern**: Multi-candidate sampling with group-relative advantage selection
> - **mHC Pattern**: 4 parallel reasoning paths with weighted aggregation
> - **Verification**: Rule-based scoring (not neural reward models)

## Task
$ARGUMENTS

---

## PROTOCOL: Enhanced Reasoning Pipeline

You will now apply DeepSeek R1 and mHC research to solve this task with dramatically improved reasoning quality. Follow this protocol exactly.

### PHASE 1: SCAFFOLD (R1 Reflection Triggers)

R1 discovered that self-reflection patterns (`<think>`, "wait, let me check") emerge from RL training and dramatically improve reasoning. We scaffold these explicitly.

**Before answering, reframe the problem:**

```
<think>
PROBLEM RESTATEMENT: [Restate the problem in your own words]

INITIAL APPROACH: [What's your first instinct?]

WAIT - Let me verify this is correct...
[Explicitly check your initial approach]

POTENTIAL ERRORS: [What could go wrong?]

RECONSIDERING: [If errors found, adjust approach]
</think>
```

---

### PHASE 2: MULTI-PATH EXPLORATION (mHC-Inspired)

mHC research shows that 4 parallel reasoning streams dramatically improve performance. Generate 4 distinct reasoning paths:

**Path 1 (Conservative, T=0.7)**: The most obvious, careful approach
**Path 2 (Standard, T=0.8)**: A balanced approach with some creativity
**Path 3 (Creative, T=0.9)**: An alternative framing or method
**Path 4 (Divergent, T=1.0)**: A contrarian or unconventional approach

For each path, produce:
1. Core reasoning (2-4 sentences)
2. Tentative answer
3. Self-identified weaknesses

**Format:**
```
PATH 1 [Conservative]:
Reasoning: ...
Answer: ...
Weakness: ...

PATH 2 [Standard]:
Reasoning: ...
Answer: ...
Weakness: ...

PATH 3 [Creative]:
Reasoning: ...
Answer: ...
Weakness: ...

PATH 4 [Divergent]:
Reasoning: ...
Answer: ...
Weakness: ...
```

---

### PHASE 3: GRPO SCORING (Rule-Based Rewards)

R1 uses GRPO (Group Relative Policy Optimization) with rule-based rewards to avoid reward model hacking. Score each path:

**Scoring Rubric (from R1 paper):**

| Criterion | Points | Check |
|-----------|--------|-------|
| Contains verification step ("wait", "check", "verify") | +0.4 | Self-correction present? |
| Structured reasoning (clear steps) | +0.3 | Logical flow? |
| Addresses edge cases | +0.2 | Robustness? |
| Answer format correct | +0.1 | Clear final answer? |

**Score each path:**
```
PATH 1 Score: _/1.0 (breakdown: verification=_, structure=_, edges=_, format=_)
PATH 2 Score: _/1.0 (breakdown: ...)
PATH 3 Score: _/1.0 (breakdown: ...)
PATH 4 Score: _/1.0 (breakdown: ...)
```

---

### PHASE 4: GRPO SELECTION (Relative Advantage)

R1's key insight: Select based on **relative** advantage, not absolute score.

**Compute group statistics:**
```
Mean score: (P1 + P2 + P3 + P4) / 4 = _
Std deviation: _

Advantage(Pi) = (Score_i - Mean) / Std

Path 1 Advantage: _
Path 2 Advantage: _
Path 3 Advantage: _
Path 4 Advantage: _

SELECTED: Path _ (highest advantage)
```

---

### PHASE 5: MHC AGGREGATION (Consensus Check)

mHC uses doubly-stochastic mixing to aggregate paths. Check for consensus:

1. **Do paths agree?** If 3+ paths give same answer → HIGH confidence
2. **Weighted agreement?** Weight answers by advantage scores
3. **Divergence?** If paths disagree significantly → investigate why

```
CONSENSUS CHECK:
- Paths agreeing: [list]
- Paths diverging: [list]
- Confidence level: [HIGH/MEDIUM/LOW]
- If LOW: Which path's reasoning is most sound and why?
```

---

### PHASE 6: FINAL VERIFICATION (R1 "Aha Moment")

R1 models developed "aha moments" - sudden realizations of errors. Before finalizing:

```
FINAL CHECK:
- Wait, did I make any arithmetic errors?
- Wait, did I misread the problem?
- Wait, does my answer actually address what was asked?
- Wait, are there any edge cases I missed?
```

If errors found, return to the selected path and correct.

---

## OUTPUT FORMAT

After completing all phases, present your answer:

```
<answer>
## Result

**Selected Path**: [N] ([Conservative/Standard/Creative/Divergent])

**Advantage Score**: [X.XX] (relative to group mean)

**Confidence**: [HIGH/MEDIUM/LOW] based on path consensus

**Answer**:
[Your final answer here]

**Verification Summary**:
- [Key verification step 1]
- [Key verification step 2]

**Alternative Perspectives Considered**:
- [Brief note on other paths and why they were not selected]
</answer>
```

---

## RULES

1. **Complete all 6 phases** - Don't skip steps even if the answer seems obvious
2. **Show your work** - The reasoning process IS the value
3. **Be honest about uncertainty** - LOW confidence is valid and useful
4. **No premature convergence** - Generate truly distinct paths, not variations
5. **Trust the process** - GRPO selection works better than intuition

---

## QUICK MODE

If the user adds `--quick` or the task is simple arithmetic/lookup:

1. Skip multi-path (use single careful path)
2. Still apply reflection scaffold
3. Still verify before answering

---

## RESEARCH FOUNDATION

This skill externalizes insights from:

1. **DeepSeek-R1** (arXiv:2501.12948): GRPO with rule-based rewards, self-reflection emergence
2. **mHC** (arXiv:2512.24880): Multi-stream reasoning with constrained aggregation
3. **DeepSeekMath**: Group relative policy optimization

The key insight: These techniques work at inference time, not just training time.

---

**Begin the MidTry protocol now. Start with Phase 1: SCAFFOLD.**
