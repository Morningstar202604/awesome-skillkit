---
name: agent-eval-harness
description: >-
  Quantify "is the AI agent behaving correctly" into a 0-100 score with a
  verifiable rubric, so you stop relying on gut feel when you ship an agent. Use
  when the user asks to evaluate an agent / score an agent / eval test cases /
  LLM behavior verification / regression test for agent behavior / prove the
  agent didn't degrade / agent evaluation harness. Do NOT use for writing the
  agent itself (use skill-author / webapp-e2e-harness) or for pure unit tests of
  code (use tdd-guide / api-test-suite-builder).
license: Apache-2.0
compatibility: Pure Python offline script (writes files only, no network requests); mode B LLM-as-judge only produces copyable review prompts, actual model calls are wired by user (credentials via env).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: programming
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Agent Eval Harness (Agent Behavior Quantitative Scoring)

Turn "is the AI agent actually correct" from **mysticism** into **regressable,
gateable** numbers: 5 auto-judgeable dimensions (structure / grounding / no
hallucination / consistency / safety) weighted into a 0-100 score, each case
giving `pass / fail / warn` verdict + failed dimension details.

Core judgment: **an agent's biggest cost isn't "can it write"—it's "after a
prompt change it silently degrades and nobody notices."** A scorer that runs,
reuses, and exits non-zero on CI is worth far more than a one-time "looks good."
This skill hard-codes scoring rubrics into a script so "behavior correctness"
is repeatably verifiable—exactly the **fixed-step** work a skill should do,
rather than letting the model improvise.

> Red lines: script is **offline** (writes files only, no network requests);
> default dry-run, `--write` saves; credentials only via env (mode B only, and
> only produces prompt text, doesn't call the model for the user).

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Cases file (JSONL) | yes | Each line `{"prompt","response","expects":{...}}`, see below |
| `--index` | no | Which line to score (0-based), default 0 |
| `--mode` | no | `offline` (default) / `judge` (LLM-as-judge prompt) |
| `--weights-json` | no | Override dimension weights (JSON object) |
| `--forbidden-json` | no | Append forbidden strings (JSON array) |

`expects` fields (all optional, defaults to lenient scoring):

| Field | Purpose | Effect on hit |
|---|---|---|
| `must_contain_table` | Requires markdown table | format bonus |
| `must_contain_code` | Requires code block ``` | format bonus |
| `min_length` | Minimum output character count | format bonus |
| `must_include` | Required keyword list | missing → grounding risk |
| `evidence` | Anti-hallucination: strings response should hit | grounding dimension |
| `forbidden` | Dangerous/forbidden strings (e.g. `rm -rf /`) | no_hallu/safety deduction |
| `conflict_pairs` | Mutually exclusive pairs `[["a","b"]]`, co-occurrence = contradiction | consistency zeroed |

## Pre-flight Checks

1. Is the cases file JSONL, each line valid JSON? (`python3 -c "import
   json,sys;[json.loads(l) for l in open('c.jsonl') if l.strip()]"` doesn't
   error = OK.)
2. Want anti-hallucination verification? Fill `evidence`; want "dangerous
   operations" deduction? Fill `forbidden`. Not filled = lenient mode.
3. Mode B doesn't need a local LLM, only generates prompt text; actual model
   calls are wired by user.

## Workflow

```bash
# 1. Dry run: offline rule scoring on case 0 (prints JSON to stdout)
python3 scripts/eval_harness.py --input assets/sample-cases.jsonl --index 0   # bundled sample (offline rule scoring); replace with your cases.jsonl

# 2. Real report output (can hang CI gate)
# python3 scripts/eval_harness.py --input cases.jsonl --index 3 \
#   --weights-json config/weights.example.json --out reports/case3.json --write

# 3. LLM-as-judge: generates a copyable review prompt (doesn't call the model for you)
# python3 scripts/eval_harness.py --input cases.jsonl --index 3 --mode judge --out judge.md
```

How to fill `expects`, per-dimension scoring logic, CI gate integration:
see [references/eval-rubric.md](references/eval-rubric.md).

## Delivery Criteria

- Each case outputs `score(0-100)` + `verdict(pass/fail/warn)` + `failed_dimensions`
- If `evidence` filled, grounding dimension **must** participate in scoring (anti-hallucination truly active)
- If `forbidden` hits, no_hallu/safety deducted, `failed_dimensions` non-empty
- Mode B produced prompt has no plaintext credentials (all via env placeholders)
- Script offline: dry-run calls no model, makes no network request

## Failure Handling Table

| Symptom | Root Cause | Action |
|---|---|---|
| All `pass` but you feel agent is hallucinating | `evidence` not filled (lenient mode) | Fill `evidence` so grounding truly bites |
| `consistency` mysteriously zero | `conflict_pairs` both values appear in response | Check response, confirm real contradiction; change case |
| Dangerous operation not deducted | `forbidden` string doesn't match actual wording | Add actual dangerous string to `--forbidden-json` or case `forbidden` |
| Scores drift (same case twice, different) | Script itself is deterministic; drift comes from **cases or weights** changing | Fix `--weights-json`, version the cases file |
| Want LLM scoring but errors 401/404 | Credentials/endpoint not set | Mode B doesn't call model for you; user sets env per pseudocode in `judge.md` |

## References

- Scoring logic / dimension semantics / CI gate: [references/eval-rubric.md](references/eval-rubric.md)
- Weights example: `config/weights.example.json`

## Pipeline Position

- Upstream: `webapp-e2e-harness` (e2e-produced response as scored object) / any agent output
- Downstream: `ci-cd-pipeline-builder` (wire `verdict=fail` into CI as behavior regression gate)
- Parallel: `skill-tester` (tests whether a single skill runs); this skill tests whether agent behavior is "correct"—different granularity
