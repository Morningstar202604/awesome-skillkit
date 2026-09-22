---
name: issue-tracker-sync
description: "Compose issue-create requests for Jira, Linear, and GitHub Issues from one input, map priorities and statuses across the three models, and render a grouped weekly report. Use when the user asks to 建 issue / 提 bug 单 / 同步任务到 Jira / 生成周报 / 跨平台 issue 同步 / 任务状态汇总 / create Jira ticket / create Linear issue / open GitHub issue / weekly engineering report. Do NOT use for chat notifications (use feishu-dingtalk-bridge), Notion databases (use notion-workspace), or code review comments on pull requests."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only for the helper script. Live execution needs outbound HTTPS to your Jira site, api.linear.app or api.github.com, plus JIRA_TOKEN / LINEAR_API_KEY / GITHUB_TOKEN in environment variables."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Issue Tracker Sync（Jira / Linear / GitHub Issues 协同）

同一件事——"建个 issue"——在三家是三种模型：Jira 是 REST + 嵌套 `fields`
（自定义字段是 `customfield_NNNNN`），Linear 是 GraphQL mutation（一切皆输入
对象、标签要 UUID），GitHub 是扁平 REST（没有优先级字段，用标签模拟）。

**核心判断：状态名不能直接对拷。** 三家都允许自定义工作流，"In Progress" 在
A 站可能是"待评审"的意思。同步前必须先做**语义对齐**，而不是字符串对拷。

**红线（本技能强制）**

1. **凭证绝不硬编码**：只从环境变量读——`JIRA_BASE_URL` / `JIRA_EMAIL` /
   `JIRA_TOKEN` / `LINEAR_API_KEY` / `GITHUB_TOKEN`。脚本从不接受、不打印、
   不落盘任何令牌；请求体里的凭证位置一律写成 `$VAR` 占位。
2. **默认 dry-run**：`build` 只打印"将发送的请求"，**不发请求**。创建 issue
   会在团队看板产生可见副作用（触发通知、计入冲刺），必须用户确认后才发。
3. **最小权限**：Jira 只需 `write:jira-work`（不要 `manage:jira-project`）；
   Linear 用个人 API key 且只授权需要的团队；GitHub PAT 只需 `issues:write`，
   **不要**用 `repo` 全量 scope。
4. **报告只读**：`weekly-report` 只从本地 JSON 渲染 Markdown，不联网、不写远端。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 目标平台 | 是 | `jira` / `linear` / `github`，可多选 |
| 标题 | 建单必填 | 简明动词短语，如"修复 CSV 导出乱码" |
| 正文 | 否 | 复现步骤/验收标准；Jira v3 下需转 ADF |
| 优先级 | 否 | 内部编号 `P0..P4`，默认 `P2`；三家各自映射 |
| 负责人 | 否 | Jira 要 `accountId`；Linear 要 user UUID；GitHub 要 login |
| 标签 | 否 | Jira/ GitHub 用名字；**Linear 要 label UUID** |
| 容器 | 建单必填 | Jira `--project` key / Linear `--team` ID / GitHub `--repo owner/name` |
| issue 列表 JSON | 周报必填 | 三家任一响应体；脚本按平台分支提取字段 |
| 令牌 | 真实执行必填 | 只在环境变量；dry-run 与周报不需要 |

**缺输入时一次性问齐**：

> 请一次提供：① 目标平台；② 标题与正文；③ 优先级（P0..P4，默认 P2）；
> ④ 负责人标识（Jira accountId / Linear user UUID / GitHub login，不知道我就留空）；
> ⑤ 容器（Jira 项目 key / Linear 团队 / GitHub 仓库）。周报另外需要一份
> issue 列表 JSON。默认我只打印请求、不发送。

## 前置自检

```bash
python3 --version                                        # 预期 >= 3.8
test -f scripts/issue_sync.py && echo SCRIPT_OK           # 预期打印 SCRIPT_OK
# 凭证检查：只判断存在性，绝不回显
for v in JIRA_BASE_URL JIRA_TOKEN LINEAR_API_KEY GITHUB_TOKEN; do
  printf '%s: ' "$v"; test -n "$(printenv $v)" && echo present || echo missing
done
test -n "$GITHUB_TOKEN" || gh auth status 2>/dev/null && echo "gh-cli available"
# 自检：python3 scripts/issue_sync.py field-map 应打印三家字段对照表
```

| 结果 | 判读 |
|---|---|
| 某平台 `missing` | 只影响真实发送；构造请求照常，先出负载 |
| 全部 missing | 仍可完成周报（纯离线）与字段映射核对 |
| `FIELD_MAP_OK` 缺失 | 脚本缺失或语法损坏，退化为照下方映射表手工拼 |

## 跨平台状态映射表

**语义对齐，不是字符串对齐。** 下表左边是本技能的规范语义，右边是各平台
的等价落点；同步时**以语义为准**，落地形态由目标平台决定。

| 规范语义 | Jira status | Linear state | GitHub（无工作流） |
|---|---|---|---|
| 待办 | To Do | Backlog / Todo | `open`，无状态标签 |
| 进行中 | In Progress | In Progress | `open` + `status:in-progress` |
| 待评审 | In Review | In Review | `open` + `status:in-review` |
| 阻塞 | Blocked | Blocked | `open` + `status:blocked` |
| 已完成 | Done | Done | `closed`（completed） |
| 已取消 | Won't Do | Canceled | `closed`（not planned） |

**优先级映射**：`P0→Highest/1/priority:critical`、`P1→High/2/priority:high`、
`P2→Medium/3/priority:medium`、`P3→Low/4/priority:low`、`P4→Lowest/0/priority:backlog`。
注意 Linear 的优先级是**整数**且 `0 = No priority`（不是最低，是"未设"）。

## 工作流

### 步骤 1：核对目标平台的工作流与字段

```bash
python3 scripts/issue_sync.py field-map        # 三家字段/状态/优先级对照
```

Jira 站点若有自定义状态或中文优先级名，**必须先查真实值**：

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_TOKEN" "$JIRA_BASE_URL/rest/api/2/field" | head -40
```

预期：拿到本实例的字段 ID 与优先级枚举名。
若失败：映射不上就**停下来问用户**，猜错会把"高优"退化成"中优"，无人察觉。

### 步骤 2：构造建单请求（dry-run）

```bash
# python3 scripts/issue_sync.py build --tracker jira \
#   --title "修复 CSV 导出乱码" --body "导出时中文乱码" --priority P1 \
#   --project ENG --labels "bug,导出" --assignee <accountId>

# python3 scripts/issue_sync.py build --tracker linear \
#   --title "修复 CSV 导出乱码" --priority P1 --team <teamUUID> \
#   --labels "<labelUUID>,<labelUUID>"

# python3 scripts/issue_sync.py build --tracker github \
#   --title "修复 CSV 导出乱码" --priority P1 --repo owner/name \
#   --labels bug --assignee octocat
```

预期：打印完整的 method/url/headers/body，凭证位置全是 `$VAR` 占位。
注意三家的结构差异：Jira 是 `body.fields.*`、Linear 是 `body.variables.input.*`、
GitHub 是 `body.*` 扁平。

若失败：`必须提供 --project/--team/--repo` → 容器参数缺失；
`未知优先级` → 只能用 `P0..P4`。

### 步骤 3：发送

```bash
curl -sS -X POST "$JIRA_BASE_URL/rest/api/2/issue" \
  -H "Authorization: Basic $(printf '%s:%s' "$JIRA_EMAIL" "$JIRA_TOKEN" | base64)" \
  -H 'Content-Type: application/json' --data @payload.json

curl -sS -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H 'Content-Type: application/json' --data @payload.json

curl -sS -X POST https://api.github.com/repos/owner/name/issues \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H 'Accept: application/vnd.github+json' \
  -H 'X-GitHub-Api-Version: 2022-11-28' --data @payload.json
```

**发送前把 payload 给用户过目**：建单会通知关注者、计入冲刺，是可见副作用。

预期：Jira 返回 `key` 如 `ENG-123`；Linear 返回 `issue.identifier`；
GitHub 返回 `number`。**记录这三者的对应关系**——这是后续同步的锚点。

若失败：Jira `400` 多为字段名/枚举值不匹配；Linear GraphQL 错误在
`errors[]` 里而 HTTP 仍是 200；GitHub `422` 多为标签不存在或负责人无权限。

### 步骤 4：生成周报

```bash
# 先拉一份 issue 列表存成 JSON（三家任一形态）
python3 scripts/issue_sync.py weekly-report \
  --json issues.json --tracker github --week 2026-W38 --output report.md
```

预期：按状态分组（进行中/阻塞/待办/已完成/已取消），**阻塞项用引用块高亮**放
在报告顶部，每组一张表含 ID/标题/状态/负责人/优先级。

若失败：`检查是否用了错误的响应包装层级` → 三家包装不同
（Jira `issues` / Linear `data.issues.nodes` / GitHub 裸数组），脚本会自动尝试，
仍失败时手工取到数组层再传。

### 步骤 5：跨平台同步锚定

同一件事在多家都有单时，**必须建立 ID 映射台账**（`ENG-123 ↔ ENG-123 ↔ #101`
外加各平台 URL），写进 issue 正文或独立 CSV。

预期：台账每个 issue 一行，含三家 ID 与状态。
若失败：无台账时**不要自动对拷状态**——只能靠标题模糊匹配，误伤率极高；
此时应该报告"无法对齐"而不是猜。

## 交付标准

- **成功定义**：目标平台返回新 issue 的 ID（Jira `key` / Linear `identifier` /
  GitHub `number`），且状态与优先级经 `weekly-report` 复查落在预期分组。
- **产物**：每平台 `payload.json`、`response.json`、ID 映射台账、
  周报 `report.md`。
- **完整性验证**：
  - 周报分组计数之和 == issue 总数（脚本首行已打印，直接核对）；
  - 建单后用返回 ID 再 GET 一次，确认 priority 与 assignee 未被平台默认值覆盖；
  - 产物中不得出现令牌明文：`grep -lE 'eyJ|ATATT|ghp_' *.json` 应无命中。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| Jira `400 field 'priority' cannot be set` | 站点优先级是中文名或自定义枚举，`High` 不存在 | 先查 `/rest/api/2/field` 拿到真实枚举名，再替换 `priority.name` |
| Jira 自定义字段写不进去 | 用了语义名（如 `故事点`）而非 `customfield_NNNNN` | 查 `/rest/api/2/field` 找到数字 ID；值还要传 option 的 `id` 而非显示名 |
| Jira `400` 提示 assignee 无效 | Cloud 版要 `accountId`，不是邮箱或用户名 | 用 `/rest/api/3/user/search?query=` 查 accountId |
| Linear 返回 200 但实际失败 | GraphQL 的错误在 `errors[]` 里，HTTP 码不反映业务失败 | 必须读响应体 `errors` 与 `data.issueCreate.success` 两个字段 |
| Linear 标签设置无效 | `labelIds` 要 UUID，传了标签名字符串 | 先查 `labels` 拿 ID；或改用 `labelIds` 为空后续手工挂 |
| GitHub 建单后没有优先级 | Issues 没有 priority 字段 | 用标签模拟（本脚本自动追加 `priority:high` 之类）；标签不存在时需先建标签 |
| GitHub `422 Validation Failed` | 标签不存在、负责人无仓库权限 | 先 `POST /repos/{o}/{r}/labels` 建标签；确认 assignee 已协作者 |
| 同步后状态语义错乱 | 直接对拷状态名字符串（各站自定义工作流不同） | 用本文档的语义映射表；拿不准时报告"需人工确认"而非自行映射 |
| 周报某些 issue 缺负责人 | 字段路径读错（如 Jira 读了 `reporter`） | `_extract_issue` 按平台分支提取，勿改成通用猜测；核对原始 JSON 键名 |
| 周报把"取消"算成"完成" | GitHub 的 `closed` 同时覆盖 completed 与 not planned | 靠标签区分（`wontfix`/`invalid` → 已取消）；否则需读 `state_reason` |

## 参考

- `scripts/issue_sync.py` —— `build`（三家请求构造）/ `field-map`（含 `--json`
  供程序消费）/ `weekly-report`（离线渲染）
- `references/sources-and-methodology.md` —— 为何用语义对齐而非字符串对拷、
  GraphQL 与 REST 的错误判定差异、周报分组的取舍
