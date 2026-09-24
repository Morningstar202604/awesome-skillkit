#!/usr/bin/env python3
"""issue_sync.py -- request builder and weekly-report generator for Jira / Linear /
GitHub Issues.

The three platforms map "create an issue" into three different models: Jira uses
REST + nested fields (custom fields are customfield_NNNNN, not field names), Linear
uses GraphQL mutations (everything is an input object), and GitHub uses REST + flat
labels/assignees arrays. This script converges the differences into three subcommands.

Design principles
-----------------
1. **Pure functions**: only builds request bodies and renders reports; never sends
   HTTP; fully testable without credentials.
2. **Dry-run by default**: `build` only prints the request that would be sent;
   sending happens after a human confirms.
3. **Credentials never hit disk**: tokens are always read from environment vars
   (JIRA_TOKEN / LINEAR_API_KEY / GITHUB_TOKEN); the script never accepts, prints,
   or stores them.
4. **Reports are read-only**: `weekly-report` builds Markdown from local JSON, with
   no network and no remote writes.

Subcommands
-----------
  build         --tracker {jira|linear|github} --title X [--body Y] [--priority P]
                [--assignee A] [--labels a,b] [--project P] [--team T] [--repo R]
  field-map     [--json]          print the three-way field/status mapping table
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
# Platform constants
# ---------------------------------------------------------------------------

# Jira Cloud REST version. v3 uses Atlassian Document Format (ADF) for rich text;
# v2 accepts plain strings -- this script defaults to the v2 shape (body as a
# string), which is easier to read and migrate.
JIRA_API_VERSION = "2"

# Jira priorities are site-level enums whose names change with the site language
# (a Chinese-language site may show "High" as localized text). The values here are
# for a default English instance; verify with field-map before using across sites.
JIRA_PRIORITIES = {"P0": "Highest", "P1": "High", "P2": "Medium",
                   "P3": "Low", "P4": "Lowest"}

# Linear priorities are **integer enums**, not strings. 0 = No priority.
LINEAR_PRIORITIES = {"P0": 1, "P1": 2, "P2": 3, "P3": 4, "P4": 0}

# GitHub Issues' REST endpoint has no priority field; convention simulates it with labels.
GITHUB_PRIORITY_LABELS = {"P0": "priority:critical", "P1": "priority:high",
                          "P2": "priority:medium", "P3": "priority:low",
                          "P4": "priority:backlog"}

# Env-var names for the three tokens/repos (the script references names, never reads values).
ENV_HINTS = {
    "jira": "JIRA_BASE_URL / JIRA_EMAIL / JIRA_TOKEN",
    "linear": "LINEAR_API_KEY",
    "github": "GITHUB_TOKEN (or use the logged-in gh CLI)",
}

# Jira custom field IDs are not fixed; you must query GET /rest/api/2/field and
# fill them in. Below: the field semantics most often needing mapping -> how to query.
JIRA_CUSTOM_FIELDS = {
    "Story points": "a numeric ID like customfield_10016, which varies by site instance; must confirm after querying",
    "Epic Link": "a numeric ID like customfield_10014, likewise instance-specific",
    "Severity": "a custom select field whose value is the option id, not the display name",
}


class BuildError(Exception):
    """Payload construction failed (bad input, not a network problem)."""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    p = Path(path)
    if not p.is_file():
        raise BuildError(f"{what} file does not exist: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"{what} is not valid JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _priority_key(raw: str) -> str:
    """Normalize the user's priority input to an uppercase P-code."""
    key = (raw or "P2").strip().upper()
    if key.isdigit():
        key = f"P{key}"
    if key not in JIRA_PRIORITIES:
        raise BuildError(
            f"unknown priority '{raw}'; use P0..P4 (P0 highest). "
            "Note: the three store priority differently (Jira string name / Linear int / GitHub label)"
        )
    return key


# ---------------------------------------------------------------------------
# build: one per platform
# ---------------------------------------------------------------------------
def build_jira(title: str, body: str, priority: str, assignee: str,
               labels: list, project: str, _team: str, _repo: str) -> dict:
    """Jira: POST /rest/api/{ver}/issue, everything nested under `fields`.

    Three common pitfalls:
      1. the description goes in `description`: v2 takes a string, v3 takes an ADF object;
      2. the assignee is `assignee.accountId` (not name/email; Cloud uses accountId);
      3. labels are a `labels` array -- **including them overwrites**, it does not append.
    """
    if not project:
        raise BuildError("Jira requires --project (the project key, e.g. ENG)")

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
    """Linear: GraphQL mutation `issueCreate`.

    Difference from REST: all parameters are **named input objects**, and the
    returned fields must be declared explicitly. `teamId` is the required team UUID,
    not the team name -- look up the name to get the ID first.
    """
    if not team:
        raise BuildError("Linear requires --team (team ID/UUID; look up the name to get the ID)")

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
        # Linear labels are a labelId array (UUIDs), not label-name strings
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
    """GitHub: POST /repos/{owner}/{repo}/issues.

    The flattest fields: `labels`/`assignees` are string arrays. There is no priority
    field -- simulated with a label (see GITHUB_PRIORITY_LABELS). `milestone` takes a
    **number** (integer), not a title string; this project uses labels instead of milestones.
    """
    if not repo or "/" not in repo:
        raise BuildError("GitHub requires --repo owner/name")

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

    print(f"# DRY-RUN: {args.tracker} issue-create request (no request sent)")
    print(f"# credentials: read from env var {ENV_HINTS[args.tracker]}; not written to disk, not printed")
    print(f"# priority: {args.priority or 'P2'} -> {priority}")
    print()
    _dump(req)
    print()
    print("# No request sent. With real credentials attached, the AI/user runs it, e.g.:")
    method, url = req["method"], req["url"].replace("{base_url}", "$JIRA_BASE_URL")
    print(f"#   curl -sS -X {method} \"{url}\" \\")
    print("#     -H 'Content-Type: application/json' --data @payload.json")
    return 0


# ---------------------------------------------------------------------------
# field-map: three-way field/status mapping
# ---------------------------------------------------------------------------
# Status mapping is **semantic alignment**, not string alignment: the three have
# different state-machine models and each allows customization, so these are
# "equivalent semantics" rather than "fixed values".
STATUS_MAP = [
    ("To Do", "To Do", "Backlog / Todo", "open (no label)"),
    ("In Progress", "In Progress", "In Progress", "open + label `status:in-progress`"),
    ("In Review", "In Review", "In Review", "open + label `status:in-review`"),
    ("Blocked", "Blocked", "Blocked", "open + label `status:blocked`"),
    ("Done", "Done", "Done", "closed (completed)"),
    ("Canceled", "Won't Do", "Canceled", "closed (not planned)"),
]

FIELD_MAP = [
    ("Title", "fields.summary", "input.title", "title"),
    ("Description", "fields.description (v2 string / v3 ADF)", "input.description",
     "body"),
    ("Priority", "fields.priority.name (site enum, changes with language)",
     "input.priority (int 0-4)", "no such field -> simulated with a label"),
    ("Assignee", "fields.assignee.accountId", "input.assigneeId (UUID)",
     "assignees[] (login string)"),
    ("Labels", "fields.labels[] (overwrite, not append)", "input.labelIds[] (UUID)",
     "labels[] (name strings; auto-creates labels)"),
    ("Container", "fields.project.key", "input.teamId (UUID)", "owner/repo in the URL"),
    ("Type", "fields.issuetype.name", "no separate field (use a label)",
     "no separate field (use a label or the issue-type API)"),
    ("Identifier", "issue.key (e.g. ENG-123)", "identifier (e.g. ENG-123)", "#123"),
    ("State query", "GET /issue/{key}", "issue(id:) or filter", "GET /issues/{number}"),
]


def cmd_field_map(args) -> int:
    if args.json:
        _dump({
            "priority": {"jira": JIRA_PRIORITIES, "linear": LINEAR_PRIORITIES,
                         "github": GITHUB_PRIORITY_LABELS},
            "status": [
                {"semantic": s, "jira": j, "linear": l, "github": g}
                for s, j, l, g in STATUS_MAP
            ],
            "fields": [
                {"semantic": s, "jira": j, "linear": l, "github": g}
                for s, j, l, g in FIELD_MAP
            ],
            "jira_custom_fields": JIRA_CUSTOM_FIELDS,
        })
        return 0

    print("# Cross-platform priority mapping")
    print()
    print("| Internal code | Jira priority.name | Linear priority | GitHub label |")
    print("|---|---|---|---|")
    for k in ("P0", "P1", "P2", "P3", "P4"):
        print(f"| {k} | {JIRA_PRIORITIES[k]} | {LINEAR_PRIORITIES[k]} "
              f"| `{GITHUB_PRIORITY_LABELS[k]}` |")
    print()

    print("# Cross-platform status mapping (semantic alignment, not fixed strings)")
    print()
    print("| Semantic | Jira status | Linear state | GitHub |")
    print("|---|---|---|---|")
    for row in STATUS_MAP:
        print("| " + " | ".join(row) + " |")
    print()

    print("# Field-location reference")
    print()
    print("| Semantic | Jira (REST fields) | Linear (GraphQL input) | GitHub (REST body) |")
    print("|---|---|---|---|")
    for row in FIELD_MAP:
        print("| " + " | ".join(row) + " |")
    print()
    print("# Jira custom fields (IDs vary by instance; confirm via /rest/api/2/field)")
    for k, v in JIRA_CUSTOM_FIELDS.items():
        print(f"- {k}: {v}")
    return 0


# ---------------------------------------------------------------------------
# weekly-report
# ---------------------------------------------------------------------------
# The equivalent "done" state set: each platform's terminal-state wording.
DONE_STATES = {"done", "closed", "completed", "resolved"}
CANCELED_STATES = {"canceled", "cancelled", "won't do", "wont do", "rejected"}
BLOCKED_STATES = {"blocked", "on hold"}
IN_PROGRESS_STATES = {"in progress", "in review", "started"}


def _norm_state(raw: str) -> str:
    return (raw or "").strip().lower()


def classify(state: str) -> str:
    """Map a platform's state string to one of the 5 report groups."""
    s = _norm_state(state)
    if s in CANCELED_STATES:
        return "Canceled"
    if s in DONE_STATES:
        return "Done"
    if s in BLOCKED_STATES:
        return "Blocked"
    if s in IN_PROGRESS_STATES:
        return "In Progress"
    return "To Do"


def _extract_issue(item: dict, tracker: str) -> dict:
    """Normalize the three platforms' issue objects into
    (id, title, state, assignee, priority, blocked, url).

    Field paths differ per platform, extracted by platform branch here -- **no generic
    guessing**, because a wrong guess silently turns "assignee" into "reporter" in the
    weekly report.
    """
    if tracker == "jira":
        f = item.get("fields") or {}
        assignee = (f.get("assignee") or {}).get("displayName", "")
        prio = (f.get("priority") or {}).get("name", "")
        labels = f.get("labels") or []
        status = (f.get("status") or {}).get("name", "")
        # Jira blocking is often a custom field or a fixVersion marker, not visible
        # here; use a "blocked" label as the signal.
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
        # Linear priority is an integer: 0 = No priority, 1 = highest
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
    # GitHub state is the binary open/closed; finer semantics can only be read from labels
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
    """Convert YYYY-WNN into (label text, start date, end date). ISO weeks start Monday."""
    if not week:
        today = date.today()
        iso = today.isocalendar()
        week = f"{iso[0]}-W{iso[1]:02d}"
    try:
        year_s, week_s = week.upper().split("-W")
        year, wk = int(year_s), int(week_s)
        start = date.fromisocalendar(year, wk, 1)  # 1 = Monday
    except (ValueError, AttributeError) as e:
        raise BuildError(f"invalid week '{week}', expected YYYY-WNN (e.g. 2026-W38): {e}")
    return f"{year}-W{wk:02d}", start, start + timedelta(days=6)


def render_report(items: list, tracker: str, week_label: str,
                  start: date, end: date) -> str:
    """Render the normalized issue list into a Markdown weekly report."""
    groups = defaultdict(list)
    for it in items:
        groups[classify(it["state"])].append(it)

    lines = [
        f"# Weekly report {week_label} ({start.isoformat()} ~ {end.isoformat()})",
        "",
        f"- data source: {tracker}",
        f"- total issues: {len(items)}",
        "- by group: " + " · ".join(
            f"{g} {len(groups[g])}" for g in
            ("In Progress", "Blocked", "To Do", "Done", "Canceled") if groups.get(g)
        ),
        "",
    ]

    blocked = groups.get("Blocked", [])
    if blocked:
        lines += ["> [!WARNING]", f"> **{len(blocked)} blocked item(s), handle first:**",
                  ">"]
        for it in blocked:
            who = it["assignee"] or "Unassigned"
            lines.append(f"> - `{it['id']}` {it['title']} (assignee: {who})")
        lines.append("")

    for group in ("In Progress", "Blocked", "To Do", "Done", "Canceled"):
        bucket = groups.get(group)
        if not bucket:
            continue
        lines += [f"## {group} ({len(bucket)})", ""]
        lines.append("| ID | Title | State | Assignee | Priority |")
        lines.append("|---|---|---|---|---|")
        for it in bucket:
            title = it["title"].replace("|", "\\|")
            lines.append(
                f"| `{it['id']}` | {title} | {it['state']} | "
                f"{it['assignee'] or 'Unassigned'} | {it['priority'] or '-'} |")
        lines.append("")

    if not items:
        lines += ["(no issue records this week.)", ""]
    return "\n".join(lines).rstrip() + "\n"


def cmd_weekly_report(args) -> int:
    raw = _load_json(args.json, "--json")
    if isinstance(raw, dict):
        # tolerate each platform's response wrapper: Jira search / Linear GraphQL / GitHub REST
        items = (raw.get("issues")
                 or (raw.get("data") or {}).get("issues", {}).get("nodes")
                 or raw.get("results")
                 or [])
    elif isinstance(raw, list):
        items = raw
    else:
        return _die("--json must be an issue array or a response object containing issues/results")

    if not items:
        return _die("--json has no issue records (check you did not use the wrong response-wrapper level)")

    normalized = [_extract_issue(it, args.tracker) for it in items]
    week_label, start, end = _week_range(args.week)
    report = render_report(normalized, args.tracker, week_label, start, end)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"# written to {args.output} ({len(normalized)} issues)")
    else:
        sys.stdout.write(report)
        print(f"# stats: {len(normalized)} issues ({args.tracker})")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="issue_sync.py",
        description="Jira / Linear / GitHub Issues request building and weekly-report generation (offline, no requests)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build", help="build an issue-create request and print it")
    s.add_argument("--tracker", choices=["jira", "linear", "github"], required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--body", default="")
    s.add_argument("--priority", default="P2", help="P0..P4, default P2")
    s.add_argument("--assignee", default="")
    s.add_argument("--labels", default="", help="comma-separated")
    s.add_argument("--project", default="", help="Jira project key")
    s.add_argument("--team", default="", help="Linear team ID")
    s.add_argument("--repo", default="", help="GitHub owner/name")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("field-map", help="print the three-way field/status mapping table")
    s.add_argument("--json", action="store_true", help="emit JSON (for programmatic use)")
    s.set_defaults(func=cmd_field_map)

    s = sub.add_parser("weekly-report", help="generate a weekly-report Markdown from an issue list")
    s.add_argument("--json", required=True)
    s.add_argument("--tracker", choices=["jira", "linear", "github"], default="github")
    s.add_argument("--week", help="YYYY-WNN, defaults to this week")
    s.add_argument("--output", help="output file; defaults to stdout")
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
