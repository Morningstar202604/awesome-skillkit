---
name: runbook-generator
description: "Generate operational runbooks from a service name — deployment, incident response, maintenance, and rollback workflows. Templated structure customizable per environment. Use when documenting on-call procedures for a new service, standardizing incident response across teams, or producing runbooks before launching to production. 当用户要求 写运维手册 / runbook / 应急处置步骤 时使用。 Do NOT use for executing the runbook steps (generation only)."
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

**Tier:** POWERFUL
**Category:** Engineering
**Domain:** DevOps / Site Reliability Engineering

---

## Overview

Generate operational runbooks quickly from a service name, then customize for deployment, incident response, maintenance, and rollback workflows.

## Core Capabilities

- Runbook skeleton generation from a CLI
- Standard sections for start/stop/health/rollback
- Structured escalation and incident handling placeholders
- Reference templates for deployment and incident playbooks

---

## When to Use

- A service has no runbook and needs a baseline immediately
- Existing runbooks are inconsistent across teams
- On-call onboarding requires standardized operations docs
- You need repeatable runbook scaffolding for new services

---

## Quick Start

```bash
# Print runbook to stdout
python3 scripts/runbook_generator.py payments-api

# Write runbook file
python3 scripts/runbook_generator.py payments-api --owner platform --output docs/runbooks/payments-api.md
```

---

## Recommended Workflow

1. Generate the initial skeleton with `scripts/runbook_generator.py`.
2. Fill in service-specific commands and URLs.
3. Add verification checks and rollback triggers.
4. Dry-run in staging.
5. Store runbook in version control near service code.

---

## Reference Docs

- `references/runbook-templates.md`

---

## Common Pitfalls

- Missing rollback triggers or rollback commands
- Steps without expected output checks
- Stale ownership/escalation contacts
- Runbooks never tested outside of incidents

## Best Practices

1. Keep every command copy-pasteable.
2. Include health checks after every critical step.
3. Validate runbooks on a fixed review cadence.
4. Update runbook content after incidents and postmortems.

---

## Runbook Quality Checklist

- [ ] Every command is copy-pasteable (no screenshots)
- [ ] Expected output is documented for each command
- [ ] Rollback steps are tested in staging
- [ ] Ownership and escalation contacts are current
- [ ] Health checks exist for each critical component
- [ ] Runbook is stored in version control near service code
- [ ] Runbook has been reviewed by on-call team
- [ ] Incident communication templates are included
- [ ] Post-incident runbook update process is defined

---

## Maintenance Schedule

| Frequency | Action |
|-----------|--------|
| **Weekly** | Review on-call handoff notes for runbook gaps |
| **Monthly** | Verify all health check endpoints are responding |
| **Quarterly** | Full runbook review with on-call team |
| **Post-Incident** | Update runbook based on incident learnings |