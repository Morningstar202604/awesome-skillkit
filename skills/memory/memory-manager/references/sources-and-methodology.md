# Sources & Methodology — memory-manager

This skill's methodology is distilled from the public practices of mem0 and letta (MemGPT), and is a **methodology distilled** result: it only borrows the update-stage decisions and memory self-editing ideas described in public docs; no source code was copied.

| Source project | License | What was distilled | Attribution |
|---|---|---|---|
| mem0 | Apache-2.0 | The update stage of the two-stage memory pipeline: after newly extracted candidates are compared against existing memory, storage happens via four operations ADD / UPDATE / DELETE / NOOP | This skill's step 2 conflict-resolution decision table and step 3 four-operation execution are derived from this; attributed in the upstream pack (memory-systems) and in this file |
| letta (MemGPT) | Apache-2.0 | The agent self-editing mode for core memory: when the agent rewrites its own memory block, it **rewrites rather than appends** to the whole block, preventing context bloat | This skill's UPDATE "rewrite, don't append" principle and changed_from evolution-note design are derived from this; attributed in the upstream pack and in this file |

## Distillation boundary (honest disclaimer)

- Specific values for TTL, usage-frequency decay, and topic compression (90 days, 0.7, ×0.8, 10 entries) are experiential values given by this skill's author, not derived from the above projects, and can be adjusted to business load.
- Audit-log requirements, GDPR-style deletion rights, and the disputed flag are engineering and compliance constraints added by this skill's author, not from mem0 / letta's original text.
- This skill is a methodology distillation; it is not affiliated with the projects above and does not represent their official views.
