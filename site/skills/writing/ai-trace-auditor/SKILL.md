---
name: ai-trace-auditor
description: "Audit a text for AI-writing fingerprints: scan built-in Chinese/English AI high-frequency word lists, measure sentence-length variance (std/mean), list/parallelism density and structural cliches, then report a 0-100 score with per-finding locations as machine-parseable JSON. Use when the user asks to detect AI flavor / AI-trace detection / check whether this reads like AI wrote it / AI-rate check / audit AI traces / detect AI writing / scan for AI style / de-AI check. Do NOT use as an official AI detector for academic-integrity arbitration — heuristic self-check only."
license: Apache-2.0
compatibility: Needs Python 3.8+ (stdlib only) for scripts/trace_scanner.py; if Python is unavailable, degrade to the manual checklist and mark the report manual_mode.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# AI Trace Auditor (AI-Trace Checkup)

AI flavor isn't mysticism; it has measurable, locatable features. This skill gives the text a "checkup": runs the word list, computes sentence-length variance, counts list density, and produces a 0-100 score with itemized findings — it only diagnoses, doesn't operate; rewriting is handed off to the downstream humanize-rewriter.

## Applicability Decision Table (Judge First, Then Check Up)

| Your Goal | Use This Skill? | Expected Value |
|---|---|---|
| Self-checking before publish/delivery, "how heavy is the AI flavor in this draft" | yes | Findings are located item by item, ready to hand to humanize-rewriter to erase traces |
| Internal review, comparing how machine-flavored two draft versions are | yes | Scores are comparable across runs on the same text (deterministic script) |
| Asking "did AI write this" (authorship attribution) | **don't** | This skill measures stylistic features, not authorship (tacit knowledge 1) |
| Academic-integrity arbitration / wanting an "official AI rate" | **refuse** | Heuristic self-check has no official standing whatsoever (Red Line 2) |
| Text under 3 sentences / heavy code and tables | degraded use | cv is undecidable; only word-list hits are usable |

## Domain Tacit Knowledge (Four Things You Must Know Before the Checkup)

**1. What commercial detectors measure — and why the word-list method is only a "folk approximation."** Mainstream commercial detectors run on two families of signals: perplexity (the model's "surprise" at the text — AI text is too predictable, so it's low) and burstiness (the fluctuation in sentence-length rhythm — humans vary, AI is even and neat). This skill's word list + cv + list_ratio is a hand-made approximation of those two signals: **it measures stylistic similarity to AI output, not AI authorship**. A formulaic piece scoring 90 may be human-written; an imitation of machine-tone scoring 30 may be human-edited — the checkup conclusion is always "does it read like AI's style", not "did AI write it".

**2. False positives have a clear high-risk population and matter more than false negatives.** Three groups' original writing is easily hurt by statistical features: non-native writers (fixed sentence patterns in instructional settings are naturally "even"), formulaic genres like official/legal/medical prose (human conventions already demand neatness), and beginners deliberately imitating "premium" tone (piling up parallelism is a learned rhetoric). So Step 3's context re-check isn't optional — **uniform != AI, neatness != machine**. The most famous historical fail was flagging a non-native student's essay as AI-generated, which is exactly why this skill insists on self-check only, not arbitration.

**3. False negatives come from paraphrase and mixed text; the word list can't catch them.** Sentence-by-sentence paraphrase can bypass any word list; the most common and hardest real case is a "human first draft + AI polish" mixed text — it reads human in one paragraph and machine in the next, and averaging the whole piece's score lands in the "can't tell" zone. When you suspect mixing (sharp style breaks between paragraphs), run a paragraph-by-paragraph check with segmented reports — far more honest than one whole-text score.

**4. The word list is a moving target that drifts with model versions.** "In summary" / "delve into" were the previous generation's cliches; the new generation's cliches change every six months — not hitting today doesn't mean clean. So the score's meaning is "how many known features were hit", not "how much unknown AI flavor remains". Always pair a conclusion with a note on the word list's coverage blind spots; never imply "passing the checkup = no AI flavor".

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| text to check | yes | Plain text or a markdown file path; paraphrases like "this is roughly what I wrote" are not accepted |
| purpose statement | no | pre-publish self-check / internal review / pre-delivery spot check; required for academic submissions, to trigger the Red Line 2 warning |

When a required item is missing, ask only once:

> Please provide: the full text to check (paste it directly or give a file path).
> Optional: the purpose of this text (publish / internal review / academic submission).

## Pre-flight Checks

This skill relies on the bundled scanner script; probe first, then act:

```bash
python3 --version                       # expect 3.8+; on failure -> manual fallback
test -f scripts/trace_scanner.py && echo OK   # expect OK printed, else script missing STOP
```

Input-side self-check: do you have the text? Texts under 3 sentences can't compute sentence-length variance — you can still run the word list, but the report must mark `cv_evaluable: false`. If the purpose statement is missing -> treat it as "pre-publish self-check" and continue; don't ask a second round. If the text exceeds 20,000 characters -> first split it by section into ~3,000-character segments and check each, then report per-segment scores and the lowest-scoring segment; scanning whole without segmenting distorts the location information.

## Red Lines (Hard Bans, Non-Negotiable)

1. This skill is heuristic self-check, not an official AI detector: the report must carry a boundary disclaimer — "the score is based on word lists and statistical features; a hit doesn't mean AI wrote it, and a miss doesn't mean a human wrote it" (see tacit knowledge 1).
2. Not for academic fraud: don't guarantee the user "the AI rate has been lowered to 0", don't treat the checkup report as proof of originality, and never help evade a school's academic-integrity review — refuse and explain when asked. For high false-positive groups like non-native writers (tacit knowledge 2), proactively flag the misfire risk.
3. Read-only, no editing: the audit process must not fix the text on the fly; repairing found issues belongs to the downstream humanize-rewriter.
4. The checkup runs locally: don't paste user text into any online detection site — pre-publish drafts often contain undisclosed information.
5. The score alone must not be shared externally: a bare score without findings has no location information; reporting just one number is forbidden; and don't imply "a high score = no AI flavor" (word-list coverage blind spot, tacit knowledge 4).

## Workflow

### Step 1: Run the Scanner

- **Action:** run on the text to check (the script ships with this skill):

```bash
python3 scripts/trace_scanner.py assets/sample-article.md        # bundled sample; or cat text | python3 scripts/trace_scanner.py -
```

- **Expected:** stdout prints a single JSON object `{stats, findings[]}`, exit code 0. stats holds ~15 fields: sentences, mean_sentence_len, std_sentence_len, cv, list_ratio, enumerator_count, ai_word_hits, score, verdict; each finding holds four fields: pos/type/evidence/fix_hint.
- **If it fails:** python3 missing or the script won't run -> fall back to manual mode: open the `AI_PATTERNS` word list in `scripts/trace_scanner.py` and check word by word, eyeball whether sentence lengths are even, count the list-line ratio, mark the whole report `manual_mode: true`, set the score field to null and explain why.

### Step 2: Read the Stats

- **Action:** read on three axes: sentence-length variance ratio cv (< 0.5 = sentence lengths too even, the core machine-tell); list density list_ratio (> 0.4 = PPT tone); the composite score.
- **Expected:** verdict-tiered conclusion:

| score | verdict | Meaning |
|---|---|---|
| >= 80 | human_like | Statistical features are in the normal range for human writing |
| 60-79 | light_ai_traces | A few traces; light tuning suffices |
| 40-59 | obvious_ai_style | Obvious machine tone; needs systematic rewriting |
| < 40 | heavy_ai_style | Heavy template tone; recommend a full rewrite |

- **If it fails:** sentences < 3 -> cv is undecidable; conclude from the word list and structural items only, and state in the report that data is insufficient.

Reading example:

```text
stats: sentences=18, cv=0.42 (alarm <0.5), list_ratio=0.55 (alarm), ai_word_hits=13
-> reading: even sentence length + dense lists are structural-layer problems; word-list hits are surface problems;
   verify by the formula 100 - 13x6 - 20 - 15 = -13 -> score bottoms out at 0, verdict necessarily heavy_ai_style;
   for such text, recommend a full rewrite outright; word-by-word patching isn't worth it.
```

- **Reading discipline:** low cv and list_ratio but zero word-list hits -> first think tacit knowledge 4 (word list is a moving target) rather than declaring "clean"; word-list hits but cv passes -> first think tacit knowledge 2 (formulaic-genre misfire) rather than convicting outright.

### Step 3: Check Findings One by One

- **Action:** contextually re-check each finding: ai_word hits depend on context — "leverage" inside an internet-industry analysis may be intentional jargon; parallelism and enumerator_chain hits are basically confirmed; the original quote in evidence is used to locate it for the user. Also self-check the author profile: if the author is a non-native writer or the genre is inherently formulaic (contract, announcement, medical record), downgrade uniform-type findings to "pending".
- **Expected:** each finding is labeled one of three states: keep (context reasonable) / confirmed (real AI trace) / pending (ambiguous). Re-check example:

```text
L3 ai_word "lever"      -> confirmed (empty jargon, no concrete referent)
L7 ai_word "robust"    -> keep (in a technical context describing fault tolerance, it's normal terminology)
L9 parallelism        -> confirmed (three clauses with the same opener, pure rhetorical filler)
```

- **If it fails:** an evidence quote can't be located in the original -> re-check by the pos line number; if still unlocatable, delete that item and explain.

### Step 4: Semantic-Layer Checks the Script Can't Run

- **Action:** manually cover four things: does every paragraph open with a summary sentence (AI's "general-to-specific" compulsion); is there abuse of three-item lists (exactly three, similar length); does the conclusion loop hollowly (said a round and said nothing); **is the style broken between paragraphs** (one paragraph fully human, the next machine-neat — mixed-text suspicion, tacit knowledge 3).
- **Expected:** append semantic-layer problems to findings in the same four-field structure, pos = the line number, type = `semantic_pattern`; if you find style breaks -> recommend paragraph-by-paragraph checking instead of a single whole-text score.
- **If it fails:** the text is too short to judge structure -> skip this step and note it.

### Step 5: Output the Report

- **Action:** consolidate into a report JSON and state it to the user:

```json
{
  "score": 34,
  "verdict": "heavy_ai_style",
  "manual_mode": false,
  "disclaimer": "Heuristic self-check, not an official detector",
  "findings": [
    {"pos": "L3", "type": "ai_word", "evidence": "...in summary, delve deeply into...", "fix_hint": turn the summary into one concrete conclusion"}
  ]
}
```

- **Expected:** the JSON parses directly with `json.loads`; the score matches the script output (semantic_pattern additions don't change the score; manual items are stated separately).
- **Expected (scripted phrasing):** close with three sentences — first the conclusion: "score 34, heavy_ai_style; the main problems are 13 word-list hits + 67% list density"; second the destination: "findings are located line by line and ready to hand to humanize-rewriter to erase traces item by item"; third the boundary: "this report measures stylistic features and known word-list coverage (tacit knowledge 1/4), not authorship, and is not any official conclusion."
- **If it fails:** JSON serialization fails -> fix escaping and re-output; delivering semi-structured text is forbidden.

## Parameter Quick Reference

| Field/Rule | Value | Notes |
|---|---|---|
| score | 0-100, higher = more human | Start at 100: each ai_word hit -6; cv<0.5 another -20; list_ratio>0.4 another -15; each parallelism -10; each enumerator chain -8 (empirical, matching script constants, tunable) |
| verdict tiers | thresholds 80/60/40 | human_like / light_ai_traces / obvious_ai_style / heavy_ai_style |
| cv alarm line | 0.5 | std/mean sentence length; empirical, tunable |
| list_ratio alarm line | 0.4 | list lines / non-empty lines; empirical, tunable |
| findings[].type enum | ai_word / uniform_sentence_length / parallelism / enumerator_chain / list_density / semantic_pattern | The first five are script-produced; semantic_pattern is only appended in the manual step |
| pos format | L line number (e.g. L3) | Statistical findings (cv, list density) are fixed at L1 |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| python3 unavailable | Environment missing | Use the manual fallback checklist; mark the report manual_mode, set score to null |
| Text under 3 sentences | Sample too short | Only produce word-list findings, note cv is undecidable; suggest merging the whole text before checking |
| Text has heavy code/tables | Word-list false positives (e.g. robust in comments) | Strip code blocks and tables first, note the removed hits in the report |
| Non-native/formulaic prose flagged high | High false-positive group (tacit knowledge 2) | Downgrade uniform findings to pending; proactively flag the misfire risk |
| Sharp style breaks between paragraphs | Mixed text (tacit knowledge 3) | Switch to paragraph-by-paragraph segmented reports; don't set one whole-text score |
| Zero word-list hits but the user insists it's AI-written | Limited word-list coverage (tacit knowledge 4) | Admit the blind spot: semantic-layer features (Step 4) and novel cliches outside the list aren't covered |
| User wants an "official AI rate" screenshot | Hits Red Lines 1/2 | Refuse; restate the heuristic boundary and that authorship attribution isn't feasible (tacit knowledge 1) |
| Score is directly 0 | Heavy template tone | Report the verdict honestly, recommend handing off to humanize-rewriter for a rewrite rather than word-by-word patching |
| Same text scores differently on two runs | Shouldn't happen (deterministic script) | Check whether a different file/version was passed; rerun after confirming |
| Hits concentrate on proper names in quotes | Word-list false positives on names | Mark as keep per Step 3; if needed suggest the user add book-title marks or quotes to disambiguate |
| The user only cares "will it pass the school's detector" | Hits Red Line 2 | Answer plainly: this report is unrelated to any detection system; no evasion guarantee |
| Mixed Chinese-English text | Sentence length counted in characters; long English sentences raise the mean | Scan and interpret normally; note in the report the limitation that cv is character-based |
| Text from OCR or speech transcription | Missing sentence breaks merge sentences into long ones | First manually fix sentence breaks, then scan; if unfixable, declare sentence segmentation untrusted and rely only on word-list hits |

## Delivery Standard

- Report JSON parses with `json.loads`; each finding has the four fields pos/type/evidence/fix_hint.
- Each finding is locatable in the original by its pos line number; evidence is an original snippet.
- The report carries the boundary disclaimer and (if applicable) a manual_mode mark; the score matches the script output.
- Context re-check complete: each finding carries a three-state label, no default "rewrite everything" conclusion; high false-positive groups self-checked (tacit knowledge 2).
- The user can take the findings and decide "edit or not" item by item, and clearly knows the score is stylistic similarity, not authorship evidence — that's the final usefulness bar of the checkup.

## References

- `references/sources-and-methodology.md` — read when you need to explain the provenance of the AI high-frequency word list, the source of the perplexity/burstiness detection principles, the basis for scoring weights, or external attribution.

## Chain Position

- Upstream: any finished writing — text from article-drafter and ai-humanizer is within this skill's checkup scope.
- Downstream: humanize-rewriter (takes this skill's findings and rewrites item by item; after rewriting, returns here for re-check).
- Parallel: own-voice-rewrite (the education-domain student-essay chain, whose final-draft re-check also calls this skill).
