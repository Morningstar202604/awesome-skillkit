# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-08-23

### Fixed

- **skill-tester**: the entire `scripts/` suite advertised by SKILL.md was missing. Implemented all four tools for real: `skill_validator.py` (structure/tier compliance), `script_tester.py` (syntax/imports/runtime with timeout), `quality_scorer.py` (4×25% scoring, `--include-security` rebalances to 5×20%, `--minimum-score` CI gate), `security_scorer.py` (four-component security posture, 53 unit tests pass). Also restored the two reference docs (`skill-structure-specification.md`, `tier-requirements-matrix.md`) and gave the bundled sample skill proper YAML frontmatter; regenerated its golden validation report.
- **env-secrets-manager**: `scripts/env_auditor.py` (referenced 4× as the core tool) did not exist. Implemented a real auditor: provider-key detection (OpenAI/GitHub/AWS/PEM/Slack/JWT), sensitive-assignment detection, `.gitignore` coverage check, `.env ↔ .env.example` drift, rotation-date awareness; output values always redacted. Added README, sample fixture + golden audit report, and 12 unit tests (65 total across both fixed skills).
- **quality_scorer**: security dimension now correctly maps the 0–25 component scale to a percentage (was reporting ~20 instead of ~80).

### Added

- `build.py` — cross-platform packaging (same semantics as `build.sh`) so Windows users can build without bash/zip.
- `_all.zip` convenience bundle — every skill from every pack in a single download (37 skills).

### Changed

- **Merged near-duplicate skills** to stop shipping reinvented wheels:
  - `database-schema-designer` merged into `database-designer` (>70% overlap). Unique material preserved in `references/schema-design-playbook.md` (multi-tenancy, RLS policies, seed data) and `references/full-schema-examples.md`.
  - `agent-workflow-designer` merged into `agent-designer`. Pattern templates and handoff contract preserved in `references/workflow_patterns.md`; `workflow_scaffolder.py` moved over.
  - Total curated skills: 35 → 33.
- **observability-designer**: dropped its duplicate `slo_designer.py`; SLO work now routes cleanly to `slo-architect` (docs updated).
- **code-reviewer / pr-review-expert**: disambiguated trigger phrases — code-reviewer is the static-analysis engine, pr-review-expert owns the end-to-end PR review workflow.
- **env-secrets-manager**: trimmed sections duplicating `secrets-vault-manager` (cloud store comparison, rotation execution, audit logging) into cross-references; this skill keeps env hygiene and detection.

### Security

- Removed stray working file from agent-builder-skill; zhihu-content-manager SKILL.md now carries proper YAML frontmatter so tools can load it.
- **Removed personal account data from the public skills**: `cnblogs-skill` and `zhihu-content-manager` no longer hardcode username/blogId/column IDs/article ledgers in SKILL.md. Account data moved to gitignored `references/account.local.json` (shipped template: `account.example.json`); `*.local.json` is excluded from git and from all scene-pack zips (verified).
- Added `.github/workflows/skill-quality.yml`: runs bundled unit tests, builds all packs, and gates changed skills on YAML frontmatter presence + dangling script references.
- Added `sync-mirrors.ps1` for pushing to gitcode/github/gitee mirrors (tokens via env vars, never stored).

## [1.2.0] - 2026-08-18

### Changed

- Restructured from per-skill zips into scene packs: one pack = one real-world scenario containing multiple skills.
- 16 scene packs covering coding, ops, writing and life scenarios.
- 35 developer skills curated from `alirezarezvani/claude-skills` (MIT), combined with 4 self-authored skills.
- `build.sh` now packages by scene pack (`packs/*/pack.json` → `dist/*.zip`).
- `manifest.json` now lists packs with per-skill source attribution.

### Added

- 16 curated scene packs under `packs/`.
- Source attribution for every skill (`alirezarezvani/claude-skills (MIT)` / `weed33834 (self-authored)`).

## [Unreleased]

### Added

- Initial SkillKit hub: curated skill packs for AI tools.
- Positioning: "the scenario is the answer — grounded in platform + tool".
- 4 self-authored skill packs:
  - `agent-builder-skill` — one-line requirement to a production-grade AI agent.
  - `chinese-parents-skill` — Chinese-parent behavior simulation / diagnosis / coping.
  - `cnblogs-skill` — automated blog publishing & management on cnblogs.com.
  - `zhihu-skill` — Zhihu article publishing & management.
- `build.sh` — one-command packaging of `skills/*` into `dist/*.zip`.
- `install.sh` / `install.ps1` — one-click install of all packs.
- Bilingual docs: English primary (`README.md`) + Chinese (`README.zh-CN.md`).
- License: Apache License 2.0.
