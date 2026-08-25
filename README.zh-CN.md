# awesome-skillkit

[English](README.md) | **中文**

面向 AI 工具的精选**场景包**合集。**每个场景包 = 一个真实场景，内含多个精选 skill。** 下载 zip → 解压 → 把 skill 文件夹拖进 AI 工具的 skills 目录 → 直接可用。

## 定位

**场景即答案——落地到平台 + 工具。**

- 每个场景包对应一个**具体场景**（"审查 PR"、"搭建 CI/CD 流水线"、"发博客"），而不是"营销""工程"这类宽泛领域。
- 每个场景包打包**协同工作的 skill 组合**——小到精简一对、大到 18 个技能的全家桶（content-publishing 端到端覆盖 16 个中文平台），不用再在上百个零散 skill 里翻找。
- 每个 skill 的**来源都明确标注**（见"来源"列），让大家知道它来自哪里。

## 场景包总览

| 场景包 | 场景 | Skill 数 | 大小 |
|--------|------|----------|------|
| ai-agent-development | AI Agent 开发 | 5 | 145 KB |
| api-development | API 开发与测试 | 2 | 49 KB |
| architecture | 系统架构设计 | 3 | 108 KB |
| ci-cd | CI/CD 流水线 | 3 | 60 KB |
| code-review | 代码审查 | 5 | 242 KB |
| containers | 容器与编排 | 3 | 66 KB |
| content-publishing | 内容多平台发布自动化 | 18 | 127 KB |
| database | 数据库设计与管理 | 2 | 99 KB |
| github-workflow | GitHub 协作工作流 | 3 | 43 KB |
| incident-response | 故障响应与 SRE | 3 | 122 KB |
| infrastructure | 基础设施即代码 | 3 | 96 KB |
| performance | 性能优化 | 1 | 12 KB |
| security | 安全与密钥管理 | 2 | 49 KB |
| tdd | 测试驱动开发 | 1 | 55 KB |

## 场景包详情

### AI Agent 开发（`ai-agent-development`）— 145 KB

**构建生产级 AI Agent、设计多 Agent 工作流、MCP 服务、功能开关与自评。**

| Skill | 来源 |
|-------|------|
| agent-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| mcp-server-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| feature-flags-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| self-eval | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| skill-tester | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### API 开发与测试（`api-development`）— 49 KB

**审查 REST API 设计并生成集成/契约测试套件。**

| Skill | 来源 |
|-------|------|
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-test-suite-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 系统架构设计（`architecture`）— 108 KB

**设计系统架构、规划零停机迁移、驾驭 monorepo。**

| Skill | 来源 |
|-------|------|
| senior-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| migration-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| monorepo-navigator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### CI/CD 流水线（`ci-cd`）— 60 KB

**生成务实的 CI/CD 流水线、发布门禁与规范驱动开发流程。**

| Skill | 来源 |
|-------|------|
| ci-cd-pipeline-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| ship-gate | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| spec-driven-workflow | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 内容多平台发布自动化（`content-publishing`）— 127 KB

**在知乎、博客园、微信公众号、掘金、CSDN、简书、B站、头条、百家号、小红书、微博、豆瓣、V2EX、SegmentFault、开源中国、静态博客等中文平台发布、编辑、管理内容——沉淀实战平台经验；附跨平台发布编排器与 AI 封面图生成。**

| Skill | 来源 |
|-------|------|
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

### 代码审查（`code-review`）— 242 KB

**审查 PR、分析代码质量、审计依赖与技术债，覆盖多语言。**

| Skill | 来源 |
|-------|------|
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| code-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| tech-debt-tracker | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| dependency-auditor | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 容器与编排（`containers`）— 66 KB

**Dockerfile 优化、docker-compose、Helm Chart 与 Kubernetes Operator。**

| Skill | 来源 |
|-------|------|
| docker-development | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| helm-chart-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 数据库设计与管理（`database`）— 99 KB

**设计表结构、ERD 图、迁移方案，并优化 SQL 查询。**

| Skill | 来源 |
|-------|------|
| database-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| sql-database-assistant | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### GitHub 协作工作流（`github-workflow`）— 43 KB

**并行 worktree、Conventional Commits 变更日志与 GitHub PR 审查。**

| Skill | 来源 |
|-------|------|
| git-worktree-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| changelog-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 故障响应与 SRE（`incident-response`）— 122 KB

**事故指挥、生成 runbook、定义 SLO 与错误预算。**

| Skill | 来源 |
|-------|------|
| incident-commander | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| runbook-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| slo-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 基础设施即代码（`infrastructure`）— 96 KB

**Terraform 模式、可观测性设计与 Kubernetes Operator。**

| Skill | 来源 |
|-------|------|
| terraform-patterns | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| observability-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 性能优化（`performance`）— 12 KB

**剖析 Node.js、Python、Go 的 CPU/内存/IO 瓶颈。**

| Skill | 来源 |
|-------|------|
| performance-profiler | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 安全与密钥管理（`security`）— 49 KB

**搭建密钥库并管理环境变量卫生。**

| Skill | 来源 |
|-------|------|
| secrets-vault-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| env-secrets-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 测试驱动开发（`tdd`）— 55 KB

**编写单元测试、fixture、mock，并引导红绿重构循环。**

| Skill | 来源 |
|-------|------|
| tdd-guide | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

## 目录结构

```
packs/                          # 场景包定义（每个场景一个目录）
├── code-review/                #   pack.json：场景元数据 + skill 清单 + 来源
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
skills/                         # 所有 skill 源码的唯一真源
├── programming/                # 上游精选（多级分类）
└── writing/                    # 自建场景技能
    ├── blog/                   #   博客园 / CSDN / 简书 / 静态博客部署
    ├── zhihu/  wechat/  juejin/#   各平台发布器
    ├── social/                 #   小红书 / 微博
    ├── video/  news/           #   B站 / 头条 / 百家号
    ├── community/              #   V2EX / SegmentFault / 开源中国 / 豆瓣
    ├── assets/  orchestrator/  #   AI 封面图 / 跨平台编排器
    └── _common/                #   共享 HTTP/dry-run/凭据 工具（非技能）
dist/                           # 构建产物：每个场景包一个 zip（已 gitignore）
```

## 快速上手（30 秒）

1. 从 **Releases** 下载你需要的**场景包** zip（或本地运行 `python3 build.py` 生成 `dist/*.zip`）。
2. 解压后得到**多个 skill 文件夹**（每个含 `SKILL.md`）。
3. 把 skill 文件夹**拖进** AI 工具的 skills 目录：
   - Claude Code：`~/.claude/skills/`（全局）或项目内 `.claude/skills/`（仅项目）
   - 其他支持 skills 的工具：使用其对应的 skills 目录
4. 新开会话即可使用，无需任何配置。

## 构建与发布

源码在 `skills/`；场景包定义在 `packs/*/pack.json`；zip 通过 Gitee / GitCode 的平台 Releases 发布（`dist/` 已 gitignore）。

```bash
# 生成 dist/*.zip（每个场景包一个 zip）
bash build.sh        # macOS / Linux / Git Bash
python3 build.py     # 跨平台（无需 bash/zip）；同时生成 dist/_all.zip 全量合集

# 发布流程
git tag v1.6.2
git push origin v1.6.2
git push gitee v1.6.2
# 在 Gitee / GitCode 的 Releases 页面创建 release 并上传 dist/*.zip
```

## 来源与更新

本仓库维护两条线：

**1. 上游精选**——从这里更新：

- **上游仓库**：[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（MIT 协议）——全部 33 个编程技能。
- 上游两个近似重复项（`database-schema-designer`、`agent-workflow-designer`）已合并进同源兄弟 skill，其独有内容以参考文档形式保留。

拉取上游更新的方法：克隆上游仓库，把对应 skill 文件夹重新复制到 `skills/programming/...`，再运行 `python3 build.py` 重新打包。

**2. 自建场景技能**（`skills/writing/`，场景包 `content-publishing`）：

- `zhihu-content-manager` / `cnblogs-skill` / `wechat-mp-publisher` / `juejin-publisher` / `csdn-publisher` / `jianshu-publisher` / `bilibili-publisher` / `toutiao-publisher` / `baijiahao-publisher` / `xiaohongshu-publisher` / `weibo-publisher` / `douban-publisher` / `v2ex-publisher` / `segmentfault-publisher` / `oschina-publisher` / `static-blog-deploy` / `cross-post-orchestrator` / `ai-cover-generator` 沉淀了中文平台特有的自动化知识，上游不覆盖。本仓库自行维护；每个技能都附带可执行、带单元测试的检查脚本，写操作默认 dry-run。

每个 skill 的完整来源标注见 [manifest.json](manifest.json)、各 `packs/*/pack.json` 及 [SOURCES.md](SOURCES.md)。

## 说明

- 非核心文件（`.github`、`.gitignore`、`docker-compose.yml` 等）不打包进 zip；运行所需内容（`SKILL.md`、`references/`、`scripts/`、`templates/`）保留。
- 各 skill 的依赖（如 Playwright、登录态）见其自身 `SKILL.md`。

## License

[Apache License 2.0](LICENSE) © 2026 weed33834
