# Sources & Methodology — ai-trace-auditor

This skill is a **methodology distillation**: the detection principles and word list come from public literature and community induction; the scoring weights are the author's engineering rules of thumb. It does not copy any project's source code or any paid detector's output.

## Methodology sources

| Source | License | What was distilled | Attribution |
|---|---|---|---|
| Perplexity and burstiness concepts in public LLM literature | Conceptual citation (mainstream academic concept) | Detection principle: human writing has less predictable vocabulary and larger sentence-length variance; this skill uses the sentence-length variance ratio cv = std/mean (alert line 0.5) and word-list hit rate as cheap proxies for the two | The principle source is noted in this file and in the SKILL.md parameter quick-reference |
| Public community compilations of high-frequency LLM words (e.g. the English lists "delve / tapestry / crucial / moreover / it's important to note", and the Chinese list "empower / lever / closed loop / it's worth noting") | Public community discussion, no single copyright holder | The AI_PATTERNS word list: 29 built-in Chinese/English regexes, each with a revision suggestion; the list can be trimmed as needed | This file declares the list as community induction + author additions |
| Common structural templates in journalism and writing teaching (three-point lists, summary-sentence openings, official-style closers) | Conceptual citation | The semantic-layer manual checks in step 4 and the findings' type enum design | This file declares them as common writing-teaching experience |

## Distillation boundary (honest disclaimer)

- This skill is **not** a complete perplexity/burstiness implementation: there's no language-model scoring, only statistical proxies, so it has blind spots to new AI clichés outside the word list — this boundary is written into SKILL.md red line 1.
- The scoring weights (each hit −6 points, cv alert line 0.5, list-density alert line 0.4, etc.) are all the author's rules of thumb, not from any literature; they can be calibrated per use case, and correspond one-to-one to the constants in scripts/trace_scanner.py.
- No affiliation or data relationship with any commercial AI detector (e.g. GPTZero, Originality, etc.); scores and their conclusions are not interchangeable.
- This skill is a methodology-distillation product and does not represent the official views of the communities or literature cited above.
