---
name: observability-designer
description: >-
  Design production-ready observability strategies combining metrics, logs, and traces. Triggers on "design a dashboard", "too many alerts", "alert fatigue", "golden signals", "grafana dashboard", "reduce alert noise", "monitoring for a new service", "observability strategy", or "alerting review". Ships a Grafana dashboard generator (golden-signal panels per service type and role) and an alert optimizer (noise, duplicates, coverage gaps). Use when adding observability to a new service, designing monitoring and alerting, building an observability plan, building dashboards, or refactoring noisy alerting. Do NOT use for installing or operating observability agents, or for SLO/error-budget design (use slo-architect).
license: Apache-2.0
compatibility: Stdlib-only Python scripts. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: infrastructure
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Observability Designer

Designs production-grade dashboards and alerting configs across the three pillars (metrics, logs, traces), replacing gut-feel choices with deterministic generators.

**Lane division:** SLO/SLI design, error-budget math, burn-rate alert thresholds — including generating SLO-definition scaffolding — go to `slo-architect` (which has `slo_designer.py`, `error_budget_calculator.py`, `slo_review.py`). This skill's lane: dashboards (`scripts/dashboard_generator.py`) and alert noise reduction (`scripts/alert_optimizer.py`).

## When Not to Use

- SLO / error-budget design → `slo-architect`
- Installing or operating observability agents (Prometheus/Grafana deployment) → an ops/infrastructure skill
- Load testing and capacity planning → `performance-profiler`

## Input Checklist

Collect everything before running anything. When inputs are missing, ask the user once with this line: "To design observability, please provide all at once: service name, service type, criticality level, dashboard audience; if optimizing alerts, also give the alert-config JSON path."

| Input | Required | Description |
|---|---|---|
| Service name | Yes | e.g. `payments` → `--name` |
| Service type | Yes | One of `api` / `web` / `database` / `queue` / `batch` / `ml` → `--service-type` |
| Criticality level | Yes | `critical` / `high` / `medium` / `low` → `--criticality`; determines alert defaults |
| Dashboard audience | Yes | `sre` / `developer` / `executive` / `ops` → `--role` |
| Alert config JSON | Needed for the alert workflow | Existing rules with thresholds and routing → `--input` (expected shape in `assets/sample_alerts.json`) |
| Service definition JSON | Optional | Richer dashboard input → `--input` (examples: `assets/sample_service_api.json`, `assets/sample_service_web.json`) |

## Pre-flight Checks

```bash
python3 --version        # Expected: Python ≥ 3.8. Both scripts depend only on the standard library.
ls scripts/dashboard_generator.py scripts/alert_optimizer.py
                         # Expected: both files listed.
```

- Python missing or too old → install Python ≥ 3.8, then stop.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then stop.
- Optimizing alerts? Also run `python3 -c "import json;json.load(open('<alerts.json>'))"` — expected: no traceback (JSON valid). Invalid → fix or export a valid config first; the optimizer doesn't repair broken JSON.

## Quick Start

```bash
# Generate a dashboard spec for a service (Grafana JSON + docs)
python3 scripts/dashboard_generator.py --service-type api --name payments --criticality critical --role sre --format grafana -o dashboard.json --doc-output dashboard.md

# Analyze an existing alert config for noise, duplicates, and coverage gaps
python3 scripts/alert_optimizer.py --input alerts.json --analyze-only --report alert_report.json
# ...after reviewing the report, emit the optimized config:
python3 scripts/alert_optimizer.py --input alerts.json --output alerts_optimized.json

# SLO definitions / error budgets → use the slo-architect skill (its scripts/slo_designer.py)
```

## Workflow

### Workflow 1: Generate a dashboard for a service

#### Step 1: Collect service facts

- **Action:** collect the input checklist (name, type, criticality, audience) all at once.
- **Expected:** all four values confirmed by the user; the service type is one of the six supported types.
- **On failure:** the type matches none → pick the closest and say so explicitly; don't silently mislabel.

#### Step 2: Generate the spec

- **Action:** `python3 scripts/dashboard_generator.py --service-type <type> --name <svc> --criticality <level> --role <role> --format grafana -o dashboard_<svc>.json --doc-output dashboard_<svc>.md`
- **Expected:** stdout prints `Dashboard specification saved to:` and `Documentation saved to:`; both files exist, and the JSON's `dashboard.title` is `<name> - <ROLE> Dashboard`.
- **On failure:** an argparse error → a required flag is missing; add it and rerun.

#### Step 3: Import and verify panel rendering

- **Action:** import dashboard_<svc>.json into Grafana; open each golden-signal panel (latency, traffic, errors, saturation) with a live time range.
- **Expected:** every panel renders data — panels for metrics that really exist in the cluster don't show `No data`.
- **On failure:** `No data` → the metric label in the panel query doesn't match your exporter's label; before wrapping up, adapt the query to your Prometheus job label.

#### Step 4: Confirm with the validation loop

- **Action:** let the dashboard run through a full on-call rotation; collect feedback on missing/idle panels.
- **Expected:** actionable-review passes — panels get used, nothing critical is missing.
- **On failure:** gaps recur → regenerate with adjusted `--role`/`--criticality`, or hand-add panels; record the reason.

### Workflow 2: Reduce alert noise

#### Step 1: Baseline the existing config

- **Action:** `python3 scripts/alert_optimizer.py --input <alerts.json> --analyze-only --report alert_report.json`
- **Expected:** the report file exists, containing `summary`, `noisy_alerts`, `coverage_gaps`, `duplicate_alerts`, `threshold_analysis`, `alert_fatigue_assessment`, `overall_recommendations` keys; stdout prints the `ALERT CONFIGURATION ANALYSIS SUMMARY` block.
- **On failure:** a JSON parse error → the input config is corrupt; fix it first (see pre-flight).

#### Step 2: Review the report before changing anything

- **Action:** read `noisy_alerts`, `duplicate_alerts`, `coverage_gaps`; for each finding decide: tune threshold, merge, delete, or keep with a written reason.
- **Expected:** every finding has a decision — no blind acceptance by default, and no silent ignoring.
- **On failure:** a finding is misjudged (e.g. something flagged "noisy" is actually a paging-critical alert) → keep it and record why; the optimizer's heuristics are suggestions, not law.

#### Step 3: Emit the optimized config

- **Action:** `python3 scripts/alert_optimizer.py --input <alerts.json> --output alerts_optimized.json`
- **Expected:** the output file exists; the diff against the input contains only the Step 2 decisions.
- **On failure:** the diff contains unreviewed changes → don't deploy; rerun `--analyze-only`, align on decisions, and re-emit.

#### Step 4: Deploy and measure

- **Action:** deploy alerts_optimized.json through the normal alerting pipeline; track the report's noise metrics for one on-call rotation.
- **Expected:** the actionable-alert ratio improves versus the baseline report.
- **On failure:** the ratio is flat or worse → rerun `--analyze-only` on the live config and iterate; noise usually lives in routing, not thresholds.

## Parameter Cheat Sheet

### dashboard_generator.py

| Parameter | Values | Description |
|---|---|---|
| `--service-type` | `api` / `web` / `database` / `queue` / `batch` / `ml` | Determines the panel set |
| `--name` | service name | Dashboard title |
| `--criticality` | `critical` / `high` / `medium` / `low` | Determines panel emphasis |
| `--role` | `sre` / `developer` / `executive` / `ops` | Per-role view |
| `--format` | `grafana` / `json` | `grafana` = importable JSON |
| `-o` / `--output` | path | Dashboard spec file |
| `--doc-output` | path | Human-readable dashboard doc |
| `--input`, `-i` | service-definition JSON | Optional; richer spec (samples in `assets/`) |
| `--summary-only` | flag | Print only the summary, don't write files |

### alert_optimizer.py

| Parameter | Values | Description |
|---|---|---|
| `--input`, `-i` | alert-config JSON | Required |
| `--output`, `-o` | path | Optimized config; omitted with `--analyze-only` |
| `--report`, `-r` | path | Analysis report file |
| `--format` | `json` / `html` | Report format |
| `--analyze-only` | flag | Analyze only; don't emit a new config |

## Design Rules (summary)

The full pattern catalog is in `references/` — these are the rules to apply while running the workflows:

- **Golden signals by service type:** latency (P50/P95/P99), traffic, errors (4xx/5xx + silent failures), saturation (queues, connection pools). Use RED for request-driven services, USE for resources.
- **Dashboard information architecture:** overview → service → component → instance drill-down; 80% ops-oriented / 20% exploration-oriented panels; ≤7±2 panels per screen; views by role (SRE ≠ executive).
- **Alerting rules:** every alert states its response action; severity = critical (service down, SLO burning) / warning (approaching threshold) / info (releases, capacity). No action → no alert.
- **Alert-fatigue control:** prefer high precision over high recall; add hysteresis (different fire/resolve thresholds); suppress during known incidents; group correlated alerts.
- **Cost control:** tiered metric retention, log/trace sampling, cardinality management — flag high-cardinality labels before they blow up storage.
- **Every critical alert has a runbook:** meaning, user impact, troubleshooting steps, recovery method, escalation path. An alert without a runbook is a finding, not a feature.

## Failure Handling Table

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `dashboard_generator.py` argparse error | Missing required flag (`--service-type`/`--name`/`--criticality`/`--role`) | Add the flag per the error and rerun |
| Panel `No data` after Grafana import | Metric label doesn't match your exporter | Adapt the panel query to your Prometheus job label |
| `alert_optimizer.py` JSON decode error | Input config corrupt | Validate with `python3 -m json.tool <file>`; fix the source config |
| The report flags a paging-critical alert as noisy | Heuristic is advisory | Keep the alert; record the exception in review |
| The optimized diff contains unreviewed changes | Step 2 was skipped or rushed | Don't deploy; align on decisions and re-emit |
| No change in actionable-alert ratio after deploy | The noise source is routing/ownership, not thresholds | Rerun `--analyze-only` on the live config; fix routing first |
| `python: command not found` | No interpreter | Install Python ≥ 3.8; both scripts use only the standard library |

## References

Read only when the corresponding situation arises:

- `references/alert_design_patterns.md` — when designing or reviewing alert rules (severity models, fatigue control, composite alerts), or when interpreting the optimizer report.
- `references/dashboard_best_practices.md` — when hand-tuning a generated dashboard (panel selection, drill-down paths, visualization choices).

## Asset Templates

- `assets/sample_alerts.json` — an alert-config example exactly matching the shape `alert_optimizer.py --input` expects; also usable as a template for your own exports
- `assets/sample_service_api.json` / `assets/sample_service_web.json` — service-definition JSON for `dashboard_generator.py --input`

## Delivery Criteria

This skill counts as done only when:

- Dashboard: `dashboard_<service>.json` (Grafana-importable) and `dashboard_<service>.md` (docs) are saved beside the service repo or in the team's dashboard directory; every panel has been verified rendering live data in Grafana.
- Alert workflow: `alert_report.json` (baseline) and `alerts_optimized.json` (reviewed diff only) are committed to version control alongside the original config; deployed and measured for one on-call rotation.
- Completeness verification: rerunning the generator command with the same parameters reproduces the dashboard files byte-for-byte (deterministic output); the alert report's `summary` counts match the rule count in the deployed config.
- Ongoing requirement: the actionable-alert ratio keeps rising across rotations; every critical alert has a runbook.
