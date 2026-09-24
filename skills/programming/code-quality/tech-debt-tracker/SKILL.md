---
name: tech-debt-tracker
description: "Scan codebases for technical debt, score severity, track trends, and generate prioritized remediation plans. Use when users mention tech debt, code quality, refactoring priority, debt scoring, cleanup sprints, or code health assessment. Also use for legacy code modernization planning and maintenance cost estimation, sorting out technical debt, grading debt items, or a debt-repayment plan. Do NOT use for performing the refactors it tracks."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Tech Debt Tracker

Scans a codebase for technical-debt signals, ranks the backlog using a cost-of-delay framework, and tracks trends from dated snapshots. This skill only tracks and plans debt-repayment work — it does not perform refactors.

Pipeline: `debt_scanner.py` → `debt_prioritizer.py` → `debt_dashboard.py`. The scanner's JSON output feeds the prioritizer directly; dated inventory snapshots feed the dashboard.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Codebase directory | Required | The path passed to the scanner; must exist and be readable |
| Prioritization framework | Optional | `cost_of_delay` (default), `wsjf`, or `rice` |
| `--team-size` | Optional | Number of people for sprint allocation (prioritizer default: 5) |
| `--sprint-capacity` | Optional | Sprint capacity in hours (prioritizer default: 80) |
| Snapshot history | Optional | Dated inventory JSON (`debt_YYYY-MM-DD.json`) for trend tracking |

When inputs are missing, ask all at once: "Please provide: (1) the codebase directory to scan; (2) framework choice (cost_of_delay/wsjf/rice, default cost_of_delay); (3) team size and capacity for sprint allocation; (4) any historical snapshot files for trend analysis. Everything else uses defaults."

## Pre-flight Checks

Probe each item; if any fails → give the fix and STOP:

```bash
python3 --version   # expected 3.8+; failure: install python3
# Self-check: python3 scripts/debt_scanner.py --help / debt_prioritizer.py / debt_dashboard.py all expected to exit 0
test -d <codebase-directory>   # expected exit code 0; failure: wrong path → ask the user for the correct directory
```

## Workflow

### Step 1: Scan the codebase

```bash
python3 scripts/debt_scanner.py examples/sample-codebase --format json --output snapshots/2026-09.json   # bundled sample codebase; swap in your real codebase root
```

Expected: produce `debt_inventory.json` containing `scan_metadata`, `summary`, `debt_items[]`, `file_statistics`, and `recommendations`. Report the `summary` counts to the user. To practice, point the scanner at `assets/sample_codebase`. On failure: `debt_items[]` is empty → the directory may have no scannable source files; confirm the path contains code, not just docs/config.

### Step 2: Prioritize the backlog

```bash
python3 scripts/debt_prioritizer.py examples/snapshots/2026-09.json --framework wsjf --team-size 6 --sprint-capacity 20 --format json --output snapshots/priorities.json   # input is the Step 1 scan artifact (bundled sample included)
```

Expected: `debt_priorities.json` contains `prioritized_backlog` (execute top-down), `sprint_allocation` (paste directly into the sprint plan), and `insights`. On failure: the inventory JSON is invalid → rerun Step 1; unknown framework name → choose from `cost_of_delay`, `wsjf`, `rice`.

### Step 3: Track the time trend

Keep dated snapshots (`debt_YYYY-MM-DD.json`), then:

```bash
python3 scripts/debt_dashboard.py --input-dir examples/snapshots/ --period monthly --format both --output debt_dashboard   # bundled snapshot directory (two-period comparison); swap in your real snapshots/
```

Or pass files explicitly:

```bash
python3 scripts/debt_dashboard.py assets/historical_debt_2024-01-15.json assets/historical_debt_2024-02-01.json --period monthly
```

Expected: the dashboard outputs the trend direction and a summary ready to present. Use it to verify whether a cleanup sprint actually reduced debt. On failure: no inventory files in `--input-dir` → pass files explicitly as positional args; inconsistent snapshot naming → filenames must contain a parseable date.

### Step 4: Verification loop

After a debt-repayment sprint: rerun Step 1 to produce a new snapshot, fold it into a rerun of Step 3, and assert that the target categories' counts actually dropped. Cleanup that doesn't move the dashboard is rework, not debt repayment.

## Debt Severity Scoring

| Factor | Weight | Description |
|------|------|------|
| Impact | 30% | How many users/services are affected? |
| Risk | 25% | Is there security, data-loss, or compliance risk? |
| Effort | 20% | How big is the fix? (inversely scored) |
| Frequency | 15% | How often does it cause problems? |
| Age | 10% | How long has this debt existed? |

Framework guidance (WSJF, RICE, the classification taxonomy) is in the references below — read when the user questions a score or asks about the basis for a particular framework.

## Failure Handling Table

| Symptom / error | Cause | Fix |
|-------------|------|------|
| Scanner outputs empty `debt_items[]` | No scannable source files in the directory | Confirm the path contains code; ask the user for the correct directory |
| Prioritizer rejects the inventory file | Inventory JSON corrupt or truncated | Rerun Step 1; check scan errors in `scan_metadata` |
| Dashboard outputs no trend | Only one snapshot | Collect at least two dated snapshots, or produce one now for later comparison |
| `--output` file not generated | `--format both` writes suffixed files (e.g. `.json`/`.txt`) | Look for the two extensions next to the output basename |
| The user thinks the score is wrong | Default weights don't fit the team | Adjust with the scanner's `--config` JSON, or manually override priorities in the report |

## Delivery Criteria

- Definition of success: the inventory (counts + per-item debt), a prioritized backlog with sprint allocation, and — if history exists — a trend summary.
- Artifact naming: `debt_inventory.json`, `debt_priorities.json`, `debt_dashboard.json` / `debt_dashboard.txt`, snapshots `debt_YYYY-MM-DD.json`.
- Save location: working-directory root; use a `snapshots/` directory when building history.
- Completeness check: the inventory `summary` total matches `len(debt_items)`; every backlog item traces back to an inventory item ID; the trend output covers all passed snapshot files.

## Security Red Lines

- Read-only against the target codebase: the scanner never modifies scanned files. Do not use this skill to "conveniently" fix debt items along the way.
- Snapshot files are audit history — never overwrite an existing dated snapshot; create a new one if you want to save.
- Scope: analysis and planning only. Performing refactors, dependency upgrades, or cleanup belongs to other skills and requires explicit user confirmation.

## References

- `references/debt-frameworks.md` — read when choosing or explaining the scoring framework
- `references/debt-classification-taxonomy.md` — read when the user disputes an item's classification
- `references/prioritization-framework.md` — read when producing or defending the backlog order
- `references/stakeholder-communication-templates.md` — read when writing executive summaries or sprint-plan communications
