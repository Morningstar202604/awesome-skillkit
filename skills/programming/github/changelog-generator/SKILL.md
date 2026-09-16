---
name: changelog-generator
description: "Produce consistent, auditable release notes from Conventional Commits. Separates commit parsing, semantic-bump logic, and changelog rendering for automated releases with editorial control. Use when cutting a release, generating CHANGELOG.md from git history, computing the next semantic version from commits, automating release notes in CI, or planning a hotfix/rollback. Examples: 'generate the changelog for v1.4.0', 'what version bump do these commits require', 'we need an emergency hotfix process'. 当用户要求 生成更新日志 / 写 CHANGELOG / 整理版本变更 时使用。 Do NOT use for publishing releases (generation only)."
license: Apache-2.0
compatibility: Requires docker. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: github
  pattern: code-generator
  tier: powerful
  verified-date: "2026-09-09"
---

# Changelog Generator

从 Conventional Commits 生成一致、可审计的发布说明。编排 commit 解析、语义化版本推算与 CHANGELOG 渲染三步；只生成，不发布。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 当前目录的 git 仓库 | 必需 | 脚本直接调用 `git` 读取历史 |
| 版本范围 | 必需 | 二选一：`--from-tag/--to-tag` 或 `--input <文件\|stdin>` 提供 commit 列表 |
| `--next-version` | 条件必需 | 渲染 CHANGELOG 条目时必须给出目标版本号 |
| `--format` | 可选 | `markdown`（默认，给人看）或 `json`（CI 机读） |
| `--write` | 可选 | 目标 `CHANGELOG.md` 路径；不传则只打印预览 |

缺失输入时一次性问齐：「请提供：①git 仓库路径（默认当前目录）②版本范围：起始 tag/结束 tag，或 commit 列表文件 ③目标版本号（如 v1.4.0）④输出格式 markdown/json（默认 markdown）。其余我采用默认值：不写文件、仅渲染 Added/Changed/Fixed。」

## 前置自检

运行前探测环境，任一失败→输出修复指引并 STOP：

```bash
git rev-parse --is-inside-work-tree   # 预期输出 true；失败：当前目录非 git 仓库 → cd 到仓库根或 STOP
python3 scripts/generate_changelog.py --help >/dev/null 2>&1   # 预期退出码 0；失败：脚本缺失或 python3 不可用
python3 scripts/version_bumper.py --help >/dev/null 2>&1
python3 scripts/commit_linter.py --help >/dev/null 2>&1
```

## 工作流

### 步骤 1：计算下一个语义化版本（用户未定版本时）

```bash
git log v1.3.0..HEAD --oneline | \
  python3 scripts/version_bumper.py --current-version 1.3.0 --output-format json
```

预期：输出含 `recommended_version` 与 `bump_type`（`major`/`minor`/`patch`/`none`）；加 `--include-commands` 时附 `git tag` 命令。
若失败：输入非真实 `git log --oneline`（缺 hex 哈希）→ 改用 `git log v1.3.0..HEAD --oneline` 重取；`--current-version` 非纯 semver → 改为合规版本号。

### 步骤 2：从 git 范围或 commit 列表生成条目

```bash
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag v1.4.0 \
  --next-version v1.4.0 --format markdown
```

或通过 stdin/文件：

```bash
git log v1.3.0..v1.4.0 --pretty=format:'%s' | \
  python3 scripts/generate_changelog.py --next-version v1.4.0 --format markdown
python3 scripts/generate_changelog.py --input commits.txt --next-version v1.4.0 --format json
```

预期：stdout 输出 Keep a Changelog 分段（Added/Changed/Fixed…）；无有效 conventional commit 时脚本 early-fail，不产出误导性空说明。
若失败：范围无效（`--from-tag` 不存在）→ 报错显式给出范围；commit 非 conventional → 提示先跑步骤 4 lint。

### 步骤 3：写回 CHANGELOG.md（默认 dry-run，需确认）

```bash
# 先预览（默认行为：不加 --write 只打印）
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag HEAD \
  --next-version v1.4.0 --format markdown
# 确认无误、经用户确认后再写：
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag HEAD \
  --next-version v1.4.0 --write CHANGELOG.md
```

预期：`--write` 后文件头部插入新条目，保留历史条目不覆盖。
若失败：写目标缺失→脚本创建安全表头骨架；若误覆盖历史 sections→从 `git` 恢复历史条目（工具为 prepend，非覆盖）。

### 步骤 4：合并前 lint commit 格式

```bash
python3 scripts/commit_linter.py --from-ref origin/main --to-ref HEAD --strict --format text
# 或文件/stdin：
python3 scripts/commit_linter.py --input commits.txt --strict
cat commits.txt | python3 scripts/commit_linter.py --format json
```

预期：`--strict` 下违例返回非零退出码，CI 据此阻断合并；text 模式打印违例行。
若失败：取不到 `origin/main`（远端未配/无网）→ 改用本地 `main..HEAD`；有违例→按输出逐条修复后重跑。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--from-tag` / `--to-tag` | git tag 名 | 定义版本范围；与 `--input` 互斥 |
| `--input` | 文件路径或 stdin | commit 列表（`git log --pretty=format:'%s'` 或 `--oneline`） |
| `--next-version` | semver（如 1.4.0） | 渲染的 CHANGELOG 版本号 |
| `--format` | `markdown` \| `json` | markdown 给人看，json 给 CI |
| `--write` | 文件路径 | 就地 prepend 到 CHANGELOG；不传=预览 |
| `--prerelease` | `alpha`\|`beta`\|`rc` | 仅 `version_bumper.py`：预发布后缀 |
| `--include-commands` | flag | 仅 `version_bumper.py`：输出 `git tag` 命令 |
| `--strict` | flag | 仅 `commit_linter.py`：违例即非零退出 |

## Conventional Commit 规则

支持类型：`feat` `fix` `perf` `refactor` `docs` `test` `build` `ci` `chore` `security` `deprecated` `remove`。
破坏性变更：`type(scope)!: summary` 或 body 含 `BREAKING CHANGE:`。
SemVer 映射：breaking → `major`；非破坏性 `feat` → `minor`；其余 → `patch`。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `recommended_version` 为空 | 输入非真实 git log | 用 `git log vX..HEAD --oneline` 重取 |
| early-fail「no valid conventional commits」 | 范围无合规提交 | 确认范围或先 lint；勿生成空说明 |
| `--write` 覆盖历史 sections | 误用覆盖模式 | 工具为 prepend；已覆盖则从 `git` 恢复 |
| `commit_linter` 非零退出 | 存在违例 commit | 按输出逐个修复后重跑 |
| 取不到 `origin/main` | 远端未配/无网 | 改用本地 `main..HEAD` |

## 交付标准

成功定义：产出结构化 CHANGELOG 条目，breaking change 含迁移动作、安全修复归入 `Security` 段、空段省略、跨段重复去除。
产物命名：`CHANGELOG.md`（仓库根，Keep a Changelog 格式）或 `<name>.json`（CI 产物）。
保存位置：仓库根目录，进入版本控制。
验证完整性：`--format json` 供 CI 校验；人工 review 草稿后再 `tag`；以 `commit_linter.py --strict` 作为合并门禁。

## 安全红线

- `--write` 为写操作，默认 dry-run（不传只预览）；写 `CHANGELOG.md` 前必须向用户确认。
- 仅生成不发布：本技能不执行 `git tag` / `git push`；tag 与发布由用户在生成确认后进行。
- 示例样本 `assets/sample_git_log.txt` 仅作输入格式样例，非真实仓库数据。

## 参考

- `references/changelog-formatting-guide.md` —— 渲染分段规则与措辞规范时读
- `references/ci-integration.md` —— 接入 CI 自动产出发布说明时读
- `references/monorepo-strategy.md` —— 多包仓库按 scope 过滤 changelog 时读
- `references/hotfix-procedures.md` —— 发布出错需分类 P0–P2 并定 hotfix/rollback 流程时读
- `README.md` —— 安装与快速上手
