---
name: dependency-auditor
description: >-
  Audit and manage dependencies across multi-language projects. Identifies
  vulnerabilities, license conflicts, transitive dependency risks, and
  safe-upgrade paths. Use when auditing third-party packages before release,
  investigating a CVE, planning a major version bump, or running a license
  compliance review. Examples: 'audit our npm dependencies', 'do we have GPL
  contamination', 'plan the upgrade to React 19', 审计依赖 / 依赖安全与许可证 /
  检查过期包 / 升级风险评估. Do NOT use for upgrading dependencies (audit and
  advisory only).
license: Apache-2.0
compatibility: Pure Python 3.10+; the three scripts are offline pattern-matchers over manifests and lockfiles. No network and no API keys required. Pair their findings with `npm audit` / `pip-audit` / `cargo audit` for live CVE coverage.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: code-quality
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Dependency Auditor

Offline, deterministic dependency auditing across 8+ package ecosystems. The
three scripts are pattern-matchers over manifests/lockfiles — they do **not**
call live advisory APIs; pair their findings with `npm audit` / `pip-audit` /
`cargo audit` for current CVE coverage.

---

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Project path | Yes | Repo root or directory containing manifests/lockfiles. |
| Output format | No | `json` (default for scripting) or `text`. |
| Fail threshold | No | `--fail-on-high` makes the scanner exit non-zero on high severity. |
| Risk threshold (planner) | No | `low` \| `medium` \| `high` (default `medium`). |
| Timeline (planner) | No | Days window for the upgrade plan (default `90`). |

If the project path is missing, ask once:

> 请提供：① 项目路径（含 package.json / requirements.txt / go.mod 等的目录）。
> 其余我采用默认值：format=json、risk-threshold=medium、timeline=90 天。

## Pre-flight Self-check

```bash
# 1. Scripts present?
test -f scripts/dep_scanner.py && test -f scripts/license_checker.py \
  && test -f scripts/upgrade_planner.py && echo "scripts-ok" \
  || { echo "ERROR: scripts/ missing — bundle incomplete"; exit 1; }

# 2. Python available?
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# 3. Target contains a recognizable manifest?
ls "$PROJECT"/*.json "$PROJECT"/go.mod "$PROJECT"/Cargo.toml \
  "$PROJECT"/Gemfile "$PROJECT"/pom.xml "$PROJECT"/composer.json 2>/dev/null \
  | grep -q . || { echo "WARN: no known manifest found in $PROJECT"; }
```

## Supported Ecosystems (parsed)

| Language | Manifests parsed |
|---|---|
| JavaScript/Node | package.json, package-lock.json, yarn.lock |
| Python | requirements.txt, pyproject.toml, Pipfile.lock, poetry.lock |
| Go | go.mod, go.sum |
| Rust | Cargo.toml, Cargo.lock |
| Ruby | Gemfile, Gemfile.lock |
| Java | pom.xml, gradle.lockfile |
| PHP | composer.json, composer.lock |
| C#/.NET | packages.config, project.assets.json |

## Workflow

### Step 1: Scan for vulnerabilities

```bash
python3 scripts/dep_scanner.py /path/to/project --format json --fail-on-high -o scan.json
```

Expected: `scan.json` with per-package findings; exit code non-zero if any
`high` severity finding (when `--fail-on-high` is set).
If failed: if no manifest is found, scanner reports 0 findings — re-run with the
correct project path.

### Step 2: Check license compliance

```bash
python3 scripts/license_checker.py /path/to/project --policy strict --format json -o licenses.json
```

Expected: `licenses.json` listing license classification and any conflict
pairs (e.g., GPL in a permissive project).
If failed: `--policy strict` surfaces unknown licenses as manual-review items —
treat unknowns as conflicts until verified.

### Step 3: Plan upgrades

```bash
python3 scripts/upgrade_planner.py scan.json --risk-threshold medium --timeline 90 --format json -o plan.json
```

Expected: `plan.json` ordering upgrades by risk, each with rollback notes.
`--quick-scan` skips transitive deps; `--security-only` limits the plan to
security fixes.
If failed: planner needs `scan.json` from Step 1 — confirm the file exists.

### Verification loop

After applying upgrades, re-run Step 1 and assert **0 high-severity findings**
before closing the audit.

## License Classification

- **Permissive**: MIT, Apache 2.0, BSD (2/3-clause), ISC
- **Copyleft (strong)**: GPL v2/v3, AGPL v3 — flags contamination risk in permissive projects
- **Copyleft (weak)**: LGPL v2.1/v3, MPL 2.0
- **Proprietary / Dual / Unknown** — unknown licenses are surfaced for manual review

The checker analyzes license inheritance through dependency chains and emits
conflict pairs with remediation suggestions.

## Upgrade Risk Matrix

| Risk | Update type | Handling |
|---|---|---|
| Low | Patch, security fixes | Apply immediately |
| Medium | Minor with new features | Batch into scheduled update |
| High | Major version, API changes | Dedicated migration task + tests |
| Critical | Known breaking changes | Planned migration with rollback procedure |

Prioritization: security patches > bug fixes > feature updates > major rewrites.

## Scripts (accurate capability claims)

- **`scripts/dep_scanner.py`** — multi-format parser; built-in offline
  vulnerability pattern set (~16 CVE patterns — a smoke layer, not a replacement
  for live advisories); transitive resolution from lockfiles; JSON + text output.
- **`scripts/license_checker.py`** — license detection from package metadata;
  compatibility matrix across 20+ license types; `--policy permissive|strict`;
  conflict detection with remediation.
- **`scripts/upgrade_planner.py`** — semver-based breaking-change prediction;
  risk-ordered migration plan with testing checklist and timeline estimation.

Sample fixtures: `test-project/` and `test-inventory.json` in this folder;
expected shapes in `expected_outputs/`.

## CI Integration

```bash
# Security gate in CI
python3 scripts/dep_scanner.py . --format json --fail-on-high
python3 scripts/license_checker.py . --policy strict --format json
```

## Failure Handling

| Symptom | Cause | Action |
|---------|-------|--------|
| 0 findings on a known-dep project | wrong project path | re-run with the directory holding the manifest |
| `high` findings block CI | expected with `--fail-on-high` | triage scan.json; patch/pin before merge |
| Unknown-license conflict | unrecognized SPDX id | verify manually, then whitelist with a documented reason |
| Planner errors on missing input | `scan.json` absent | run Step 1 first |

## Delivery Standard

Success = three artifacts produced and reconciled:

- `scan.json` — findings drive which packages to pin/patch now.
- `licenses.json` — conflicts handed to the user as a legal-risk list.
- `plan.json` — upgrades ordered by risk with rollback notes.

Verify: re-run Step 1 after upgrades and confirm 0 high-severity findings.
Save outputs in the project's `audit/` or CI artifact directory. This skill
audits only — it never writes upgrades to the user's manifests.

## References

- `references/vulnerability_assessment_guide.md` — read when interpreting
  scanner findings and deciding which CVE patterns to trust.
- `references/license_compatibility_matrix.md` — read when resolving
  `licenses.json` conflicts and contamination flags.
- `references/dependency_management_best_practices.md` — read for cadence and
  false-positive handling (whitelisting, maintainer contact).

Live advisory commands (not bundled — run in the target repo for current CVE
coverage):

| Ecosystem | Audit Command |
|-----------|---------------|
| Node.js | `npm audit` |
| Python | `pip-audit` |
| Go | `govulncheck` |
| Rust | `cargo audit` |
| Java | `dependency-check` |
| Ruby | `bundle audit` |
| PHP | `composer audit` |
| .NET | `dotnet list package --vulnerable` |
