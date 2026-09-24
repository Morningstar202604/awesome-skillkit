---
name: helm-chart-builder
description: "Helm chart development agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw — chart scaffolding, values design, template patterns, dependency management, security hardening, and chart testing. Use when: the user wants to write a Helm chart, write K8s deployment manifests, create or improve Helm charts, design values.yaml files, implement template helpers, audit chart security (RBAC, network policies, pod security), manage subcharts, or run helm lint/test. Do NOT use for deploying charts to a live cluster (template generation only)."
license: Apache-2.0
compatibility: Requires helm CLI for lint/template; network only for `helm dependency update`. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: containers
  pattern: pipeline-builder
  tier: powerful
  verified-date: "2026-09-09"
---

# Helm Chart Builder

> Production-grade Helm charts. Sensible defaults. Secure by default. No copy-paste.

A Helm workflow with strong opinions, turning ad-hoc Kubernetes manifests into maintainable, testable, reusable charts. It covers chart structure, values design, template patterns, dependency management, and security hardening.

This isn't a Helm tutorial — it's a set of concrete decisions about how to build charts that ops trusts and developers don't fight over.

## Slash Commands

| Command | Effect |
|---------|-------------|
| `/helm:create` | Generate a production-grade Helm-chart scaffold per best-practice structure |
| `/helm:review` | Analyze an existing chart for problems — missing labels, hardcoded values, template anti-patterns |
| `/helm:security` | Audit a chart's security issues — RBAC, network policies, pod security, secret handling |

## When to Activate

Recognize these phrasings from the user:

- "Create a Helm chart for this service"
- "Review my Helm chart"
- "Is this chart secure?"
- "Design a values.yaml"
- "Add a subchart dependency"
- "Set up helm tests"
- "Helm best practices for [workload type]"
- Any request involving Helm charts, values.yaml, Chart.yaml, templates, helpers, _helpers.tpl, subcharts, helm lint, helm test

The user has a Helm chart, or wants to package Kubernetes resources → this skill applies.

## Input Checklist

| Input | Required | Description |
|-------|----------|-------------|
| Chart directory | Required | The existing chart to review/harden, or the name to generate |
| Workload type | Required | Web service / worker / CronJob / stateful service / library chart |
| Image repo and tag source | Required | The registry path, and how the tag is supplied (values, appVersion) |
| Ingress / TLS needs | Optional | Hosts, paths, TLS secrets |
| Subchart dependencies | Optional | e.g. postgresql, redis — with version constraints |
| Secret source | Optional | External secrets operator / sealed-secrets / user-provided |

When inputs are missing, collect them all at once: "Please provide all at once: (1) the chart directory or new chart name, (2) workload type (web service/worker/CronJob/stateful/library), (3) image repo and tag strategy, (4) ingress/TLS needs and subchart dependencies, (5) how secrets are supplied. Everything else I default per the checklist below."

## Pre-flight Checks

Probe first, then act; on any failure, give the fix and stop:

```bash
python3 --version   # expected 3.8+; on failure: install python3
# Self-check: python3 scripts/chart_analyzer.py --help and values_validator.py --help should both exit 0
helm version --short >/dev/null 2>&1   # expected exit code 0; on failure: helm not installed → install the helm CLI, or deliver a static review only
test -d <chart-dir>/templates   # expected exit code 0 for review/security tasks; on failure: not a chart → ask the user for the chart root
```

## Workflow

### Step 1: Determine the workload type (`/helm:create`)

- Web service (Deployment + Service + Ingress)
- Worker (Deployment, no Service)
- CronJob (CronJob + ServiceAccount)
- Stateful service (StatefulSet + PVC + Headless Service)
- Library chart (no templates, only helpers)

Expected: confirm the workload type with the user before scaffolding; it determines the template set.

### Step 2: Generate the chart structure

```text
mychart/
├── Chart.yaml              # Chart metadata and dependencies
├── values.yaml             # Default configuration
├── values.schema.json      # Optional: JSON Schema for validating values
├── .helmignore             # Files excluded when packaging
├── templates/
│   ├── _helpers.tpl        # Named templates and helper functions
│   ├── deployment.yaml     # Workload resource
│   ├── service.yaml        # Service exposure
│   ├── ingress.yaml        # Ingress (if applicable)
│   ├── serviceaccount.yaml # ServiceAccount
│   ├── hpa.yaml            # HorizontalPodAutoscaler
│   ├── pdb.yaml            # PodDisruptionBudget
│   ├── networkpolicy.yaml  # NetworkPolicy
│   ├── configmap.yaml      # ConfigMap (if needed)
│   ├── secret.yaml         # Secret (if needed)
│   ├── NOTES.txt           # Post-install usage notes
│   └── tests/
│       └── test-connection.yaml
└── charts/                 # Subcharts (dependencies)
```

Apply Chart.yaml best practices:

```text
METADATA
├── apiVersion: v2 (Helm 3 only — never v1)
├── name: exactly matches the directory name
├── version: semver (the chart version, not the app version)
├── appVersion: the app version string
├── description: a one-line summary of what the chart deploys
└── type: application (library for shared helpers)

DEPENDENCIES
├── Pin dependency versions with ~X.Y.Z (patch-level floating)
├── Use a condition field to make subcharts optional
├── Use alias for multiple instances of the same subchart
└── Run helm dependency update after changes
```

values.yaml rules: every value has an inline comment; dev defaults are sensible; flatten when possible; don't hardcode cluster-specific values (registry, domain, storage class).

### Step 3: Validate the chart

```bash
python3 scripts/chart_analyzer.py examples/mychart/               # bundled sample chart; swap in mychart/ for your real project
python3 scripts/chart_analyzer.py examples/mychart/ --output json
python3 scripts/chart_analyzer.py examples/mychart/ --security
helm lint mychart/
helm template mychart/ --debug
```

Expected: the analyzer has no structural or anti-pattern flags; `helm lint` exits 0; `helm template` renders all resources without errors.
On failure: a template-render error with file/line — fix the named template; lint fails on values — fix the defaults in values.yaml.

### Step 4: Review an existing chart (`/helm:review`)

Structural checks:

| Check | Severity | Fix |
|-------|----------|-----|
| Missing _helpers.tpl | High | Build helpers for common labels and selectors |
| No NOTES.txt | Medium | Add post-install notes |
| No .helmignore | Low | Create one, excluding .git, CI files, tests |
| Missing Chart.yaml fields | Medium | Add description, appVersion, maintainers |
| Hardcoded values in templates | High | Extract to values.yaml with defaults |

Template-quality checks:

| Check | Severity | Fix |
|-------|----------|-----|
| Missing standard labels | High | Use `app.kubernetes.io/*` labels via _helpers.tpl |
| No resource requests/limits | Critical | Add a resources section with defaults in values.yaml |
| Hardcoded image tag | High | Switch to `{{ .Values.image.repository }}:{{ .Values.image.tag }}` |
| No imagePullPolicy | Medium | Default `IfNotPresent`, overridable |
| Missing liveness/readiness probes | High | Add probes with configurable path and port |
| No Pod anti-affinity | Medium | Add preferred anti-affinity for HA |
| Duplicated template code | Medium | Extract into named templates in _helpers.tpl |

Values quality:

```bash
python3 scripts/values_validator.py examples/mychart/values.yaml             # bundled sample values
python3 scripts/values_validator.py mychart/values.yaml --output json
python3 scripts/values_validator.py mychart/values.yaml --strict
```

Expected: a review report in the format `HELM CHART REVIEW — <chart name>` with CRITICAL/HIGH/MEDIUM/LOW counts and per-item fixes; `values_validator --strict` passes.
On failure: the validator flags uncommented values or secret-looking defaults → fix values.yaml per its output and rerun.

### Step 5: Security audit (`/helm:security`)

Pod security:

| Check | Severity | Fix |
|-------|----------|-----|
| No securityContext | Critical | Add runAsNonRoot, readOnlyRootFilesystem |
| Running as root | Critical | Set `runAsNonRoot: true`, `runAsUser: 1000` |
| Writable root filesystem | High | Set `readOnlyRootFilesystem: true` + emptyDir for tmp |
| All capabilities retained | High | Drop ALL, add only the caps actually needed |
| Privileged container | Critical | Set `privileged: false`, use specific capabilities |
| No seccomp profile | Medium | Set `seccompProfile.type: RuntimeDefault` |
| allowPrivilegeEscalation true | High | Set `allowPrivilegeEscalation: false` |

RBAC:

| Check | Severity | Fix |
|-------|----------|-----|
| No ServiceAccount | Medium | Create a dedicated SA, don't use default |
| automountServiceAccountToken true | Medium | Set false when the Pod doesn't need the K8s API |
| Using ClusterRole instead of Role | Medium | Use a namespace-scoped Role when there's no cluster-level need |
| Wildcard permissions | Critical | Use concrete resource names and verbs |
| No RBAC at all | Low | Acceptable when the Pod doesn't need the K8s API |

Networking and secrets:

| Check | Severity | Fix |
|-------|----------|-----|
| No NetworkPolicy | Medium | Add default-deny ingress + explicit allow rules |
| Secrets in values.yaml | Critical | Use an external secrets operator or sealed-secrets instead |
| No PodDisruptionBudget | Medium | Add a PDB with minAvailable for HA workloads |
| hostNetwork: true | High | Remove unless absolutely necessary (e.g. a CNI plugin) |
| hostPID or hostIPC | Critical | Never use in application charts |

Expected: a report in the format `SECURITY AUDIT — <chart name>` with severity counts and fix steps; zero CRITICAL findings before delivery.

### Step 6: Proactive callouts

Point these out even when nobody asks:

- **No _helpers.tpl** → create one. Every chart needs standard labels and fullname helpers.
- **Hardcoded image tag in templates** → extract to values.yaml. The tag must be overridable.
- **No resource requests/limits** → add them. An unlimited Pod starves the node.
- **Running as root** → add a securityContext. No exceptions in production charts.
- **No NOTES.txt** → create one. Users need post-install notes.
- **Secrets in values.yaml defaults** → delete them. Use a placeholder with a comment explaining how to supply the secret.
- **No liveness/readiness probes** → add them. Kubernetes needs to know whether the Pod is healthy.
- **Missing app.kubernetes.io labels** → add them via _helpers.tpl. Required for resource tracking.

## Template Patterns

### Pattern 1: Standard labels (_helpers.tpl)

```yaml
{{/*
Common labels for all resources.
*/}}
{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.chart" . }}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels (a subset of common labels — must be immutable).
*/}}
{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Pattern 2: A hardened Pod spec

```yaml
spec:
  serviceAccountName: {{ include "mychart.serviceAccountName" . }}
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: {{ .Chart.Name }}
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
      image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
      imagePullPolicy: {{ .Values.image.pullPolicy }}
      resources:
        {{- toYaml .Values.resources | nindent 8 }}
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

### Pattern 3: Conditional resources

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "mychart.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

## Values Design Principles

```text
STRUCTURE
├── Flat over nested (image.tag beats container.spec.image.tag)
├── Group by resource (service.*, ingress.*, resources.*)
├── Use enabled: true/false for optional resources
├── Comment every key with an inline YAML comment
└── Provide sensible dev defaults

NAMING
├── Use camelCase keys (replicaCount, not replica_count)
├── Boolean keys use adjectives (enabled, required), not verbs
├── At most 3 levels of nesting
└── Align with upstream conventions (image.repository, image.tag, image.pullPolicy)

ANTI-PATTERNS
├── Hardcoded cluster URLs or domains
├── Secrets as defaults
├── Empty strings where null is meant
├── Too-deep nesting (>3 levels)
├── Uncommented values
└── A values.yaml that doesn't work without overrides
```

## Dependency Management

```text
SUBCHARTS
├── Use Chart.yaml dependencies (not requirements.yaml — Helm 3)
├── Pin versions: version: ~15.x.x (patch floating)
├── Make subcharts optional with a condition: postgresql.enabled
├── Use alias for multiple instances of the same chart
├── Override a subchart's values under its name key in values.yaml
└── Run helm dependency update before packaging

LIBRARY CHARTS
├── type: library in Chart.yaml — no templates directory
├── Export only named templates — don't render resources
├── Use for shared labels, annotations, security contexts
└── Version separately from application charts
```

## Failure Handling Table

| Symptom / error | Cause | Fix |
|-----------------|-------|-----|
| `helm template` render error with template name/line | Template syntax or a missing helper | Fix the named template in _helpers.tpl; rerun with `--debug` |
| `helm lint` fails on values | Defaults violate a chart constraint | Fix the defaults in values.yaml; re-lint |
| The analyzer flags a hardcoded image tag | A template bypassed values | Switch to `{{ .Values.image.repository }}:{{ .Values.image.tag }}` |
| `values_validator --strict` fails | An uncommented key or secret-looking default | Fix per the validator's per-key hints and rerun |
| `helm dependency update` fails | The chart repo is unreachable or the version doesn't exist | Check the repo URL and the `~X.Y.Z` constraint; retry, or vendor the subchart into `charts/` |
| The chart installs but Pods CrashLoopBackOff | Misconfigured probes/securityContext | Check the liveness/readiness paths and the relationship of `runAsNonRoot` to the image user; adjust values |

## Delivery Criteria

Definition of success: the chart passes `chart_analyzer.py`, `values_validator.py --strict`, `helm lint`, and `helm template`; the security audit has zero CRITICAL findings; every value has an inline comment.
Artifact naming: the chart directory is named after the chart (matching `Chart.yaml`'s `name`); review/security reports are written as `chart_review.md` / `chart_security_audit.md`.
Save location: the chart goes in the project's `charts/` or `deploy/` directory; reports go beside it.
Completeness verification: `helm template` output renders all expected resources for the chosen workload type; there's a NOTES.txt; the chart's tests directory has a connection-test hook; subchart dependencies have version pins and a condition.

## Safety Red Lines

- Never deploy (`helm install`/`helm upgrade`) — this skill only generates and validates templates; deployment is the user's action on a real cluster.
- Secrets never go in values.yaml defaults — only a placeholder, with a comment explaining the external secret source.
- A production chart's security context is non-negotiable: runAsNonRoot, readOnlyRootFilesystem, dropped capabilities.

## References

- `references/chart-patterns.md` — read for the full template-pattern catalog (HPA, PDB, NetworkPolicy, tests) when scaffolding goes beyond the basics
- `references/values-design.md` — when designing or refactoring the values.yaml structure and naming

## Related Skills

- **senior-devops** — broader DevOps scope (CI/CD, IaC, monitoring). Complementary — use helm-chart-builder for chart specifics, senior-devops for pipelines and infrastructure.
- **docker-development** — container building. Complementary — docker-development builds images, helm-chart-builder deploys them to Kubernetes.
- **ci-cd-pipeline-builder** — pipeline building. Complementary — helm-chart-builder defines the deployment artifact, ci-cd-pipeline-builder automates its delivery.
- **senior-security** — application security. Complementary — helm-chart-builder covers the Kubernetes layer (RBAC, pod security), senior-security covers app-layer threats.

Once the chart is generated, **then say: "The chart is validated; next, call kubernetes-operator to add the controller/CRD design" — the chain unfolds automatically**.
