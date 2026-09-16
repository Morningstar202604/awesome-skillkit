---
name: helm-chart-builder
description: "Helm chart development agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw — chart scaffolding, values design, template patterns, dependency management, security hardening, and chart testing. Use when: user wants to create or improve Helm charts, design values.yaml files, implement template helpers, audit chart security (RBAC, network policies, pod security), manage subcharts, or run helm lint/test. 当用户要求 写 Helm chart / K8s 部署清单 时使用。 Do NOT use for deploying charts to a live cluster (template generation only)."
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

> Production-grade Helm charts. Sensible defaults. Secure by design. No cargo-culting.

Opinionated Helm workflow that turns ad-hoc Kubernetes manifests into maintainable, testable, reusable charts. Covers chart structure, values design, template patterns, dependency management, and security hardening.

Not a Helm tutorial — a set of concrete decisions about how to build charts that operators trust and developers don't fight.

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/helm:create` | Scaffold a production-ready Helm chart with best-practice structure |
| `/helm:review` | Analyze an existing chart for issues — missing labels, hardcoded values, template anti-patterns |
| `/helm:security` | Audit chart for security issues — RBAC, network policies, pod security, secrets handling |

## When This Skill Activates

Recognize these patterns from the user:

- "Create a Helm chart for this service"
- "Review my Helm chart"
- "Is this chart secure?"
- "Design a values.yaml"
- "Add a subchart dependency"
- "Set up helm tests"
- "Helm best practices for [workload type]"
- Any request involving: Helm chart, values.yaml, Chart.yaml, templates, helpers, _helpers.tpl, subcharts, helm lint, helm test

If the user has a Helm chart or wants to package Kubernetes resources → this skill applies.

## 输入清单

| Input | Required | Description |
|-------|----------|-------------|
| Chart directory | Required | Existing chart to review/harden, or a name to scaffold |
| Workload type | Required | Web service / worker / CronJob / Stateful service / library chart |
| Image repository & tag source | Required | Registry path and how the tag is supplied (values, appVersion) |
| Ingress / TLS needs | Optional | Hosts, paths, TLS secrets |
| Subchart dependencies | Optional | e.g. postgresql, redis — with version constraints |
| Secrets source | Optional | External secrets operator / sealed-secrets / user-supplied |

Collect missing inputs in one shot: "Please provide: ① the chart directory or a new chart name ② workload type (web service/worker/CronJob/stateful/library) ③ image repository and tag strategy ④ ingress/TLS needs and subchart dependencies ⑤ how secrets are provided. Everything else I'll default per the checklists below."

## 前置自检

Probe before running; on any failure, give the fix and STOP:

```bash
python3 --version   # expect 3.8+; fail: install python3
python3 scripts/chart_analyzer.py --help >/dev/null 2>&1     # expect exit 0; fail: script missing → check skill dir
python3 scripts/values_validator.py --help >/dev/null 2>&1
helm version --short >/dev/null 2>&1   # expect exit 0; fail: helm not installed → install helm CLI or deliver static review only
test -d <chart-dir>/templates   # expect exit 0 for review/security tasks; fail: not a chart → ask user for the chart root
```

## 工作流

### 步骤 1: Identify workload type (`/helm:create`)

- Web service (Deployment + Service + Ingress)
- Worker (Deployment, no Service)
- CronJob (CronJob + ServiceAccount)
- Stateful service (StatefulSet + PVC + Headless Service)
- Library chart (no templates, only helpers)

Expected: workload type confirmed with the user before scaffolding; it decides the template set.

### 步骤 2: Scaffold chart structure

```text
mychart/
├── Chart.yaml              # Chart metadata and dependencies
├── values.yaml             # Default configuration
├── values.schema.json      # Optional: JSON Schema for values validation
├── .helmignore             # Files to exclude from packaging
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
│   ├── NOTES.txt           # Post-install usage instructions
│   └── tests/
│       └── test-connection.yaml
└── charts/                 # Subcharts (dependencies)
```

Apply Chart.yaml best practices:

```text
METADATA
├── apiVersion: v2 (Helm 3 only — never v1)
├── name: matches directory name exactly
├── version: semver (chart version, not app version)
├── appVersion: application version string
├── description: one-line summary of what the chart deploys
└── type: application (or library for shared helpers)

DEPENDENCIES
├── Pin dependency versions with ~X.Y.Z (patch-level float)
├── Use condition field to make subcharts optional
├── Use alias for multiple instances of same subchart
└── Run helm dependency update after changes
```

values.yaml rules: every value has an inline comment; sensible dev defaults; flat where possible; no hardcoded cluster-specific values (registry, domain, storage class).

### 步骤 3: Validate the chart

```bash
python3 scripts/chart_analyzer.py mychart/               # static analysis
python3 scripts/chart_analyzer.py mychart/ --output json
python3 scripts/chart_analyzer.py mychart/ --security
helm lint mychart/
helm template mychart/ --debug
```

Expected: analyzer reports no structural or anti-pattern flags; `helm lint` exits 0; `helm template` renders all resources without errors.
If it fails: template render errors show file/line — fix the named template; lint failures on values → fix defaults in values.yaml.

### 步骤 4: Review an existing chart (`/helm:review`)

Structure checks:

| Check | Severity | Fix |
|-------|----------|-----|
| Missing _helpers.tpl | High | Create helpers for common labels and selectors |
| No NOTES.txt | Medium | Add post-install instructions |
| No .helmignore | Low | Create one to exclude .git, CI files, tests |
| Missing Chart.yaml fields | Medium | Add description, appVersion, maintainers |
| Hardcoded values in templates | High | Extract to values.yaml with defaults |

Template quality checks:

| Check | Severity | Fix |
|-------|----------|-----|
| Missing standard labels | High | Use `app.kubernetes.io/*` labels via _helpers.tpl |
| No resource requests/limits | Critical | Add resources section with defaults in values.yaml |
| Hardcoded image tag | High | Use `{{ .Values.image.repository }}:{{ .Values.image.tag }}` |
| No imagePullPolicy | Medium | Default to `IfNotPresent`, overridable |
| Missing liveness/readiness probes | High | Add probes with configurable paths and ports |
| No pod anti-affinity | Medium | Add preferred anti-affinity for HA |
| Duplicate template code | Medium | Extract into named templates in _helpers.tpl |

Values quality:

```bash
python3 scripts/values_validator.py mychart/values.yaml             # text report
python3 scripts/values_validator.py mychart/values.yaml --output json
python3 scripts/values_validator.py mychart/values.yaml --strict
```

Expected: a review report `HELM CHART REVIEW — <chart name>` with CRITICAL/HIGH/MEDIUM/LOW counts and per-finding fixes; `values_validator --strict` passes.
If it fails: validator flags undocumented or secret-like defaults → fix values.yaml per its output and re-run.

### 步骤 5: Security audit (`/helm:security`)

Pod security:

| Check | Severity | Fix |
|-------|----------|-----|
| No securityContext | Critical | Add runAsNonRoot, readOnlyRootFilesystem |
| Running as root | Critical | Set `runAsNonRoot: true`, `runAsUser: 1000` |
| Writable root filesystem | High | Set `readOnlyRootFilesystem: true` + emptyDir for tmp |
| All capabilities retained | High | Drop ALL, add only specific needed caps |
| Privileged container | Critical | Set `privileged: false`, use specific capabilities |
| No seccomp profile | Medium | Set `seccompProfile.type: RuntimeDefault` |
| allowPrivilegeEscalation true | High | Set `allowPrivilegeEscalation: false` |

RBAC:

| Check | Severity | Fix |
|-------|----------|-----|
| No ServiceAccount | Medium | Create dedicated SA, don't use default |
| automountServiceAccountToken true | Medium | Set to false unless pod needs K8s API access |
| ClusterRole instead of Role | Medium | Use namespace-scoped Role unless cluster-wide needed |
| Wildcard permissions | Critical | Use specific resource names and verbs |
| No RBAC at all | Low | Acceptable if pod doesn't need K8s API access |

Network and secrets:

| Check | Severity | Fix |
|-------|----------|-----|
| No NetworkPolicy | Medium | Add default-deny ingress + explicit allow rules |
| Secrets in values.yaml | Critical | Use external secrets operator or sealed-secrets |
| No PodDisruptionBudget | Medium | Add PDB with minAvailable for HA workloads |
| hostNetwork: true | High | Remove unless absolutely required (e.g., CNI plugin) |
| hostPID or hostIPC | Critical | Never use in application charts |

Expected: a report `SECURITY AUDIT — <chart name>` with severity counts and remediation steps; zero CRITICAL findings before handover.

### 步骤 6: Proactive flags

Flag these without being asked:

- **No _helpers.tpl** → Create one. Every chart needs standard labels and fullname helpers.
- **Hardcoded image tag in template** → Extract to values.yaml. Tags must be overridable.
- **No resource requests/limits** → Add them. Pods without limits can starve the node.
- **Running as root** → Add securityContext. No exceptions for production charts.
- **No NOTES.txt** → Create one. Users need post-install instructions.
- **Secrets in values.yaml defaults** → Remove them. Use placeholders with comments explaining how to provide secrets.
- **No liveness/readiness probes** → Add them. Kubernetes needs to know if the pod is healthy.
- **Missing app.kubernetes.io labels** → Add via _helpers.tpl. Required for proper resource tracking.

## Template Patterns

### Pattern 1: Standard Labels (_helpers.tpl)

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
Selector labels (subset of common labels — must be immutable).
*/}}
{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Pattern 2: Security-Hardened Pod Spec

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

### Pattern 3: Conditional Resources

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
├── Flat over nested (image.tag > container.spec.image.tag)
├── Group by resource (service.*, ingress.*, resources.*)
├── Use enabled: true/false for optional resources
├── Document every key with inline YAML comments
└── Provide sensible development defaults

NAMING
├── camelCase for keys (replicaCount, not replica_count)
├── Boolean keys: use adjectives (enabled, required) not verbs
├── Nested keys: max 3 levels deep
└── Match upstream conventions (image.repository, image.tag, image.pullPolicy)

ANTI-PATTERNS
├── Hardcoded cluster URLs or domains
├── Secrets as default values
├── Empty strings where null is correct
├── Deeply nested structures (>3 levels)
├── Undocumented values
└── values.yaml that doesn't work without overrides
```

## Dependency Management

```text
SUBCHARTS
├── Use Chart.yaml dependencies (not requirements.yaml — Helm 3)
├── Pin versions: version: ~15.x.x (patch float)
├── Use condition: to make optional: condition: postgresql.enabled
├── Use alias: for multiple instances of same chart
├── Override subchart values under subchart name key in values.yaml
└── Run helm dependency update before packaging

LIBRARY CHARTS
├── type: library in Chart.yaml — no templates directory
├── Export named templates only — no rendered resources
├── Use for shared labels, annotations, security contexts
└── Version independently from application charts
```

## 失败处置表

| Symptom / Error | Cause | Fix |
|-----------------|-------|-----|
| `helm template` render error with template name/line | Template syntax or missing helper | Fix the named template in _helpers.tpl; re-run with `--debug` |
| `helm lint` fails on values | Defaults violate chart constraints | Fix values.yaml defaults; re-lint |
| Analyzer flags hardcoded image tag | Template bypasses values | Switch to `{{ .Values.image.repository }}:{{ .Values.image.tag }}` |
| `values_validator --strict` fails | Undocumented keys or secret-like defaults | Apply validator's per-key fixes, re-run |
| `helm dependency update` fails | Chart repo unreachable or version not found | Verify repo URL and `~X.Y.Z` constraint exists; retry or vendor the subchart into `charts/` |
| Chart installs but pods CrashLoopBackOff | Probe/securityContext misconfigured | Check liveness/readiness paths and `runAsNonRoot` vs image user; adjust values |

## 交付标准

Success definition: chart passes `chart_analyzer.py`, `values_validator.py --strict`, `helm lint`, and `helm template`; security audit has zero CRITICAL findings; every value documented with inline comments.
Artifact naming: chart directory named after the chart (matches `Chart.yaml` `name`); review/security reports as `chart_review.md` / `chart_security_audit.md` when written to files.
Save location: chart in the project's `charts/` or `deploy/` folder; reports next to it.
Verify completeness: `helm template` output renders every intended resource for the chosen workload type; NOTES.txt present; test connection hook present in the chart's tests directory; subchart dependencies pinned with conditions.

## 安全红线

- Never deploy (`helm install`/`helm upgrade`) — this skill generates and validates templates only; deployment is the user's action on a live cluster.
- Secrets never default in values.yaml — placeholders only, with comments describing the external secrets source.
- Security contexts are non-negotiable in production charts: runAsNonRoot, readOnlyRootFilesystem, dropped capabilities.

## 参考

- `references/chart-patterns.md` — read for the full template pattern catalog (HPA, PDB, NetworkPolicy, tests) when scaffolding beyond the basics
- `references/values-design.md` — read when designing or refactoring values.yaml structure and naming

## Related Skills

- **senior-devops** — Broader DevOps scope (CI/CD, IaC, monitoring). Complementary — use helm-chart-builder for chart-specific work, senior-devops for pipeline and infrastructure.
- **docker-development** — Container building. Complementary — docker-development builds the images, helm-chart-builder deploys them to Kubernetes.
- **ci-cd-pipeline-builder** — Pipeline construction. Complementary — helm-chart-builder defines the deployment artifact, ci-cd-pipeline-builder automates its delivery.
- **senior-security** — Application security. Complementary — helm-chart-builder covers Kubernetes-level security (RBAC, pod security), senior-security covers application-level threats.

chart 生成后，**接着说："chart 已校验，继续调用 kubernetes-operator 补充控制器/CRD 设计"——链条自动展开**。
