---
name: debug-diagnoser
description: "Parse stack traces and error logs, identify root cause from 10+ known patterns, and suggest a minimal fix. Outputs a structured diagnosis consumable by code-generator. Use when triaging a crash/bug report before fixing — troubleshooting an error, locating a crash cause, looking at a traceback, or debugging an issue. Do NOT use for fixing the code itself (diagnosis and hypothesis ranking only)."
license: Apache-2.0
compatibility: Pure Python standard library (re). No external dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/debug
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Debug Diagnoser

Triage errors: parse the stack → match known error patterns → rank by severity → give a minimal fix suggestion, producing a structured diagnosis JSON for code-generator to consume. It only diagnoses and ranks; it doesn't change code.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| `--trace` | One of two | Stack/error text (quoted, may contain escaped newlines) |
| `--file` | One of two | Path to an error log file; at least one of `--trace` / `--file` must be provided |
| `--output` | Optional | Where the diagnosis is written; defaults to stdout |

When inputs are missing, ask for all at once: "Please provide: (1) the full traceback text or the path to an error log file; (2) (optional) whether to write the result to a file. Everything else I run on defaults: the diagnosis prints to the terminal."

## Pre-flight Checks

Probe the environment before running; on any failure → give the fix and STOP:

```bash
python3 --version   # expected 3.8+; on failure: install python3
python3 scripts/diagnoser.py --help >/dev/null 2>&1   # expected exit code 0; on failure: script missing → check the skill directory
test -f <the --file path the user gave>   # expected exit code 0; on failure: the log file doesn't exist → use --trace to paste the text directly
```

## Workflow

### Step 1: Collect the complete error

Expected: get a full traceback containing the exception type and `File "...", line N` (a truncated stack loses matching clues).
On failure: the user only gave a screenshot/description of the error → ask them to paste the text log; if the log file is too large → first run `grep -n "Traceback\|Error" error.log` to locate the key section.

### Step 2: Run the diagnosis

```bash
python3 scripts/diagnoser.py --trace "Traceback ... TypeError: 'NoneType' object is not callable"
python3 scripts/diagnoser.py --file error.log --output diagnosis.json
```

Expected: stdout (or the `--output` file) emits JSON with `status` = `diagnosed`, containing `issues[]` (each with `error_type`/`likely_cause`/`fix_suggestion`/`severity`), `locations[]` (`file:line`, up to 5), `top_severity`, `recommendation`, and `next_skill`.

### Step 3: Verify the match

Expected: `top_severity` is consistent with the error content (critical > high > medium); when there's no match, `status` is `no_match` and `recommendation` flags manual investigation.
On failure: `no_match` but the error is obvious → check the full pattern library in [references/error-patterns.md](references/error-patterns.md), triage manually by pattern, and note in the report that it's a manual diagnosis.

### Step 4: Rank by recommendation and hand off

Expected: when there are multiple issues, report them to the user one by one from highest to lowest `severity`; when an automatic fix is needed, hand off to code-generator per `next_skill`.

## Error Pattern Quick Reference

| Pattern (matched by script regex, case-insensitive) | Severity | Fix direction |
|------|--------|----------|
| `TypeError` + None/undefined/not callable/argument | high | Null checks, initialization |
| `KeyError` | medium | `.get(key, default)`, check the data structure |
| `ModuleNotFoundError` / `ImportError` | medium | Install the dependency or fix the import path |
| `IndexError` / list index out of range | high | Boundary checks, safe indexing |
| `ValueError` / could not convert / invalid literal | medium | Type conversion, input validation |
| `ConnectionError` / ECONNREFUSED | high | Check service liveness, host/port, retry backoff |
| `FileNotFoundError` | medium | Absolute path, confirm the file exists |
| `PermissionError` | high | Check user permissions and umask |
| `MemoryError` | critical | Process in chunks |
| `TimeoutError` | medium | Increase the timeout, optimize the slow path |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `status: no_match` | The error isn't among the 10 known patterns | Read references/error-patterns.md for manual triage; tell the user it's a manual conclusion |
| `locations` is empty | The stack has no `xxx.py:NN`-style file:line | Expected; locate it manually from the traceback text and supplement it |
| Passing `--trace` reports a shell error | The text contains unescaped quotes/special characters | Save it as a log file and pass it with `--file` |
| `--file` reads no content | Wrong path or no read permission | Check the path and permissions; or use `--trace` |
| The output wasn't written to a file | `--output` wasn't passed | Expected (prints stdout); add `--output diagnosis.json` if you want a file |

## Delivery Criteria

Definition of success: output JSON `status=diagnosed`, every issue has the cause/fix/severity triad, and multiple issues are ranked by severity.
Artifact naming: diagnosis report `diagnosis.json` (when written via `--output`).
Save location: same directory as the error log or the working-directory root.
Completeness verification: `issues` corresponds one-to-one with the exception types in the log; each location's file:line can be opened and checked in the source; on `no_match`, the user has been explicitly informed.

## Safety Red Lines

- This skill only diagnoses; it doesn't modify any code file; the fix is done by code-generator or by hand.
- `--output` overwrites a same-named file; if the target path already exists, confirm with the user first.
- The diagnosis is a ranking of hypotheses rather than a confirmed root cause; when delivering to the user, it must be annotated as "verify in order".

## References

- [references/error-patterns.md](references/error-patterns.md) — read on `no_match` or when you need the full pattern library and variants
- [references/debug-checklist.md](references/debug-checklist.md) — read when manual reproduction/triage is still needed after the script's triage

After locating the root cause and fixing it, **then say: "The diagnosis has located the root cause; next, call code-reviewer to review the fix, or code-generator to generate the fix patch directly" — the chain unfolds automatically**.
