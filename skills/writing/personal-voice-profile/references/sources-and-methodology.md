# Sources & Methodology — personal-voice-profile

This skill is a **methodology distillation**: the analysis framework comes from public stylometry and content style-guide practice; the field design and confidence constraints are the author's engineering decisions. It does not copy any project's source code.

## Methodology sources

| Source | License | What was distilled | Attribution |
|---|---|---|---|
| The voice vs tone distinction in public content style guides (common practice in free online guides such as the Mailchimp Content Style Guide) | Free public guide, conceptual citation | The tone-layer analysis framework: distinguishing "persona" (voice) from "scenario tone" (tone); this skill's tonal layer is organized accordingly, as are the observation dimensions for how readers are addressed and interjection habits | Noted in this file and in the SKILL.md tone-layer steps |
| The mainstream idea of stylometry: characterizing writing style via countable features | Mainstream academic concept, conceptual citation | The quantitative definitions for the lexical/syntactic layers: high-frequency words, median and variance of sentence length, punctuation frequency; the sentence-length definition stays consistent with ai-trace-auditor (effective character count) | This file declares it as a conceptual borrowing; it does not adopt the authorship-attribution conclusions |
| Online-writing-community discussions of the "author fingerprint" (inductive practice around verbal tics, structural templates, opening/closing habits) | Public community practice | The structural-layer dimensions (opening/closing/transition templates) and the example_snippets raw-sample design | This file declares it as community-practice induction |

## Distillation boundary (honest disclaimer)

- The minimum sample size (≥3 pieces) and the rule that "every conclusion must attach raw-text evidence" are this skill's author's engineering constraints, not from the sources above; the stylometry field has no conclusion directly corresponding to "minimum sample size" for this scenario.
- This skill only does a **descriptive profile**, not authorship identification; it cannot be used to judge whether a given text "was written by so-and-so" — this boundary pairs with red lines 2 and 3.
- The JSON field structure (lexical/syntactic/tonal/structural/example_snippets) is this skill's custom spec and has no compatibility with any external product.
- This skill is a methodology-distillation product, has no affiliation with the guides and communities cited above, and does not represent their original authors' views.
