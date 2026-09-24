---
name: memory-architect
description: "Use when designing a long-term memory architecture for an AI agent: layered memory (working/core/archival), storage selection, memory entry schema, read/write paths, and forgetting policy. Triggers on memory system design, memory architecture, agent long-term memory, memory design, memory schema, memory layering, storage selection, forgetting mechanism, memory pressure, knowledge retrieval, RAG. NOT for extraction/management/retrieval logic itself — use memory-extractor, memory-manager, or memory-retriever."
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

# Memory Architect

When most people give an agent memory, they just "dump it all into a vector database and walk away" — the result is retrieval noise, stale memories polluting the context, and privacy you can never delete. This skill designs before it builds: before writing a single line of storage code, settle all five questions — what to remember, which layer to put it in, what structure it takes, who may edit it, and how it is forgotten — then produce an executable architecture decision record.

## Input Checklist

Collect everything up front before starting. If an input is missing, ask the user once with this prompt: "To design a memory architecture, please provide all at once: the agent's purpose and main tasks, the expected memory scale (order of magnitude of entry count), whether a vector database / database is available, privacy requirements (whether user personal information is involved), and the token budget constraint (the upper limit of context memory may occupy)."

| Input | Required | Notes |
|---|---|---|
| Agent purpose and task type | Yes | Determines what to remember: customer service stores preferences, coding assistants store project state, assistants store facts and relations |
| Memory scale order | Yes | Hundreds / thousands / 100k+ entries; directly drives storage selection |
| Available storage facilities | Yes | Plain files / SQLite / vector database; with no vector database the design must take the degraded path |
| Privacy requirements | Yes | Whether to store PII, whether deletion-right support is needed; if involved, triggers red line 2 |
| Token budget | No | Upper limit of memory injectable per session; defaults to the empirical 2000 tokens, adjustable |
| Concurrent writers | No | Single agent or multiple agents writing together; multi-writer setups must add timestamp and source fields |

## Pre-flight Self-check

This is a pure-prompt skill; no environment probing needed. It only checks input completeness:

- Are the first four of the six inputs (purpose, scale, storage facilities, privacy requirements) all clear? If any is missing → stop and ask once with the prompt above; do not guess.
- User says "just design something generic" → design scale at the thousands level, storage on the plain-file degraded path, and explicitly mark these two assumptions in the ADR.
- User only wants "a chat log archive" → that is not a memory system; this skill does not apply — say so directly.

## Red Lines

1. Never store sensitive credentials: passwords, API keys, tokens, and private keys never enter the memory store. If found, refuse the write and prompt the user to use environment variables or a secrets manager instead.
2. PII must be flagged: when a memory entry contains personally identifiable information, the schema's `pii` field must be true, and the design must include the ability to delete all of a user's entries in one action by user_id.
3. The design must include a forgetting mechanism: a memory system with no TTL and no eviction policy is a liability, not an asset. A deliverable missing a forgetting mechanism must be reworked.
4. Never design records "just in case": every memory category must answer "who reads it, when, and what they do with it." If you cannot answer that, do not store it.
5. When privacy level is unconfirmed, always design to the highest privacy tier (store less, encryption-aware, deletable).

## Workflow

### Step 1: Requirements Profiling

- **Action:** Break memory needs into five categories and register each — facts (who the user is), preferences (what the user likes), decisions (what was decided), project state (how far along things are), relations (who has what connection to whom). For each category record: writer, reader, lifespan (in-session / weekly / permanent), privacy level.
- **Expected:** A five-row requirements table, each row complete with its four elements.
- **On failure:** The user cannot name a reader for a category → remove that category from the design; do not keep memories "that might come in handy."

### Step 2: Layered Design

- **Action:** Map each requirements category to one of three layers, and complete storage selection.
- **Expected:** A layering table plus a selection conclusion, with an explicit storage medium per layer.

| Layer | What goes here | Lifespan | Implementation reference |
|---|---|---|---|
| working | Intermediate state of the current task | Single task | Agent runtime variables, not persisted to disk |
| core | A small set of key facts resident in context | Long-lived, self-updating | Letta's core memory (an agent-editable resident block) and the Claude memory tool's MEMORY.md index |
| archival | Full persistent memory, retrieved on demand | Permanent until TTL expiry | Letta's archival memory (vector database) or file-based topical memory |

Storage selection table (three axes: data volume, retrieval latency, ops cost):

| Option | Suitable data volume | Retrieval latency | Ops cost |
|---|---|---|---|
| Plain files (MEMORY.md index + topic files) | < a few thousand entries | Full-text scan, slow but acceptable | Zero dependencies, git-versionable |
| SQLite (FTS5 full-text index) | Thousands to 100k entries | Millisecond keyword retrieval | Single file, no service |
| Vector database (e.g. Qdrant / Chroma) | 10k+ entries or when semantic search is needed | Ten-millisecond range | Needs an embedding pipeline and service |
| SQLite + hybrid vectors | 100k+ entries, high-quality retrieval required | Lowest (hybrid retrieval) | Highest; two indexes must be kept in sync |

Selection decision rule: < 2000 entries → plain files; 2000–100000 and keyword-only → SQLite; semantic similarity search needed → vector database; ample budget and large scale → hybrid. All thresholds are empirical and adjustable.

### Step 3: Schema Design

- **Action:** Freeze the memory entry structure per the template below; field names in English, machine-parseable:

```json
{
  "id": "mem_20260916_0001",
  "content": "The user prefers a concise reply style",
  "type": "preference",
  "user_id": "u_123",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z",
  "confidence": 0.9,
  "ttl": "2027-09-16",
  "source": "conversation:2026-09-16",
  "pii": false,
  "tags": ["style"]
}
```

- **Expected:** A frozen schema; `id` globally unique, `type` constrained to the five categories fact / preference / decision / project_status / relation.
- **On failure:** The user asks to add a field → only optional fields may be added, noted in the ADR; changing the semantics of existing fields is forbidden.

### Step 4: Read/Write Paths

- **Action:** Settle three things. Write timing (incremental extraction after each conversation turn — see memory-extractor; or batch write-back at session end — see the Claude memory tool's session-close write-back pattern). Load budget (the upper limit of core-layer injection per session, default empirical 2000 tokens, adjustable; the archival layer is injected based on retrieval results — see memory-retriever). Edit permissions (Letta-style agent self-editing of the core layer, or a controlled pipeline-only write — layers involving PII are always controlled).
- **Expected:** Write timing, the numeric load budget, and per-layer edit permissions all land in the ADR.
- **On failure:** The user asks for agent self-edit rights over PII entries → refuse and cite red line 2; offer the controlled alternative: the agent may raise a deletion request, executed by the pipeline.

### Step 5: Deliver the ADR and Initialize

- **Action:** Produce an architecture decision record (JSON style) and give storage initialization commands (e.g. `sqlite3 memory.db "CREATE TABLE memories (...)"` or the vector-database collection creation command).
- **Expected:** Each ADR decision has an id, the decision itself, the rationale, alternatives considered, and the reason for rejection; the initialization command runs directly.
- **On failure:** You cannot write the rationale for a decision → the decision is not thought through; go back to the corresponding step and redo it.

ADR output structure:

```json
{
  "project": "my-agent-memory",
  "date": "2026-09-16",
  "requirements": [{"kind": "preference", "lifespan": "long", "privacy": "pii-possible"}],
  "decisions": [
    {"id": "ADR-1", "decision": "Use SQLite FTS5 for the archival layer", "why": "Under 10k entries, no semantic search needed", "alternatives": ["plain files", "vector database"], "rejected_because": "File scanning degrades with scale; vector DB introduces embedding ops cost"}
  ],
  "forgetting": {"ttl_enabled": true, "decay_rule": "not hit for 90 days and confidence<0.7 is down-weighted"},
  "load_budget_tokens": 2000
}
```

## Parameter Quick Reference

| Parameter | Default | Notes |
|---|---|---|
| Core-layer load budget | 2000 tokens | Empirical, adjustable; if exceeded, the core layer is holding things that belong in archival |
| Single-entry TTL | 180 days | Empirical, adjustable; preference entries may be permanent, project-state entries recommended at 30–90 days |
| `confidence` initial value | Explicit fact 0.9 / inferred fact 0.6 | Aligned with memory-extractor's scoring rules |
| `type` values | 5 categories | fact / preference / decision / project_status / relation |
| Forgetting check frequency | Run alongside every write | May also be scheduled in batch; aligned with memory-manager's decay rules |

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| User insists "store everything in the vector DB" | Requirements profiling was skipped | Return to step 1, force out real needs by probing for readers; if still insistent, record the objection and proceed |
| After layering, the core layer does not fit | Retrieval-type memory wrongly placed in core | Move to archival; keep only identity and current goal in core |
| Downstream skills reject schema fields | Inconsistent with memory-extractor output | Reverse-revise the schema against memory-extractor's candidates.json fields |
| No vector DB but the user wants semantic search | Insufficient facilities | Design a degraded path: SQLite FTS5 + a keyword synonym table, and note the upgrade trigger in the ADR |
| Initialization command fails | Environment lacks SQLite or a vector DB | Drop one tier in the selection table and reissue the command; do not install heavyweight dependencies on the spot |
| Privacy requirements are unclear | The user has not assessed data sensitivity | Design to the highest privacy tier per red line 5, and mark "to be confirmed" in the ADR |

## Delivery Standards

- The five-row requirements table, layering mapping table, and storage selection conclusion are all present, with every decision traceable to a requirement.
- The frozen schema includes all required fields (id, content, type, user_id, created_at, updated_at, confidence, ttl, source, pii), with all field names in English.
- The ADR is valid JSON, containing the three blocks decisions, forgetting, and load_budget_tokens.
- The forgetting mechanism is explicit: at least one TTL rule and one down-weighting rule.
- The initialization command can be copied and run directly by the user.
- The PII handling path is verifiable: all related entries can be listed and deleted by user_id.

## References

- `references/sources-and-methodology.md` — read when you need to explain which projects the layered-memory, file-based-memory, and entry-based-memory methodologies come from and how to attribute them; also read before review to cross-check methodology provenance.

## Chain Position

- Upstream: `agent-designer` (after the agent's overall design is finalized, the memory architecture is a sub-design of it).
- Downstream: `memory-extractor` (extracts entries per this skill's schema) → `memory-manager` (manages lifecycles per this skill's forgetting policy) → `memory-retriever` (injects per this skill's load budget).
- This skill is the starting point of the memory-systems chain: the schema and forgetting policy are frozen here; the three downstream skills only execute and do not redesign.
