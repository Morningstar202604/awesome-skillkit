---
name: git-worktree-manager
description: "Run parallel feature work safely with Git worktrees. Standardizes branch isolation, port allocation, environment sync, and cleanup so each worktree behaves like an independent local app. Optimized for multi-agent workflows where each agent or terminal session owns one worktree. Use when running multiple feature branches simultaneously, isolating experimental work, or coordinating multi-agent development across the same repo. 当用户要求 用 git worktree / 多分支并行开发 时使用。 Do NOT use for resolving merge conflicts inside a worktree."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: github
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-09"
---

# Git Worktree Manager

用 Git worktree 安全地并行开发：每分支一个隔离工作树、自动化端口分配、环境同步与清理。面向多智能体工作流，每个 agent/终端会话独占一个 worktree。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `--repo` | 必需 | 主仓库路径（默认 `.`） |
| `--branch` | 必需（创建时） | 新/已有分支名，如 `feature/new-auth` |
| `--name` | 必需（创建时） | worktree 目录名，建议 `wt-<topic>` |
| `--base-branch` | 可选 | 新分支的基点，如 `main`/`develop` |
| `--stale-days` | 可选 | 清理时判定陈旧的存活天数（默认 14） |
| `--install-deps` | 可选 | 按 lockfile 探测安装依赖 |
| `--format` | 可选 | `text`（人审，默认）或 `json`（流水线） |

缺失输入时一次性问齐：「请提供：①主仓库路径（默认当前目录）②分支名 ③worktree 名（建议 `wt-<topic>`）④基点分支（默认 `main`）。其余默认：不装依赖、输出 text。」

## 前置自检

```bash
git rev-parse --is-inside-work-tree   # 预期 true；失败：非 git 仓库 → STOP
python3 scripts/worktree_manager.py --help >/dev/null 2>&1   # 预期退出码 0；失败：脚本/ python3 缺失
python3 scripts/worktree_cleanup.py --help >/dev/null 2>&1
git rev-parse --verify main >/dev/null 2>&1   # 预期基点分支存在；失败：确认 --base-branch
```

## 工作流

### 步骤 1：创建完整预置的 worktree

```bash
python3 scripts/worktree_manager.py \
  --repo . \
  --branch feature/new-auth \
  --name wt-auth \
  --base-branch main \
  --install-deps \
  --format text
```

预期：创建 worktree 目录并切到目标分支（不存在则基于基点新建），生成 `.worktree-ports.json` 端口映射，复制 `.env*`，脚本退出码 0。
若失败：目标路径已存在→检查路径，勿覆盖；依赖安装失败→保留 worktree、标记状态转人工恢复；`.env` 复制失败→告警并列出缺失文件继续。

### 步骤 2：流水线/多智能体输入（JSON 模式）

```bash
cat config.json | python3 scripts/worktree_manager.py --format json
# 或
python3 scripts/worktree_manager.py --input config.json --format json
```

预期：同步骤 1，输出为 JSON 便于机器消费。
若失败：JSON 字段缺 `branch`/`name`→校验输入 schema 后重传。

### 步骤 3：并行会话约定

- 主仓库：集成分支（`main`/`develop`）占默认端口。
- 每个 worktree：偏移端口，端口分配写入该树下的 `.worktree-ports.json`。
- 每个 worktree 独占一个 agent，避免共享分支。

### 步骤 4：带安全检查的清理

```bash
python3 scripts/worktree_cleanup.py --repo . --stale-days 14 --format text
python3 scripts/worktree_cleanup.py --repo . --remove-merged --format text
```

预期：仅移除「已合并 + 工作树干净」的 worktree；扫描报告无意外残留脏树。
若失败：存在未提交改动→默认不移除，列出路径；需强制移除须显式 `--force` 且经用户确认（见安全红线）。

## 端口分配策略

默认 `base + (index * stride)` 并做冲突检测：App `3000`、Postgres `5432`、Redis `6379`、stride `10`。
完整策略与边界情况见 `references/port-allocation-strategy.md`。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--repo` | 路径 | 主仓库（默认 `.`） |
| `--branch` | 分支名 | 新/已有分支 |
| `--name` | 名字 | worktree 目录名 |
| `--base-branch` | 分支名 | 新分支基点 |
| `--install-deps` | flag | 按 lockfile 安装依赖 |
| `--stale-days` | 整数 | 清理陈旧阈值（默认 14） |
| `--remove-merged` | flag | 仅移除已合并 worktree |
| `--force` | flag | 强制移除（含脏树）—需用户确认 |
| `--format` | `text`/`json` | 输出形态 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `git worktree add` 失败（路径已存在） | 目标路径占用 | 检查路径，勿覆盖 |
| 依赖安装失败 | lockfile 或网络问题 | 保留 worktree 转人工恢复 |
| `.env` 复制失败 | 源仓库无该文件 | 告警列出缺失项继续 |
| 端口冲突 | 与外部服务撞端口 | 调 `--base` 重跑分配 |
| 清理扫描到脏树 | 有未提交改动 | 默认不移除；强制须确认 |

## 交付标准

成功定义：`git worktree list` 显示预期路径+分支；`.worktree-ports.json` 存在且端口唯一；`.env` 已复制（源有则成功）；依赖安装退出码 0；清理扫描无意外脏树。
产物命名：worktree 目录 `<name>/`，端口映射 `.worktree-ports.json`（位于 worktree 内）。
保存位置：主仓库同级目录；端口映射随 worktree 留存。
验证完整性：运行上方三条 `git worktree list` / `.worktree-ports.json` / `git status` 检查。

## 安全红线

- **移除是破坏性操作**：`worktree_cleanup.py` 默认只删「已合并且干净」的树；删脏树/未合并树必须显式 `--force` 且先向用户确认，确认前不执行。
- 端口映射写入文件而非记忆/终端便签；多智能体用 `wt-<taskId>` 命名避免误提交到错误窗口。
- 清理后若删错了，需从 `git worktree prune` 之外的备份恢复——因此确认前务必复核路径。

## 参考

- `references/port-allocation-strategy.md` —— 端口分配完整策略与边界情况
- `references/docker-compose-patterns.md` —— 每 worktree 覆盖 `docker-compose` 模板
- `README.md` —— 快速上手与安装
