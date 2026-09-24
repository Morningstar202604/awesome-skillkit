# Sources & Methodology — memory-extractor

This skill's methodology is distilled from mem0's public practice, and is a **methodology distilled** result: it only borrows the extraction-stage flow and fact-splitting principles described in public docs; no source code was copied.

| Source project | License | What was distilled | Attribution |
|---|---|---|---|
| mem0 | Apache-2.0 | The extraction stage of the two-stage memory pipeline: extract candidate facts from the conversation, then hand to the update stage to compare against existing memory and decide ADD/UPDATE/DELETE/NOOP; the fine-grained fact principle—one memory = one independently standing fact | This skill's "candidate extraction → dedup comparison" two-step structure and compound-sentence splitting rules are derived from this; attributed in the upstream pack (memory-systems) and in this file |

## Distillation boundary (honest disclaimer)

- This skill covers only the extraction stage of mem0's two stages; the post-comparison storage decisions (ADD/UPDATE/DELETE/NOOP) belong to the sibling skill memory-manager in the upstream pack, corresponding to mem0's update stage.
- Confidence-scoring values (explicit 0.9 / inferred ≤ 0.7 / NO_DEDUP cap 0.8) are experiential values given by this skill's author, not derived from mem0, and can be calibrated to the business.
- Sensitive-category exclusion rules and the evidence_quote traceability requirement are engineering constraints added by this skill's author, not from mem0's original text.
- This skill is a methodology distillation, has no affiliation with mem0, and does not represent its official views.
