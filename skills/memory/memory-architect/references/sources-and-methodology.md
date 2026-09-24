# Sources & Methodology — memory-architect

This skill's methodology is distilled from the public practices of three projects, and is a **methodology distilled** result: it only borrows the design ideas and layering concepts described in public docs; no source code was copied.

| Source project | License | What was distilled | Attribution |
|---|---|---|---|
| mem0 | Apache-2.0 | A memory entry = a natural-language fact + structured metadata (user_id, timestamp, run_id), not a bare embedding; the ideas of entry-based storage and per-user isolation | This skill's schema template fields user_id / source / confidence are derived from this; attributed in the upstream pack (memory-systems) and in this file |
| letta (MemGPT) | Apache-2.0 | Layered memory: core memory (resident context, agent self-editable) / archival memory (persistent store, retrieved on demand) / recall memory (conversation-history index); the memory-pressure concept | This skill's "step 2 layered design" three-layer table and core-layer edit-permission discussion are derived from this; attributed in the upstream pack and in this file |
| Claude memory tool | per Anthropic official doc terms | File-based memory: MEMORY.md index + per-topic split files, loaded at session start, written back at end | This skill's storage-selection table "pure files" option and session-close writeback mode are derived from this; attributed in the upstream pack and in this file |

## Distillation boundary (honest disclaimer)

- This skill is a methodology distillation; it is not affiliated with the projects above and does not represent their official views.
- The three-axis storage-selection table and specific thresholds (2000 entries, 2000 tokens, etc.) are experiential values given by this skill's author, not derived from the above projects, and can be adjusted to actual load.
- The original projects' specific implementation details (e.g. mem0's vector-index parameters, letta's memory-page scheduling) are out of scope for this skill.
