---
name: memory-extractor
description: "Use when turning a conversation or document into structured memory candidates: decide what is worth remembering, split facts to fine granularity, deduplicate, and score confidence. Triggers on memory extraction, conversation to memory, extracting memory entries, memory extraction, extract memories, conversation to memory, candidate extraction, confidence scoring, fine-grained facts, knowledge retrieval, RAG. NOT for storing, updating, or retrieving memories — use memory-manager or memory-retriever."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Memory Extractor

Nine out of ten things in a conversation are not worth remembering. This skill solves "what is worth remembering and how to record it cleanly": it extracts candidate memory entries from a conversation or document, splits each to fine granularity, deduplicates, and scores confidence, producing a machine-parseable candidates.json. It only extracts — it does not write to the store (that is memory-manager's job).

## Input Checklist

Collect everything up front before starting. If an input is missing, ask the user once with this prompt: "To extract memory entries, please provide all at once: the conversation or document text to extract from, the user_id the memories belong to, and an export of the existing memory store (for deduplication; skip dedup and mark NO_DEDUP if absent)."

| Input | Required | Notes |
|---|---|---|
| Conversation/document text | Yes | Full text or conversation log; secondhand "roughly what we talked about" paraphrases are not accepted |
| user_id | Yes | The owning subject; multi-user conversations must be labeled separately |
| Existing store export | No | Same-topic existing entries for dedup comparison; when absent, mark NO_DEDUP in the output |
| Schema constraint | No | If upstream memory-architect has frozen a schema, execute per its type enum |

## Pre-flight Self-check

This is a pure-prompt skill; no environment probing needed. It only checks input completeness:

- Are the source text and user_id both present? If either is missing → ask once with the prompt above; do not guess the ownership.
- Is the source text a paraphrase rather than the original record? Paraphrasing introduces the paraphraser's summarizing distortion → ask for the original; if you cannot get it, drop the whole output one confidence tier and mark `secondhand: true`.
- Existing store export is missing → proceed normally, but mark the final output NO_DEDUP and let memory-manager complete the dedup.

## Red Lines

1. Do not infer sensitive categories: health, finances, religion, political leanings, sexual orientation, and the like are never extracted unless the user **explicitly asks** to remember them in conversation — a passing mention like "I've been in chemo lately" is not an extractable memory.
2. Inferred entries must be flagged: any entry not directly supported by the user's own words but inferred from behavior or context gets confidence ≤ 0.7 and an `[inferred]` marker appended to the content.
3. evidence_quote must be a verbatim quotation from the source: any entry that cannot yield a verbatim quote is dropped; never fabricate evidence "from memory."
4. Do not extract one-off transactions: "book me a meeting room for Wednesday" is a schedule item, not a memory; writing it into the store only creates noise.
5. Do not rewrite the user's stance: the source saying "I don't want to use Vue for now" must not be extracted as "the user dislikes Vue."

## Workflow

### Step 1: Read Through and Segment

- **Action:** Read the source through and split it at topic shifts; tag each segment with a topic label.
- **Expected:** A segment list, each with a topic label and a line-number range traceable to the source.
- **On failure:** The source has no clear topic boundaries (e.g. a running log) → split mechanically at a fixed turn count (empirical: 10 turns per segment, adjustable).

### Step 2: Candidate Extraction

- **Action:** Scan each segment for four signal types, each with a standard prompt template:
  - fact: the user states something about themselves — "I work in Shanghai," "I write backends in Python."
  - preference: expresses likes/dislikes or requirements — "keep replies short," "no emojis."
  - decision: a call or choice made — "let's go with PostgreSQL," "no mobile for now."
  - project_status: progress and blockers — "the login module is live," "stuck on the payment callback."

  Discrimination prompt: is this statement still true six months from now? If yes → fact or preference; if it only describes a settled point in time → decision; if it describes "how far along things are" → project_status. Words like "like/hate/stop/try to" → prefer preference first.

- **Expected:** Each candidate has a source location (line number) and a category; vague sentences ("maybe," "probably") are demoted to pending.
- **On failure:** One sentence carries multiple signal types → split into multiple candidates and classify separately; do not cram them into one entry.

### Step 3: Fine-grained Splitting

- **Action:** Apply "one memory = one independently true fact" to every entry: split compound sentences ("the user works in Shanghai and has a cat" becomes two entries), split conditional sentences ("weekdays sleep early" and "weekends stay up late" are two entries).
- **Expected:** Each candidate stands on its own with no residual pronouns — replace "he" and "that company" with concrete referents.

Splitting example:

```text
Source: "The user does backend development in Shanghai, has a cat at home, and recently wants to replace the database from MySQL."
Split: 1) "The user works in Shanghai as a backend developer" (fact)
       2) "The user has a cat at home" (fact)
       3) "The user plans to replace the current database (currently MySQL)" (project_status)
```

- **On failure:** After splitting, an entry loses independent meaning → merge it back and note in granularity_note why it cannot be split.

### Step 4: Dedup and Confidence Scoring

- **Action:** Compare entry by entry against the existing store (semantic equivalence counts as duplicate, e.g. "I work in Shanghai" vs "my workplace is Shanghai"). Scoring rules: the user says it explicitly = 0.9; a preference repeated multiple times = 0.95; inferred from behavior = 0.6; inferred from a single indirect clue = below 0.6.
- **Expected:** Each candidate has a confidence value and its scoring rationale; duplicates are marked `duplicate_of` and carry the existing entry's id.
- **On failure:** Existing store is missing (NO_DEDUP mode) → skip comparison, cap confidence at 0.8 to leave room for later calibration.

### Step 5: Output candidates.json

- **Action:** Aggregate into a JSON array, field names all in English, with a one-line summary (counts per category, average confidence).

```json
[
  {
    "content": "The user works in Shanghai",
    "type": "fact",
    "confidence": 0.9,
    "evidence_quote": "I usually work here in Shanghai",
    "granularity_note": "Split from a compound sentence; the other entry is 'the user has a cat'",
    "user_id": "u_123",
    "duplicate_of": null
  }
]
```

- **Expected:** The JSON parses directly with `json.loads`; each entry has all four elements (content/type/confidence/evidence_quote).
- **On failure:** JSON validation fails → fix quote escaping and commas and re-emit; half-structured text is not allowed as delivery.

## Parameter Quick Reference

| Field/Rule | Value | Notes |
|---|---|---|
| `type` enum | fact / preference / decision / project_status | Signals outside the four are not extracted |
| Explicit fact confidence | 0.9 | Empirical, adjustable; multi-source repetition may rise to 0.95 |
| Inferred entry confidence | ≤ 0.7 plus `[inferred]` | Red line 2, cannot be raised |
| NO_DEDUP mode confidence cap | 0.8 | Empirical, adjustable |
| evidence_quote | Verbatim from source | Longest single sentence; cross-sentence quotes split into multiple entries |
| Topic segment length | 10 turns/segment | Empirical, adjustable |

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Extracted entries exceed the source's information content | Inferences written as facts | Check evidence_quote entry by entry; demote unsupported ones to inferred or delete |
| Sensitive categories appear in candidates | Passing mentions treated as explicit intent | Delete per red line 1; keep only when the user's own words contain "remember / note this" |
| Masses of duplicate candidates | The same preference emphasized repeatedly in conversation | Merge into one entry, confidence at 0.95 from multiple occurrences |
| Unsure of category assignment | The line between preference and decision is blurry | Look at tense: expressing likes/dislikes is preference, settling on a choice is decision; if still unsure, treat as preference and note it |
| Candidates far exceed the reasonable density for the conversation | Small talk and process chatter also extracted | Return to step 2 and re-screen with "is it still true in six months"; recommend no more than 10 candidates per conversation turn (empirical, adjustable) |
| evidence_quote is semantically disconnected from content | The source location was copied wrong | Re-paste line numbers and check each; drop entries that cannot be located per red line 3 |
| user_id confused across people | A group chat with no speaker labels | Stop extracting; ask for a source with speaker labels |
| JSON too long to maintain | One conversation produced too much | Output multiple arrays by topic segment, each independently parseable |
| Output entries are all trivial minutiae | Over-fine splitting | Stop splitting at "can stand independently"; do not split for splitting's sake; mark trivia `low_value` in granularity_note for memory-manager to down-weight |

## Delivery Standards

- candidates.json is a valid JSON array; each entry has the seven fields content, type, confidence, evidence_quote, granularity_note, user_id, duplicate_of.
- Each evidence_quote can be located verbatim in the source (line number preferred).
- Zero entries in sensitive categories; all inferred entries ≤ 0.7 and carry `[inferred]`.
- All compound sentences are split, with no residual pronouns.
- A summary line is attached: counts per category, average confidence, and whether NO_DEDUP applies.

## References

- `references/sources-and-methodology.md` — read when you need to explain where the fine-grained-fact principle and two-stage extraction flow come from (mem0) and how to attribute them; also read during review to cross-check methodology.

## Chain Position

- Upstream: `memory-architect` (the definer of the schema and type enum; this skill produces under its constraints).
- Downstream: `memory-manager` (receives this skill's candidates.json and executes ADD/UPDATE/DELETE/NOOP store decisions).
- This skill is the "entry step" of the memory-systems chain: output quality directly determines how clean the downstream store is; better fewer than sloppy.
