---
name: observability-designer
description: "可观测性体系设计指南。当需要为服务规划 metrics/logs/traces、定义 RED/USE 指标、设计仪表盘与告警、接入 OpenTelemetry、做健康检查与关键路径埋点时，由 fullstack-devops-engineer 加载执行。触发场景：design a dashboard / too many alerts / alert fatigue / golden signals / grafana dashboard / reduce alert noise / monitoring for a new service / observability strategy / alerting review；中文触发词：设计监控告警 / 可观测性方案 / 仪表盘 / 降低告警噪音。Do NOT use for 安装或运维可观测性 agent，也不用于 SLO/错误预算设计（交给 slo-architect）。"
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

# Observability Designer / 可观测性设计

跨三大支柱（metrics、logs、traces）设计生产级仪表盘与告警配置，用确定性生成器替代拍脑袋。本 skill 面向 fullstack-devops-engineer，目标是让系统出问题时**能快速定位、能被用户感知到前发现**。

## 车道划分

SLO/SLI 设计、错误预算数学、burn-rate 告警阈值——包括生成 SLO 定义脚手架——交给 `slo-architect`（它带 `slo_designer.py`、`error_budget_calculator.py`、`slo_review.py`）。本技能的车道：仪表盘（`scripts/dashboard_generator.py`）与告警降噪（`scripts/alert_optimizer.py`）。

## 何时使用

- 新服务上线前要接监控/日志/链路追踪；
- 故障后复盘发现"看不见、查不到"；
- 设计仪表盘、告警规则、埋点方案。

## 何时不使用

- SLO / 错误预算设计 → `slo-architect`
- 安装或运维可观测性 agent（Prometheus/Grafana 部署）→ ops/infrastructure 类技能
- 压测与容量规划 → `performance-profiler`

## 三大支柱

1. **Metrics（指标）**：聚合数值，看趋势、配告警，低成本高覆盖。
2. **Logs（日志）**：离散事件，排查细节，结构化输出。
3. **Traces（链路）**：单次请求跨服务调用链，定位慢在哪一跳。

统一用 OpenTelemetry 埋点，后端可接 Prometheus/Grafana、Loki、Tempo/Jaeger。

## RED 方法（请求类服务）

- **Rate**：每秒请求数（QPS/RPM）。
- **Errors**：失败请求数/比例。
- **Duration**：请求延迟分布（p50/p95/p99），不只看平均值。

## USE 方法（资源类，如 DB/CPU）

- **Utilization**：利用率（CPU/内存/磁盘/连接池占用）。
- **Saturation**：饱和度（队列长度、等待时间）。
- **Errors**：错误计数（OOM、连接拒绝、慢查询数）。

## 必埋的黄金指标

- HTTP：`http_requests_total{route,method,status}`、`http_request_duration_seconds` 直方图。
- 业务：关键业务事件下单/支付成功量与失败量（**业务指标比技术指标更能反映用户受影响面**）。
- 依赖：DB 连接池使用率、外部 API 调用耗时与错误率。
- 容器：CPU/内存/重启次数/OOMKill。

## 结构化日志

- 每行 JSON，必带字段：`ts`、`level`、`service`、`trace_id`、`span_id`、`user_id`(脱敏)、`route`、`error`。
- 错误日志带 stack trace，不打印整个请求体（PII）。
- 日志级别分级：`debug`/`info`/`warn`/`error`，生产默认 info。

## 告警设计原则

- **告警"症状"而非"原因"**：告"用户看到 500 增多/延迟升高"，而不是"某台机器 CPU 高"。
- **少而精**：告警必须有人行动，告了没人理=没告。
- **分级**：Critical（立即响应）/ Warning（工作时间处理）/ Info（仅记录）。
- 每个告警带 runbook 链接：现象、影响、排查步骤、值班人。

## 输入清单

跑任何东西前一次性收集。缺输入时用这句话向用户问一次："要设计可观测性，请一次性提供：服务名、服务类型、关键级别、仪表盘受众；若要优化告警，再给告警配置 JSON 路径。"

| 输入 | 必需 | 说明 |
|---|---|---|
| 服务名 | 是 | 如 `payments` → `--name` |
| 服务类型 | 是 | `api` / `web` / `database` / `queue` / `batch` / `ml` 之一 → `--service-type` |
| 关键级别 | 是 | `critical` / `high` / `medium` / `low` → `--criticality`；决定告警默认值 |
| 仪表盘受众 | 是 | `sre` / `developer` / `executive` / `ops` → `--role` |
| 告警配置 JSON | 告警工作需要 | 现有规则及其阈值与路由 → `--input`（预期形状见 `assets/sample_alerts.json`） |
| 服务定义 JSON | 可选 | 更丰富的仪表盘输入 → `--input`（示例：`assets/sample_service_api.json`、`assets/sample_service_web.json`） |

## 前置自检

```bash
python3 --version        # 预期：Python ≥ 3.8。两个脚本均仅依赖标准库。
ls scripts/dashboard_generator.py scripts/alert_optimizer.py
                         # 预期：两个文件全部列出。
```

- Python 缺失或版本过旧 → 安装 Python ≥ 3.8，然后停止。
- 脚本文件缺失 → 目录不对；`cd` 到本技能目录重新检查，然后停止。
- 优化告警？再跑 `python3 -c "import json;json.load(open('<alerts.json>'))"` —— 预期：无 traceback（JSON 有效）。无效 → 先修复或导出有效配置；优化器不修复损坏的 JSON。

## 快速开始

```bash
# 为服务生成仪表盘 spec（Grafana JSON + 文档）
python3 scripts/dashboard_generator.py --service-type api --name payments --criticality critical --role sre --format grafana -o dashboard.json --doc-output dashboard.md

# 分析现有告警配置的噪音、重复与覆盖缺口
python3 scripts/alert_optimizer.py --input alerts.json --analyze-only --report alert_report.json
# ...报告确认后再输出优化配置：
python3 scripts/alert_optimizer.py --input alerts.json --output alerts_optimized.json

# SLO 定义/错误预算 → 用 slo-architect 技能（其 scripts/slo_designer.py）
```

## 工作流

### 工作流 1：为服务生成仪表盘

#### 步骤 1：收集服务事实

- **动作：** 一次性收集输入清单（名称、类型、关键级别、受众）。
- **预期：** 四个值均经用户确认；服务类型是六种支持类型之一。
- **失败时：** 类型对不上任何一种 → 选最接近的并明说；不要悄悄贴错标签。

#### 步骤 2：生成规格

- **动作：** `python3 scripts/dashboard_generator.py --service-type <type> --name <svc> --criticality <level> --role <role> --format grafana -o dashboard_<svc>.json --doc-output dashboard_<svc>.md`
- **预期：** stdout 打出 `Dashboard specification saved to:` 与 `Documentation saved to:`；两个文件存在，JSON 的 `dashboard.title` 为 `<name> - <ROLE> Dashboard`。
- **失败时：** argparse 报错 → 缺必填 flag，补上重跑。

#### 步骤 3：导入并验证面板渲染

- **动作：** 把 dashboard_<svc>.json 导入 Grafana；用实时时间范围打开每个 golden-signal 面板（latency、traffic、errors、saturation）。
- **预期：** 每个面板都渲染出数据——集群里确实存在该指标的面板不出现 `No data`。
- **失败时：** `No data` → 面板查询里的指标 label 与你的 exporter label 不匹配；收尾前把查询适配到你的 Prometheus job label。

#### 步骤 4：用验证环确认

- **动作：** 让仪表盘跑满一个 on-call 轮换；收集缺失/闲置面板的反馈。
- **预期：** actionable-review 通过——面板有人用，关键项无缺失。
- **失败时：** 缺口反复出现 → 调整 `--role`/`--criticality` 重新生成，或手工补面板；记录原因。

### 工作流 2：降低告警噪音

#### 步骤 1：给现有配置建基线

- **动作：** `python3 scripts/alert_optimizer.py --input <alerts.json> --analyze-only --report alert_report.json`
- **预期：** 报告文件存在，含 `summary`、`noisy_alerts`、`coverage_gaps`、`duplicate_alerts`、`threshold_analysis`、`alert_fatigue_assessment`、`overall_recommendations` 键；stdout 打出 `ALERT CONFIGURATION ANALYSIS SUMMARY` 块。
- **失败时：** JSON 解析错 → 输入配置损坏；先修（见前置自检）。

#### 步骤 2：改动之前先审报告

- **动作：** 读 `noisy_alerts`、`duplicate_alerts`、`coverage_gaps`；逐条决定：调阈值、合并、删除，还是保留并写明理由。
- **预期：** 每条发现项都有决定——没有默认照收，也没有默默无视。
- **失败时：** 某条发现项判错了（如 "noisy" 的其实是 paging-critical 告警）→ 保留它并记录原因；优化器启发式只是建议，不是法律。

#### 步骤 3：输出优化配置

- **动作：** `python3 scripts/alert_optimizer.py --input <alerts.json> --output alerts_optimized.json`
- **预期：** 输出文件存在；与输入 diff 只包含步骤 2 的决定。
- **失败时：** diff 出现未评审的变更 → 不要部署；重跑 `--analyze-only`，对齐决定后重新输出。

#### 步骤 4：部署并度量

- **动作：** 经常规告警流水线部署 alerts_optimized.json；跟踪报告的噪音指标一个 on-call 轮换。
- **预期：** actionable-alert 比例较基线报告改善。
- **失败时：** 比例持平或更差 → 对线上配置重跑 `--analyze-only` 并迭代；噪音源通常在路由，不在阈值。

## 参数速查表

### dashboard_generator.py

| 参数 | 取值 | 说明 |
|---|---|---|
| `--service-type` | `api` / `web` / `database` / `queue` / `batch` / `ml` | 决定面板集合 |
| `--name` | 服务名 | 仪表盘标题 |
| `--criticality` | `critical` / `high` / `medium` / `low` | 决定面板侧重 |
| `--role` | `sre` / `developer` / `executive` / `ops` | 按角色的视图 |
| `--format` | `grafana` / `json` | `grafana` = 可导入 JSON |
| `-o` / `--output` | 路径 | 仪表盘 spec 文件 |
| `--doc-output` | 路径 | 人类可读的仪表盘文档 |
| `--input`, `-i` | 服务定义 JSON | 可选；更丰富的 spec（样例在 `assets/`） |
| `--summary-only` | flag | 只打印摘要，不写文件 |

### alert_optimizer.py

| 参数 | 取值 | 说明 |
|---|---|---|
| `--input`, `-i` | 告警配置 JSON | 必需 |
| `--output`, `-o` | 路径 | 优化后的配置；`--analyze-only` 时省略 |
| `--report`, `-r` | 路径 | 分析报告文件 |
| `--format` | `json` / `html` | 报告格式 |
| `--analyze-only` | flag | 只分析，不输出新配置 |

## 设计规则（摘要）

完整模式目录在 `references/` —— 以下是跑工作流时就要套用的规则：

- **按服务类型的 golden signals：** latency（P50/P95/P99）、traffic、errors（4xx/5xx + 静默失败）、saturation（队列、连接池）。请求驱动服务用 RED，资源用 USE。
- **仪表盘信息架构：** overview → service → component → instance 逐层下钻；80% 运维向 / 20% 探索向面板；每屏 ≤7±2 个面板；按角色分视图（SRE ≠ 高管）。
- **告警规则：** 每条告警写明响应动作；severity = critical（服务宕机、SLO 烧穿）/ warning（逼近阈值）/ info（发布、容量）。没有动作 → 不许告警。
- **告警疲劳控制：** 高精确优先于高召回；加迟滞（fire/resolve 阈值不同）；已知故障期间抑制；关联告警分组。
- **成本控制：** 分层指标保留期、log/trace 采样、基数管理——高基数 label 在撑爆存储之前就标出来。
- **每条 critical 告警配 runbook：** 含义、用户影响、排查步骤、恢复方法、升级路径。没有 runbook 的告警是一个发现项，不是一个功能。

## 失败处置表

| 症状 / 退出码 | 原因 | 修复 |
|---|---|---|
| `dashboard_generator.py` argparse 报错 | 缺必填 flag（`--service-type`/`--name`/`--criticality`/`--role`） | 按报错补 flag 重跑 |
| Grafana 导入后面板 `No data` | 指标 label 与你的 exporter 不一致 | 把面板查询适配到你的 Prometheus job label |
| `alert_optimizer.py` JSON decode 报错 | 输入配置损坏 | 用 `python3 -m json.tool <file>` 校验；修源配置 |
| 报告把 paging-critical 告警标为 noisy | 启发式仅供参考 | 保留该告警；在评审中记录例外 |
| 优化 diff 含未评审的变更 | 步骤 2 被跳过或敷衍 | 不要部署；对齐决定后重新输出 |
| 部署后 actionable-alert 比例无变化 | 噪音源是路由/归属，不是阈值 | 对线上配置重跑 `--analyze-only`；先修路由 |
| `python: command not found` | 无解释器 | 安装 Python ≥ 3.8；两个脚本均仅依赖标准库 |

## 参考

仅在对应情况出现时读：

- `references/alert_design_patterns.md` —— 设计或评审告警规则时（severity 模型、疲劳控制、复合告警），或优化器报告需要解读时。
- `references/dashboard_best_practices.md` —— 生成的仪表盘需要手工微调时（面板选择、下钻路径、可视化选型）。

## 资产模板

- `assets/sample_alerts.json` —— 与 `alert_optimizer.py --input` 预期形状完全一致的告警配置示例；也可作为你自己导出的模板
- `assets/sample_service_api.json` / `assets/sample_service_web.json` —— 供 `dashboard_generator.py --input` 用的服务定义 JSON

## 交付标准

满足以下条件才算跑完本技能：

- 仪表盘：`dashboard_<service>.json`（可导入 Grafana）与 `dashboard_<service>.md`（文档）保存在服务仓库旁或团队仪表盘目录；每个面板都在 Grafana 中验证过渲染实时数据。
- 告警工作：`alert_report.json`（基线）与 `alerts_optimized.json`（仅含已评审 diff）与原配置一起存入版本控制；已部署并度量一个 on-call 轮换。
- 完整性验证：同参数重跑生成器命令，字节级复现仪表盘文件（确定性输出）；告警报告的 `summary` 计数与已部署配置的规则数一致。
- 持续要求：actionable-alert 比例跨轮换持续上升；每条 critical 告警都有 runbook。

## 清单（交付前逐项过）

- [ ] 服务暴露 `/health/live` 与 `/health/ready`（不含敏感信息）。
- [ ] RED 三指标已埋，延迟看 p95/p99 而非平均。
- [ ] 日志结构化、带 trace_id，可与 trace 串起来。
- [ ] 关键业务事件有业务指标。
- [ ] 仪表盘分层：高层（用户体验 SLO）+ 排障（服务/依赖下钻）。
- [ ] 每个告警有 runbook、有值班人、已分级。
- [ ] 外部依赖（DB/缓存/支付）的错误与延迟有监控。
- [ ] 重启/OOM/崩溃有告警。
- [ ] 告警经过演练，确认误报率可接受。

## 易错点

- **只看平均值**：平均延迟 200ms 可能掩盖 1% 请求 5s，必须看分位数。
- **告警风暴**：一个故障触发几十条告警，值班人麻木；做聚合与依赖抑制。
- **日志打印敏感信息**：手机号/身份证/卡号明文进日志，合规事故；脱敏。
- **健康检查做重了**：readiness 里连了 DB/外部 API，外部一抖就全量重启，探针要轻、要分层。
- **没 trace_id 贯穿**：跨服务请求查不到关联，日志像散沙；OTel 上下文必须透传。
- **指标维度爆炸**：label 里塞 user_id/order_id，时间序列数量爆炸，后端直接崩。
