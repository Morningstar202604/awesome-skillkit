# Sources & Methodology

- Skill: `skill-finder` (originally written for awesome-skillkit, Apache-2.0).
- Position: one of this repo's meta-skills; together with `skill-author` (generation) and `skill-linter` (validation) forms the scenario pack `Skill Forge`.

## Methodology borrowed (structural level only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Anthropic *Skill Authoring Best Practices* public doc | see original | "Metadata resident, body on demand" means retrieval should be name/description-primary, body-secondary—this skill's three-level weights come from this |
| agentskills.io open spec | see site | Skill discovery relies on the name + description routing mechanism, as the basis for scoring weight allocation |
| Community find-skills / skill-index tools | see respective repos | The minimal result form of "keyword → hit list + owning set + path"; this repo did not reference their implementation; weights, ranking, and output format are all self-defined |
| This repo's skill-listing script (`list_skills.py` under the repo root `tools/`) | Apache-2.0 (same repo) | Borrowed the output convention of "list skills grouped by category"; this script is an independent implementation, additionally providing retrieval scoring and pack matching |

## Originality statement

`scripts/find_skill.py`'s three subcommands, relevance weight table (name 5 / name-prefix extra 3 / description 3 /
pack description 2 / body 1), reproducible same-score sort by name ascending, `pack`'s intersection judgment and
ordering-priority heuristic (orchestration-first → script-bearing → pure-prompt), and `references/repo-map.md`'s
statistics methodology table are all designed from scratch for this repo. All skill data is read at runtime from
`manifest.json` and `skills/**/SKILL.md`; the script contains **no hardcoded skill list**—this is the prerequisite
for this skill to evolve in sync with the repo without code changes. No third-party SKILL.md, scripts, or documentation was translated, paraphrased, or excerpted.

## Merged adaptations to this repo's conventions

1. **Real data source first**: move the "skill list" completely out of code, switching to disk scan + manifest read,
   avoiding the list drifting from the repo;
2. **Explainable relevance**: give up vector retrieval, switch to weighted word frequency that can be recomputed item by item,
   so any ranking result can be manually verified—consistent with this repo's "determinism first" design axiom;
3. **Health check as a bonus**: `stats` additionally exposes orphan skills and dangling pack references,
   merging "repo inventory" and "data consistency alerts" into one call.

## License

This skill and its reference files are distributed under Apache-2.0; the upstream specs and documents listed carry their own license terms, which do not apply to this file.
