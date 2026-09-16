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

Production secret infrastructure management for teams running HashiCorp Vault, cloud-native secret stores, or hybrid architectures. This skill covers policy authoring, auth method configuration, automated rotation, dynamic secrets, audit logging, and incident response.

**Distinct from env-secrets-manager** which handles local `.env` file hygiene and leak detection. This skill operates at the infrastructure layer — Vault clusters, cloud KMS, certificate authorities, and CI/CD secret injection.

## When to use

- Standing up a new Vault cluster or migrating to a managed secret store
- Designing auth methods for services, CI runners, and human operators
- Implementing automated credential rotation (database, API keys, certificates)
- Auditing secret access patterns for compliance (SOC 2, ISO 27001, HIPAA)
- Responding to a secret leak that requires mass revocation
- Integrating secrets into Kubernetes workloads or CI/CD pipelines

## Input checklist

Collect once before designing. If inputs are missing, ask the user once with: "要设计密钥基础设施，请一次性提供：部署形态（Vault 自建 / 云托管）、服务与消费者清单、现有密钥盘点（类型/最近轮换时间/负责人）、合规要求。"

| Input | Required | Description |
|---|---|---|
| Deployment form | Yes | self-hosted Vault (Raft HA) vs AWS Secrets Manager / Azure Key Vault / GCP Secret Manager vs hybrid |
| Service & consumer list | Yes | which services, CI runners, humans need which secrets |
| Secret inventory JSON | For rotation planning | entries with `name`, `type`, `last_rotated` (`YYYY-MM-DD`), `owner` → `rotation_planner.py --inventory` |
| App requirements | For config generation | app name, auth method, secret types → `vault_config_generator.py` |
| Compliance targets | For audit design | SOC 2 / ISO 27001 / HIPAA retention minimums |
| Audit log files | For anomaly review | Vault/cloud audit logs (JSON lines or JSON array) → `audit_log_analyzer.py --log-file` |

## Pre-flight checks

```bash
python3 --version        # Expected: Python ≥ 3.8. All 3 scripts are stdlib-only.
ls scripts/vault_config_generator.py scripts/rotation_planner.py scripts/audit_log_analyzer.py
                         # Expected: all 3 files listed.
python3 -m json.tool <inventory.json > /dev/null && echo ok
                         # Expected: ok — inventory JSON is valid.
```

- Python missing/outdated → install Python ≥ 3.8, then STOP.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then STOP.
- Driving a live Vault? Also verify CLI reachability: `vault status` — expected: seal state and cluster info printed. Unreachable → fix address/token (export `VAULT_ADDR`, `VAULT_TOKEN` as environment variables — never inline credentials in commands) before any `vault write`.

## HashiCorp Vault Patterns

### Architecture Decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| Deployment mode | HA with Raft storage | No external dependency, built-in leader election |
| Auto-unseal | Cloud KMS (AWS KMS / Azure Key Vault / GCP KMS) | Eliminates manual unseal, enables automated restarts |
| Namespaces | One per environment (dev/staging/prod) | Blast-radius isolation, independent policies |
| Audit devices | File + syslog (dual) | Vault refuses requests if all audit devices fail — dual prevents outages |

### Auth Methods

**AppRole** — Machine-to-machine authentication for services and batch jobs.

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

**Kubernetes** — Pod-native authentication via service account tokens.

```hcl
vault write auth/kubernetes/role/api-server \
  bound_service_account_names=api-server \
  bound_service_account_namespaces=production \
  policies=api-server-secrets \
  ttl=1h
```

**OIDC** — Human operator access via SSO provider (Okta, Azure AD, Google Workspace).

```hcl
vault write auth/oidc/role/engineering \
  bound_audiences="vault" \
  allowed_redirect_uris="https://vault.example.com/ui/vault/auth/oidc/oidc/callback" \
  user_claim="email" \
  oidc_scopes="openid,profile,email" \
  policies="engineering-read" \
  ttl=8h
```

### Secret Engines

| Engine | Use Case | TTL Strategy |
|--------|----------|-------------|
| KV v2 | Static secrets (API keys, config) | Versioned, manual rotation |
| Database | Dynamic DB credentials | 1h default, 24h max |
| PKI | TLS certificates | 90d leaf certs, 5y intermediate CA |
| Transit | Encryption-as-a-service | Key rotation every 90d |
| SSH | Signed SSH certificates | 30m for interactive, 8h for automation |

### Policy Design

Follow least-privilege with path-based granularity:

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

**Policy naming convention:** `{service}-{access-level}` (e.g., `payment-service-read`, `api-gateway-admin`).

## Cloud Secret Store Integration

### Comparison Matrix

| Feature | AWS Secrets Manager | Azure Key Vault | GCP Secret Manager |
|---------|--------------------|-----------------|--------------------|
| Rotation | Built-in Lambda | Custom logic via Functions | Cloud Functions |
| Versioning | Automatic | Manual or automatic | Automatic |
| Encryption | AWS KMS (default or CMK) | HSM-backed | Google-managed or CMEK |
| Access control | IAM policies + resource policy | RBAC + Access Policies | IAM bindings |
| Cross-region | Replication supported | Geo-redundant by default | Replication supported |
| Audit | CloudTrail | Azure Monitor + Diagnostic Logs | Cloud Audit Logs |
| Pricing model | Per-secret + per-API call | Per-operation + per-key | Per-secret version + per-access |

### When to Use Which

- **AWS Secrets Manager**: RDS/Aurora credential rotation out of the box. Best when fully on AWS.
- **Azure Key Vault**: Certificate management strength. Required for Azure AD integrated workloads.
- **GCP Secret Manager**: Simplest API surface. Best for GKE-native workloads with Workload Identity.
- **HashiCorp Vault**: Multi-cloud, dynamic secrets, PKI, transit encryption. Best for complex or hybrid environments.

### SDK Access Patterns

**Principle:** Always fetch secrets at startup or via sidecar — never bake into images or config files.

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

## Secret Rotation Workflows

### Rotation Strategy by Secret Type

| Secret Type | Rotation Frequency | Method | Downtime Risk |
|-------------|-------------------|--------|---------------|
| Database passwords | 30 days | Dual-account swap | Zero (A/B rotation) |
| API keys | 90 days | Generate new, deprecate old | Zero (overlap window) |
| TLS certificates | 60 days before expiry | ACME or Vault PKI | Zero (graceful reload) |
| SSH keys | 90 days | Vault-signed certificates | Zero (CA-based) |
| Service tokens | 24 hours | Dynamic generation | Zero (short-lived) |
| Encryption keys | 90 days | Key versioning (rewrap) | Zero (version coexistence) |

### Database Credential Rotation (Dual-Account)

1. Two database accounts exist: `app_user_a` and `app_user_b`
2. Application currently uses `app_user_a`
3. Rotation rotates `app_user_b` password, updates secret store
4. Application switches to `app_user_b` on next credential fetch
5. After grace period, `app_user_a` password is rotated
6. Cycle repeats

### API Key Rotation (Overlap Window)

1. Generate new API key with provider
2. Store new key in secret store as `current`, move old to `previous`
3. Deploy applications — they read `current`
4. After all instances restarted (or TTL expired), revoke `previous`
5. Monitoring confirms zero usage of old key before revocation

## Dynamic Secrets

Dynamic secrets are generated on-demand with automatic expiration. Prefer dynamic secrets over static credentials wherever possible.

### Database Dynamic Credentials (Vault)

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

### Cloud IAM Dynamic Credentials

Vault can generate short-lived AWS IAM credentials, Azure service principal passwords, or GCP service account keys — eliminating long-lived cloud credentials entirely.

### SSH Certificate Authority

Replace SSH key distribution with a Vault-signed certificate model:

1. Vault acts as SSH CA
2. Users/machines request signed certificates with short TTL (30 min)
3. SSH servers trust the CA public key — no `authorized_keys` management
4. Certificates expire automatically — no revocation needed for normal operations

## Audit Logging

### What to Log

| Event | Priority | Retention |
|-------|----------|-----------|
| Secret read access | HIGH | 1 year minimum |
| Secret creation/update | HIGH | 1 year minimum |
| Auth method login | MEDIUM | 90 days |
| Policy changes | CRITICAL | 2 years (compliance) |
| Failed access attempts | CRITICAL | 1 year |
| Token creation/revocation | MEDIUM | 90 days |
| Seal/unseal operations | CRITICAL | Indefinite |

### Anomaly Detection Signals

- Secret accessed from new IP/CIDR range
- Access volume spike (>3x baseline for a path)
- Off-hours access for human auth methods
- Service accessing secrets outside its policy scope (denied requests)
- Multiple failed auth attempts from single source
- Token created with unusually long TTL

### Compliance Reporting

Generate periodic reports covering:

1. **Access inventory** — Which identities accessed which secrets, when
2. **Rotation compliance** — Secrets overdue for rotation
3. **Policy drift** — Policies modified since last review
4. **Orphaned secrets** — Secrets with no recent access (>90 days)

Use `audit_log_analyzer.py` to parse Vault or cloud audit logs for these signals.

## Workflow: Stand up rotation + audit for a service

### Step 1: Build the secret inventory

- **Action:** enumerate every secret (name, type, `last_rotated` as `YYYY-MM-DD`, owner) into a JSON file.
- **Expected:** valid JSON (checked in pre-flight); no entry missing `last_rotated`.
- **If it fails:** a secret's rotation date is unknown → include it anyway; the planner marks it overdue, which is the honest state.

### Step 2: Generate the rotation schedule

- **Action:** `python3 scripts/rotation_planner.py --inventory secrets.json --policy 30d` (or `60d`/`90d`; add `--json` for CI).
- **Expected:** a schedule listing each secret's next rotation due date; entries without `last_rotated` print a stderr `WARNING` and are marked overdue.
- **If it fails:** JSON validation error → fix the inventory; wrong policy tier → the 3 policies are `30d` (aggressive), `60d`, `90d` only.

### Step 3: Generate Vault auth + policy config

- **Action:** `python3 scripts/vault_config_generator.py --app-name <svc> --auth-method approle --secrets db-creds,api-key --environment production`
- **Expected:** HCL policy/auth config rendered for the requested auth method (`approle` / `kubernetes` / `oidc`).
- **If it fails:** argparse error → a required flag is missing; review the rendered policy for least privilege before applying — the generator is a starting point, not an approval.

### Step 4: Review and apply through change control

- **Action:** human reviews the generated policies; apply via `vault policy write` / `vault write auth/...` with `VAULT_TOKEN` in the environment.
- **Expected:** `vault policy read <policy>` shows the reviewed content; a test token gets exactly the intended paths and nothing more.
- **If it fails:** test token can read unintended paths → tighten path scopes before rollout; never "fix later".

### Step 5: Wire audit log analysis

- **Action:** `python3 scripts/audit_log_analyzer.py --log-file <vault-audit.log> --threshold 5` (or `--sample` to see output shape on a synthetic log).
- **Expected:** `=== Audit Log Analysis Report ===` with summary counts and anomaly list; exit 0.
- **If it fails:** empty report on a real log → check the log is JSON lines/array format; lower `--threshold` (lower = more sensitive) if nothing surfaces.

## Failure handling

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `rotation_planner.py` stderr `WARNING: ... no last_rotated date` | inventory entry lacks rotation date | correct — secret is tracked as overdue; fill the date after its first rotation |
| `rotation_planner.py` JSON error | inventory not valid JSON / wrong shape | validate with `python3 -m json.tool`; entries need `name`/`type`/`last_rotated`/`owner` |
| `vault_config_generator.py` argparse error | missing `--app-name`/`--auth-method`/`--secrets` | add the flag named in the error; `--auth-method` accepts only `approle`/`kubernetes`/`oidc` |
| Generated policy broader than needed | generator defaults | hand-tighten paths before `vault policy write`; the review step is mandatory |
| `vault write` → permission denied | token lacks management capabilities | use a management token from the change process, not a service token |
| Audit analyzer reports nothing | wrong log format or threshold too high | confirm JSON lines/array; lower `--threshold` |
| Vault sealed and refusing requests | restart without auto-unseal | follow Unseal procedure (below) — quorum of key holders or KMS auto-unseal |
| Audit devices all failed → Vault refuses requests | file+syslog both down | restore at least one audit device; this fail-closed behavior is by design |

## Emergency Procedures

### Secret Leak Response (Immediate)

**Time target: Contain within 15 minutes of detection.**

1. **Identify scope** — Which secret(s) leaked, where (repo, log, error message, third party)
2. **Revoke immediately** — Rotate the compromised credential at the source (provider API, Vault, cloud SM)
3. **Invalidate tokens** — Revoke all Vault tokens that accessed the leaked secret
4. **Audit blast radius** — Query audit logs for usage of the compromised secret in the exposure window
5. **Notify stakeholders** — Security team, affected service owners, compliance (if PII/regulated data)
6. **Post-mortem** — Document root cause, update controls to prevent recurrence

### Vault Seal Operations

**When to seal:** Active security incident affecting Vault infrastructure, suspected key compromise.

**Sealing** stops all Vault operations. Use only as last resort.

**Unseal procedure:**
1. Gather quorum of unseal key holders (Shamir threshold)
2. Or confirm auto-unseal KMS key is accessible
3. Unseal via `vault operator unseal` or restart with auto-unseal
4. Verify audit devices reconnected
5. Check active leases and token validity

See `references/emergency_procedures.md` for complete playbooks.

## CI/CD Integration

### Vault Agent Sidecar (Kubernetes)

Vault Agent runs alongside application pods, handles authentication and secret rendering:

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

### External Secrets Operator (Kubernetes)

For teams preferring declarative GitOps over agent sidecars:

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

Eliminate long-lived secrets in CI by using OIDC federation:

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

## Anti-Patterns

| Anti-Pattern | Risk | Correct Approach |
|-------------|------|-----------------|
| Hardcoded secrets in source code | Leak via repo, logs, error output | Fetch from secret store at runtime |
| Long-lived static tokens (>30 days) | Stale credentials, no accountability | Dynamic secrets or short TTL + rotation |
| Shared service accounts | No audit trail per consumer | Per-service identity with unique credentials |
| No rotation policy | Compromised creds persist indefinitely | Automated rotation on schedule |
| Secrets in environment variables on CI | Visible in build logs, process table | Vault Agent or OIDC-based injection |
| Single unseal key holder | Bus factor of 1, recovery blocked | Shamir split (3-of-5) or auto-unseal |
| No audit device configured | Zero visibility into access | Dual audit devices (file + syslog) |
| Wildcard policies (`path "*"`) | Over-permissioned, violates least privilege | Explicit path-based policies per service |

## Parameter quick reference

| Script | Key parameters | Notes |
|---|---|---|
| `scripts/vault_config_generator.py` | `--app-name`, `--auth-method approle\|kubernetes\|oidc`, `--secrets` (comma-separated types), `--environment`, `--namespace`, `--json` | renders Vault policy + auth config |
| `scripts/rotation_planner.py` | `--inventory <json>`, `--policy 30d\|60d\|90d`, `--json` | missing/invalid `last_rotated` → marked overdue |
| `scripts/audit_log_analyzer.py` | `--log-file <file>`, `--threshold <n>` (lower = more sensitive, default 5), `--json`, `--sample` | JSON lines or JSON array logs |

## References

Read the reference only when the corresponding situation applies:

- `references/vault_patterns.md` — read when designing Vault architecture, auth methods, or policies beyond the patterns above.
- `references/cloud_secret_stores.md` — read when choosing or integrating AWS/Azure/GCP secret stores (SDK details, rotation hooks, IAM wiring).
- `references/emergency_procedures.md` — read during a leak/seal incident — complete response playbooks, not background reading.

## Cross-References

- **env-secrets-manager** — Local `.env` file hygiene, leak detection, drift awareness
- **senior-secops** — Security operations, incident response, threat modeling
- **ci-cd-pipeline-builder** — Pipeline design where secrets are consumed
- **docker-development** — Container secret injection patterns
- **helm-chart-builder** — Kubernetes secret management in Helm charts

## Deliverables and success criteria

A run of this skill is done when:

- Rotation plan saved as `rotation_schedule_<policy>_<date>.json|md` (from `rotation_planner.py --json` plus human annotations) in the team's security workspace; every overdue secret has an owner and a date.
- Vault config saved as `<app>_<auth-method>_config.hcl`; applied only after the Step 4 least-privilege review; `vault policy read` matches the reviewed file.
- Audit analysis saved as `audit_analysis_<date>.json|md`; anomaly findings triaged with dispositions.
- Verification of completeness: re-running each script with the same inputs reproduces the saved artifacts (deterministic); a test token for the new policy reads exactly its intended paths and nothing else.
- Boundary: this skill never stores, prints, or reads real secret values — workflow design only.
