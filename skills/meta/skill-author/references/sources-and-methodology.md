# Sources & Methodology

- Skill: `skill-author` (originally written for awesome-skillkit, Apache-2.0).
- Position: this skill is one of this repo's **meta-skills**, and together with `skill-linter` (validation) and `skill-finder` (retrieval) forms the scenario pack `Skill Forge`.

## Methodology borrowed (structural level only; no text copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Anthropic *Skill Authoring Best Practices* public doc | see original | The three-layer progressive disclosure of "metadata resident → body activated → resources on demand"; the core conclusion that description determines whether a skill is loaded |
| agentskills.io open spec | see site | The frontmatter field set (name / description / license / compatibility / metadata) and the name kebab-case constraint |
| SkillsBench public empirical findings | see paper | "Monolithic kitchen-sink" skills score significantly worse; one scenario per skill; skill granularity should map one-to-one with trigger phrases |
| OpenAI skill-creator public docs | see repo | The order discipline of "clarify requirements before writing": do not produce files directly when requirements are unclear |

All the above sources are restated as a **methodology skeleton**: this skill's five-question clarification template,
ten-commandment checklist, four skeleton variants table, and
`references/skill-template.md` are all written from scratch—no upstream passages or examples were translated, paraphrased, or excerpted.

## Merged adaptations to this repo's conventions

1. **Ten commandments inline**: this repo's skill-authoring standard (SKILL-STANDARD-v2 under the repo root `docs/`) §3's ten writing commandments are inlined into the body as a table,
   each with a "what counts as a violation" criterion, so authors need not jump to external docs;
2. **Machine-layer English / human-layer Chinese separation**: frontmatter and code stay in English, body in Chinese,
   aligned with this repo's trigger-word engineering requirement of "Chinese users are the main force";
3. **Verifiability**: self-check steps are changed to executable commands (`lint_skill.py` + `wc -l` + `grep -c`),
   downgrading "is it well written" to "do the checks pass."

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
