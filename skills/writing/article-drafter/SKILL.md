---
name: article-drafter
description: "Generate an article first draft from an approved outline. Fills in each section with prose based on key points, audience level, and style. Use after the outline is approved, before editing/SEO, e.g. writing a first article draft / drafting the body / help me write this / expand the outline into an article. Also triggers on body drafting / write first draft / expand outline / draft article / write first draft. Do NOT use for publishing the finished draft to platforms, or for building the outline itself (use article-outliner)."
license: Apache-2.0
compatibility: Pure prompt-based drafting; LLM generates prose. Optional helper scripts/drafter.py requires Python 3.8+ (stdlib only). No API keys required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Article Drafter (Generate a First Draft From an Outline)

Based on an approved outline, expand each section's key points into readable prose at the audience level and style, producing a draft ready for review.

## Applicability Decision Table

| Situation | Use This Skill? | Why |
|------|------------|------|
| Outline approved, need to write the body | yes, this skill's home turf | Expand each section from its points |
| Outline not yet settled | no, go to article-outliner first | Drafting before the outline is settled = building on sand |
| Draft written, need polishing | no, go to content-editor | Drafting and editing are two jobs; mixing them does both poorly (see tacit knowledge 1) |
| Need to publish to platforms | no, edit first, then go to publishing skills | An unedited draft shouldn't meet readers directly |
| Only missing one hook or conclusion | yes, `--section` single-section mode | No need to rerun the whole piece |

## Honest Disclosure (Read First)

- `scripts/drafter.py` is a **skeleton generator**: the produced `draft` field is a placeholder prompt (marked `status:"draft_placeholder"`), not finished body text. **The body is generated section by section by the agent in Step 2.** The "real script output" and "after agent fills in" examples below are given separately and aren't passed off as one.
- The script doesn't validate the `audience` enum value (it accepts "junior-to-mid engineer" too); normalizing the enum to beginner/intermediate/expert is the agent-layer's job (Step 0).
- `word_count +/-20%` is the agent's self-check target; the script doesn't enforce a word-count gate.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| `outline` | yes | Outline object: with `title`, `sections[]` (each section `heading`/`points`/`word_count_target`), optional `hook`/`conclusion` |
| `audience` | no | `beginner` / `intermediate` / `expert`, default `intermediate`, determines terminology density |
| `tone` | no | Style, e.g. `technical` / `casual` / `news` |
| `research_notes` | no | Raw material, used to supplement facts and data |

When missing, ask everything at once: "Please provide: ① the outline (title + per-section points + per-section word target); ② target audience (beginner/intermediate/expert); ③ tone; otherwise I take defaults: audience=intermediate, tone=technical, research_notes=empty."

## Pre-flight Checks

1. Confirm `outline` exists and is non-empty:
   ```bash
   python3 scripts/drafter.py --outline outline.json --output /tmp/draft_check.json
   ```
   Expected: exit code `0`; in **outline mode** the `sections` array length >= the outline's section count.
   If it fails: `[ERROR] outline file does not exist` -> wrong path; ask the user to confirm `outline.json`'s location, then STOP.
2. `--topic` mode (no outline) produces an empty skeleton (`sections: []`); this is by design — it only holds a title as a placeholder, not a drafting basis.
3. Confirm the `audience` value: when not in `beginner|intermediate|expert`, the agent normalizes it (e.g. "junior-to-mid engineer" -> intermediate) and restates the mapping to the user. The script layer does no validation.
4. If not using the script (pure prompt mode), skip Step 1 and go straight to Workflow Step 2.

## Workflow

### Step 1: Generate the Outline Skeleton (Deterministic, Optional)

Run the script to structure the outline into a draft-placeholder skeleton; the body is filled by the agent in Step 2:
```bash
python3 scripts/drafter.py --outline outline.json --audience intermediate --output draft.json
```
Expected: `draft.json` has `title`/`hook`/`sections[]`/`status:"draft"`/`needs_review:true`, each section's `draft` a placeholder prompt.
If it fails: a missing parameter reports `Need --outline, --topic, or --section` -> add `--outline` and rerun.

### Step 2: Fill in the Body Section by Section (Agent-Generated, Per Drafting Discipline)

For each `sections[]` item, **first read all of that section's points and figure out "what should the reader understand from this section" before writing** (tacit knowledge 3), then:

- Read `points` and expand into 2-4 paragraphs; each point must land on at least one **concrete** noun/number/scene — no stopping at abstract sentences like "very important / indispensable";
- Match the `audience` terminology density (see "Audience Style Rules");
- Hit `word_count_target` +/-20%;
- **Don't go back to rewrite finished sections** — the draft stage only moves forward; editing is left to content-editor (tacit knowledge 1/2).

Expected: each section's `draft` field is non-empty, word count within the target range.
If it fails: a section has no `points` -> use `heading` as the sole point and generate, marking that section `needs_review`.

### Step 3: Write the Opening Hook and Conclusion CTA

- The hook opens with a **concrete scene or counterintuitive fact**, not an abstract generality like "in today's fast-developing era" (a direct corollary of tacit knowledge 3);
- Use `outline.hook` (if present) as the opening 2 sentences to grab attention; if absent, self-write a scene-setting opener;
- Write `conclusion` + a call to action (follow/save/comment, per platform conventions).
Expected: `hook` and `conclusion` non-empty.

### Step 4: Produce the Complete Draft

Integrate into a complete draft, output JSON or Markdown.
Expected: the artifact has all sections, total word count, status `draft`, pending-review marker; hand to content-editor rather than publishing directly.

## Drafting Tacit Knowledge (Sourced; Read Once Before Drafting)

Writing methodology is "something subjective", and this section all comes from public publications and primary texts, not invented:

1. **The draft's job is to "exist", not to be "good".** Anne Lamott's "shitty first drafts" chapter in Bird by Bird: all good writers write terrible first drafts; the first draft is the "down draft" (just pour it out); perfectionism is the #1 killer of drafts. Corollary: **drafting and editing must be physically separated** — people who edit as they write are actually letting the editor's anxiety block drafting.
2. **The expectation when revising is subtraction.** Stephen King, On Writing: second draft = first draft - 10%; write with the door closed (only for yourself), revise with the door open (for the reader). Corollary: at drafting, slightly exceeding the word target (leaving ~10% headroom per the same rule) is healthy, leaving room for cuts; stopping only when you've hit the target word count usually means padding.
3. **Meaning before wording.** George Orwell, Politics and the English Language (1946): "think out the meaning as clearly as possible in pictures and feelings first, then choose — not accept — the words." Pre-fabricated phrases (dying metaphors) are a sign that thinking has been taken over: English's "in my opinion it is not an unjustifiable assumption that", and Chinese's equivalent "leverage / grip / closed loop / ignite / deep analysis". **Recognition note**: Orwell's "ban the passive voice" targets English style; Chinese patient-subject (the "bei"-disposal) sentences are often more natural, so this isn't transplanted mechanically — what's transplanted is the principle "let meaning choose the word", not a line-by-line rule.
4. **Cut needless words.** Strunk & White's The Elements of Style "Omit needless words" + Orwell rule (iii) "omit every word you can": in Chinese first drafts, "just / almost / obviously / basically / you could say" are mostly filler; deleting them usually loses nothing.
5. **Filter words distance the reader** (Jane Friedman's editing checklist): filter words like "I noticed / she felt / seems" make the reader look at the scene through frosted glass; "she felt a chill" is worse than "the wind blowing through the doorframe blew out the candle". Also vary sentence length — consecutive same-length sentences are the rhythm signature of machine tone.
6. **Research is the bulk of drafting time.** Robert Caro's way of working: by the time he writes, the research is long done; writing is pouring out what's already been thought through. Corollary: when `research_notes` is empty, first ask the user for material before writing — a draft written without ingredients can only rely on fabrication, and fabrication is the most expensive drafting error.

**Sources**: Anne Lamott, Bird by Bird (1994); Stephen King, On Writing (2000); George Orwell, "Politics and the English Language" (1946, Horizon); William Strunk Jr. & E.B. White, The Elements of Style; Jane Friedman's self-editing checklist; Robert Caro, Working (2019). Each claim was cross-checked across multiple sources before adoption; single-source claims that couldn't be cross-verified were excluded.

## Red Lines (What Not to Do at the Draft Stage)

1. **Don't run polishing loops while drafting** — rewriting goes to content-editor; this skill's artifacts always carry `needs_review:true`.
2. **Don't open with pre-fabricated phrases** — the hook bans "in today's era of... / with the development of... / as everyone knows".
3. **Don't pad for word count** — when points can't carry `word_count_target`, honestly shorten and mark `needs_review`, rather than repeating expressions to fill space.
4. **No invented data without a source** — numbers, cases, and quotes not in `research_notes` get written as "to be added" placeholders in the draft; making them up is forbidden.
5. **Don't rewrite the user's outline's section structure and order** — if you have opinions on structure, raise them in the delivery notes; the draft stays faithful to the outline.

## Input/Output Example

Input `outline`:
```json
{
  "outline": {
    "title": "FastAPI Performance Optimization",
    "sections": [
      {"heading": "Why It's Slow", "points": ["sync I/O", "N+1"], "word_count_target": 300}
    ]
  },
  "audience": "intermediate",
  "tone": "technical",
  "research_notes": "optional raw material"
}
```

**Real script output** (skeleton; `draft` is a placeholder prompt):
```json
{
  "title": "FastAPI Performance Optimization",
  "hook": "",
  "sections": [
    {
      "heading": "Why It's Slow",
      "draft": "sync I/O.\n\n(intermediate reader view: explain why + how to do it + caveats)\n\nN+1.\n\n(intermediate reader view: explain why + how to do it + caveats)\n",
      "word_count": 66,
      "target": 300,
      "status": "draft_placeholder",
      "note": "Production: LLM generates full text based on outline + research",
      "id": null
    }
  ],
  "conclusion": "",
  "total_words_target": 2000,
  "status": "draft",
  "needs_review": true
}
```

**After the agent fills it in** (final delivery after Steps 2-3):
```json
{
  "title": "FastAPI Performance Optimization",
  "hook": "The same endpoint: load-test QPS dropped from 120 to 9 — two hours of debugging, and the culprit was one query inside a loop.",
  "sections": [
    {
      "id": 1,
      "heading": "Why It's Slow",
      "draft": "FastAPI itself is an async framework, but as soon as you write one synchronous blocking call in a route, the whole event loop stalls... (body)",
      "word_count": 318,
      "target": 300,
      "status": "ok",
      "note": ""
    }
  ],
  "conclusion": "(summary + CTA)",
  "total_words_target": 2000,
  "status": "draft",
  "needs_review": true
}
```

> Downstream handoff: content-editor's `--draft` reads this file directly; it requires a top-level `title` and `sections[]` (each with `heading`/`draft`), which this output satisfies.

## Audience Style Rules

| Audience | Terminology Density | Examples | Code |
|------|---------|------|------|
| Beginner | minimum, all explained | 3-4 per section | full snippets |
| Intermediate | moderate, standard terms | 2-3 per section | key snippets |
| Expert | high density, assumed known | 0-1 per section | one-line snippets |

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--outline` | file path | Outline JSON (see input example), one of the required inputs |
| `--topic` | string | Quick topic when no outline (produces an empty skeleton) |
| `--section` | string | Draft a single section only |
| `--audience` | beginner/intermediate/expert | default `intermediate`; the script doesn't validate, normalization is the agent's job |
| `--output` | file path | Write the draft JSON |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|-------------|------|------|
| `[ERROR] outline file does not exist` | Wrong path | Confirm the file exists, fix the path, rerun |
| `Need --outline, --topic, or --section` | Missing input | Add `--outline` or switch to pure prompt mode |
| A section's word count deviates >20% | Too few/too many points | Split or merge `points`, regenerate that section; don't pad |
| Illegal `audience` value | Free text | The agent normalizes to the three-tier enum and restates the mapping to the user |
| Wanting to edit as you write | Missing drafting discipline | Stop. Record the points to change in `note`, and hand them all to content-editor after delivery |
| research_notes empty | No ingredients | Ask the user for material; otherwise write "to be added" at data points; fabrication is forbidden |

## Delivery Standard

- Success: produce a complete draft, all sections' `draft` non-empty, total word count near `total_words_target`.
- Artifact name: `draft.json` (structured) or `draft.md` (Markdown).
- Save location: user-specified directory; the script uses `--output`, default stdout.
- Completeness check: `sections` count == outline section count; each section's `word_count` within target +/-20%; `status=="draft"` and `needs_review==true`.

## References

- `references/drafting-tips.md` — writing tips by section type; read as needed when writing Step 2.
- `references/sources-and-methodology.md` — per-item sources of the tacit knowledge and the sourcing discipline.
