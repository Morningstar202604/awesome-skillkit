# Methodology sources and design trade-offs (notion-workspace)

> When to read: when you want to upgrade the Notion API version, change pagination strategy, or question "why the script sends no requests".
> This file only covers design rationale; it does not repeat the operational steps in SKILL.md.

## Idea sources (distilled from public methodology; not copied text)

| This skill's approach | Idea distilled from |
|---|---|
| Request construction separated from network sending | The hexagonal-architecture "port/adapter" separation: business rules (payload shape) don't depend on IO (HTTP client) |
| `build-*` only prints, doesn't send | Terraform `plan` / `apply` two-phase; `kubectl --dry-run=client`'s "see the payload first" convention |
| Block-type whitelist, unknown type errors | The compiler's fail-fast strategy on unknown AST nodes: silent degradation hides data loss |
| Unmapped blocks rendered as HTML comments | The Markdown ecosystem's `<!-- -->` comment-placeholder convention: degrade but leave a trace, easy to fill in later |
| Credentials never enter the script | Twelve-Factor App principle III config: config lives in the environment, not in code |
| Pagination uses cursor not offset | The consensus of cursor-pagination APIs like Notion/Stripe/Twitter: cursors don't skip/duplicate rows under concurrent changes |

## Key trade-offs

**Why does the script send no HTTP requests at all?** One, so `build-*` / `parse-*` can be fully unit-tested in an environment with no network and
no token; two, to keep the decision of "whether to write into the user's workspace" in human hands. The script only answers
"what does the payload look like," not "whether to send." The cost is that the send step needs the AI or user to assemble curl themselves—
this part is given a directly copyable template in SKILL.md step 3.

**Why is the version header hardcoded as a constant in the script?** Notion's `Notion-Version` is not optional
decoration: across versions, property semantics and block structures change. Scattered strings will eventually
drift, so consolidated into one `NOTION_VERSION` constant—upgrading is a single-point edit, and
`build-*` output prints it out for manual verification.

**Why is the `page_size` cap intercepted at the script layer?** 100 is the server-side hard cap; blocking locally
saves a round trip that would fail anyway; more importantly, it pushes the correct solution (pagination) to the user
directly, rather than letting them think bumping `page_size` pulls everything in one shot.

**Why must `parent-type` be explicit rather than auto-detected?** Page and database `parent`
structures differ (`page_id` vs `database_id`), and the two IDs look identical—impossible to infer from the
string. Auto-guessing produces a 400 when wrong, and the 400 error won't tell you
"actually, it's the parent type that's wrong." Explicit declaration surfaces the error at the call site.

**Why only 9 block types supported?** Tables, sync blocks, embeds, database views have complex block structures
with their own nested constraints; half-baked support produces payloads the server rejects. Under the whitelist strategy,
encountering an unsupported type errors immediately with a supported list—behavior is predictable.

## Official documentation

- Notion API versioning and request headers: <https://developers.notion.com/reference/versioning>
- Create page (`POST /v1/pages` and `parent` structure): <https://developers.notion.com/reference/post-page>
- Query database (cursor pagination, filter/sorts): <https://developers.notion.com/reference/post-database-query>
- Block objects and type list: <https://developers.notion.com/reference/block>
- Rich-text objects and `annotations`: <https://developers.notion.com/reference/rich-text>
- Rate limits (~3 req/s and 429 handling): <https://developers.notion.com/reference/request-limits>
- Integration authorization model (why unauthorized returns 404): <https://developers.notion.com/docs/authorization>
