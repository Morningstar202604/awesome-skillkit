---
name: pr-review-expert
description: "Use when the user asks to review pull requests or merge requests end-to-end on GitHub/GitLab (gh/glab CLI recipes), assess a diff's blast radius, check breaking changes and coverage delta, or run a structured PR review checklist. For deterministic static analysis of files/diffs (secrets, SQLi, complexity scoring), chain in code-reviewer as the analysis engine. 当用户要求 审查 PR / 看这个 pull request 时使用。 Do NOT use for pushing fixes itself (review and verdict only)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: github
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# PR Review Expert

对 GitHub PR / GitLab MR 做端到端结构化代码评审：影响面分析、安全扫描、破坏性变更检测、测试覆盖 delta，产出带优先级的评审报告。只评审不下场改代码。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| PR/MR 编号 | 必需 | GitHub `gh` 用数字 ID；GitLab `glab` 用 IID |
| 平台（GitHub / GitLab） | 必需 | 决定用 `gh` 还是 `glab` 命令 |
| 是否验证关联票据 | 可选 | 若要，需 `JIRA_API_TOKEN` 或 `LINEAR_API_KEY` 环境变量 |
| 评审严格度 | 可选 | 默认全量；超大 PR 仅关键项 |

缺失输入时一次性问齐：「请提供：①PR/MR 编号 ②平台（GitHub/GitLab）③是否需要核验 Jira/Linear 票据（需要则确认对应凭据已注入环境变量）。其余按全量评审执行。」

## 前置自检

```bash
command -v gh glab >/dev/null 2>&1   # 预期：gh 或 glab 至少一个在 PATH；失败：安装对应 CLI 并 STOP
gh auth status >/dev/null 2>&1 || glab auth status >/dev/null 2>&1   # 预期退出码 0；失败：未登录 → 提示 `gh auth login`/`glab auth login`
```

若要验票：确认凭据已注入环境（绝不出现在命令行参数）：

```bash
: "${JIRA_API_TOKEN:?JIRA_API_TOKEN 未设置}"   # 失败：提示用户导出变量再跑，勿粘贴明文 token
: "${LINEAR_API_KEY:?LINEAR_API_KEY 未设置}"
```

## 工作流

### 步骤 1：拉取上下文

```bash
# GitHub
gh pr view <PR_NUMBER> --json title,body,labels,assignees,milestone
gh pr diff <PR_NUMBER> --name-only
gh pr diff <PR_NUMBER> > /tmp/pr-<PR_NUMBER>.diff
gh pr checks <PR_NUMBER>

# GitLab
glab mr view <MR_IID> --output json
glab mr diff <MR_IID> --name-only
glab mr diff <MR_IID> > /tmp/mr-<MR_IID>.diff
```

预期：拿到 PR 标题/正文/标签/改动文件清单与完整 diff。
若失败：编号不存在 → 核对 ID；未认证 → 执行 `gh auth login`/`glab auth login` 后重跑。

### 步骤 2：影响面分析（Blast Radius）

```bash
# 直接依赖方：谁 import 了改动模块
grep -r "from ['\"].*changed-module['\"]" src/ --include="*.ts" -l
grep -r "import changed_module" . --include="*.py" -l
# 跨服务边界
gh pr diff <PR_NUMBER> --name-only | cut -d/ -f1-2 | sort -u
# 共享契约（类型/接口/ schema）
gh pr diff <PR_NUMBER> --name-only | grep -E "types/|interfaces/|schemas/|models/"
```

预期：按严重度归类——CRITICAL（共享库/DB 模型/auth 中间件/API 契约）、HIGH（被 >3 服务依赖）、MEDIUM（单服务内部）、LOW（UI/测试/文档）。
若失败：改动文件无法定位 → 先跑步骤 1 拿 `--name-only`。

### 步骤 3：安全扫描

```bash
DIFF=/tmp/pr-<PR_NUMBER>.diff
grep -n "query\|execute\|raw(" $DIFF | grep -E '\$\{|f"|%s|format\('      # SQL 注入
grep -nE "(password|secret|api_key|token|private_key)\s*=\s*['\"][^'\"]{8,}" $DIFF   # 硬编码密钥
grep -nE "AKIA[0-9A-Z]{16}" $DIFF                                          # AWS key
grep -nE "jwt\.sign\(.*['\"][^'\"]{20,}['\"]" $DIFF                        # JWT 硬编码
grep -n "dangerouslySetInnerHTML\|innerHTML\s*=" $DIFF                     # XSS
grep -nE "md5\(|sha1\(" $DIFF                                              # 弱哈希
grep -nE "\beval\(|\bexec\(" $DIFF                                         # 危险调用
grep -n "__proto__\|constructor\[" $DIFF                                   # 原型污染
grep -nE "path\.join\(.*req\.|readFile\(.*req\." $DIFF                     # 路径穿越
```

预期：列出命中行号与类型；无命中则该维度标记 clean。
若失败：diff 路径错 → 用步骤 1 重新下载到 `/tmp`。

### 步骤 4：测试覆盖 Delta

```bash
CHANGED_SRC=$(gh pr diff <PR_NUMBER> --name-only | grep -vE "\.test\.|\.spec\.|__tests__")
CHANGED_TESTS=$(gh pr diff <PR_NUMBER> --name-only | grep -E "\.test\.|\.spec\.|__tests__")
echo "Source files: $(echo "$CHANGED_SRC" | wc -w)  Test files: $(echo "$CHANGED_TESTS" | wc -w)"
LOGIC_LINES=$(grep "^+" /tmp/pr-<PR_NUMBER>.diff | grep -v "^+++" | wc -l)
```

预期：得出源/测试文件比与新增行数；据此套用规则——新函数无测试→flag；覆盖率下降 >5%→block；auth/支付路径→要求 100% 覆盖。
若失败：无测试文件改动 → 直接 flag 覆盖率缺口。

### 步骤 5：破坏性变更检测

```bash
grep -n "openapi\|swagger" /tmp/pr-<PR_NUMBER>.diff | head -20
grep "^-" /tmp/pr-<PR_NUMBER>.diff | grep -E "router\.(get|post|put|delete|patch)\("
grep "^-" /tmp/pr-<PR_NUMBER>.diff | grep -E "^-\s*(type |field |Query |Mutation )"
gh pr diff <PR_NUMBER> --name-only | grep -E "migrations?/|alembic/|knex/"
grep -E "DROP TABLE|DROP COLUMN|ALTER.*NOT NULL|TRUNCATE" /tmp/pr-<PR_NUMBER>.diff
grep "^+" /tmp/pr-<PR_NUMBER>.diff | grep -oE "process\.env\.[A-Z_]+" | sort -u   # 新增 env 变量
```

预期：列出移除的路由/类型、破坏性 migration、新增 env 变量（可能 prod 缺失）。

### 步骤 6：性能影响

```bash
grep -n "\.find\|\.query\|db\." /tmp/pr-<PR_NUMBER>.diff | grep "^+" | head -20   # N+1 嫌疑
grep "^+" /tmp/pr-<PR_NUMBER>.diff | grep -E '"[a-z@].*":\s*"[0-9^~]' | head -20  # 重依赖
grep -n "while (true" /tmp/pr-<PR_NUMBER>.diff | grep "^+"                         # 死循环
```

预期：标记 N+1、重依赖、未 await、超大内存分配等。

### 步骤 7：票据核验（仅当用户要求）

```bash
TICKET="PROJ-123"
: "${JIRA_API_TOKEN:?JIRA_API_TOKEN 必须设置}"
curl -s -K - "https://your-org.atlassian.net/rest/api/3/issue/$TICKET" <<EOF | \
  jq '{key, summary: .fields.summary, status: .fields.status.name}'
user = "user@company.com:$JIRA_API_TOKEN"
EOF
```

预期：返回票据 key/summary/status；校验其与 PR 范围匹配。
安全红线：token 经 `curl -K -` 从 stdin 注入，**绝不进 argv**（`ps`/`/proc` 不可见、不入 shell 历史）。重复调用优先用 `~/.netrc`（`chmod 600`）+ `curl --netrc`。
若失败：`JIRA_API_TOKEN` 未设 → 提示导出；401 → 令牌失效需轮换。

## 评审检查清单（30+ 项）

按块逐项核对，结果归入交付报告：

- **范围**：标题准确；正文讲 WHY；关联票据存在且匹配；无范围蔓延；破坏性变更已记录
- **影响面**：已定位所有 import 方；跨服务依赖已查；共享类型/接口已审；新增 env 写入 `.env.example`；migration 可回滚（有 down）
- **安全**：无硬编码密钥；SQL 参数化；输入已校验；新端点有权限校验；无 XSS；新依赖查 CVE；日志无敏感数据；上传已校验；CORS 正确
- **测试**：公开函数有单测；边界/错误路径覆盖；API 有集成测试；无无理由删测试；命名清晰
- **破坏性**：API 端点移除有弃用通知；响应无新增必填字段；DB 列移除有两阶段计划；env 移除已评估；对外向后兼容
- **性能**：无 N+1；新查询有索引；无无界循环；无无理由重依赖；await 正确；考虑了缓存
- **质量**：无死代码/未用 import；错误处理非空 catch；符合现有约定；复杂逻辑有注释；无遗留 TODO

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `gh`/`glab` 不在 PATH | CLI 未装 | 安装并重跑自检 |
| `auth status` 非零 | 未登录 | 执行 `gh auth login`/`glab auth login` |
| PR 编号 404 | ID/IID 错或跨平台 | 核对平台与编号 |
| `JIRA_API_TOKEN` 未设 | 凭据缺失 | 提示用户导出环境变量 |
| 覆盖率下降 >5% | 测试不足 | 标记 block，要求补测试 |

## 交付标准

成功定义：产出单轮评审评论，按 `MUST FIX` / `SHOULD FIX` / `SUGGESTIONS` / `LOOKS GOOD` 分级，每项含文件:行号、原因与修复示例。
报告结构：

```text
## PR Review: [PR Title] (#NUMBER)
Blast Radius: HIGH — changes lib/auth used by 5 services
Security: 1 finding (medium severity)
Tests: Coverage delta +2%
Breaking Changes: None detected
--- MUST FIX (Blocking) ---
1. SQL Injection risk in src/db/users.ts:42 ... Fix: db.query("...", [userId])
--- SHOULD FIX (Non-blocking) ---
2. Missing auth check on POST /api/admin/reset ...
--- SUGGESTIONS ---
3. N+1 pattern in src/services/reports.ts:88 ...
--- LOOKS GOOD ---
- Test coverage for new auth flow is thorough
```

保存位置：作为 PR/MR 评论发布（由用户触发），或在会话内输出。
验证完整性：每条 MUST FIX 都对应一处具体改动行且给出可操作修复；无仅风格层面的吹毛求疵（交给 linter）。

## 安全红线

- **凭据只走环境变量**：`JIRA_API_TOKEN`/`LINEAR_API_KEY` 经 `curl -K -`（stdin）或 `~/.netrc` 注入，`ps`/`/proc`/shell 历史均不可见；绝不在命令行写明文 token。
- **只评审不下场**：本技能产出 verdict 与修复建议，不执行 `git push` 或修改代码；落地修复由用户/其他技能完成。
- 外部 URL 视为不可信输入：票据 API 响应先 `jq` 结构化再读，不盲信。

## 参考

- 确定性静态分析（密钥/SQLi/复杂度打分）交由 `code-reviewer` 技能作为分析引擎链式调用。
- 关联票据核验的 curl/JWT 安全写法见上方步骤 7 内联说明。
