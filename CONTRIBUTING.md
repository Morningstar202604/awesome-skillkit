# Contributing to SkillKit

Thanks for your interest in contributing! This project is a curated collection of skill packs, so contributions fall into two categories: **new skills** and **improvements to the hub itself**.

## How to contribute

1. **Fork** the repository and create a feature branch.
2. Make your changes.
3. Run `bash build.sh` to verify the zips still build.
4. Open a **Pull Request** with a clear description of what and why.

## Adding a new skill pack

- The skill must be **self-authored** (no forks of others' work).
- It must contain a `SKILL.md` (at any depth) plus any runtime-required files (`references/`, `scripts/`, `templates/`).
- It should map to one **concrete scenario** and be grounded in a **platform + tool** (see the project positioning in the README).
- Keep the pack lean: 3–5 skills per scenario, no bloat.
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
