---
name: slo-architect
description: >-
  Use when defining, reviewing, or operating SLOs/SLIs/error budgets, setting an SLO, designing SLIs and error budgets, or choosing availability targets. Triggers on "define an SLO", "what should our SLO be", "error budget", "burn rate", "SLI", "service level objective", "Google SRE workbook", "multi-window burn-rate alert", or any reliability-target question. Ships SLO designer, error-budget calculator with multi-window burn-rate thresholds, and SLO reviewer that catches the common bugs (target too aggressive, window too short, conflicting SLOs, no SLI definition). 4 references on SLO principles + SLI design + error budget math + composition with feature-flags-architect/chaos-engineering/kubernetes-operator. NOT a generic observability skill — specifically the SLO discipline. Do NOT use for provisioning monitoring infrastructure.
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: incident
  pattern: architecture
  tier: powerful
  verified-date: "2026-09-09"
---

# SLO Architect

Define SLOs that mean something. Most real-world "SLOs" are numbers nobody believes — every endpoint says 99.9%, there's no SLI definition, no error budget, and no one knows what to do when the budget burns through. This skill executes the discipline of the Google SRE Workbook: pick the right SLI, set a target users actually care about, compute the error budget, wire up multi-window burn-rate alerts, and write the policy for what happens when the budget is exhausted.

## When to Use

- Defining a new SLO for a service or feature
- Reviewing an existing SLO for common mistakes
- Choosing the right SLI (event-based vs window-based vs request-based)
- Computing error budgets and burn-rate alert thresholds
- Linking SLOs to existing controls — feature-flag kill switches, chaos blast radius, operator capability levels

## When Not to Use

- Generic observability strategy (metrics + logs + traces) → use `observability-designer`
- Legally binding customer SLAs → that's contract drafting, not engineering
- Performance load testing (a capacity problem, not a reliability problem) → use `performance-profiler`
- An in-progress incident response → use `incident-response`

## Input Checklist

Collect everything before running any tool. When inputs are missing, ask the user once with this line: "To generate an SLO, please provide all at once: service name, SLI type, target value, window in days, owner, and the error-budget policy doc path (also give the existing SLO-doc directory for review if you have one)."

| Input | Required | Description |
|---|---|---|
| Service name | Yes | e.g. `checkout-svc` → `--service` |
| SLI type | Yes | One of `request-success-rate` / `request-latency` / `availability-time` / `data-freshness` / `correctness` → `--sli-type` |
| Target value | Yes | e.g. `99.9` (percent) → `--target`; derive it from 30 days of historical SLI data, don't guess |
| Window in days | No | Default 28 (= 4 calendar weeks) → `--window-days` |
| Owner | Required for a live SLO | The accountable team or person → `--owner`; otherwise renders a `<must define>` placeholder |
| Error-budget policy doc | Required for a live SLO | Path to the written policy → `--policy-doc`; otherwise renders a `<must define>` placeholder |
| SLO-doc directory | Review only | Directory of existing SLO definitions (markdown/JSON) → `--slo-doc` |

## Pre-flight Checks

Run at the repo root (or use the relative-path form below from this skill's directory). Stop at the first failure and fix it — don't improvise.

```bash
python3 --version        # Expected: Python ≥ 3.8. All 3 tools depend only on the standard library.
ls scripts/slo_designer.py scripts/error_budget_calculator.py scripts/slo_review.py
                         # Expected: all 3 files listed.
```

- Python missing or too old → install Python ≥ 3.8, then stop (don't run the tools with an unverified interpreter version).
- Script files missing → wrong directory; `cd` to this skill's directory, then stop and re-check.
- Reviewing existing SLOs? Also run `ls <slo-doc-dir>` — expected: at least one `.md`/`.json` SLO doc. Empty → point `--slo-doc` at a real directory, or use `--sample` first to see the tools' output shape.

## Quick Start

```bash
# 1. Design an SLO (single line; --owner and --policy-doc are required constraints, missing → exit code 1)
python scripts/slo_designer.py --service checkout-svc --sli-type request-success-rate --target 99.9 --window-days 30 --owner payments-team --policy-doc docs/slo-policy.md

# 2. Compute the error budget + multi-window burn-rate alerts
python scripts/error_budget_calculator.py --target 99.9 --window-days 30

# 3. Review an existing SLO definition for common mistakes
python scripts/slo_review.py --slo-doc assets/slos/   # bundled compliant sample (target/window/numerator/denominator/error-budget policy — all five elements present); swap in docs/slos/ for your real project
```

## The Three Python Tools

All depend only on the standard library.

### `slo_designer.py`

Generates a structured SLO definition with required fields. Missing `--service`/`--sli-type`/`--target` → an argparse error, exit code 2. Missing `--owner`/`--policy-doc` → the output carries `<must define>` placeholders and a `WARNING: missing required fields` line; the SLO isn't live until the placeholders are filled.

```bash
# Single-line usage (the wrapped layout below is readability only; merge into one line when copying):
# python scripts/slo_designer.py \
#   --service checkout-svc \
#   --sli-type request-success-rate \
#   --target 99.9 \
#   --window-days 30 \
#   --owner team-checkout
```

**Supported SLI types:**

- `request-success-rate` — `(total_requests - bad_requests) / total_requests`
- `request-latency` — `count(requests < threshold) / total_requests`
- `availability-time` — `(window - downtime) / window`
- `data-freshness` — `count(data_age < threshold) / total_data_points`
- `correctness` — `count(correct_outputs) / total_outputs`

Default output is markdown; required fields are either filled in or marked `<must define>`. JSON output (`--format json`) is consumed by `slo_review.py`.

### `error_budget_calculator.py`

Given a target availability + window, it computes:

- The allowed downtime within the window
- Multi-window burn-rate thresholds per the Google SRE Workbook (Chapter 5):
  - **Fast burn** — page if 2% of the monthly budget is consumed within 1 hour
  - **Slow burn** — page if 5% is consumed within 6 hours
  - **Ticket burn** — open a ticket if 10% is consumed within 3 days
- Recommended alert rules (PromQL-shaped output)

```bash
python scripts/error_budget_calculator.py --target 99.9 --window-days 30
python scripts/error_budget_calculator.py --target 99.95 --window-days 7 --format json
```

### `slo_review.py`

Audits a directory of SLO definitions (markdown or JSON) for common mistakes. Exit code 0 = clean; exit code 1 = findings (usable as a merge gate).

```bash
python scripts/slo_review.py --slo-doc assets/slos/   # bundled sample SLO-doc directory; swap in docs/slos/ for your real project
```

**Checks:**

- `target_too_high`: target ≥ 99.99% (sustainable only with enormous engineering investment)
- `target_too_low`: target ≤ 99.0% (usually a wrong SLI; users will notice)
- `window_too_short`: window < 7 days (statistical noise dominates)
- `window_too_long`: window > 90 days (feedback is too slow)
- `no_sli_definition`: the SLI section is missing or vague ("everything OK")
- `no_error_budget_policy`: no written action for when the budget burns through
- `cpu_as_sli`: using CPU/memory as a proxy for user experience (wrong signal)

## Parameter Cheat Sheet

| Parameter | Values | Description |
|---|---|---|
| `--sli-type` | `request-success-rate` / `request-latency` / `availability-time` / `data-freshness` / `correctness` | Designer only |
| `--window-days` | integer, default 28 | Designer + calculator; review flags <7 or >90 as findings |
| `--target` | float percent, e.g. `99.9` | Designer + calculator |
| `--format` | `markdown`/`json` (designer), `text`/`json` (calculator, review) | The designer's JSON output feeds `slo_review.py` |
| `--owner`, `--policy-doc`, `--user-journey`, `--sli-numerator`, `--sli-denominator`, `--sli-labels`, `--review-cadence` | free text | Designer; missing owner/policy → `<must define>` |
| `--slo-doc` | file or directory path | Review only; `--sample` audits the built-in example |

## SLI Selection Quick Reference

| User-experience question | SLI type | Measurement |
|---|---|---|
| "Did the request succeed?" | request-success-rate | `2xx / total` |
| "Is the response fast enough?" | request-latency | `count(p99 < threshold) / total` |
| "Is the service up?" | availability-time | `(window - downtime) / window` |
| "Is the data fresh?" | data-freshness | `count(data_age < threshold) / total` |
| "Is the answer correct?" | correctness | `count(correct) / total` |

See `references/sli_design.md` for examples and anti-patterns.

## Error-Budget Math (basics)

Take a 99.9% SLO over a 30-day window (corresponding to `error_budget_calculator.py --target 99.9 --window-days 30`):

- Allowed downtime: `0.1% × 30 × 24 × 60 = 43.2 minutes`
- Fast burn: burn 2% of the budget in 1 hour → burn-rate multiple `0.02 / (1/720) = 14.4`
- Slow burn: burn 5% in 6 hours → multiple `0.05 / (6/720) = 6.0`
- Ticket burn: burn 10% in 3 days → multiple `0.10 / (72/720) = 1.0`

`error_budget_calculator.py` computes this for you and emits paste-ready alert rules.

## Collaboration With the Rest of the Composition

This skill explicitly composes with three others:

| Skill | How they compose |
|---|---|
| `feature-flags-architect` | Gradual-rollout abort conditions reference the SLO burn-rate thresholds |
| `chaos-engineering` | The blast-radius calculator already takes the monthly error budget as input — define it here |
| `kubernetes-operator` | Operator capability L4 (Deep Insights) requires an SLO + Prometheus rules |

The output of `error_budget_calculator.py` matches the shape the chaos-engineering skill's `blast_radius_calculator.py` expects on stdin.

## Workflows

### Workflow 1: Define a new SLO

#### Step 1: Collect inputs and lock the user journey

- **Action:** determine the user journey to protect (e.g. "checkout completion"); collect the input checklist all at once.
- **Expected:** a written journey statement, plus service name, SLI type, owner, and policy-doc path.
- **On failure:** the user can't name a journey → don't fabricate; ask which user-facing flow, when it breaks, hurts revenue most.

#### Step 2: Choose and define the SLI

- **Action:** pick the SLI type per the quick reference; define numerator/denominator with concrete labels (or pass `--sli-numerator`/`--sli-denominator`/`--sli-labels`).
- **Expected:** one SLI, in the form `count(http_requests_total{status=~"2..|3.."}) / count(http_requests_total)` — never "everything OK".
- **On failure:** only system metrics (CPU/RAM) come to mind → that's exactly the `cpu_as_sli` mistake; reread `references/sli_design.md` and pick a request-level SLI.

#### Step 3: Set the target from historical data

- **Action:** measure the SLI over the last 30 days; `target = floor(p50 × 100) / 100`.
- **Expected:** a target the system has actually already met — not a wish.
- **On failure:** no historical data → deploy SLI measurement first, and come back in 30 days; don't guess.

#### Step 4: Render the SLO definition

- **Action:** `python scripts/slo_designer.py --service <svc> --sli-type <type> --target <t> --window-days 28 --owner <team> --policy-doc <path>`
- **Expected:** the markdown output has no `<must define>` placeholder and no `WARNING: missing required fields` line.
- **On failure:** exit code 2 → a required flag is missing; add it per the error; the output has `<must define>` → add `--owner`/`--policy-doc` and rerun.

#### Step 5: Generate burn-rate alerts

- **Action:** `python scripts/error_budget_calculator.py --target <t> --window-days <w>`
- **Expected:** the output lists `fast_burn`, `slow_burn`, `ticket_burn` rows with `burn rate` values and PromQL-shaped rules.
- **On failure:** the allowed downtime shows `0` → a 100% target isn't an SLO; pick a realistic target.

#### Step 6: Write the error-budget policy

- **Action:** fill in `assets/error_budget_policy.md` (budget <50% / <10% / exhausted → who does what).
- **Expected:** the policy doc is committed and linked from the SLO definition.
- **On failure:** the team won't commit to consequences → the SLO is decoration; escalate before continuing.

#### Step 7: Review before going live

- **Action:** `python scripts/slo_review.py --slo-doc <dir-or-file>`
- **Expected:** exit code 0, no FAIL/WARN.
- **On failure:** exit code 1 → fix every `[FAIL]` line (lower the target, define the SLI, add the policy link), and rerun until exit code 0.

### Workflow 2: Quarterly SLO review

#### Step 1: Run the review gate over all active SLOs

- **Action:** `python scripts/slo_review.py --slo-doc assets/slos/   # bundled sample SLO-doc directory; swap in docs/slos/ for your real project`
- **Expected:** exit code 0; any `[FAIL]`/`[WARN]` line is a work item.
- **On failure:** fix findings first; don't tune targets and tune checks in the same change.

#### Step 2: Calibrate targets with last quarter's data

- **Action:** for each SLO decide: never burned → tighten; repeatedly burned → loosen the target or fix the system; alerts ignored → adjust thresholds.
- **Expected:** each SLO ends the review with a keep/tighten/loosen decision on record.
- **On failure:** no burn data collected → the SLI isn't being measured at all; return to Workflow 1 Step 2.

#### Step 3: Audit policy enforcement and archive

- **Action:** check whether the error-budget policy was actually followed when the budget burned through; commit the revised SLO and archive the old version with a date stamp.
- **Expected:** the revised doc is committed; the archive is retrievable by date.
- **On failure:** the policy was ignored twice running → the problem is organizational, not numerical; escalate to the owning team's lead.

### Workflow 3: SLO-driven rollback

#### Step 1: Detect abnormal burning

- **Action:** a burn-rate alert fires from the thresholds generated in Workflow 1 Step 5.
- **Expected:** the alert states the SLO, window, and current burn rate.
- **On failure:** the alert lacks these fields → the thresholds were hand-edited; regenerate with the calculator.

#### Step 2: Roll back via the kill switch

- **Action:** trigger the feature-flag kill switch (see `feature-flags-architect`); confirm the new release stops burning the budget.
- **Expected:** the burn rate returns to baseline within one alert window.
- **On failure:** still burning after rollback → the regression wasn't caused by this release; declare an incident instead.

#### Step 3: Feed the post-mortem into the next revision

- **Action:** record what burned, why, and whether the target was set correctly.
- **Expected:** the post-mortem action items reference concrete SLO parameter changes.
- **On failure:** the revision has no owner → the SLO will rot; assign one before wrapping up.

## Failure Handling Table

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `slo_designer.py` exit code 2 | Missing required flag (`--service`/`--sli-type`/`--target`) | Add the flag per the argparse error and rerun |
| `WARNING: missing required fields: owner, error_budget.policy_doc` | `--owner`/`--policy-doc` not passed | Add both; the SLO isn't live until the placeholders are gone |
| `slo_review.py` exit code 1 with `[FAIL] ...` | The SLO doc hit one of the 7 mistake patterns | Fix each line, rerun until exit code 0 |
| `[FAIL] cpu_as_sli` | CPU/memory chosen as the SLI | Switch to a request-level SLI (see the quick reference) |
| The calculator shows allowed downtime `0.00 min` | Target ≈ 100% | Pick a target the system has historically actually met |
| `python: command not found` | No interpreter | Install Python ≥ 3.8; all tools use only the standard library |
| The calculator's burn rate doesn't match the math in this doc | Different `--target`/`--window-days` | Expected — the numbers here are for 99.9%/30d; trust the tool's computation for your input |

## References

Read only when the corresponding situation arises — don't preload all three:

- `references/sli_design.md` — when choosing an SLI type, or when `slo_review.py` reports `no_sli_definition`/`cpu_as_sli`; the 5 SLI types with examples and anti-patterns.
- `references/error_budget.md` — when computing a budget, tuning burn-rate alerts, or writing an error-budget policy.
- `references/composition.md` — when wiring the SLO into feature-flag aborts, chaos blast radius, or operator capability levels.

(The fundamentals of SLI, SLO, and SLA follow the Google SRE Workbook throughout.)

## Slash Commands

`/slo-design` — an interactive SLO design wizard that runs all 3 tools in sequence.

## Asset Templates

- `assets/slo_template.yaml` — a fill-in SLO YAML
- `assets/error_budget_policy.md` — a fill-in policy template

## Anti-patterns

- **Every endpoint at 99.99%** — copy-pasted SLOs that nobody verified the system can sustain
- **CPU usage as the SLI** — system metrics aren't user experience
- **Single-window burn-rate alerting** — a 5-minute window is too noisy, a 30-day window too blunt
- **No error-budget policy** — burning through with no action is meaningless
- **An SLO with no owner** — nobody accountable, it inevitably rots
- **Reviewing the SLO only once a year** — the system's character changes faster than that
- **Writing the SLA into the SLO doc** — different audience, different stakes; manage them separately
- **SLO target = SLA target** — the SLO must be tighter (beat the contract before the customer notices)

## Delivery Criteria

This skill counts as done only when:

- The SLO definition (the markdown output of `slo_designer.py`, named after its rendered heading, e.g. `slo-<service>-<sli-type>.md`) is saved in the team's SLO-doc directory (e.g. `docs/slos/`) and has **no `<must define>` placeholder**.
- The `error_budget_calculator.py` burn-rate alert rules are pasted into the alerting system and have actually fired in testing.
- The error-budget policy (filled in per `assets/error_budget_policy.md`) is committed and linked from the SLO doc.
- Every in-scope SLO passes `slo_review.py --slo-doc <dir>` with exit code 0.
- Ongoing requirement: burn-rate alerts for targeted SLOs fire ≤2 times a month (signal, not noise); the average detection time for a violation is <30 minutes; the quarterly review actually happens quarterly.
