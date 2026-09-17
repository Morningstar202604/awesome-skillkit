#!/usr/bin/env python3
"""issue_sync.py -- Jira / Linear / GitHub Issues 的请求构造与周报生成器。

三家把"建一个 issue"映射成了三套模型：
Jira 用 REST + 嵌套 fields（自定义字段是 customfield_NNNNN 而非字段名），
Linear 用 GraphQL mutation（一切皆输入对象），
GitHub 用 REST + 扁平的 labels/assignees 数组。本脚本把差异收敛成三个子命令。

设计原则
--------
1. **纯函数**：只构造请求体与渲染报告，绝不发 HTTP；无需凭证即可完整测试。
2. **默认 dry-run**：`build` 只打印将发送的请求，发送由人确认后执行。
3. **凭证不落盘**：token 一律从环境变量读取（JIRA_TOKEN / LINEAR_API_KEY /
   GITHUB_TOKEN），脚本内部从不接受、不打印、不落盘。
4. **报告只读**：`weekly-report` 从本地 JSON 生成 Markdown，不联网、不写远端。

子命令
------
  build         --tracker {jira|linear|github} --title X [--body Y] [--priority P]
                [--assignee A] [--labels a,b] [--project P] [--team T] [--repo R]
  field-map     [--json]          打印三家字段/状态映射对照表
  weekly-report --json file.json [--week YYYY-WNN] [--output out.md]

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# 平台常量
# ---------------------------------------------------------------------------

# Jira Cloud 的 REST 版本。v3 用 Atlassian Document Format(ADF) 表示富文本，
# v2 接受纯字符串——本脚本默认 v2 形态（body 为字符串），更易读也更好迁移。
JIRA_API_VERSION = "2"

# Jira 优先级是站点级枚举，名字随站点语言变（中文站点可能是"高"）。
# 这里给的是默认英文实例的取值，跨站点使用前必须先用 field-map 核对。
JIRA_PRIORITIES = {"P0": "Highest", "P1": "High", "P2": "Medium",
                   "P3": "Low", "P4": "Lowest"}

# Linear 的优先级是 **整数枚举**，不是字符串。0 = No priority。
LINEAR_PRIORITIES = {"P0": 1, "P1": 2, "P2": 3, "P3": 4, "P4": 0}

# GitHub Issues 的 REST 端点没有优先级字段，约定用标签模拟。
GITHUB_PRIORITY_LABELS = {"P0": "priority:critical", "P1": "priority:high",
                          "P2": "priority:medium", "P3": "priority:low",
                          "P4": "priority:backlog"}

# 三家令牌/仓库的环境变量名（脚本只引用名字，不读取值）。
ENV_HINTS = {
    "jira": "JIRA_BASE_URL / JIRA_EMAIL / JIRA_TOKEN",
    "linear": "LINEAR_API_KEY",
    "github": "GITHUB_TOKEN（或用已登录的 gh CLI）",
}

# Jira 的自定义字段 ID 不固定，必须用 GET /rest/api/2/field 查出后回填。
# 这里给出的是最常需要映射的字段语义 -> 查询方式说明。
JIRA_CUSTOM_FIELDS = {
    "故事点": "customfield_10016 之类的数字 ID，随站点实例不同，必须查询后确认",
    "Epic Link": "customfield_10014 之类的数字 ID，同样随实例不同",
    "严重程度": "自定义 select 字段，值为 option 的 id 而非显示名",
}


class BuildError(Exception):
    """负载构造失败（输入不合法，非网络问题）。"""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    p = Path(path)
    if not p.is_file():
        raise BuildError(f"{what} 文件不存在: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"{what} 不是合法 JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _priority_key(raw: str) -> str:
    """把用户输入的优先级归一到大写 P 编号。"""
    key = (raw or "P2").strip().upper()
    if key.isdigit():
        key = f"P{key}"
    if key not in JIRA_PRIORITIES:
        raise BuildError(
            f"未知优先级 '{raw}'；用 P0..P4（P0 最高）。"
            "注意：三家对优先级的存储方式不同（Jira 字符串名 / Linear 整数 / GitHub 标签）"
        )
    return key


# ---------------------------------------------------------------------------
# build：三家各一套
# ---------------------------------------------------------------------------
def build_jira(title: str, body: str, priority: str, assignee: str,
               labels: list, project: str, _team: str, _repo: str) -> dict:
    """Jira：POST /rest/api/{ver}/issue，一切塞进嵌套的 `fields`。

    三个易错点：
      1. 描述用 `description`，v2 收字符串、v3 收 ADF 对象；
      2. 经办人是 `assignee.accountId`（不是 name/email，Cloud 版用 accountId）；
      3. 标签是 `labels` 数组，**带上就是覆盖**，不是追加。
    """
    if not project:
        raise BuildError("Jira 必须提供 --project（项目 key，如 ENG）")

    fields: dict = {
        "project": {"key": project},
        "summary": title,
        "issuetype": {"name": "Task"},
        "priority": {"name": JIRA_PRIORITIES[priority]},
    }
    if body:
        fields["description"] = body
    if labels:
        fields["labels"] = labels
    if assignee:
        fields["assignee"] = {"accountId": assignee}

    return {
        "method": "POST",
        "url": f"{{base_url}}/rest/api/{JIRA_API_VERSION}/issue",
        "headers": {
            "Authorization": "Basic base64($JIRA_EMAIL:$JIRA_TOKEN)",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "body": {"fields": fields},
    }


def build_linear(title: str, body: str, priority: str, assignee: str,
                 labels: list, _project: str, team: str, _repo: str) -> dict:
    """Linear：GraphQL mutation `issueCreate`。

    与 REST 的差别：所有参数都是**命名输入对象**，且返回字段必须显式声明。
    `teamId` 是必填的团队 UUID，不是团队名——团队名要先查一次拿 ID。
    """
    if not team:
        raise BuildError("Linear 必须提供 --team（团队 ID/UUID；名字需先查 ID）")

    input_obj: dict = {
        "teamId": team,
        "title": title,
        "priority": LINEAR_PRIORITIES[priority],
    }
    if body:
        input_obj["description"] = body
    if assignee:
        input_obj["assigneeId"] = assignee
    if labels:
        # Linear 的标签是 labelId 数组（UUID），不是标签名字符串
        input_obj["labelIds"] = labels

    query = (
        "mutation IssueCreate($input: IssueCreateInput!) {"
        " issueCreate(input: $input) { success issue { id identifier url } } }"
    )
    return {
        "method": "POST",
        "url": "https://api.linear.app/graphql",
        "headers": {
            "Authorization": "$LINEAR_API_KEY",
            "Content-Type": "application/json",
        },
        "body": {
            "query": query,
            "variables": {"input": input_obj},
        },
    }


def build_github(title: str, body: str, priority: str, assignee: str,
                 labels: list, _project: str, _team: str, repo: str) -> dict:
    """GitHub：POST /repos/{owner}/{repo}/issues。

    字段最扁平：`labels`/`assignees` 是字符串数组。
    没有优先级字段——用标签模拟（见 GITHUB_PRIORITY_LABELS）。
    `milestone` 要传 **number**（整数）而非标题字符串；本项目用标签代替里程碑。
    """
    if not repo or "/" not in repo:
        raise BuildError("GitHub 必须提供 --repo owner/name")

    payload: dict = {"title": title}
    if body:
        payload["body"] = body
    all_labels = list(labels)
    prio_label = GITHUB_PRIORITY_LABELS[priority]
    if prio_label not in all_labels:
        all_labels.append(prio_label)
    if all_labels:
        payload["labels"] = all_labels
    if assignee:
        payload["assignees"] = [assignee]

    return {
        "method": "POST",
        "url": f"https://api.github.com/repos/{repo}/issues",
        "headers": {
            "Authorization": "Bearer $GITHUB_TOKEN",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        "body": payload,
    }


BUILDERS = {"jira": build_jira, "linear": build_linear, "github": build_github}


def cmd_build(args) -> int:
    priority = _priority_key(args.priority)
    labels = [x.strip() for x in (args.labels or "").split(",") if x.strip()]
    req = BUILDERS[args.tracker](
        args.title, args.body or "", priority, args.assignee or "",
        labels, args.project or "", args.team or "", args.repo or "")

    print(f"# DRY-RUN：{args.tracker} issue 创建请求（未发送任何请求）")
    print(f"# 凭证：从环境变量 {ENV_HINTS[args.tracker]} 读取，不落盘、不打印")
    print(f"# 优先级：{args.priority or 'P2'} -> {priority}")
    print()
    _dump(req)
    print()
    print("# 未发送任何请求。接上真实凭证后由 AI/用户执行，例如：")
    method, url = req["method"], req["url"].replace("{base_url}", "$JIRA_BASE_URL")
    print(f"#   curl -sS -X {method} \"{url}\" \\")
    print("#     -H 'Content-Type: application/json' --data @payload.json")
    return 0


# ---------------------------------------------------------------------------
# field-map：三家字段/状态对照
# ---------------------------------------------------------------------------
# 状态映射是**语义对齐**而非字符串对齐：三家的状态机模型不同，
# 且每一家都允许自定义，所以这里给的是"等价语义"而非"固定值"。
STATUS_MAP = [
    ("待办", "To Do", "Backlog / Todo", "open（无 label）"),
    ("进行中", "In Progress", "In Progress", "open + label `status:in-progress`"),
    ("待评审", "In Review", "In Review", "open + label `status:in-review`"),
    ("阻塞", "Blocked", "Blocked", "open + label `status:blocked`"),
    ("已完成", "Done", "Done", "closed（completed）"),
    ("已取消", "Won't Do", "Canceled", "closed（not planned）"),
]

FIELD_MAP = [
    ("标题", "fields.summary", "input.title", "title"),
    ("描述", "fields.description（v2 字符串 / v3 ADF）", "input.description",
     "body"),
    ("优先级", "fields.priority.name（站点枚举，随语言变）",
     "input.priority（整数 0-4）", "无此字段 → 用标签模拟"),
    ("负责人", "fields.assignee.accountId", "input.assigneeId（UUID）",
     "assignees[]（login 字符串）"),
    ("标签", "fields.labels[]（覆盖非追加）", "input.labelIds[]（UUID）",
     "labels[]（名字符串，自动建标签）"),
    ("所属容器", "fields.project.key", "input.teamId（UUID）", "URL 里的 owner/repo"),
    ("类型", "fields.issuetype.name", "无独立字段（用 label 区分）",
     "无独立字段（用 label 或 issue type API）"),
    ("唯一标识", "issue.key（如 ENG-123）", "identifier（如 ENG-123）", "#123"),
    ("状态查询", "GET /issue/{key}", "issue(id:) 或 filter", "GET /issues/{number}"),
]


def cmd_field_map(args) -> int:
    if args.json:
        _dump({
            "priority": {"jira": JIRA_PRIORITIES, "linear": LINEAR_PRIORITIES,
                         "github": GITHUB_PRIORITY_LABELS},
            "status": [
                {"语义": s, "jira": j, "linear": l, "github": g}
                for s, j, l, g in STATUS_MAP
            ],
            "fields": [
                {"语义": s, "jira": j, "linear": l, "github": g}
                for s, j, l, g in FIELD_MAP
            ],
            "jira_custom_fields": JIRA_CUSTOM_FIELDS,
        })
        return 0

    print("# 跨平台优先级映射")
    print()
    print("| 内部编号 | Jira priority.name | Linear priority | GitHub 标签 |")
    print("|---|---|---|---|")
    for k in ("P0", "P1", "P2", "P3", "P4"):
        print(f"| {k} | {JIRA_PRIORITIES[k]} | {LINEAR_PRIORITIES[k]} "
              f"| `{GITHUB_PRIORITY_LABELS[k]}` |")
    print()

    print("# 跨平台状态映射（语义对齐，非固定字符串）")
    print()
    print("| 语义 | Jira status | Linear state | GitHub |")
    print("|---|---|---|---|")
    for row in STATUS_MAP:
        print("| " + " | ".join(row) + " |")
    print()

    print("# 字段位置对照")
    print()
    print("| 语义 | Jira（REST fields） | Linear（GraphQL input） | GitHub（REST body） |")
    print("|---|---|---|---|")
    for row in FIELD_MAP:
        print("| " + " | ".join(row) + " |")
    print()
    print("# Jira 自定义字段（ID 随实例不同，必须查 /rest/api/2/field 确认）")
    for k, v in JIRA_CUSTOM_FIELDS.items():
        print(f"- {k}: {v}")
    return 0


# ---------------------------------------------------------------------------
# weekly-report
# ---------------------------------------------------------------------------
# 判定"完成"的等价状态集：三家各自的终态写法。
DONE_STATES = {"done", "closed", "completed", "已解决", "已完成", "resolved"}
CANCELED_STATES = {"canceled", "cancelled", "won't do", "wont do", "已取消",
                   "rejected"}
BLOCKED_STATES = {"blocked", "阻塞", "on hold"}
IN_PROGRESS_STATES = {"in progress", "in review", "进行中", "待评审", "started"}


def _norm_state(raw: str) -> str:
    return (raw or "").strip().lower()


def classify(state: str) -> str:
    """把一个平台的状态字符串归到 5 个报告分组之一。"""
    s = _norm_state(state)
    if s in CANCELED_STATES:
        return "已取消"
    if s in DONE_STATES:
        return "已完成"
    if s in BLOCKED_STATES:
        return "阻塞"
    if s in IN_PROGRESS_STATES:
        return "进行中"
    return "待办"


def _extract_issue(item: dict, tracker: str) -> dict:
    """把三家的 issue 对象归一成 (id, title, state, assignee, priority, blocked, url)。

    三家的字段路径不同，这里按平台分支提取——**不做通用猜测**，
    猜错会把"负责人"读成"报告人"这类不易察觉的错误带进周报。
    """
    if tracker == "jira":
        f = item.get("fields") or {}
        assignee = (f.get("assignee") or {}).get("displayName", "")
        prio = (f.get("priority") or {}).get("name", "")
        labels = f.get("labels") or []
        status = (f.get("status") or {}).get("name", "")
        # Jira 阻塞常用自定义字段或 fixVersion 标记，这里看不出来；
        # 用 labels 里的 blocked 标记作为信号。
        blocked = any("block" in str(l).lower() for l in labels)
        return {
            "id": item.get("key", ""),
            "title": f.get("summary", ""),
            "state": status,
            "assignee": assignee,
            "priority": prio,
            "blocked": blocked,
            "url": "",
        }
    if tracker == "linear":
        state = (item.get("state") or {}).get("name", "")
        assignee = (item.get("assignee") or {}).get("name", "")
        prio_num = item.get("priority")
        # Linear 优先级是整数：0 表示 No priority，1 最高
        rev = {v: k for k, v in LINEAR_PRIORITIES.items()}
        prio = rev.get(prio_num, str(prio_num))
        labels = [l.get("name", "") for l in (item.get("labels") or [])]
        blocked = any("block" in str(l).lower() for l in labels)
        return {
            "id": item.get("identifier", ""),
            "title": item.get("title", ""),
            "state": state,
            "assignee": assignee,
            "priority": prio,
            "blocked": blocked,
            "url": item.get("url", ""),
        }
    # github
    state_raw = item.get("state", "")
    labels = [l.get("name", "") if isinstance(l, dict) else str(l)
              for l in (item.get("labels") or [])]
    blocked = any("block" in str(l).lower() for l in labels)
    assignee = ", ".join(
        (a.get("login", "") if isinstance(a, dict) else str(a))
        for a in (item.get("assignees") or []))
    # GitHub 的状态是 open/closed 二值，细分语义只能从标签读
    if _norm_state(state_raw) == "closed":
        if any("wontfix" in l.lower() or "invalid" in l.lower() for l in labels):
            state = "Canceled"
        else:
            state = "Done"
    else:
        state = "open"
        for l in labels:
            low = l.lower()
            if "in-progress" in low or "in progress" in low:
                state = "In Progress"
                break
            if "in-review" in low:
                state = "In Review"
                break
            if "blocked" in low:
                state = "Blocked"
                break
    return {
        "id": f"#{item.get('number', '')}",
        "title": item.get("title", ""),
        "state": state,
        "assignee": assignee,
        "priority": "",
        "blocked": blocked or _norm_state(state) == "blocked",
        "url": item.get("html_url", ""),
    }


def _week_range(week: str | None) -> tuple:
    """把 YYYY-WNN 转成 (说明文本, 起始日期, 结束日期)。ISO 周从周一起算。"""
    if not week:
        today = date.today()
        iso = today.isocalendar()
        week = f"{iso[0]}-W{iso[1]:02d}"
    try:
        year_s, week_s = week.upper().split("-W")
        year, wk = int(year_s), int(week_s)
        start = date.fromisocalendar(year, wk, 1)  # 1 = Monday
    except (ValueError, AttributeError) as e:
        raise BuildError(f"周编号 '{week}' 不合法，应为 YYYY-WNN（如 2026-W38）：{e}")
    return f"{year}-W{wk:02d}", start, start + timedelta(days=6)


def render_report(items: list, tracker: str, week_label: str,
                  start: date, end: date) -> str:
    """把归一后的 issue 列表渲染成 Markdown 周报。"""
    groups = defaultdict(list)
    for it in items:
        groups[classify(it["state"])].append(it)

    lines = [
        f"# 周报 {week_label}（{start.isoformat()} ~ {end.isoformat()}）",
        "",
        f"- 数据源：{tracker}",
        f"- issue 总数：{len(items)}",
        "- 分组统计：" + " · ".join(
            f"{g} {len(groups[g])}" for g in
            ("进行中", "阻塞", "待办", "已完成", "已取消") if groups.get(g)
        ),
        "",
    ]

    blocked = groups.get("阻塞", [])
    if blocked:
        lines += ["> [!WARNING]", f"> **阻塞项 {len(blocked)} 个，需优先处理：**",
                  ">"]
        for it in blocked:
            who = it["assignee"] or "未指派"
            lines.append(f"> - `{it['id']}` {it['title']}（负责人：{who}）")
        lines.append("")

    for group in ("进行中", "阻塞", "待办", "已完成", "已取消"):
        bucket = groups.get(group)
        if not bucket:
            continue
        lines += [f"## {group}（{len(bucket)}）", ""]
        lines.append("| ID | 标题 | 状态 | 负责人 | 优先级 |")
        lines.append("|---|---|---|---|---|")
        for it in bucket:
            title = it["title"].replace("|", "\\|")
            lines.append(
                f"| `{it['id']}` | {title} | {it['state']} | "
                f"{it['assignee'] or '未指派'} | {it['priority'] or '—'} |")
        lines.append("")

    if not items:
        lines += ["（本周无 issue 记录。）", ""]
    return "\n".join(lines).rstrip() + "\n"


def cmd_weekly_report(args) -> int:
    raw = _load_json(args.json, "--json")
    if isinstance(raw, dict):
        # 兼容三家各自的响应包装：Jira search / Linear GraphQL / GitHub REST
        items = (raw.get("issues")
                 or (raw.get("data") or {}).get("issues", {}).get("nodes")
                 or raw.get("results")
                 or [])
    elif isinstance(raw, list):
        items = raw
    else:
        return _die("--json 必须是 issue 数组或含 issues/results 的响应对象")

    if not items:
        return _die("--json 里没有 issue 记录（检查是否用了错误的响应包装层级）")

    normalized = [_extract_issue(it, args.tracker) for it in items]
    week_label, start, end = _week_range(args.week)
    report = render_report(normalized, args.tracker, week_label, start, end)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"# 已写入 {args.output}（{len(normalized)} 条 issue）")
    else:
        sys.stdout.write(report)
        print(f"# 统计：{len(normalized)} 条 issue（{args.tracker}）")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="issue_sync.py",
        description="Jira / Linear / GitHub Issues 请求构造与周报生成（离线，不发请求）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build", help="构造 issue 创建请求并打印")
    s.add_argument("--tracker", choices=["jira", "linear", "github"], required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--body", default="")
    s.add_argument("--priority", default="P2", help="P0..P4，默认 P2")
    s.add_argument("--assignee", default="")
    s.add_argument("--labels", default="", help="逗号分隔")
    s.add_argument("--project", default="", help="Jira 项目 key")
    s.add_argument("--team", default="", help="Linear 团队 ID")
    s.add_argument("--repo", default="", help="GitHub owner/name")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("field-map", help="打印三家字段/状态映射表")
    s.add_argument("--json", action="store_true", help="以 JSON 输出（便于程序消费）")
    s.set_defaults(func=cmd_field_map)

    s = sub.add_parser("weekly-report", help="从 issue 列表生成周报 Markdown")
    s.add_argument("--json", required=True)
    s.add_argument("--tracker", choices=["jira", "linear", "github"], default="github")
    s.add_argument("--week", help="YYYY-WNN，默认本周")
    s.add_argument("--output", help="输出文件；缺省打印到 stdout")
    s.set_defaults(func=cmd_weekly_report)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BuildError as e:
        return _die(str(e))


if __name__ == "__main__":
    sys.exit(main())
