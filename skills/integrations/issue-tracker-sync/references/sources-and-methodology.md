# Methodology sources and design trade-offs (issue-tracker-sync)

> When to read: when you're onboarding a fourth tracker (e.g. GitLab / Azure Boards / Feishu Tasks),
> changing weekly-report grouping logic, or questioning "why no automatic two-way sync".

## Idea sources (distilled from public methodology; not copied text)

| This skill's approach | Idea distilled from |
|---|---|
| Use a "canonical semantics" middle layer rather than directly copying status names | The canonical model / semantic mediator pattern in data integration: pairwise mapping of N sources is N², through a middle layer is 2N |
| `build` / `field-map` / `weekly-report` three-part separation | Port-adapter: outbound writes, reference data, and read-only reports have different lifecycles and permissions |
| Priorities use internal numbers P0..P4 | The config-management convention of "internal identifier + external mapping table," avoiding treating one platform's enums as the baseline |
| Normalized extraction written per-platform, no generic guessing | The anti-guessing principle in parser design: the errors of guess-based field extraction are silent and cost the most |
| Weekly report must record the ID-mapping ledger | The correlation ID / external-ID mapping-table idea from distributed systems: anchorless sync is unrecoverable |
| dry-run produces the request body first | Terraform `plan` / `kubectl --dry-run=client` two-phase convention |

## Key trade-offs

**Why no automatic two-way sync?** Two-way sync needs three prerequisites: reliable ID mapping, conflict-detection
policy (who wins when both sides change), and idempotent writes. All three depend on the other platform's event stream, and the three vendors'
webhook semantics, redelivery behavior, and field-change notifications all differ. A half-built two-way sync is more dangerous than none—it
silently reverts state when no one is watching. So this skill does only **one-way construction + read-only reporting**,
leaving the sync anchor (ID ledger) explicitly to the user to maintain.

**Why is status mapping "semantic alignment" rather than table lookup?** All three vendors allow custom workflows.
A Jira site can rename "In Progress" to something else, or insert a middle state like "pending PM confirmation."
Mapping by string breaks at the first customized site. Using canonical semantics as the middle layer,
and reporting "needs human confirmation" when no mapping fits, beats guessing a result.

**Why does `field-map` provide both human-readable and `--json` output?** The table is for humans;
JSON is for the orchestration layer to consume (e.g. letting the AI batch-construct requests per the mapping table).
Two views from one source of truth, avoiding the mapping table drifting between docs and code.

**Why not help the user look up Jira's customfield ID?** That needs real credentials and network calls,
conflicting with this skill's "script testable offline" constraint; more importantly, field IDs are **site-specific**,
hardcoding them in the script will inevitably go stale. The right approach is to give the query command in SKILL.md, letting the user
get the current value in the real environment.

**Why is the weekly report grouped by status rather than by assignee?** The weekly report's reader is the team;
what they most need to see immediately is "what's stuck" (blockers highlighted on top), and only secondarily "who's doing what."
Grouping by assignee hides blockers—they scatter across each person's table, and the reader has to discover them.

**Why split GitHub's `closed` into done/canceled?** `closed` is a binary state,
but semantically "finished" and "decided not to do" mean completely different things to the weekly-report reader: the former is delivery,
the latter is a decision. Distinguishing by label is the common GitHub-ecosystem practice; as a fallback, read the
`state_reason` field.

## Official documentation

- Jira REST API v2 create issue: <https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issues/#api-rest-api-2-issue-post>
- Jira field query (find customfield IDs and priority enums): <https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-fields/>
- Jira Cloud user search (get accountId): <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/>
- Linear GraphQL `issueCreate` mutation: <https://developers.linear.app/docs/graphql/working-with-the-graphql-api>
- Linear priority enum notes: <https://linear.app/docs/priorities>
- GitHub Issues REST (create and fields): <https://docs.github.com/en/rest/issues/issues#create-an-issue>
- GitHub API version header: <https://docs.github.com/en/rest/about-the-rest-api/api-versions>
- Python `datetime.date.fromisocalendar` (ISO week calculation basis): <https://docs.python.org/3/library/datetime.html#datetime.date.fromisocalendar>
