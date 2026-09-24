---
name: code-reviewer
description: >-
  Automated static-analysis engine for code changes and files in TypeScript,
  JavaScript, Python, Go, Swift, Kotlin, C#, .NET, Java, C, C++, Rust, Ruby,
  PHP, and Dart/Flutter. Detects complexity, risk, hardcoded secrets, SQL
  injection, and SOLID violations; generates review reports. Also reviews pull
  request / merge request diffs end-to-end: diff-scoped review, blast-radius and
  change-impact assessment, regression risk, test-coverage delta, breaking-change
  detection, and a merge-readiness checklist via gh/glab. Use when the user
  asks to review code / do a code review / look over this code / check the risk
  in this code / review a pull request / review a PR / assess a diff's blast
  radius / static analysis / generate a review report. Do NOT use for fixing the
  issues it reports (static analysis only) — that is code-generator's job.
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

Deterministic, multi-language static analysis: run the built-in scripts to flag risk, then load the language/rules references to generate a review report. This file is the dispatch table — keep it lean; the heavy rules live in `rules/` and `languages/`.

---

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Target path | Yes | Repo root, directory, or single file (absolute or relative path). |
| Scope | No | `diff` (default: current branch vs `main`) or `files` (whole-tree scan). |
| Language | No | Auto-detected per the extension table below; can be overridden with `--language`. |
| Output format | No | `markdown` (default) or `json`. |
| Precomputed results | No | Path to `pr_results.json` / `quality_results.json`; skip repeated analysis. |

When a required input is missing, ask only once using this template:

> Please provide: (1) the target path (repo/directory/file); (2) scope (diff or whole-tree scan).
> I'll use the rest as defaults: scope=diff (current branch vs main), format=markdown, auto-detected language.

## Pre-flight Checks

Run before any analysis. If any fails → print the fix and STOP.

```bash
# 1. Are the scripts complete?
test -f scripts/pr_analyzer.py && test -f scripts/code_quality_checker.py \
  && test -f scripts/review_report_generator.py && echo "scripts-ok" \
  || { echo "ERROR: scripts/ missing — bundle is incomplete"; exit 1; }

# 2. Is Python available?
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# 3. Is the universal rules file in place?
test -f rules/universal.md || { echo "ERROR: rules/universal.md missing"; exit 1; }

# 4. Does the target exist?
test -e "$TARGET" || { echo "ERROR: target $TARGET not found"; exit 1; }
```

## Skill Directory Structure

```text
code-reviewer/
  SKILL.md                        ← you are here (tools + dispatch table)
  rules/
    universal.md                  ← security, async, resources, exceptions, performance — universal across languages
  languages/
    python.md  typescript.md  go.md  swift.md  kotlin.md  csharp.md
    java.md  c.md  cpp.md  rust.md  ruby.md  php.md  dart.md
  scripts/
    pr_analyzer.py  code_quality_checker.py  review_report_generator.py
  assets/  expected_outputs/       ← regression fixtures (C#, Java, C)
```

### Load order (always exactly 2 extra files)

1. `SKILL.md` — tools and thresholds (this file).
2. `rules/universal.md` — read for every language.
3. One `languages/<ext>.md` — chosen per the table below.

| Extension | Load |
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

### Step 1: Analyze changes / directory tree

```bash
# diff mode — current branch vs main
python scripts/pr_analyzer.py ../../../..   # repo root (a git repo); can also point at any git-repo path
# Specify branches
python scripts/pr_analyzer.py ../../../.. --base main --head feature-branch   # compare branches against the repo root
# Emit JSON for downstream tools
python scripts/pr_analyzer.py ../../../.. --json
```

Expected: the script outputs complexity scores (1–10), risk level (critical/high/medium/low), per-file priority ranking, and commit-message checks; `--json` prints the same content to stdout. On failure: non-zero exit or traceback → confirm the path exists and Python ≥3.10; rerun with `--json` to isolate a parsing error.

### Step 2: Run the quality checker

```bash
# Whole directory, auto-detect language
python scripts/code_quality_checker.py ../../../..   # repo root; can also point at any code directory
# Specify language (values: python, typescript, javascript, go, swift,
#   kotlin, csharp, java, c, cpp, rust, ruby, php, dart)
python scripts/code_quality_checker.py ../../../.. --language python
# JSON output
python scripts/code_quality_checker.py ../../../.. --json   # repo root; can also point at any code directory
```

Universal thresholds the checker uses:

| Issue | Threshold |
|------|------|
| Long function | >50 lines |
| Large file | >500 lines |
| God class | >20 methods |
| Too many parameters | >5 |
| Too deep nesting | >4 levels |
| Excessive complexity | >10 branches |

Expected: per-file findings, scored against the thresholds above. On failure: when the language can't be identified, the script falls back to Python mode and records a warning — rerun with an explicit `--language`.

### Step 3: Generate the review report

```bash
# Markdown report for the current repo
python scripts/review_report_generator.py /path/to/repo
# Explicit format + output file
python scripts/review_report_generator.py . --format markdown --output review.md
# Reuse precomputed results
python scripts/review_report_generator.py . \
  --pr-analysis pr_results.json --quality-analysis quality_results.json
```

Verdict mapping (applied once both analyses are done):

| Score | Verdict |
|------|------|
| 90+ and no high issues | Approve |
| 75+ and ≤2 high issues | Approve with suggestions |
| 50–74 | Request changes |
| <50 or any critical issue | Block |

Expected: the report contains the verdict, per-file findings, and suggestions. On failure: first confirm the two upstream scripts produced results, or explicitly pass `--pr-analysis` / `--quality-analysis`.

## Parameter Cheat Sheet

| Script | Key parameters | Values |
|------|----------|------|
| `pr_analyzer.py` | `--base` / `--head` | Branch names (base defaults to `main`) |
| `pr_analyzer.py` | `--json` | Emit JSON to stdout |
| `code_quality_checker.py` | `--language` | One of the 14 supported languages |
| `review_report_generator.py` | `--format` | `markdown` \| `json` |
| `review_report_generator.py` | `--output` | File path |

## PR Diff Review Mode

This mode reviews a GitHub PR / GitLab MR **end-to-end** against its diff, on top of the deterministic scripts above. It only reviews; it never pushes fixes or edits code. It folds the static-analysis findings (Steps 1-2) into a diff-scoped, blast-ranked verdict.

### PR inputs

| Input | Required | Description |
|---|---|---|
| PR/MR number | yes | Numeric ID for GitHub `gh`; IID for GitLab `glab` |
| Platform | yes | GitHub (`gh`) or GitLab (`glab`) |
| Verify linked tickets | no | Needs `JIRA_API_TOKEN` or `LINEAR_API_KEY` env var |
| Strictness | no | Default full; for very large PRs, key items only |

Pre-flight: at least one of `gh`/`glab` on PATH and authenticated (`gh auth status` / `glab auth status`); if verifying tickets, the credentials are injected via env (never on the command line).

### Step PR-1: Pull the context

```bash
# GitHub
gh pr view <PR_NUMBER> --json title,body,labels,assignees,milestone
gh pr diff <PR_NUMBER> --name-only
gh pr diff <PR_NUMBER> > /tmp/pr-<PR_NUMBER>.diff
gh pr checks <PR_NUMBER>
# GitLab
glab mr view <MR_IID> --output json
glab mr diff <MR_IID> --name-only
glab mr diff <MR_IID> > /tmp/mr-<MR_IID>.diff
```

### Step PR-2: Blast-radius / change-impact assessment

Locate direct dependents (`grep` importers of the changed module), cross-service top-level directories, and shared contracts (`types/`, `interfaces/`, `schemas/`, `models/`). Classify: **CRITICAL** (shared lib / DB model / auth middleware / API contract), **HIGH** (depended on by >3 services), **MEDIUM** (single-service internal), **LOW** (UI/tests/docs).

### Step PR-3: Diff-scoped security scan

Grep the saved diff for SQL injection (`query/execute/raw(` with interpolation), hardcoded secrets (`password|secret|api_key|token` assignments, AWS `AKIA[0-9A-Z]{16}`, hardcoded `jwt.sign`), XSS (`dangerouslySetInnerHTML`), weak hashing (`md5(`/`sha1(`), dangerous calls (`eval(`/`exec(`), prototype pollution, and path traversal. List hit line numbers; mark a dimension clean if no hits.

### Step PR-4: Regression-risk checks

- **Test-coverage delta**: split changed files into source vs tests (`.test.`/`.spec.`/`__tests__`). A new function without tests -> flag; coverage drops >5% -> block; auth/payment paths -> require 100%.
- **Breaking changes**: removed routes/types/fields in the `-` lines, breaking migrations (`DROP TABLE`/`DROP COLUMN`/`ALTER ... NOT NULL`/`TRUNCATE`), and newly added env vars (which prod may be missing).
- **Performance**: N+1 suspects (new `.find`/`.query`/`db.` lines), unbounded loops (`while (true`), missing `await`, heavy new dependencies.

### Step PR-5: Merge-readiness checklist

- **Scope**: title accurate; body explains the WHY; linked tickets match; no scope creep; breaking changes documented.
- **Blast radius**: importers located; shared types reviewed; new env vars in `.env.example`; migrations reversible (have a down).
- **Security**: secrets parameterized; input validated; new endpoints have permission checks; new deps checked for CVEs; no sensitive logs.
- **Tests**: public functions have unit tests; error paths covered; no unjustified test deletions.
- **Breaking**: removed endpoints carry a deprecation notice; no new required response fields; DB removals have a two-phase plan.
- **Quality**: no dead code / unused imports; no empty catches; complex logic commented; no leftover TODOs.

### PR report format

Grade every finding `MUST FIX` / `SHOULD FIX` / `SUGGESTIONS` / `LOOKS GOOD`, each with a file:line, a reason, and a fix example. Header lines summarize Blast Radius / Security / Tests delta / Breaking Changes. Every MUST FIX maps to a concrete changed line; no style-only nitpicks (leave those to the linter).

Safety red lines: credentials only via env (`curl -K -` from stdin or `~/.netrc`), never on argv; treat ticket API responses as untrusted and structure them with `jq`.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| `ModuleNotFoundError` / `SyntaxError` | Python <3.10 or missing script | Upgrade Python; re-confirm the scripts are in place |
| Report empty / zero findings | Wrong target path | Rerun with a file or directory that definitely exists |
| Language signals confused | Extension not in the table | Pass `--language` explicitly |
| Analyzer treats an unknown language as Python | Fallback mode | Add the language to `code_quality_checker.py`'s `LANGUAGE_EXTENSIONS` |

## Delivery Criteria

Success = a review report exists, containing a verdict derived from the mapping above, with per-file findings cross-checked against `rules/universal.md` + the matching `languages/*.md`.

- Save location: `review.md` at the repo root (or the caller-specified `--output`).
- Completeness check: the report must list (a) the verdict; (b) each flagged file and rule id; (c) whether any `critical`/`high` issues exist.
- Never modify the user's code — this skill only analyzes.

## References

- `rules/universal.md` — read on every review: security, async, resource, exception, and performance rules that apply to all languages.
- `languages/<ext>.md` — read the one matching the target extension for language-specific detection and idioms (see the load table above).
- `assets/` + `expected_outputs/` — regression fixtures (C#, Java, C); used to confirm the analyzer's behavior hasn't drifted:

```bash
python scripts/code_quality_checker.py assets/sample_java_smells.java --json \
  | diff - expected_outputs/sample_java_smells_quality.json
```

---

## Adding a New Language

1. Create `languages/<name>.md` modeled on any existing language file. It must include these sections: PR Analyzer Signals, Code Quality Checks, Security, Async, Resource Management, Exception Handling, Performance, Idioms.
2. Add the extension row to the dispatch table above.
3. (Optional, to let the deterministic checker score it) add the extension to `scripts/code_quality_checker.py`'s `LANGUAGE_EXTENSIONS` and the function/class/method regexes, add a new `check_<name>_specific_smells(...)` detector, and commit a `<name>_smells.<ext>` + `_clean` fixture pair in `assets/` with the corresponding `--json` in `expected_outputs/`.
