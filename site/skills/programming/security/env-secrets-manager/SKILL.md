---
name: env-secrets-manager
description: "Manage environment-variable hygiene and secrets safety across local development and production. Triggers on "audit .env", "secrets scan", "check for leaked keys", "rotate credentials", "env file hygiene", "committed secrets", "detect-secrets or gitleaks setup", "missing env var incident". Practical auditing, drift awareness, rotation readiness. Use when auditing .env files for committed secrets, planning a credential rotation, debugging missing-env-var production incidents, or hardening a new project against secrets leakage. 当用户要求 管理环境变量 / 密钥审计 / 检查 .env 泄露 / 轮换准备 时使用。 Do NOT use for reading or printing secret values (hygiene checks only); production vault infrastructure and rotation execution live in secrets-vault-manager."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: security
  pattern: workflow
  tier: expert
  verified-date: "2026-09-09"
---

# Env & Secrets Manager

管理本地开发与生产流程中的环境变量卫生与密钥安全。本技能聚焦实操审计、漂移感知与轮换准备。

## 核心能力

- `.env` 与 `.env.example` 的生命周期指引
- 仓库工作树的密钥泄露检测（`scripts/env_auditor.py`）
- 按严重度分级报告疑似凭据
- 轮换与止损的实操指引
- 面向 CI 检查的即用型输出

## 何时使用

- 推送涉及 env/config 文件的提交之前
- 安全审计与事故分诊过程中
- 引导新贡献者建立安全的 env 约定时
- 验证没有明显密钥被硬编码时

## 何时不使用

- 读取或打印密钥值——只做卫生检查；发现项一律脱敏
- 生产 vault 基础设施、轮换执行、审计日志后端、HA/DR → `secrets-vault-manager`

## 输入清单

扫描前一次性收集。缺输入时用这句话向用户问一次："要审计密钥泄露，请一次性提供：仓库根目录路径、是否需要 CI 用的 JSON 输出、是否已有 .secrets.baseline / .gitleaksignore。"

| 输入 | 必需 | 说明 |
|---|---|---|
| 仓库 / 项目根目录 | 是 | 扫描路径 → `env_auditor.py` 的位置参数 |
| 输出格式 | 否 | text（默认）或 CI 流水线用 `--json` |
| 扫描大小上限 | 否 | `--max-filesize <KB>`；大的生成文件会拖慢扫描 |
| 已有的 baseline/ignore 文件 | 用于误报分诊 | `.secrets.baseline`（detect-secrets）和/或 `.gitleaksignore`（gitleaks），纳入版本控制 |

## 前置自检

```bash
python3 --version        # 预期：Python ≥ 3.8。审计脚本仅依赖标准库。
ls scripts/env_auditor.py
                         # 预期：文件列出。
test -d <repo-root> && echo ok
                         # 预期：ok —— 目标仓库存在。
```

- Python 缺失或版本过旧 → 安装 Python ≥ 3.8，然后停止。
- 脚本缺失 → 目录不对；`cd` 到本技能目录重新检查，然后停止。
- 目标仓库不存在 → 扫描前与用户确认路径；不要扫错树。

## 快速开始

```bash
# 扫描仓库中的疑似密钥泄露（输出已脱敏）
python3 scripts/env_auditor.py assets/sample-repo   # 随包样例仓库（占位密钥+正确 .gitignore）；你的真实项目换成仓库根

# CI 流水线用的 JSON 输出
python3 scripts/env_auditor.py assets/sample-repo --json
```

## 工作流

### 步骤 1：扫描工作树

- **动作：** `python3 scripts/env_auditor.py <repo-root>`（CI 加 `--json`）。
- **预期：** `=== ENV AUDITOR ===` 标头、`Findings: N (critical=x, high=y, ...)` 汇总行，以及每条带 `file:line` 和**已脱敏**摘录（如 `sk-F...(30 chars)`）的发现项；有发现项也退出码 0。
- **失败时：** 输出 `usage: env_auditor.py ...` → 缺仓库路径位置参数；发现项为 0 → 确认扫的是目标根目录，不是子目录。

### 步骤 2：按严重度分诊

- **动作：** 按 `critical` → `high` → `medium`/`low` 顺序处理；每条发现项判定：真实凭据、测试夹具，还是误报。
- **预期：** 每条发现项标上 real / test-fixture / false-positive。
- **失败时：** 分不清值是否真实 → 在证明之前一律当真实的；绝不打印值来判别（审计器的脱敏摘录足够定位）。

### 步骤 3：轮换真实凭据并清除暴露值

- **动作：** 先在 provider 侧轮换，再从工作树与历史中移除该值；把 `.env.example` 更新为空占位符，确认 `.gitignore` 覆盖 `.env`。
- **预期：** provider 侧旧凭据已吊销；工作树只剩占位符。
- **失败时：** 值已进 git 历史 → 删文件不够；无论怎样都必须轮换凭据，改写历史是另一项与用户显式确认的决定。

### 步骤 4：记录轮换元数据

- **动作：** 给每个凭据标注 `# ROTATED: <date>` 与过期元数据；为每个密钥维护消费方清单（哪些服务在读它）。
- **预期：** 每个密钥都有轮换日期注释和已知消费方列表。
- **失败时：** 某密钥消费方不明 → 不要盲轮换；先盘点消费方，否则轮换会弄坏它们。

### 步骤 5：加 CI/pre-commit 门禁

- **动作：** 把 gitleaks 或 detect-secrets 接进 pre-commit 与 CI（配置见下）；重跑 `env_auditor.py` 与 `gitleaks detect` / `detect-secrets scan` 直到干净。
- **预期：** 门禁能拦下植入的测试密钥；当前工作树跑出干净结果。
- **失败时：** 明知有真实密钥门禁却放行 → 规则集太窄；加规则，而不是忽略文件。

## 失败处置表

| 症状 / 退出码 | 原因 | 修复 |
|---|---|---|
| `usage: env_auditor.py [-h] [--json] ...` | 缺仓库路径位置参数 | 把仓库根目录作为第一个参数传入 |
| 明知有泄露却报 0 发现项 | 扫错根目录，或文件超过大小上限 | 从正确根目录重跑；调高 `--max-filesize` |
| `tests/` 或 fixtures 中有发现项 | 有意的测试凭据 | 核实确实为假；确保不进生产配置，并记入 baseline |
| `.env.example` 含看似真实的值 | 示例文件被填了真实配置 | 按泄露处理：轮换，替换为空占位符 |
| 轮换凭据后下游服务故障 | 消费方不明 | 利用 provider 的重叠窗口恢复（如支持），补全消费方清单，再次轮换 |
| 调试时密钥被打印进 CI 日志 | 日志语句打印了 env | 脱敏/删除该日志行；轮换被打印的值 |
| gitleaks 误报泛滥 | 默认规则对该技术栈太宽 | 收紧 regex 或加 `.gitleaksignore` 指纹——默认绝不整文件忽略 |

## Pre-commit 密钥检测

在密钥进入版本控制之前拦住，是性价比最高的防御。两个主流工具覆盖这一领域。

### gitleaks

```toml
# .gitleaks.toml — minimal configuration
[extend]
useDefault = true

[[rules]]
id = "custom-internal-token"
description = "Internal service token pattern"
regex = '''INTERNAL_TOKEN_[A-Za-z0-9]{32}'''
secretGroup = 0
```

- 安装：`brew install gitleaks` 或从 GitHub releases 下载。
- Pre-commit hook：`gitleaks git --pre-commit --staged`
- Baseline 扫描：`gitleaks detect --source . --report-path gitleaks-report.json`
- 误报在 `.gitleaksignore` 中管理（每行一个指纹）。

### detect-secrets

```bash
# Generate baseline
detect-secrets scan --all-files > .secrets.baseline

# Pre-commit hook (via pre-commit framework)
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

- 支持为组织特定模式编写**自定义插件**。
- 审计流程：`detect-secrets audit .secrets.baseline`，交互式标记真/假阳性。

### 误报管理

- 把 `.gitleaksignore` 或 `.secrets.baseline` 纳入版本控制，全团队共享排除项。
- 安全审计时复查误报清单——排除模式日久可能掩盖真实泄露。
- 优先收紧 regex，而不是大范围忽略文件。

## 轮换准备（仅检测侧）

深度轮换执行——provider 自动化、动态密钥、应急处置清单——属于 **secrets-vault-manager**。本技能覆盖准备侧：

- 在每个凭据旁记录创建/过期元数据。
- 在过期前 30、14、7 天设提醒。
- 跑 `scripts/env_auditor.py`，标出没有轮换日期注释（`# ROTATED: <date>`）的密钥。
- 为每个密钥维护消费方清单，让轮换的爆炸半径在需要之前就已知。

> **交叉引用：** 生产 vault 基础设施、云密钥存储选型（Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager）、轮换执行流程、审计日志后端与灾备，见 `secrets-vault-manager`。

## CI/CD 密钥注入（要点）

- 优先 **OIDC federation / 短期令牌**，而不是长期访问密钥。
- 绝不在流水线输出中回显或打印密钥值；依赖平台打码，但不要去测试它。
- 不向不受信任 fork 触发的流水线暴露密钥。
- 流水线架构模式 → `ci-cd-pipeline-builder`；vault 支撑的注入 → `secrets-vault-manager`。

## 审计日志（要点）

谁在何时访问了哪个密钥属于 vault 领地——云原生审计链路（CloudTrail / Activity Log / Cloud Audit Logs / Vault audit backend）、批量读取告警与 SIEM 对接都在 `secrets-vault-manager` 覆盖。本地等价要求：`.env` 的值不进 shell 历史和 CI 日志。

## 常见坑

- 在 `.env.example` 里提交真实值
- 轮换了一个系统，漏掉下游消费方
- 调试或事故响应时把密钥打进日志
- 未经核实就把疑似泄露当低优先级

## 最佳实践

1. 生产环境的唯一事实源用密钥管理器。
2. 开发用 env 文件留在本地并 gitignore。
3. 合并前在 CI 强制检测。
4. 凭据轮换后立即重测应用链路。

## 参考

仅在对应情况出现时读：

- `references/secret-patterns.md` —— 分诊发现项命中了什么（审计器检测哪些凭据形状）或编写自定义检测规则时。
- `references/validation-detection-rotation.md` —— 判断发现项是否为活跃凭据，或规划轮换准备清单时。

## 资产模板

- `assets/sample_env_leak.env` —— 含"假但逼真"凭据形状的样例文件；在信任一次干净结果之前，先用它验证审计器能命中你的模式。

## 交叉引用

| 技能 | 关系 |
|-------|-------------|
| **Secrets Vault Manager**（`secrets-vault-manager`） | 生产 vault 基础设施、轮换执行、审计日志、HA/DR |
| **CI/CD Pipeline Builder**（`ci-cd-pipeline-builder`） | 流水线架构、密钥注入模式 |

## 交付标准

满足以下条件才算跑完本技能：

- 审计报告以 `env_audit_<repo>_<date>.json`（经 `--json`）保存在仓库旁或安全工作区；原始发现项绝不以未脱敏形式贴进工单。
- 每条发现项按以下之一收口：已轮换+已移除、误报已入 baseline、测试夹具已记录。
- `.env.example` 只含占位符；`.gitignore` 覆盖 `.env`；每个凭据都有轮换元数据（`# ROTATED: <date>`）。
- 完整性验证：`python3 scripts/env_auditor.py <repo-root>` 在当前工作树报 0 critical/high；pre-commit/CI 门禁能拦下植入的测试密钥。
- 持续要求：过期前 30/14/7 天的轮换提醒真实触发；每个密钥的消费方清单保持最新。
