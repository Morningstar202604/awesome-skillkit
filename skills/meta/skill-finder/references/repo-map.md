# Repository Map and Statistics Methodology

This file explains what the world looks like to `find_skill.py`: which directories are scanned, what is skipped,
and how each number in `stats` is computed. **Read this when interpreting statistics or when "a skill should exist but I can't find it."**

## Table of Contents Map

```
awesome-skillkit/
├── manifest.json          # the single authoritative manifest: hub / version / packs[]
├── packs/<pack-id>/pack.json   # member skill name list per pack (mirrored with manifest)
├── skills/                # the skills themselves, one top-level directory per category
│   ├── meta/              # meta-skills (where this skill lives, Skill Forge scenario pack)
│   ├── programming/       # software development, split into 19 second-level domains
│   ├── video/  ppt/  office/  paper/  audio/  design/  education/
│   ├── writing/           # content publishing, split into blog/ community/ news/ social/ video/
│   ├── marketing/  memory/  chat/  scenarios/
│   └── _common/           # cross-skill shared modules, not skills
└── tools/                 # repo-level gates and build scripts, not skills
```

## What counts as a "skill"

Scan rule: `skills/**/SKILL.md`, at **any depth** (the common publishing-skill
`skills/writing/…/csdn-publisher/SKILL.md` three levels deep is treated the same as `skills/video/video-generation/SKILL.md`
two levels deep).

`SKILL.md` under the following paths is **skipped**, because these are not the skill itself:

| Path fragment | Why skipped |
|---|---|
| `assets/` | The skill's own example projects, e.g. `skills/programming/ai-engineering/skill-tester/assets/sample-skill/SKILL.md` |
| `templates/` | Template files, not loadable skills |
| `_common/` | Cross-skill shared code directory |
| `__pycache__/` | Compiled artifacts |

Therefore the skill count in `stats` will be a few less than the raw count from `find skills -name SKILL.md`;
the difference is these categories above. The two not matching is not a bug.

## Where each field comes from

| Field | Source | When missing |
|---|---|---|
| `name` | SKILL.md frontmatter `name` | falls back to directory name |
| `description` | frontmatter `description` | empty string; during retrieval the skill can only be hit by name and body |
| `category` / `tier` | frontmatter `metadata.*` | bucketed into "(unlabeled)" |
| `title` | The first `# ` H1 heading in the body | empty string |
| `summary` | The first non-heading, non-blank, non-code-block paragraph, truncated to 80 chars | falls back to `title` |
| `has_scripts` | Whether a `scripts/` subdirectory exists under the skill directory | boolean, no fallback needed |
| `has_references` | Whether a `references/` subdirectory exists | same as above |
| Owning pack | Reverse index from `manifest.json`'s `packs[].skills[].name` | empty list → counted as orphan |
| Pack Chinese name | `packs[].name_zh` | falls back to pack id |

Body and description are both matched after `lower()`, so `PDF` and `pdf` are equivalent;
Chinese is unaffected by case and is matched by direct substring.

## `stats` calculation methodology

| Metric | Algorithm |
|---|---|
| `skills_on_disk` | Number of skill records scanned (example directories skipped per the rules above) |
| `packs` | Length of `manifest.json`'s `packs` array |
| `skills_referenced_by_packs` | Size of the **deduplicated** set of all pack member skill names |
| `skills_with_scripts` | Number of skill directories containing `scripts/` |
| `by_category` | Count by `category`; unlabeled bucketed into "(unlabeled)" |
| `by_tier` | Same, count by `tier` |
| `orphan_skills` | On disk but not in any pack's `skills[].name` → WARN-level issue |
| `pack_references_missing_on_disk` | Referenced by a pack but not found on disk → ERROR-level issue (repo gate will block) |

`skills_on_disk` is usually slightly larger than `skills_referenced_by_packs`: the difference is orphan skills
or newly added skills not yet packed. When both are equal and both warning lists are empty, packs ↔ disk are fully consistent.

## Troubleshooting order when a skill can't be found

1. **Keyword too narrow**: first use `stats` to see the category distribution, then search by category name;
2. **Misremembered skill name**: skill names in this repo are all kebab-case, no spaces, no capitals,
   e.g. `video-generation` not `Video Generation`;
3. **The skill is in `assets/`**: that's an example, not a loadable skill—being unsearchable is expected behavior;
4. **The skill is on disk but not in `manifest.json`**: `search` can still hit it (it scans disk),
   but `pack` will tell you it doesn't belong to any pack;
5. **The skill is only in `manifest.json`**: `search` won't hit it, and `stats` will list it in
   `pack_references_missing_on_disk`—this is a data error that needs fixing.

## Weight design trade-offs

Name weight (5) is far higher than body (1) because the skill name itself is a human compression:
the author already compressed "what this skill does" into a few words when naming it. Description weight (3)
corresponds to the mechanism of "the model decides whether to load based on name+description alone."
Pack-description hits are worth +2 and counted once per skill, so that "the whole pack is relevant" cases float up,
while preventing 20 skills in the same pack from inflating each other's scores via pack description and drowning out the truly hit one.
