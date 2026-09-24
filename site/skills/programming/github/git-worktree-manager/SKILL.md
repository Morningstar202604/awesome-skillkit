---
name: git-worktree-manager
description: "Run parallel feature work safely with Git worktrees, using git worktrees, or doing multi-branch parallel development. Standardizes branch isolation, port allocation, environment sync, and cleanup so each worktree behaves like an independent local app. Optimized for multi-agent workflows where each agent or terminal session owns one worktree. Use when running multiple feature branches simultaneously, isolating experimental work, or coordinating multi-agent development across the same repo. Do NOT use for resolving merge conflicts inside a worktree."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: github
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-09"
---

# Git Worktree Manager

Develop in parallel safely with Git worktrees: one isolated work tree per branch, automated port allocation, environment sync, and cleanup. Built for multi-agent workflows where each agent/terminal session owns exactly one worktree.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| `--repo` | Required | Main repo path (default `.`) |
| `--branch` | Required (on create) | New or existing branch name, e.g. `feature/new-auth` |
| `--name` | Required (on create) | Worktree directory name; suggest `wt-<topic>` |
| `--base-branch` | Optional | The base for a new branch, e.g. `main`/`develop` |
| `--stale-days` | Optional | Days alive before cleanup judges it stale (default 14) |
| `--install-deps` | Optional | Detect and install dependencies per the lockfile |
| `--format` | Optional | `text` (human review, default) or `json` (pipelines) |

When inputs are missing, ask for all at once: "Please provide: (1) main repo path (default current directory), (2) branch name, (3) worktree name (suggested `wt-<topic>`), (4) base branch (default `main`). Everything else defaults: don't install deps, output text."

## Pre-flight Checks

```bash
git rev-parse --is-inside-work-tree   # expected true; on failure: not a git repo → STOP
# Self-check: python3 scripts/worktree_manager.py --help and worktree_cleanup.py --help should both exit 0
git rev-parse --verify main >/dev/null 2>&1   # expected: the base branch exists; on failure: confirm --base-branch
```

## Workflow

### Step 1: Create a fully provisioned worktree

```bash
# Single-line usage is shown in Step 2's --input example (runnable as-is); the wrapped layout below is readability only; merge into one line when copying:
# python3 scripts/worktree_manager.py \
#   --repo . \
#   --branch feature/new-auth \
#   --name wt-auth \
#   --base-branch main \
#   --install-deps \
#   --format text
```

Expected: create the worktree directory and switch to the target branch (create it from the base if it doesn't exist), generate a `.worktree-ports.json` port map, copy `.env*`, and the script exits 0. If a worktree already exists at the same path, reuse it directly (idempotent, exit 0).
On failure: the target path already exists → check the path, don't overwrite; dependency install fails → keep the worktree, mark its status, and hand off for manual recovery; `.env` copy fails → warn and list the missing files, then continue.

### Step 2: Pipeline / multi-agent input (JSON mode)

```bash
# Piped usage: cat config.json | python3 scripts/worktree_manager.py --format json
# Or
python3 scripts/worktree_manager.py --input assets/sample-worktree-config.json --dry-run --format json   # bundled sample + read-only rehearsal (validates the config, prints the plan, writes nothing); drop --dry-run to actually create
```

Expected: same as Step 1, but the output is JSON for machine consumption.
On failure: the JSON lacks `branch`/`name` fields → validate the input schema and resend.

### Step 3: Parallel-session conventions

- Main repo: the integration branch (`main`/`develop`) owns the default ports.
- Each worktree: offset ports; the port allocation is written to `.worktree-ports.json` inside that tree.
- Each worktree is owned by exactly one agent; avoid shared branches.

### Step 4: Cleanup with safety checks

```bash
python3 scripts/worktree_cleanup.py --repo . --stale-days 14 --format text
python3 scripts/worktree_cleanup.py --repo . --remove-merged --format text
```

Expected: only removes worktrees that are "merged + clean work tree"; the scan reports no unexpectedly leftover dirty trees.
On failure: uncommitted changes exist → don't remove by default; list the path; a forced removal requires explicit `--force` and user confirmation (see the safety red lines).

## Port Allocation Strategy

Default `base + (index * stride)` with conflict detection: App `3000`, Postgres `5432`, Redis `6379`, stride `10`.
See `references/port-allocation-strategy.md` for the full strategy and edge cases.

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| `--repo` | path | Main repo (default `.`) |
| `--branch` | branch name | New or existing branch |
| `--name` | name | Worktree directory name |
| `--base-branch` | branch name | Base for a new branch |
| `--install-deps` | flag | Install dependencies per the lockfile |
| `--stale-days` | integer | Staleness threshold for cleanup (default 14) |
| `--remove-merged` | flag | Remove only merged worktrees |
| `--force` | flag | Force removal (including dirty trees) — needs user confirmation |
| `--format` | `text`/`json` | Output shape |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `git worktree add` failed (path exists) | The target path is taken | Check the path; don't overwrite |
| Dependency install failed | Lockfile or network issue | Keep the worktree, hand off for manual recovery |
| `.env` copy failed | The source repo lacks the file | Warn, list the missing items, continue |
| Port conflict | Collides with an external service | Adjust `--app-base` / `--db-base` / `--redis-base` and rerun the allocation |
| Cleanup scan found a dirty tree | Uncommitted changes | Don't remove by default; force requires confirmation |

## Delivery Criteria

Definition of success: `git worktree list` shows the expected paths + branches; `.worktree-ports.json` exists with unique ports; `.env` was copied (succeeds if the source has it); dependency install exits 0; the cleanup scan finds no unexpected dirty trees.
Artifact naming: worktree directory `<name>/`, port map `.worktree-ports.json` (inside the worktree).
Save location: a directory sibling to the main repo; the port map stays with the worktree.
Completeness verification: run the three checks above — `git worktree list` / `.worktree-ports.json` / `git status`.

## Safety Red Lines

- **Removal is destructive**: `worktree_cleanup.py` by default only deletes "merged and clean" trees; deleting a dirty/unmerged tree requires explicit `--force` and prior user confirmation — don't execute before confirmation.
- Port maps are written to a file, not memory/terminal sticky notes; multi-agent setups use `wt-<taskId>` naming to avoid committing to the wrong window.
- If cleanup deletes the wrong thing, recovery is from a backup outside `git worktree prune` — so double-check the path before confirming.

## References

- `references/port-allocation-strategy.md` — the full port-allocation strategy and edge cases
- `references/docker-compose-patterns.md` — per-worktree `docker-compose` override templates
- `README.md` — quick start and installation
