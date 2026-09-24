---
name: kubernetes-operator
description: >-
  Use when building a Kubernetes Operator — custom controllers that reconcile CRD state. Triggers on "build an operator", "CRD design", "reconcile loop", "controller-runtime", "kubebuilder", "operator-sdk", "metacontroller", "KOPF", "operator capability levels", "custom resource", writing a K8s operator, or building a custom controller. Ships CRD validator, reconcile-loop linter, and OperatorHub capability auditor (all stdlib Python), 4 references on the operator pattern + CRD design + reconcile patterns + tooling landscape, and a /operator-audit slash command. NOT a generic k8s skill — specifically the Operator pattern. Do NOT use for operating a live cluster (manifest and operator authoring only).
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

Build correctly-reconciling operators. Most operator problems aren't Kubernetes problems; they're reconcile-loop problems: missing finalizers, blocking calls, transient errors not requeued, status drift, over-broad RBAC. This skill uses deterministic means to catch them before code hits the cluster.

## When to Use

- Building a new Kubernetes Operator (a controller for a CRD)
- Reviewing an existing operator's capability-level gaps
- Auditing a CRD spec's status/conditions/finalizer correctness
- Selecting a framework (controller-runtime / kubebuilder / operator-sdk / metacontroller / KOPF)
- Designing a Custom Resource's API surface
- Hardening RBAC, leader election, or webhook validation

## When Not to Use

- Pure Helm chart packaging → use `helm-chart-builder`
- Routine kubectl operations / blue-green releases → use `senior-devops`
- Generic k8s security posture → use `cloud-security`
- "I just want to run a workload" — that's a Deployment / Job, not an operator

## Input Checklist

Collect everything before starting. When inputs are missing, ask the user once with this line: "To audit/build an Operator, please provide all at once: the operator repo path, the CRD YAML path, the controller Go source path, and the target language/framework (if decided)."

| Input | Required | Description |
|---|---|---|
| Operator repo root | Yes (audit/bootstrap) | The directory containing `config/`, `controllers/`, `api/` → `--operator-dir` |
| CRD YAML file or directory | Yes (CRD check) | config/crd/myapp.yaml in the user's operator repo → `--crd` |
| Go controller source | Yes (reconcile lint) | e.g. `controllers/myapp_controller.go` → `--controller` |
| Group/Version/Kind | Yes (new operator) | e.g. `apps.example.com/v1alpha1`, kind `MyApp` |
| Language/framework constraint | For framework selection | Go / Python / Java / multi-language; see the tooling landscape |

## Pre-flight Checks

```bash
python3 --version        # Expected: Python ≥ 3.8. All 3 tools depend only on the standard library.
ls scripts/crd_validator.py scripts/reconcile_lint.py scripts/operator_capability_audit.py
                         # Expected: all 3 files listed.
```

- Python missing or too old → install Python ≥ 3.8, then stop.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then stop.
- Auditing an existing operator? Also run `ls <operator-dir>/config/crd/ <operator-dir>/controllers/` — expected: at least one CRD YAML and one controller `.go` file. Missing → confirm the repo layout with the user before continuing (don't guess paths).

## Core Principle: an operator is a reconcile loop, not a script

```text
observe(actual) → desired = read(spec) → diff(actual, desired) → act → update(status)
                                                                          ↓
                                                                   requeue / done
```

Failed operators usually look like this:

1. Treating reconcile as an imperative script (do this, then that) rather than declarative (make actual=desired, idempotently)
2. Not requeuing on transient failure
3. Not using finalizers, leaving orphaned resources
4. Updating spec instead of status
5. Not using the status subresource (a status update triggers spec reconciliation → infinite loop)
6. Blocking inside reconcile (long HTTP calls, locks)
7. Forgetting leader election → split-brain on multi-replica deployments

The 3 tools below catch these one by one.

## Quick Start

```bash
# Run the following commands inside the skill directory (skills/programming/infrastructure/kubernetes-operator/)

# Validate a CRD design
python scripts/crd_validator.py --crd assets/config/crd/myapp.yaml

# Lint a Go reconcile function
python scripts/reconcile_lint.py --controller assets/controllers/myapp_controller.go

# Score against OperatorHub Capability Levels (1-5)
python scripts/operator_capability_audit.py --operator-dir assets/
```

## The Three Python Tools

All depend only on the standard library. Use `--help` for usage.

### `crd_validator.py`

Validates CRD YAML against operator-pattern best practices.

```bash
python scripts/crd_validator.py --crd assets/config/crd/myapp.yaml   # bundled sample CRD
python scripts/crd_validator.py --crd assets/config/crd/ --format json
```

**Checks:**

- `spec.versions[*].subresources.status` is set (status subresource)
- `spec.scope` is `Namespaced` (not `Cluster`), unless there's a clear reason
- Singular and listKind are defined
- `spec.versions[*].schema.openAPIV3Schema` has type definitions (no top-level `x-kubernetes-preserve-unknown-fields: true`)
- At least one version marked `served: true` and `storage: true`
- The schema includes a Conditions array (compatible with `metav1.Conditions`)
- Printer columns include `Age` and `Status`/`Phase`

### `reconcile_lint.py`

The reconcile function of Go controllers, looking for anti-patterns.

```bash
python scripts/reconcile_lint.py --controller assets/controllers/myapp_controller.go   # bundled sample controller
```

**Checks (regex heuristics):**

- The return value is a `(ctrl.Result, error)` shape
- Errors trigger a non-zero requeue (`return ctrl.Result{Requeue: true}, err`)
- Calling `client.Update()` on the spec object is flagged (the controller should only update status)
- `time.Sleep` appearing in reconcile is flagged (use `RequeueAfter` instead)
- HTTP calls without context cancellation are flagged
- A finalizer added without a `defer`
- The CRD has conditions but no `IsConditionTrue` / `SetCondition` calls
- The reconcile function exceeds 80 lines (split into subroutines)

### `operator_capability_audit.py`

Scores an operator against OperatorHub's 5 capability levels.

```bash
python scripts/operator_capability_audit.py --operator-dir .
```

**Levels:**

- **L1 — Basic Install:** CRD defined, controller responsible for deployment
- **L2 — Seamless Upgrades:** PDB, conversion webhook, version-skew policy
- **L3 — Full Lifecycle:** backup, restore, disaster recovery
- **L4 — Deep Insights:** metrics endpoint, Prometheus rules, alerts
- **L5 — Auto Pilot:** auto-scaling, auto-tuning, anomaly detection

Reports the current level + the concrete next steps to advance.

## Parameter Cheat Sheet

| Parameter | Values | Description |
|---|---|---|
| `--crd` | CRD YAML file or directory path | Validator; a directory is scanned recursively |
| `--controller` | Go source-file path | Linter; regex heuristics, not a Go AST parser |
| `--operator-dir` | operator repo root | Capability audit; walks to detect L1–L5 evidence |
| `--format` | `text` / `json` (all 3 tools support it) | JSON for CI pipelines and diff |

## Tooling Landscape

Choose a framework by language and complexity. See `references/tooling_landscape.md` for details.

| Framework | Language | Best for | Maintenance status |
|---|---|---|---|
| **controller-runtime** | Go | Production-grade, low-level control | Active (sig-api-machinery) |
| **kubebuilder** | Go | Standard scaffolding, convention-first | Active (Kubernetes SIGs) |
| **operator-sdk** | Go / Helm / Ansible | OpenShift / multi-paradigm teams | Active (Red Hat) |
| **metacontroller** | Any (webhook-based) | Multi-language teams avoiding Go | Less active |
| **KOPF** | Python | Python teams, async-first | Active (community) |
| **java-operator-sdk** | Java | JVM teams | Active (Red Hat / Java SIG) |

Decision rules:

- New operator + Go team → kubebuilder
- New operator + Python team → KOPF
- New operator + language undecided → metacontroller
- Target is OpenShift → operator-sdk

## CRD Design Principles

See `references/crd_design.md`. Quick rules:

1. **status is the source of truth for what the controller knows about the world.** spec is what the user wants; status is what the controller observes.
2. **Enable the status subresource.** Otherwise a status update triggers reconciliation again (infinite loop).
3. **Use Conditions.** `Ready`, `Reconciling`, `Degraded`, each with a reason and message.
4. **Add a finalizer.** Without one, deletion races the controller and external resources become orphans.
5. **Version the CRD from day one.** `v1alpha1` → `v1beta1` → `v1`; plan a conversion webhook.
6. **Validate with an OpenAPI v3 schema.** Validation that should fail at admission shouldn't rely on the controller as a backstop.
7. **Use `additionalPrinterColumns` to optimize `kubectl get`.** Show at least `Age`, `Phase`, `Ready`.
8. **CRDs are Namespaced unless they manage cluster-scoped resources.**

## Reconcile-Loop Principles

See `references/reconcile_loop.md`. Quick rules:

1. **Idempotent.** Reconciling the same state twice → the same result, zero side effects.
2. **Read once, decide, act.** Don't repeatedly observe the world during reconciliation.
3. **Update status, not spec.** spec belongs to the user.
4. **Return errors that trigger a requeue.** Use `ctrl.Result{RequeueAfter: ...}` for known transient cases.
5. **Never block.** No `time.Sleep`, no long HTTP calls without a context.
6. **Use the cache.** Read through the controller's cached client; only bypass the cache with a clear reason.
7. **Multi-replica requires leader election.** Otherwise run in single-replica mode.
8. **Set OwnerReferences.** Cascade deletion is a free gift of the operator pattern.

## Workflows

### Workflow 1: Scaffold an operator from scratch (Go + kubebuilder)

#### Step 1: Set the API shape

- **Action:** determine Group/Version/Kind, e.g. `apps.example.com/v1alpha1`, kind `MyApp`.
- **Expected:** a one-line API declaration confirmed by the user.
- **On failure:** the user is unsure → ask once; don't fabricate a group domain.

#### Step 2: Scaffold with kubebuilder

- **Action:** `kubebuilder init --domain example.com --repo github.com/org/myapp-operator && kubebuilder create api --group apps --version v1alpha1 --kind MyApp`
- **Expected:** config/crd/bases/apps.example.com_myapps.yaml and `controllers/myapp_controller.go` exist.
- **On failure:** kubebuilder not installed → install it (see kubebuilder docs) and stop; don't hand-write the scaffold.

#### Step 3: Validate the generated CRD

- **Action:** `python scripts/crd_validator.py --crd config/crd/bases/apps.example.com_myapps.yaml`
- **Expected:** no FAIL (fresh scaffolding commonly has printer-column/conditions WARNs, which is normal).
- **On failure:** fix each item (add status subresource, conditions, printer columns) — starting from `assets/crd_template.yaml` — rerun until clean.

#### Step 4: Implement the reconcile function

- **Action:** first write the simplest correct version: read desired state, diff, act, update status.
- **Expected:** the function compiles; no `time.Sleep`; status updated via `r.Status().Update`.
- **On failure:** the logic looks imperative ("if creating, do A") → reshape it per `references/reconcile_loop.md` into "make actual=desired".

#### Step 5: Lint the controller

- **Action:** `python scripts/reconcile_lint.py --controller assets/controllers/myapp_controller.go   # bundled sample controller`
- **Expected:** zero FAIL; function ≤80 lines.
- **On failure:** fix per each item's hint (replace sleep with `RequeueAfter`, replace `Update` with `Status().Update`), rerun until clean.

#### Step 6: Audit the capability level

- **Action:** `python scripts/operator_capability_audit.py --operator-dir .`
- **Expected:** report at least L1 and list concrete next steps.
- **On failure:** below L1 → missing CRD or Deployment manifest; finish the scaffold first.

#### Step 7: Smoke-test on an ephemeral cluster

- **Action:** `kubectl apply -f config/samples/` against a kind cluster; watch `kubectl get myapps` show conditions.
- **Expected:** the sample resource becomes `Ready=True` with no controller error loop in the logs.
- **On failure:** the logs show an infinite reconcile loop → go back to Step 4; don't keep deploying.

### Workflow 2: Audit an existing operator

#### Step 1: Score the repo

- **Action:** `python scripts/operator_capability_audit.py --operator-dir <path>`
- **Expected:** get a level (1–5) and a gap list for advancement.
- **On failure:** wrong directory (CRD not found) → confirm the repo root with the user.

#### Step 2: Validate the CRD and lint the controller

- **Action:** `python scripts/crd_validator.py --crd config/crd/`, then `python scripts/reconcile_lint.py --controller controllers/` (repeat per controller file).
- **Expected:** a triage-able findings list.
- **On failure:** a tool can't parse a file → confirm it's the expected YAML/Go; corrupt format is itself a finding.

#### Step 3: Triage and record

- **Action:** FAIL → block the release, fix before the next deploy; WARN → open an issue, fix within 30 days. Record the current capability level in the README.
- **Expected:** every finding has an owner and a due date; the README states the level.
- **On failure:** a finding has no owner → assign one before wrapping up; unowned findings inevitably rot.

#### Step 4: Plan advancement

- **Action:** schedule one capability-level advancement per quarter.
- **Expected:** the next-level gap list from Step 1 is the roadmap.
- **On failure:** the gaps don't fit in one quarter → shrink to the smallest subset that advances the level.

### Workflow 3: Choose a framework

#### Step 1: List constraints

- **Action:** note the team's language stack, deployment target (native k8s vs OpenShift), and operator complexity (single CRD / multi-CRD / cluster-scoped).
- **Expected:** three constraints written down.
- **On failure:** conflicting constraints (e.g. Python team + OpenShift-only features) → surface the conflict to the user; it affects the recommendation.

#### Step 2: Match against the landscape

- **Action:** apply the decision rules above; cross-check with `references/tooling_landscape.md`.
- **Expected:** exactly one primary framework, with a rationale.
- **On failure:** two candidates tied → do a 1-week proof-of-concept each before deciding.

## Failure Handling Table

| Symptom / exit code | Cause | Fix |
|---|---|---|
| Validator exit code 2 (missing `--crd`) | No CRD path given | Pass `--crd <file-or-dir>`; use `--format json` in CI |
| Validator: `status subresource` finding | CRD lacks `subresources.status` | Add it; otherwise status updates loop-trigger reconciliation |
| Validator: `x-kubernetes-preserve-unknown-fields` finding | Schema escapes validation | Define concrete types, or narrow the escape hatch to leaf fields |
| Linter: `time.Sleep` finding | Blocking inside reconcile | Replace with `ctrl.Result{RequeueAfter: ...}` |
| Linter: spec `client.Update()` finding | The controller modified the user-owned spec | Use only `r.Status().Update(ctx, obj)` to update status |
| Audited level below expectation | Evidence files missing (PDB, metrics, backup) | Treat the gap list as a work plan; don't hand-edit the score |
| Linter/validator errors parsing input | The file isn't the expected format | Check path/extension; corrupt format is itself a finding |
| `python: command not found` | No interpreter | Install Python ≥ 3.8; all tools use only the standard library |

## References

Read only when the corresponding situation arises:

- `references/operator_pattern.md` — when deciding whether an operator is even the right tool (vs Deployment/Job/Helm).
- `references/crd_design.md` — when designing or versioning a CRD, or fixing schema/conditions/finalizer-related findings.
- `references/reconcile_loop.md` — when writing or fixing a reconcile function, or handling linter findings.
- `references/tooling_landscape.md` — when choosing between frameworks (Workflow 3).

## Slash Commands

`/operator-audit` — run all 3 tools against an operator repo and produce a markdown report.

## Asset Templates

- `assets/crd_template.yaml` — a CRD with status subresource, conditions, finalizer hints, and printer columns
- `assets/reconcile_skeleton.go` — a Go controller reconcile function with idempotence, conditions, finalizer, and requeue patterns

## Anti-patterns

- **`time.Sleep(30 * time.Second)` inside reconcile** — blocks other reconciles. Use `RequeueAfter`.
- **Setting status with `r.Client.Update(ctx, obj)`** — use `r.Status().Update(ctx, obj)` instead.
- **No leader election + 2+ replicas** — split-brain.
- **No finalizer** — external resources become orphans on deletion.
- **CRD without a status subresource** — a status update triggers spec reconciliation (infinite loop).
- **reconcile function > 200 lines** — split out reconcileXxx subroutines by condition.
- **`x-kubernetes-preserve-unknown-fields: true` on the spec root** — disables validation.
- **Imperative reconcile** — "on create do A, on update do B, on delete do C". The shape is wrong. reconcile = make actual=desired, regardless of how it got there.

## Delivery Criteria

This skill counts as done only when:

- All three tools exit cleanly on the target repo: `crd_validator.py` (0 FAIL), `reconcile_lint.py` (0 FAIL), `operator_capability_audit.py` (level reported with gaps listed).
- The audit report (the `/operator-audit` markdown or the tools' text output, e.g. `operator_audit_<date>.md`) goes into the operator repo's `docs/` or is attached to the review.
- The operator's README states the current OperatorHub capability level.
- Ongoing requirement: 100% of new CRDs pass `crd_validator.py` before merge; reconcile functions pass `reconcile_lint.py`; the operator reaches Level 3 (Full Lifecycle) before public release.
