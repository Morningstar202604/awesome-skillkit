---
name: changelog-generator
description: "Produce consistent, auditable release notes from Conventional Commits. Separates commit parsing, semantic-bump logic, and changelog rendering for automated releases with editorial control. Use when cutting a release, generating CHANGELOG.md from git history, computing the next semantic version from commits, writing release notes, organizing version changes, automating release notes in CI, or planning a hotfix/rollback. Examples: 'generate the changelog for v1.4.0', 'what version bump do these commits require', 'we need an emergency hotfix process'. Do NOT use for publishing releases (generation only)."
license: Apache-2.0
compatibility: "Pure Python 3 stdlib scripts; requires a local git repo and the `git` CLI on PATH. No API keys, no Docker required."
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: github
  pattern: code-generator
  tier: powerful
  verified-date: "2026-09-09"
---

# Changelog Generator

Produces consistent, auditable release notes from Conventional Commits. It orchestrates three steps — commit parsing, semver inference, and CHANGELOG rendering; it only generates, it does not publish.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| A git repo in the current directory | Required | The scripts call `git` directly to read history |
| Version range | Required | One of: `--from-tag/--to-tag`, or a commit list via `--input <file\|stdin>` |
| `--next-version` | Conditionally required | The target version must be given when rendering a CHANGELOG entry |
| `--format` | Optional | `markdown` (default, for humans) or `json` (machine-readable for CI) |
| `--write` | Optional | Target `CHANGELOG.md` path; otherwise only prints a preview |

When inputs are missing, ask for all at once: "Please provide: (1) git repo path (default current directory), (2) version range: start tag/end tag, or a commit-list file, (3) target version number (e.g. v1.4.0), (4) output format markdown/json (default markdown). I'll use the rest as defaults: don't write a file, render only Added/Changed/Fixed."

## Pre-flight Checks

Probe the environment before running; on any failure → emit remediation guidance and STOP:

```bash
git rev-parse --is-inside-work-tree   # expected output true; on failure: the current dir isn't a git repo → cd to the repo root or STOP
# Self-check: python3 scripts/generate_changelog.py --help should exit 0; on failure: script missing or python3 unavailable
# Self-check: python3 scripts/version_bumper.py --help and python3 scripts/commit_linter.py --help likewise
```

## Workflow

### Step 1: Compute the next semantic version (when the user hasn't set one)

```bash
python3 scripts/version_bumper.py --current-version 1.3.0 --input examples/commits.txt --output-format json   # runs offline: bundled sample (git log --oneline format)
# Real usage (piped input): git log v1.3.0..HEAD --oneline | python3 scripts/version_bumper.py --current-version 1.3.0
```

Expected: output includes `recommended_version` and `bump_type` (`major`/`minor`/`patch`/`none`); with `--include-commands` it appends `git tag` commands.
On failure: the input isn't real `git log --oneline` (missing hex hashes) → re-fetch with `git log v1.3.0..HEAD --oneline`; `--current-version` isn't pure semver → use a compliant version number.

### Step 2: Generate entries from a git range or a commit list

```bash
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag v1.4.0 \
  --next-version v1.4.0 --format markdown
```

Or via stdin/file:

```bash
python3 scripts/generate_changelog.py --input examples/commit-subjects.txt --next-version v1.4.0 --format markdown   # bundled sample (plain subject lines, --pretty=format:'%s' output format)
# Real usage (piped input): git log v1.3.0..v1.4.0 --pretty=format:'%s' | python3 scripts/generate_changelog.py --next-version v1.4.0 --format markdown
```

Expected: stdout emits Keep a Changelog sections (Added/Changed/Fixed…); when there are no valid conventional commits the script early-fails rather than producing a misleading empty note.
On failure: the range is invalid (`--from-tag` doesn't exist) → the error explicitly states the range; commits aren't conventional → prompt to run Step 4 lint first.

### Step 3: Write back to CHANGELOG.md (dry-run by default, needs confirmation)

```bash
# Preview first (default behavior: without --write it only prints)
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag HEAD \
  --next-version v1.4.0 --format markdown
# After confirming it's correct and the user approves, write:
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag HEAD \
  --next-version v1.4.0 --write CHANGELOG.md
```

Expected: after `--write` a new entry is inserted at the top of the file, preserving historical entries (no overwrite).
On failure: the write target is missing → the script creates a safe header skeleton; if historical sections are accidentally overwritten → restore historical entries from `git` (the tool prepends, it doesn't overwrite).

### Step 4: Lint commit format before merge

```bash
python3 scripts/commit_linter.py --from-ref origin/main --to-ref HEAD --strict --format text
# Or file/stdin:
python3 scripts/commit_linter.py --input commits.txt --strict
cat commits.txt | python3 scripts/commit_linter.py --format json
```

Expected: under `--strict`, violations return a non-zero exit code, which CI uses to block the merge; text mode prints the violating lines.
On failure: `origin/main` can't be fetched (no remote/network) → use the local `main..HEAD` instead; violations exist → fix each per the output and rerun.

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| `--from-tag` / `--to-tag` | git tag names | Define the version range; mutually exclusive with `--input` |
| `--input` | file path or stdin | Commit list (`git log --pretty=format:'%s'` or `--oneline`) |
| `--next-version` | semver (e.g. 1.4.0) | The version number rendered into the CHANGELOG |
| `--format` | `markdown` \| `json` | markdown for humans, json for CI |
| `--write` | file path | Prepend in place to the CHANGELOG; omitted = preview |
| `--prerelease` | `alpha`\|`beta`\|`rc` | `version_bumper.py` only: pre-release suffix |
| `--include-commands` | flag | `version_bumper.py` only: emit `git tag` commands |
| `--strict` | flag | `commit_linter.py` only: non-zero exit on any violation |

## Conventional Commit Rules

Supported types: `feat` `fix` `perf` `refactor` `docs` `test` `build` `ci` `chore` `security` `deprecated` `remove`.
Breaking changes: `type(scope)!: summary` or a body containing `BREAKING CHANGE:`.
SemVer mapping: breaking → `major`; non-breaking `feat` → `minor`; everything else → `patch`.

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `recommended_version` is empty | The input isn't a real git log | Re-fetch with `git log vX..HEAD --oneline` |
| early-fail "no valid conventional commits" | No compliant commits in the range | Confirm the range or lint first; don't generate an empty note |
| `--write` overwrote historical sections | Overwrite mode used by mistake | The tool prepends; if already overwritten, restore from `git` |
| `commit_linter` non-zero exit | Violating commits exist | Fix each per the output and rerun |
| `origin/main` can't be fetched | No remote/network | Use the local `main..HEAD` |

## Delivery Criteria

Definition of success: produce a structured CHANGELOG entry, breaking changes include migration actions, security fixes go into a `Security` section, empty sections are omitted, and cross-section duplicates are removed.
Artifact naming: `CHANGELOG.md` (repo root, Keep a Changelog format) or `<name>.json` (CI artifact).
Save location: repo root, committed to version control.
Completeness verification: `--format json` for CI validation; tag only after human review of the draft; use `commit_linter.py --strict` as the merge gate.

## Safety Red Lines

- `--write` is a write operation, dry-run by default (without it, it only previews); confirm with the user before writing `CHANGELOG.md`.
- Generate only, don't publish: this skill doesn't run `git tag` / `git push`; tagging and releasing are done by the user after generation is confirmed.
- The sample `assets/sample_git_log.txt` is only an input-format example, not real repo data.

## References

- `references/changelog-formatting-guide.md` — read when rendering section rules and wording conventions
- `references/ci-integration.md` — read when wiring CI to produce release notes automatically
- `references/monorepo-strategy.md` — read when filtering a changelog by scope in a multi-package repo
- `references/hotfix-procedures.md` — read when a release goes wrong and you need to triage P0–P2 and define a hotfix/rollback process
- `README.md` — installation and quick start
