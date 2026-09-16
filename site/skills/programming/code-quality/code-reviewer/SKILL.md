---
name: code-reviewer
description: >-
  Automated static-analysis engine for code changes and files in TypeScript,
  JavaScript, Python, Go, Swift, Kotlin, C#, .NET, Java, C, C++, Rust, Ruby,
  PHP, and Dart/Flutter. Detects complexity, risk, hardcoded secrets, SQL
  injection, and SOLID violations; generates review reports. Use when the user
  asks to 审查代码 / code review / 帮我看这段代码 / 检查这段代码的风险 / 静态分析
  / 生成审查报告. Do NOT use for fixing the issues it reports (static analysis
  only) — that is code-generator's job.
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash. The three bundled scripts require Python 3.10+.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: code-reviewer
  tier: powerful
  verified-date: "2026-09-09"
---

# Code Reviewer

Deterministic, multi-language static analysis: run the bundled scripts to flag
risk, then load the language/rule references to produce a review. This file is
the dispatch table — keep it short; the heavy rules live in `rules/` and
`languages/`.

---

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Target path | Yes | A repo root, a directory, or a single file (absolute or relative). |
| Scope | No | `diff` (default: current branch vs `main`) or `files` (whole-tree scan). |
| Language | No | Auto-detected from extension table below; override with `--language`. |
| Output format | No | `markdown` (default) or `json`. |
| Pre-computed analyses | No | Paths to `pr_results.json` / `quality_results.json` to skip re-running. |

If any required input is missing, ask once with this template:

> 请提供：① 目标路径（仓库/目录/文件）；② 范围（diff 还是整树扫描）。
> 其余我采用默认值：scope=diff（当前分支 vs main）、format=markdown、语言自动识别。

## Pre-flight Self-check

Run before any analysis. Any failure → print the fix and STOP.

```bash
# 1. Scripts present?
test -f scripts/pr_analyzer.py && test -f scripts/code_quality_checker.py \
  && test -f scripts/review_report_generator.py && echo "scripts-ok" \
  || { echo "ERROR: scripts/ missing — bundle is incomplete"; exit 1; }

# 2. Python available?
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# 3. Universal rule file present?
test -f rules/universal.md || { echo "ERROR: rules/universal.md missing"; exit 1; }

# 4. Target exists?
test -e "$TARGET" || { echo "ERROR: target $TARGET not found"; exit 1; }
```

## How the skill is organized

```text
code-reviewer/
  SKILL.md                        ← you are here (tools + dispatch table)
  rules/
    universal.md                  ← security, async, resources, exceptions, perf — all languages
  languages/
    python.md  typescript.md  go.md  swift.md  kotlin.md  csharp.md
    java.md  c.md  cpp.md  rust.md  ruby.md  php.md  dart.md
  scripts/
    pr_analyzer.py  code_quality_checker.py  review_report_generator.py
  assets/  expected_outputs/       ← regression fixtures (C#, Java, C)
```

### Loading order (always exactly 2 extra files)

1. `SKILL.md` — tools and thresholds (this file).
2. `rules/universal.md` — always, for every language.
3. One `languages/<ext>.md` — chosen from the table below.

| Extension(s) | Load |
|---|---|
| `.py` | `languages/python.md` |
| `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` | `languages/typescript.md` |
| `.go` | `languages/go.md` |
| `.swift` | `languages/swift.md` |
| `.kt`, `.kts` | `languages/kotlin.md` |
| `.cs`, `.csx`, `.razor`, `.cshtml` | `languages/csharp.md` |
| `.java` | `languages/java.md` |
| `.c`, `.h` | `languages/c.md` |
| `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh`, `.hxx` | `languages/cpp.md` |
| `.rs` | `languages/rust.md` |
| `.rb`, `.rake`, `.gemspec`, `.ru` | `languages/ruby.md` |
| `.php`, `.phtml` | `languages/php.md` |
| `.dart` | `languages/dart.md` |

## Workflow

### Step 1: Analyze the change / tree

```bash
# Diff mode — current branch against main
python scripts/pr_analyzer.py /path/to/repo
# Specific branches
python scripts/pr_analyzer.py . --base main --head feature-branch
# JSON for downstream tools
python scripts/pr_analyzer.py /path/to/repo --json
```

Expected: script prints complexity score (1–10), risk category
(critical/high/medium/low), file prioritization, and commit-message
validation; `--json` writes the same to stdout.
If failed: non-zero exit or traceback → confirm path exists and Python ≥3.10;
re-run with `--json` to isolate parse errors.

### Step 2: Run the quality checker

```bash
# Whole directory, auto language
python scripts/code_quality_checker.py /path/to/code
# Specific language (one of: python, typescript, javascript, go, swift,
#   kotlin, csharp, java, c, cpp, rust, ruby, php, dart)
python scripts/code_quality_checker.py . --language java
# JSON output
python scripts/code_quality_checker.py /path/to/code --json
```

Universal thresholds used by the checker:

| Issue | Threshold |
|-------|-----------|
| Long function | >50 lines |
| Large file | >500 lines |
| God class | >20 methods |
| Too many params | >5 |
| Deep nesting | >4 levels |
| High complexity | >10 branches |

Expected: per-file findings scored against the thresholds above.
If failed: if a language is unknown the script falls back to Python patterns and
logs a warning — re-run with explicit `--language`.

### Step 3: Generate the review report

```bash
# Markdown report for the current repo
python scripts/review_report_generator.py /path/to/repo
# Explicit format + output file
python scripts/review_report_generator.py . --format markdown --output review.md
# Reuse pre-computed analyses
python scripts/review_report_generator.py . \
  --pr-analysis pr_results.json --quality-analysis quality_results.json
```

Verdict mapping (apply after both analyses are in):

| Score | Verdict |
|-------|---------|
| 90+ with no high issues | Approve |
| 75+ with ≤2 high issues | Approve with suggestions |
| 50–74 | Request changes |
| <50 or any critical issue | Block |

Expected: a report containing the verdict, per-file findings, and the
recommendation. If failed: ensure the two upstream scripts produced output
before invoking the generator, or pass `--pr-analysis` / `--quality-analysis`
explicitly.

## Parameter Cheat-sheet

| Script | Key flag | Values |
|--------|----------|--------|
| `pr_analyzer.py` | `--base` / `--head` | branch names (default base `main`) |
| `pr_analyzer.py` | `--json` | emit JSON to stdout |
| `code_quality_checker.py` | `--language` | one of the 14 supported languages |
| `review_report_generator.py` | `--format` | `markdown` \| `json` |
| `review_report_generator.py` | `--output` | file path |

## Failure Handling

| Symptom | Cause | Action |
|---------|-------|--------|
| `ModuleNotFoundError` / `SyntaxError` | Python <3.10 or missing script | upgrade Python; re-verify scripts present |
| Empty report / no findings | wrong target path | re-run with an existing file or directory |
| Wrong-language signals | extension not in table | pass `--language` explicitly |
| Analyzer flags unknown language as Python | fallback mode | add the language to `LANGUAGE_EXTENSIONS` in `code_quality_checker.py` |

## Delivery Standard

Success = a review report exists with a verdict from the mapping above and
per-file findings cross-checked against `rules/universal.md` + the matching
`languages/*.md`.

- Save location: `review.md` in the repo root (or caller-specified `--output`).
- Verify completeness: report must list (a) verdict, (b) each flagged file with
  rule id, (c) whether any `critical`/`high` issue is present.
- Do NOT modify the user's code — this skill analyzes only.

## References

- `rules/universal.md` — read for every review: security, async, resource,
  exception, and performance rules that apply to all languages.
- `languages/<ext>.md` — read the one matching the target extension for
  language-specific detections and idioms (see loading table above).
- `assets/` + `expected_outputs/` — regression fixtures (C#, Java, C); use to
  confirm the analyzer's behavior has not drifted:

```bash
python scripts/code_quality_checker.py assets/sample_java_smells.java --json \
  | diff - expected_outputs/sample_java_smells_quality.json
```

---

## Extending to a new language

1. Create `languages/<name>.md` from any existing language file. It must contain
   these sections: PR Analyzer Signals, Code Quality Checks, Security, Async,
   Resource Management, Exception Handling, Performance, Idioms.
2. Add the extension row to the dispatch table above.
3. (Optional, to make the deterministic checker score it) add the extension to
   `LANGUAGE_EXTENSIONS` and the function/class/method regexes in
   `scripts/code_quality_checker.py`, add a `check_<name>_specific_smells(...)`
   detector, and commit a `<name>_smells.<ext>` + `_clean` fixture under
   `assets/` with its expected `--json` under `expected_outputs/`.
