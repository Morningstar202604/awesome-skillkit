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

> 生产级 Helm chart。合理的默认值。默认安全。拒绝照抄。

一套带明确主张的 Helm 工作流，把临时拼凑的 Kubernetes manifests 变成可维护、可测试、可复用的 chart。覆盖 chart 结构、values 设计、模板模式、依赖管理与安全加固。

这不是 Helm 教程——这是一组具体决策，关于如何构建运维信得过、开发不打架的 chart。

## 斜杠命令

| 命令 | 作用 |
|---------|-------------|
| `/helm:create` | 按最佳实践结构生成生产级 Helm chart 脚手架 |
| `/helm:review` | 分析现有 chart 的问题——缺标签、硬编码值、模板反模式 |
| `/helm:security` | 审计 chart 的安全问题——RBAC、网络策略、Pod 安全、密钥处理 |

## 何时激活

识别用户的这些表达：

- "Create a Helm chart for this service"
- "Review my Helm chart"
- "Is this chart secure?"
- "Design a values.yaml"
- "Add a subchart dependency"
- "Set up helm tests"
- "Helm best practices for [workload type]"
- 任何涉及 Helm chart、values.yaml、Chart.yaml、templates、helpers、_helpers.tpl、subcharts、helm lint、helm test 的请求

用户有 Helm chart，或想打包 Kubernetes 资源 → 本技能适用。

## 输入清单

| 输入 | 必需 | 说明 |
|-------|----------|-------------|
| Chart 目录 | 必需 | 要评审/加固的现有 chart，或待生成的名称 |
| 工作负载类型 | 必需 | Web service / worker / CronJob / Stateful service / library chart |
| Image 仓库与 tag 来源 | 必需 | Registry 路径，以及 tag 如何提供（values、appVersion） |
| Ingress / TLS 需求 | 可选 | Hosts、路径、TLS secrets |
| Subchart 依赖 | 可选 | 如 postgresql、redis——带版本约束 |
| 密钥来源 | 可选 | External secrets operator / sealed-secrets / 用户提供 |

缺输入时一次性收集："请一次性提供：① chart 目录或新 chart 名称 ② 工作负载类型（web service/worker/CronJob/stateful/library）③ image 仓库与 tag 策略 ④ ingress/TLS 需求与 subchart 依赖 ⑤ 密钥如何提供。其余我按下方清单给默认值。"

## 前置自检

先探测再动手；任一失败，给出修复方法并停止：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
python3 scripts/chart_analyzer.py --help >/dev/null 2>&1     # 预期退出码 0；失败：脚本缺失 → 检查技能目录
python3 scripts/values_validator.py --help >/dev/null 2>&1
helm version --short >/dev/null 2>&1   # 预期退出码 0；失败：helm 未安装 → 安装 helm CLI，或只交付静态评审
test -d <chart-dir>/templates   # review/security 任务预期退出码 0；失败：不是 chart → 向用户要 chart 根目录
```

## 工作流

### 步骤 1：确定工作负载类型（`/helm:create`）

- Web service（Deployment + Service + Ingress）
- Worker（Deployment，无 Service）
- CronJob（CronJob + ServiceAccount）
- Stateful service（StatefulSet + PVC + Headless Service）
- Library chart（无 templates，只有 helpers）

预期：脚手架生成前与用户确认工作负载类型；它决定模板集合。

### 步骤 2：生成 chart 结构

```text
mychart/
├── Chart.yaml              # Chart 元数据与依赖
├── values.yaml             # 默认配置
├── values.schema.json      # 可选：values 校验用的 JSON Schema
├── .helmignore             # 打包时排除的文件
├── templates/
│   ├── _helpers.tpl        # 命名模板与辅助函数
│   ├── deployment.yaml     # 工作负载资源
│   ├── service.yaml        # Service 暴露
│   ├── ingress.yaml        # Ingress（如适用）
│   ├── serviceaccount.yaml # ServiceAccount
│   ├── hpa.yaml            # HorizontalPodAutoscaler
│   ├── pdb.yaml            # PodDisruptionBudget
│   ├── networkpolicy.yaml  # NetworkPolicy
│   ├── configmap.yaml      # ConfigMap（如需要）
│   ├── secret.yaml         # Secret（如需要）
│   ├── NOTES.txt           # 安装后使用说明
│   └── tests/
│       └── test-connection.yaml
└── charts/                 # Subchart（依赖）
```

套用 Chart.yaml 最佳实践：

```text
METADATA
├── apiVersion: v2（仅 Helm 3——绝不用 v1）
├── name: 与目录名完全一致
├── version: semver（chart 版本，不是应用版本）
├── appVersion: 应用版本字符串
├── description: chart 部署内容的一行摘要
└── type: application（共享 helpers 用 library）

DEPENDENCIES
├── 依赖版本用 ~X.Y.Z 锁定（patch 级浮动）
├── 用 condition 字段让 subchart 可选
├── 同一 subchart 多实例用 alias
└── 变更后运行 helm dependency update
```

values.yaml 规则：每个值都带行内注释；开发默认值合理；能扁平就扁平；不硬编码集群相关值（registry、域名、storage class）。

### 步骤 3：校验 chart

```bash
python3 scripts/chart_analyzer.py mychart/               # 静态分析
python3 scripts/chart_analyzer.py mychart/ --output json
python3 scripts/chart_analyzer.py mychart/ --security
helm lint mychart/
helm template mychart/ --debug
```

预期：分析器无结构或反模式标记；`helm lint` 退出码 0；`helm template` 渲染全部资源无报错。
失败时：模板渲染错误带 file/line——修指定的模板；lint 因 values 失败 → 修 values.yaml 的默认值。

### 步骤 4：评审现有 chart（`/helm:review`）

结构检查：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 缺 _helpers.tpl | High | 为通用标签与选择器建 helpers |
| 无 NOTES.txt | Medium | 补安装后说明 |
| 无 .helmignore | Low | 建一个，排除 .git、CI 文件、tests |
| Chart.yaml 字段缺失 | Medium | 补 description、appVersion、maintainers |
| 模板中硬编码值 | High | 提取到 values.yaml 并给默认值 |

模板质量检查：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 缺标准标签 | High | 经 _helpers.tpl 使用 `app.kubernetes.io/*` 标签 |
| 无 resource requests/limits | Critical | 在 values.yaml 加带默认值的 resources 节 |
| 硬编码 image tag | High | 改用 `{{ .Values.image.repository }}:{{ .Values.image.tag }}` |
| 无 imagePullPolicy | Medium | 默认 `IfNotPresent`，可覆盖 |
| 缺 liveness/readiness 探针 | High | 加探针，路径与端口可配置 |
| 无 Pod 反亲和 | Medium | 为 HA 加 preferred 反亲和 |
| 模板代码重复 | Medium | 提取为 _helpers.tpl 中的命名模板 |

values 质量：

```bash
python3 scripts/values_validator.py mychart/values.yaml             # 文本报告
python3 scripts/values_validator.py mychart/values.yaml --output json
python3 scripts/values_validator.py mychart/values.yaml --strict
```

预期：一份 `HELM CHART REVIEW — <chart name>` 评审报告，带 CRITICAL/HIGH/MEDIUM/LOW 计数与逐项修复；`values_validator --strict` 通过。
失败时：校验器标记未注释的值或疑似密钥的默认值 → 按其输出修 values.yaml 并重跑。

### 步骤 5：安全审计（`/helm:security`）

Pod 安全：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 无 securityContext | Critical | 加 runAsNonRoot、readOnlyRootFilesystem |
| 以 root 运行 | Critical | 设 `runAsNonRoot: true`、`runAsUser: 1000` |
| 根文件系统可写 | High | 设 `readOnlyRootFilesystem: true` + tmp 用 emptyDir |
| 保留全部 capabilities | High | Drop ALL，只加确实需要的 caps |
| 特权容器 | Critical | 设 `privileged: false`，用具体 capabilities |
| 无 seccomp profile | Medium | 设 `seccompProfile.type: RuntimeDefault` |
| allowPrivilegeEscalation true | High | 设 `allowPrivilegeEscalation: false` |

RBAC：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 无 ServiceAccount | Medium | 建专用 SA，不用 default |
| automountServiceAccountToken true | Medium | Pod 不需要访问 K8s API 就设为 false |
| 用 ClusterRole 而非 Role | Medium | 无集群级需求就用 namespace 级 Role |
| 通配权限 | Critical | 用具体资源名与动词 |
| 完全没有 RBAC | Low | Pod 不需要访问 K8s API 时可接受 |

网络与密钥：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 无 NetworkPolicy | Medium | 加 default-deny ingress + 显式 allow 规则 |
| values.yaml 中放密钥 | Critical | 改用 external secrets operator 或 sealed-secrets |
| 无 PodDisruptionBudget | Medium | HA 工作负载加带 minAvailable 的 PDB |
| hostNetwork: true | High | 除非绝对必要（如 CNI plugin）否则移除 |
| hostPID 或 hostIPC | Critical | 应用 chart 中绝不使用 |

预期：一份 `SECURITY AUDIT — <chart name>` 报告，带严重度计数与修复步骤；交付前零 CRITICAL 发现项。

### 步骤 6：主动提示项

无人要求也要指出：

- **无 _helpers.tpl** → 建一个。每个 chart 都需要标准标签与 fullname helpers。
- **模板中硬编码 image tag** → 提取到 values.yaml。tag 必须可覆盖。
- **无 resource requests/limits** → 加上。无限额的 Pod 会饿死节点。
- **以 root 运行** → 加 securityContext。生产 chart 无例外。
- **无 NOTES.txt** → 建一个。用户需要安装后说明。
- **values.yaml 默认值里有密钥** → 删掉。用占位符加注释说明如何提供密钥。
- **无 liveness/readiness 探针** → 加上。Kubernetes 需要判断 Pod 是否健康。
- **缺 app.kubernetes.io 标签** → 经 _helpers.tpl 加上。资源跟踪必需。

## 模板模式

### 模式 1：标准标签（_helpers.tpl）

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

### 模式 2：安全加固的 Pod Spec

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

### 模式 3：条件资源

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

## values 设计原则

```text
STRUCTURE
├── 扁平优先于嵌套（image.tag 优于 container.spec.image.tag）
├── 按资源分组（service.*、ingress.*、resources.*）
├── 可选资源用 enabled: true/false
├── 每个键都用行内 YAML 注释说明
└── 提供合理的开发默认值

NAMING
├── 键用 camelCase（replicaCount，不是 replica_count）
├── 布尔键用形容词（enabled、required），不用动词
├── 嵌套键最多 3 层
└── 对齐上游惯例（image.repository、image.tag、image.pullPolicy）

ANTI-PATTERNS
├── 硬编码集群 URL 或域名
├── 密钥当默认值
├── 该用 null 的地方用空字符串
├── 过深嵌套（>3 层）
├── 无注释的值
└── 不加覆盖就无法工作的 values.yaml
```

## 依赖管理

```text
SUBCHARTS
├── 用 Chart.yaml dependencies（不是 requirements.yaml——Helm 3）
├── 锁版本：version: ~15.x.x（patch 浮动）
├── 用 condition: 让 subchart 可选：condition: postgresql.enabled
├── 同一 chart 多实例用 alias:
├── 在 values.yaml 的 subchart 名称键下覆盖其值
└── 打包前运行 helm dependency update

LIBRARY CHARTS
├── Chart.yaml 里 type: library——无 templates 目录
├── 只导出命名模板——不渲染资源
├── 用于共享标签、annotations、安全上下文
└── 与应用 chart 分开版本化
```

## 失败处置表

| 症状 / 报错 | 原因 | 修复 |
|-----------------|-------|-----|
| `helm template` 渲染错误带模板名/行号 | 模板语法或缺失 helper | 修 _helpers.tpl 中的指定模板；用 `--debug` 重跑 |
| `helm lint` 因 values 失败 | 默认值违反 chart 约束 | 修 values.yaml 默认值；重新 lint |
| 分析器标记硬编码 image tag | 模板绕过了 values | 改用 `{{ .Values.image.repository }}:{{ .Values.image.tag }}` |
| `values_validator --strict` 失败 | 有未注释的键或疑似密钥的默认值 | 按校验器的逐键提示修复，重跑 |
| `helm dependency update` 失败 | chart 仓库不可达或版本不存在 | 核对仓库 URL 与 `~X.Y.Z` 约束；重试，或把 subchart vendor 进 `charts/` |
| chart 装上了但 Pod CrashLoopBackOff | 探针/securityContext 配置不当 | 核对 liveness/readiness 路径与 `runAsNonRoot` 同镜像用户的关系；调整 values |

## 交付标准

成功定义：chart 通过 `chart_analyzer.py`、`values_validator.py --strict`、`helm lint` 与 `helm template`；安全审计零 CRITICAL 发现项；每个值都有行内注释。
产物命名：chart 目录以 chart 名命名（与 `Chart.yaml` 的 `name` 一致）；评审/安全报告落盘时为 `chart_review.md` / `chart_security_audit.md`。
保存位置：chart 放项目的 `charts/` 或 `deploy/` 目录；报告放旁边。
完整性验证：`helm template` 输出渲染出所选工作负载类型的全部预期资源；有 NOTES.txt；chart 的 tests 目录有连接测试 hook；subchart 依赖带版本锁定与 condition。

## 安全红线

- 绝不部署（`helm install`/`helm upgrade`）——本技能只生成与校验模板；部署是用户在真实集群上的动作。
- 密钥绝不作为 values.yaml 默认值——只放占位符，配注释说明外部密钥来源。
- 生产 chart 的安全上下文不可妥协：runAsNonRoot、readOnlyRootFilesystem、drop capabilities。

## 参考

- `references/chart-patterns.md` —— 脚手架超出基础范围时读完整模板模式目录（HPA、PDB、NetworkPolicy、tests）
- `references/values-design.md` —— 设计或重构 values.yaml 结构与命名时

## 相关技能

- **senior-devops** —— 更宽的 DevOps 范围（CI/CD、IaC、监控）。互补——chart 专项用 helm-chart-builder，流水线与基础设施用 senior-devops。
- **docker-development** —— 容器构建。互补——docker-development 构建镜像，helm-chart-builder 把它们部署到 Kubernetes。
- **ci-cd-pipeline-builder** —— 流水线构建。互补——helm-chart-builder 定义部署产物，ci-cd-pipeline-builder 自动化其交付。
- **senior-security** —— 应用安全。互补——helm-chart-builder 覆盖 Kubernetes 层安全（RBAC、Pod 安全），senior-security 覆盖应用层威胁。

chart 生成后，**接着说："chart 已校验，继续调用 kubernetes-operator 补充控制器/CRD 设计"——链条自动展开**。
