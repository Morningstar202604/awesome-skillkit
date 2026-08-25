# Contributing to SkillKit

Thanks for your interest in contributing! This project is a curated collection of skill packs, so contributions fall into two categories: **new skills** and **improvements to the hub itself**.

## How to contribute

1. **Fork** the repository and create a feature branch.
2. Make your changes.
3. Run the quality gates (all must pass):
   - `python tools/validate_skills.py` — skill standard + reference integrity, **0 errors**
   - `python -m pytest skills -q` — all unit tests green
   - `python build.py` — packs still build
4. Open a **Pull Request** with a clear description of what and why.

PRs that fail any gate will not be merged; paste the gate output in the PR description.

## Authoring standards

New and edited skills must follow `docs/SKILL-STANDARD-v2.md` (machine-first writing rules, frontmatter spec, workflow skeleton). Versioning and release policy: `docs/VERSIONING.md`. Strategic direction: `docs/DIRECTION-V2.md`.

## Adding a new skill pack

- The skill must be **self-authored** (no forks of others' work).
- It must contain a `SKILL.md` (at any depth) plus any runtime-required files (`references/`, `scripts/`, `templates/`).
- It should map to one **concrete scenario** and be grounded in a **platform + tool** (see the project positioning in the README).
- Keep the pack focused on its one scenario — a couple of skills for narrow scenarios, more (10+) only when the scenario genuinely spans many platforms (see `content-publishing`).
- Reuse shared helpers from `skills/writing/_common/publish_common.py` (HTTP / dry-run / credentials) instead of re-implementing them.
- Update `manifest.json` and the README tables accordingly.

## Commit conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(skill): add xxx-skill pack
fix(hub): correct install path in install.sh
docs(readme): update quick-pick table
```

## Code style

- Shell scripts: `set -euo pipefail`, POSIX-friendly, no unnecessary defensive code.
- Keep comments to "why", not "what".

## Questions

Open an issue with the `question` label, or reach out via the discussion board.
