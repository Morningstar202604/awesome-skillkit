---
name: content-editor
description: "Proofread, polish, and style-unify article drafts. Detects banned words, inconsistent tone, overlong sentences, and grammar issues. Scores editability. Use after drafting, before SEO and publishing, e.g. polishing an article / proofreading typos / unifying writing style / removing AI tone / running a quality check on an article. Do NOT use for generating new content from scratch (editing and polishing only)."
license: Apache-2.0
compatibility: Pure Python analysis; LLM-assisted for rewriting. Optional helper scripts/editor.py requires Python 3.8+ (stdlib only). No API keys required.
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Content Editor (Proofreading, Polishing, and Style Unification)

Runs a quality check on a formed draft: scans banned words, overlong sentences, section transitions, and style consistency, and gives a 0-100 editability score.

## Honest Disclosure (Read First)

- **`score` is a "mechanical editability-risk score", not an article-quality score.** The formula `100 - issues*5 - long_sentences*2` only counts banned words and long sentences: an empty-but-clean article can score full marks, while an insightful article with three banned words gets docked. The score's purpose is to prioritize editing attention, not to grade the article.
- **The script doesn't rewrite the body.** The `edited` field in `editor.py`'s output is the **input text returned as-is** — the real rewriting is done by the agent based on `issues`/`suggestions`; "the script fixed it" is a misreading.
- `issues[].line` is actually a **character offset** (`text.find(word)`), not a line number; the 12 in the example JSON means the 12th character.
- The banned-word scan is **substring matching** with no context judgment: "should" appearing inside "this feature" will also hit — manually remove such false positives during review.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| `draft` | yes | Draft object: `title` + `sections[]` (each section `heading`/`draft`) |
| `style` | no | `technical` / `casual` / `news`, default `technical` |
| `brand_voice` | no | A text description of the desired tone, used to align the LLM rewrite |

When missing, ask everything at once: "Please provide: ① the draft to polish (JSON or plain text); ② style (technical/casual/news); ③ brand voice (nullable). Otherwise default: style=technical."

## Pre-flight Checks

1. Verify the script works (optional, deterministic scan):
   ```bash
   python3 scripts/editor.py --draft draft.json --style technical --output edited.json
   ```
   Expected: exit code `0`, output has `score`/`issues`/`suggestions`.
   If it fails: `Need --draft or --text` -> add `--draft` or `--text` and rerun.
2. Confirm the `style` value is in `technical|casual|news`; otherwise fall back to `technical`.
3. Pure prompt mode can skip Step 1 and go straight to the workflow.

## Workflow

### Step 1: Load the Draft

Read `draft`, extract the full text and each section's text.
Expected: a scannable text string and per-section indices.
If it fails: JSON parse error -> ask the user to fix the `draft` structure, then STOP.

### Step 2: Scan Banned Words

Per the `style` rule set (see "Style Rule Table"), match the `ban` list word by word.
Expected: produce `issues[]` entries with `type:"banned_word"`, containing the hit word and position.
If it fails: a word spans sections -> record only the first hit `line`.

### Step 3: Check Sentence Length

Split by periods, count long sentences exceeding `max_sentence_len`.
Expected: `long_sentences` count accurate.
If it fails: text without periods -> split by newlines and count again.

### Step 4: Check Section Transitions

Check whether adjacent sections have transition sentences/phrases; suggest one if missing.
Expected: `suggestions[]` contains transition suggestions (if there's a gap).

### Step 5: Score

`score = 100 - issues*5 - long_sentences*2`, floor 0.
Expected: output `score` (0-100), `issues`, `suggestions`, `sections_edited`.

### Step 6: Produce the Checkup Result

Consolidate into a result object (example below); the LLM rewrites the draft based on it.

## Input/Output Example

Input:
```json
{
  "draft": {
    "title": "...",
    "sections": [{"heading": "...", "draft": "text..."}]
  },
  "style": "technical",
  "brand_voice": "optional: description of desired voice"
}
```

Output:
```json
{
  "style": "technical",
  "title": "Article Title",
  "score": 82,
  "issues": [
    {"type": "banned_word", "word": "I think", "line": 12},
    {"type": "long_sentence", "chars": 78, "limit": 40, "line": 25}
  ],
  "suggestions": ["Add transition phrase between sections 2 and 3"],
  "long_sentences": 3,
  "total_sentences": 20,
  "word_count": 850,
  "edited": "the full rewritten body text (plain text)",
  "sections_edited": 5,
  "status": "reviewed"
}
```

> Downstream handoff: `edited` is the rewritten body for humans; `title` + `sections_edited` helps backfill the structure. If the downstream (seo-optimizer / platform publishing skills) needs structured sections, pass back the `sections` from Step 1's `draft.json`; this skill's output is authoritative as the plain-text `edited`.

## Style Rule Table

| Style | Banned Words | Replacement | Max Sentence Length |
|------|--------|---------|----------|
| Technical | I think / should / maybe | according to / measured / the conclusion is | 40 chars |
| Casual | in summary / thus it follows | put plainly / see | 25 chars |
| News | shocking / blew up / amazing | reportedly / sources say | 30 chars |

## Editing Tacit Knowledge (Sourced; Read Before You Edit)

1. **The banned-word list is fundamentally a critique of "pre-fabricated phrases", not word dirt.** George Orwell, Politics and the English Language (1946): cliches (dying metaphors) are "unassimilated other people's thought", using ready-made phrases instead of thinking. English's "in my opinion it is not an unjustifiable assumption that" and Chinese's "leverage / grip / closed loop" are the same disease — **the replacement table is only a symptom scanner; what the editor must cure is "is this sentence actually thinking"**.
2. **The first editing pass always subtracts.** Stephen King, On Writing: second draft = first draft - 10%, "kill your darlings" (adverbs are not your friend). Translated into checkup actions: first delete filler words like "just / almost / obviously / basically" and filter words ("I notice / seems"), then consider adding things — reversing the order is gilding a padded article.
3. **The criterion for "omit needless words" is "deleting it loses nothing"** (Strunk & White, The Elements of Style, rule 17). Mechanical synonym replacement isn't the same as fixing: swapping "I think" for "the conclusion is" without analytical support is trading soft padding for hard padding.
4. **The sentence-length cap is a check trigger, not "wrong whenever exceeded".** Jane Friedman's editing checklist emphasizes that sentence-length variation creates rhythm: consecutive same-length sentences are a machine-tone signature. A 40-character long sentence with three layers of progressive logic can be kept; 18-character nonsense still gets cut. The `long_sentences` count is a reminder, not a verdict.
5. **The editor doesn't do fact-checking, but must flag suspicious spots.** When numbers don't add up or a quote is dubious, list a "to be confirmed by author" checklist in the delivery notes — the editor's boundary is language and structure; overstepping to "fix the data on the fly" manufactures new errors.

**Sources**: Orwell, "Politics and the English Language" (1946); King, On Writing (2000); Strunk & White, The Elements of Style; Jane Friedman self-editing checklist. All public publications, cross-checked across multiple sources.

## Red Lines (What the Editor Doesn't Do)

1. **Don't do mechanical synonym replacement** — passing the scanner != a better article; every replacement must answer "what is this sentence actually saying now".
2. **Don't erase the author's voice fingerprints** — verbal tics are part of style; only handle what conflicts with the target style.
3. **Don't overstep to fix factual content** — only mark "to be confirmed"; don't change data on the author's behalf.
4. **Don't delete reasonable long sentences just to raise the score** — keep long sentences with progressive logic; what you cut is redundancy, not length.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--draft` | file path | Draft JSON (see input example), one of the required inputs |
| `--text` | string | Plain-text draft |
| `--style` | technical/casual/news | default `technical` |
| `--output` | file path | write the checkup result JSON |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|-------------|------|------|
| `Need --draft or --text` | Missing input | Add `--draft` or `--text` |
| JSON parse failed | Draft structure error | Ask the user to fix the `draft` fields |
| Illegal `style` value | Typo | Fall back to `technical` and note it |
| `score` is negative | Too many issues | Floor to 0, prioritize rewriting banned words |

## Delivery Standard

- Success: produce a checkup result with `score`, `issues`, `suggestions`, `status:"reviewed"`.
- Artifact name: `edited.json` (checkup result) or `draft.reviewed.md` (rewritten body).
- Save location: user-specified directory; the script uses `--output`, default stdout.
- Completeness check: `score` in [0,100]; when non-empty, `issues` and `suggestions` correspond respectively; `sections_edited` == draft section count.

## References

- `references/style-guide.md` — house style details; read as needed in Steps 2/5.
- `references/grammar-checks.md` — common Chinese-English grammar error list; read in Steps 2/3.
