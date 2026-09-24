---
name: humanize-rewriter
description: "Rewrite AI-flavored text into natural human writing: inject burstiness (long-short sentence rhythm), upgrade abstractions to concrete details, add first-person reaction and controlled imperfection, while freezing all facts, numbers, terms and conclusions. Use when the user asks to remove AI flavor / humanize this text / make it sound human / rewrite to lower the AI rate / humanize text / make it sound human / rewrite the AI draft. Do NOT use for legal, medical or academic-submission texts, and never invent facts the source does not contain."
license: Apache-2.0
compatibility: Needs Python 3.8+ (stdlib only) for the baseline/rescan step via the ai-trace-auditor bundle scanner; if unavailable, degrade to its manual checklist and mark the report manual_mode.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: writing
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-21"
---

# Humanize Rewriter (Humanizing Rewrite)

Ghostwritten AI prose is neat but cold. This skill tears down and rebuilds its expression layer — rhythm, concreteness, emotion, controlled imperfection — without touching the information layer with a single finger. Every step is verifiable: there's a baseline score before rewriting, and it must drop significantly after.

## Applicability Decision Table (Judge First, Then Write)

| What You Have | Use This Skill? | How |
|---|---|---|
| AI-generated first draft, want it to read "human-written" | Deep personification (default) | Full workflow, all six steps |
| Human-written draft misflagged by a detector, want to reduce traces | Light de-tracing | Only erase findings hits, skip emotion injection |
| Legal/medical/academic-submission text | **don't** | Wording is the compliance boundary; recommend manual polishing (Red Line 3) |
| Short text under 100 chars | **don't** | No rewriting room; say so plainly |
| User asks to "drop the AI rate to 0" | Refuse to guarantee | Only promise a verifiable score drop (see tacit knowledge 3) |

## Domain Tacit Knowledge (Four Things You Must Know Before Writing)

**1. What detectors (and humans' "AI feel") actually measure.** The essence of AI text is the "next-token probability distribution" taking the safest path — producing low-perplexity, even-sentence-length, neatly-structured prose. This means: **neatness itself is a trace**. Delete ten AI high-frequency words, and if the whole text is still "every sentence 30 chars, every paragraph three sentences, every paragraph opens with a summary," experienced readers and statistical detectors recognize it at a glance. So this skill's focus isn't word-swapping but **breaking rhythmic evenness** — cv (sentence-length coefficient of variation) represents "human-ness" better than word-list hits.

**2. Parallelism and enumeration are the biggest exposure surface.** The LLM training objective makes "three similar-length parallel clauses" the highest-probability safe expression — this is the hardest feature to erase and the highest-recurrence one. Rule of thumb: as long as a rewritten draft still has one "not only... but also... what's more" or three consecutive similar-length parallel sentences, the whole piece's "AI feel" is set by it, and every other change is wasted. When rewriting paragraph by paragraph, strangle it first.

**3. "Lowering the AI rate" is false security and must be broken to the user's face.** This skill's score correlates with any third-party detector (commercial or school-built) **without causation**: word lists differ, weights differ, burstiness algorithms differ, and the same rewritten draft can score 30+ points apart across detectors. The standard delivery phrasing is "statistical features have dropped significantly" — never promise "passes XX detector"; if the user presses, give the principle in tacit knowledge 1, not a guarantee.

**4. Performative human-ness is a second layer of machine tone.** Forcing in emotional sentences creates new tells: every paragraph has "to be honest", every long sentence paired with an em-dash, "frankly I didn't believe it at first" everywhere — "fake human-ness" that human editors spot at a glance is exactly what the word list can't measure. Post-2025 model rewrites universally carry "em-dash dependency"; it's already the new generation's AI cliche. Discipline: at most two or three emotional sentences in the whole text, at most one rhetorical punctuation per paragraph; better to leave one paragraph untouched than force emotion into it.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Text to rewrite | yes | AI-generated first draft or clearly AI-flavored finished piece; too short (<100 chars) leaves no rewriting room |
| voice profile | no | voice-profile.json produced by personal-voice-profile; if absent, use a generic human-ness strategy and declare it |
| Rewrite intensity | no | light de-tracing (only erase checkup hits) / deep personification (default); if the user doesn't say, go deep |
| Protection list | no | expressions the user names as off-limits; merged with Red Line 1's default freeze items |

When a required item is missing, ask only once:

> Please provide: ① the full text to rewrite; ② optional — your voice profile file (generic strategy if none), rewrite intensity (light de-tracing / deep personification), any sentences that must not be touched?

## Pre-flight Checks

Probe one environment: re-checking depends on trace_scanner.py inside the ai-trace-auditor skill directory (a pure-stdlib script, shipped with that skill's bundle).

```bash
# set SCANNER to the actual path, e.g.:
# SCANNER="C:/path/to/awesome-skillkit/skills/writing/ai-trace-auditor/scripts/trace_scanner.py"
SCANNER="<ai-trace-auditor dir>/scripts/trace_scanner.py"
python3 --version && test -f "$SCANNER" && printf 'probe sentence.\n' | python3 "$SCANNER" - >/dev/null && echo "check=ok"
```

(Pipe one line of probe text rather than `--help`: this script takes a file as a positional argument, and `--help` would be treated as a filename and error; and don't use `| head`, or `$?` is always 0 and meaningless.)

If the script runs -> use the standard flow; if not (no python3 / script missing) -> use the manual checklist throughout (see Step 1 if it fails), marking `manual_mode: true` at delivery. Input-side self-check: do you have the text? Under 100 chars -> say plainly there's insufficient rewriting room and don't recommend starting. Rewrite intensity unstated -> do deep personification and say so in the first reply; don't wait for a second user confirmation.

## Red Lines (Hard Bans, Non-Negotiable)

1. Don't change facts and conclusions: numbers, terms, quotes, claims, causal relationships are all frozen — this skill only touches the expression layer. Extract the banned-change items into a list before rewriting, and check off each at delivery.
2. Don't add information the original lacks: especially numbers. A concreteness upgrade like "from 3 hours to 40 minutes" can only come from facts already in the text or user confirmation; never make one up.
3. Formal legal, medical, and academic-submission texts are out of scope for this skill: in such texts wording is the compliance boundary, and the expression layer's "human-ness" introduces risk; only recommend manual polishing.
4. Don't promise to bypass any platform's or institution's AI detection: this skill improves readability and authenticity, and the rewrite result is unrelated to any detection system's conclusion — say so plainly when asked; see tacit knowledge 3 for the principle.
5. Don't manufacture performative human-ness: emotion-injection sentences <=3 in the whole text, rhetorical punctuation <=1 per paragraph; exceeding this violates the red line, and at re-check roll back against tacit knowledge 4.

## Workflow

### Step 1: Checkup Baseline

- **Action:** first get a baseline score with ai-trace-auditor's scanner (the script is in that skill's directory; cd there first or write the full path):

```bash
python3 "$SCANNER" text_to_rewrite.md     # $SCANNER is the full-path variable set in pre-flight checks
                                          # also supports cat text | python3 "$SCANNER" -
```

- **Expected:** output `{stats, findings[]}` JSON, exit code 0; record the baseline score and the findings list — this is the target for every later step.
- **If it fails:** python3 unavailable -> switch to the manual three-check (word list word by word / eyeball whether sentence lengths are even / count list-line ratio), manually record hits as a comparison checklist, mark the report manual_mode; text the user pasted directly isn't saved to disk -> first save a temp file then scan, or go straight via stdin — the script supports `-` to read standard input (usage in Step 1 code-block comments).

### Step 2: Lock the Banned-Change List

- **Action:** extract four kinds of freeze items from the original: all numbers and units, proper nouns and terms, direct quotes, conclusion sentences. Number them one by one.
- **Expected:** the banned-change list is complete and checkable; ambiguous expressions (e.g. whether "about 30%" counts as movable) are confirmed with the user once face to face. Sample list:

```text
Banned list #1 numbers & units: 3 hours / 40 minutes / 12 people / 2026 Q2
Banned list #2 terms & proper nouns: Kubernetes, HPBX protocol, A/B test
Banned list #3 direct quotes: "Users told us they leave if loading is one second slower."
Banned list #4 conclusion: so the cache layer must stay; cutting it is cutting first-screen experience.
```

- **If it fails:** the user adds a protection list -> merge into this list; can't extract (the whole text is conclusions) -> say this skill only suits light de-tracing.

### Step 3: Load the Voice Profile

- **Action:** if there's a voice-profile.json -> read out the four-layer parameters (lexical catchphrases and high-frequency verbs, syntactic sentence-length and paragraph habits, tonal tone and address, structural opening/closing routines), aligning the rewrite to them; if not -> use a generic strategy and tell the user "running personal-voice-profile first would make it more like you".
- **Expected:** the rewrite baseline is set — every later paragraph asks "does this read like the person in the profile". Alignment-reading example:

```text
profile.syntactic.median_sentence_len = 22  -> keep the rewrite's median sentence length around 20-25
profile.tonal.habit = "likes ending paragraphs with rhetorical questions"  -> at most one rhetorical question per paragraph; better fewer than overdone
```

- **If it fails:** profile file corrupted or fields missing -> fill whichever layer is missing with its generic default; don't discard the whole thing.

### Step 4: Rewrite Paragraph by Paragraph

- **Action:** execute "keep information, change expression, inject emotion" paragraph by paragraph, using the four techniques in priority order:
  - **Burstiness injection:** after two long sentences in a row, follow with a <=8-char short one; split a 60-char long sentence into a 40-char one plus a 12-char one. Target cv >= 0.5 (aligned with the checkup threshold).
  - **Concreteness upgrade:** replace abstract generalizations with concrete nouns, numbers, scenes — "significantly improved efficiency" -> "the same batch of drafts, from 3 hours down to 40 minutes" (the number must come from the original or user confirmation, see Red Line 2).
  - **Emotion injection:** add first-person reactions, hesitation, asides — "to be honest I didn't believe it at first", at most two or three in the whole text (Red Line 5), not piled up.
  - **Imperfection allowed:** spoken insertions, em-dash detours, an occasional rhetorical question; let one unglamorous expression stay as-is.
- At the same time, erase traces against Step 1's findings item by item: ai_word hits -> swap for concrete expression, parallelism -> split the sentence, enumerator_chain -> turn into subheadings or expand directly, list_density -> knead non-parallel lists back into paragraphs.
- Technique priority: **first strangle parallelism and enumeration (tacit knowledge 2's biggest exposure surface), then erase findings hits (verifiable), finally apply the four techniques (perceptible)** — doing only the last layer misleads the checkup score; doing only the first two leaves readers feeling nothing changed.
- **Expected:** after each paragraph, you can map sentence by sentence between original and rewrite; banned-list items have zero change; total emotional sentences <=3; total em-dashes no more than the original. Before/after example:

```text
Original: In summary, cache optimization significantly improved system performance, not only lowering latency but also raising throughput.
After: The moment we cut in the cache, endpoint latency dropped from 800ms to 90ms, and throughput climbed with it — numbers don't lie.
Techniques: delete "in summary / not only...but also" (checkup L3 hit, and a parallelism exposure surface) -> burstiness: append a short sentence after the long one
           -> "800ms->90ms" is a fact already in the original (Red Line 2: no new number); em-dash follows the original rhythm, not added
```

- **If it fails:** a paragraph stays no matter how you rewrite it -> keep it as-is and note "this paragraph is information-dense, not force-injected"; don't manufacture emotion.

### Step 5: Re-check

- **Action:** run Step 1's scan command on the rewrite again, same parameters as the baseline.
- **Expected:** score drops >=20 points vs. baseline (empirical, tunable), and cv rises above 0.5; if a voice profile was loaded, sentence length and paragraph shape should approach the profile's syntactic layer. Comparison-record example:

```text
Baseline: score 23, heavy_ai_style, ai_word_hits=7, cv=0.38, list_ratio=0.55
         (verify: 100 - 7*6 - 20(cv<0.5) - 15(list_ratio>0.4) = 23, matching the script's formula)
Re-check: score 88, human_like, ai_word_hits=2, cv=0.61, list_ratio=0.32
         (verify: 100 - 2*6 = 88; cv and list_ratio both passed the line, no longer docked)
Conclusion: drop 65 >= 20, passes; the 2 residual hits get treatment notes in the comparison table
```

- **If it fails:** score rises instead of falling -> likely you turned all long sentences into even short ones; go back to Step 4 and redo long-short alternation; just short of the line -> only do point patching on residual findings, don't rewrite the whole piece. Score passes but it still reads fake -> go back to tacit knowledge 4 to hunt for performative human-ness, rolling back sentence by sentence.

### Step 6: Deliver

- **Action:** output three artifacts: ① the full rewritten draft; ② a change comparison table, each `original -> after <- technique/basis`; ③ the score comparison and boundary disclaimer — "statistical features have dropped significantly (baseline X -> re-check Y), with no causal link to any third-party detector's conclusion".
- **Expected:** the user can accept or reject each change item by item; the boundary disclaimer travels with delivery (Red Line 4).
- **If it fails:** the comparison table doesn't match the rewrite -> recompute the table from the rewrite as authoritative; delivering two disconnected versions is forbidden.

## Output Spec

| Artifact | Structure | Notes |
|---|---|---|
| Rewritten draft | Continuous prose | Paragraph-by-paragraph correspondence with the original; banned items untouched verbatim |
| Change comparison table | each row: original / after / technique / basis | basis points to a checkup finding's pos or a voice-profile field |
| Re-check result | `{score, verdict, findings[]}` | Same structure as the ai-trace-auditor report; baseline and re-check scores shown side by side |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Re-check score rises instead of falling | Short sentences piled into a new even rhythm | Go back to Step 4 and redo long-short alternation; verify cv |
| Score passes but "still reads fake" | Performative human-ness (tacit knowledge 4) | Roll back emotion stacking and em-dashes sentence by sentence, then re-check |
| Banned content was changed | A slip while rewriting | Roll back against the banned list item by item, rerun re-check |
| User asks to invent details/numbers | Hits Red Line 2 | Refuse; suggest inserting a `<to be confirmed by you: specific value>` placeholder |
| User presses "will it pass XX detector" | Hits Red Line 4 | Refuse to guarantee; explain correlation-without-causation via tacit knowledge 3 |
| After rewriting it reads like someone else wrote it | Profile not loaded or intensity too high | Revert to light de-tracing: only erase findings hits, no emotion injection |
| The whole text is conclusions with nothing to change | Information layer and expression layer inseparable | Say plainly this skill fits poorly; recommend rewriting rather than revising |
| Rewrite is >20% over/under length | Emotion injection or cuts out of control | Anchor back to the original length; note the deviation in the comparison table |
| Emotional sentences clash with the piece's tone | Wrong intensity or missing profile | Roll back the jarring injected sentences; keep the structural-layer changes |
| Em-dashes/ellipses used twice as much as the original | "Imperfection allowed" treated as punctuation stacking | Roll rhetorical punctuation back to at most one per paragraph; record rollbacks in the table |
| The user brings a formal text like a contract/medical record | Hits Red Line 3 | Refuse to rewrite and explain why; only give directional manual-polishing advice |

## Delivery Standard

- Re-check score drops >=20 vs. baseline (empirical, tunable); the banned list checked item by item with zero changes.
- Change comparison table complete: every change traceable to a technique and basis, no unrecorded changes.
- The rewrite contains no numbers or facts absent from the original; includes a detection-boundary disclaimer (correlation without causation, tacit knowledge 3 wording).
- Performative human-ness self-check passes: emotional sentences <=3, rhetorical punctuation <=1 per paragraph, zero residual parallelism/enumeration.
- The rewrite can be handed straight to content-editor or publishing skills: no unconfirmed placeholders left (`<to be confirmed by you: ...>` must either have been clarified with the user in Step 4 or kept as an explicit placeholder).
- After reading the rewrite, the user can say "this sentence sounds like me" or point out "this one doesn't" — the latter goes into the next round of point patching.

## References

- `references/sources-and-methodology.md` — read when you need to explain the sources of the burstiness and concreteness principles, the basis for the four techniques, or external attribution.

## Chain Position

- Upstream: ai-trace-auditor (its checkup report is this skill's target list); personal-voice-profile (the voice profile aligns "human-ness" to a specific person).
- Downstream: content-editor (final-draft polishing), per-platform publishing skills (wechat-mp-publisher, zhihu-content-manager, juejin-publisher, etc.).
- Parallel: own-voice-rewrite (the restrained version for the education domain's student essays; use this skill for general writing-domain cases).
