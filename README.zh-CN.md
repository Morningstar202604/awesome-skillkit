<p align="center"><img src="docs/logo.svg" alt="awesome-skillkit" width="220" /></p>

<h1 align="center">awesome-skillkit</h1>

<p align="center">
  <b>36 个真实场景包 · 154 个精选技能 · 解压即用——<br>把整套工作能力，一次交给你的 AI 工具。</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square" alt="License" /></a>
  <img src="https://img.shields.io/badge/skills-154-brightgreen?style=flat-square" alt="Skills" />
  <img src="https://img.shields.io/badge/packs-36-blue?style=flat-square" alt="Packs" />
  <img src="https://img.shields.io/badge/version-0.22.0-success?style=flat-square" alt="Version" />
</p>

<p align="center">
  <a href="https://x33834.github.io/awesome-skillkit/"><img src="https://img.shields.io/badge/%F0%9F%8C%90_%E5%AE%98%E7%BD%91-Web-brightgreen?style=flat-square" alt="Official Site" /></a>
  <a href="https://github.com/x33834/awesome-skillkit/releases/latest/download/_all.zip"><img src="https://img.shields.io/badge/%E2%AC%87%EF%B8%8F_%E4%B8%8B%E8%BD%BD-_all.zip-blue?style=flat-square" alt="Download all packs" /></a>
  <a href="https://gitcode.com/badhope/awesome-skillkit"><img src="https://img.shields.io/badge/GitCode-镜像-3A72BE?style=flat-square" alt="GitCode" /></a>
  <a href="https://gitee.com/badhope/awesome-skillkit"><img src="https://img.shields.io/badge/Gitee-镜像-C71D23?style=flat-square" alt="Gitee" /></a>
</p>

<p align="center"><a href="README.md">English</a> | <strong>简体中文</strong> | <a href="README.ja.md">日本語</a></p>

---

## 🌐 一键切回英文

仓库里的 `SKILL.md` 正在由其他协作方翻译为英文，过渡期间中英文混杂。想阅读英文版或把整站翻回英文：

- **[🌐 Google 翻译 — 把官网一键译成英文](https://translate.google.com/translate?sl=zh-CN&tl=en&u=https://x33834.github.io/awesome-skillkit/)**（推荐，免安装）
- **[必应翻译备选](https://cn.bing.com/translator?from=zh-Hans&to=en)**（粘贴链接即可翻译）
- **[沉浸式翻译浏览器扩展](https://github.com/immersive-translate/immersive-translate)**（长期使用推荐，整站中英对照）
- 📄 英文 README：[**README.md**](README.md)

---

## 这是什么？

**awesome-skillkit** 是一套面向 AI 编程 / 智能体工具（Claude Code 以及任何能读取 `SKILL.md` 的工具）的精选**场景技能包**。每个场景包都围绕一个具体的真实工作场景组织——"评审一个 PR"、"搭好一条 CI/CD 流水线"、"把一篇文章一键分发到 16 个中文平台"、"端到端产出一条短视频"——而不是笼统的"工程"或"营销"。

用法极简：

```mermaid
flowchart LR
    A[真实工作场景] --> B[场景包<br/>一包 = 一个场景]
    B --> C[一组协同技能<br/>1–19 个]
    C --> D[拖入 AI 工具<br/>skills 目录]
    D --> E[新会话即用<br/>零配置]
    style A fill:#eaf2ff,stroke:#5b8def
    style E fill:#eafaea,stroke:#4caf72
```

- 每个包都对应一个**具体场景**，落点是平台与工具，而非空泛的领域名词。
- 每个包打包的是**该场景下真正协同工作的那组技能**——小到双人搭档（`API 开发与测试`），大到 19 个技能的全家桶（`AI 研究与写作`），或是一台覆盖 18 个中文平台的分发机器（`内容多平台发布自动化`）。
- 每个技能的**来源都逐项标注**于 [`manifest.json`](manifest.json) 和各 `packs/*/pack.json`——自研、上游精选（MIT）、或基于公开文档蒸馏，不含糊、不混装。

## 下载指南（两条路径）

### 路径 A · 逛官网（最省心）

1. 打开 **<https://x33834.github.io/awesome-skillkit/>**。
2. 按技能名、领域标签或场景包名搜索。
3. 在技能卡片上点 **↓ SKILL.md** 下载单个文件，或在场景包卡片上整包下载 zip。
4. 想一口气全要？英雄区的 **↓ `_all.zip`** 一键拿下。

### 路径 B · 直接逛仓库

| 你想要的 | 去哪里拿 |
|---|---|
| 单个 `SKILL.md` | 浏览 [`skills/`](skills/)，打开原始文件 |
| 单个场景包 zip | [`dist/<pack-id>.zip`](dist/)（本地构建），或 [Releases](https://github.com/x33834/awesome-skillkit/releases/latest) 里对应的资源 |
| 全量打包 | `dist/_all.zip`，或 [`_all.zip` Release 资源](https://github.com/x33834/awesome-skillkit/releases/latest/download/_all.zip) |
| 国内镜像 | [GitCode](https://gitcode.com/badhope/awesome-skillkit) · [Gitee](https://gitee.com/badhope/awesome-skillkit)（标签一致，Release 已挂好资源） |

> 每个包的 zip 由 `python3 build.py` 构建，并随每次 GitHub Release 一起发布；GitCode / Gitee 镜像推送相同标签并上传相同资源。

## 场景包目录（全部 36 个）

下表是完整目录。每行链接到对应包目录，技能列列出了包内打包的全部 `SKILL.md`。

| 包 ID | 场景包 | 名称 (EN) | 技能数 | 包含技能 |
|---|---|---|:---:|---|
| [`ai-agent-development`](packs/ai-agent-development) | **AI Agent 开发** | AI Agent Development | 5 | `agent-designer`, `mcp-server-builder`, `feature-flags-architect`, `self-eval`, `skill-tester` |
| [`ai-media-toolkit`](packs/ai-media-toolkit) | **AI 媒体生成工具箱** | AI Media Toolkit | 4 | `video-generation`, `image-generation`, `music-generation`, `ai-cover-generator` |
| [`ai-research-writing`](packs/ai-research-writing) | **AI 研究与写作** | AI Research & Writing | 19 | `deep-research`, `web-search`, `paper-topic-selector`, `article-outliner`, `article-drafter`, `content-editor`, `seo-optimizer`, `lit-review`, `experiment-runner`, `figure-maker`, `arch-diagram`, `neural-net-draw`, `latex-formatter`, `self-reviewer`, `journal-adapt`, `anti-defensive`, `ai-humanizer`, `tex-cleaner`, `pub-plotter` |
| [`ai-video-pipeline`](packs/ai-video-pipeline) | **AI 短视频生产流水线** | AI Video Pipeline | 6 | `video-script-writer`, `video-voice-synth`, `video-lip-sync`, `video-editor`, `video-subtitles`, `video-thumbnail` |
| [`api-development`](packs/api-development) | **API 开发与测试** | API Development & Testing | 2 | `api-design-reviewer`, `api-test-suite-builder` |
| [`architecture`](packs/architecture) | **系统架构设计** | System Architecture | 3 | `senior-architect`, `migration-architect`, `monorepo-navigator` |
| [`audio-studio`](packs/audio-studio) | **音频工作室** | Audio Studio | 3 | `podcast-producer`, `tts-voice-director`, `episode-publisher` |
| [`chat-prompt-craft`](packs/chat-prompt-craft) | **聊天提示词工艺** | Chat Prompt Craft | 1 | `chat-prompt-engineer` |
| [`ci-cd`](packs/ci-cd) | **CI/CD 流水线** | CI/CD Pipeline | 3 | `ci-cd-pipeline-builder`, `ship-gate`, `spec-driven-workflow` |
| [`code-planning`](packs/code-planning) | **代码规划与生成** | Code Planning & Generation | 3 | `code-intent-planner`, `code-generator`, `debug-diagnoser` |
| [`code-review`](packs/code-review) | **代码审查** | Code Review | 5 | `pr-review-expert`, `code-reviewer`, `api-design-reviewer`, `tech-debt-tracker`, `dependency-auditor` |
| [`containers`](packs/containers) | **容器与编排** | Containers & Orchestration | 3 | `docker-development`, `helm-chart-builder`, `kubernetes-operator` |
| [`content-publishing`](packs/content-publishing) | **内容多平台发布自动化** | Content Publishing Automation | 18 | `zhihu-content-manager`, `cnblogs-skill`, `wechat-mp-publisher`, `juejin-publisher`, `csdn-publisher`, `jianshu-publisher`, `bilibili-publisher`, `toutiao-publisher`, `baijiahao-publisher`, `xiaohongshu-publisher`, `weibo-publisher`, `douban-publisher`, `v2ex-publisher`, `segmentfault-publisher`, `oschina-publisher`, `static-blog-deploy`, `cross-post-orchestrator`, `ai-cover-generator` |
| [`data-ml-science`](packs/data-ml-science) | **数据科学与科学计算** | Data, ML & Scientific Computing | 7 | `etl-builder`, `feature-engineer`, `model-formulator`, `model-solver`, `simulation-runner`, `result-visualizer`, `ml-pipeline` |
| [`database`](packs/database) | **数据库设计与管理** | Database Design & Management | 2 | `database-designer`, `sql-database-assistant` |
| [`dataviz-studio`](packs/dataviz-studio) | **数据可视化工作室** | Data Viz Studio | 2 | `dashboard-designer`, `chart-recommender` |
| [`de-ai-writing`](packs/de-ai-writing) | **去 AI 味写作** | De-AI Writing | 3 | `ai-trace-auditor`, `humanize-rewriter`, `personal-voice-profile` |
| [`edu-craft`](packs/edu-craft) | **教育工艺** | Edu Craft | 3 | `course-designer`, `exercise-generator`, `feynman-explainer` |
| [`github-workflow`](packs/github-workflow) | **GitHub 协作工作流** | GitHub Collaboration | 3 | `git-worktree-manager`, `changelog-generator`, `pr-review-expert` |
| [`growth-marketing`](packs/growth-marketing) | **增长营销** | Growth Marketing | 3 | `product-copywriter`, `campaign-designer`, `channel-adapter` |
| [`homework-autopilot`](packs/homework-autopilot) | **作业自动驾驶** | Homework Autopilot | 3 | `assignment-intake`, `solution-drafter`, `own-voice-rewrite` |
| [`image-studio`](packs/image-studio) | **画图工作台** | Image Studio | 4 | `image-prompt-engineer`, `image-generation`, `visual-style-anchor`, `ai-cover-generator` |
| [`incident-response`](packs/incident-response) | **故障响应与 SRE** | Incident Response & SRE | 3 | `incident-commander`, `runbook-generator`, `slo-architect` |
| [`infrastructure`](packs/infrastructure) | **基础设施即代码** | Infrastructure as Code | 3 | `terraform-patterns`, `observability-designer`, `kubernetes-operator` |
| [`knowledge-base`](packs/knowledge-base) | **个人知识库** | Knowledge Base | 2 | `personal-wiki`, `knowledge-graph-builder` |
| [`memory-systems`](packs/memory-systems) | **长期记忆系统** | Memory Systems | 4 | `memory-architect`, `memory-extractor`, `memory-manager`, `memory-retriever` |
| [`office-productivity`](packs/office-productivity) | **办公效率工具箱** | Office Productivity | 10 | `ppt-builder`, `excel-assistant`, `resume-tailor`, `meeting-notes`, `internal-comms-writer`, `docx-writer`, `pdf-pipeline`, `epub-builder`, `docx-template-fill`, `career-ops-lite` |
| [`performance`](packs/performance) | **性能优化** | Performance Profiling | 1 | `performance-profiler` |
| [`security`](packs/security) | **安全与密钥管理** | Security & Secrets | 4 | `secrets-vault-manager`, `env-secrets-manager`, `pii-redactor`, `prompt-injection-guard` |
| [`skill-forge`](packs/skill-forge) | **技能锻造厂** | Skill Forge | 5 | `skill-author`, `skill-linter`, `skill-finder`, `session-handoff`, `weekly-report-generator` |
| [`tdd`](packs/tdd) | **测试驱动开发** | Test-Driven Development | 4 | `tdd-guide`, `webapp-flow-tester`, `webapp-e2e-harness`, `agent-eval-harness` |
| [`toolsmith`](packs/toolsmith) | **工具与自动化** | Toolsmith | 6 | `file-organizer`, `batch-renamer`, `format-converter`, `task-scheduler`, `invoice-organizer`, `bank-statement-reconcile` |
| [`video-design-studio`](packs/video-design-studio) | **视频设计工作室** | Video Design Studio | 4 | `storyboard-designer`, `shot-recipe-designer`, `video-prompt-engineer`, `visual-style-anchor` |
| [`viral-entertainment`](packs/viral-entertainment) | **爆款娱乐场景** | Viral Entertainment | 2 | `ai-baby-podcast`, `nailong-laugh-shorts` |
| [`visual-design-studio`](packs/visual-design-studio) | **视觉设计工作室** | Visual Design Studio | 5 | `design-brief-interpreter`, `image-prompt-engineer`, `layout-spec-auditor`, `frontend-design-director`, `frontend-component-lab` |
| [`workspace-integrations`](packs/workspace-integrations) | **外部集成工具箱** | Workspace Integrations | 4 | `notion-workspace`, `feishu-dingtalk-bridge`, `issue-tracker-sync`, `cloud-drive-manager` |

> 部分技能（如 `api-design-reviewer`、`kubernetes-operator`、`image-generation`、`ai-cover-generator`）会出现在多个包中——这是有意为之，因为它们在不同场景下被复用。

## 如何安装（30 秒）

1. **下载**你所需场景的 zip（或直接拿 `_all.zip`）。
2. **解压**——你会得到若干个技能文件夹，每个里面有一个 `SKILL.md`。
3. **拖入** AI 工具的 skills 目录：
   - Claude Code：`~/.claude/skills/`（全局）或 `.claude/skills/`（项目级）
   - 其他支持 skills 的工具：放到其官方文档指定的目录即可。
4. **开一个新会话**。无需环境变量、无需配置——当你的请求命中技能描述时，它会自动生效。

## 从源码构建

```bash
python3 build.py     # 为每个包重新生成 dist/<pack-id>.zip，并打包 dist/_all.zip
```

`build.py` 读取 [`manifest.json`](manifest.json) 与各 `packs/*/pack.json`，从 `skills/` 暂存被引用的技能文件夹后写出 zip。`dist/` 已被 gitignore，由 CI / Release 挂载构建产物。

## 参与贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。简而言之：新增场景包请先开 issue；每个新技能必须包含 `SKILL.md`、在对应 `packs/*/pack.json` 中标注来源，并在 [`tests/`](tests/) 下附上冒烟测试。

## 开源协议

[Apache License 2.0](LICENSE) © 2026 Morningstar202604
