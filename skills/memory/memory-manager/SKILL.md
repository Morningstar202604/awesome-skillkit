---
name: memory-manager
description: "Use when managing the lifecycle of an agent's memory store: resolve conflicts between new candidates and existing entries, execute ADD/UPDATE/DELETE/NOOP operations, and run forgetting policies (TTL, recency decay, topic compaction). Triggers on memory management, memory deduplication, conflict resolution, memory lifecycle, memory deduplication, ADD UPDATE DELETE NOOP, TTL expiry, memory compaction, memory consolidation, long-term memory, RAG. NOT for extracting new candidates or retrieving memories — use memory-extractor or memory-retriever."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-16"
---

# Memory Manager

Memory stores rot: new and old entries conflict, facts go stale, and same-topic duplicates bloat. This skill manages the memory's full lifecycle — every new candidate first passes a conflict-resolution decision table, the store uses only the four atomic operations ADD/UPDATE/DELETE/NOOP, and three brooms — TTL, decay, and compaction — sweep the store regularly. Every operation leaves an audit log: memories may be rewritten, but never silently.

## Input Checklist

Collect everything up front before starting. If an input is missing, ask the user once with this prompt: "To manage the memory store, please provide all at once: the existing memory store export (JSON), the new candidates to store (memory-extractor's candidates.json), and this run's mode (incremental merge / full-store sweep / responding to a user deletion request)."

| Input | Required | Notes |
|---|---|---|
| Existing store export | Yes | JSON entry array; must include id, content, confidence, updated_at, hit_count |
| New candidates | Required in merge mode | candidates.json from memory-extractor; not needed for a full sweep |
| Run mode | Yes | merge (incremental merge) / sweep (full-store sweep) / purge (responding to an explicit user deletion) |
| User deletion instruction | Required in purge mode | Explicitly identifies the deletion target (by id or by user_id for all) |

## Pre-flight Self-check

This is a pure-prompt skill; no environment probing needed. It only checks input completeness:

- Is the existing store export valid JSON with entries carrying ids? A store without ids → first ask to add ids per memory-architect's schema; do not invent ids on the spot.
- In merge mode, do candidates carry evidence_quote? Candidates without evidence → send back to memory-extractor for re-extraction; this skill does not accept entries without evidence.
- In purge mode, is the deletion instruction specific to an id or user_id? "Delete the useless ones" is not a clear instruction → ask for clarification before acting (red line 2 does not allow guessing).

## Red Lines

1. DELETE must leave an audit log: every deletion records op, target_id, the full before-text, and the reason in the operations log; the log is persisted alongside the store.
2. When a user explicitly asks for deletion → delete immediately and irrecoverably (GDPR-style right to erasure): do not unilaterally do a "soft delete with backup"; when deletion is requested by user_id, delete all of that user's entries.
3. Conflicts never overwrite history: entry content updates must preserve the evolution note changed_from; silent overwriting of old values is forbidden.
4. Never silently modify machine fields other than confidence and ttl: id, created_at, and user_id are never changed.
5. The audit log is persisted at the same level as the store: an operation that only outputs "what changed" without producing an archivable log file is not complete.

## Workflow

### Step 1: Read in the Store and Candidates

- **Action:** Load the existing store and candidates, and build two indexes: a primary index by id, and a comparison index by content keywords (compare same-topic candidates together).
- **Expected:** A stats snapshot: entry count in store, candidate count, distribution by type.
- **On failure:** The store file is corrupted or truncated → stop and ask for a re-export; "skip bad lines and continue" is forbidden — silently losing data is unacceptable.

### Step 2: Conflict Resolution

- **Action:** Adjudicate each candidate against the decision table:

| Situation | Verdict | Action |
|---|---|---|
| Semantically equivalent, no new information | NOOP | Discard the candidate, log reason as duplicate |
| Semantically equivalent, updated information (state changed) | UPDATE | The new value wins; the old value goes into the changed_from note |
| Same topic but contradictory timelines ("works in Shanghai" vs "back in Beijing") | UPDATE + disputed flag | Take the newer timestamp as authoritative; mark the entry `disputed: true` for the retrieval side to down-weight |
| New topic | ADD | Store directly, inheriting the candidate's confidence |
| Complementary to an existing entry (two sides of the same fact) | ADD (after splitting finer) | Both entries coexist, cross-referenced in each other's tags |
| Partial overlap (neither equivalent nor complementary) | UPDATE (merge) | Take the more informative phrasing as the body, dedup the overlap, fold in the unique information; if hard to merge, split finer and treat as complementary |

- **Expected:** Every candidate gets a unique verdict, with no dangling items. The evolution note format is uniformly `[changed_from: original old value]`; disputed adds `[disputed: true]`; both markers are machine-readable by memory-retriever.
- **On failure:** New and old entries cannot be judged for recency (timestamps missing) → conservatively take NOOP and log ambiguous; better to miss than to err.

### Step 3: Execute the Four Operations

- **Action:** Turn verdicts into atomic operations and generate an operation log, each `{op, target_id, before, after, reason}`. UPDATE follows Letta's core-memory self-edit pattern — rewrite the whole block rather than appending at the end, to avoid append-bloat like "user works in Shanghai → user is now in Beijing → user works in Shanghai."
- **Expected:** After the operations array runs in order, the store state is consistent; the changed_from chain in each UPDATE's after is traceable.
- **On failure:** An operation's target id does not exist in the store → void that operation and log it, without interrupting the rest.

### Step 4: Forgetting and Compaction

- **Action:** Run the three brooms in order —
  1. TTL broom: entries whose `ttl` field is earlier than today are deleted directly (audit-logged).
  2. Decay broom: entries not retrieved for over 90 days (empirical, adjustable) and with confidence < 0.7 get confidence multiplied by 0.8 (empirical, adjustable); entries falling below 0.4 are deleted. For stores missing hit_count, use the days since updated_at instead.
  3. Compaction broom: when same-topic entries (same user_id + same type + same tags) exceed 10 (empirical, adjustable), summarize and merge them into one topic summary; delete the originals and mark the summary entry's source as `compacted`.
- **Expected:** Each broom produces a cleanup list; the store entry count drops or stays stable, never only grows. Execution cadence: TTL and decay run alongside every merge; compaction runs only on a full sweep — compaction is expensive and changes retrieval habits, so it should not run on every incremental merge.
- **On failure:** The compaction summary loses key detail (e.g. specific numbers) → do not compact that topic; prefer bloat over distortion, and log skip_compaction.

### Step 5: Output the Operation Log and New Store

- **Action:** Produce operations.json and the updated full store JSON, with stats: counts for each of the four operations, how many deletions the sweep made, and before/after entry counts.
- **Expected:** operations.json can be archived directly as an audit record; every entry in the new store conforms to memory-architect's schema.
- **On failure:** The stats do not reconcile (operation count ≠ store delta) → replay the operations step by step to find the discrepancy, fix it, then deliver.

operations.json structure:

```json
{
  "date": "2026-09-16",
  "mode": "merge",
  "operations": [
    {"op": "UPDATE", "target_id": "mem_001", "before": "The user works in Shanghai", "after": "The user is back working in Beijing [changed_from: The user works in Shanghai] [disputed: false]", "reason": "candidate newer by 90 days"}
  ],
  "sweep": {"ttl_deleted": 3, "decayed": 12, "compacted_topics": 2},
  "stats": {"before": 210, "after": 198}
}
```

## Parameter Quick Reference

| Parameter | Default | Notes |
|---|---|---|
| Decay trigger line | Not hit for 90 days and confidence < 0.7 | Empirical, adjustable |
| Decay factor | confidence × 0.8 per pass | Empirical, adjustable; one pass per full sweep |
| Deletion threshold | confidence < 0.4 | Empirical, adjustable |
| Compaction trigger line | Same topic > 10 entries | Empirical, adjustable |
| disputed flag | Set true on timeline contradictions | The retrieval side (memory-retriever) down-weights on this |
| Healthy NOOP ratio line | > 60% signals the extraction side is too noisy | Empirical, adjustable; persistently over the line means going back to tune memory-extractor |
| Recommended sweep frequency | Weekly or every 1000 writes | Empirical, adjustable; the full sweep (all three brooms) triggers here |
| Audit log retention | Same lifecycle as the store | The log is persisted with the store, not expired separately; purge operation logs are kept permanently |

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Store count only grows, never shrinks | Only ADD, no sweep | Re-run step 4's three brooms; the long-term fix is to schedule sweep as a periodic task |
| The same fact is repeatedly UPDATEd | Extraction granularity too coarse, or the fact itself is unstable | Check the changed_from chain length; entries over 3 updates are marked unstable for the retrieval side to down-weight |
| User looks for an entry after DELETE | The user does not remember requesting the deletion | Show the reason and the original instruction text from the audit log; the store does not roll back (red line 2) |
| Retrieval worsens after compaction | The summary dropped high-value detail | Roll back that topic's compaction (rebuildable from the audit log), and raise the compaction trigger line |
| Candidate fields do not match the store | Schema version drift | Map fields against memory-architect's frozen version; write the mapping table into the log |
| A purge request is vaguely targeted | The user gave no id | Use a retrieval preview to list the candidate deletions and ask the user to confirm; do not delete before confirmation |
| Sweep wrongly deletes entries the user still needs | TTL set too short or decay too fast | Manually restore the entry from the audit log's before-text; lower the corresponding parameter and record the adjustment in the store's metadata |
| After merge, two near-duplicate entries appear in the store | The keyword comparison index missed a pair | Add the missed pair to the log and run a dedicated re-comparison of step 2; the long-term fix is dual-path comparison once candidates carry embeddings |
| The user asks to "also optimize the store while you're at it" | Out of scope for this mode | Make clear this run only does the declared mode; full-store optimization goes through sweep mode as a separate task |
| The candidate's user_id matches no owner in the store | A new user or a labeling error | Confirm with the user: if a new user, ADD directly; if a labeling error, send back to memory-extractor to fix the ownership |

## Delivery Standards

- operations.json is valid JSON; every operation has the five fields op, target_id, before, after, reason; every DELETE has an audit record.
- The new store is valid JSON; all entries conform to the upstream schema; the changed_from chain is complete and traceable.
- Each of the three brooms produces a cleanup list; the before/after entry counts reconcile.
- In purge mode, the target entries have zero residue, and the audit log records the user's original instruction text.
- A stats section is attached: four-operation distribution, sweep volume, and count change.
- The audit log is persisted with the store (same directory or same export bundle) and can be replayed independently.

## References

- `references/sources-and-methodology.md` — read when you need to explain where the ADD/UPDATE/DELETE/NOOP decision table and the core-memory self-edit rewrite pattern come from (mem0 / letta) and how to attribute them; also read during review to cross-check methodology.

## Chain Position

- Upstream: `memory-extractor` (the only legitimate source of candidates.json) and `memory-architect` (the definer of the schema and forgetting policy).
- Downstream: `memory-retriever` (consumes the clean store this skill maintains; disputed and unstable flags are for it to down-weight).
- This skill is the "librarian" of the memory-systems chain: no matter how well the upstream produces, without this skill's adjudication and sweeping the store still rots.
