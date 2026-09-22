---
name: terraform-patterns
description: "Terraform infrastructure-as-code agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. Covers module design patterns, state management strategies, provider configuration, security hardening, policy-as-code with Sentinel/OPA, and CI/CD plan/apply workflows. Use when: user wants to design Terraform modules, manage state backends, review Terraform security, implement multi-region deployments, or follow IaC best practices. 当用户要求 写 Terraform / 基础设施即代码 / IaC 模块 时使用。 Do NOT use for running terraform apply (pattern authoring only)."
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

# Terraform Patterns

> 可预期的基础设施。安全的状态。可组合的模块。零漂移。

一套带明确主张的 Terraform 工作流，把失控的 HCL 变成结构良好、安全、生产级的基础设施代码。覆盖模块设计、状态管理、provider 模式、安全加固与 CI/CD 集成。

这不是 Terraform 教程——这是一组具体决策，关于如何写出不会在凌晨 3 点出事的基础设施代码。

## 斜杠命令

| 命令 | 作用 |
|---------|-------------|
| `/terraform:review` | 分析 Terraform 代码的反模式、安全问题与结构问题 |
| `/terraform:module` | 设计或重构 Terraform 模块，规范 inputs、outputs 与组合 |
| `/terraform:security` | 审计 Terraform 代码的安全漏洞、密钥暴露与 IAM 配置错误 |

## 何时激活

识别用户的这些表达：

- "Review this Terraform code"
- "Design a Terraform module for..."
- "My Terraform state is..."
- "Set up remote state backend"
- "Multi-region Terraform deployment"
- "Terraform security review"
- "Module structure best practices"
- "Terraform CI/CD pipeline"
- 任何涉及 `.tf` 文件、HCL、Terraform 模块、状态管理、provider 配置、基础设施即代码的请求

用户有 `.tf` 文件，或想用 Terraform 创建基础设施 → 本技能适用。

## 输入清单

扫描前一次性收集。缺输入时用这句话向用户问一次："要审计 Terraform 代码，请一次性提供：Terraform 目录路径、目标云厂商/后端类型、是否含多环境隔离。"

| 输入 | 必需 | 说明 |
|---|---|---|
| Terraform 目录 | 是 | `.tf` 目录树的路径，如 `./terraform`——两个脚本的位置参数 |
| 云 / 后端类型 | state review 需要 | AWS / GCP / Azure / Terraform Cloud——决定后端建议 |
| 环境隔离策略 | state review 需要 | 独立目录 vs workspaces vs Terragrunt |
| 模块范围 | `/terraform:module` 需要 | 模块负责什么（networking、compute……）以及消费方是谁 |

## 前置自检

```bash
python3 --version        # 预期：Python ≥ 3.8。两个脚本均仅依赖标准库。
ls scripts/tf_module_analyzer.py scripts/tf_security_scanner.py
                         # 预期：两个文件全部列出。
ls <tf-dir>/*.tf         # 预期：至少一个 .tf 文件。为空 → 目录不对。
```

- Python 缺失或版本过旧 → 安装 Python ≥ 3.8，然后停止。
- 脚本文件缺失 → 目录不对；`cd` 到本技能目录重新检查，然后停止。
- 目标目录没有 `.tf` 文件 → 与用户确认路径；不要扫一棵空树还称之为 review。

## 工作流

### `/terraform:review` — Terraform 代码评审

#### 步骤 1：分析现状

- **动作：** 读目标目录所有 `.tf` 文件；识别模块结构（扁平 vs 嵌套）；统计 resources、data sources、variables、outputs；核对命名约定。
- **预期：** 一份可在报告中引用的清单（计数 + 结构）。
- **失败时：** 目录不可读 → 与用户确认路径；不要评审一棵猜出来的树。

#### 步骤 2：套用评审清单

```text
MODULE STRUCTURE
├── Variables have descriptions and type constraints
├── Outputs expose only what consumers need
├── Resources use consistent naming: {provider}_{type}_{purpose}
├── Locals used for computed values and DRY expressions
└── No hardcoded values — everything parameterized or in locals

STATE & BACKEND
├── Remote backend configured (S3, GCS, Azure Blob, Terraform Cloud)
├── State locking enabled (DynamoDB for S3, native for others)
├── State encryption at rest enabled
├── No secrets stored in state (or state access is restricted)
└── Workspaces or directory isolation for environments

PROVIDERS
├── Version constraints use pessimistic operator: ~> 5.0
├── Required providers block in terraform {} block
├── Provider aliases for multi-region or multi-account
└── No provider configuration in child modules

SECURITY
├── No hardcoded secrets, keys, or passwords
├── IAM follows least-privilege principle
├── Encryption enabled for storage, databases, secrets
├── Security groups are not overly permissive (no 0.0.0.0/0 ingress on sensitive ports)
└── Sensitive variables marked with sensitive = true
```

- **预期：** 清单每一行都标 pass/fail，并附文件引用。
- **失败时：** 某一行无法仅凭代码判断（如 state backend）→ 标 "needs runtime check"，不要猜。

#### 步骤 3：生成结构报告

- **动作：** `python3 scripts/tf_module_analyzer.py assets/terraform`
- **预期：** 文本报告列出 resource/variable/output 分析与命名检查；退出码 0。
- **失败时：** argparse 报错 → 把目录作为位置参数传入；解析异常 → HCL 可能非标准，在报告中注明。

#### 步骤 4：跑安全扫描

- **动作：** `python3 scripts/tf_security_scanner.py assets/terraform`
- **预期：** 带严重度的发现项清单；退出码 0（strict 模式会升级 warning——CI 中用 `--strict`）。
- **失败时：** 有发现项 → 按下方 `/terraform:security` 表分诊；存在 Critical 发现项时不要合并。

### `/terraform:module` — 模块设计

#### 步骤 1：确定模块范围

- **动作：** 一个模块 = 一个逻辑分组；确定输入（variables）、outputs、资源边界；决定扁平还是嵌套。
- **预期：** 一段范围说明，写明模块由谁消费。
- **失败时：** 范围横跨多个关注点（network + compute + DB）→ 拆分；不要设计上帝模块。

#### 步骤 2：套用模块设计清单

```text
STRUCTURE
├── main.tf        — Primary resources
├── variables.tf   — All input variables with descriptions and types
├── outputs.tf     — All outputs with descriptions
├── versions.tf    — terraform {} block with required_providers
├── locals.tf      — Computed values and naming conventions
├── data.tf        — Data sources (if any)
└── README.md      — Usage examples and variable documentation

VARIABLES
├── Every variable has: description, type, validation (where applicable)
├── Sensitive values marked: sensitive = true
├── Defaults provided for optional settings
├── Use object types for related settings: variable "config" { type = object({...}) }
└── Validate with: validation { condition = ... }

OUTPUTS
├── Output IDs, ARNs, endpoints — things consumers need
├── Include description on every output
├── Mark sensitive outputs: sensitive = true
└── Don't output entire resources — only specific attributes

COMPOSITION
├── Root module calls child modules
├── Child modules never call other child modules
├── Pass values explicitly — no hidden data source lookups in child modules
├── Provider configuration only in root module
└── Use module "name" { source = "./modules/name" }
```

- **预期：** 清单全部满足后，模块才交给消费方使用。
- **失败时：** 某个 variable 定不出类型 → 模块边界划错了；回到步骤 1。

#### 步骤 3：生成模块脚手架

- **动作：** 按 STRUCTURE 输出文件结构（含样板代码、variable validation 块、必要的 lifecycle 规则）。
- **预期：** 文件落盘，`terraform fmt` 格式干净。
- **失败时：** `terraform fmt` 报错 → 生成的 HCL 有语法问题；交付前先修。

### `/terraform:security` — 安全审计

#### 步骤 1：代码级审计

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| `.tf` 文件中硬编码密钥 | Critical | 改用 sensitive = true 的 variables 或 vault |
| IAM policy 含 `*` 操作 | Critical | 收窄到具体操作与资源 |
| Security group 对端口 22/3389 开放 0.0.0.0/0 | Critical | 限制到已知 CIDR，或改用 SSM/bastion |
| S3 bucket 未加密 | High | 加 `server_side_encryption_configuration` 块 |
| S3 bucket 允许公开访问 | High | 加 `aws_s3_bucket_public_access_block` |
| RDS 未加密 | High | 设 `storage_encrypted = true` |
| RDS 可公开访问 | High | 设 `publicly_accessible = false` |
| CloudTrail 未启用 | Medium | 加 `aws_cloudtrail` 资源 |
| 有状态资源缺 `prevent_destroy` | Medium | 加 `lifecycle { prevent_destroy = true }` |
| 密钥类变量未标 `sensitive = true` | Medium | 给密钥变量加 `sensitive = true` |

- **预期：** 每行都对照代码核查；发现项映射到 file:line。
- **失败时：** 出现 Critical 发现项 → 阻断合并；任何 plan/apply 之前先修。

#### 步骤 2：状态安全审计

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 本地 state 文件 | Critical | 迁移到带加密的 remote backend |
| remote state 未加密 | High | 在后端启用加密（SSE-S3、KMS） |
| 无 state 锁 | High | S3 配 DynamoDB，TF Cloud 用原生锁 |
| state 全团队成员可访问 | Medium | 用 IAM policy 或 TF Cloud teams 限权 |

- **预期：** 检查 backend 配置（backend.tf / terraform {} 块），每行都有结论。
- **失败时：** 本地 state 文件里发现真实密钥 → 按泄露处理；轮换这些凭据（见 `env-secrets-manager` / `secrets-vault-manager`）。

#### 步骤 3：生成安全报告

- **动作：** `python3 scripts/tf_security_scanner.py assets/terraform`（CI 加 `--output json`；`--strict` 升级 warning）
- **预期：** 机器可读的发现项与人工审计一致；无 Critical 发现项脱离跟踪。
- **失败时：** 扫描器与人工审计不一致 → 以人工对照为准；人工表才是事实源。

## 工具

两个脚本均为仅依赖标准库的 Python。

| 脚本 | 位置参数 | Flags | 用途 |
|---|---|---|---|
| `scripts/tf_module_analyzer.py` | Terraform 目录（省略则演示） | `--output text\|json` | 结构、variables/outputs、命名、组合 |
| `scripts/tf_security_scanner.py` | Terraform 目录或 `.tf` 文件（省略则演示） | `--output text\|json`、`--strict` | 密钥、IAM、开放的 SG、加密、公开访问 |

```bash
# 分析一个 Terraform 目录
python3 scripts/tf_module_analyzer.py assets/terraform
python3 scripts/tf_module_analyzer.py assets/terraform --output json
python3 scripts/tf_module_analyzer.py ./modules/vpc

# 扫描一个 Terraform 目录
python3 scripts/tf_security_scanner.py assets/terraform
python3 scripts/tf_security_scanner.py assets/terraform --output json
python3 scripts/tf_security_scanner.py assets/terraform --strict
```

## 模块设计模式

### 模式 1：扁平模块（中小项目）

```text
infrastructure/
├── main.tf          # 全部资源
├── variables.tf     # 全部输入
├── outputs.tf       # 全部输出
├── versions.tf      # Provider 版本要求
├── terraform.tfvars # 环境取值（不提交）
└── backend.tf       # 远端状态配置
```

适用：单一应用、< 20 个资源、一个团队全权负责。

### 模式 2：嵌套模块（中大型项目）

```text
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf          # 以 dev 参数调用模块
│   │   ├── backend.tf       # Dev 状态后端
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── ...
│   └── prod/
│       └── ...
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   │   └── ...
│   └── database/
│       └── ...
└── versions.tf
```

适用：多环境、共享基础设施模式、团队协作。

### 模式 3：Terragrunt 单仓

```text
infrastructure/
├── terragrunt.hcl           # 根配置
├── modules/                  # 可复用模块
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── dev/
│   ├── terragrunt.hcl       # Dev 覆盖配置
│   ├── vpc/
│   │   └── terragrunt.hcl   # 模块调用
│   └── eks/
│       └── terragrunt.hcl
└── prod/
    ├── terragrunt.hcl
    └── ...
```

适用：大规模、多环境、DRY 配置、团队级隔离。

## Provider 配置模式

### 版本锁定

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"    # 允许 5.x，挡住 6.0
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
```

### 用 Alias 实现多 Region

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "west"
  region = "us-west-2"
}

resource "aws_s3_bucket" "primary" {
  bucket = "my-app-primary"
}

resource "aws_s3_bucket" "replica" {
  provider = aws.west
  bucket   = "my-app-replica"
}
```

### 用 Assume Role 实现多账号

```hcl
provider "aws" {
  alias  = "production"
  region = "us-east-1"

  assume_role {
    role_arn = "arn:aws:iam::PROD_ACCOUNT_ID:role/TerraformRole"
  }
}
```

## 状态管理

决策规则：单人开发 + 小项目 → 可用本地 state，但尽快迁 remote；Terraform Cloud/Enterprise → 原生 backend（自带锁、加密、RBAC）；AWS → S3 + DynamoDB；GCP → GCS；Azure → Blob Storage。环境之间用独立 state 文件隔离——独立目录（推荐）或 workspaces（更简单，隔离更弱）。所有环境共用一个 state 文件：绝对不行。

Backend HCL、迁移步骤（`state mv`/`import`/`rm`）、锁行为、force-unlock 流程 → `references/state-management.md`。

## 参考

仅在对应情况出现时读：

- `references/state-management.md` —— 选择/配置 backend、迁移 state（本地→remote、跨 backend）、导入既有资源、处理锁冲突 / force-unlock 时。
- `references/cicd-and-advanced-patterns.md` —— 任务涉及 CI/CD plan/apply 流水线（GitHub Actions）、drift 检测、多云 provider aliasing、OpenTofu 迁移、Infracost 成本门禁、导入既有基础设施或 Terragrunt 布局时。

## 安装

```bash
# 一行安装（任意工具）
git clone https://github.com/alirezarezvani/claude-skills.git
cp -r claude-skills/engineering/terraform-patterns ~/.claude/skills/

# 多工具安装 —— convert.sh 来自上游 claude-skills 仓库（本仓库不打包）：
# https://github.com/alirezarezvani/claude-skills
bash <claude-skills>/scripts/convert.sh --skill terraform-patterns --tool codex|gemini|cursor|windsurf|openclaw

# OpenClaw
clawhub install terraform-patterns
```

## 相关技能

- **senior-devops** —— 更宽的 DevOps 范围（CI/CD、监控）；流水线与基础设施运维用它。
- **aws-solution-architect** —— 设计 AWS 架构；terraform-patterns 负责落地实现。
- **senior-security** —— 应用层威胁；terraform-patterns 覆盖基础设施安全态势。
- **ci-cd-pipeline-builder** —— 自动化部署 terraform-patterns 定义的内容。

## 失败处置表

| 症状 / 退出码 | 原因 | 修复 |
|---|---|---|
| `tf_module_analyzer.py` 打出演示报告 | 未给目录参数 | 把 Terraform 目录作为位置参数传入 |
| 扫描器无输出但人工审计发现问题 | 扫描器基于正则，不是 HCL 解析器 | 人工清单（步骤 1 的表）是事实源；把扫描缺口记录在案 |
| 扫描器 `--strict` 让 CI 因 warning 失败 | strict 模式升级 warning | 修复，或把已接受的 warning 显式记入基线 |
| 报告中出现 HCL 解析异常 | 非标准/生成的 HCL | 在报告中注明；请用户侧用 `terraform validate` 验证 |
| 本地 `terraform.tfstate` 中发现 state 密钥 | 本地 state 带真实取值 | 按凭据泄露处理：轮换密钥，迁移到加密的 remote backend |
| `python: command not found` | 无解释器 | 安装 Python ≥ 3.8；两个脚本均仅依赖标准库 |

## 交付标准

满足以下条件才算跑完本技能：

- 评审/安全报告以 `tf_review_<dir>_<date>.md` / `tf_security_<dir>_<date>.md`（或 `--output json` 变体）保存，位置在被审计目录树旁或团队文档区。
- 每个 Critical 发现项要么已在代码中修复，要么有带负责人的跟踪 issue；Medium 发现有截止日期。
- 新建/重构的模块：STRUCTURE 清单的文件全部存在，`terraform fmt` 干净，README 含用法示例。
- 完整性验证：重跑 `tf_security_scanner.py --output json`，发现项数量与报告一致；人工审计中的发现项无一项游离在跟踪清单之外。
- 边界：本技能绝不运行 `terraform plan`/`apply`——只做模式编写。
