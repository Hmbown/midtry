# MidTry: Codex Integration Handoff

## Mission

Make MidTry a universal reasoning enhancement skill that works across:
1. **Codex CLI** (OpenAI)
2. **Claude Code** (Anthropic) - already done
3. **Any LLM CLI tool** that supports custom commands/skills

Then **test it works** by running a reasoning task through the full protocol.

---

## What MidTry Is

MidTry externalizes DeepSeek R1 and mHC research for inference-time reasoning enhancement:

- **R1 GRPO**: Generate multiple reasoning paths, score with rule-based rewards, select best using group-relative advantage
- **mHC Multi-path**: 4 parallel reasoning streams with controlled diversity (temps 0.7-1.0)
- **Verification**: Explicit "wait, let me check" scaffolding

**Result**: Dramatically better reasoning on complex tasks without model retraining.

---

## Current State

### Files in this repo:
- `midtry.md` - The skill prompt (Claude Code format with `$ARGUMENTS` placeholder)
- `README.md` - Documentation
- `docs/ALGORITHM.md` - Technical spec
- `docs/RESEARCH.md` - Research foundation
- `examples/` - Sample outputs

### Already working:
- Claude Code: `~/.claude/commands/midtry.md`

---

## Your Tasks

### 1. Create Codex Skill (Agent Skills Standard)

Codex uses agent skills. Create a `midtry` skill at `.codex/skills/midtry` with:
- `SKILL.md` (metadata + workflow)
- `references/protocol.md` (full protocol and formatting)

Optional: add a `midtry` wrapper script that invokes `$midtry <task>` via `codex exec`.

### 2. Create Universal Installation Script

Create `install.sh` that:
```bash
#!/bin/bash
# Detect which CLI tools are installed and install midtry for each

# Claude Code
if [ -d "$HOME/.claude/commands" ]; then
    cp midtry.md "$HOME/.claude/commands/"
    echo "Installed for Claude Code"
fi

# Codex skill
if [ -d "$HOME/.codex/skills" ]; then
    cp -R .codex/skills/midtry "$HOME/.codex/skills/"
    echo "Installed for Codex skill"
fi

# Add other CLI tools as discovered
```

### 3. Test the Skill

Run this test problem through MidTry and verify all 6 phases execute:

**Test Problem:**
```
$midtry A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?
```

**Expected Behavior:**
1. Phase 1 should restate: "How many sheep remain after some run away"
2. Phase 2 should generate 4 paths (some may catch the trick, some may not)
3. Phase 3 should score paths on verification presence
4. Phase 4 should compute relative advantages
5. Phase 5 should check consensus
6. Phase 6 should verify the answer

**Correct Answer:** 9 (it's a trick question - "all BUT 9" means 9 remain)

**Success Criteria:**
- At least one path catches the trick wording
- That path scores higher due to verification
- Final answer is 9 with explanation of the wordplay

### 4. Document Codex-Specific Setup

Update README.md with:
- Codex installation instructions
- Any Codex-specific configuration
- How to invoke in Codex

---

## The MidTry Protocol (Reference)

```
PHASE 1: SCAFFOLD
- Restate problem
- Initial approach
- "Wait, let me verify..."
- Identify potential errors

PHASE 2: MULTI-PATH (4 paths)
- Path 1: Conservative (T=0.7)
- Path 2: Standard (T=0.8)
- Path 3: Creative (T=0.9)
- Path 4: Divergent (T=1.0)

PHASE 3: SCORE (rule-based)
- Verification steps: +0.4
- Structured reasoning: +0.3
- Edge cases: +0.2
- Format correct: +0.1

PHASE 4: SELECT (GRPO)
- Advantage = (score - mean) / std
- Select highest advantage

PHASE 5: CONSENSUS
- Count agreeing paths
- HIGH (3-4 agree), MEDIUM (2), LOW (all different)

PHASE 6: VERIFY
- Final "aha moment" check
- Arithmetic, understanding, edge cases
```

---

## Files You May Need to Create

1. `midtry_codex.md` - Codex-formatted version
2. `install.sh` - Universal installer
3. `test_midtry.sh` - Automated test runner (optional)

---

## Success Checklist

- [ ] MidTry works in Codex CLI
- [ ] Installation is documented
- [ ] Test problem (sheep) returns correct answer (9)
- [ ] All 6 phases visible in output
- [ ] README updated with Codex instructions

---

## Research Context

If you need to understand why MidTry works:

- **DeepSeek-R1** (arXiv:2501.12948): GRPO training produces self-reflection patterns. We scaffold these explicitly.
- **mHC** (arXiv:2512.24880): 4 parallel streams improve reasoning. We simulate with 4 reasoning paths.
- **Key insight**: Structured exploration + verification = better reasoning. Works at inference time, not just training.

---

**Go make MidTry universal. Test it. Ship it.**
