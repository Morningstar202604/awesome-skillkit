# Sources & Methodology

- Skill: `skill-linter` (originally written for awesome-skillkit, Apache-2.0).
- Position: one of this repo's meta-skills; together with `skill-author` (generation) and `skill-finder` (retrieval) forms the scenario pack `Skill Forge`.

## Methodology borrowed (structural level only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| agentskills.io open spec | see site | The frontmatter field set and name kebab-case constraint, as the judgment basis for `FM-FIELDS` / `NAME-SYNC` |
| Anthropic *Skill Authoring Best Practices* public doc | see original | "Description determines whether a skill is loaded," therefore routing information is made into a standalone `DESC-ROUTE` rather than merged into field checks |
| Community lint tools' public positioning notes (SkillCheck, etc.) | see respective repos | The "report + fix suggestion + exit code" output trio; this repo did not reference their rule implementations or code |
| This repo's repo-level validator (`validate_skills.py` under the repo root `tools/`) | Apache-2.0 (same repo) | Reused the parsing strategy of "minimal YAML subset parsing + fenced code block skipping," within-repo reuse; this script is an independent implementation, no code copied |

## Originality statement

`scripts/lint_skill.py`'s eight checks, judgment thresholds (220 lines / 0.15 CJK ratio / trigger words >=5 /
failure table >=4 rows), the `Finding` data structure, and the `FIX:` output format are all designed and implemented from scratch for this repo.
The edge-case table in `references/check-rules.md` comes from actual execution observation of this script, not cited from any external checklist.
No third-party SKILL.md, validation script, or its documentation was translated, paraphrased, or excerpted.

## Merged adaptations to this repo's conventions

1. **Dual-track gate**: this skill is positioned as the skill-level self-discipline line (stricter line count, more granular fix hints),
   coexisting with the repo-level validator (`validate_skills.py` under the repo root `tools/`); in conflict, the latter is the merge criterion;
2. **Executable**: downgrades "standards compliance," a subjective judgment, to eight deterministic predicates + one exit code,
   easy to hang into CI and pre-commit;
3. **Chinese-first**: adds the `LANG-CJK` check, corresponding to this repo's writing requirement of "body all Chinese, frontmatter machine layer English";
   this check has known false positives for pure-code skills, explicitly documented in `check-rules.md`.

## License

This skill and its reference files are distributed under Apache-2.0; the upstream specs and documents listed carry their own license terms, which do not apply to this file.
