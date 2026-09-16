---
name: ci-cd-pipeline-builder
description: "Generate pragmatic CI/CD pipelines from detected project stack signals — fast baseline generation, repeatable checks, environment-aware deployment stages. Use when setting up CI for a new project, refactoring existing pipelines, or standardizing deployment workflows across multiple repos. 当用户要求 搭 CI/CD 流水线 / 配置自动构建部署 时使用。 Do NOT use for debugging an existing pipeline on a live runner."
license: Apache-2.0
compatibility: Pure prompt-based; runs Python stdlib scripts via Bash. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: cicd
  pattern: pipeline-builder
  tier: powerful
  verified-date: "2026-09-09"
---

# CI/CD Pipeline Builder

从检测到的项目栈信号生成务实的 CI/CD 流水线（不靠猜）：先探测技术栈，产出带缓存与 matrix 策略的 GitHub Actions 或 GitLab CI 基线 YAML，合并前完成校验。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 仓库路径 | 是 | 待生成流水线的项目根目录，如 `.` |
| CI 平台 | 是 | github / gitlab（决定 `--platform`，脚本仅支持这两种） |
| 输出路径 | 否 | GitHub 默认写入 `.github/workflows/` 下的 `ci.yml`；GitLab 默认 `.gitlab-ci.yml` |
| 栈检测报告 | 否 | 已有 `detected-stack.json` 时用 `--input`，跳过重复检测 |

输入缺失时一次性问齐："请提供：① 仓库路径；② 目标平台（GitHub Actions 还是 GitLab CI）；③ 是否有已生成的检测报告可复用。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。

# 2. 两个工具脚本存在
ls scripts/stack_detector.py scripts/pipeline_generator.py
# 预期：两个文件名（在技能目录内执行）。失败→cd 到技能目录；仍缺→STOP 回报。

# 3. 目标仓库存在且含栈信号
ls <仓库路径>/package.json <仓库路径>/requirements.txt <仓库路径>/pyproject.toml <仓库路径>/go.mod <仓库路径>/Cargo.toml 2>/dev/null
# 预期：至少一个文件。全空→确认项目类型，否则检测将一无所获，STOP。
```

## 工作流

### 步骤 1：检测技术栈

```bash
python3 scripts/stack_detector.py --repo . --format text
python3 scripts/stack_detector.py --repo . --format json > detected-stack.json
```

- **动作**：从仓库文件（lockfile、manifest、配置）探测语言/运行时/工具链；`--input` 或 stdin 可喂预计算的信号 JSON 做离线分析。
- **预期**：text 模式输出可读栈摘要；json 模式生成 `detected-stack.json`。
- **若失败**：输出为空 → 仓库无已知信号文件，向用户确认项目类型后 STOP。

### 步骤 2：生成流水线

```bash
# 从检测报告生成（推荐，两步可复查）
python3 scripts/pipeline_generator.py \
  --input detected-stack.json \
  --platform github \
  --output .github/workflows/ci.yml \
  --format text

# 或从仓库直接端到端生成
python3 scripts/pipeline_generator.py --repo . --platform gitlab --output .gitlab-ci.yml
```

- **动作**：按检测结果生成含 `lint`/`test`/`build` 阶段与缓存/matrix 策略的 YAML；`--output` 缺省时打印到 stdout。
- **预期**：目标路径生成合法 YAML，包含检测到的构建/测试命令。
- **若失败**：报 `--platform` 缺失 → 该参数必填（github/gitlab 二选一）；YAML 为空 → 检测报告无信号，重跑步骤 1。

### 步骤 3：合并前校验

1. 确认 YAML 里引用的命令（`test`/`lint`/`build`）在项目的构建定义（package.json scripts、Makefile 目标）中真实存在。
2. 尽量本地复现流水线命令（如 `npx act` 或逐条执行 script）。
3. 确认所需 secrets/env var 已在 YAML 注释或文档中列明。
4. 确认 deploy job 仅由受保护分支/环境触发。

- **预期**：四项逐一核对通过；任何引用命令不存在即为 FAIL。
- **若失败**：命令不存在 → 改用项目真实命令重新生成（重跑步骤 2），不要手写占位命令。

### 步骤 4：安全添加部署阶段

- **动作**：按顺序演进：先 CI-only（lint/test/build）→ 加 staging 部署（显式 environment）→ 加生产部署（人工审批门禁）；rollout/rollback 命令保持显式可审计。部署细节与门禁模式见参考 `deployment-gates.md`。
- **预期**：每次演进后 YAML 仍通过步骤 3 的四项核对。
- **若失败**：用户要求直接上生产部署无门禁 → 说明风险（无人工审批的自动上线），坚持保留 manual gate 或获得书面确认。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `--repo` | 目录路径 | 扫描目标仓库 |
| `--input` | JSON 文件 | 预计算栈检测报告（离线分析） |
| `--format` | text / json | 输出格式 |
| `--platform` | github / gitlab | 必填；目标 CI 平台 |
| `--output` | 文件路径 | YAML 落盘路径，缺省 stdout |

## 平台决策速查

| 因素 | GitHub Actions | GitLab CI | Jenkins |
|--------|---------------|-----------|---------|
| **搭建方式** | YAML 放 .github/workflows | YAML 放 .gitlab-ci.yml | Groovy/Jenkinsfile |
| **运行器** | GitHub 托管、自托管 | 共享级、组级、项目级 | 自托管 |
| **密钥** | 仓库/环境变量 | CI/CD Variables | Credentials 插件 |
| **缓存** | actions/cache | cache key/tag | Workspace 清理 |
| **矩阵** | strategy.matrix | parallel:matrix | Matrix Authorization |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| `error: the following arguments are required: --platform` | 生成时未指定平台 | 补 `--platform github\|gitlab` |
| 检测输出为空 | 仓库无已知信号文件 | 与用户确认项目类型；确认后仍空则 STOP |
| YAML 引用不存在的命令 | 检测信号与实际 scripts 不符 | 改用项目真实命令重新生成 |
| 生成路径目录不存在 | `.github/workflows/` 未创建 | `mkdir -p` 后重跑，或确认用户接受路径 |

## 交付标准

- 成功定义：`detected-stack.json`（如两步走）与目标平台 YAML 均生成，且步骤 3 四项核对全过。
- 产物命名：GitHub → 写入 `.github/workflows/` 下的 `ci.yml`；GitLab → `.gitlab-ci.yml`；检测报告 `detected-stack.json`。
- 保存位置：目标仓库内对应路径（写入前向用户确认）。
- 完整性验证：YAML 可被 `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <file>`（或 `npx js-yaml <file>`）解析无错。

## 参考

- `references/pipeline-design-notes.md` — 检测启发式、生成策略、平台取舍、合并前校验清单、扩展指引；解读检测结果或定制流水线时读。
- `references/github-actions-templates.md` — GitHub Actions 模板；生成 GitHub YAML 后需要进阶配置时读。
- `references/gitlab-ci-templates.md` — GitLab CI 模板；生成 GitLab YAML 后需要进阶配置时读。
- `references/deployment-gates.md` — 部署门禁与回滚模式；执行步骤 4 时读。
