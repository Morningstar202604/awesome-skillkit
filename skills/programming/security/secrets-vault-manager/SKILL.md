---
name: secrets-vault-manager
description: >-
  Use when the user asks to set up secret management infrastructure, integrate HashiCorp Vault, configure cloud secret stores (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager), implement secret rotation, or audit secret access patterns. Triggers on "set up Vault", "vault policies", "AppRole or OIDC auth", "rotate database credentials", "dynamic secrets", "vault audit log", "secret leak response", "External Secrets Operator", using a vault to manage credentials, secret rotation, or auditing secret access. Do NOT use for storing or reading production secret values (workflow design only); local .env hygiene lives in env-secrets-manager.
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

Manages production secret infrastructure for teams running HashiCorp Vault, cloud-native secret stores, or hybrid architectures. Covers policy authoring, auth-method configuration, automated rotation, dynamic secrets, audit logs, and incident response.

**Distinct from env-secrets-manager** — that one handles local `.env` file hygiene and leak detection. This skill operates at the infrastructure layer — Vault clusters, cloud KMS, certificate authorities, and CI/CD secret injection.

## When to Use

- Standing up a new Vault cluster, or migrating to a managed secret store
- Designing auth methods for services, CI runners, and human operators
- Implementing automated credential rotation (databases, API keys, certificates)
- Auditing secret access patterns for compliance (SOC 2, ISO 27001, HIPAA)
- Responding to a secret leak requiring mass revocation
- Wiring secrets into Kubernetes workloads or CI/CD pipelines

## Input Checklist

Collect everything before design. When inputs are missing, ask the user once with this line: "To design secret infrastructure, please provide all at once: the deployment shape (self-hosted Vault / cloud-managed), the list of services and consumers, the existing secret inventory (type / last rotated / owner), and compliance requirements."

| Input | Required | Description |
|---|---|---|
| Deployment shape | Yes | Self-hosted Vault (Raft HA) vs AWS Secrets Manager / Azure Key Vault / GCP Secret Manager vs hybrid |
| Services and consumers list | Yes | Which services, CI runners, and people need which secrets |
| Secret inventory JSON | Needed for rotation planning | Entries with `name`, `type`, `last_rotated` (`YYYY-MM-DD`), `owner` → `rotation_planner.py --inventory` |
| Application requirements | Needed for config generation | App name, auth method, secret types → `vault_config_generator.py` |
| Compliance targets | Needed for audit design | Minimum retention periods for SOC 2 / ISO 27001 / HIPAA |
| Audit log file | Needed for anomaly review | Vault/cloud audit logs (JSON lines or JSON array) → `audit_log_analyzer.py --log-file` |

## Pre-flight Checks

```bash
python3 --version        # Expected: Python ≥ 3.8. All 3 scripts depend only on the standard library.
ls scripts/vault_config_generator.py scripts/rotation_planner.py scripts/audit_log_analyzer.py
                         # Expected: all 3 files listed.
python3 -m json.tool <inventory.json > /dev/null && echo ok
                         # Expected: ok — the inventory JSON is valid.
```

- Python missing or too old → install Python ≥ 3.8, then stop.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then stop.
- Going to operate a real Vault? Verify CLI reachability additionally: `vault status` — expected: prints seal status and cluster info. If unreachable → fix the address/token (export `VAULT_ADDR` and `VAULT_TOKEN` as environment variables — never inline credentials in a command) before running any `vault write`.

## HashiCorp Vault Patterns

### Architecture decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| Deployment mode | HA with Raft storage | No external dependency, built-in leader election |
| Auto-unseal | Cloud KMS (AWS KMS / Azure Key Vault / GCP KMS) | Avoids manual unseal, supports automatic restart |
| Namespaces | One per environment (dev/staging/prod) | Blast-radius isolation, independent policies |
| Audit devices | File + syslog (dual path) | Vault rejects requests when all audit devices fail — dual path prevents outage |

### Auth methods

**AppRole** — machine-to-machine auth for services and batch jobs.

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

**Kubernetes** — Pod-native auth based on service-account tokens.

```hcl
vault write auth/kubernetes/role/api-server \
  bound_service_account_names=api-server \
  bound_service_account_namespaces=production \
  policies=api-server-secrets \
  ttl=1h
```

**OIDC** — human-operator access via an SSO provider (Okta, Azure AD, Google Workspace).

```hcl
vault write auth/oidc/role/engineering \
  bound_audiences="vault" \
  allowed_redirect_uris="https://vault.example.com/ui/vault/auth/oidc/oidc/callback" \
  user_claim="email" \
  oidc_scopes="openid,profile,email" \
  policies="engineering-read" \
  ttl=8h
```

### Secret engines

| Engine | Use case | TTL policy |
|--------|----------|-------------|
| KV v2 | Static secrets (API keys, config) | Versioned, manually rotated |
| Database | Dynamic DB credentials | Default 1h, max 24h |
| PKI | TLS certificates | Leaf certs 90d, intermediate CA 5y |
| Transit | Encryption-as-a-service | Rotate keys every 90d |
| SSH | Signed SSH certificates | Interactive 30m, automation 8h |

### Policy design

Follow least privilege, controlling at the path granularity:

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

**Policy naming convention:** `{service}-{access-level}` (e.g. `payment-service-read`, `api-gateway-admin`).

## Cloud Secret Store Integration

### Comparison matrix

| Feature | AWS Secrets Manager | Azure Key Vault | GCP Secret Manager |
|---------|--------------------|-----------------|--------------------|
| Rotation | Built-in Lambda | Custom logic via Functions | Cloud Functions |
| Versioning | Automatic | Manual or automatic | Automatic |
| Encryption | AWS KMS (default or CMK) | HSM-backed | Google-managed or CMEK |
| Access control | IAM policies + resource policies | RBAC + Access Policies | IAM bindings |
| Cross-region | Replication supported | Geo-redundant by default | Replication supported |
| Audit | CloudTrail | Azure Monitor + Diagnostic Logs | Cloud Audit Logs |
| Billing model | Per secret + per API call | Per operation + per secret | Per secret version + per access |

### Selection guidance

- **AWS Secrets Manager**: RDS/Aurora credential rotation out of the box. Best when fully on AWS.
- **Azure Key Vault**: Strong at certificate management. A must for Azure AD-integrated workloads.
- **GCP Secret Manager**: Simplest API surface. Best for GKE workloads paired with Workload Identity.
- **HashiCorp Vault**: Multi-cloud, dynamic secrets, PKI, transit encryption. Best for complex or hybrid environments.

### SDK access patterns

**Principle:** pull secrets at startup or via a sidecar — never bake them into images or config files.

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

## Secret Rotation Workflow

### Rotation strategy by secret type

| Secret type | Rotation frequency | Method | Downtime risk |
|-------------|-------------------|--------|---------------|
| Database password | 30 days | Dual-account switch | Zero (A/B rotation) |
| API key | 90 days | Mint new, retire old | Zero (overlap window) |
| TLS certificate | 60 days before expiry | ACME or Vault PKI | Zero (graceful reload) |
| SSH key | 90 days | Vault-signed certificates | Zero (CA-based) |
| Service token | 24 hours | Dynamically generated | Zero (short-lived) |
| Encryption key | 90 days | Key versioning (rewrap) | Zero (versions coexist) |

### Database credential rotation (dual-account)

1. Two database accounts exist: `app_user_a` and `app_user_b`
2. The app currently uses `app_user_a`
3. On rotation, rotate `app_user_b`'s password and update the secret store
4. The app switches to `app_user_b` on its next credential pull
5. After a grace period, rotate `app_user_a`'s password
6. Loop

### API key rotation (overlap window)

1. Generate a new API key at the provider
2. Store the new key as `current` in the secret store; move the old one to `previous`
3. Deploy the apps — they read `current`
4. After all instances have restarted (or TTL expired), revoke `previous`
5. Monitoring confirms zero usage of the old key before revocation

## Dynamic Secrets

Dynamic secrets are generated on demand and expire automatically. Wherever feasible, prefer dynamic secrets over static credentials.

### Dynamic database credentials (Vault)

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

### Cloud IAM dynamic credentials

Vault can mint short-lived AWS IAM credentials, Azure service-principal passwords, or GCP service-account keys — eliminating long-lived cloud credentials entirely.

### SSH certificate authority

Replace SSH key distribution with a Vault signed-certificate model:

1. Vault acts as the SSH CA
2. Users/machines request short-TTL (30-minute) signed certificates
3. SSH servers trust the CA public key — no need to maintain `authorized_keys`
4. Certificates expire automatically — no revocation needed for routine operations

## Audit Logging

### What to record

| Event | Priority | Retention |
|-------|----------|-----------|
| Secret read access | HIGH | At least 1 year |
| Secret create/update | HIGH | At least 1 year |
| Auth-method logins | MEDIUM | 90 days |
| Policy changes | CRITICAL | 2 years (compliance) |
| Failed access attempts | CRITICAL | 1 year |
| Token create/revoke | MEDIUM | 90 days |
| Seal/unseal operations | CRITICAL | Permanent |

### Anomaly detection signals

- A secret accessed from a new IP/CIDR range
- A surge in access volume (a path >3x its baseline)
- Off-hours access for human auth methods
- A service accessing secrets outside its policy scope (denied requests)
- Multiple failed authentications from a single source
- A token granted an unusually long TTL

### Compliance reporting

Periodically generate reports covering:

1. **Access inventory** — which identities accessed which secrets when
2. **Rotation compliance** — secrets overdue for rotation
3. **Policy drift** — policies modified since the last review
4. **Orphaned secrets** — secrets with no recent access (>90 days)

Use `audit_log_analyzer.py` to parse Vault or cloud audit logs and extract these signals.

## Workflow: Set Up Rotation + Audit for a Service

### Step 1: Build the secret inventory

- **Action:** enumerate every secret (name, type, `last_rotated` as `YYYY-MM-DD`, owner) into a JSON file.
- **Expected:** the JSON is valid (verified in pre-flight); no entry lacks `last_rotated`.
- **On failure:** a secret's rotation date is unknown → still include it; the planner will flag it overdue, which is the honest state.

### Step 2: Generate the rotation plan

- **Action:** `python3 scripts/rotation_planner.py --inventory secrets.json --policy 30d` (or `60d`/`90d`; add `--json` for CI).
- **Expected:** the plan lists each secret's next rotation due date; entries without `last_rotated` emit a `WARNING` to stderr and are flagged overdue.
- **On failure:** a JSON validation error → fix the inventory; a bad policy tier → only `30d` (aggressive), `60d`, and `90d` are valid.

### Step 3: Generate Vault auth + policy config

- **Action:** `python3 scripts/vault_config_generator.py --app-name <svc> --auth-method approle --secrets db-creds,api-key --environment production`
- **Expected:** renders HCL policy/auth config for the chosen auth method (`approle` / `kubernetes` / `oidc`).
- **On failure:** an argparse error → a required flag is missing; review whether the rendered policy is least-privilege before applying it — the generator is a starting point, not approval.

### Step 4: Review via the change process and apply

- **Action:** have a human review the generated policy; apply it via `vault policy write` / `vault write auth/...`, with `VAULT_TOKEN` in an environment variable.
- **Expected:** `vault policy read <policy>` matches the reviewed content; a test token gets exactly the expected paths and nothing more.
- **On failure:** the test token can read an unexpected path → tighten the path scope before shipping; never "do it later".

### Step 5: Wire up audit-log analysis

- **Action:** `python3 scripts/audit_log_analyzer.py --log-file <vault-audit.log> --threshold 5` (or use `--sample` to see the output shape on synthetic logs).
- **Expected:** `=== Audit Log Analysis Report ===` with summary counts and an anomaly list; exit code 0.
- **On failure:** a real log yields an empty report → confirm the log is JSON lines/array format; if there are no signals, lower `--threshold` (lower = more sensitive).

## Failure Handling Table

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `rotation_planner.py` stderr `WARNING: ... no last_rotated date` | An inventory entry lacks a rotation date | Correct behavior — the secret is recorded as overdue; fill in the date after the first rotation |
| `rotation_planner.py` JSON error | The inventory isn't valid JSON / wrong shape | Validate with `python3 -m json.tool`; entries need `name`/`type`/`last_rotated`/`owner` |
| `vault_config_generator.py` argparse error | Missing `--app-name`/`--auth-method`/`--secrets` | Add the flag per the error; `--auth-method` accepts only `approle`/`kubernetes`/`oidc` |
| The generated policy is wider than needed | Generator defaults | Hand-tighten paths before `vault policy write`; the review step cannot be skipped |
| `vault write` → permission denied | The token lacks management capabilities | Use a management token issued via the change process, not a service token |
| The audit analyzer has no output | Wrong log format or threshold too high | Confirm JSON lines/array; lower `--threshold` |
| Vault is sealed and rejects requests | No auto-unseal on restart | Follow the unseal process (below) — key holders reach quorum, or KMS auto-unseal |
| All audit devices failed → Vault rejects requests | file+syslog both down | Restore at least one audit device first; fail-closed is by design |

## Emergency Procedures

### Secret leak response (execute immediately)

**Time target: stop the bleeding within 15 minutes of discovery.**

1. **Determine scope** — which secrets leaked and where (repo, logs, error messages, third parties)
2. **Revoke immediately** — rotate the leaked credential at the source (provider API, Vault, cloud SM)
3. **Invalidate tokens** — revoke all Vault tokens that accessed the leaked secret
4. **Audit the blast radius** — check audit logs for how the secret was used during the exposure window
5. **Notify stakeholders** — the security team, affected service owners, and compliance (when PII/regulated data is involved)
6. **Post-mortem** — record the root cause and update controls to prevent recurrence

### Vault seal operations

**When to seal:** an active security incident affecting Vault infrastructure, or suspected key compromise.

**Sealing** shuts down all Vault operations. Use it only as a last resort.

**Unseal process:**

1. Gather unseal-key holders to reach quorum (Shamir threshold)
2. Or confirm the auto-unseal KMS key is reachable
3. Unseal via `vault operator unseal`, or restart with auto-unseal
4. Confirm audit devices are reconnected
5. Check active leases and token validity

See `references/emergency_procedures.md` for the full playbook.

## CI/CD Integration

### Vault Agent sidecar (Kubernetes)

Vault Agent runs alongside the app Pod, handling auth and secret rendering:

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

For teams that prefer declarative GitOps over an agent sidecar:

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

Use OIDC federation to eliminate long-lived secrets in CI:

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

## Anti-patterns

| Anti-pattern | Risk | Correct approach |
|-------------|------|-----------------|
| Hard-coding secrets in source | Leakage via repo, logs, error messages | Pull from a secret store at runtime |
| Long-lived static tokens (>30 days) | Stale credentials, no accountability | Dynamic secrets or short TTL + rotation |
| Shared service accounts | No per-consumer audit trail | Independent identities and credentials per service |
| No rotation policy | Compromised credentials live indefinitely | Automated rotation on schedule |
| Secrets in CI environment variables | Visible in build logs, process tables | Vault Agent or OIDC-based injection |
| Single unseal-key holder | Bus factor of 1, recovery blocked | Shamir sharding (3-of-5) or auto-unseal |
| No audit devices configured | Zero visibility into access | Dual audit devices (file + syslog) |
| Wildcard policies (`path "*"`) | Over-privileged, violates least privilege | Explicit per-service, per-path policies |

## Parameter Cheat Sheet

| Script | Key parameters | Description |
|---|---|---|
| `scripts/vault_config_generator.py` | `--app-name`, `--auth-method approle\|kubernetes\|oidc`, `--secrets` (comma-separated types), `--environment`, `--namespace`, `--json` | Renders Vault policy + auth config |
| `scripts/rotation_planner.py` | `--inventory <json>`, `--policy 30d\|60d\|90d`, `--json` | Missing/invalid `last_rotated` → flagged overdue |
| `scripts/audit_log_analyzer.py` | `--log-file <file>`, `--threshold <n>` (lower = more sensitive, default 5), `--json`, `--sample` | JSON lines or JSON array logs |

## References

Read only when the corresponding situation arises:

- `references/vault_patterns.md` — when designing Vault architectures, auth methods, or policies beyond the patterns above.
- `references/cloud_secret_stores.md` — when selecting or integrating AWS/Azure/GCP secret stores (SDK details, rotation hooks, IAM wiring).
- `references/emergency_procedures.md` — read during an active leak/seal incident — the full response playbook, not bedtime reading.

## Cross-References

- **env-secrets-manager** — local `.env` file hygiene, leak detection, drift awareness
- **senior-secops** — security operations, incident response, threat modeling
- **ci-cd-pipeline-builder** — pipeline design that consumes secrets
- **docker-development** — container secret injection patterns
- **helm-chart-builder** — Kubernetes secret management in Helm charts

## Delivery Criteria

This skill counts as done only when:

- The rotation plan is saved in the team's secure workspace as `rotation_schedule_<policy>_<date>.json|md` (from `rotation_planner.py --json` plus human annotation); every overdue secret has an owner and a date.
- Vault config is saved as `<app>_<auth-method>_config.hcl`; applied only after the Step 4 least-privilege review; `vault policy read` matches the reviewed file.
- The audit analysis is saved as `audit_analysis_<date>.json|md`; anomalous findings have been triaged with a disposition.
- Completeness verification: rerunning each script with the same input reproduces the saved artifact (determinism); a test token for the new policy reads exactly the expected paths and nothing else.
- Boundary: this skill never stores, prints, or reads real secret values — it does workflow design only.
