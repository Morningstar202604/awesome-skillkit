---
name: debug-diagnoser
description: "Parse stack traces and error logs, identify root cause from 10+ known patterns, suggest minimal fix. Outputs structured diagnosis consumable by code-generator. Use when a crash/bug report needs triage before fixing. 当用户要求 排查报错 / 定位崩溃原因 / 看这个 traceback / debug 一下 时使用。 Do NOT use for fixing the code itself (diagnosis and hypothesis ranking only)."
license: Apache-2.0
compatibility: Pure Python regex analysis. No external dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/debug
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Debug Diagnoser

Triage errors: parse stack trace → identify pattern → suggest fix.

## When to Use

- User reports a crash with stack trace
- CI test failed, need to triage before fixing
- Multiple errors in logs, need priority ranking
- Hand off diagnosis to code-generator for automated fix

## Error Pattern Library

| Pattern | Cause | Fix | Severity |
|---------|-------|-----|----------|
| TypeError (None) | Uninitialized variable | Add null check | High |
| KeyError | Missing dict key | Use .get() | Medium |
| ModuleNotFoundError | Missing dep | pip install | Medium |
| IndexError | Out of bounds | Add bounds check | High |
| ValueError (convert) | Type mismatch | Cast int()/float() | Medium |
| ConnectionError | Service down | Check service, retry | High |
| FileNotFoundError | Path wrong | Use absolute path | Medium |
| PermissionError | Access denied | Check user/umask | High |
| MemoryError | OOM | Chunk processing | Critical |
| TimeoutError | Too slow | Increase timeout, optimize | Medium |

## Usage

```bash
python3 diagnoser.py --trace "Traceback... TypeError: NoneType..."
python3 diagnoser.py --file error.log
```

## Output

```json
{
  "status": "diagnosed",
  "issues": [
    {
      "error_type": "TypeError: None is not callable",
      "likely_cause": "Null/undefined value passed where type expected",
      "fix_suggestion": "Add null check or ensure initialization before use",
      "severity": "high"
    }
  ],
  "locations": [{"file": "main.py", "line": 42}],
  "next_skill": "code-generator"
}
```

## Workflow

1. Parse stack trace (extract error type, file, line)
2. Match against 10 known patterns
3. Rank by severity (critical > high > medium)
4. Generate fix suggestion
5. Output: structured diagnosis JSON
6. Hand off to code-generator (if automated fix needed)

## References

- [references/error-patterns.md](references/error-patterns.md) — full pattern library
- [references/debug-checklist.md](references/debug-checklist.md) — manual debug steps

定位根因并修复后，**接着说："诊断已定位根因，继续调用 code-reviewer 复核修复改动，或 code-generator 直接生成修复补丁"——链条自动展开**。
