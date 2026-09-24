---
name: article-outliner
description: "Create article outlines: structure, section hierarchy, key points, and reading flow. Supports blog posts, technical articles, news, listicles, and opinion pieces. Also audits an existing draft's structure with reverse outlining, and de-duplicates listicle entries (MECE check). Use when the topic is defined but structure is needed before drafting, e.g. building an article outline / listing an outline / planning structure / help me organize the article framework / check whether the article structure has problems. Do NOT use for writing full prose (outline only — use article-drafter for that), nor for line-level editing of a finished draft (use content-editor)."
license: Apache-2.0
compatibility: "Pure prompt-based structuring. Optional scripts/outliner.py is a deterministic skeleton generator (Python 3.8+, stdlib only) — it emits template headings and field scaffolding, NOT content; the real outlining work happens in prompt mode. No API keys required."
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-22"
---

# Article Outliner (Lock the Structure Before You Write)

This skill produces a **structure contract**: each section's claim, key points, word-count budget, and inter-section relationships. It does not produce body text.

The outline is the only thing in the whole article with the "lowest change cost" — deleting a section on the outline takes 10 seconds; deleting a section in the finished draft takes 2 hours. This skill's entire design revolves around that point.

## Applicability Decision Table

| Your Situation | Where This Skill Sits | Go To |
|----------|--------------|------|
| Topic in hand, structure not settled | yes, write mode: produce the outline | this skill |
| Draft exists, suspect structure is off | yes, audit mode: reverse-outline checkup | this skill, Workflow B |
| Listicle entries look overlapping/padded | yes, the MECE three-check | this skill, tacit knowledge 3 + verification steps |
| Structure settled, need to write the body | out of scope | article-drafter |
| Body exists, need to cut words / remove AI tone | out of scope | content-editor |
| The title can't extract a question word (topic not converged) | note: converge first — add a question word before starting | references/outline-templates.md section 1 judgment method |
| Just want a title/hook, no structure | yes, light mode: deliver title/hook only, skip section design | this skill |

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| `topic` | yes | Article topic, e.g. `FastAPI performance optimization` |
| `type` | no | `technical` / `blog` / `news` / `listicle` / `opinion` / `tutorial`, default `technical` |
| `target_length` | no | `short(800)` / `medium(2000)` / `long(5000)`, default `medium` |
| `audience` | no | `beginner` / `intermediate` / `expert`, default `intermediate` |
| `key_points` | no | Key-point list, e.g. `["async","caching","DB indexing"]` |
| `platforms` | no | Target platforms, e.g. `["csdn","juejin","wechat"]` |

**Extract first, then judge what's missing**: the user's information often comes in natural language/prose rather than field format — "I listed 7 items: write type annotations, use lint, ..., help me build the outline" has already given both `topic` and `key_points`. **First extract the prose into fields; only what's still absent after extraction counts as missing**; judging information already in hand as "missing" and asking the user to resend = a delivery failure (`key_points` is "nullable" anyway and is never a blocker).

Only when `topic` is still missing after extraction do you ask everything at once: "Please provide: ① topic; ② article type (technical/blog/news/listicle/opinion/tutorial); ③ target length; ④ target audience; ⑤ key points (nullable). Otherwise defaults: type=technical, target_length=medium, audience=intermediate."

## Pre-flight Checks

1. **Topic-convergence check**: pull the question word out of the title — "how to" -> tutorial, "should we / really?" -> opinion, "which / several" -> listicle, "why it failed / how to recover" -> blog (retrospective), "vs / compare" -> technical (review). Can't extract a question word = the topic hasn't converged; add a question word before starting.
2. Verify the script works (optional, deterministic skeleton):
   ```bash
   python3 scripts/outliner.py --topic "FastAPI performance optimization" --type technical --output outline.json
   ```
   Expected: exit code `0`, generates `outline.json` with `sections[]` and each section's `word_count_target`.
3. **`--type` accepts only the 6 enum values.** Passing another value -> argparse errors out directly (rc=2); it does **not** auto-fall-back to `technical`; if you want the default, don't pass the parameter.
4. Pure prompt mode can skip Step 2 and go straight to Workflow A.

## Tacit Knowledge (What Determines Whether the Outline Is Usable)

### 1. Every Section Must Answer the Question the Previous One Raised

The Minto Pyramid's Q&A chain: between two adjacent sections you must be able to insert "after reading the previous section, what does the reader naturally ask?" — if the next section can't answer it, it doesn't belong in this article (either add a transition or move it out).

**Mechanical self-check**: cover all headings, read only the two adjacent sections' point lists, and see whether you can tell "why the next section has to exist." Can't tell = a logic gap.

### 2. "Conclusion First vs. Suspense Buildup" Is Set by the Reader's Situation, Not a Style Preference

Readers arriving from search (time pressure, ready to leave) -> conclusion first; readers pulled in by a recommendation feed (already decided to read) -> suspense buildup. **A hybrid is the default best**: give the directional conclusion, leave detail as suspense. The full decision table and hybrid phrasing are in `references/flow-guide.md` section 2.

### 3. MECE Only Holds for Inventory-Type Outlines

MECE (mutually exclusive, collectively exhaustive) is a check tool for "lists/inventories": entries share a dimension, don't overlap, and cover the main categories. **Forcing MECE onto narrative and opinion pieces tears the argument apart** — Minto herself stated in the original book that the framework doesn't apply to open-ended exploration, and MECE is hard to achieve fully in practice. So: check it for listicles, don't check it for technical/opinion.

### 4. When a Heading Contains "and / plus / as well as", It's Usually Two Sections Crushed Into One

A section's pass criterion is "can state its core work in one sentence." `Performance optimization and deployment practice` can't -> split into two sections, or pick one of the two in the heading.

### 5. title and hook Serve Two Different Audiences

| Field | Serves | Optimization Goal | Common Mistake |
|------|----------|----------|----------|
| `title` | people who haven't clicked in yet (search/feed) | get selected: concrete object + verifiable information | writing it as an internal codename or "Intro to XX" |
| `hook` | people who already clicked in | keep them: create an information gap/tension | repeating the title, or a generic question like "have you hit X pain points?" |

Writing the two as one field gives a title that's both long and flat.

### 6. The Word-Count Budget Is an Anti-Squeezing Device, Not a Quota

`word_count_target`'s job is to prevent one section from swelling and eating the others' space (especially the "background" section in technical articles). In actual writing, word count is a result. If one section's budget is 3x another's, first ask "what justifies that" — if you can't answer, it's structural imbalance.

### 7. With an Existing Draft, Use "Reverse Outlining" to Check the Structure

Reverse-extract "what each section actually says" (not what the heading claims it says) from the draft, and compare against the title/opening promise. Three high-frequency problems: one section doing two things; a section whose removal leaves the article intact (= an irrelevant digression); the ending conclusion not matching the opening promise. In academic writing teaching this is called reverse outlining, the standard structural checkup technique.

### 8. CTA Varies by Platform, But the Script Only Produces One `conclusion` Field

CSDN/Juejin's interaction is likes and saves, WeChat Official Accounts is "wow/forward", Zhihu is "upvote", Bilibili is "triple-tap". **When cross-posting, write a conclusion per platform** — the script's single field is a skeleton, not a finished product (see Honest Disclosure).

## Red Lines (Hard Bans)

1. **Don't fabricate data and sources**: numbers in the outline like "10x performance improvement" or "90% of developers" must have a citable source; if not, rephrase qualitatively or mark "data to be added".
2. **Don't pad listicles**: a 7-item title means 7 items; padded entries dilute the whole piece's credibility — better to change the title to 5 items.
3. **Don't hand the user's raw material back as-is**: `key_points` are raw material that must be processed into writable claims (with criteria/actions/quantified goals); a bare list equals no outline done.
4. **Don't overstep into body text**: this skill delivers structure; writing paragraphs infringes on article-drafter's job and deprives the user of their checkpoint to review the structure.
5. **Don't promise writing quality**: a qualified structure != a good article. At delivery you must state that quality still depends on body writing and material quality.

## Honest Disclosure (The Script Mode's Actual Behavior)

`scripts/outliner.py` is a **deterministic skeleton generator**, not an "AI outline". The following behavior was verified by actual run on 2026-09-22:

1. **Section headings come from a fixed template table**: `technical` -> `Problem Background / Cause Analysis / Solution / Comparative Test / Summary`. These headings are **topic-agnostic**, skeleton slots that must be rewritten per the corresponding template in `references/outline-templates.md`.
2. **`title` / `hook` / `conclusion` are placeholder text**: respectively `{topic}: From Beginner to Pro`, "Have you hit pain points related to {topic}?", and the literal string `summarize key points + CTA`. All three must be rewritten (tacit knowledge 5, 8).
3. **`points` are carried over from `--points`**: each point goes into one section; when points exceed sections they're round-robined (no point dropped); sections with no provided points get an empty points array.
4. **`word_count_target` is divided evenly across sections** (remainder pushed to the earlier sections), ignoring content weight; the sections' sum always equals `total_words_target`.
5. **`reading_time_min` = `total_words_target // 250`** (250 words/min is the conventional English reading-speed figure). Chinese reading is usually faster, so this field is **conservative for Chinese content** (overestimates reading time).
6. **Illegal `--type` value -> argparse error exit rc=2**, no auto-fallback.
7. The script only produces a single-level `level: 2` structure, no third-level headings; it doesn't validate whether `type` matches the content.

> For probe records and the full field list, see `references/sources-and-methodology.md`.

## Workflow A: write Mode (Build an Outline From Scratch)

### Step 1: Converge the Topic, Reader, and Medium
Per pre-flight check 1, set `type`; set `audience` and `platforms` (which decide conclusion-first vs. CTA form).
Expected: `type` / `audience` / `platforms` all clear. If it fails: `audience` unclear -> use `intermediate` and note it at delivery.

### Step 2: Pick the Template Skeleton
Read `references/outline-templates.md` section 1 quick reference, pick one of A technical tutorial / B opinion commentary / C list inventory / D case retrospective / E review comparison, and take that template's "parts x role x word share x required elements" table.
Expected: one template and its word share selected. If it fails: can't extract a question word -> return to pre-flight check 1.

### Step 3: Write Each Section as a Claim + Points
Rewrite each h2 into a **claim** (not "what is X" / "overview"); each section has 2-5 points, and points must be concrete and actionable (with actions/criteria/quantified goals).
Expected: one claim + 2-5 points per section. If it fails: a section can't produce a claim -> it may be two sections; split per tacit knowledge 4.

### Step 4: Mark Inter-Section Relationships
For each adjacent pair of sections, label the relationship type (progression/contrast/parallel/cause-effect/example/problem-solution), producing a `link_to_prev` field; an adjacent pair you can't label = a logic gap.
Expected: no unlabelable adjacent pairs. The full relationship table and test questions are in `references/flow-guide.md` section 3.

### Step 5: Allocate the Word-Count Budget
Allocate each section's `word_count_target` per the template's shares, replacing the script's even split (the script's even split is an information-free default).
Expected: sections sum to `total_words_target`; the body (argument/steps/entries) >= 55%, background setup <= 15% (both are empirical values from `references/outline-templates.md`, not platform rules).

### Step 6: Write title / hook / conclusion
Write title and hook per tacit knowledge 5's division of labor; conclusion gives a concrete CTA per platform (tacit knowledge 8).
Expected: title contains a concrete object and verifiable information; hook creates an information gap within 2 sentences; conclusion has a concrete action.

### Step 7: Run the Built-in Verification
Check off the "Built-in Verification Steps" below one by one; in script mode, also check per Honest Disclosure 1-4 whether the placeholder fields have been rewritten.

## Workflow B: audit Mode (Reverse-Outline Checkup)

1. **Reverse extraction**: read the draft and condense what each section "actually says" (not what the heading claims), presenting it as a list.
2. **Three checks**: ① which sections are doing two things (-> split suggestion); ② which sections leave the article intact if deleted (-> irrelevant digression, suggest deletion); ③ whether the heading, opening promise, and ending conclusion all point to the same thing (-> conclusion drift; fix the ending, not the opening).
3. **Output a diagnosis table**: `section -> actual claim -> problem type -> remedy`. Logic-gap types and fix priority are in `references/flow-guide.md` section 5.
4. **Don't rewrite the body**: only give structural remediation suggestions; line-level rewriting goes to content-editor.

## Structure-Pattern Table

| Pattern | When to Use | Sections | Key Risk |
|------|--------|------|----------|
| Problem -> Solution | technical articles, fault retrospectives | 3-5 | the background section swells and eats the body budget |
| Listicle | tips, resource inventories | N items + intro + outro | entries on different dimensions/padded (must check MECE) |
| Tutorial | how-to guides | steps 1-N + prerequisites + result | uneven step granularity (one command vs. a whole chapter) |
| News | announcements, updates | what -> why -> how -> impact | burying the most important info (inverted pyramid fails) |
| Opinion | commentary, opinion pieces | claim -> evidence -> counter-argument -> conclusion | strawman counter-argument; conclusion drift |

## Built-in Verification Steps (Check Each Before Delivery)

- [ ] **Q&A chain test**: cover the headings, read only adjacent sections' points; you can answer "why does the next section have to exist"
- [ ] **Claim test**: every h2 can be rewritten into a claim
- [ ] **MECE three-check** (listicle only): same dimension, no overlap, exhaustive coverage explained
- [ ] **Consistency test**: title / hook / conclusion point to the same thing
- [ ] **Word-count test**: sections' `word_count_target` sum = `total_words_target`
- [ ] **Placeholder cleared** (script mode): template headings and the title/hook/conclusion placeholder text all rewritten

Full criteria (including body-share and counter-argument-share requirements) are in `references/outline-templates.md` section 7 and `references/flow-guide.md` section 6.

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|-------------|------|------|
| "Need --topic or --json-input" | Missing topic | Add `--topic` or provide a topic field in `--json-input` |
| argparse `invalid choice` (rc=2) | Illegal `--type` value | Use one of the 6 enum values; the script won't auto-fall-back |
| A section's points are empty | No `--points` given or fewer points than sections | Hand-write points per Workflow A Step 3; don't leave empty sections |
| Heading contains "and / plus" | Two sections crushed into one | Split per tacit knowledge 4, or pick one |
| Adjacent sections can't get `link_to_prev` labeled | Logic gap | Add a transition or reorder per flow-guide section 3 |
| Listicle entries are interchangeable without affecting understanding | True parallelism (acceptable); if not interchangeable | Not interchangeable = hidden dependency; relabel as progression |
| Ending conclusion != opening promise | Conclusion drift | Fix the ending callback (don't change the opening, flow-guide section 5) |
| User wants "professional feel" but the points are all empty talk | Material insufficient to support the structure | Say plainly: the outline can't fill a material gap; supplement material first |

## Delivery Standard

- Produce an `outline` object: `title` / `hook` / `sections[]` (each with `id` / `heading` / `level` / `points` / `word_count_target`) / `conclusion` / `total_words_target` / `reading_time_min`.
- `sections` length in [3,7] (listicle allows 7+2); each section's `points` 2-5.
- Sections' `word_count_target` sum = `total_words_target`.
- Tabular delivery must also give the `link_to_prev` annotation column.
- In script mode additionally verify: template headings and placeholder text have been rewritten (Honest Disclosure 1-2).
- In audit mode produce a structure diagnosis table, without editing the body.

## References

- `references/outline-templates.md` — 5 Chinese outline templates (selection quick reference / word shares / required elements / pass criteria section 7). Required reading for Workflow A Step 2 and before delivery.
- `references/flow-guide.md` — logic-flow design (conclusion first vs. suspense, inter-section relationship labels, transition-sentence library, logic-gap fixes, flow checklist section 6). Required reading for Workflow A Step 4 and Workflow B.
- `references/sources-and-methodology.md` — sources of the tacit knowledge, sourcing discipline, and script probe records.

## Appendix: CLI Contract (Parameter Quick Reference)

| Parameter | Value | Notes |
|------|------|------|
| `--topic` | string | Article topic, mutually exclusive with `--json-input` |
| `--type` | technical/blog/news/listicle/opinion/tutorial | default `technical`; illegal values error out |
| `--length` | short/medium/long | default `medium` |
| `--audience` | beginner/intermediate/expert | default `intermediate` |
| `--points` | multiple values | key-point list |
| `--platforms` | multiple values | target platforms |
| `--json-input` | file path | full JSON input (containing topic) |
| `--output` | file path | write the outline JSON; default prints to stdout |
