<p align="center"><img src="docs/logo.svg" alt="Awesome SkillKit Logo" width="200" height="60" /></p>

# awesome-skillkit

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE) ![Skills](https://img.shields.io/badge/skills-113-brightgreen) ![Packs](https://img.shields.io/badge/scenes-27-blue)

**English** | [中文](README.zh-CN.md) | [日本語](README.ja.md)

> 🌐 **Browse online** — search all 113 skills and download any single `SKILL.md` or a whole pack zip:
> [GitHub Pages](https://x33834.github.io/awesome-skillkit/) · [GitCode Pages](https://gitcode.host/badhope/awesome-skillkit) · [Gitee Pages](https://badhope.gitee.io/awesome-skillkit/site/)
> (deploy guide: [docs/DEPLOY-SITE.md](docs/DEPLOY-SITE.md))

Curated **scene packs** for AI tools. **Each pack = one real-world scenario, containing multiple hand-picked skills.** Download a zip → unzip → drag the skill folders into your AI tool's skills directory → it just works.

## Positioning

**The scenario is the answer — grounded in platform + tool.**

- 🎯 Each pack maps to one **concrete scenario** ("review a pull request", "build a CI/CD pipeline", "post to my blog"), not a broad domain.
- 🧩 Each pack bundles **the skills that work together for that scenario** — from a focused pair to a full 18-skill suite (`content-publishing` covers 16 Chinese platforms end-to-end) — no more hunting through a hundred standalone skills.
- 🏷️ Every skill's **source is clearly attributed** (see the Source column), so you always know where it came from.

## Scene Packs

| Pack | Scenario | Skills | Size |
|------|----------|--------|------|
| ai-agent-development | AI Agent Development | 5 | 151 KB |
| ai-media-toolkit | AI Media Generation | 4 | 19 KB |
| ai-research-writing | AI Research & Writing | 19 | 129 KB |
| ai-video-pipeline | AI Video Pipeline | 6 | 61 KB |
| video-design-studio | Video Design Studio (pre-production) | 4 | 32 KB |
| visual-design-studio | Visual Design Studio | 3 | 14 KB |
| audio-studio | Audio Studio (podcast chain) | 3 | 14 KB |
| growth-marketing | Growth Marketing (e-commerce) | 3 | 15 KB |
| edu-craft | Edu Craft (mastery teaching) | 3 | 15 KB |
| chat-prompt-craft | Chat Prompt Craft | 1 | 8 KB |
| api-development | API Development & Testing | 2 | 50 KB |
| architecture | System Architecture | 3 | 109 KB |
| ci-cd | CI/CD Pipeline | 3 | 64 KB |
| code-planning | Code Planning & Generation | 3 | 74 KB |
| code-review | Code Review | 5 | 246 KB |
| containers | Containers & Orchestration | 3 | 67 KB |
| content-publishing | Content Publishing Automation | 18 | 132 KB |
| data-ml-science | Data, ML & Scientific Computing | 7 | 63 KB |
| database | Database Design & Management | 2 | 102 KB |
| github-workflow | GitHub Collaboration | 3 | 39 KB |
| incident-response | Incident Response & SRE | 3 | 123 KB |
| infrastructure | Infrastructure as Code | 3 | 95 KB |
| office-productivity | Office Productivity | 4 | 11 KB |
| performance | Performance Profiling | 1 | 11 KB |
| security | Security & Secrets | 2 | 46 KB |
| tdd | Test-Driven Development | 1 | 50 KB |
| viral-entertainment | Viral Entertainment (meme shorts) | 2 | 9 KB |

**27 packs · 113 skills.** Project docs: [Direction v2](docs/DIRECTION-V2.md) · [Skill Standard](docs/SKILL-STANDARD-v2.md) · [Versioning & Release policy](docs/VERSIONING.md) · [Video landscape research](docs/VIDEO-LANDSCAPE.md) 

## Pack Details

### AI Agent Development (`ai-agent-development`) — 151 KB

**Build production-grade AI agents, design multi-agent workflows, MCP servers, feature flags, and self-evaluation.**

| Skill | Source |
|-------|--------|
| agent-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| mcp-server-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| feature-flags-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| self-eval | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| skill-tester | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### API Development & Testing (`api-development`) — 50 KB

**Review REST API designs and generate integration/contract test suites.**

| Skill | Source |
|-------|--------|
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-test-suite-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### System Architecture (`architecture`) — 109 KB

**Design system architecture, plan zero-downtime migrations, and navigate monorepos.**

| Skill | Source |
|-------|--------|
| senior-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| migration-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| monorepo-navigator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### CI/CD Pipeline (`ci-cd`) — 64 KB

**Generate pragmatic CI/CD pipelines, release gates, and spec-driven development workflows.**

| Skill | Source |
|-------|--------|
| ci-cd-pipeline-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| ship-gate | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| spec-driven-workflow | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Content Publishing Automation (`content-publishing`) — 132 KB

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

### Code Review (`code-review`) — 246 KB

**Review pull requests, analyze code quality, audit dependencies and tech debt across languages.**

| Skill | Source |
|-------|--------|
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| code-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| tech-debt-tracker | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| dependency-auditor | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Containers & Orchestration (`containers`) — 68 KB

**Dockerfile optimization, docker-compose, Helm charts, and Kubernetes operators.**

| Skill | Source |
|-------|--------|
| docker-development | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| helm-chart-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Database Design & Management (`database`) — 102 KB

**Design schemas, ERD diagrams, migrations, and optimize SQL queries.**

| Skill | Source |
|-------|--------|
| database-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| sql-database-assistant | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### GitHub Collaboration (`github-workflow`) — 39 KB

**Parallel worktrees, conventional-commit changelogs, and PR review on GitHub.**

| Skill | Source |
|-------|--------|
| git-worktree-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| changelog-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Incident Response & SRE (`incident-response`) — 123 KB

**Command incidents, generate runbooks, and define SLOs/error budgets.**

| Skill | Source |
|-------|--------|
| incident-commander | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| runbook-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| slo-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Infrastructure as Code (`infrastructure`) — 95 KB

**Terraform patterns, observability design, and Kubernetes operators.**

| Skill | Source |
|-------|--------|
| terraform-patterns | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| observability-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Performance Profiling (`performance`) — 11 KB

**Profile CPU/memory/I/O bottlenecks in Node.js, Python, and Go.**

| Skill | Source |
|-------|--------|
| performance-profiler | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Security & Secrets (`security`) — 46 KB

**Set up secret vaults and manage environment-variable hygiene.**

| Skill | Source |
|-------|--------|
| secrets-vault-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| env-secrets-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Test-Driven Development (`tdd`) — 50 KB

**Write unit tests, fixtures, mocks, and guide red-green-refactor cycles.**

| Skill | Source |
|-------|--------|
| tdd-guide | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

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

### Viral Entertainment (`viral-entertainment`) — 9 KB

**Special entertainment scenarios: talking-baby podcast pipeline and "laughing mascot" meme shorts (nailong style) — character consistency discipline and platform-compliance built in.**

| Skill | Source |
|-------|--------|
| ai-baby-podcast | self-authored |
| nailong-laugh-shorts | self-authored |

### Video Design Studio (`video-design-studio`) — 32 KB

**Pre-production design layer: storyboard with continuity contracts, shot lists from 12 recipe cards, cross-model video-prompt engineering with a structural auditor, and visual style anchors with character consistency cards. Methodology credited to open-source projects (video-storyboard / video-shotcraft / visual-skills) — see each skill's sources-and-methodology.md.**

| Skill | Source |
|-------|--------|
| storyboard-designer | self-authored |
| shot-recipe-designer | self-authored |
| video-prompt-engineer | self-authored |
| visual-style-anchor | self-authored |

### Visual Design Studio (`visual-design-studio`) — 14 KB

**AI visual-design chain: brief -> spec -> prompt -> layout audit. design-brief-interpreter turns a vague request into a 7-field machine-checkable spec, image-prompt-engineer writes five-segment text-to-image prompts with per-model dialects and text-rendering rules, layout-spec-auditor checks ratio/resolution/safe-area/text-budget against a built-in platform spec table. Methodology credited to Anthropic canvas-design / designskills / Replicate prompting guide — see sources-and-methodology.md.**

| Skill | Source |
|-------|--------|
| design-brief-interpreter | self-authored |
| image-prompt-engineer | self-authored |
| layout-spec-auditor | self-authored |

### Audio Studio (`audio-studio`) — 14 KB

**AI podcast chain: topic/document -> script -> voice -> publishable episode. podcast-producer writes segmented spoken-words-only scripts with a TTS-safety linter, tts-voice-director casts voices from a cross-engine catalog and plans ffmpeg stitching, episode-publisher emits shownotes, timestamped chapters and platform metadata with the AI-disclosure line. Methodology credited to Kokoro/Qwen3-TTS ecosystem practice (Podify / inference.sh) — see sources-and-methodology.md.**

| Skill | Source |
|-------|--------|
| podcast-producer | self-authored |
| tts-voice-director | self-authored |
| episode-publisher | self-authored |

### Growth Marketing (`growth-marketing`) — 15 KB

**E-commerce marketing chain: product-copywriter picks a conversion framework (FAB/PAS/AIDA) with objection handling and ad-law fact hygiene; campaign-designer plans calendar + channel matrix + single-variable A/B pairs; channel-adapter rewrites per-channel with a built-in constraint table audited by channel_fit_check.py. Methodology credited to direct-response frameworks and the open marketing-skills ecosystem — see sources-and-methodology.md.**

| Skill | Source |
|-------|--------|
| product-copywriter | self-authored |
| campaign-designer | self-authored |
| channel-adapter | self-authored |

### Edu Craft (`edu-craft`) — 15 KB

**Mastery-teaching chain: course-designer turns a topic into a learning contract + dependency-ordered checkpoints; exercise-generator emits open-ended strict exercises (MCQ banned) with rubrics, linted by exercise_lint.py; feynman-explainer runs the six-beat Feynman loop for failed checkpoints until re-test passes. Methodology credited to the Feynman/mastery-learning ecosystem — see sources-and-methodology.md.**

| Skill | Source |
|-------|--------|
| course-designer | self-authored |
| exercise-generator | self-authored |
| feynman-explainer | self-authored |



### AI Video Pipeline (`ai-video-pipeline`) — 62 KB

**The whole short-video line in one pack: script → voice → lip-sync → assembly → subtitles → thumbnail. Six skills that hand off to each other, ending in a publish-ready vertical video.**

| Skill | Source |
|-------|--------|
| video-script-writer | self-authored |
| video-voice-synth | self-authored |
| video-lip-sync | self-authored |
| video-editor | self-authored |
| video-subtitles | self-authored |
| video-thumbnail | self-authored |

### AI Research & Writing (`ai-research-writing`) — 129 KB

**From question to finished long-form piece: multi-round research and report synthesis, academic topic selection, outline, draft, style editing, and keyword/platform-rule optimization.**

| Skill | Source |
|-------|--------|
| deep-research | self-authored |
| web-search | self-authored |
| paper-topic-selector | self-authored |
| article-outliner | self-authored |
| article-drafter | self-authored |
| content-editor | self-authored |
| seo-optimizer | self-authored |
| lit-review | self-authored |
| experiment-runner | self-authored |
| figure-maker | self-authored |
| arch-diagram | self-authored |
| neural-net-draw | self-authored |
| latex-formatter | self-authored |
| self-reviewer | self-authored |
| journal-adapt | self-authored |
| anti-defensive | self-authored |
| ai-humanizer | self-authored |
| tex-cleaner | self-authored |
| pub-plotter | self-authored |

### Code Planning & Generation (`code-planning`) — 72 KB

**Turn a vague request into working code: three-layer waterfall intent recognition, structured implementation plans, two-tier generation (Jinja2 template engine + LLM), and systematic failure diagnosis with runnable Jinja2 templates bundled.**

| Skill | Source |
|-------|--------|
| code-intent-planner | self-authored |
| code-generator | self-authored |
| debug-diagnoser | self-authored |

### Data, ML & Scientific Computing (`data-ml-science`) — 63 KB

**Data and modeling end to end: ETL cleaning and transforms, feature engineering with leakage warnings, mathematical formulation and solver selection, Monte Carlo simulation, result visualization, ML training pipelines with hyperparameter tuning, and metric interpretation.**

| Skill | Source |
|-------|--------|
| etl-builder | self-authored |
| feature-engineer | self-authored |
| model-formulator | self-authored |
| model-solver | self-authored |
| simulation-runner | self-authored |
| result-visualizer | self-authored |
| ml-pipeline | self-authored |

### Chat Prompt Craft (`chat-prompt-craft`) — 8 KB

**Prompt engineering for conversational AI assistants (Doubao, ChatGPT, Kimi, DeepSeek, etc.): one-shot task prompts built on the five-element formula (role + background + task + requirements + format), agent/persona system prompts, reverse constraints that kill filler, and a heuristic structural audit.**

| Skill | Source |
|-------|--------|
| chat-prompt-engineer | self-authored |

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

1. 📦 Download the zip for the **scene** you need from **Releases** (or run `python3 build.py` to build `dist/*.zip` locally).
2. 📂 Unzip it — you get **multiple skill folders** (each containing `SKILL.md`).
3. 🧲 **Drag** the skill folders into your AI tool's skills directory:
   - Claude Code: `~/.claude/skills/` (global) or `.claude/skills/` in your project (project-only)
   - Other tools with skills support: use their corresponding skills directory
4. 🚀 Start a new session — it works immediately, no configuration needed.

## Build & Release

Source lives in `skills/`; scene packs are defined in `packs/*/pack.json`; zips are published via platform Releases on Gitee / GitCode (`dist/` is gitignored).

```bash
# Generate dist/*.zip (one zip per scene pack)
python3 build.py     # single build entry; cross-platform; also emits dist/_all.zip with every skill

# Release flow (formal releases use tools/release.py, see docs/VERSIONING.md)
python3 tools/release.py 0.13.1 --commit   # validate CHANGELOG → bump → commit → tag
git push origin main --follow-tags
# Create the release on Gitee / GitCode and upload dist/*.zip
# (manifest.json's version field is the single source of truth — avoid manual tags)
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

[Apache License 2.0](LICENSE) © 2026 Morningstar202604

---


