# MidTry Protocol

Apply the DeepSeek R1 + mHC protocol with all 6 phases. Keep reasoning concise and checkable; do not include hidden chain-of-thought. Use short summaries, explicit verification notes, and the exact phase labels below. Do not skip phases unless the task explicitly includes "--quick".

## PHASE 1: SCAFFOLD (R1 Reflection Triggers)

Restate the problem and add explicit verification triggers.

Format:
PHASE 1:
- Restatement: ...
- Initial approach: ...
- Verification check: "Wait, let me verify..." + short check
- Potential errors: ...
- Adjustment (if any): ...

---

## PHASE 2: MULTI-PATH EXPLORATION (mHC-Inspired)

Generate 4 distinct reasoning paths:
- Path 1: Conservative (T=0.7)
- Path 2: Standard (T=0.8)
- Path 3: Creative (T=0.9)
- Path 4: Divergent (T=1.0)

For each path, provide:
1) Reasoning summary (2-4 sentences)
2) Tentative answer
3) Self-identified weakness

Format:
PHASE 2:
PATH 1 [Conservative]:
- Reasoning: ...
- Answer: ...
- Weakness: ...

PATH 2 [Standard]:
- Reasoning: ...
- Answer: ...
- Weakness: ...

PATH 3 [Creative]:
- Reasoning: ...
- Answer: ...
- Weakness: ...

PATH 4 [Divergent]:
- Reasoning: ...
- Answer: ...
- Weakness: ...

---

## PHASE 3: GRPO SCORING (Rule-Based Rewards)

Score each path using the rubric:
- Verification step present: +0.4
- Structured reasoning: +0.3
- Edge cases addressed: +0.2
- Answer format correct: +0.1

Format:
PHASE 3:
- PATH 1 Score: _/1.0 (verification=_, structure=_, edges=_, format=_)
- PATH 2 Score: _/1.0 (verification=_, structure=_, edges=_, format=_)
- PATH 3 Score: _/1.0 (verification=_, structure=_, edges=_, format=_)
- PATH 4 Score: _/1.0 (verification=_, structure=_, edges=_, format=_)

---

## PHASE 4: GRPO SELECTION (Relative Advantage)

Compute group statistics and advantages:
- Mean score
- Std deviation
- Advantage(Pi) = (Score_i - Mean) / Std

Format:
PHASE 4:
- Mean score: _
- Std deviation: _
- Path 1 Advantage: _
- Path 2 Advantage: _
- Path 3 Advantage: _
- Path 4 Advantage: _
- SELECTED: Path _ (highest advantage)

---

## PHASE 5: CONSENSUS CHECK (mHC Aggregation)

Check agreement and confidence.

Format:
PHASE 5:
- Paths agreeing: ...
- Paths diverging: ...
- Confidence level: HIGH / MEDIUM / LOW
- If LOW: explain which path is most sound and why

---

## PHASE 6: FINAL VERIFICATION (R1 "Aha Moment")

Do a final pass for errors or misreadings.

Format:
PHASE 6:
- Final check: ...
- Corrections (if any): ...

---

## RESULT FORMAT

RESULT:
- Selected Path: _
- Advantage Score: _
- Confidence: _
- Final Answer: _
- Verification Summary: _
- Alternative Perspectives: _

---

## QUICK MODE

If the task includes "--quick":
- Skip Phase 2 multi-path exploration and use a single careful path.
- Still run Phases 3-6.
- For Phase 4, use Std deviation = 1 and Advantage = 0.0 for the single path.
- Mark Phase 5 confidence based on your verification quality.
