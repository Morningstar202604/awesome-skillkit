# Sources & Methodology — memory-retriever

This skill's methodology is distilled from the public practices of mem0 and letta (MemGPT), and is a **methodology distilled** result: it only borrows the retrieval ideas and injection patterns described in public docs; no source code was copied.

| Source project | License | What was distilled | Attribution |
|---|---|---|---|
| mem0 | Apache-2.0 | Memory retrieval returns structured entries (natural-language fact + metadata) as the unit, not bare embedding chunks; entry-level confidence and source traceability | This skill's injection-block source/timestamp elements and confidence annotation line are derived from this; attributed in the upstream pack (memory-systems) and in this file |
| letta (MemGPT) | Apache-2.0 | Layered retrieval and context-pressure management: retrieve and inject from the archival layer on demand, control injection volume to leave room for working memory; separate conversation history (recall) from knowledge memory | This skill's token-budget hard cutoff and "memory-block boundary markers" design are derived from this; attributed in the upstream pack and in this file |

## Distillation boundary (honest disclaimer)

- The hybrid-retrieval fusion formula and weights (0.4 semantic / 0.3 keyword / 0.2 recency / 0.1 confidence), top-K, and relevance floor are experiential values given by this skill's author, not derived from the above projects, and can be calibrated to the business.
- BM25 and vector recall are industry-standard retrieval techniques, not proprietary methodology of any single project.
- Query rewriting and coreference resolution are engineering practices added by this skill's author; the keyword_only degradation path is a no-vector-store solution designed by this skill's author.
- This skill is a methodology distillation; it is not affiliated with the projects above and does not represent their official views.
