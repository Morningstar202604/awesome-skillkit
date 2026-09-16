---
name: secrets-vault-manager
description: "Use when the user asks to set up secret management infrastructure, integrate HashiCorp Vault, configure cloud secret stores (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager), implement secret rotation, or audit secret access patterns. Triggers on "set up Vault", "vault policies", "AppRole or OIDC auth", "rotate database credentials", "dynamic secrets", "vault audit log", "secret leak response", "External Secrets Operator". 当用户要求 用密钥库 / Vault 管理凭据 / 密钥轮换 / 审计密钥访问 时使用。 Do NOT use for storing or reading production secret values (workflow design only); local .env hygiene lives in env-secrets-manager."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: security
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-09"
---

# Secrets Vault Manager

面向运行 HashiCorp Vault、云原生密钥存储或混合架构的团队，管理生产密钥基础设施。覆盖策略编写、认证方式配置、自动化轮换、动态密钥、审计日志与事件响应。

**区别于 env-secrets-manager**——那个管本地 `.env` 文件卫生与泄露检测。本技能在基础设施层运作——Vault 集群、云 KMS、证书颁发机构、CI/CD 密钥注入。

## 何时使用

- 搭建新 Vault 集群，或迁移到托管密钥存储
- 为服务、CI runner、人类操作员设计认证方式
- 实施自动化凭据轮换（数据库、API key、证书）
- 面向合规审计密钥访问模式（SOC 2、ISO 27001、HIPAA）
- 响应需要大规模吊销的密钥泄露
- 把密钥接入 Kubernetes 工作负载或 CI/CD 流水线

## 输入清单

设计前一次性收集。缺输入时用这句话向用户问一次："要设计密钥基础设施，请一次性提供：部署形态（Vault 自建 / 云托管）、服务与消费者清单、现有密钥盘点（类型/最近轮换时间/负责人）、合规要求。"

| 输入 | 必需 | 说明 |
|---|---|---|
| 部署形态 | 是 | 自建 Vault（Raft HA）vs AWS Secrets Manager / Azure Key Vault / GCP Secret Manager vs 混合 |
| 服务与消费者清单 | 是 | 哪些服务、CI runner、人需要哪些密钥 |
| 密钥盘点 JSON | 轮换规划需要 | 条目含 `name`、`type`、`last_rotated`（`YYYY-MM-DD`）、`owner` → `rotation_planner.py --inventory` |
| 应用需求 | 配置生成需要 | 应用名、认证方式、密钥类型 → `vault_config_generator.py` |
| 合规目标 | 审计设计需要 | SOC 2 / ISO 27001 / HIPAA 的最低保留期 |
| 审计日志文件 | 异常复盘需要 | Vault/云审计日志（JSON lines 或 JSON array）→ `audit_log_analyzer.py --log-file` |

## 前置自检

```bash
python3 --version        # 预期：Python ≥ 3.8。3 个脚本均仅依赖标准库。
ls scripts/vault_config_generator.py scripts/rotation_planner.py scripts/audit_log_analyzer.py
                         # 预期：3 个文件全部列出。
python3 -m json.tool <inventory.json > /dev/null && echo ok
                         # 预期：ok —— 盘点 JSON 有效。
```

- Python 缺失或版本过旧 → 安装 Python ≥ 3.8，然后停止。
- 脚本文件缺失 → 目录不对；`cd` 到本技能目录重新检查，然后停止。
- 要操作真实 Vault？再验证 CLI 可达性：`vault status` —— 预期：打印 seal 状态与集群信息。不可达 → 修好地址/token（把 `VAULT_ADDR`、`VAULT_TOKEN` 导出为环境变量——绝不在命令里内联凭据）再执行任何 `vault write`。

## HashiCorp Vault 模式

### 架构决策

| 决策 | 建议 | 理由 |
|----------|---------------|-----------|
| 部署模式 | Raft 存储的 HA | 无外部依赖，内置 leader 选举 |
| Auto-unseal | 云 KMS（AWS KMS / Azure Key Vault / GCP KMS） | 免去手动 unseal，支持自动重启 |
| Namespaces | 每环境一个（dev/staging/prod） | 爆炸半径隔离，策略独立 |
| Audit devices | File + syslog（双路） | 全部审计设备失效时 Vault 会拒绝请求——双路可避免停摆 |

### 认证方式

**AppRole** — 服务与批处理任务的机器对机器认证。

```hcl
# Enable AppRole
path "auth/approle/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Application-specific role
vault write auth/approle/role/payment-service \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_num_uses=1 \
  secret_id_ttl=10m \
  token_policies="payment-service-read"
```

**Kubernetes** — 基于 service account token 的 Pod 原生认证。

```hcl
vault write auth/kubernetes/role/api-server \
  bound_service_account_names=api-server \
  bound_service_account_namespaces=production \
  policies=api-server-secrets \
  ttl=1h
```

**OIDC** — 经 SSO provider（Okta、Azure AD、Google Workspace）的人类操作员访问。

```hcl
vault write auth/oidc/role/engineering \
  bound_audiences="vault" \
  allowed_redirect_uris="https://vault.example.com/ui/vault/auth/oidc/oidc/callback" \
  user_claim="email" \
  oidc_scopes="openid,profile,email" \
  policies="engineering-read" \
  ttl=8h
```

### Secret 引擎

| 引擎 | 用途 | TTL 策略 |
|--------|----------|-------------|
| KV v2 | 静态密钥（API key、配置） | 版本化，手动轮换 |
| Database | 动态 DB 凭据 | 默认 1h，上限 24h |
| PKI | TLS 证书 | 叶子证书 90d，中间 CA 5y |
| Transit | 加密即服务 | 每 90d 轮换密钥 |
| SSH | 签名 SSH 证书 | 交互 30m，自动化 8h |

### 策略设计

遵循最小权限，按路径控制粒度：

```hcl
# payment-service-read policy
path "secret/data/production/payment/*" {
  capabilities = ["read"]
}

path "database/creds/payment-readonly" {
  capabilities = ["read"]
}

# Deny access to admin paths explicitly
path "sys/*" {
  capabilities = ["deny"]
}
```

**策略命名约定：** `{service}-{access-level}`（如 `payment-service-read`、`api-gateway-admin`）。

## 云密钥存储集成

### 对比矩阵

| 特性 | AWS Secrets Manager | Azure Key Vault | GCP Secret Manager |
|---------|--------------------|-----------------|--------------------|
| 轮换 | 内置 Lambda | 经 Functions 写自定义逻辑 | Cloud Functions |
| 版本管理 | 自动 | 手动或自动 | 自动 |
| 加密 | AWS KMS（默认或 CMK） | HSM 支撑 | Google 托管或 CMEK |
| 访问控制 | IAM policies + 资源策略 | RBAC + Access Policies | IAM bindings |
| 跨 region | 支持复制 | 默认异地冗余 | 支持复制 |
| 审计 | CloudTrail | Azure Monitor + Diagnostic Logs | Cloud Audit Logs |
| 计费模型 | 按密钥 + 按 API 调用 | 按操作 + 按密钥 | 按密钥版本 + 按访问 |

### 选型建议

- **AWS Secrets Manager**：RDS/Aurora 凭据轮换开箱即用。全面在 AWS 上时最佳。
- **Azure Key Vault**：证书管理见长。Azure AD 集成工作负载的必选项。
- **GCP Secret Manager**：API 面最简。配 Workload Identity 的 GKE 原生工作负载最佳。
- **HashiCorp Vault**：多云、动态密钥、PKI、transit 加密。复杂或混合环境最佳。

### SDK 访问模式

**原则：** 启动时或经 sidecar 拉取密钥——绝不烧进镜像或配置文件。

```python
# AWS Secrets Manager pattern
import boto3, json

def get_secret(secret_name, region="us-east-1"):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
```

```python
# GCP Secret Manager pattern
from google.cloud import secretmanager

def get_secret(project_id, secret_id, version="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

```python
# Azure Key Vault pattern
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret(vault_url, secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

## 密钥轮换工作流

### 按密钥类型的轮换策略

| 密钥类型 | 轮换频率 | 方法 | 停机风险 |
|-------------|-------------------|--------|---------------|
| 数据库密码 | 30 天 | 双账号切换 | 零（A/B 轮换） |
| API key | 90 天 | 生成新的、废弃旧的 | 零（重叠窗口） |
| TLS 证书 | 到期前 60 天 | ACME 或 Vault PKI | 零（平滑 reload） |
| SSH 密钥 | 90 天 | Vault 签名证书 | 零（基于 CA） |
| 服务令牌 | 24 小时 | 动态生成 | 零（短时效） |
| 加密密钥 | 90 天 | 密钥版本化（rewrap） | 零（版本共存） |

### 数据库凭据轮换（双账号）

1. 存在两个数据库账号：`app_user_a` 与 `app_user_b`
2. 应用当前使用 `app_user_a`
3. 轮换时转 `app_user_b` 的密码，更新密钥存储
4. 应用在下次拉取凭据时切到 `app_user_b`
5. 宽限期过后，轮换 `app_user_a` 的密码
6. 循环往复

### API key 轮换（重叠窗口）

1. 在 provider 处生成新 API key
2. 新 key 以 `current` 存入密钥存储，旧的挪到 `previous`
3. 发布应用——它们读 `current`
4. 全部实例重启完（或 TTL 过期）后，吊销 `previous`
5. 吊销前由监控确认旧 key 零使用

## 动态密钥

动态密钥按需生成、自动过期。凡可行之处，优先动态密钥而非静态凭据。

### 数据库动态凭据（Vault）

```hcl
# Configure database engine
vault write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@db.example.com:5432/app" \
  allowed_roles="app-readonly,app-readwrite" \
  username="vault_admin" \
  password="<admin-password>"

# Create role with TTL
vault write database/roles/app-readonly \
  db_name=postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl=1h \
  max_ttl=24h
```

### 云 IAM 动态凭据

Vault 可生成短期 AWS IAM 凭据、Azure service principal 密码或 GCP service account key——彻底消灭长期云凭据。

### SSH 证书颁发机构

用 Vault 签名证书模型取代 SSH 密钥分发：

1. Vault 充当 SSH CA
2. 用户/机器申请短 TTL（30 分钟）的签名证书
3. SSH 服务器信任 CA 公钥——无需维护 `authorized_keys`
4. 证书自动过期——常规操作无需吊销

## 审计日志

### 该记录什么

| 事件 | 优先级 | 保留期 |
|-------|----------|-----------|
| 密钥读取访问 | HIGH | 至少 1 年 |
| 密钥创建/更新 | HIGH | 至少 1 年 |
| 认证方式登录 | MEDIUM | 90 天 |
| 策略变更 | CRITICAL | 2 年（合规） |
| 失败访问尝试 | CRITICAL | 1 年 |
| Token 创建/吊销 | MEDIUM | 90 天 |
| Seal/unseal 操作 | CRITICAL | 永久 |

### 异常检测信号

- 密钥从新 IP/CIDR 段被访问
- 访问量激增（某路径超基线 3 倍以上）
- 人类认证方式的非工作时间访问
- 服务访问其策略范围外的密钥（被拒请求）
- 单一来源多次认证失败
- Token 被赋予异常长的 TTL

### 合规报告

定期生成覆盖以下内容的报告：

1. **访问清单** —— 哪些身份在何时访问了哪些密钥
2. **轮换合规** —— 已逾期未轮换的密钥
3. **策略漂移** —— 上次评审后被修改过的策略
4. **孤儿密钥** —— 近期无访问的密钥（>90 天）

用 `audit_log_analyzer.py` 解析 Vault 或云审计日志，提取这些信号。

## 工作流：为一个服务搭建轮换 + 审计

### 步骤 1：建立密钥盘点

- **动作：** 把每个密钥（name、type、`last_rotated` 用 `YYYY-MM-DD`、owner）枚举成 JSON 文件。
- **预期：** JSON 有效（前置自检已验）；没有条目缺 `last_rotated`。
- **失败时：** 某密钥轮换日期不明 → 照样收录；规划器会标它逾期，这才是诚实状态。

### 步骤 2：生成轮换计划

- **动作：** `python3 scripts/rotation_planner.py --inventory secrets.json --policy 30d`（或 `60d`/`90d`；CI 加 `--json`）。
- **预期：** 计划列出每个密钥的下次轮换到期日；无 `last_rotated` 的条目向 stderr 打 `WARNING` 并标记逾期。
- **失败时：** JSON 校验错 → 修盘点；policy 档位错 → 只有 `30d`（激进）、`60d`、`90d` 三档。

### 步骤 3：生成 Vault auth + 策略配置

- **动作：** `python3 scripts/vault_config_generator.py --app-name <svc> --auth-method approle --secrets db-creds,api-key --environment production`
- **预期：** 按所选认证方式（`approle` / `kubernetes` / `oidc`）渲染出 HCL 策略/auth 配置。
- **失败时：** argparse 报错 → 缺必填 flag；应用前审查渲染出的策略是否最小权限——生成器只是起点，不是批准。

### 步骤 4：走变更流程评审并应用

- **动作：** 由人评审生成的策略；经 `vault policy write` / `vault write auth/...` 应用，`VAULT_TOKEN` 放环境变量。
- **预期：** `vault policy read <policy>` 与评审过的内容一致；测试 token 恰好拿到预期路径，不多一分。
- **失败时：** 测试 token 能读非预期路径 → 上线前收紧路径范围；绝不"以后再说"。

### 步骤 5：接好审计日志分析

- **动作：** `python3 scripts/audit_log_analyzer.py --log-file <vault-audit.log> --threshold 5`（或用 `--sample` 在合成日志上看输出形状）。
- **预期：** `=== Audit Log Analysis Report ===` 带汇总计数与异常清单；退出码 0。
- **失败时：** 真实日志却出空报告 → 确认日志是 JSON lines/array 格式；无信号时调低 `--threshold`（越低越敏感）。

## 失败处置表

| 症状 / 退出码 | 原因 | 修复 |
|---|---|---|
| `rotation_planner.py` stderr `WARNING: ... no last_rotated date` | 盘点条目缺轮换日期 | 行为正确——密钥被记为逾期；首次轮换后补日期 |
| `rotation_planner.py` JSON 报错 | 盘点不是有效 JSON / 形状不对 | 用 `python3 -m json.tool` 校验；条目需 `name`/`type`/`last_rotated`/`owner` |
| `vault_config_generator.py` argparse 报错 | 缺 `--app-name`/`--auth-method`/`--secrets` | 按报错补 flag；`--auth-method` 只接受 `approle`/`kubernetes`/`oidc` |
| 生成的策略比需要的宽 | 生成器默认值 | `vault policy write` 前手工收紧路径；评审步骤不可省 |
| `vault write` → permission denied | token 缺管理能力 | 用变更流程发放的管理 token，不要用服务 token |
| 审计分析器无输出 | 日志格式不对或阈值过高 | 确认 JSON lines/array；调低 `--threshold` |
| Vault sealed 并拒绝请求 | 重启时无 auto-unseal | 走 Unseal 流程（见下）——密钥持有人凑到法定人数，或 KMS auto-unseal |
| 审计设备全部失效 → Vault 拒绝请求 | file+syslog 同时宕机 | 先恢复至少一个审计设备；fail-closed 是设计使然 |

## 应急流程

### 密钥泄露响应（立即执行）

**时间目标：发现后 15 分钟内止损。**

1. **判定范围** —— 哪些密钥泄露、在哪（repo、日志、报错、第三方）
2. **立即吊销** —— 在源头轮换被泄露的凭据（provider API、Vault、云 SM）
3. **作废 token** —— 吊销所有访问过该泄露密钥的 Vault token
4. **审计爆炸半径** —— 查审计日志，确认暴露窗口内该密钥的使用情况
5. **通知干系人** —— 安全团队、受影响服务负责人、合规（涉及 PII/受监管数据时）
6. **复盘** —— 记录根因，更新控制措施防复发

### Vault Seal 操作

**何时 seal：** 影响 Vault 基础设施的活跃安全事件、疑似密钥被攻破。

**Sealing** 会停掉全部 Vault 操作。仅在万不得已时使用。

**Unseal 流程：**

1. 召集 unseal key 持有人凑法定人数（Shamir 阈值）
2. 或确认 auto-unseal 的 KMS 密钥可访问
3. 经 `vault operator unseal` unseal，或带 auto-unseal 重启
4. 确认审计设备已重连
5. 检查活跃 lease 与 token 有效性

完整 playbook 见 `references/emergency_procedures.md`。

## CI/CD 集成

### Vault Agent Sidecar（Kubernetes）

Vault Agent 与应用 Pod 并行运行，负责认证与密钥渲染：

```yaml
# Pod annotation for Vault Agent Injector
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "api-server"
  vault.hashicorp.com/agent-inject-secret-db: "database/creds/app-readonly"
  vault.hashicorp.com/agent-inject-template-db: |
    {{- with secret "database/creds/app-readonly" -}}
    postgresql://{{ .Data.username }}:{{ .Data.password }}@db:5432/app
    {{- end }}
```

### External Secrets Operator（Kubernetes）

偏好声明式 GitOps 而非 agent sidecar 的团队：

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: api-credentials
  data:
    - secretKey: api-key
      remoteRef:
        key: secret/data/production/api
        property: key
```

### GitHub Actions OIDC

用 OIDC federation 消灭 CI 里的长期密钥：

```yaml
- name: Authenticate to Vault
  uses: hashicorp/vault-action@v2
  with:
    url: https://vault.example.com
    method: jwt
    role: github-ci
    jwtGithubAudience: https://vault.example.com
    secrets: |
      secret/data/ci/deploy api_key | DEPLOY_API_KEY ;
      secret/data/ci/deploy db_password | DB_PASSWORD
```

## 反模式

| 反模式 | 风险 | 正确做法 |
|-------------|------|-----------------|
| 源码硬编码密钥 | 经 repo、日志、报错泄露 | 运行时从密钥存储拉取 |
| 长期静态 token（>30 天） | 凭据陈旧、无法追责 | 动态密钥或短 TTL + 轮换 |
| 共享服务账号 | 无按消费者的审计链路 | 每服务独立身份、独立凭据 |
| 无轮换策略 | 被攻破的凭据无限期存活 | 按计划自动轮换 |
| 密钥放 CI 环境变量 | 可见于构建日志、进程表 | Vault Agent 或基于 OIDC 的注入 |
| 单一 unseal key 持有人 | bus factor 为 1，恢复被卡死 | Shamir 分片（3-of-5）或 auto-unseal |
| 未配置审计设备 | 访问零可见性 | 双审计设备（file + syslog） |
| 通配策略（`path "*"`） | 权限过大，违反最小权限 | 每服务显式的按路径策略 |

## 参数速查表

| 脚本 | 关键参数 | 说明 |
|---|---|---|
| `scripts/vault_config_generator.py` | `--app-name`、`--auth-method approle\|kubernetes\|oidc`、`--secrets`（逗号分隔类型）、`--environment`、`--namespace`、`--json` | 渲染 Vault 策略 + auth 配置 |
| `scripts/rotation_planner.py` | `--inventory <json>`、`--policy 30d\|60d\|90d`、`--json` | 缺失/无效的 `last_rotated` → 标记逾期 |
| `scripts/audit_log_analyzer.py` | `--log-file <file>`、`--threshold <n>`（越低越敏感，默认 5）、`--json`、`--sample` | JSON lines 或 JSON array 日志 |

## 参考

仅在对应情况出现时读：

- `references/vault_patterns.md` —— 设计超出上述模式的 Vault 架构、认证方式或策略时。
- `references/cloud_secret_stores.md` —— 选型或集成 AWS/Azure/GCP 密钥存储时（SDK 细节、轮换 hook、IAM 接线）。
- `references/emergency_procedures.md` —— 泄露/seal 事件进行中读——完整响应 playbook，不是背景读物。

## 交叉引用

- **env-secrets-manager** —— 本地 `.env` 文件卫生、泄露检测、漂移感知
- **senior-secops** —— 安全运营、事件响应、威胁建模
- **ci-cd-pipeline-builder** —— 消费密钥的流水线设计
- **docker-development** —— 容器密钥注入模式
- **helm-chart-builder** —— Helm chart 中的 Kubernetes 密钥管理

## 交付标准

满足以下条件才算跑完本技能：

- 轮换计划以 `rotation_schedule_<policy>_<date>.json|md`（来自 `rotation_planner.py --json` 加人工标注）保存在团队安全工作区；每个逾期密钥都有负责人和日期。
- Vault 配置以 `<app>_<auth-method>_config.hcl` 保存；仅在步骤 4 最小权限评审后应用；`vault policy read` 与评审文件一致。
- 审计分析以 `audit_analysis_<date>.json|md` 保存；异常发现项已分诊并有处置结论。
- 完整性验证：同输入重跑每个脚本，能复现已保存的产物（确定性）；新策略的测试 token 恰好读到预期路径，别无其他。
- 边界：本技能绝不存储、打印或读取真实密钥值——只做流程设计。
