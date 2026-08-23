# awesome-skillkit

[English](README.md) | **中文**

面向 AI 工具的精选**场景包**合集。**每个场景包 = 一个真实场景，内含多个精选 skill。** 下载 zip → 解压 → 把 skill 文件夹拖进 AI 工具的 skills 目录 → 直接可用。

## 定位

**场景即答案——落地到平台 + 工具。**

- 每个场景包对应一个**具体场景**（"审查 PR"、"搭建 CI/CD 流水线"、"发博客"），而不是"营销""工程"这类宽泛领域。
- 每个场景包打包 **3–7 个协同工作的 skill**，不用再在上百个零散 skill 里翻找。
- 每个 skill 的**来源都明确标注**（见"来源"列），让大家知道它来自哪里。

## 场景包总览

| 场景包 | 场景 | Skill 数 | 大小 |
|--------|------|----------|------|
| ai-agent-development | AI Agent 开发 | 6 | 883 KB |
| api-development | API 开发与测试 | 2 | 49 KB |
| architecture | 系统架构设计 | 3 | 108 KB |
| blog-writing | 博客写作发文 | 1 | 29 KB |
| ci-cd | CI/CD 流水线 | 3 | 60 KB |
| code-review | 代码审查 | 5 | 242 KB |
| containers | 容器与编排 | 3 | 66 KB |
| database | 数据库设计与管理 | 2 | 95 KB |
| family-communication | 家庭沟通 | 1 | 255 KB |
| github-workflow | GitHub 协作工作流 | 3 | 39 KB |
| incident-response | 故障响应与 SRE | 3 | 118 KB |
| infrastructure | 基础设施即代码 | 3 | 92 KB |
| performance | 性能优化 | 1 | 8 KB |
| security | 安全与密钥管理 | 2 | 45 KB |
| tdd | 测试驱动开发 | 1 | 51 KB |
| zhihu-writing | 知乎写作发文 | 1 | 7 KB |

## 场景包详情

### AI Agent 开发（`ai-agent-development`）— 1796 KB

**构建生产级 AI Agent、设计多 Agent 工作流、MCP 服务、功能开关与自评。**

| Skill | 来源 |
|-------|------|
| agent-builder-skill | weed33834 (self-authored) |
| agent-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| mcp-server-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| feature-flags-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| self-eval | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| skill-tester | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### API 开发与测试（`api-development`）— 100 KB

**审查 REST API 设计并生成集成/契约测试套件。**

| Skill | 来源 |
|-------|------|
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-test-suite-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 系统架构设计（`architecture`）— 223 KB

**设计系统架构、规划零停机迁移、驾驭 monorepo。**

| Skill | 来源 |
|-------|------|
| senior-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| migration-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| monorepo-navigator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 博客写作发文（`blog-writing`）— 60 KB

**博客园发文与管理：选题、写作、配图、API 发布。**

| Skill | 来源 |
|-------|------|
| cnblogs-skill | weed33834 (self-authored) |

### CI/CD 流水线（`ci-cd`）— 126 KB

**生成务实的 CI/CD 流水线、发布门禁与规范驱动开发流程。**

| Skill | 来源 |
|-------|------|
| ci-cd-pipeline-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| ship-gate | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| spec-driven-workflow | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 代码审查（`code-review`）— 502 KB

**审查 PR、分析代码质量、审计依赖与技术债，覆盖多语言。**

| Skill | 来源 |
|-------|------|
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| code-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| tech-debt-tracker | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| dependency-auditor | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 容器与编排（`containers`）— 138 KB

**Dockerfile 优化、docker-compose、Helm Chart 与 Kubernetes Operator。**

| Skill | 来源 |
|-------|------|
| docker-development | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| helm-chart-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 数据库设计与管理（`database`）— 198 KB

**设计表结构、ERD 图、迁移方案，并优化 SQL 查询。**

| Skill | 来源 |
|-------|------|
| database-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| sql-database-assistant | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 家庭沟通（`family-communication`）— 513 KB

**用 10 维画像模拟、诊断与应对中国式家长。**

| Skill | 来源 |
|-------|------|
| chinese-parents-skill | weed33834 (self-authored) |

### GitHub 协作工作流（`github-workflow`）— 83 KB

**并行 worktree、Conventional Commits 变更日志与 GitHub PR 审查。**

| Skill | 来源 |
|-------|------|
| git-worktree-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| changelog-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 故障响应与 SRE（`incident-response`）— 244 KB

**事故指挥、生成 runbook、定义 SLO 与错误预算。**

| Skill | 来源 |
|-------|------|
| incident-commander | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| runbook-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| slo-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 基础设施即代码（`infrastructure`）— 207 KB

**Terraform 模式、可观测性设计与 Kubernetes Operator。**

| Skill | 来源 |
|-------|------|
| terraform-patterns | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| observability-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 性能优化（`performance`）— 17 KB

**剖析 Node.js、Python、Go 的 CPU/内存/IO 瓶颈。**

| Skill | 来源 |
|-------|------|
| performance-profiler | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 安全与密钥管理（`security`）— 80 KB

**搭建密钥库并管理环境变量卫生。**

| Skill | 来源 |
|-------|------|
| secrets-vault-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| env-secrets-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 测试驱动开发（`tdd`）— 105 KB

**编写单元测试、fixture、mock，并引导红绿重构循环。**

| Skill | 来源 |
|-------|------|
| tdd-guide | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### 知乎写作发文（`zhihu-writing`）— 16 KB

**知乎文章发布/编辑/删除、草稿、话题、封面与乱码修复。**

| Skill | 来源 |
|-------|------|
| zhihu-content-manager | weed33834 (self-authored) |

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
├── tdd/
├── blog-writing/
├── zhihu-writing/
└── family-communication/
skills/                         # 所有 skill 源码的唯一真源
└── programming/ | writing/ | life/   # 多级分类
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

源码在 `skills/`；场景包定义在 `packs/*/pack.json`；zip 通过 GitHub Releases 发布（`dist/` 已 gitignore）。

```bash
# 生成 dist/*.zip（每个场景包一个 zip）
bash build.sh        # macOS / Linux / Git Bash
python3 build.py     # 跨平台（无需 bash/zip）；同时生成 dist/_all.zip 全量合集

# 发布流程
git tag v1.2.0
git push origin v1.2.0
# 在 GitHub Releases 页面创建 release 并上传 dist/*.zip
```

## 来源说明

- **33 个 skill** 精选自 [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（MIT 协议）。上游两个近似重复项（`database-schema-designer`、`agent-workflow-designer`）已合并进同源兄弟 skill，其独有内容以参考文档形式保留。
- **4 个 skill** 为仓库作者自建：`agent-builder-skill`、`chinese-parents-skill`、`cnblogs-skill`、`zhihu-content-manager`。
- 每个 skill 的完整来源标注见 [manifest.json](manifest.json) 及各 `packs/*/pack.json`。

## 说明

- 非核心文件（`.github`、`.gitignore`、`docker-compose.yml` 等）不打包进 zip；运行所需内容（`SKILL.md`、`references/`、`scripts/`、`templates/`）保留。
- 各 skill 的依赖（如 Playwright、登录态）见其自身 `SKILL.md`。

## License

[Apache License 2.0](LICENSE) © 2026 weed33834
