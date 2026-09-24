---
name: issue-tracker-sync
description: "Compose issue-create requests for Jira, Linear, and GitHub Issues from one input, map priorities and statuses across the three models, and render a grouped weekly report. Use when the user asks to create an issue / file a bug ticket / sync tasks to Jira / generate a weekly report / cross-platform issue sync / task status summary / create Jira ticket / create Linear issue / open GitHub issue / weekly engineering report. Do NOT use for chat notifications (use feishu-dingtalk-bridge), Notion databases (use notion-workspace), or code review comments on pull requests."
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

# Issue Tracker Sync (Jira / Linear / GitHub Issues)

The same thing — "create an issue" — is three models across the three: Jira is REST + nested `fields`
(custom fields are `customfield_NNNNN`), Linear is a GraphQL mutation (everything is an input object,
labels need UUIDs), and GitHub is flat REST (no priority field, simulated with labels).

**Core judgment: status names cannot be copied verbatim.** All three allow custom workflows; "In Progress" might mean
"pending review" on site A. Before syncing you must do **semantic alignment**, not string copying.

**Red lines (enforced by this skill)**

1. **Never hardcode credentials**: read only from environment variables — `JIRA_BASE_URL` / `JIRA_EMAIL` /
   `JIRA_TOKEN` / `LINEAR_API_KEY` / `GITHUB_TOKEN`. The script never accepts, prints, or
   persists any token; credential positions in request bodies are always written as `$VAR` placeholders.
2. **Dry-run by default**: `build` only prints "the request that would be sent" and **sends no request**.
   Creating an issue produces a visible side effect on the team board (triggers notifications, counts toward the sprint),
   and must only be sent after user confirmation.
3. **Least privilege**: Jira only needs `write:jira-work` (not `manage:jira-project`);
   Linear uses a personal API key authorized only for the teams you need; GitHub PAT only needs `issues:write`,
   **do not** use the full `repo` scope.
4. **Reports are read-only**: `weekly-report` only renders Markdown from local JSON, with no network access and no remote writes.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Target platform | Yes | `jira` / `linear` / `github`, multi-select allowed |
| Title | Required for ticket creation | A concise verb phrase, e.g. "Fix garbled CSV export" |
| Body | No | Reproduction steps / acceptance criteria; under Jira v3 it must be converted to ADF |
| Priority | No | Internal numbering `P0..P4`, default `P2`; mapped separately per provider |
| Assignee | No | Jira wants `accountId`; Linear wants a user UUID; GitHub wants a login |
| Labels | No | Jira/GitHub use names; **Linear wants label UUIDs** |
| Container | Required for ticket creation | Jira `--project` key / Linear `--team` ID / GitHub `--repo owner/name` |
| Issue list JSON | Required for the weekly report | A response body from any of the three; the script branches by provider to extract fields |
| Token | Required for real execution | Environment variable only; not needed for dry-run and the weekly report |

**When inputs are missing, ask for all at once:**

> Please provide in one go: ① the target platform; ② title and body; ③ priority (P0..P4, default P2);
> ④ assignee identifier (Jira accountId / Linear user UUID / GitHub login; leave blank if unknown);
> ⑤ container (Jira project key / Linear team / GitHub repo). The weekly report additionally needs an
> issue list JSON. By default I only print requests and do not send.

## Pre-flight Self-check

```bash
python3 --version                                        # expect >= 3.8
test -f scripts/issue_sync.py && echo SCRIPT_OK           # expect to print SCRIPT_OK
# Credential check: only judge existence, never echo
for v in JIRA_BASE_URL JIRA_TOKEN LINEAR_API_KEY GITHUB_TOKEN; do
  printf '%s: ' "$v"; test -n "$(printenv $v)" && echo present || echo missing
done
test -n "$GITHUB_TOKEN" || gh auth status 2>/dev/null && echo "gh-cli available"
# Self-check: python3 scripts/issue_sync.py field-map should print the three providers' field comparison
```

| Result | Interpretation |
|---|---|
| A platform is `missing` | Only affects real sending; building requests proceeds, build the payload first |
| All `missing` | The weekly report (fully offline) and field-map cross-check can still be completed |
| `FIELD_MAP_OK` missing | The script is missing or syntactically broken; fall back to hand-assembling per the mapping table below |

## Cross-platform Status Mapping Table

**Semantic alignment, not string alignment.** The left side of the table is this skill's canonical semantics; the right side is each provider's
equivalent landing point; when syncing, **semantics win** and the landing form is decided by the target provider.

| Canonical semantics | Jira status | Linear state | GitHub (no workflow) |
|---|---|---|---|
| To do | To Do | Backlog / Todo | `open`, no status label |
| In progress | In Progress | In Progress | `open` + `status:in-progress` |
| In review | In Review | In Review | `open` + `status:in-review` |
| Blocked | Blocked | Blocked | `open` + `status:blocked` |
| Done | Done | Done | `closed` (completed) |
| Canceled | Won't Do | Canceled | `closed` (not planned) |

**Priority mapping**: `P0→Highest/1/priority:critical`, `P1→High/2/priority:high`,
`P2→Medium/3/priority:medium`, `P3→Low/4/priority:low`, `P4→Lowest/0/priority:backlog`.
Note that Linear's priority is an **integer** and `0 = No priority` (not the lowest — it means "unset").

## Workflow

### Step 1: Check the Target Platform's Workflow and Fields

```bash
python3 scripts/issue_sync.py field-map        # three providers' fields/status/priorities comparison
```

If the Jira site has custom statuses or Chinese priority names, **you must look up the real values first**:

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_TOKEN" "$JIRA_BASE_URL/rest/api/2/field" | head -40
```

Expected: get this instance's field IDs and priority enum names.
On failure: if you cannot map them, **stop and ask the user**; guessing would quietly degrade "high priority" to "medium," and no one would notice.

### Step 2: Build the Ticket-Creation Request (dry-run)

```bash
# python3 scripts/issue_sync.py build --tracker jira \
#   --title "Fix garbled CSV export" --body "Chinese characters garbled on export" --priority P1 \
#   --project ENG --labels "bug,export" --assignee <accountId>

# python3 scripts/issue_sync.py build --tracker linear \
#   --title "Fix garbled CSV export" --priority P1 --team <teamUUID> \
#   --labels "<labelUUID>,<labelUUID>"

# python3 scripts/issue_sync.py build --tracker github \
#   --title "Fix garbled CSV export" --priority P1 --repo owner/name \
#   --labels bug --assignee octocat
```

Expected: prints the full method/url/headers/body, with credential positions all as `$VAR` placeholders.
Note the structural differences: Jira is `body.fields.*`, Linear is `body.variables.input.*`,
GitHub is flat `body.*`.

On failure: `must provide --project/--team/--repo` → the container argument is missing;
`unknown priority` → only `P0..P4` are allowed.

### Step 3: Send

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

**Before sending, show the payload to the user**: creating a ticket notifies watchers and counts toward the sprint — a visible side effect.

Expected: Jira returns a `key` like `ENG-123`; Linear returns `issue.identifier`;
GitHub returns `number`. **Record the correspondence among these three** — it is the anchor for later syncing.

On failure: Jira `400` is usually a field-name/enum-value mismatch; Linear GraphQL errors live in
`errors[]` while HTTP is still 200; GitHub `422` is usually a missing label or an assignee with no permission.

### Step 4: Generate the Weekly Report

```bash
# first pull an issue list and save it as JSON (any of the three's shape)
python3 scripts/issue_sync.py weekly-report \
  --json issues.json --tracker github --week 2026-W38 --output report.md
```

Expected: grouped by status (in-progress / blocked / to-do / done / canceled), with **blocked items highlighted in a blockquote** at
the top of the report, one table per group with ID/title/status/assignee/priority.

On failure: `check whether you used the wrong response wrapper level` → the three wrap differently
(Jira `issues` / Linear `data.issues.nodes` / GitHub a bare array); the script tries automatically,
and if it still fails, manually reach the array layer before passing it in.

### Step 5: Anchor Cross-platform Sync

When the same item has tickets on multiple providers, **you must build an ID mapping ledger** (`ENG-123 ↔ ENG-123 ↔ #101`
plus each provider's URL), written into the issue body or a standalone CSV.

Expected: one row per issue in the ledger, with the three IDs and status.
On failure: without a ledger, **do not auto-copy statuses** — fuzzy title matching has a very high misfire rate;
in that case report "cannot align" rather than guessing.

## Delivery Standards

- **Definition of success**: the target provider returns the new issue's ID (Jira `key` / Linear `identifier` /
  GitHub `number`), and the status and priority land in the expected groups when rechecked by `weekly-report`.
- **Artifacts**: per-provider `payload.json`, `response.json`, the ID mapping ledger,
  and the weekly report `report.md`.
- **Integrity verification**:
  - The sum of the weekly report's group counts == the total issue count (the script prints this on the first line; check directly);
  - After creation, GET the returned ID once to confirm priority and assignee were not overwritten by provider defaults;
  - No token plaintext in artifacts: `grep -lE 'eyJ|ATATT|ghp_' *.json` should have no hits.

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Jira `400 field 'priority' cannot be set` | The site's priorities are Chinese names or a custom enum, and `High` does not exist | First query `/rest/api/2/field` to get the real enum names, then replace `priority.name` |
| A Jira custom field won't write | Used a semantic name (e.g. "story points") instead of `customfield_NNNNN` | Query `/rest/api/2/field` to find the numeric ID; the value must also be the option's `id`, not the display name |
| Jira `400` says the assignee is invalid | Cloud needs `accountId`, not an email or username | Use `/rest/api/3/user/search?query=` to look up the accountId |
| Linear returns 200 but actually failed | GraphQL errors live in `errors[]`; the HTTP code does not reflect business failure | Must read both `errors` and `data.issueCreate.success` from the response body |
| Linear label setting has no effect | `labelIds` needs UUIDs; a label-name string was passed | First query `labels` to get IDs; or leave `labelIds` empty and attach them manually afterward |
| No priority after creating a GitHub issue | Issues have no priority field | Simulate with labels (the script auto-appends `priority:high` etc.); if the label does not exist, create it first |
| GitHub `422 Validation Failed` | Label does not exist, or the assignee has no repo permission | First `POST /repos/{o}/{r}/labels` to create the label; confirm the assignee is already a collaborator |
| Status semantics are scrambled after sync | Status name strings were copied directly (each site has a different custom workflow) | Use this doc's semantic mapping table; when unsure, report "needs manual confirmation" rather than mapping on your own |
| Some issues in the weekly report lack an assignee | Read the wrong field path (e.g. Jira read `reporter`) | `_extract_issue` extracts by provider branch; do not change it to a generic guess; check the raw JSON key names |
| The weekly report counts "canceled" as "done" | GitHub's `closed` covers both completed and not planned | Distinguish by label (`wontfix`/`invalid` → canceled); otherwise read `state_reason` |

## References

- `scripts/issue_sync.py` — `build` (three-provider request construction) / `field-map` (includes `--json`
  for programmatic consumption) / `weekly-report` (offline rendering)
- `references/sources-and-methodology.md` — why semantic alignment rather than string copying,
  the difference in error detection between GraphQL and REST, and the trade-offs in grouping the weekly report
