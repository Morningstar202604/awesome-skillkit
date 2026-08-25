# Ship-Gate Check Catalog

> Single source of truth for check semantics: `scripts/ship_gate_scanner.py`
> (`CHECKS` = automated, `MANUAL_CHECKS` = user-confirmed). This document is the
> human/agent-readable index; the scanner is authoritative for behavior.
>
> Tags: `auto` runs without user interaction; `manual` requires user confirmation;
> `stack:` marks checks that are skipped when that stack is not detected.

## Contents
- [Severity model](#severity-model)
- [Automated checks (CHECKS)](#automated-checks-checks)
- [Manual confirmation checks (MANUAL_CHECKS)](#manual-confirmation-checks-manual_checks)
- [Stack detection rules](#stack-detection-rules)

## Severity model

| Severity | Meaning | Verdict impact |
|---|---|---|
| CRITICAL | Must fix before shipping | Any finding → DO NOT SHIP (exit 1) |
| HIGH | Fix or accept documented risk | Only-HIGH findings → SHIP WITH CAUTION (exit 2) |
| ADVISORY | Recommended improvement | Never blocks |

## Automated checks (CHECKS)

| ID | Check | Severity | Stack |
|---|---|---|---|
| SEC-01 | No API keys or secrets in frontend code | CRITICAL | — |
| SEC-04 | CORS not wildcard | CRITICAL | — |
| SEC-05 | CSRF protection on state-changing endpoints | CRITICAL | — |
| SEC-06 | Input validated and sanitized server-side | HIGH | — |
| SEC-07 | Rate limiting on auth and sensitive endpoints | HIGH | — |
| SEC-08 | Passwords hashed with bcrypt or argon2 | CRITICAL | — |
| SEC-11 | CSP headers configured | HIGH | — |
| SEC-13 | No eval() or dangerouslySetInnerHTML without sanitization | HIGH | js |
| SEC-14 | No sensitive data in URLs or logs | HIGH | — |
| SEC-17 | No hardcoded secrets in .env committed to repo | CRITICAL | — |
| SEC-18 | .env files listed in .gitignore | CRITICAL | — |
| DB-03 | Parameterized queries everywhere (no SQL injection) | CRITICAL | — |
| DB-05 | Connection pooling configured | HIGH | — |
| DB-06 | Migrations in version control | HIGH | — |
| DB-07 | RLS enabled on all Supabase tables | CRITICAL | supabase |
| DB-08 | No service_role key in client-side code | CRITICAL | supabase |
| DB-12 | No PII stored unencrypted | HIGH | — |
| DEPLOY-09 | Health check endpoint exists | HIGH | — |
| DEPLOY-10 | Structured logging (not raw console) | HIGH | — |
| CODE-01 | No console.log in production build | HIGH | js |
| CODE-03 | No empty catch blocks | HIGH | — |
| CODE-07 | No TODO-auth or TODO-security patterns | CRITICAL | — |
| CODE-09 | React error boundaries in place | HIGH | react |
| CODE-10 | No leaked stack traces in error responses | HIGH | — |
| CODE-11 | No eslint-disable on security rules | HIGH | js |
| CODE-12 | Lockfile committed | HIGH | — |
| CODE-13 | No wildcard versions in package.json | HIGH | js |
| CODE-14 | TypeScript strict mode enabled | ADVISORY | ts |
| AI-01 | System prompts not leakable via user input | CRITICAL | ai |
| AI-02 | No prompt injection vectors in user inputs | CRITICAL | ai |
| AI-03 | LLM API keys not in frontend code | CRITICAL | ai |
| AI-05 | AI response output sanitized before rendering | HIGH | ai |
| DEP-01 | No git:// or URL-based dependencies | HIGH | — |
| DEP-05 | No suspicious postinstall scripts | HIGH | js |
| DEP-06 | Dependencies pinned (no wildcard *) | HIGH | — |
| FE-01 | Meta tags present (title, description, OG) | ADVISORY | web |
| FE-02 | Favicon configured | ADVISORY | web |
| FE-03 | Custom 404 page exists | ADVISORY | web |
| FE-09 | robots.txt present | ADVISORY | web |
| OBS-01 | Error monitoring configured (Sentry, etc.) | ADVISORY | — |
| OBS-03 | Structured logging with request IDs | ADVISORY | — |

## Manual confirmation checks (MANUAL_CHECKS)

Present each as a checklist item; the user must confirm PASS/FAIL.

| ID | Check | Severity | Stack |
|---|---|---|---|
| SEC-02 | Every route checks authentication | CRITICAL | — |
| SEC-03 | HTTPS enforced, HTTP redirected | CRITICAL | — |
| SEC-10 | Sessions invalidated on logout (server-side) | HIGH | — |
| DB-01 | Backups configured and tested | CRITICAL | — |
| DB-02 | Backup restore tested (not just backup) | CRITICAL | — |
| DB-04 | Separate dev and production databases | HIGH | — |
| DB-11 | App uses a non-root DB user | HIGH | — |
| DEPLOY-01 | All env vars set on production server | CRITICAL | — |
| DEPLOY-02 | SSL certificate installed and valid | CRITICAL | — |
| DEPLOY-05 | Rollback plan exists | HIGH | — |
| DEPLOY-06 | Staging test passed before production | HIGH | — |
| AI-07 | Agent permissions scoped (no unrestricted access) | HIGH | ai |
| AI-08 | No sensitive data sent to third-party LLMs without consent | HIGH | ai |
| FE-04 | Responsive design tested on mobile | HIGH | web |
| OBS-05 | Uptime monitoring configured | HIGH | — |

## Stack detection rules

Detected in Step 1 of SKILL.md from dependency manifests:

| Signal | Stack unlocked |
|---|---|
| `react` / `next` in dependencies | react, web |
| `typescript` in dependencies | ts |
| `@supabase/supabase-js` in dependencies | supabase |
| `openai` in dependencies | ai |
| package.json present | js |
| requirements.txt present | python |

Checks tagged for a missing stack are reported as SKIP, never FAIL.
Scan patterns per category live in `references/patterns.md`.
