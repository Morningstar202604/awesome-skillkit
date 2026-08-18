---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_1c7ffc529a2411f1a98a525400f8a581
    ReservedCode1: c4Rcdsi8C/sVj6fiVq4Ms4viKQX6q4HD1vDadl70xfx5rJy2EmbQEOQ+p5zksHxfy/Coo9Ty/ZYTVdtB+lUOC58bDmBroB3c0KeHPHaGLU2OtOAyuBoohhqEJkz/I15vnYjSCc/8Rl5BSj3TgOStUmyPjqXvQUEaME3595ryAZRWcCD0Ry0lIH7/OI0=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_1c7ffc529a2411f1a98a525400f8a581
    ReservedCode2: c4Rcdsi8C/sVj6fiVq4Ms4viKQX6q4HD1vDadl70xfx5rJy2EmbQEOQ+p5zksHxfy/Coo9Ty/ZYTVdtB+lUOC58bDmBroB3c0KeHPHaGLU2OtOAyuBoohhqEJkz/I15vnYjSCc/8Rl5BSj3TgOStUmyPjqXvQUEaME3595ryAZRWcCD0Ry0lIH7/OI0=
---



# awesome-skillkit

[English](README.md) | **中文**

常用技能包合集。**下载 zip → 解压 → 拖进 AI 工具的 skills 目录 → 立即生效**，不用再纠结一堆技能该用哪个。

## 定位

**场景即答案，落地到平台+工具。**

- 每个技能包对应一个**具体使用场景**（"我要发博客"、"我要发知乎"），而不是"营销""工程"这类大领域。
- 细节落到**平台 + 工具**：如"博客园发文"（cnblogs.com + API/浏览器）、"知乎发文"（zhihu.com + Playwright）。
- 包内只放精选的 3-5 个技能，下载即用，不堆数量。

## 快速选择

| 技能 | 场景 | 平台 + 工具 | 什么时候用 |
|------|------|-----------|-----------|
| [agent-builder-skill](skills/programming/ai-agents/agent-builder-skill/) | 编程 > AI Agent | 通用 + 代码生成 | 想"做个 XX 应用/Agent"，但不想多轮沟通 |
| [chinese-parents-skill](skills/life/family/chinese-parents-skill/) | 生活 > 家庭 | 通用 + 模拟/诊断 | 想理解家长、分析家长类型、不知道怎么开口 |
| [cnblogs-skill](skills/writing/blog/cnblogs-skill/) | 写作 > 博客 | 博客园 cnblogs.com + API/浏览器 | 要发博文、管理博客、社区互动 |
| [zhihu-content-manager](skills/writing/zhihu/zhihu-content-manager/) | 写作 > 知乎 | 知乎 zhihu.com + Playwright | 要发/改/删知乎文章、清草稿、修乱码 |

## 目录结构

技能按**场景 → 子场景**多级目录组织，直接浏览目录树即可找到对应技能包，不用看一长串平铺列表。

```
skills/
├── programming/
│   ├── ai-agents/
│   │   └── agent-builder-skill/        # 一句话需求 -> 生产级 AI Agent
│   ├── ai-engineering/                 # mcp-server-builder、feature-flags-architect、self-eval、skill-tester
│   ├── api/                            # api-design-reviewer、api-test-suite-builder
│   ├── architecture/                   # senior-architect、migration-architect、monorepo-navigator
│   ├── cicd/                           # ci-cd-pipeline-builder、ship-gate、spec-driven-workflow
│   ├── code-quality/                   # code-reviewer、tdd-guide、tech-debt-tracker、dependency-auditor
│   ├── containers/                     # docker-development、helm-chart-builder
│   ├── database/                       # database-designer、database-schema-designer、sql-database-assistant
│   ├── github/                         # pr-review-expert、git-worktree-manager、changelog-generator
│   ├── incident/                       # incident-commander、runbook-generator、slo-architect
│   ├── infrastructure/                 # kubernetes-operator、observability-designer、terraform-patterns
│   ├── performance/                    # performance-profiler
│   ├── security/                       # env-secrets-manager、secrets-vault-manager
│   └── workflow/                       # agent-designer、agent-workflow-designer
├── writing/
│   ├── blog/
│   │   └── cnblogs-skill/              # 博客园发文与管理
│   └── zhihu/
│       └── zhihu-content-manager/      # 知乎文章发布/编辑/删除
└── life/
    └── family/
        └── chinese-parents-skill/      # 理解家长、与家长沟通
```

## 怎么用（30 秒上手）

1. 从 **Releases** 下载对应技能的 zip（或直接使用 `skills/` 下的源码目录）
2. 解压，得到一个以技能名命名的文件夹（内含 `SKILL.md`）
3. 把整个文件夹**拖进** AI 工具的 skills 目录：
   - Claude Code：`~/.claude/skills/`（全局）或项目下 `.claude/skills/`（仅该项目）
   - 其他支持 skills 的工具：放入其对应 skills 目录
4. 新开会话即可触发，无需任何配置

> 也可以一键安装全部技能（见下方"一键安装"）。

## 一键安装

把全部技能解压到 `~/.claude/skills/`：

```bash
# 1. 先生成压缩包（若 dist/ 为空）
bash build.sh

# 2. Linux / macOS
bash install.sh

# Windows (PowerShell)
.\install.ps1
```

指定安装目录：

```bash
bash install.sh /path/to/skills-dir
```

## 打包发布

源码在 `skills/`，压缩包通过 GitHub Releases 发布（不进仓库，`dist/` 已被 .gitignore 忽略）。

```bash
# 生成 dist/*.zip
bash build.sh

# 发布流程
git tag v1.0.0
git push origin v1.0.0
# 在 GitHub Releases 页面创建 release，上传 dist/*.zip
```

## 技能清单

完整元数据见 [manifest.json](manifest.json)（名称 / 类别 / 触发词 / 大小）。

| 技能 | 大小 | 来源 |
|------|------|------|
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

## 说明

- 收录本人自建仓库的 skill，并精选 [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（MIT）的开发者场景技能包。
- 打包时已剔除 `.github`、`.gitignore`、`docker-compose.yml` 等非技能核心文件，保留 `SKILL.md`、`references/`、`scripts/`、`templates/` 等运行所需内容。
- 各技能依赖（如 playwright、登录态）以各自 `SKILL.md` 内说明为准。
*（内容由AI生成，仅供参考）*

## 许可证

[Apache License 2.0](LICENSE) © 2026 weed33834
