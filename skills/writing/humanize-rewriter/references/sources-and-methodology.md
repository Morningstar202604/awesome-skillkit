# Sources & Methodology — humanize-rewriter

This skill is a **methodology distillation**: the rewriting techniques come from mainstream public concepts in writing teaching and language statistics; the do-not-change list and re-check threshold are the author's engineering constraints. It does not copy any project's source code.

## Methodology sources

| Source | License | What was distilled | Attribution |
|---|---|---|---|
| Burstiness and perplexity concepts in public LLM literature | Conceptual citation (mainstream academic concept) | The quantitative target for burstiness injection: human writing has larger sentence-length variance, so the executable rule is "after two consecutive long sentences, follow with one short sentence of ≤8 characters", with cv ≥ 0.5 as the re-check threshold (aligned with ai-trace-auditor's alert line) | Noted in this file and in the SKILL.md workflow |
| The "show, don't tell" principle common to journalism and creative-writing teaching | Conceptual citation (mainstream writing-teaching principle) | The concreteness upgrade technique: abstract generalization → concrete nouns/numbers/scenarios; first-person reactions and asides in emotional injection | This file declares it as common writing-teaching experience |
| Colloquial habits in online writing and personal-blog practice (parentheticals, dash detours, rhetorical questions, deliberate imperfection) | Public community practice | The concrete list of "imperfection allowed" techniques and the restraint principle of "one instance is enough; don't pile them up" | This file declares it as community-practice induction |

## Distillation boundary (honest disclaimer)

- The technique rules (≤8-character short sentences, cv ≥ 0.5, re-check drop ≥20 points, etc.) are all the author's rules of thumb and can be calibrated by genre; they are not experimental conclusions from any literature.
- The "do-not-change list" (numbers, terms, conclusions, citations frozen) is a safety constraint added by this skill's author, not from the sources above — it's an engineering guardrail against "human warmth" damaging information integrity.
- This skill explicitly makes **no promise** to lower any commercial AI detector's score; the correspondence at the detection-principle level (sentence-length variance, lexical predictability) is only a heuristic proxy, written into red line 4.
- This skill is a methodology-distillation product, has no affiliation with the writing-teaching traditions cited above, and does not represent their original authors' views.
