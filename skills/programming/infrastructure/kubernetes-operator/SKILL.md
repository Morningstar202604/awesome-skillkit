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

构建调谐正确的 Operator。多数 operator 问题不是 Kubernetes 的问题，而是调谐循环的问题：finalizer 缺失、阻塞调用、瞬态错误不 requeue、status 漂移、RBAC 过度授权。本技能用确定性手段在代码进集群之前拦住它们。

## 何时使用

- 构建新的 Kubernetes Operator（CRD 的控制器）
- 审查现有 operator 的能力等级缺口
- 审计 CRD spec 的 status/conditions/finalizer 正确性
- 选型框架（controller-runtime / kubebuilder / operator-sdk / metacontroller / KOPF）
- 设计 Custom Resource 的 API 面
- 加固 RBAC、leader 选举或 webhook 校验

## 何时不使用

- 纯 Helm chart 打包 → 用 `helm-chart-builder`
- 常规 kubectl 操作 / 蓝绿发布 → 用 `senior-devops`
- 泛用 k8s 安全态势 → 用 `cloud-security`
- "我只是想跑个负载" —— 那是 Deployment / Job，不是 operator

## 输入清单

开工前一次性收集。缺输入时用这句话向用户问一次："要审计/构建 Operator，请一次性提供：operator 仓库路径、CRD YAML 路径、controller Go 源文件路径、目标语言/框架（如已定）。"

| 输入 | 必需 | 说明 |
|---|---|---|
| Operator 仓库根目录 | 是（audit/bootstrap） | 包含 `config/`、`controllers/`、`api/` 的目录 → `--operator-dir` |
| CRD YAML 文件或目录 | 是（CRD 检查） | 用户 operator 仓库中的 config/crd/myapp.yaml → `--crd` |
| Go controller 源码 | 是（reconcile lint） | 如 `controllers/myapp_controller.go` → `--controller` |
| Group/Version/Kind | 是（新 operator） | 如 `apps.example.com/v1alpha1`，kind `MyApp` |
| 语言/框架约束 | 用于框架选型 | Go / Python / Java / 多语言；见工具选型全景 |

## 前置自检

```bash
python3 --version        # 预期：Python ≥ 3.8。3 个工具全部仅依赖标准库。
ls scripts/crd_validator.py scripts/reconcile_lint.py scripts/operator_capability_audit.py
                         # 预期：3 个文件全部列出。
```

- Python 缺失或版本过旧 → 安装 Python ≥ 3.8，然后停止。
- 脚本文件缺失 → 目录不对；`cd` 到本技能目录重新检查，然后停止。
- 审计现有 operator？再跑 `ls <operator-dir>/config/crd/ <operator-dir>/controllers/` —— 预期：至少一个 CRD YAML 和一个控制器 `.go` 文件。缺失 → 与用户确认仓库布局后再继续（不要猜路径）。

## 核心原则：operator 是调谐循环，不是脚本

```text
observe(actual) → desired = read(spec) → diff(actual, desired) → act → update(status)
                                                                          ↓
                                                                   requeue / done
```

失败的 operator 通常是这样：

1. 把 reconcile 当命令式脚本（先做这个，再做这个）而不是声明式（幂等地让 actual=desired）
2. 瞬态失败不 requeue
3. 不用 finalizer，留下孤儿资源
4. 改 spec 而不是改 status
5. 不用 status 子资源（status 更新会触发 spec 调谐 → 死循环）
6. reconcile 内阻塞（长 HTTP 调用、锁）
7. 忘了 leader 选举 → 多副本部署时脑裂

下面 3 个工具逐一拦住这些问题。

## 快速开始

```bash
# 以下命令在技能目录（skills/programming/infrastructure/kubernetes-operator/）内执行

# 校验 CRD 设计
python scripts/crd_validator.py --crd assets/config/crd/myapp.yaml

# lint 一个 Go reconcile 函数
python scripts/reconcile_lint.py --controller assets/controllers/myapp_controller.go

# 按 OperatorHub Capability Levels（1-5）打分
python scripts/operator_capability_audit.py --operator-dir assets/
```

## 三个 Python 工具

全部仅依赖标准库。用 `--help` 查看用法。

### `crd_validator.py`

按 operator 模式最佳实践校验 CRD YAML。

```bash
python scripts/crd_validator.py --crd assets/config/crd/myapp.yaml   # 随包样例 CRD
python scripts/crd_validator.py --crd assets/config/crd/ --format json
```

**检查项：**

- `spec.versions[*].subresources.status` 已设置（status 子资源）
- `spec.scope` 为 `Namespaced`（不是 `Cluster`），除非有明确理由
- 单数形式与 listKind 已定义
- `spec.versions[*].schema.openAPIV3Schema` 有类型定义（顶层不允许 `x-kubernetes-preserve-unknown-fields: true`）
- 至少一个版本标记 `served: true` 且 `storage: true`
- schema 中包含 Conditions 数组（兼容 `metav1.Conditions`）
- Printer columns 包含 `Age` 与 `Status`/`Phase`

### `reconcile_lint.py`

lint Go 控制器的 reconcile 函数，查反模式。

```bash
python scripts/reconcile_lint.py --controller assets/controllers/myapp_controller.go   # 随包样例 controller
```

**检查项（基于正则启发式）：**

- 返回值是 `(ctrl.Result, error)` 形状
- 错误触发非零 requeue（`return ctrl.Result{Requeue: true}, err`）
- 对 spec 对象调用 `client.Update()` 会被标记（控制器只应更新 status）
- reconcile 内出现 `time.Sleep` 会被标记（改用 `RequeueAfter`）
- 无 context 取消的 HTTP 调用会被标记
- 添加 finalizer 后缺少 `defer`
- CRD 里有 conditions 却没有 `IsConditionTrue` / `SetCondition` 调用
- reconcile 函数超过 80 行（拆分子例程）

### `operator_capability_audit.py`

按 OperatorHub 的 5 个能力等级给 operator 打分。

```bash
python scripts/operator_capability_audit.py --operator-dir .
```

**等级：**

- **L1 — Basic Install：** 定义 CRD，控制器负责部署
- **L2 — Seamless Upgrades：** PDB、conversion webhook、版本偏差策略
- **L3 — Full Lifecycle：** 备份、恢复、故障还原
- **L4 — Deep Insights：** 指标端点、Prometheus 规则、告警
- **L5 — Auto Pilot：** 自动扩缩、自动调优、异常检测

报告当前等级 + 晋级的具体下一步。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `--crd` | CRD YAML 文件或目录路径 | 校验器；目录会递归扫描 |
| `--controller` | Go 源文件路径 | linter；正则启发式，不是 Go AST 解析器 |
| `--operator-dir` | operator 仓库根目录 | 能力审计；遍历检测 L1–L5 证据 |
| `--format` | `text` / `json`（3 个工具都支持） | JSON 用于 CI 流水线与 diff |

## 工具选型全景

按语言和复杂度选框架。详见 `references/tooling_landscape.md`。

| 框架 | 语言 | 最适合 | 维护状态 |
|---|---|---|---|
| **controller-runtime** | Go | 生产级、底层可控 | 活跃（sig-api-machinery） |
| **kubebuilder** | Go | 标准脚手架、约定优先 | 活跃（Kubernetes SIGs） |
| **operator-sdk** | Go / Helm / Ansible | OpenShift / 混合范式团队 | 活跃（Red Hat） |
| **metacontroller** | 任意（基于 webhook） | 多语言团队、避开 Go | 不太活跃 |
| **KOPF** | Python | Python 团队、async 优先 | 活跃（社区） |
| **java-operator-sdk** | Java | JVM 团队 | 活跃（Red Hat / Java SIG） |

决策规则：

- 新 operator + Go 团队 → kubebuilder
- 新 operator + Python 团队 → KOPF
- 新 operator + 语言未定 → metacontroller
- 目标是 OpenShift → operator-sdk

## CRD 设计原则

详见 `references/crd_design.md`。速记规则：

1. **status 是控制器对世界认知的事实来源。** spec 是用户想要的；status 是控制器观测到的。
2. **启用 status 子资源。** 否则 status 更新会再次触发调谐（死循环）。
3. **用 Conditions。** `Ready`、`Reconciling`、`Degraded`，每个都带 reason 和 message。
4. **加 finalizer。** 没有 finalizer，删除会和控制器赛跑，外部资源成为孤儿。
5. **从第 1 天起就做 CRD 版本化。** `v1alpha1` → `v1beta1` → `v1`，规划 conversion webhook。
6. **用 OpenAPI v3 schema 校验。** 该在准入阶段失败的校验，不要指望控制器兜底。
7. **用 `additionalPrinterColumns` 优化 `kubectl get`。** 至少展示 `Age`、`Phase`、`Ready`。
8. **CRD 用 Namespaced，除非它管理集群级资源。**

## 调谐循环原则

详见 `references/reconcile_loop.md`。速记规则：

1. **幂等。** 同一状态调谐两次 → 结果相同，零副作用。
2. **读一次、决策、行动。** 调谐过程中不要反复观察世界。
3. **更新 status，不更新 spec。** spec 属于用户。
4. **返回能触发 requeue 的错误。** 已知瞬态场景用 `ctrl.Result{RequeueAfter: ...}`。
5. **绝不阻塞。** 不用 `time.Sleep`，不做无 context 的长 HTTP 调用。
6. **用缓存。** 通过控制器的缓存 client 读取；有明确理由才绕过缓存。
7. **多副本必须 leader 选举。** 否则启用单副本模式。
8. **设置 OwnerReferences。** 级联删除是 operator 模式的免费馈赠。

## 工作流

### 工作流 1：从零搭建 operator（Go + kubebuilder）

#### 步骤 1：定下 API 形状

- **动作：** 确定 Group/Version/Kind，如 `apps.example.com/v1alpha1`，kind `MyApp`。
- **预期：** 用户确认过的一行 API 声明。
- **失败时：** 用户拿不准 → 问一次；不要编造 group domain。

#### 步骤 2：用 kubebuilder 生成脚手架

- **动作：** `kubebuilder init --domain example.com --repo github.com/org/myapp-operator && kubebuilder create api --group apps --version v1alpha1 --kind MyApp`
- **预期：** config/crd/bases/apps.example.com_myapps.yaml 与 `controllers/myapp_controller.go` 存在。
- **失败时：** kubebuilder 未安装 → 安装（见 kubebuilder 文档）后停止；不要手写脚手架。

#### 步骤 3：校验生成的 CRD

- **动作：** `python scripts/crd_validator.py --crd config/crd/bases/apps.example.com_myapps.yaml`
- **预期：** 无 FAIL（全新脚手架常出现 printer columns/conditions 的 WARN，属正常）。
- **失败时：** 修完每一项（补 status 子资源、conditions、printer columns）—— 从 `assets/crd_template.yaml` 起步 —— 重跑直到干净。

#### 步骤 4：实现 reconcile 函数

- **动作：** 先写最简单的正确版本：读期望状态、diff、行动、更新 status。
- **预期：** 函数可编译；无 `time.Sleep`；status 经 `r.Status().Update` 更新。
- **失败时：** 逻辑像命令式（"如果是创建就做 A"）→ 按 `references/reconcile_loop.md` 重塑为"让 actual=desired"。

#### 步骤 5：lint 控制器

- **动作：** `python scripts/reconcile_lint.py --controller assets/controllers/myapp_controller.go   # 随包样例 controller`
- **预期：** 零 FAIL；函数 ≤80 行。
- **失败时：** 按每项提示修复（用 `RequeueAfter` 替代 sleep，用 `Status().Update` 替代 `Update`），重跑直到干净。

#### 步骤 6：审计能力等级

- **动作：** `python scripts/operator_capability_audit.py --operator-dir .`
- **预期：** 至少报告 L1 并列出具体下一步。
- **失败时：** 低于 L1 → 缺 CRD 或 Deployment manifest；先补完脚手架。

#### 步骤 7：在一次性集群里冒烟测试

- **动作：** 对 kind 集群 `kubectl apply -f config/samples/`；观察 `kubectl get myapps` 出现 conditions。
- **预期：** 示例资源变为 `Ready=True`，日志中无控制器错误循环。
- **失败时：** 日志出现无限调谐循环 → 回到步骤 4；不要继续部署。

### 工作流 2：审计现有 operator

#### 步骤 1：给仓库打分

- **动作：** `python scripts/operator_capability_audit.py --operator-dir <path>`
- **预期：** 得到等级（1–5）与晋级的缺口清单。
- **失败时：** 目录不对（找不到 CRD）→ 与用户确认仓库根目录。

#### 步骤 2：校验 CRD 并 lint 控制器

- **动作：** `python scripts/crd_validator.py --crd config/crd/`，然后 `python scripts/reconcile_lint.py --controller controllers/`（每个控制器文件重复）。
- **预期：** 得到可分诊的发现清单。
- **失败时：** 工具无法解析某文件 → 确认它是预期的 YAML/Go；格式损坏本身就是一个发现项。

#### 步骤 3：分诊并记录

- **动作：** FAIL → 阻断发布，下次部署前修复；WARN → 开 issue，30 天内修复。在 README 记录当前能力等级。
- **预期：** 每个发现项有负责人和截止日期；README 写明等级。
- **失败时：** 发现项没有负责人 → 收尾前先指派；无主发现项必然烂掉。

#### 步骤 4：规划晋级

- **动作：** 每季度安排一次能力等级晋级。
- **预期：** 步骤 1 输出的下一等级缺口清单即路线图。
- **失败时：** 缺口一个季度吃不下 → 缩到能推进等级的最小子集。

### 工作流 3：选框架

#### 步骤 1：列出约束

- **动作：** 记下团队语言栈、部署目标（原生 k8s 还是 OpenShift）、operator 复杂度（单 CRD / 多 CRD / 集群级）。
- **预期：** 写下三条约束。
- **失败时：** 约束冲突（如 Python 团队 + 仅 OpenShift 特性）→ 把冲突摆给用户；它会影响推荐。

#### 步骤 2：对照全景匹配

- **动作：** 套用上面的决策规则；与 `references/tooling_landscape.md` 交叉核对。
- **预期：** 恰好一个主框架，且给出理由。
- **失败时：** 两个候选打平 → 各做 1 周 proof-of-concept 再定。

## 失败处置表

| 症状 / 退出码 | 原因 | 修复 |
|---|---|---|
| Validator 退出码 2（缺 `--crd`） | 未给 CRD 路径 | 传 `--crd <file-or-dir>`；CI 中用 `--format json` |
| Validator：`status subresource` 发现项 | CRD 缺 `subresources.status` | 补上；否则 status 更新会循环触发调谐 |
| Validator：`x-kubernetes-preserve-unknown-fields` 发现项 | schema 逃避了校验 | 定义具体类型，或把逃生口收窄到叶子字段 |
| Linter：`time.Sleep` 发现项 | reconcile 内阻塞 | 换成 `ctrl.Result{RequeueAfter: ...}` |
| Linter：spec `client.Update()` 发现项 | 控制器改了用户所有的 spec | 只用 `r.Status().Update(ctx, obj)` 更新 status |
| 审计等级低于预期 | 证据文件缺失（PDB、指标、备份） | 把缺口清单当工作计划；不要手改分数 |
| Linter/validator 解析输入报错 | 文件不是预期格式 | 核对路径/扩展名；格式损坏本身就是一个发现项 |
| `python: command not found` | 无解释器 | 安装 Python ≥ 3.8；所有工具仅依赖标准库 |

## 参考

仅在对应情况出现时读：

- `references/operator_pattern.md` —— 判断 operator 是否本就是对的工具时（对比 Deployment/Job/Helm）。
- `references/crd_design.md` —— 设计或版本化 CRD，或修复 schema/conditions/finalizer 相关发现项时。
- `references/reconcile_loop.md` —— 写或修 reconcile 函数，或处理 linter 发现项时。
- `references/tooling_landscape.md` —— 在框架之间选型时（工作流 3）。

## 斜杠命令

`/operator-audit` —— 对 operator 仓库跑全部 3 个工具，产出 markdown 报告。

## 资产模板

- `assets/crd_template.yaml` —— 带 status 子资源、conditions、finalizer 提示、printer columns 的 CRD
- `assets/reconcile_skeleton.go` —— 带幂等、conditions、finalizer、requeue 模式的 Go 控制器 reconcile 函数

## 反模式

- **reconcile 内 `time.Sleep(30 * time.Second)`** —— 阻塞其他调谐。用 `RequeueAfter`。
- **用 `r.Client.Update(ctx, obj)` 设 status** —— 改用 `r.Status().Update(ctx, obj)`。
- **无 leader 选举 + 2 副本以上** —— 脑裂。
- **无 finalizer** —— 删除时外部资源成为孤儿。
- **CRD 无 status 子资源** —— status 更新触发 spec 调谐（无限循环）。
- **reconcile 函数 > 200 行** —— 按 condition 拆出 reconcileXxx 子例程。
- **spec 根上 `x-kubernetes-preserve-unknown-fields: true`** —— 让校验失效。
- **命令式 reconcile** —— "创建做 A、更新做 B、删除做 C"。形状就错了。reconcile = 让 actual=desired，无论怎么走到这一步。

## 交付标准

满足以下条件才算跑完本技能：

- 三个工具在目标仓库全部干净退出：`crd_validator.py`（0 FAIL）、`reconcile_lint.py`（0 FAIL）、`operator_capability_audit.py`（报告等级并列明缺口）。
- 审计报告（`/operator-audit` 的 markdown 或工具文本输出，如 `operator_audit_<date>.md`）存进 operator 仓库的 `docs/` 或附在评审中。
- operator 的 README 写明当前 OperatorHub 能力等级。
- 持续要求：100% 的新 CRD 合并前通过 `crd_validator.py`；reconcile 函数通过 `reconcile_lint.py`；operator 公开发布前达到 Level 3（Full Lifecycle）。
