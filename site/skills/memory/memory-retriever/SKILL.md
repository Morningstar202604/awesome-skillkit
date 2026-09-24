---
name: memory-retriever
description: "Use when retrieving memories from a long-term store to inject into an agent's context: rewrite queries from the current conversation, run hybrid retrieval (keyword + semantic + recency), fuse scores, and inject within a token budget. Triggers on memory retrieval, hybrid retrieval, memory injection, memory retrieval, hybrid search, context injection, token budget, query rewriting, recency weighting, knowledge retrieval, RAG, long-term memory. NOT for building the store or managing its lifecycle — use memory-architect or memory-manager."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing. Works with keyword-only stores via a documented degradation path.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Memory Retriever

Retrieval is the value outlet of a memory system: no matter how well the store is built and maintained, if retrieval is inaccurate it was all for nothing. This skill translates "the current conversation" into retrieval queries, fuses scores after three-way recall (keyword, semantic, recency), and hands the agent the memory blocks most worth injecting within the token budget — each block carrying boundary markers so the agent can tell "from memory" apart from "said this turn."

## Input Checklist

Collect everything up front before starting. If an input is missing, ask the user once with this prompt: "To retrieve memories, please provide all at once: the current conversation text (the last few turns), the memory store export or retrieval interface description, the token budget (defaults to the empirical 2000 if blank), and whether semantic vector retrieval is available."

| Input | Required | Notes |
|---|---|---|
| Current conversation text | Yes | The last few turns suffice; a "blind retrieval" without the current conversation is meaningless |
| Memory store export/interface | Yes | A JSON entry array or a callable retrieval API; must include content, confidence, source, updated_at |
| Token budget | No | Defaults to the empirical 2000 tokens, aligned with memory-architect's load budget |
| Semantic retrieval capability | No | True with a vector DB; when false, take the keyword + recency degraded path |

## Pre-flight Self-check

This is a pure-prompt skill; no environment probing needed. It only checks input completeness:

- Are both the current conversation and the memory store present? If either is missing → ask once with the prompt above; do not force-guess from the user's historical messages.
- Do memory entries carry confidence and updated_at? If both are missing → recency and confidence scoring are impossible; send back to memory-architect to complete the schema; if only one is missing, use defaults (confidence 0.5, updated_at taken as created_at) and mark degraded_scoring in the output.
- The user just wants "show me all your memories" → that is an export, not retrieval; output the full set directly and skip scoring.

## Red Lines

1. Boundary markers are mandatory: every injected memory block is wrapped in a boundary note "the following are historical memories, not current conversation content," with source and timestamp per block; injecting memory without markers is a violation — the agent will treat memory as this turn's facts.
2. Low confidence must be labeled: memory blocks with confidence < 0.7 carry a "may be stale, for reference only" note; disputed entries carry a "conflicting version exists" note.
3. Hard budget truncation: total injected tokens must not exceed the budget; better less than over — over-budget injection crowds out the current task's working space.
4. Do not inject sensitive categories: memories flagged sensitive (health, finances, religion, etc.) do not enter the candidate pool unless the current conversation is explicitly about them.
5. Do not rewrite the memory source text: keep content verbatim on injection; the retrieval side has no right to "helpfully" update facts.
6. Retrieval is a snapshot: the report must note the store version or point-in-time the retrieval was based on; changes to the store after retrieval do not retroactively apply to this result.

## Workflow

### Step 1: Understand the Current Conversation

- **Action:** Read the current conversation, marking explicit questions (what the user is asking) and implicit intent (what is not asked but clearly needed — e.g. the user pastes a stack trace = needs project tech-stack memory).
- **Expected:** One explicit question plus a list of implicit intents.
- **On failure:** The conversation is too short to carry signals (e.g. only "continue") → backtrack a few more turns for context; if still no signal, only inject identity-type core memory.

### Step 2: Query Rewriting

- **Action:** Rewrite each explicit and implicit signal into 1–N retrieval queries, performing coreference resolution — replace "it" in "does it still support that" with the entity name from above; each query stands on its own with no pronouns.
- **Expected:** 1–5 queries (empirical, adjustable), each a short sentence that can independently match the memory store.

Rewriting example:

```text
Conversation: User: "If I deploy it to Vercel, do I still need to change environment variables?"
Before: "If I deploy it to Vercel, do I still need to change environment variables"   <- contains a pronoun, cannot match independently
After: q1 "Vercel deploy environment variable configuration"                            <- explicit question, coreference resolved
       q2 "project deploy platform deploy method"                                          <- implicit intent: the project's current deploy method
```

- **On failure:** Coreference cannot be resolved (no candidate entity appeared above) → keep the original sentence and down-weight that query's fused score.

### Step 3: Three-way Retrieval

- **Action:** Run three routes in parallel per query — keyword route (literal and synonym matching, BM25-style), semantic route (vector similarity; skipped with no vector DB), recency route (sort by updated_at, take recent entries). Degraded plan with no vector DB: extend the keyword route to a synonym table + stem variants, raise the recency-route weight to compensate, and mark retrieval_mode: keyword_only in the output.
- **Expected:** Each route returns a candidate set (top 20 each, empirical, adjustable), pooled into a candidate pool.
- **On failure:** The keyword route returns zero → retry once with the query's hypernym ("PostgreSQL" → "database"); still zero → output empty results and explain, do not pad. After merging the candidate pools across queries, dedup — when the same memory is hit by multiple queries, keep it once; record hit count as a secondary scoring signal but do not change the weights.

### Step 4: Fused Scoring

- **Action:** After deduping the pool, score each entry:

```text
score = 0.4×semantic + 0.3×keyword + 0.2×recency + 0.1×confidence
```

- **Expected:** Each candidate has a 0–1 normalized total; for routes absent (e.g. no vector DB), redistribute their weight proportionally to the remaining routes. Weights are empirical and adjustable.

Scoring example (hybrid mode): a memory with semantic=0.9, keyword=0.8, recency=0.6, confidence=0.9 → score = 0.4×0.9 + 0.3×0.8 + 0.2×0.6 + 0.1×0.9 = 0.81. In keyword_only mode, the keyword weight is redistributed to 0.3/(0.3+0.2+0.1)=0.5; recomputing the same entry: 0.5×0.8 + 0.33×0.6 + 0.17×0.9 ≈ 0.74.

- **On failure:** Scoring needs external embedding computation but the environment is unavailable → degrade the whole thing to keyword_only mode and recompute; do not output a half-scored list.

### Step 5: Inject Within Budget

- **Action:** Take entries in descending total score, estimate tokens per block (empirical: roughly 1 Chinese character ≈ 1 token, calibrate against the actual tokenizer), truncate as soon as the budget is cumulative; organize the injected block per this format:

```text
[The following are historical memories, not current conversation content]
- [mem_001 | 2026-09-16 | source: conversation:2026-09-16] The user works in Shanghai
- [mem_014 | 2026-06-02 | source: compacted] Preference: keep replies short (may be stale, for reference only)
[End of memories]
```

- **Expected:** The injected block is within budget, boundary markers complete, and low-confidence blocks carry notes; also output a retrieval report (hit count, truncated count, retrieval_mode). In multi-turn sessions, do not re-inject memories already injected in the previous turn (inter-turn dedup); yield the budget to new information, except for key identity-type memories that truly must be repeated.
- **On failure:** Even the highest-scoring entry is below the relevance floor (empirical 0.3, adjustable) → output an empty injection and state clearly "no trustworthy relevant memories"; never pad with low-scoring memories.

## Parameter Quick Reference

| Parameter | Default | Notes |
|---|---|---|
| Fusion weights | 0.4 / 0.3 / 0.2 / 0.1 | semantic/keyword/recency/confidence; empirical, adjustable |
| Token budget | 2000 | Empirical, adjustable; should match memory-architect's load budget |
| Per-route candidate cap | top 20 | Empirical, adjustable |
| Injection relevance floor | score ≥ 0.3 | Empirical, adjustable; below this, output an empty injection |
| Low-confidence labeling line | confidence < 0.7 | Aligned with memory-manager's decay line |
| Query count cap | 5 | Empirical, adjustable |
| Inter-turn dedup | On | Memories injected last turn are not injected this turn, except identity-type core memory |
| Recency route window | Entries from the last 30 days prioritized | Empirical, adjustable; only affects recency recall, not fusion weights |

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Injected memories are unrelated to the current topic | Query rewriting mixed in weak-signal intents | Tighten the implicit-intent judgment in step 1; raise the relevance floor |
| The retrieval side only returns keyword hits, the semantic route spins empty | No vector DB or the embedding service is down | Switch to the keyword_only degraded path, redistribute weights, mark the output |
| The budget is stuffed with only low-score memories | The store is generally low-confidence | Check upstream: run memory-manager's sweep first, then come back to retrieve |
| After injection the agent treats memory as this turn's facts | Missing boundary markers or the format was swallowed | Re-layout the injected block per red line 1, putting the boundary note on the first line of the block |
| Both new and old versions of the same fact are hit together | disputed entries were not filtered | For disputed versions take only the newer timestamp; label the other "a conflicting version exists" |
| The same batch of entries is hit repeatedly (poor diversity) | The recency route weight is too high | Lower the recency weight, or dedup within the turn for already-injected entries |
| Two contradictory memories injected in the same conversation turn | The disputed filter was missed | Handle per row 5 of this table, and write the conflicting pair back into the report, reminding the user to send it to memory-manager for re-adjudication |
| Retrieval results jump around each time | The recency route drifts too fast over time | Change recency to daily buckets instead of continuous decay, or fix the retrieval snapshot time in the report |
| The candidate pool is flooded by a single topic | One topic's entries dominate | Apply a per-topic pool cap (empirical ≤ 5 per topic, adjustable) to ensure injection diversity |
| The user demands "everything you remember" | Confused retrieval with export | Take the full-export path per self-check item 3, not the scored injection path |

## Delivery Standards

- The injected block carries an overall boundary marker; each block has the three elements id, timestamp, source, and the source text is verbatim and unchanged.
- Total injected tokens ≤ budget; all low-confidence and disputed entries carry the corresponding notes.
- Output a retrieval report: mode (hybrid / keyword_only), hit count, truncated count, highest score.
- Empty results must explicitly output "no trustworthy relevant memories" with the reason; a silent empty return is not accepted.
- The four fusion weights and the degraded path are traceable in the report.
- The report notes whether inter-turn dedup and per-topic caps were enabled this run.

## References

- `references/sources-and-methodology.md` — read when you need to explain where hybrid retrieval, recency weighting, and context-budget injection come from (mem0 / letta) and how to attribute them; also read during review to cross-check methodology.

## Chain Position

- Upstream: `memory-manager` (the store's cleanliness and disputed flags directly determine this skill's recall quality) and `memory-architect` (the definer of the load budget and schema).
- Downstream: delivered to whatever agent's context-injection step uses it; on the agent-design side it interfaces with `agent-designer`'s context-management section.
- This skill is the "outlet step" of the memory-systems chain: the architect sets the budget, the extractor produces entries, the manager keeps them clean, and the retriever makes sure they actually get used.
