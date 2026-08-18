# awesome-skillkit

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
| [agent-builder-skill](skills/programming/ai-agents/agent-builder-skill/) | Programming > AI Agents | Generic + code generation | You want to "build an app/agent" from a one-line requirement without long back-and-forth |
| [chinese-parents-skill](skills/life/family/chinese-parents-skill/) | Life > Family | Generic + simulation/diagnosis | You want to understand parents, analyze their type, or don't know how to start the conversation |
| [cnblogs-skill](skills/writing/blog/cnblogs-skill/) | Writing > Blog | cnblogs.com + API/browser | You need to publish blog posts, manage your blog, or engage with the community |
| [zhihu-content-manager](skills/writing/zhihu/zhihu-content-manager/) | Writing > Zhihu | zhihu.com + Playwright | You need to publish/edit/delete Zhihu articles, clear drafts, or fix garbled text |

## Directory Layout

Skills are organized by **scenario → sub-scenario** (multi-level directories), so you can find the right pack by browsing the tree instead of reading a flat list.

```
skills/
├── programming/
│   ├── ai-agents/
│   │   └── agent-builder-skill/        # one-line requirement -> production-grade AI agent
│   ├── ai-engineering/                 # mcp-server-builder, feature-flags-architect, self-eval, skill-tester
│   ├── api/                            # api-design-reviewer, api-test-suite-builder
│   ├── architecture/                   # senior-architect, migration-architect, monorepo-navigator
│   ├── cicd/                           # ci-cd-pipeline-builder, ship-gate, spec-driven-workflow
│   ├── code-quality/                   # code-reviewer, tdd-guide, tech-debt-tracker, dependency-auditor
│   ├── containers/                     # docker-development, helm-chart-builder
│   ├── database/                       # database-designer, database-schema-designer, sql-database-assistant
│   ├── github/                         # pr-review-expert, git-worktree-manager, changelog-generator
│   ├── incident/                       # incident-commander, runbook-generator, slo-architect
│   ├── infrastructure/                 # kubernetes-operator, observability-designer, terraform-patterns
│   ├── performance/                    # performance-profiler
│   ├── security/                       # env-secrets-manager, secrets-vault-manager
│   └── workflow/                       # agent-designer, agent-workflow-designer
├── writing/
│   ├── blog/
│   │   └── cnblogs-skill/              # publish & manage posts on cnblogs.com
│   └── zhihu/
│       └── zhihu-content-manager/      # publish/edit/delete Zhihu articles
└── life/
    └── family/
        └── chinese-parents-skill/      # understand & talk to Chinese parents
```

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
| chinese-parents-skill | 559 KB | [weed33834/chinese-parents-skill](https://github.com/weed33834/chinese-parents-skill) |
| agent-builder-skill | 1923 KB | [weed33834/agent-builder-skill](https://github.com/weed33834/agent-builder-skill) |
| feature-flags-architect | 45 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| mcp-server-builder | 26 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| self-eval | 8 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| skill-tester | 83 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| api-design-reviewer | 187 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| api-test-suite-builder | 23 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| migration-architect | 265 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| monorepo-navigator | 23 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| senior-architect | 120 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| ci-cd-pipeline-builder | 25 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| ship-gate | 72 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| spec-driven-workflow | 85 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| code-reviewer | 163 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| dependency-auditor | 197 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| tdd-guide | 170 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| tech-debt-tracker | 326 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| docker-development | 49 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| helm-chart-builder | 70 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| database-designer | 245 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| database-schema-designer | 18 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| sql-database-assistant | 76 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| changelog-generator | 63 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| git-worktree-manager | 25 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| pr-review-expert | 12 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| incident-commander | 304 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| runbook-generator | 3 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| slo-architect | 48 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| kubernetes-operator | 64 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| observability-designer | 207 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| terraform-patterns | 65 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| performance-profiler | 17 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| env-secrets-manager | 21 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| secrets-vault-manager | 78 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| agent-designer | 260 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| agent-workflow-designer | 7 KB | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) |
| cnblogs-skill | 69 KB | [weed33834/cnblogs-skill](https://github.com/weed33834/cnblogs-skill) |
| zhihu-content-manager | 15 KB | [weed33834/zhihu-skill](https://github.com/weed33834/zhihu-skill) |

## Notes

- Self-authored skill repos + curated packs from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT).
- Non-core files (`.github`, `.gitignore`, `docker-compose.yml`, etc.) are excluded from the zips; runtime-required content (`SKILL.md`, `references/`, `scripts/`, `templates/`) is kept.
- Per-skill dependencies (e.g. Playwright, login state) are documented in each skill's own `SKILL.md`.

## License

[Apache License 2.0](LICENSE) © 2026 weed33834
