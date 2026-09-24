---
name: notion-workspace
description: "Build and parse Notion API payloads offline: page creation bodies, database query filters with cursor pagination, and block-to-Markdown rendering. Use when the user asks to write to Notion / sync to Notion / create a Notion page / query a Notion database / export a Notion page / organize a Notion workspace / write to Notion / create Notion page / query Notion database / export Notion page / sync notes to Notion. Do NOT use for Slack or Feishu messaging (use feishu-dingtalk-bridge), issue trackers (use issue-tracker-sync), or local Markdown files that never leave disk."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only for the helper script. Live execution needs a Notion internal integration token in NOTION_TOKEN plus outbound HTTPS to api.notion.com — the bundled script never sends requests and runs fully offline."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Notion Workspace (Read/Write Notion Workspace)

Solves the class of needs "push local content into Notion, or pull Notion content back." This skill's focus
is not "sending requests" but **constructing the requests correctly** — the Notion API's type system is more cumbersome than most REST APIs;
get the four-layer structure of `parent`, `properties`, `rich_text`, and block types wrong by one layer and you eat a 400.

**Core judgment: Notion's payload is a strongly typed structured object, not free JSON.**
So this skill first uses the script to build the payload offline for human review, then sends with credentials.

**Red lines (enforced by this skill)**

1. **Never hardcode credentials**: the token is read only from the `NOTION_TOKEN` environment variable;
   writing it into SKILL.md examples, scripts, JSON files, or git is forbidden. The script itself **does not read the token at all** — it only
   builds payloads and sends no requests.
2. **Dry-run by default**: the `build-*` subcommands only print "the JSON that would be sent" and **send no
   HTTP requests**. The send action must happen only after the user confirms.
3. **Least privilege**: request only the two capabilities `content: read` and `content: update` (or `insert`),
   do not turn on unrelated scopes like reading user info; the integration is only authorized to the pages that need it,
   not the whole workspace.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Operation intent | Yes | Read (query/export) or write (create page / append blocks / update properties) |
| Target object ID | Yes | The parent page `page_id`, the database `database_id`, or a page ID; take it from the last 32-hex segment of the URL |
| Content source | Required for write ops | The body to write: a local Markdown file or a block JSON array |
| Properties/filter | No | Required for the database case: the column names to write, or the filter/sorts for the query |
| `NOTION_TOKEN` | Required for real execution | The Notion integration token, environment variable only; not needed to build read-only payloads |

**When inputs are missing, ask for all at once:**

> Please provide in one go: ① read or write; ② the target page/database ID (or just give the Notion link and
> I will extract the ID); ③ the content file to write or the conditions to query; ④ confirm the token is in
> the `NOTION_TOKEN` environment variable (I will not ask you to paste it). The default behavior is to only print the request payload,
> send no requests; when you actually want to execute, please say "execute" explicitly.

## Pre-flight Self-check

```bash
python3 --version                                     # expect >= 3.8
test -f scripts/notion_ops.py && echo SCRIPT_OK       # expect to print SCRIPT_OK
# Credential check: only judge "whether it exists," never echo the content
test -n "$NOTION_TOKEN" && echo "ticket present" || echo "NOTION_TOKEN missing"
# Only check existence, never echo $NOTION_TOKEN — a token in terminal history is a leak
# python3 scripts/notion_ops.py --help >/dev/null && echo CLI_OK
```

| Result | Interpretation |
|---|---|
| `NOTION_TOKEN missing` | Only affects the "actually send" step; building payloads and parsing responses still work |
| `SCRIPT_OK` missing | The script is absent; fall back to hand-assembling JSON per this doc's field table |
| `CLI_OK` missing | A subcommand was mistyped; run `--help` to check |

## Workflow

### Step 1: Confirm the Target and Permissions

Clarify read/write and the target object ID. If the user gives `https://www.notion.so/<workspace>/<title>-<32-hex>`,
take the last 32-hex segment as the ID. **Before a write op you must confirm the integration has been authorized to that page** —
unauthorized pages return 404 rather than 403, which is Notion's deliberate design (it does not leak whether the object exists).

Expected: a clean ID string plus read/write intent.
On failure (the ID has hyphens): UUID form `8f3e-2a1b-...` needs hyphens removed before passing it in.

### Step 2: Build the Request Payload (dry-run)

```bash
# 2a. Create a page: child blocks are described as JSON first, the script converts them to Notion block structure
python3 scripts/notion_ops.py build-page --parent demo-parent --title sample page   # dry run: only builds the request body, sends no network request

# python3 scripts/notion_ops.py build-page \
#   --title "Weekly report 2026-W38" --blocks blocks.json \
#   --parent <parent-page-id> --parent-type page

# 2b. When clearing child blocks and attaching a database record instead, switch parent-type to database
# python3 scripts/notion_ops.py build-page \
#   --title "Task A" --parent <database-id> --parent-type database

# 2c. Query a database
# python3 scripts/notion_ops.py build-database-query \
#   --database <database-id> --filter filter.json --sorts sorts.json --page-size 100
```

Expected: prints the full request body + request header list + child block count, with the ending explicitly stating "no request was sent."
`--page-size` over 100 or more than 100 child blocks are blocked directly by the script (see the failure table).

On failure: reports `unsupported block type` → switch the type per the mapping table below;
reports `must provide --parent` → Notion does not support creating pages at the workspace root; a parent object is required.

### Step 3: Send (credentials injected by the proxy layer)

Save step 2's output as `payload.json`, then the AI or user executes it with curl/SDK:

```bash
curl -sS -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  --data @payload.json > response.json
```

**Both headers are indispensable**: `Authorization` and `Notion-Version`. The latter decides field semantics —
omitting it or having it rewritten by a proxy silently gets you a response under the old schema.

Expected: HTTP 200 and the response body contains the new page's `id`.
On failure: `400 validation_error` → check the failure table; `401` → check the token;
`404 object_not_found` → first suspect "the integration is not authorized to that page."

### Step 4: Parse the Response

```bash
# python3 scripts/notion_ops.py parse-page --json response.json          # single page
# python3 scripts/notion_ops.py parse-page --json query_result.json      # database query result
# python3 scripts/notion_ops.py blocks-to-markdown --json blocks.json    # pulled block tree
```

Expected: properties are flattened into a Markdown table, with each column's type noted; a query response first reports
`N records total has_more=?`.
On failure: a property shows `(empty)` → that column is genuinely empty or the integration has no permission to read that property (common for relation columns).

### Step 5: Paginate to Pull Everything

Notion uses **cursor pagination**: there is no offset, only `start_cursor` / `next_cursor`.

```bash
# python3 scripts/notion_ops.py build-database-query \
#   --database <ID> --page-size 100 --start-cursor "<the previous page's next_cursor>"
```

Loop: send → read `has_more` → if true, feed `next_cursor` back into `--start-cursor` → repeat.

**You must rate-limit**: an integration averages about **3 req/s**; beyond that you get 429.
Leave ≥ 350ms between pages, and on 429 use exponential backoff (prefer the `Retry-After` header).

Expected: continue until some response has `has_more=false` and `next_cursor=null`.
On failure: an infinite loop → check whether you mistakenly reused the previous page's cursor; an expired cursor restarts from page one.

### Step 6: Deliver

Report: the operated object and ID, the affected entry count, and the artifact file paths. For write ops, attach the response's `url`
so the user can click through to verify. If only a dry-run was done, state explicitly that "no request was sent."

Expected: the delivery note covers the object ID, entry count, and artifact path; write ops attach the `url`; when only a dry-run was done,
it explicitly says "no request was sent."
On failure: `url` is missing (the response was truncated) → build
`https://www.notion.so/<32-hex>` from the page ID for the user to verify; if an artifact path cannot be written → say that only
a dry-run was done and nothing has been persisted yet; do not fudge it with "done."

## Block Type Mapping Table

| Local JSON `type` | Notion block | Required fields | Renders back to Markdown |
|---|---|---|---|
| `paragraph` | `paragraph` | `rich_text` | Blank line between paragraphs |
| `heading_1/2/3` | Same name | `rich_text` | `#`/`##`/`###` |
| `bulleted_list_item` | Same name | `rich_text` | `- ` |
| `numbered_list_item` | Same name | `rich_text` | `1. ` |
| `to_do` | `to_do` | `rich_text` + `checked` | `- [x]` / `- [ ]` |
| `code` | `code` | `rich_text` + `language` | Triple-backtick fence |
| `callout` | `callout` | `rich_text` + `icon` | `> [!NOTE]` |
| `quote` | `quote` | `rich_text` | `> ` |
| `divider` | `divider` | None | `---` |

Block types not listed (tables, sync blocks, embeds, etc.) are not guessed by the script; it errors out directly or renders
an HTML comment placeholder — **leave a trace rather than silently dropping content**.

## Delivery Standards

- **Definition of success**: a write op returns 200 with the new object's `id` in the response; a read op's pagination loop
  converges on `has_more=false`, with no duplicate/missing pages.
- **Artifacts**: `payload.json` (reviewable payload before sending), `response.json` (raw response),
  and the parsed Markdown file.
- **Integrity verification**:
  - After a write op, GET the returned `id` once to confirm properties and child block counts match expectations;
  - For a read op, compare `parse-page`'s record count with this run's cumulative count;
  - No token plaintext in any artifact (`grep -c "$NOTION_TOKEN" *.json` should be 0).

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| `400 validation_error: body failed validation` | The payload structure is misaligned: `parent` type and ID mismatch, or `rich_text` wrapper missing | Regenerate the payload with this skill's `build-*`, do not hand-edit; double-check `--parent-type` |
| `400` with `children` too long | More than 100 child blocks in a single request | Split batches: first create an empty page, then attach ≤100 blocks per call via `PATCH /v1/blocks/{id}/children` |
| `401 unauthorized` | Token missing, expired, or revoked | Regenerate the integration token and update the environment variable; do not echo the token to the terminal |
| `404 object_not_found` | **The integration is not authorized to that page** (the page does exist — Notion deliberately does not distinguish) | On the Notion page, top-right `•••` → Connections → add this integration |
| `429 rate_limited` | Over about 3 req/s | Read the `Retry-After` header and back off; raise the inter-page interval to ≥350ms; batch writes in chunks |
| `400` says a property name does not exist | A database column was renamed, or a page-level `title` structure was mistakenly used | First GET an existing record, use `parse-page` to print the real column names, then align |
| Paginated results duplicate or lose data | The cursor was not fed back, or data changed during paging | Sort by `created_time` for a stable order; the cursor is only valid within the current session |
| Rich-text formatting is lost | Wrote back directly with `plain_text` without converting `annotations` | On the parse side use `blocks-to-markdown`; on the write side hand-construct the `annotations` object |

## References

- `scripts/notion_ops.py` — four subcommands: `build-page` / `build-database-query` /
  `parse-page` / `blocks-to-markdown`; `NOTION_VERSION` is the single source of truth for the version header
- `references/sources-and-methodology.md` — the design trade-offs for pinning the version header, cursor pagination, and rate limiting
