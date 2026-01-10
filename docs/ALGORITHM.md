# MidTry Algorithm Specification

## Pseudocode

```
ALGORITHM: MidTry Enhanced Reasoning Protocol

INPUT: task (string)
OUTPUT: enhanced_response (string), confidence (HIGH|MEDIUM|LOW)

1. SCAFFOLD PHASE:
   scaffolded_task ← add_reflection_triggers(task)
   // Adds: problem restatement, initial approach, verification prompts

2. MULTI-PATH GENERATION:
   paths ← []
   FOR i IN [1, 2, 3, 4]:
       temperature ← 0.6 + (i * 0.1)  // 0.7, 0.8, 0.9, 1.0
       path ← generate_reasoning_path(scaffolded_task, temperature, path_type[i])
       paths.append(path)
   // path_type: [Conservative, Standard, Creative, Divergent]

3. SCORING PHASE:
   FOR each path IN paths:
       score ← 0
       IF contains_verification(path): score += 0.4
       IF has_structure(path): score += 0.3
       IF addresses_edges(path): score += 0.2
       IF format_correct(path): score += 0.1
       path.score ← score

4. GRPO SELECTION:
   scores ← [p.score FOR p IN paths]
   mean_score ← mean(scores)
   std_score ← std(scores)

   FOR each path IN paths:
       path.advantage ← (path.score - mean_score) / std_score

   selected ← argmax(paths, key=advantage)

5. CONSENSUS CHECK:
   answers ← extract_answers(paths)
   agreement_count ← count_matching(answers)

   IF agreement_count >= 3:
       confidence ← HIGH
   ELIF agreement_count >= 2:
       confidence ← MEDIUM
   ELSE:
       confidence ← LOW
       // Investigate divergence

6. FINAL VERIFICATION:
   // "Aha moment" trigger
   verified_response ← final_check(selected.response)
   // Checks: arithmetic, problem understanding, edge cases

RETURN verified_response, confidence
```

## Scoring Function Details

### Verification Check (+0.4)
```python
def contains_verification(response):
    patterns = [
        r"wait",
        r"let me (check|verify|reconsider)",
        r"hold on",
        r"actually",
        r"hmm",
        r"checking",
        r"verify"
    ]
    return any(re.search(p, response.lower()) for p in patterns)
```

### Structure Check (+0.3)
```python
def has_structure(response):
    indicators = [
        "step 1" or "first",
        "step 2" or "second" or "then",
        "therefore" or "thus" or "so",
        "answer" or "result" or "conclusion"
    ]
    return sum(1 for i in indicators if i in response.lower()) >= 2
```

### Edge Case Check (+0.2)
```python
def addresses_edges(response):
    patterns = [
        r"edge case",
        r"special case",
        r"what if",
        r"corner case",
        r"boundary",
        r"empty|null|zero|negative"
    ]
    return any(re.search(p, response.lower()) for p in patterns)
```

### Format Check (+0.1)
```python
def format_correct(response):
    has_answer_section = "<answer>" in response or "Answer:" in response
    not_rambling = len(response) < 5000  # Reasonable length
    return has_answer_section and not_rambling
```

## GRPO Advantage Formula

From DeepSeek-R1:

```
Advantage(i) = (score_i - μ) / σ

where:
  μ = mean of all scores in group
  σ = standard deviation of scores

Selection: argmax(Advantage)
```

This ensures selection is based on relative performance, not absolute thresholds.

## Consensus Aggregation

Inspired by mHC's doubly-stochastic mixing:

```python
def compute_consensus(paths):
    answers = [extract_answer(p.response) for p in paths]
    weights = softmax([p.advantage for p in paths])

    # Find most common answer weighted by advantage
    answer_weights = defaultdict(float)
    for ans, w in zip(answers, weights):
        answer_weights[normalize(ans)] += w

    consensus_answer = max(answer_weights, key=answer_weights.get)
    consensus_weight = answer_weights[consensus_answer]

    # Confidence based on weight concentration
    if consensus_weight > 0.75:
        return consensus_answer, "HIGH"
    elif consensus_weight > 0.5:
        return consensus_answer, "MEDIUM"
    else:
        return consensus_answer, "LOW"
```

## Path Diversity Strategy

Based on mHC's multi-stream design:

| Path | Temperature | Strategy | Purpose |
|------|-------------|----------|---------|
| 1 | 0.7 | Conservative | Reliable baseline |
| 2 | 0.8 | Standard | Balanced exploration |
| 3 | 0.9 | Creative | Alternative approaches |
| 4 | 1.0 | Divergent | Contrarian thinking |

Higher temperatures explore more of the solution space but may produce lower-quality individual responses. GRPO selection ensures we get the best from each temperature regime.

## Computational Complexity

- **Path generation**: O(4 * response_length)
- **Scoring**: O(4 * response_length) for regex matching
- **GRPO selection**: O(4) for statistics
- **Total**: Linear in response length, constant in number of paths

The overhead is primarily in generation, which is 4x a single response. For complex reasoning tasks where accuracy matters more than latency, this is a worthwhile tradeoff.
