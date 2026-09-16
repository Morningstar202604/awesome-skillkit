---
name: kubernetes-operator
description: "Use when building a Kubernetes Operator — custom controllers that reconcile CRD state. Triggers on "build an operator", "CRD design", "reconcile loop", "controller-runtime", "kubebuilder", "operator-sdk", "metacontroller", "KOPF", "operator capability levels", or "custom resource". Ships CRD validator, reconcile-loop linter, and OperatorHub capability auditor (all stdlib Python), 4 references on the operator pattern + CRD design + reconcile patterns + tooling landscape, and a /operator-audit slash command. NOT a generic k8s skill — specifically the Operator pattern. 当用户要求 写 K8s Operator / 自定义控制器 时使用。 Do NOT use for operating a live cluster (manifest and operator authoring only)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: infrastructure
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Kubernetes Operator

Build operators that reconcile correctly. Most operator bugs are not Kubernetes bugs — they are reconcile-loop bugs: missing finalizers, blocking calls, no requeue on transient errors, status drift, RBAC over-grants. This skill catches them deterministically before they reach a cluster.

## When to use

- Building a new Kubernetes Operator (controller for a CRD)
- Reviewing an existing operator for capability-level gaps
- Auditing a CRD spec for status/conditions/finalizer correctness
- Choosing a framework (controller-runtime / kubebuilder / operator-sdk / metacontroller / KOPF)
- Designing the API surface of a Custom Resource
- Hardening RBAC, leader election, or webhook validation

## When NOT to use

- Plain Helm chart packaging → use `helm-chart-builder`
- Standard kubectl operations / blue-green deploys → use `senior-devops`
- General k8s security posture → use `cloud-security`
- "I want to run a workload" — that's a Deployment / Job, not an operator

## Input checklist

Collect once before running anything. If inputs are missing, ask the user once with: "要审计/构建 Operator，请一次性提供：operator 仓库路径、CRD YAML 路径、controller Go 源文件路径、目标语言/框架（如已定）。"

| Input | Required | Description |
|---|---|---|
| Operator repo root | Yes (audit/bootstrap) | directory containing `config/`, `controllers/`, `api/` → `--operator-dir` |
| CRD YAML file or directory | Yes (CRD checks) | e.g. config/crd/myapp.yaml in the user's operator repo → `--crd` |
| Go controller source | Yes (reconcile lint) | e.g. `controllers/myapp_controller.go` → `--controller` |
| Group/Version/Kind | Yes (new operator) | e.g. `apps.example.com/v1alpha1`, kind `MyApp` |
| Language/framework constraint | For framework choice | Go / Python / Java / polyglot; see Tooling landscape |

## Pre-flight checks

```bash
python3 --version        # Expected: Python ≥ 3.8. All 3 tools are stdlib-only.
ls scripts/crd_validator.py scripts/reconcile_lint.py scripts/operator_capability_audit.py
                         # Expected: all 3 files listed.
```

- Python missing/outdated → install Python ≥ 3.8, then STOP.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then STOP.
- Auditing an existing operator? Also run `ls <operator-dir>/config/crd/ <operator-dir>/controllers/` — expected: at least one CRD YAML and one controller `.go` file. Missing → confirm the repo layout with the user before proceeding (do not guess paths).

## Core principle: an operator is a reconcile loop, not a script

```text
observe(actual) → desired = read(spec) → diff(actual, desired) → act → update(status)
                                                                          ↓
                                                                   requeue / done
```

Operators that fail are the ones that:
1. Treat reconcile as imperative (do this, then this, then this) instead of declarative (make actual=desired, idempotently)
2. Don't requeue transient failures
3. Don't use finalizers, leaving orphan resources
4. Mutate spec instead of status
5. Don't use the status subresource (status updates trigger spec reconciles → loop)
6. Block in reconcile (long HTTP calls, locks)
7. Forget leader election → split-brain on multi-replica deploys

The 3 tools below catch each of these.

## Quick start

```bash
SKILL=skills/programming/infrastructure/kubernetes-operator   # from the awesome-skillkit repo root

# Validate a CRD design
python "$SKILL/scripts/crd_validator.py" --crd config/crd/myapp.yaml

# Lint a Go reconcile function
python "$SKILL/scripts/reconcile_lint.py" --controller controllers/myapp_controller.go

# Score against OperatorHub Capability Levels (1-5)
python "$SKILL/scripts/operator_capability_audit.py" --operator-dir .
```

## The 3 Python tools

All stdlib-only. Run with `--help`.

### `crd_validator.py`

Validates a CRD YAML against operator-pattern best practices.

```bash
python scripts/crd_validator.py --crd config/crd/myapp.yaml
python scripts/crd_validator.py --crd config/crd/ --format json
```

**Checks:**
- `spec.versions[*].subresources.status` is set (status subresource)
- `spec.scope` is `Namespaced` (not `Cluster`) unless explicitly justified
- Singular and listKind defined
- `spec.versions[*].schema.openAPIV3Schema` has type definitions (no `x-kubernetes-preserve-unknown-fields: true` at top level)
- A version is marked `served: true` AND `storage: true`
- Conditions array is in the schema (allows `metav1.Conditions`)
- Printer columns include `Age` and `Status`/`Phase`

### `reconcile_lint.py`

Lints a Go controller reconcile function for anti-patterns.

```bash
python scripts/reconcile_lint.py --controller controllers/myapp_controller.go
```

**Checks (regex-based heuristics):**
- Returns are `(ctrl.Result, error)` shape
- Errors trigger a non-zero requeue (`return ctrl.Result{Requeue: true}, err`)
- `client.Update()` on the spec object is flagged (controllers should update only status)
- `time.Sleep` inside reconcile is flagged (use `RequeueAfter`)
- HTTP calls without context cancellation are flagged
- Missing `defer` after a finalizer add
- No `IsConditionTrue` / `SetCondition` calls when conditions present in CRD
- Reconcile function exceeds 80 lines (extract subroutines)

### `operator_capability_audit.py`

Scores an operator against OperatorHub's 5 Capability Levels.

```bash
python scripts/operator_capability_audit.py --operator-dir .
```

**Levels:**
- **L1 — Basic Install:** CRD defined, controller deploys it
- **L2 — Seamless Upgrades:** PDBs, conversion webhooks, version skew strategy
- **L3 — Full Lifecycle:** backups, restores, failure recovery
- **L4 — Deep Insights:** metrics endpoint, Prometheus rules, alerts
- **L5 — Auto Pilot:** auto-scaling, auto-tuning, anomaly detection

Reports current level + concrete next steps to advance one level.

## Parameter quick reference

| Parameter | Values | Notes |
|---|---|---|
| `--crd` | path to CRD YAML file or directory | validator; directories are scanned recursively |
| `--controller` | path to Go source file | linter; regex heuristics, not a Go AST parser |
| `--operator-dir` | operator repo root | capability audit; walk detects L1–L5 evidence |
| `--format` | `text` / `json` (all 3 tools) | JSON for CI pipelines and diffing |

## Tooling landscape

Pick a framework based on language and complexity. See `references/tooling_landscape.md`.

| Framework | Language | Best for | Maintenance |
|---|---|---|---|
| **controller-runtime** | Go | Production-grade, low-level control | Active (sig-api-machinery) |
| **kubebuilder** | Go | Standard scaffolding, opinionated | Active (Kubernetes SIGs) |
| **operator-sdk** | Go / Helm / Ansible | OpenShift / mixed-paradigm teams | Active (Red Hat) |
| **metacontroller** | Any (webhook-based) | Polyglot teams, avoiding Go | Less active |
| **KOPF** | Python | Python shops, async-first | Active (community) |
| **java-operator-sdk** | Java | JVM shops | Active (Red Hat / Java SIG) |

Decision rules:
- New operator + Go shop → kubebuilder
- New operator + Python shop → KOPF
- New operator + can't pick a language → metacontroller
- OpenShift target → operator-sdk

## CRD design principles

See `references/crd_design.md` for full detail. Quick rules:

1. **status is the source of truth for the controller's view of the world.** Spec is what the user wants; status is what the controller observed.
2. **Use the status subresource.** Without it, status updates re-trigger reconcile (loop).
3. **Use Conditions.** `Ready`, `Reconciling`, `Degraded`. Each carries a reason and message.
4. **Add finalizers.** Without finalizers, deletion races the controller and orphans external resources.
5. **Version your CRD from day 1.** `v1alpha1` → `v1beta1` → `v1`. Plan a conversion webhook.
6. **Validate via OpenAPI v3 schema.** Don't rely on the controller for validation that should fail at admission.
7. **Use `additionalPrinterColumns` for `kubectl get`.** Show `Age`, `Phase`, `Ready` at minimum.
8. **Namespace your CRDs unless they manage cluster-scoped resources.**

## Reconcile loop principles

See `references/reconcile_loop.md` for full detail. Quick rules:

1. **Idempotent.** Reconciling the same state twice → same result, zero side effects.
2. **Read once, decide, act.** Don't observe the world repeatedly during reconcile.
3. **Update status, not spec.** Spec belongs to the user.
4. **Return errors that requeue.** Use `ctrl.Result{RequeueAfter: ...}` for known transient cases.
5. **Never block.** No `time.Sleep`. No long HTTP calls without context.
6. **Use the cache.** Read via the controller's cached client; only escape the cache for a specific reason.
7. **Leader-elect when running >1 replica.** Otherwise enable single-replica mode.
8. **Set OwnerReferences.** Cascading deletion is the operator pattern's free gift.

## Workflows

### Workflow 1: Bootstrap a new operator (Go + kubebuilder)

#### Step 1: Fix the API shape

- **Action:** pick Group/Version/Kind, e.g. `apps.example.com/v1alpha1`, kind `MyApp`.
- **Expected:** a one-line API statement the user has confirmed.
- **If it fails:** user unsure → ask once; do not invent a group domain.

#### Step 2: Scaffold with kubebuilder

- **Action:** `kubebuilder init --domain example.com --repo github.com/org/myapp-operator && kubebuilder create api --group apps --version v1alpha1 --kind MyApp`
- **Expected:** config/crd/bases/apps.example.com_myapps.yaml and `controllers/myapp_controller.go` exist.
- **If it fails:** kubebuilder not installed → install it (see kubebuilder docs) and STOP; do not hand-roll the scaffold.

#### Step 3: Validate the generated CRD

- **Action:** `python scripts/crd_validator.py --crd config/crd/bases/apps.example.com_myapps.yaml`
- **Expected:** no FAIL findings (warnings about printer columns/conditions are common on fresh scaffolds).
- **If it fails:** fix every finding (add status subresource, conditions, printer columns) — start from `assets/crd_template.yaml` — then re-run until clean.

#### Step 4: Implement the reconcile function

- **Action:** write the simplest correct version first: read desired state, diff, act, update status.
- **Expected:** function compiles; no `time.Sleep`; status updated via `r.Status().Update`.
- **If it fails:** logic feels imperative ("if creating do A") → reshape to "make actual=desired" per `references/reconcile_loop.md`.

#### Step 5: Lint the controller

- **Action:** `python scripts/reconcile_lint.py --controller controllers/myapp_controller.go`
- **Expected:** zero FAIL findings; function ≤80 lines.
- **If it fails:** apply the fix named in each finding (`RequeueAfter` instead of sleep, `Status().Update` instead of `Update`), re-run until clean.

#### Step 6: Audit capability level

- **Action:** `python scripts/operator_capability_audit.py --operator-dir .`
- **Expected:** at least L1 reported with concrete next steps listed.
- **If it fails:** below L1 → CRD or Deployment manifest missing; finish scaffold first.

#### Step 7: Smoke-test in a throwaway cluster

- **Action:** `kubectl apply -f config/samples/` against a kind cluster; watch `kubectl get myapps` show conditions.
- **Expected:** sample resource becomes `Ready=True` without controller error loops in logs.
- **If it fails:** infinite reconcile loop in logs → return to Step 4; do not deploy further.

### Workflow 2: Audit an existing operator

#### Step 1: Score the repo

- **Action:** `python scripts/operator_capability_audit.py --operator-dir <path>`
- **Expected:** a level (1–5) plus gap list for the next level.
- **If it fails:** wrong directory (no CRDs found) → confirm repo root with the user.

#### Step 2: Validate CRDs and lint controllers

- **Action:** `python scripts/crd_validator.py --crd config/crd/` then `python scripts/reconcile_lint.py --controller controllers/` (repeat per controller file).
- **Expected:** a findings list you can triage.
- **If it fails:** tool cannot parse a file → check it is YAML/Go as expected; malformed files are themselves findings.

#### Step 3: Triage and document

- **Action:** FAIL → block release, fix before next deploy; WARN → file an issue, fix within 30 days. Document the current capability level in README.
- **Expected:** every finding has an owner and a due date; README states the level.
- **If it fails:** findings without owners → assign before closing; unowned findings always bit-rot.

#### Step 4: Plan advancement

- **Action:** schedule one capability level advancement per quarter.
- **Expected:** next level's gap list (from Step 1 output) becomes the roadmap.
- **If it fails:** gaps too large for a quarter → descope to the smallest subset that advances the level.

### Workflow 3: Choose a framework

#### Step 1: Identify constraints

- **Action:** note team language skills, deployment target (vanilla k8s vs OpenShift), operator complexity (single CRD vs multi-CRD vs cluster-wide).
- **Expected:** three constraints written down.
- **If it fails:** constraints conflict (e.g. Python shop + OpenShift-only feature) → surface the conflict to the user; it changes the recommendation.

#### Step 2: Match against the landscape

- **Action:** apply the decision rules above; cross-check with `references/tooling_landscape.md`.
- **Expected:** exactly one primary framework with a stated reason.
- **If it fails:** two candidates tie → build a 1-week proof-of-concept of each before committing.

## Failure handling

| Symptom / exit code | Cause | Fix |
|---|---|---|
| Validator exits 2 (`--crd` required) | no CRD path given | pass `--crd <file-or-dir>`; use `--format json` in CI |
| Validator: `status subresource` finding | CRD lacks `subresources.status` | add it; without it status updates loop reconciles |
| Validator: `x-kubernetes-preserve-unknown-fields` finding | schema escapes validation | define concrete types or scope the escape to a leaf field |
| Linter: `time.Sleep` finding | blocking inside reconcile | replace with `ctrl.Result{RequeueAfter: ...}` |
| Linter: spec `client.Update()` finding | controller mutates user-owned spec | update status only via `r.Status().Update(ctx, obj)` |
| Audit reports below expected level | evidence files absent (PDB, metrics, backups) | treat gap list as the work plan; do not hand-edit the score |
| Linter/validator parse errors on input | file is not the expected format | confirm path/extension; malformed input is itself a finding |
| `python: command not found` | no interpreter | install Python ≥ 3.8; all tools are stdlib-only |

## References

Read the reference only when the corresponding situation applies:

- `references/operator_pattern.md` — read when deciding whether an operator is the right tool at all (vs Deployment/Job/Helm).
- `references/crd_design.md` — read when designing or versioning a CRD, or fixing validator findings about schema/conditions/finalizers.
- `references/reconcile_loop.md` — read when writing or fixing the reconcile function, or resolving linter findings.
- `references/tooling_landscape.md` — read when choosing between frameworks (Workflow 3).

## Slash command

`/operator-audit` — Run all 3 tools on an operator repo and produce a markdown report.

## Asset templates

- `assets/crd_template.yaml` — CRD with status subresource, conditions, finalizer hint, printer columns
- `assets/reconcile_skeleton.go` — Go controller reconcile function with idempotency, conditions, finalizers, requeue patterns

## Anti-patterns

- **`time.Sleep(30 * time.Second)` inside reconcile** — block other reconciles. Use `RequeueAfter`.
- **`r.Client.Update(ctx, obj)` to set status** — use `r.Status().Update(ctx, obj)` instead.
- **No leader election + 2+ replicas** — split-brain.
- **No finalizer** — external resources orphan on deletion.
- **CRD without status subresource** — status updates trigger spec reconciles (infinite loop).
- **Reconcile function > 200 lines** — extract reconcileXxx subroutines per condition.
- **`x-kubernetes-preserve-unknown-fields: true` on spec root** — defeats validation.
- **Imperative reconcile** — "if creating, do A; if updating, do B; if deleting, do C". Wrong shape. Reconcile = make actual=desired, regardless of how we got here.

## Deliverables and success criteria

A run of this skill is done when:

- All three tools exit clean on the target repo: `crd_validator.py` (0 FAIL), `reconcile_lint.py` (0 FAIL), `operator_capability_audit.py` (a reported level with documented gaps).
- The audit report (markdown from `/operator-audit` or tool text output, e.g. `operator_audit_<date>.md`) is saved in the operator repo's `docs/` or attached to the review.
- The operator's README states the current OperatorHub capability level.
- Ongoing: 100% of new CRDs pass `crd_validator.py` before merge; reconcile functions pass `reconcile_lint.py`; operators reach Level 3 (Full Lifecycle) before public release.
