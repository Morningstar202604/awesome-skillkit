---
name: runbook-generator
description: "Generate operational runbooks from a service name — deployment, incident response, maintenance, and rollback workflows. Templated structure customizable per environment. Use when writing an ops manual, generating a runbook, documenting on-call or emergency-response procedures, documenting on-call procedures for a new service, standardizing incident response across teams, or producing runbooks before launching to production. Do NOT use for executing the runbook steps (generation only)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: incident
  pattern: code-generator
  tier: powerful
  verified-date: "2026-09-09"
---

# Runbook Generator

Generates an operable runbook skeleton from a service name: deployment, incident response, maintenance, and rollback workflows, with a templated structure customizable per environment. It only generates; it does not execute the steps inside.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Service name | Required | Positional arg, e.g. `payments-api` |
| `--owner` | Optional | Owning team, written into the runbook header |
| `--output` | Optional | Output path; otherwise prints to stdout |
| Service-specific commands/URLs | Optional | Filled in manually after generation |

When inputs are missing, ask for all at once: "Please provide: (1) service name, (2) owning team (owner, optional), (3) output path (optional, defaults to stdout). Everything else is generated on the default skeleton."

## Pre-flight Checks

```bash
python3 scripts/runbook_generator.py --help >/dev/null 2>&1   # expected exit code 0; on failure: script/python3 missing → STOP
```

## Workflow

### Step 1: Generate the skeleton

```bash
# Print to stdout
python3 scripts/runbook_generator.py payments-api
# Write to a file
python3 scripts/runbook_generator.py payments-api --owner platform --output docs/runbooks/payments-api.md
```

Expected: output is a runbook skeleton with the standard start/stop/health/rollback sections; written to the target path with `--output`.
On failure: the `--output` parent directory doesn't exist → `mkdir -p` the target directory first, then write; the service name is missing → prompt for the positional arg.

### Step 2: Fill in service-specific content

- Replace placeholders with real commands and URLs (every step must be copy-pasteable).
- Add a health check for every critical step; define rollback triggers and rollback commands.

### Step 3: Rehearse on staging and commit

- Dry-run to verify the expected output of each step on staging.
- Commit to version control beside the service code, and have the on-call team review it.

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| Positional arg | service name | e.g. `payments-api` |
| `--owner` | team name | Responsible party in the runbook header |
| `--output` | file path | Output location; omitted = stdout |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `--output` write failure | Parent directory missing | `mkdir -p` the target directory and rerun |
| Service name missing | No positional arg given | Fill in the service name |
| A runbook step errors when copied to production | Placeholder commands weren't replaced with real service names/paths | Replace all `<service>` placeholders and run each step live on staging to verify |
| A rollback step fails in rehearsal | The old-version image the rollback script relies on was pruned | Check the image retention policy; point the rollback script to a long-lived tag |
| The on-call contact is wrong | The template's owner is a placeholder or has left the team | Take the person on shift from the rota and write them in; set a quarterly review reminder |

## Delivery Criteria

Definition of success: every command is copy-pasteable, every critical step has expected output, the rollback steps are verified on staging, the owner/escalation contact is current, health checks are complete, and it's committed to version control with on-call review.
Artifact naming: `<service>.md` (or what `--output` specifies).
Save location: beside the service code (e.g. `docs/runbooks/`), committed to version control.
Completeness verification: check off the runbook quality checklist line by line — commands are pasteable, have expected output, rollback is tested, owner is current, includes an incident-communication template, includes a post-incident update process.

## Safety Red Lines

- **Generate only; do not execute**: this skill does not run any command inside the runbook (deploy/rollback/restart). Actual execution is done by on-call during rehearsal/incidents, with user confirmation.
- Rollback triggers and commands must be verified on staging before being written into the production runbook.

## References

- `references/runbook-templates.md` — reference templates for deployment and incident playbooks
