# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.2] - 2026-08-25

### Added

- **content-publishing 场景包扩展至 18 个技能**（第二批量产完成，覆盖主流中文平台）：
  - `csdn-publisher`：CSDN 博客发布/管理，Web 内部 API，7 子命令，7 测试。
  - `jianshu-publisher`：简书发布/管理，Web 内部 API，4 子命令，4 测试。
  - `bilibili-publisher`：B 站视频/专栏/动态发布，官方 API + Web API 混合，5 子命令，4 测试。
  - `toutiao-publisher`：今日头条/抖音文章/微头条发布，官方 API + Web API，2 子命令，4 测试。
  - `baijiahao-publisher`：百家号文章/视频/草稿发布，官方 API，3 子命令，3 测试。
  - `xiaohongshu-publisher`：小红书笔记草稿/发布/编辑/删除，Web 内部 API，4 子命令，4 测试。
  - `weibo-publisher`：微博发布/转发/评论/删除/图片上传，官方 API + Web API，3 子命令，4 测试。
  - `douban-publisher`：豆瓣日记/广播/小组话题发布，Web 内部 API，3 子命令，3 测试。
  - `v2ex-publisher`：V2EX 发帖/回复/节点列表，Web 内部 API，3 子命令，3 测试。
  - `segmentfault-publisher`：SegmentFault 文章/提问发布，Web 内部 API，3 子命令，3 测试。
  - `oschina-publisher`：开源中国博客/问答/动态，官方 API + Web API，3 子命令，3 测试。
  - `static-blog-deploy`：Hexo/Hugo/GitHub Pages/GitLab Pages/Vercel/Netlify 静态站点部署，6 子命令，3 测试。
- 全新增 12 个技能，content-publishing 包从 6 扩展至 18 技能（覆盖 CSDN、简书、B站、头条、百家号、小红书、微博、豆瓣、V2EX、SegmentFault、开源中国、静态博客部署）。
- 所有新技能均遵循统一安全设计：默认 dry-run、凭据环境变量隔离、端点常量标注 VERIFY BEFORE USE、带单元测试。

## [1.6.1] - 2026-08-25

### Refactored

- 提取发布公共工具 `skills/writing/_common/publish_common.py`，集中以下重复逻辑：
  - `http_json`：统一 GET/POST、cookie 支持 str|dict、网络异常包装为 `PublishError`
  - `dry_run_guard`：统一 dry-run 提示
  - `load_credential`：统一从环境变量/文件加载凭据
  - `dump_json(data)`：统一 `json.dumps(data, ensure_ascii=False, indent=2)` 输出（消除 12+ 处重复）
  - `load_json(path)`：统一 BOM-safe JSON 读取（消除 4 处 `open + json.load` 重复）
- 简化 3 个脚本的 import 前导（10 行→3 行，删除死代码路径）
- wechat / juejin / ai-cover-generator / cross-post-orchestrator 四个脚本改为复用该模块，
  删除各自重复的 HTTP、UA、`_guarded_execute`、`load_cookie`、`json.dumps` 实现
- `build.py` 现在会把 `_common` 一并打包进引用它的场景包（如 content-publishing），
  保证用户解压后即可运行；本地经 junction 调用时 `os.path.realpath` 也能正确解析

## [1.6.0] - 2026-08-25

### Added

- **content-publishing 场景包扩至 6 个技能**（第一批产线完成）：
  - `wechat-mp-publisher`：公众号官方草稿箱/发布 API 客户端（token/uploadimg/add_material/draft_add/freepublish），multipart 手工构造、默认 dry-run，7 个单元测试。
  - `juejin-publisher`：掘金 Web 内部接口客户端；端点常量显式标注 VERIFY BEFORE USE 并附 DevTools 核对步骤（不虚构 API），6 个单元测试。
  - `cross-post-orchestrator`：manifest 驱动的多平台编排器——plan 模式零联网检查各平台前置条件，run 模式调度兄弟技能 CLI，无脚本平台输出精确手工清单并返回退出码 2；发布台账持久化，8 个单元测试。
  - `ai-cover-generator`：对接本地图片服务（127.0.0.1:30080）——尺寸约束校验（16 倍数/宽高比/总像素）、task_id 容错解析、轮询下载、PIL 压缩 <1MB；服务不可达明确报错，7 个单元测试。
- `cnblogs-skill` 补充单元测试（5 个，含 BOM 回归用例）。

### Verified

- 全部 33 个单元测试通过（6 技能 × unittest discover）。
- agentseed MCP 门禁：4 个新脚本 verify_code suspects=[] 且 scan_hallucination clean/blocking=false。

## [1.5.0] - 2026-08-25

### Added

- **Scenario-skill track**: the repo now maintains self-authored China-platform automation skills alongside upstream curation, under `skills/writing/`.
- Restored `zhihu-content-manager` and reworked it:
  - removed sandbox-hardcoded paths (`/app/chromium-...`, `/tmp/.pip-global/...`); browser path now resolves via env var or Playwright's bundled Chromium.
  - decoupled from private image-generation tooling; any text-to-image tool works.
  - moved personal style/content-ops guidance to `references/content-ops.md` (customizable baseline).
  - added `scripts/zhihu_html_lint.py` — offline pre-publish gate (bare `<img>`, `<table>`, empty paragraphs, unescaped code brackets, Latin-1 mojibake) with 10 unit tests.
- Restored `cnblogs-skill` and reworked it:
  - fixed BOM bug in `cnblogs-pre-publish-check.py` (`utf-8-sig`); h1 detection now works on Windows-authored files.
  - removed private tool dependencies (`dumate-browser-use`, `baidu-image-gen`); generalized to any Playwright session / image tool.
- New pack `content-publishing` bundling both skills.

### Removed

- Deceptive engagement playbook: fake-persona reply script for "are you AI?" questions and daily quota farming table. Replaced with honest, quality-first interaction guidelines.

## [1.4.0] - 2026-08-25

### Removed

- **Dropped all self-authored skills** — the repository is now a pure curated collection of the upstream project:
  - `agent-builder-skill` (was in pack `ai-agent-development`)
  - `chinese-parents-skill` (was in pack `family-communication`)
  - `cnblogs-skill` (was in pack `blog-writing`)
  - `zhihu-content-manager` (was in pack `zhihu-writing`)
  - Removed now-empty packs: `blog-writing`, `family-communication`, `zhihu-writing`. Packs: 16 → 13; skills: 37 → 33.

### Changed

- `manifest.json`: removed self-authored entries; source notes now point to the single upstream.
- Added [SOURCES.md](SOURCES.md) — upstream address and step-by-step update guide for all skills.

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
- Added `sync-mirrors.ps1` for pushing to the GitCode + Gitee mirrors (tokens via env vars, never stored). GitHub is dropped as a distribution platform for now; upstream attribution links are unaffected.

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
