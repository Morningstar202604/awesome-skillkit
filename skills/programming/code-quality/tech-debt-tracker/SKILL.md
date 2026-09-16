---
name: tech-debt-tracker
description: "Scan codebases for technical debt, score severity, track trends, and generate prioritized remediation plans. Use when users mention tech debt, code quality, refactoring priority, debt scoring, cleanup sprints, or code health assessment. Also use for legacy code modernization planning and maintenance cost estimation. 当用户要求 梳理技术债 / 债项分级 / 还债计划 时使用。 Do NOT use for performing the refactors it tracks."
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

Scan a codebase for technical debt signals, prioritize the backlog with a cost-of-delay framework, and track trends across dated snapshots. This skill tracks and plans debt work — it does not perform the refactors.

Pipeline: `debt_scanner.py` → `debt_prioritizer.py` → `debt_dashboard.py`. The scanner's JSON output feeds the prioritizer directly; dated inventory snapshots feed the dashboard.

## 输入清单

| Input | Required | Description |
|-------|----------|-------------|
| Codebase directory | Required | Path passed to the scanner; must exist and be readable |
| Prioritization framework | Optional | `cost_of_delay` (default), `wsjf`, or `rice` |
| `--team-size` | Optional | Headcount for sprint allocation (prioritizer default: 5) |
| `--sprint-capacity` | Optional | Sprint capacity in hours (prioritizer default: 80) |
| Snapshot history | Optional | Dated inventory JSONs (`debt_YYYY-MM-DD.json`) for trend tracking |

Collect missing inputs in one shot: "Please provide: ① the codebase directory to scan ② framework choice (cost_of_delay/wsjf/rice, default cost_of_delay) ③ team size and sprint capacity for sprint allocation ④ any prior snapshot files for trend analysis. Everything else I'll default."

## 前置自检

Probe before running; on any failure, give the fix and STOP:

```bash
python3 --version   # expect 3.8+; fail: install python3
python3 scripts/debt_scanner.py --help >/dev/null 2>&1       # expect exit 0; fail: script missing → check skill dir
python3 scripts/debt_prioritizer.py --help >/dev/null 2>&1
python3 scripts/debt_dashboard.py --help >/dev/null 2>&1
test -d <codebase-directory>   # expect exit 0; fail: wrong path → ask user for the correct directory
```

## 工作流

### 步骤 1: Scan the codebase

```bash
python3 scripts/debt_scanner.py /path/to/codebase --format json --output debt_inventory.json
```

Expected: `debt_inventory.json` is created and contains `scan_metadata`, `summary`, `debt_items[]`, `file_statistics`, and `recommendations`. Report the `summary` counts to the user. Dry run: point the scanner at `assets/sample_codebase`.
If it fails: empty `debt_items[]` → the directory may have no scannable source files; confirm the path contains code, not just docs/config.

### 步骤 2: Prioritize the backlog

```bash
python3 scripts/debt_prioritizer.py debt_inventory.json --framework wsjf --team-size 6 --sprint-capacity 20 --format json --output debt_priorities.json
```

Expected: `debt_priorities.json` contains `prioritized_backlog` (work top-down), `sprint_allocation` (paste into sprint planning), and `insights`.
If it fails: invalid inventory JSON → re-run step 1; unknown framework name → use one of `cost_of_delay`, `wsjf`, `rice`.

### 步骤 3: Track trends over time

Keep dated snapshots (`debt_YYYY-MM-DD.json`), then:

```bash
python3 scripts/debt_dashboard.py --input-dir snapshots/ --period monthly --format both --output debt_dashboard
```

Or pass files explicitly:

```bash
python3 scripts/debt_dashboard.py assets/historical_debt_2024-01-15.json assets/historical_debt_2024-02-01.json --period monthly
```

Expected: dashboard reports trend direction plus an executive-ready summary. Use it to verify a cleanup sprint actually reduced debt.
If it fails: `--input-dir` has no inventory files → pass files explicitly as positional arguments; snapshot naming inconsistent → filenames must contain a parseable date.

### 步骤 4: Verification loop

After a remediation sprint: re-run 步骤 1 to produce a new snapshot, re-run 步骤 3 including it, and assert the targeted categories' counts dropped. A cleanup that doesn't move the dashboard is rework, not debt paydown.

## Debt Severity Scoring

| Factor | Weight | Description |
|--------|--------|-------------|
| Impact | 30% | How many users/services are affected? |
| Risk | 25% | Security, data loss, or compliance risk? |
| Effort | 20% | How much work to fix? (inverse) |
| Frequency | 15% | How often does this cause issues? |
| Age | 10% | How long has this debt existed? |

Framework guidance (WSJF, RICE, classification taxonomy) lives in the references below — read them when the user challenges a score or asks for a specific framework's rationale.

## 失败处置表

| Symptom / Error | Cause | Fix |
|-----------------|-------|-----|
| Scanner output has empty `debt_items[]` | Directory has no scannable source files | Confirm the path contains code; ask user for the right directory |
| Prioritizer rejects the inventory file | Inventory JSON malformed or truncated | Re-run 步骤 1 and check `scan_metadata` for scan errors |
| Dashboard prints no trend | Only one snapshot available | Collect at least two dated snapshots, or generate one now and compare later |
| `--output` file not written | `--format both` writes prefixed files (e.g. `.json`/`.txt`) | Check for both extensions next to the output base name |
| Scores look wrong to the user | Default weights don't match team context | Adjust via scanner `--config` JSON, or override priorities manually in the report |

## 交付标准

Success definition: inventory (counts + itemized debt), a priority-ordered backlog with sprint allocation, and — when history exists — a trend summary.
Artifact naming: `debt_inventory.json`, `debt_priorities.json`, `debt_dashboard.json` / `debt_dashboard.txt`, snapshots `debt_YYYY-MM-DD.json`.
Save location: working directory root, or a `snapshots/` folder when building history.
Verify completeness: inventory `summary` totals match `len(debt_items)`; every backlog entry traces back to an inventory item ID; trend output covers every snapshot file passed in.

## 安全红线

- Read-only on the target codebase: the scanner never modifies scanned files. Do not "fix" debt items as part of this skill.
- Snapshot files are audit history — never overwrite an existing dated snapshot; create a new one instead.
- Scope: analysis and planning only. Executing refactors, dependency upgrades, or cleanups belongs to other skills and requires explicit user confirmation.

## 参考

- `references/debt-frameworks.md` — read when choosing or explaining a scoring framework
- `references/debt-classification-taxonomy.md` — read when users dispute how an item is categorized
- `references/prioritization-framework.md` — read when producing or defending the backlog order
- `references/stakeholder-communication-templates.md` — read when writing executive summaries or sprint-plan communications
