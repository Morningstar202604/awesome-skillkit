# SkillKit

**English** | [中文](README.zh-CN.md)

Curated skill packs for AI tools. **Download a zip → unzip → drag it into your AI tool's skills directory → it just works.** No more wondering which of a hundred skills you actually need.

## Positioning

**The scenario is the answer — grounded in platform + tool.**

- Each pack maps to one **concrete scenario** ("I want to post to my blog", "I want to post to Zhihu"), not a broad domain like "marketing" or "engineering".
- Details go down to **platform + tool**: e.g. "Blog post on cnblogs.com" (cnblogs.com + API/browser), "Zhihu post" (zhihu.com + Playwright).
- Each pack contains only 3–5 hand-picked skills. Download and go — no bloat.

## Quick Pick

| Skill | Scenario | Platform + Tool | When to use |
|-------|----------|-----------------|-------------|
| [agent-builder-skill](skills/agent-builder-skill/) | Development | Generic + code generation | You want to "build an app/agent" from a one-line requirement without long back-and-forth |
| [chinese-parents-skill](skills/chinese-parents-skill/) | Life | Generic + simulation/diagnosis | You want to understand parents, analyze their type, or don't know how to start the conversation |
| [cnblogs-skill](skills/cnblogs-skill/) | Writing | cnblogs.com + API/browser | You need to publish blog posts, manage your blog, or engage with the community |
| [zhihu-skill](skills/zhihu-skill/) | Writing | zhihu.com + Playwright | You need to publish/edit/delete Zhihu articles, clear drafts, or fix garbled text |

## Getting Started (30 seconds)

1. Download the zip for the skill you need from **Releases** (or use the source directory under `skills/` directly).
2. Unzip it — you get a folder named after the skill (containing `SKILL.md`).
3. **Drag** the whole folder into your AI tool's skills directory:
   - Claude Code: `~/.claude/skills/` (global) or `.claude/skills/` in your project (project-only)
   - Other tools with skills support: use their corresponding skills directory
4. Start a new session — it works immediately, no configuration needed.

> You can also install all skills at once (see "One-Click Install" below).

## One-Click Install

Install all skills into `~/.claude/skills/`:

```bash
# 1. Build the zips first (if dist/ is empty)
bash build.sh

# 2. Linux / macOS
bash install.sh

# Windows (PowerShell)
.\install.ps1
```

Install to a custom directory:

```bash
bash install.sh /path/to/skills-dir
```

## Build & Release

Source lives in `skills/`; zips are published via GitHub Releases (not committed to the repo — `dist/` is gitignored).

```bash
# Generate dist/*.zip
bash build.sh

# Release flow
git tag v1.0.0
git push origin v1.0.0
# Create a release on the GitHub Releases page and upload dist/*.zip
```

## Skill Inventory

Full metadata is in [manifest.json](manifest.json) (name / category / triggers / size).

| Skill | Size | Source |
|-------|------|--------|
| agent-builder-skill | 735 KB | [weed33834/agent-builder-skill](https://github.com/weed33834/agent-builder-skill) |
| chinese-parents-skill | 255 KB | [weed33834/chinese-parents-skill](https://github.com/weed33834/chinese-parents-skill) |
| cnblogs-skill | 29 KB | [weed33834/cnblogs-skill](https://github.com/weed33834/cnblogs-skill) |
| zhihu-skill | 8 KB | [weed33834/zhihu-skill](https://github.com/weed33834/zhihu-skill) |

## Notes

- Only self-authored skill repos are included (no forks).
- Non-core files (`.github`, `.gitignore`, `docker-compose.yml`, etc.) are excluded from the zips; runtime-required content (`SKILL.md`, `references/`, `scripts/`, `templates/`) is kept.
- Per-skill dependencies (e.g. Playwright, login state) are documented in each skill's own `SKILL.md`.

## License

[Apache License 2.0](LICENSE) © 2026 weed33834
