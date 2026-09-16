---
name: observability-designer
description: "Design production-ready observability strategies combining metrics, logs, and traces. Triggers on "design a dashboard", "too many alerts", "alert fatigue", "golden signals", "grafana dashboard", "reduce alert noise", "monitoring for a new service", "observability strategy", or "alerting review". Ships a Grafana dashboard generator (golden-signal panels per service type and role) and an alert optimizer (noise, duplicates, coverage gaps). Use when adding observability to a new service or refactoring noisy alerting. 当用户要求 设计监控告警 / 可观测性方案 / 仪表盘 / 降低告警噪音 时使用。 Do NOT use for installing or operating observability agents, or for SLO/error-budget design (use slo-architect)."
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

Design production-ready dashboards and alert configurations across the three pillars (metrics, logs, traces), with deterministic generators instead of vibes.

**Lane split:** for SLO/SLI design, error-budget math, and burn-rate alerting thresholds — including scaffolding SLO definitions — route to `slo-architect` (it ships `slo_designer.py`, `error_budget_calculator.py`, and `slo_review.py`). This skill's lane: dashboards (`scripts/dashboard_generator.py`) and alert-noise reduction (`scripts/alert_optimizer.py`).

## When NOT to use

- SLO / error budget design → `slo-architect`
- Installing or operating observability agents (Prometheus/Grafana deployment) → ops/infrastructure skills
- Load testing and capacity planning → `performance-profiler`

## Input checklist

Collect once before running anything. If inputs are missing, ask the user once with: "要设计可观测性，请一次性提供：服务名、服务类型、关键级别、仪表盘受众；若要优化告警，再给告警配置 JSON 路径。"

| Input | Required | Description |
|---|---|---|
| Service name | Yes | e.g. `payments` → `--name` |
| Service type | Yes | one of `api`, `web`, `database`, `queue`, `batch`, `ml` → `--service-type` |
| Criticality | Yes | `critical` / `high` / `medium` / `low` → `--criticality`; drives alert defaults |
| Dashboard audience | Yes | `sre` / `developer` / `executive` / `ops` → `--role` |
| Alert config JSON | For alert work | existing rules with thresholds and routing → `--input` (see `assets/sample_alerts.json` for the expected shape) |
| Service definition JSON | Optional | richer dashboard input → `--input` (examples: `assets/sample_service_api.json`, `assets/sample_service_web.json`) |

## Pre-flight checks

```bash
python3 --version        # Expected: Python ≥ 3.8. Both scripts are stdlib-only.
ls scripts/dashboard_generator.py scripts/alert_optimizer.py
                         # Expected: both files listed.
```

- Python missing/outdated → install Python ≥ 3.8, then STOP.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then STOP.
- Optimizing alerts? Also run `python3 -c "import json;json.load(open('<alerts.json>'))"` — expected: no traceback (valid JSON). Invalid → fix or export a valid config first; the optimizer does not repair malformed JSON.

## Quick start

```bash
# Dashboard spec (Grafana JSON + docs) for a service
python3 scripts/dashboard_generator.py --service-type api --name payments --criticality critical --role sre --format grafana -o dashboard.json --doc-output dashboard.md

# Analyze an existing alert config for noise, duplicates, and coverage gaps
python3 scripts/alert_optimizer.py --input alerts.json --analyze-only --report alert_report.json
# ...then emit the optimized config once the report is reviewed:
python3 scripts/alert_optimizer.py --input alerts.json --output alerts_optimized.json

# SLO definitions/error budgets → use the slo-architect skill (scripts/slo_designer.py there)
```

## Workflows

### Workflow 1: Generate a dashboard for a service

#### Step 1: Collect service facts

- **Action:** gather the Input checklist (name, type, criticality, audience) in one pass.
- **Expected:** four values confirmed by the user; service type is one of the six supported.
- **If it fails:** type does not fit any of the six → pick the closest and say so; do not silently mislabel.

#### Step 2: Generate the specification

- **Action:** `python3 scripts/dashboard_generator.py --service-type <type> --name <svc> --criticality <level> --role <role> --format grafana -o dashboard_<svc>.json --doc-output dashboard_<svc>.md`
- **Expected:** stdout prints `Dashboard specification saved to:` and `Documentation saved to:`; both files exist and the JSON has a `dashboard.title` of `<name> - <ROLE> Dashboard`.
- **If it fails:** argparse error → a required flag is missing, add it and re-run.

#### Step 3: Import and verify panels render

- **Action:** import dashboard_<svc>.json into Grafana; open every golden-signal panel (latency, traffic, errors, saturation) with a live time range.
- **Expected:** every panel renders data — no `No data` on panels whose metric exists in the cluster.
- **If it fails:** `No data` → the metric label in the panel query does not match your exporter's labels; adapt queries to your Prometheus job labels before closing the task.

#### Step 4: Verify with the verification loop

- **Action:** leave the dashboard live for one on-call rotation; collect feedback on missing/unused panels.
- **Expected:** actionable-review passes — panels used, nothing critical missing.
- **If it fails:** recurring gap → regenerate with adjusted `--role`/`--criticality` or hand-add the missing panel; record why.

### Workflow 2: Reduce alert noise

#### Step 1: Baseline the current config

- **Action:** `python3 scripts/alert_optimizer.py --input <alerts.json> --analyze-only --report alert_report.json`
- **Expected:** report file exists with keys `summary`, `noisy_alerts`, `coverage_gaps`, `duplicate_alerts`, `threshold_analysis`, `alert_fatigue_assessment`, `overall_recommendations`; stdout prints an `ALERT CONFIGURATION ANALYSIS SUMMARY` block.
- **If it fails:** JSON parse error → the input config is malformed; fix it first (see pre-flight).

#### Step 2: Review the report before changing anything

- **Action:** read `noisy_alerts`, `duplicate_alerts`, and `coverage_gaps`; decide per finding: fix threshold, merge, delete, or keep with reason.
- **Expected:** every finding has a decision — none silently accepted or ignored.
- **If it fails:** a finding is wrong (e.g. "noisy" alert is actually a paging-critical one) → keep it and document why; optimizer heuristics are advisory, not law.

#### Step 3: Emit the optimized config

- **Action:** `python3 scripts/alert_optimizer.py --input <alerts.json> --output alerts_optimized.json`
- **Expected:** output file exists; diff against input shows only the decisions from Step 2.
- **If it fails:** diff shows unreviewed changes → do not deploy; re-run `--analyze-only`, reconcile decisions, re-emit.

#### Step 4: Deploy and measure

- **Action:** deploy alerts_optimized.json through your normal alerting pipeline; track the report's noise metrics for one on-call rotation.
- **Expected:** actionable-alert ratio improved vs the baseline report.
- **If it fails:** ratio flat or worse → re-run `--analyze-only` against the live config and iterate; noise sources are usually routing, not thresholds.

## Parameter quick reference

### dashboard_generator.py

| Parameter | Values | Notes |
|---|---|---|
| `--service-type` | `api` / `web` / `database` / `queue` / `batch` / `ml` | selects panel set |
| `--name` | service name | dashboard title |
| `--criticality` | `critical` / `high` / `medium` / `low` | drives panel emphasis |
| `--role` | `sre` / `developer` / `executive` / `ops` | role-based view |
| `--format` | `grafana` / `json` | `grafana` = importable JSON |
| `-o` / `--output` | path | dashboard spec file |
| `--doc-output` | path | human-readable dashboard doc |
| `--input`, `-i` | service definition JSON | optional; richer spec (samples in `assets/`) |
| `--summary-only` | flag | print summary without writing files |

### alert_optimizer.py

| Parameter | Values | Notes |
|---|---|---|
| `--input`, `-i` | alert config JSON | required |
| `--output`, `-o` | path | optimized config; omit with `--analyze-only` |
| `--report`, `-r` | path | analysis report file |
| `--format` | `json` / `html` | report format |
| `--analyze-only` | flag | analysis without emitting a new config |

## Design rules (digest)

The full pattern catalogs live in `references/` — the rules below are the ones to apply while running the workflows:

- **Golden signals per service:** latency (P50/P95/P99), traffic, errors (4xx/5xx + silent failures), saturation (queues, connection pools). RED for request-driven services, USE for resources.
- **Dashboard information architecture:** overview → service → component → instance drill-down; 80% operational / 20% exploratory panels; ≤7±2 panels per screen; role-based views (SRE ≠ executive).
- **Alert rules:** every alert names a response action; severity = critical (service down, SLO burn) / warning (approaching threshold) / info (deploys, capacity). No action → no alert.
- **Alert fatigue controls:** high precision over high recall; hysteresis (different fire/resolve thresholds); suppression during known outages; group related alerts.
- **Cost controls:** tiered metric retention, log/trace sampling, cardinality management — flag high-cardinality labels before they explode storage.
- **Runbook per critical alert:** what it means, user impact, investigation steps, resolution, escalation. An alert without a runbook is a finding, not a feature.

## Failure handling

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `dashboard_generator.py` argparse error | required flag missing (`--service-type`/`--name`/`--criticality`/`--role`) | add the flag named in the error and re-run |
| Panel `No data` after Grafana import | metric labels differ from your exporter | adapt panel queries to your Prometheus job labels |
| `alert_optimizer.py` JSON decode error | input config malformed | validate with `python3 -m json.tool <file>`; fix source config |
| Report flags a paging-critical alert as noisy | heuristic is advisory | keep the alert; document the exception in the review |
| Optimized diff contains unreviewed changes | Step 2 skipped or rushed | do not deploy; reconcile decisions, re-emit |
| Actionable-alert ratio unchanged after deploy | noise source is routing/ownership, not thresholds | re-run `--analyze-only` on live config; fix routing first |
| `python: command not found` | no interpreter | install Python ≥ 3.8; both scripts are stdlib-only |

## References

Read the reference only when the corresponding situation applies:

- `references/alert_design_patterns.md` — read when designing or reviewing alert rules (severity models, fatigue controls, composite alerts) or when the optimizer report needs interpretation.
- `references/dashboard_best_practices.md` — read when the generated dashboard needs hand-tuning (panel selection, drill-down paths, visualization choices).

## Asset templates

- `assets/sample_alerts.json` — example alert config in the exact shape `alert_optimizer.py --input` expects; also a template for your own export
- `assets/sample_service_api.json` / `assets/sample_service_web.json` — service definition JSONs for `dashboard_generator.py --input`

## Deliverables and success criteria

A run of this skill is done when:

- Dashboard: `dashboard_<service>.json` (Grafana-importable) and `dashboard_<service>.md` (doc) saved next to the service's repo or the team's dashboard directory; every panel verified rendering live data in Grafana.
- Alert work: `alert_report.json` (baseline), `alerts_optimized.json` (reviewed diff only), saved alongside the original config in version control; deployed and measured for one on-call rotation.
- Verification of completeness: re-running the same generator command reproduces the dashboard files byte-for-byte (deterministic output); the alert report's `summary` counts match the deployed config's rule count.
- Ongoing: actionable-alert ratio trending up across rotations; every critical alert has a runbook.
