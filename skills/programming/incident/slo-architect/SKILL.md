---
name: slo-architect
description: "Use when defining, reviewing, or operating SLOs/SLIs/error budgets. Triggers on "define an SLO", "what should our SLO be", "error budget", "burn rate", "SLI", "service level objective", "Google SRE workbook", "multi-window burn-rate alert", or any reliability-target question. Ships SLO designer, error-budget calculator with multi-window burn-rate thresholds, and SLO reviewer that catches the common bugs (target too aggressive, window too short, conflicting SLOs, no SLI definition). 4 references on SLO principles + SLI design + error budget math + composition with feature-flags-architect/chaos-engineering/kubernetes-operator. NOT a generic observability skill — specifically the SLO discipline. 当用户要求 定 SLO / 设计 SLI 与错误预算 / 可用性目标 时使用。 Do NOT use for provisioning monitoring infrastructure."
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

Define SLOs that mean something. Most "SLOs" in the wild are arbitrary numbers no one believes — 99.9% on every endpoint, no SLI definition, no error budget, no policy for what happens when budget burns. This skill enforces the discipline from Google's SRE Workbook: pick the right SLI, set a target users actually care about, calculate the error budget, wire multi-window burn-rate alerts, and have a written policy for when budget runs out.

## When to use

- Defining a new SLO for a service or feature
- Reviewing existing SLOs for common bugs
- Picking the right SLI (event-based vs time-window based vs request-based)
- Computing error budgets and burn-rate alert thresholds
- Tying SLOs to existing controls — feature flags abort, chaos blast radius, operator capability levels

## When NOT to use

- General observability strategy (metrics + logs + traces) → use `observability-designer`
- Customer-facing SLAs with legal teeth → that's contract drafting, not engineering
- Performance load testing (capacity, not reliability) → use `performance-profiler`
- Active incident response → use `incident-response`

## Input checklist

Collect all of this in one pass before running any tool. If inputs are missing, ask the user once with: "要生成 SLO，请一次性提供：服务名、SLI 类型、目标值、窗口天数、负责人、错误预算策略文档路径（如已有 SLO 文档目录也给 review 用）。"

| Input | Required | Description |
|---|---|---|
| Service name | Yes | e.g. `checkout-svc` → `--service` |
| SLI type | Yes | one of `request-success-rate`, `request-latency`, `availability-time`, `data-freshness`, `correctness` → `--sli-type` |
| Target | Yes | e.g. `99.9` (percent) → `--target`; pick from 30 days of historical SLI data, not vibes |
| Window days | No | default 28 (= 4 calendar weeks) → `--window-days` |
| Owner | For a live SLO | team or person on the hook → `--owner`; omitted renders `<must define>` placeholder |
| Error budget policy doc | For a live SLO | path to the written policy → `--policy-doc`; omitted renders `<must define>` placeholder |
| SLO doc directory | For review only | where existing SLO definitions (markdown/JSON) live → `--slo-doc` |

## Pre-flight checks

Run from the repo root (or the skill directory for the relative forms below). Stop at the first failure and fix it — do not improvise.

```bash
python3 --version        # Expected: Python ≥ 3.8. All 3 tools are stdlib-only.
ls scripts/slo_designer.py scripts/error_budget_calculator.py scripts/slo_review.py
                         # Expected: all 3 files listed.
```

- Python missing/outdated → install Python ≥ 3.8, then STOP (do not run the tools with another interpreter version you did not verify).
- Script files missing → you are in the wrong directory; `cd` to this skill's directory, then STOP and re-check.
- Reviewing existing SLOs? Also run `ls <slo-doc-dir>` — expected: at least one `.md`/`.json` SLO doc. Empty → point `--slo-doc` at the real directory or use `--sample` to see the tool's output shape first.

## Quick start

```bash
SKILL=skills/programming/incident/slo-architect   # from the awesome-skillkit repo root

# 1. Design an SLO
python "$SKILL/scripts/slo_designer.py" \
  --service checkout-svc \
  --sli-type request-success-rate \
  --target 99.9 \
  --window-days 30

# 2. Compute error budget + multi-window burn-rate alerts
python "$SKILL/scripts/error_budget_calculator.py" \
  --target 99.9 --window-days 30

# 3. Review existing SLO definitions for common bugs
python "$SKILL/scripts/slo_review.py" --slo-doc docs/slos/
```

## The 3 Python tools

All stdlib-only.

### `slo_designer.py`

Generates a structured SLO definition with required fields. Missing `--service`/`--sli-type`/`--target` → argparse error, exit 2. Missing `--owner`/`--policy-doc` → renders with `<must define>` placeholders plus a `WARNING: missing required fields` line; the SLO is NOT live until those are filled.

```bash
python scripts/slo_designer.py \
  --service checkout-svc \
  --sli-type request-success-rate \
  --target 99.9 \
  --window-days 30 \
  --owner team-checkout
```

**SLI types supported:**
- `request-success-rate` — `(total_requests - bad_requests) / total_requests`
- `request-latency` — `count(requests < threshold) / total_requests`
- `availability-time` — `(window - downtime) / window`
- `data-freshness` — `count(data_age < threshold) / total_data_points`
- `correctness` — `count(correct_outputs) / total_outputs`

Output is markdown by default with all required fields filled or marked `<must define>`. JSON output (`--format json`) is consumed by `slo_review.py`.

### `error_budget_calculator.py`

Given target availability + window, computes:
- Allowed downtime in the window
- Multi-window burn-rate thresholds per Google SRE Workbook (Chapter 5):
  - **Fast burn** — page if 2% of monthly budget consumed in 1 hour
  - **Slow burn** — page if 5% consumed in 6 hours
  - **Ticket burn** — ticket if 10% consumed in 3 days
- Recommended alerting rules (PromQL-shaped output)

```bash
python scripts/error_budget_calculator.py --target 99.9 --window-days 30
python scripts/error_budget_calculator.py --target 99.95 --window-days 7 --format json
```

### `slo_review.py`

Audits a directory of SLO definitions (markdown or JSON) for the common bugs. Exit 0 = clean, exit 1 = findings exist (use as a pre-merge gate).

```bash
python scripts/slo_review.py --slo-doc docs/slos/
```

**Checks:**
- `target_too_high`: target ≥ 99.99% (sustainable only with massive engineering investment)
- `target_too_low`: target ≤ 99.0% (probably wrong SLI; users will notice)
- `window_too_short`: window < 7 days (statistical noise dominates)
- `window_too_long`: window > 90 days (slow feedback)
- `no_sli_definition`: SLI section missing or vague ("everything OK")
- `no_error_budget_policy`: no documented action when budget burns
- `cpu_as_sli`: CPU/memory used as user-experience proxy (wrong signal)

## Parameter quick reference

| Parameter | Values | Notes |
|---|---|---|
| `--sli-type` | `request-success-rate` / `request-latency` / `availability-time` / `data-freshness` / `correctness` | designer only |
| `--window-days` | int, default 28 | designer + calculator; review flags <7 or >90 |
| `--target` | float percent, e.g. `99.9` | designer + calculator |
| `--format` | `markdown`/`json` (designer), `text`/`json` (calculator, review) | JSON designer output feeds `slo_review.py` |
| `--owner`, `--policy-doc`, `--user-journey`, `--sli-numerator`, `--sli-denominator`, `--sli-labels`, `--review-cadence` | free text | designer; missing owner/policy → `<must define>` |
| `--slo-doc` | path to file or directory | review only; `--sample` audits an embedded example |

## SLI selection cheatsheet

| User experience | SLI type | What you measure |
|---|---|---|
| "Did the request succeed?" | request-success-rate | `2xx / total` |
| "Was the response fast?" | request-latency | `count(p99 < threshold) / total` |
| "Was the service up?" | availability-time | `(window - downtime) / window` |
| "Is the data current?" | data-freshness | `count(data_age < threshold) / total` |
| "Was the answer correct?" | correctness | `count(correct) / total` |

See `references/sli_design.md` for examples and anti-patterns.

## Error budget math (the basics)

For 99.9% SLO over 30 days (matches `error_budget_calculator.py --target 99.9 --window-days 30`):
- Allowed unavailability: `0.1% × 30 × 24 × 60 = 43.2 minutes`
- Fast burn: 2% of budget burned in 1h → `0.02 / (1/720) = 14.4` burn-rate multiplier
- Slow burn: 5% of budget burned in 6h → `0.05 / (6/720) = 6.0` multiplier
- Ticket burn: 10% of budget burned in 3d → `0.10 / (72/720) = 1.0` multiplier

`error_budget_calculator.py` does this math for you and emits ready-to-paste alert rules.

## Composition with the rest of the portfolio

This skill explicitly composes with three others:

| Skill | Composition |
|---|---|
| `feature-flags-architect` | Rollout abort criteria reference SLO burn-rate thresholds |
| `chaos-engineering` | Blast-radius calculator already takes monthly error budget as input — define it here |
| `kubernetes-operator` | Operator capability L4 (Deep Insights) requires SLOs + Prometheus rules |

The `error_budget_calculator.py` output is in the same shape as the chaos-engineering skill's `blast_radius_calculator.py` expects on stdin.

## Workflows

### Workflow 1: Define a new SLO

#### Step 1: Collect inputs and pick the user journey

- **Action:** fix the user journey to protect (e.g. "checkout completion"); collect the Input checklist in one pass.
- **Expected:** a written journey statement plus service name, SLI type, owner, policy doc path.
- **If it fails:** user cannot name the journey → do not invent one; ask which user-facing flow pays the bills if it breaks.

#### Step 2: Choose and define the SLI

- **Action:** pick SLI type via the cheatsheet; define numerator/denominator with concrete labels (or pass `--sli-numerator`/`--sli-denominator`/`--sli-labels`).
- **Expected:** an SLI sentence like `count(http_requests_total{status=~"2..|3.."}) / count(http_requests_total)` — never "everything OK".
- **If it fails:** only system metrics (CPU/RAM) come to mind → that is the `cpu_as_sli` bug; re-read `references/sli_design.md` and pick a request-level SLI.

#### Step 3: Pick a target from history

- **Action:** measure the SLI over the last 30 days; `target = floor(p50 × 100) / 100`.
- **Expected:** a target the system has already sustained — not an aspirational number.
- **If it fails:** no historical data exists → deploy SLI measurement first, revisit in 30 days; do not guess.

#### Step 4: Render the SLO definition

- **Action:** `python scripts/slo_designer.py --service <svc> --sli-type <type> --target <t> --window-days 28 --owner <team> --policy-doc <path>`
- **Expected:** markdown with no `<must define>` placeholders and no `WARNING: missing required fields` line.
- **If it fails:** exit 2 → a required flag is missing, add it; `<must define>` in output → supply `--owner`/`--policy-doc` and re-run.

#### Step 5: Generate burn-rate alerts

- **Action:** `python scripts/error_budget_calculator.py --target <t> --window-days <w>`
- **Expected:** output lists `fast_burn`, `slow_burn`, `ticket_burn` rows with `burn rate` values and PromQL-shaped rules.
- **If it fails:** allowed downtime shows `0` → target 100% is not an SLO; pick a realistic target.

#### Step 6: Write the error budget policy

- **Action:** fill `assets/error_budget_policy.md` (when budget <50% / <10% / exhausted → who does what).
- **Expected:** policy doc committed and linked from the SLO definition.
- **If it fails:** team won't commit to consequences → the SLO is decoration; escalate before proceeding.

#### Step 7: Review before going live

- **Action:** `python scripts/slo_review.py --slo-doc <dir-or-file>`
- **Expected:** exit 0, no FAIL/WARN findings.
- **If it fails:** exit 1 → fix each `[FAIL]` line (lower target, define SLI, add policy link) and re-run until exit 0.

### Workflow 2: Quarterly SLO review

#### Step 1: Run the review gate on every active SLO

- **Action:** `python scripts/slo_review.py --slo-doc docs/slos/`
- **Expected:** exit 0; any `[FAIL]`/`[WARN]` line is a work item.
- **If it fails:** fix findings first; do not adjust targets and checks in the same change.

#### Step 2: Calibrate targets against last quarter's data

- **Action:** for each SLO decide: never burned → tighten; burned constantly → loosen target or fix the system; alerts useless → adjust thresholds.
- **Expected:** each SLO ends the review with keep/tighten/loosen decision recorded.
- **If it fails:** no burn data collected → the SLI isn't actually measured; go back to Workflow 1 Step 2.

#### Step 3: Audit policy follow-through and archive

- **Action:** check whether error budget policies were actually followed when budget burned; commit revised SLOs, archive old versions with date stamps.
- **Expected:** revised docs committed; archives retrievable by date.
- **If it fails:** policies ignored twice in a row → the problem is organizational, not numeric; escalate to the owning team's lead.

### Workflow 3: SLO-driven rollback

#### Step 1: Detect abnormal burn

- **Action:** burn-rate alert fires from thresholds generated in Workflow 1 Step 5.
- **Expected:** alert names the SLO, window, and current burn rate.
- **If it fails:** alert fired without those fields → thresholds were hand-edited; regenerate from the calculator.

#### Step 2: Roll back via kill switch

- **Action:** trip the feature-flag kill switch (see `feature-flags-architect`); confirm new deploys stop burning budget.
- **Expected:** burn rate returns to baseline within one alert window.
- **If it fails:** burn continues after rollback → the regression is not the deploy; open an incident instead.

#### Step 3: Feed the postmortem into the next revision

- **Action:** record what burned, why, and whether the target was right.
- **Expected:** postmortem action items reference concrete SLO parameter changes.
- **If it fails:** no owner for the revision → SLO bit-rots; assign one before closing.

## Failure handling

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `slo_designer.py` exits 2 | required flag missing (`--service`/`--sli-type`/`--target`) | add the flag shown in the argparse error and re-run |
| `WARNING: missing required fields: owner, error_budget.policy_doc` | `--owner`/`--policy-doc` omitted | supply both; SLO is not live until placeholders are gone |
| `slo_review.py` exits 1 with `[FAIL] ...` | SLO doc has one of the 7 bug patterns | fix each listed finding, re-run until exit 0 |
| `[FAIL] cpu_as_sli` | CPU/memory chosen as SLI | switch to a request-level SLI (see cheatsheet) |
| Allowed downtime `0.00 min` in calculator output | target ≈ 100% | pick a target the system has sustained historically |
| `python: command not found` | no interpreter | install Python ≥ 3.8; all tools are stdlib-only |
| Calculator burn rates differ from this doc's math | different `--target`/`--window-days` | expected — the numbers here assume 99.9%/30d; trust the tool for your inputs |

## References

Read the reference only when the corresponding situation applies — do not preload all three:

- `references/sli_design.md` — read when choosing an SLI type or when `slo_review.py` flags `no_sli_definition`/`cpu_as_sli`; 5 SLI types with examples and anti-patterns.
- `references/error_budget.md` — read when computing budgets, tuning burn-rate alerts, or writing the error budget policy.
- `references/composition.md` — read when wiring SLOs into feature-flag aborts, chaos blast radius, or operator capability levels.

(SLI vs SLO vs SLA fundamentals follow the Google SRE Workbook canon throughout.)

## Slash command

`/slo-design` — interactive SLO design wizard that runs all 3 tools.

## Asset templates

- `assets/slo_template.yaml` — fillable SLO YAML
- `assets/error_budget_policy.md` — fillable policy template

## Anti-patterns

- **99.99% on every endpoint** — copy-paste SLOs that nobody verified the system can sustain
- **CPU usage as SLI** — system metrics aren't user experience
- **Single-window burn-rate alert** — too noisy if 5-min, too slow if 30-day
- **No error budget policy** — burning budget means nothing without an action
- **SLOs without owners** — no one is responsible; they bit-rot
- **SLOs reviewed once a year** — system characteristics change faster than that
- **SLAs in the SLO doc** — different audience, different stakes; keep them separate
- **SLO target = SLA target** — SLO must be tighter (you should beat your contract before customers notice)

## Deliverables and success criteria

A run of this skill is done when:

- The SLO definition (markdown from `slo_designer.py`, named after the rendered title, e.g. `slo-<service>-<sli-type>.md`) is saved in the team's SLO doc directory (e.g. `docs/slos/`) with **no `<must define>` placeholders**.
- The burn-rate alert rules from `error_budget_calculator.py` are pasted into the alerting system and fire in a test.
- The error budget policy (filled from `assets/error_budget_policy.md`) is committed and linked from the SLO doc.
- `slo_review.py --slo-doc <dir>` exits 0 for every SLO in scope.
- Ongoing: burn-rate alerts fire ≤2 times/month per SLO that's hit (signal, not noise); mean time to detect a violation <30 min; quarterly reviews actually happen quarterly.
