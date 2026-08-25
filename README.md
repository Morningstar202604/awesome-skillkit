# awesome-skillkit

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE) ![Skills](https://img.shields.io/badge/skills-59-brightgreen) ![Packs](https://img.shields.io/badge/scenes-17-blue) [![Gitee](https://img.shields.io/badge/Gitee-badhope-C71D23)](https://gitee.com/badhope/awesome-skillkit) [![GitCode](https://img.shields.io/badge/GitCode-badhope-3B82F6)](https://gitcode.com/badhope/awesome-skillkit)

**English** | [中文](README.zh-CN.md) | [日本語](README.ja.md)

Curated **scene packs** for AI tools. **Each pack = one real-world scenario, containing multiple hand-picked skills.** Download a zip → unzip → drag the skill folders into your AI tool's skills directory → it just works.

## Positioning

**The scenario is the answer — grounded in platform + tool.**

- Each pack maps to one **concrete scenario** ("review a pull request", "build a CI/CD pipeline", "post to my blog"), not a broad domain.
- Each pack bundles **the skills that work together for that scenario** — from a focused pair to a full 18-skill suite (`content-publishing` covers 16 Chinese platforms end-to-end) — no more hunting through a hundred standalone skills.
- Every skill's **source is clearly attributed** (see the Source column), so you always know where it came from.

## Scene Packs

| Pack | Scenario | Skills | Size |
|------|----------|--------|------|
| ai-agent-development | AI Agent Development | 5 | 145 KB |
| api-development | API Development & Testing | 2 | 49 KB |
| architecture | System Architecture | 3 | 108 KB |
| ci-cd | CI/CD Pipeline | 3 | 60 KB |
| code-review | Code Review | 5 | 242 KB |
| containers | Containers & Orchestration | 3 | 66 KB |
| content-publishing | Content Publishing Automation | 18 | 127 KB |
| database | Database Design & Management | 2 | 99 KB |
| github-workflow | GitHub Collaboration | 3 | 43 KB |
| incident-response | Incident Response & SRE | 3 | 122 KB |
| infrastructure | Infrastructure as Code | 3 | 96 KB |
| performance | Performance Profiling | 1 | 12 KB |
| security | Security & Secrets | 2 | 49 KB |
| tdd | Test-Driven Development | 1 | 55 KB |
| ai-media-toolkit | AI Media Generation | 4 | 19 KB |
| office-productivity | Office Productivity | 4 | 11 KB |
| viral-entertainment | Viral Entertainment (meme shorts) | 2 | 11 KB |

**17 packs · 59 skills.** Project docs: [Direction v2](docs/DIRECTION-V2.md) · [Skill Standard](docs/SKILL-STANDARD-v2.md) · [Versioning & Release policy](docs/VERSIONING.md) · [Expert review](docs/EXPERT-REVIEW-AND-ROADMAP.md)

## Pack Details

### AI Agent Development (`ai-agent-development`) — 145 KB

**Build production-grade AI agents, design multi-agent workflows, MCP servers, feature flags, and self-evaluation.**

| Skill | Source |
|-------|--------|
| agent-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| mcp-server-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| feature-flags-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| self-eval | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| skill-tester | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### API Development & Testing (`api-development`) — 49 KB

**Review REST API designs and generate integration/contract test suites.**

| Skill | Source |
|-------|--------|
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-test-suite-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### System Architecture (`architecture`) — 108 KB

**Design system architecture, plan zero-downtime migrations, and navigate monorepos.**

| Skill | Source |
|-------|--------|
| senior-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| migration-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| monorepo-navigator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### CI/CD Pipeline (`ci-cd`) — 60 KB

**Generate pragmatic CI/CD pipelines, release gates, and spec-driven development workflows.**

| Skill | Source |
|-------|--------|
| ci-cd-pipeline-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| ship-gate | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| spec-driven-workflow | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Content Publishing Automation (`content-publishing`) — 127 KB

**Publish, edit and manage articles/videos on Chinese platforms (Zhihu, cnblogs, WeChat MP, Juejin, CSDN, Jianshu, Bilibili, Toutiao, Baijiahao, Xiaohongshu, Weibo, Douban, V2EX, SegmentFault, OSChina, Static Blogs) — battle-tested platform knowledge, a cross-post orchestrator, and AI cover-image generation.**

| Skill | Source |
|-------|--------|
| zhihu-content-manager | skillkit authors (self-authored) |
| cnblogs-skill | skillkit authors (self-authored) |
| wechat-mp-publisher | skillkit authors (self-authored) |
| juejin-publisher | skillkit authors (self-authored) |
| csdn-publisher | skillkit authors (self-authored) |
| jianshu-publisher | skillkit authors (self-authored) |
| bilibili-publisher | skillkit authors (self-authored) |
| toutiao-publisher | skillkit authors (self-authored) |
| baijiahao-publisher | skillkit authors (self-authored) |
| xiaohongshu-publisher | skillkit authors (self-authored) |
| weibo-publisher | skillkit authors (self-authored) |
| douban-publisher | skillkit authors (self-authored) |
| v2ex-publisher | skillkit authors (self-authored) |
| segmentfault-publisher | skillkit authors (self-authored) |
| oschina-publisher | skillkit authors (self-authored) |
| static-blog-deploy | skillkit authors (self-authored) |
| cross-post-orchestrator | skillkit authors (self-authored) |
| ai-cover-generator | skillkit authors (self-authored) |

### Code Review (`code-review`) — 242 KB

**Review pull requests, analyze code quality, audit dependencies and tech debt across languages.**

| Skill | Source |
|-------|--------|
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| code-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| tech-debt-tracker | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| dependency-auditor | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Containers & Orchestration (`containers`) — 66 KB

**Dockerfile optimization, docker-compose, Helm charts, and Kubernetes operators.**

| Skill | Source |
|-------|--------|
| docker-development | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| helm-chart-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Database Design & Management (`database`) — 99 KB

**Design schemas, ERD diagrams, migrations, and optimize SQL queries.**

| Skill | Source |
|-------|--------|
| database-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| sql-database-assistant | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### GitHub Collaboration (`github-workflow`) — 43 KB

**Parallel worktrees, conventional-commit changelogs, and PR review on GitHub.**

| Skill | Source |
|-------|--------|
| git-worktree-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| changelog-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Incident Response & SRE (`incident-response`) — 122 KB

**Command incidents, generate runbooks, and define SLOs/error budgets.**

| Skill | Source |
|-------|--------|
| incident-commander | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| runbook-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| slo-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Infrastructure as Code (`infrastructure`) — 96 KB

**Terraform patterns, observability design, and Kubernetes operators.**

| Skill | Source |
|-------|--------|
| terraform-patterns | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| observability-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Performance Profiling (`performance`) — 12 KB

**Profile CPU/memory/I/O bottlenecks in Node.js, Python, and Go.**

| Skill | Source |
|-------|--------|
| performance-profiler | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Security & Secrets (`security`) — 49 KB

**Set up secret vaults and manage environment-variable hygiene.**

| Skill | Source |
|-------|--------|
| secrets-vault-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| env-secrets-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Test-Driven Development (`tdd`) — 55 KB

### AI Media Generation (`ai-media-toolkit`) — 19 KB

**Text/image-to-video, text/image-to-image generation, music generation, and cover-image creation through a local generation gateway — full submit/poll/download workflows with failure handling.**

| Skill | Source |
|-------|--------|
| video-generation | self-authored |
| image-generation | self-authored |
| music-generation | self-authored |
| ai-cover-generator | self-authored |

### Office Productivity (`office-productivity`) — 11 KB

**Daily office work: real .pptx deck builder, Excel clean-and-analyze with before/after evidence, JD-driven resume tailoring with anti-fabrication rules, and structured meeting minutes.**

| Skill | Source |
|-------|--------|
| ppt-builder | self-authored |
| excel-assistant | self-authored |
| resume-tailor | self-authored |
| meeting-notes | self-authored |

### Viral Entertainment (`viral-entertainment`) — 11 KB

**Special entertainment scenarios: talking-baby podcast pipeline and "laughing mascot" meme shorts (nailong style) — character consistency discipline and platform-compliance built in.**

| Skill | Source |
|-------|--------|
| ai-baby-podcast | self-authored |
| nailong-laugh-shorts | self-authored |

**Write unit tests, fixtures, mocks, and guide red-green-refactor cycles.**

| Skill | Source |
|-------|--------|
| tdd-guide | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

## Directory Layout

```
packs/                          # scene pack definitions (one dir per scenario)
├── code-review/                #   pack.json: scenario metadata + skill list + sources
├── ci-cd/
├── containers/
├── database/
├── api-development/
├── github-workflow/
├── architecture/
├── incident-response/
├── infrastructure/
├── ai-agent-development/
├── security/
├── performance/
└── tdd/
skills/                         # single source of truth for all skill code
├── programming/                # curated from upstream (multi-level taxonomy)
└── writing/                    # self-authored scenario skills
    ├── blog/                   #   cnblogs / csdn / jianshu / static-blog-deploy
    ├── zhihu/  wechat/  juejin/ #   per-platform publishers
    ├── social/                 #   xiaohongshu / weibo
    ├── video/  news/           #   bilibili / toutiao / baijiahao
    ├── community/              #   v2ex / segmentfault / oschina / douban
    ├── assets/  orchestrator/  #   ai-cover-generator / cross-post-orchestrator
    └── _common/                #   shared HTTP/dry-run/credential helpers (not a skill)
dist/                           # build output: one zip per scene pack (gitignored)
```

## Getting Started (30 seconds)

1. Download the zip for the **scene** you need from **Releases** (or run `python3 build.py` to build `dist/*.zip` locally).
2. Unzip it — you get **multiple skill folders** (each containing `SKILL.md`).
3. **Drag** the skill folders into your AI tool's skills directory:
   - Claude Code: `~/.claude/skills/` (global) or `.claude/skills/` in your project (project-only)
   - Other tools with skills support: use their corresponding skills directory
4. Start a new session — it works immediately, no configuration needed.

## Build & Release

Source lives in `skills/`; scene packs are defined in `packs/*/pack.json`; zips are published via platform Releases on Gitee / GitCode (`dist/` is gitignored).

```bash
# Generate dist/*.zip (one zip per scene pack)
bash build.sh        # macOS / Linux / Git Bash
python3 build.py     # cross-platform (no bash/zip needed); also emits dist/_all.zip with every skill

# Release flow
git tag v1.12.1
git push origin main --follow-tags
powershell -File sync-mirrors.ps1   # gitcode + gitee + github
# Create a release on the Gitee/GitCode Releases page and upload dist/*.zip
```

## Sources & Updates

This repository maintains two tracks:

**1. Upstream curation** — update from there:

- **Upstream**: [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT license) — all 33 programming skills.
- Two upstream near-duplicates (`database-schema-designer`, `agent-workflow-designer`) were merged into their siblings; their unique material was preserved as reference docs inside the surviving skill.

To pull upstream updates: clone the upstream repo, re-copy the corresponding skill folders into `skills/programming/...`, then re-run `python3 build.py`.

**2. Self-authored scenario skills** (`skills/writing/`, pack `content-publishing`):

- `zhihu-content-manager` / `cnblogs-skill` / `wechat-mp-publisher` / `juejin-publisher` / `csdn-publisher` / `jianshu-publisher` / `bilibili-publisher` / `toutiao-publisher` / `baijiahao-publisher` / `xiaohongshu-publisher` / `weibo-publisher` / `douban-publisher` / `v2ex-publisher` / `segmentfault-publisher` / `oschina-publisher` / `static-blog-deploy` / `cross-post-orchestrator` / `ai-cover-generator` encode China-platform-specific automation knowledge that upstream does not cover. Maintained in this repo; each ships executable pre-publish check scripts with unit tests, defaulting to dry-run.

Full per-skill attribution is in [manifest.json](manifest.json), each `packs/*/pack.json`, and [SOURCES.md](SOURCES.md).

## Notes

- Non-core files (`.github`, `.gitignore`, `docker-compose.yml`, etc.) are excluded from the zips; runtime-required content (`SKILL.md`, `references/`, `scripts/`, `templates/`) is kept.
- Per-skill dependencies (e.g. Playwright, login state) are documented in each skill's own `SKILL.md`.

## License

[Apache License 2.0](LICENSE) © 2026 weed33834

---

**If this helps you, please Star the repo on [GitCode](https://gitcode.com/badhope/awesome-skillkit) / [Gitee](https://gitee.com/badhope/awesome-skillkit) / [GitHub](https://github.com/Morningstar202604/awesome-skillkit)** - it is how other people find these packs.
