# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.3] - 2026-08-26

### Fixed

- **构建不可复现修复**：zip 条目此前嵌入源文件时间戳，导致每次重建产生不同
  sha256（manifest 校验和随构建漂移、失去可信度）。现统一固定条目时间戳，
  相同输入产出字节级相同的 zip——已实测连续两次构建哈希完全一致。
- 平台仓库描述补齐：GitCode 与 Gitee 均已通过各自 API 写入英文简介
  （GitHub 此前已完成 description + 15 topics）。

## [0.12.2] - 2026-08-26

### Changed

- **可发现性优化（对标同类头部仓库后择优采纳）**：
  - 三语 README 增加徽章行（License/Skills/Packs/Gitee/GitCode）与底部三平台 Star 引导——awesome-claude-skills(13k★) 与 anthropics/skills 均有徽章，属同行标准做法；
  - **不添加自定义 Logo**：头部同类仓库均无 Logo 图标，遵循"同行没做就不做"原则。
- **平台元数据**：GitHub 仓库 description 与 15 个 topics 已通过 API 生效；Gitee/GitCode 的 API 拒绝 git 凭据直调（需网页端设置或专用私人令牌）。

### Fixed

- **sync-mirrors.ps1 假报错修复**：PowerShell 5.1 在 EAP=Stop 下把 git 的 stderr 进度（如 "Everything up-to-date"）渲染为红色异常并可能中断脚本；现改为经 cmd /c 进程级合并流、仅以退出码判定成败。实测三平台一次跑通、退出码 0。

## [0.12.1] - 2026-08-26

### Changed

- 三语 README 同步至当前状态：17 包 / 59 技能总览表、三个新包详情段（ai-media-toolkit / office-productivity / viral-entertainment）、项目文档链接区、发布示例命令更新。
- sync-mirrors.ps1 升级为三平台同步（GitCode + Gitee + GitHub）：支持环境变量令牌与命名 remote 凭据双通道，自动推送 tags；新增 gitee/github 命名 remote。
- 许可确认：全仓统一 Apache-2.0（LICENSE、frontmatter、CONTRIBUTING 已一致）。

## [0.12.0] - 2026-08-26

### Changed

- **`meme-mascot-shorts` 重写为 `nailong-laugh-shorts`**（按需求改为"大笑奶龙"直出版）：
  - 删除路线门与梗源复盘，改为纯生产手册：形象描述库（官方风基础体/大笑变异体/比例失调"奶蛙感"三套可复制 prompt）、双管线（A 表情包成精图生视频 / B 真人动作套壳还原原梗扭曲感）、自制笑声变声器配方、概率 bait 文案模板表、皮肤矩阵系列化；
  - 风险提示压缩为一行事实陈述（非盈利常见后果=限流下架、商用必追责），决策权交还用户。

### Fixed

- **发布流程缺陷（重要）**：release.py 此前只提交 manifest+CHANGELOG，导致
  v1.7.0–v1.11.0 的标签树缺失当时未暂存的新增技能文件。现 release.py 增加
  脏工作区硬门禁：有任何未提交变更即拒绝发版；本版为首个全量完整树。
- 补交 v1.7.0 以来全部场景技能与三个新包文件。

## [0.11.0] - 2026-08-26

### Added

- **品类 G 第二个技能 `meme-mascot-shorts`**（"大笑奶龙"式魔性萌物短视频，基于 2026-01 梗源调研）：
  - 梗源拆解：真人动作 AI 套壳（军体拳→奶龙="奶蛙"）× 变声器魔性笑声 × 概率 bait 文案的四方缝合公式；
  - **三条合规路线硬性前置**（A 正版素材 / B 原创同类萌物【推荐】 / C 直接用 IP=高侵权风险）：奶龙 IP 方有活跃维权判例（玩具销售赔偿、商标异议胜诉、上海知产法院首例 AI LoRA 侵权案判赔 5 万），Route C 需用户书面确认已知风险；
  - Route B 原创度自检底线（剪影/五官/配色两项以上明显不同）、"听觉锤先行"设计法、hook-and-body 皮肤矩阵系列化；
  - references/meme-case-study.md：梗起源与官方应对失效的传播学复盘（脱敏公式）。
- `viral-entertainment` 包扩至 2 技能。
- 门禁基线：59 技能 / 17 包 / 0 错误 / 76 警告；18 个分发包 sha256 全覆盖。

## [0.10.0] - 2026-08-26

### Added

- **品类 C 落地：新包 `office-productivity` 四件套**
  - `ppt-builder`：大纲公式→逐页 spec JSON→捆绑脚本渲染真 .pptx（python-pptx 缺席时优雅降级 markdown），含 spec 校验器与 7 个单测；
  - `excel-assistant`：先勘察后动手、一步一改带前后证据、编码三连降序尝试、交付 `_cleaned` + findings.md；
  - `resume-tailor`：JD 提取→差距矩阵→STAR 量化重写→ATS 卫生检查，双产物（定制稿+逐条可追溯 edit_log），硬禁造假红线；
  - `meeting-notes`：议题分段→决议/讨论/行动三分类（原话作证据）→行动项表格（无主必标 `<待指派>`），固定骨架输出。
- **品类 G 上线：新包 `viral-entertainment` 首个技能 `ai-baby-podcast`**（AI 宝宝播客/会说话角色短视频全流水线，基于 2026-08 成熟打法调研）：
  - 形象图 prompt 公式 → 反差脚本公式（成人观点×婴儿脸+固定口癖）→ 成人声 TTS 干声 → 口型驱动（短句先行）→ 剪映收尾五步；
  - 角色一致性纪律：角色卡七件套、锁定 seed/音色、每 10 条漂移审计、永不从文字重生角色（references/character-consistency.md）；
  - 合规红线四条硬禁令：《人工智能生成合成内容标识办法》显式声明要求（2025-09-01 施行）、纯虚构形象、不克隆名人声纹肖像、避开平台点名整治题材。
- DIRECTION-V2 品类表新增 G 行与电影级/宣传片系列愿景备注。
- 门禁基线：58 技能 / 17 包 / 0 错误 / 76 警告；测试 180 通过 +1 条件跳过；18 个分发包含 sha256。

## [0.9.0] - 2026-08-26

### Added

- **品类 B 第三个技能 `music-generation`**（brief → 配乐/歌曲）：三槽位风格公式（流派+乐器+情绪用途）、纯音乐/歌词双模式、端点 404 快速失败（VERIFY BEFORE USE，禁止本地合成兜底）、六症状失败处置表、量化交付标准。
- **`ai-cover-generator` 跨包挂入 `ai-media-toolkit`**（封面图生成复用既有资产，不造重复轮子），包扩至 4 技能。
- 门禁基线：53 技能 / 0 错误 / 76 警告；16 个分发包 sha256 全覆盖。

## [0.8.0] - 2026-08-26

### Added

- **品类 B 第二个技能 `image-generation`**（文生图 + 图生图，同骨架同纪律）：
  - 尺寸约束表（16 倍数、宽高比 1:3–3:1、总像素上下限，标 VERIFY BEFORE USE）与常用尺寸清单；
  - 参数错误自动修正重试路径；轮询 3–5 秒/次、120 次上限；
  - 六症状失败处置表；量化交付标准（非空 png + 时间戳命名 + 绝对路径回报）;
  - 提示词四段式公式：主体细节 / 风格媒介 / 构图视角 / 文字排版（含"精确引述文字内容"规则）。
- **`ai-media-toolkit` 包扩至 2 技能**（对齐 SkillsBench"每包 2–3 个聚焦技能"最优区间），双语描述同步更新。
- 门禁基线：52 技能 / 0 错误 / 76 警告；16 个分发包 sha256 全覆盖。

## [0.7.0] - 2026-08-26

### Added

- **品类 B（AI 媒体生成）首个示范技能 `video-generation`**，按 SKILL-STANDARD-v2 §4 骨架编写：
  - 输入清单 + 一次性询问模板；前置自检（网关探活，失败即停、禁止回退本地渲染）；
  - 工作流五步全部"命令+预期输出+失败分支"三件套；60 次轮询上限；
  - 失败处置表六种症状对应处置；交付标准量化（非空 mp4 + 时间戳命名 + 绝对路径回报）；
  - `references/prompt-recipes.md`：四槽位提示词公式与强弱示例对照。
  - 网关地址走 `VIDEO_GATEWAY_BASE` 环境变量（默认 `http://127.0.0.1:30080`）。
- **新场景包 `ai-media-toolkit`**（15 号包），manifest 同步注册。
- 门禁基线更新：51 技能 / 0 错误 / 76 警告；16 个分发包全部带 sha256。

## [0.6.3] - 2026-08-26

### Fixed

- **install.ps1 平铺解压修复**：原先按 zip 名嵌套子目录解压，导致 Windows 用户安装后技能无法被 AI 工具发现；现与 install.sh 同语义平铺，并在安装后自检 SKILL.md 可发现数量。
- **build.py 两处修复**：
  - `_common` 公共库此前因全局累积状态被误打进所有后序场景包，现仅打包真正依赖它的包；
  - 构建完成后自动把每个包的实际 `size_kb` 与 `sha256` 回填 `manifest.json`，分发产物首次可校验。
- **导航断链清零**（由新增 validator 驱动）：
  - `ship-gate` 补齐被三处引用的 `references/checks.md` 检查目录（与 scanner 内 CHECKS/MANUAL_CHECKS 注册表逐条对齐）；
  - `slo-architect` 移除指向不存在文件的引用、修正跨技能路径表述；
  - `cnblogs-skill/image-guide` 移除指向不存在旧版文档的指针；
  - `bilibili/weibo/jianshu/csdn` 四个 publisher 中 `_common` 相对路径更正为打包布局真实形态。
- manifest.json 中文描述中重复的"豆瓣"去除。

### Added

- **治理制度文档**：`docs/VERSIONING.md`（SemVer 语义、发布流程、历史处置决定：不回溯伪造 tag、自本版起 tag 全覆盖）、`docs/DIRECTION-V2.md`（通用场景工作流库战略）、`docs/SKILL-STANDARD-v2.md`（机器优先编写规范与门禁清单）。
- **tools/validate_skills.py** 质量门禁：frontmatter 合规、引用完整性（区分"导航断链=ERROR"与"宣传性缺失脚本=WARN"）、渐进披露行数、绝对路径检测、pack↔磁盘一致性。当前基线：**50 技能 0 错误 / 76 警告（存量债务已登记）**。
- **tools/release.py** 发布助手：SemVer 校验、CHANGELOG 小节强制、manifest 版本同步、annotated tag。
- **tools/migrate_metadata_v2.py** 一次性迁移（已完成）：全部 50 个技能补齐 `license` 与 `metadata.version/category/verified-date`。
- CONTRIBUTING.md 接入门禁：PR 必须通过 validator + pytest + build 三关。

### Changed

- `terraform-patterns` 正文 740→417 行（规范 G5），CI/CD、多云、OpenTofu、Terragrunt 等章节移入 `references/cicd-and-advanced-patterns.md`。

### Security

- `.git/config` 中内嵌的明文访问令牌已从 remote URL 移除（该令牌应视为已泄露，需在 GitCode 后台吊销轮换）。

## [0.6.2] - 2026-08-25

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

## [0.6.1] - 2026-08-25

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

## [0.6.0] - 2026-08-25

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

## [0.5.0] - 2026-08-25

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

## [0.4.0] - 2026-08-25

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

## [0.3.0] - 2026-08-23

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

## [0.2.0] - 2026-08-18

### Changed

- Restructured from per-skill zips into scene packs: one pack = one real-world scenario containing multiple skills.
- 16 scene packs covering coding, ops, writing and life scenarios.
- 35 developer skills curated from `alirezarezvani/claude-skills` (MIT), combined with 4 self-authored skills.
- `build.sh` now packages by scene pack (`packs/*/pack.json` → `dist/*.zip`).
- `manifest.json` now lists packs with per-skill source attribution.

### Added

- 16 curated scene packs under `packs/`.
- Source attribution for every skill (`alirezarezvani/claude-skills (MIT)` / `Morningstar202604 (self-authored)`).

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
