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

> Predictable infrastructure. Secure state. Modules that compose. No drift.

Opinionated Terraform workflow that turns sprawling HCL into well-structured, secure, production-grade infrastructure code. Covers module design, state management, provider patterns, security hardening, and CI/CD integration.

Not a Terraform tutorial — a set of concrete decisions about how to write infrastructure code that doesn't break at 3 AM.

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/terraform:review` | Analyze Terraform code for anti-patterns, security issues, and structure problems |
| `/terraform:module` | Design or refactor a Terraform module with proper inputs, outputs, and composition |
| `/terraform:security` | Audit Terraform code for security vulnerabilities, secrets exposure, and IAM misconfigurations |

## When This Skill Activates

Recognize these patterns from the user:

- "Review this Terraform code"
- "Design a Terraform module for..."
- "My Terraform state is..."
- "Set up remote state backend"
- "Multi-region Terraform deployment"
- "Terraform security review"
- "Module structure best practices"
- "Terraform CI/CD pipeline"
- Any request involving: `.tf` files, HCL, Terraform modules, state management, provider configuration, infrastructure-as-code

If the user has `.tf` files or wants to provision infrastructure with Terraform → this skill applies.

## Input checklist

Collect once before scanning. If inputs are missing, ask the user once with: "要审计 Terraform 代码，请一次性提供：Terraform 目录路径、目标云厂商/后端类型、是否含多环境隔离。"

| Input | Required | Description |
|---|---|---|
| Terraform directory | Yes | path to the `.tf` tree, e.g. `./terraform` — positional arg of both scripts |
| Cloud / backend type | For state review | AWS / GCP / Azure / Terraform Cloud — decides backend recommendation |
| Environment strategy | For state review | separate directories vs workspaces vs Terragrunt |
| Module scope | For `/terraform:module` | what the module owns (networking, compute, …) and its consumers |

## Pre-flight checks

```bash
python3 --version        # Expected: Python ≥ 3.8. Both scripts are stdlib-only.
ls scripts/tf_module_analyzer.py scripts/tf_security_scanner.py
                         # Expected: both files listed.
ls <tf-dir>/*.tf         # Expected: at least one .tf file. Empty → wrong directory.
```

- Python missing/outdated → install Python ≥ 3.8, then STOP.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then STOP.
- Target dir has no `.tf` files → confirm the path with the user; do not scan an empty tree and call it a review.

## Workflow

### `/terraform:review` — Terraform Code Review

#### Step 1: Analyze current state

- **Action:** read all `.tf` files in the target directory; identify module structure (flat vs nested); count resources, data sources, variables, outputs; check naming conventions.
- **Expected:** an inventory (counts + structure) you can quote in the report.
- **If it fails:** directory unreadable → confirm path with the user; do not review a guessed tree.

#### Step 2: Apply review checklist

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

- **Expected:** every checklist line marked pass/fail with file references.
- **If it fails:** a line cannot be judged from code alone (e.g. state backend) → mark "needs runtime check" instead of guessing.

#### Step 3: Generate the structural report

- **Action:** `python3 scripts/tf_module_analyzer.py ./terraform`
- **Expected:** text report listing resource/variable/output analysis and naming checks; exit 0.
- **If it fails:** argparse error → pass the directory as positional arg; parse oddities → the HCL may be non-standard, note it in the report.

#### Step 4: Run the security scan

- **Action:** `python3 scripts/tf_security_scanner.py ./terraform`
- **Expected:** findings list with severities; exit 0 (strict mode elevates warnings — use `--strict` in CI).
- **If it fails:** findings exist → triage per the `/terraform:security` table below; do not merge with Critical findings open.

### `/terraform:module` — Module Design

#### Step 1: Identify module scope

- **Action:** one module = one logical grouping; determine inputs (variables), outputs, resource boundaries; decide flat vs nested.
- **Expected:** a one-paragraph scope statement including who consumes the module.
- **If it fails:** scope spans multiple concerns (network + compute + DB) → split; do not design a god-module.

#### Step 2: Apply module design checklist

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

- **Expected:** checklist satisfied before any consumer uses the module.
- **If it fails:** a variable cannot get a type → the module boundary is wrong; revisit Step 1.

#### Step 3: Generate the module scaffold

- **Action:** output the file structure (per STRUCTURE above) with boilerplate, variable validation blocks, and lifecycle rules where appropriate.
- **Expected:** files exist on disk with `terraform fmt` clean formatting.
- **If it fails:** `terraform fmt` errors → syntax problem in generated HCL; fix before handing over.

### `/terraform:security` — Security Audit

#### Step 1: Code-level audit

| Check | Severity | Fix |
|-------|----------|-----|
| Hardcoded secrets in `.tf` files | Critical | Use variables with sensitive = true or vault |
| IAM policy with `*` actions | Critical | Scope to specific actions and resources |
| Security group with 0.0.0.0/0 on port 22/3389 | Critical | Restrict to known CIDR blocks or use SSM/bastion |
| S3 bucket without encryption | High | Add `server_side_encryption_configuration` block |
| S3 bucket with public access | High | Add `aws_s3_bucket_public_access_block` |
| RDS without encryption | High | Set `storage_encrypted = true` |
| RDS publicly accessible | High | Set `publicly_accessible = false` |
| CloudTrail not enabled | Medium | Add `aws_cloudtrail` resource |
| Missing `prevent_destroy` on stateful resources | Medium | Add `lifecycle { prevent_destroy = true }` |
| Variables without `sensitive = true` for secrets | Medium | Add `sensitive = true` to secret variables |

- **Expected:** each row checked against the code; findings mapped to file:line.
- **If it fails:** a Critical finding → block merge; fix before any plan/apply.

#### Step 2: State security audit

| Check | Severity | Fix |
|-------|----------|-----|
| Local state file | Critical | Migrate to remote backend with encryption |
| Remote state without encryption | High | Enable encryption on backend (SSE-S3, KMS) |
| No state locking | High | Enable DynamoDB for S3, native for TF Cloud |
| State accessible to all team members | Medium | Restrict via IAM policies or TF Cloud teams |

- **Expected:** backend config inspected (backend.tf / terraform {} block), each row answered.
- **If it fails:** state file with real secrets found locally → treat as a leak; rotate those credentials (see `env-secrets-manager` / `secrets-vault-manager`).

#### Step 3: Generate the security report

- **Action:** `python3 scripts/tf_security_scanner.py ./terraform` (add `--output json` for CI; `--strict` to elevate warnings)
- **Expected:** machine-readable findings matching the manual audit; no Critical findings left untracked.
- **If it fails:** scanner and manual audit disagree → reconcile; the manual table above is the source of truth.

## Tooling

Both scripts are stdlib-only Python.

| Script | Positional arg | Flags | Purpose |
|---|---|---|---|
| `scripts/tf_module_analyzer.py` | Terraform directory (omit for demo) | `--output text\|json` | structure, variables/outputs, naming, composition |
| `scripts/tf_security_scanner.py` | Terraform dir or `.tf` file (omit for demo) | `--output text\|json`, `--strict` | secrets, IAM, open SGs, encryption, public access |

```bash
# Analyze a Terraform directory
python3 scripts/tf_module_analyzer.py ./terraform
python3 scripts/tf_module_analyzer.py ./terraform --output json
python3 scripts/tf_module_analyzer.py ./modules/vpc

# Scan a Terraform directory
python3 scripts/tf_security_scanner.py ./terraform
python3 scripts/tf_security_scanner.py ./terraform --output json
python3 scripts/tf_security_scanner.py ./terraform --strict
```

## Module Design Patterns

### Pattern 1: Flat Module (Small/Medium Projects)

```text
infrastructure/
├── main.tf          # All resources
├── variables.tf     # All inputs
├── outputs.tf       # All outputs
├── versions.tf      # Provider requirements
├── terraform.tfvars # Environment values (not committed)
└── backend.tf       # Remote state configuration
```

Best for: Single application, < 20 resources, one team owns everything.

### Pattern 2: Nested Modules (Medium/Large Projects)

```text
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf          # Calls modules with dev params
│   │   ├── backend.tf       # Dev state backend
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

Best for: Multiple environments, shared infrastructure patterns, team collaboration.

### Pattern 3: Mono-Repo with Terragrunt

```text
infrastructure/
├── terragrunt.hcl           # Root config
├── modules/                  # Reusable modules
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── dev/
│   ├── terragrunt.hcl       # Dev overrides
│   ├── vpc/
│   │   └── terragrunt.hcl   # Module invocation
│   └── eks/
│       └── terragrunt.hcl
└── prod/
    ├── terragrunt.hcl
    └── ...
```

Best for: Large-scale, many environments, DRY configuration, team-level isolation.

## Provider Configuration Patterns

### Version Pinning
```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"    # Allow 5.x, block 6.0
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
```

### Multi-Region with Aliases
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

### Multi-Account with Assume Role
```hcl
provider "aws" {
  alias  = "production"
  region = "us-east-1"

  assume_role {
    role_arn = "arn:aws:iam::PROD_ACCOUNT_ID:role/TerraformRole"
  }
}
```

## State Management

Decision rules: single dev + tiny project → local state but migrate to remote ASAP; Terraform Cloud/Enterprise → native backend (locking, encryption, RBAC built in); AWS → S3 + DynamoDB; GCP → GCS; Azure → Blob Storage. Environments are isolated by separate state files — separate directories (recommended) or workspaces (simpler, weaker isolation). One state file for all environments: never.

Backend HCL, migration steps (`state mv`/`import`/`rm`), locking behavior, and force-unlock procedures → `references/state-management.md`.

## References

Read the reference only when the corresponding situation applies:

- `references/state-management.md` — read when choosing/configuring a backend, migrating state (local→remote, between backends), importing existing resources, or handling lock contention / force-unlock.
- `references/cicd-and-advanced-patterns.md` — read when the task touches CI/CD plan/apply pipelines (GitHub Actions), drift detection, multi-cloud provider aliasing, OpenTofu migration, Infracost cost gates, importing existing infrastructure, or Terragrunt layouts.

## Installation

```bash
# One-liner (any tool)
git clone https://github.com/alirezarezvani/claude-skills.git
cp -r claude-skills/engineering/terraform-patterns ~/.claude/skills/

# Multi-tool install — convert.sh comes from the upstream claude-skills repo (not bundled here):
# https://github.com/alirezarezvani/claude-skills
bash <claude-skills>/scripts/convert.sh --skill terraform-patterns --tool codex|gemini|cursor|windsurf|openclaw

# OpenClaw
clawhub install terraform-patterns
```

## Related Skills

- **senior-devops** — broader DevOps scope (CI/CD, monitoring); use for pipeline and infrastructure operations.
- **aws-solution-architect** — designs the AWS architecture; terraform-patterns implements it.
- **senior-security** — application-level threats; terraform-patterns covers infrastructure security posture.
- **ci-cd-pipeline-builder** — automates deployment of what terraform-patterns defines.

## Failure handling

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `tf_module_analyzer.py` prints a demo report | no directory argument given | pass the Terraform dir as positional arg |
| Scanner reports nothing but manual audit finds issues | scanner is regex-based, not an HCL parser | manual checklist (Step 1 tables) is the source of truth; file scanner gaps |
| Scanner `--strict` fails CI on warnings | strict mode elevates warnings | fix or explicitly baseline the accepted warnings |
| HCL parse oddities in report | non-standard/generated HCL | note in report; verify by `terraform validate` on the user's side |
| State secrets found in local `terraform.tfstate` | local state with real values | treat as credential leak: rotate secrets, migrate to encrypted remote backend |
| `python: command not found` | no interpreter | install Python ≥ 3.8; both scripts are stdlib-only |

## Deliverables and success criteria

A run of this skill is done when:

- Review/security reports are saved as `tf_review_<dir>_<date>.md` / `tf_security_<dir>_<date>.md` (or the `--output json` variants) next to the audited tree or in the team's docs location.
- Every Critical finding is either fixed in code or has a tracked issue with an owner; Medium findings have a due date.
- New/refactored modules: all files from the STRUCTURE checklist exist, `terraform fmt` clean, README with a usage example.
- Verification of completeness: re-running `tf_security_scanner.py --output json` reproduces the same finding count as the report; no finding appears in the manual audit that is absent from the tracked list.
- Boundary: this skill never runs `terraform plan`/`apply` — pattern authoring only.
