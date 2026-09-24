---
name: terraform-patterns
description: "Terraform infrastructure-as-code agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. Covers module design patterns, state management strategies, provider configuration, security hardening, policy-as-code with Sentinel/OPA, and CI/CD plan/apply workflows. Use when: the user wants to write Terraform, design Terraform modules, manage state backends, review Terraform security, implement multi-region deployments, author IaC modules, or follow IaC best practices. Do NOT use for running terraform apply (pattern authoring only)."
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

> Predictable infrastructure. Secure state. Composable modules. Zero drift.

A Terraform workflow with strong opinions, turning runaway HCL into well-structured, secure, production-grade infrastructure code. It covers module design, state management, provider patterns, security hardening, and CI/CD integration.

This is not a Terraform tutorial — it's a set of concrete decisions about how to write infrastructure code that doesn't blow up at 3 a.m.

## Slash Commands

| Command | Effect |
|---------|-------------|
| `/terraform:review` | Analyze Terraform code for anti-patterns, security issues, and structural problems |
| `/terraform:module` | Design or refactor a Terraform module, standardizing inputs, outputs, and composition |
| `/terraform:security` | Audit Terraform code for security vulnerabilities, secret exposure, and IAM misconfigurations |

## When to Activate

Recognize these phrasings from the user:

- "Review this Terraform code"
- "Design a Terraform module for..."
- "My Terraform state is..."
- "Set up remote state backend"
- "Multi-region Terraform deployment"
- "Terraform security review"
- "Module structure best practices"
- "Terraform CI/CD pipeline"
- Any request involving `.tf` files, HCL, Terraform modules, state management, provider configuration, or infrastructure-as-code

The user has `.tf` files, or wants to create infrastructure with Terraform → this skill applies.

## Input Checklist

Collect everything before scanning. When inputs are missing, ask the user once with this line: "To audit Terraform code, please provide all at once: the Terraform directory path, the target cloud/backend type, and whether there is multi-environment isolation."

| Input | Required | Description |
|---|---|---|
| Terraform directory | Yes | Path to the `.tf` tree, e.g. `./terraform` — the positional argument for both scripts |
| Cloud / backend type | Needed for state review | AWS / GCP / Azure / Terraform Cloud — determines the backend recommendation |
| Environment isolation strategy | Needed for state review | Separate directories vs workspaces vs Terragrunt |
| Module scope | Needed for `/terraform:module` | What the module owns (networking, compute, ...) and who consumes it |

## Pre-flight Checks

```bash
python3 --version        # Expected: Python ≥ 3.8. Both scripts depend only on the standard library.
ls scripts/tf_module_analyzer.py scripts/tf_security_scanner.py
                         # Expected: both files listed.
ls <tf-dir>/*.tf         # Expected: at least one .tf file. Empty → wrong directory.
```

- Python missing or too old → install Python ≥ 3.8, then stop.
- Script files missing → wrong directory; `cd` to this skill's directory and re-check, then stop.
- The target directory has no `.tf` files → confirm the path with the user; don't scan an empty tree and call it a review.

## Workflow

### `/terraform:review` — Terraform Code Review

#### Step 1: Analyze the current state

- **Action:** read all `.tf` files in the target directory; identify the module structure (flat vs nested); count resources, data sources, variables, outputs; check naming conventions.
- **Expected:** an inventory (counts + structure) that can be cited in the report.
- **On failure:** the directory isn't readable → confirm the path with the user; don't review a tree you guessed.

#### Step 2: Apply the review checklist

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

- **Expected:** every line of the checklist marked pass/fail, with file references.
- **On failure:** a line can't be judged from code alone (e.g. state backend) → mark it "needs runtime check"; don't guess.

#### Step 3: Generate the structure report

- **Action:** `python3 scripts/tf_module_analyzer.py assets/terraform`
- **Expected:** a text report listing resource/variable/output analysis and naming checks; exit code 0.
- **On failure:** an argparse error → pass the directory as a positional argument; a parse exception → the HCL may be non-standard; note it in the report.

#### Step 4: Run the security scan

- **Action:** `python3 scripts/tf_security_scanner.py assets/terraform`
- **Expected:** a findings list with severities; exit code 0 (strict mode escalates warnings — use `--strict` in CI).
- **On failure:** findings exist → triage per the `/terraform:security` table below; don't merge when Critical findings exist.

### `/terraform:module` — Module Design

#### Step 1: Define the module scope

- **Action:** one module = one logical group; determine inputs (variables), outputs, and resource boundaries; decide flat vs nested.
- **Expected:** a scope statement naming who consumes the module.
- **On failure:** the scope spans multiple concerns (network + compute + DB) → split it; don't design a god module.

#### Step 2: Apply the module-design checklist

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

- **Expected:** the module is handed to consumers only after the checklist is fully satisfied.
- **On failure:** a variable's type can't be decided → the module boundary was drawn wrong; go back to Step 1.

#### Step 3: Generate the module scaffold

- **Action:** emit the file structure per STRUCTURE (including boilerplate, variable validation blocks, and necessary lifecycle rules).
- **Expected:** files persist to disk and `terraform fmt` is clean.
- **On failure:** `terraform fmt` errors → the generated HCL has syntax problems; fix before delivery.

### `/terraform:security` — Security Audit

#### Step 1: Code-level audit

| Check | Severity | Fix |
|-------|----------|-----|
| Hardcoded secrets in `.tf` files | Critical | Use variables with sensitive = true or a vault |
| IAM policy contains `*` actions | Critical | Narrow to specific actions and resources |
| Security group opens 0.0.0.0/0 to port 22/3389 | Critical | Restrict to known CIDRs, or use SSM/bastion instead |
| S3 bucket unencrypted | High | Add a `server_side_encryption_configuration` block |
| S3 bucket allows public access | High | Add `aws_s3_bucket_public_access_block` |
| RDS unencrypted | High | Set `storage_encrypted = true` |
| RDS publicly accessible | High | Set `publicly_accessible = false` |
| CloudTrail not enabled | Medium | Add an `aws_cloudtrail` resource |
| Stateful resources lacking `prevent_destroy` | Medium | Add `lifecycle { prevent_destroy = true }` |
| Secret-type variables not marked `sensitive = true` | Medium | Add `sensitive = true` to secret variables |

- **Expected:** every line checked against the code; findings mapped to file:line.
- **On failure:** a Critical finding appears → block the merge; fix before any plan/apply.

#### Step 2: State security audit

| Check | Severity | Fix |
|-------|----------|-----|
| Local state file | Critical | Migrate to a remote backend with encryption |
| Remote state unencrypted | High | Enable encryption on the backend (SSE-S3, KMS) |
| No state lock | High | Configure DynamoDB for S3; native lock for TF Cloud |
| State accessible to all team members | Medium | Restrict via IAM policy or TF Cloud teams |

- **Expected:** check the backend config (backend.tf / the terraform {} block); every line has a verdict.
- **On failure:** real secrets found in a local state file → treat as a leak; rotate those credentials (see `env-secrets-manager` / `secrets-vault-manager`).

#### Step 3: Generate the security report

- **Action:** `python3 scripts/tf_security_scanner.py assets/terraform` (add `--output json` in CI; `--strict` escalates warnings)
- **Expected:** the machine-readable findings match the human audit; no Critical finding escapes tracking.
- **On failure:** the scanner disagrees with the human audit → the human cross-check wins; the human table is the source of truth.

## Tools

Both scripts are Python using only the standard library.

| Script | Positional arg | Flags | Purpose |
|---|---|---|---|
| `scripts/tf_module_analyzer.py` | Terraform directory (demo if omitted) | `--output text\|json` | Structure, variables/outputs, naming, composition |
| `scripts/tf_security_scanner.py` | Terraform directory or `.tf` file (demo if omitted) | `--output text\|json`, `--strict` | Secrets, IAM, open SGs, encryption, public access |

```bash
# Analyze a Terraform directory
python3 scripts/tf_module_analyzer.py assets/terraform
python3 scripts/tf_module_analyzer.py assets/terraform --output json
python3 scripts/tf_module_analyzer.py ./modules/vpc

# Scan a Terraform directory
python3 scripts/tf_security_scanner.py assets/terraform
python3 scripts/tf_security_scanner.py assets/terraform --output json
python3 scripts/tf_security_scanner.py assets/terraform --strict
```

## Module Design Patterns

### Pattern 1: Flat modules (small/medium projects)

```text
infrastructure/
├── main.tf          # all resources
├── variables.tf     # all inputs
├── outputs.tf       # all outputs
├── versions.tf      # provider version requirements
├── terraform.tfvars # environment values (not committed)
└── backend.tf       # remote state config
```

Suits: a single app, < 20 resources, one team fully responsible.

### Pattern 2: Nested modules (medium/large projects)

```text
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf          # call modules with dev params
│   │   ├── backend.tf       # dev state backend
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

Suits: multiple environments, shared infrastructure patterns, team collaboration.

### Pattern 3: Terragrunt monorepo

```text
infrastructure/
├── terragrunt.hcl           # root config
├── modules/                  # reusable modules
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── dev/
│   ├── terragrunt.hcl       # dev overrides
│   ├── vpc/
│   │   └── terragrunt.hcl   # module call
│   └── eks/
│       └── terragrunt.hcl
└── prod/
    ├── terragrunt.hcl
    └── ...
```

Suits: large scale, multiple environments, DRY config, team-level isolation.

## Provider Configuration Patterns

### Version Pinning

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"    # allow 5.x, block 6.0
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
```

### Multi-region with Aliases

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

### Multi-account with Assume Role

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

Decision rules: solo development + small project → local state is acceptable, but migrate to remote as soon as possible; Terraform Cloud/Enterprise → use the native backend (built-in locking, encryption, RBAC); AWS → S3 + DynamoDB; GCP → GCS; Azure → Blob Storage. Isolate environments with separate state files — separate directories (recommended) or workspaces (simpler, weaker isolation). All environments sharing one state file: absolutely not.

Backend HCL, migration steps (`state mv`/`import`/`rm`), lock behavior, and the force-unlock process → `references/state-management.md`.

## References

Read only when the corresponding situation arises:

- `references/state-management.md` — when choosing/configuring a backend, migrating state (local→remote, cross-backend), importing existing resources, or handling lock conflicts / force-unlock.
- `references/cicd-and-advanced-patterns.md` — when the task involves CI/CD plan/apply pipelines (GitHub Actions), drift detection, multi-cloud provider aliasing, OpenTofu migration, Infracost cost gates, importing existing infrastructure, or a Terragrunt layout.

## Installation

```bash
# One-line install (any tool)
git clone https://github.com/alirezarezvani/claude-skills.git
cp -r claude-skills/engineering/terraform-patterns ~/.claude/skills/

# Multi-tool install — convert.sh comes from the upstream claude-skills repo (not bundled here):
# https://github.com/alirezarezvani/claude-skills
bash <claude-skills>/scripts/convert.sh --skill terraform-patterns --tool codex|gemini|cursor|windsurf|openclaw

# OpenClaw
clawhub install terraform-patterns
```

## Related Skills

- **senior-devops** — broader DevOps scope (CI/CD, monitoring); use it for pipelines and infrastructure operations.
- **aws-solution-architect** — designing AWS architecture; terraform-patterns handles the implementation.
- **senior-security** — application-layer threats; terraform-patterns covers the infrastructure security posture.
- **ci-cd-pipeline-builder** — automates the deployment of what terraform-patterns defines.

## Failure Handling Table

| Symptom / exit code | Cause | Fix |
|---|---|---|
| `tf_module_analyzer.py` prints a demo report | No directory argument given | Pass the Terraform directory as a positional argument |
| Scanner has no output but the human audit finds problems | The scanner is regex-based, not an HCL parser | The human checklist (Step 1 table) is the source of truth; record the scanner's gaps |
| The scanner's `--strict` makes CI fail on a warning | strict mode escalates warnings | Fix it, or record an accepted warning in the baseline explicitly |
| An HCL parse exception appears in the report | Non-standard/generated HCL | Note it in the report; ask the user to validate with `terraform validate` |
| State secrets found in a local `terraform.tfstate` | Local state carries real values | Treat as a credential leak: rotate the keys, migrate to an encrypted remote backend |
| `python: command not found` | No interpreter | Install Python ≥ 3.8; both scripts use only the standard library |

## Delivery Criteria

This skill counts as done only when:

- The review/security report is saved as `tf_review_<dir>_<date>.md` / `tf_security_<dir>_<date>.md` (or the `--output json` variant), beside the audited tree or in the team's doc area.
- Every Critical finding is either fixed in code or has a tracking issue with an owner; Medium findings have a due date.
- New/refactored modules: all STRUCTURE-checklist files exist, `terraform fmt` is clean, and the README has usage examples.
- Completeness verification: rerunning `tf_security_scanner.py --output json` yields a finding count matching the report; no finding from the human audit floats outside the tracking list.
- Boundary: this skill never runs `terraform plan`/`apply` — it only authors patterns.
