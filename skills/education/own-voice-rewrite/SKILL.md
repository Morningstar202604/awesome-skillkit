---
name: own-voice-rewrite
description: >-
  Rewrite a homework draft in the student's own voice. Two calibration paths:
  if a real writing sample from the student is available, extract distributional
  voice features (sentence-length band, punctuation rhythm, connective
  preferences) and a negative-constraint list; otherwise fall back to grade-level
  calibration (primary / middle / high-school vocabulary, sentence-length caps)
  and declare it as a proxy. Then force-inject the student's real materials in
  place of generic filler, add restrained human touches, re-audit with
  ai-trace-auditor, and deliver with a read-through-before-submitting reminder
  plus an append-only calibration record. The human-warmth core of the
  homework-autopilot chain. Use when the user asks to rewrite in student voice /
  make it sound like me / remove essay tone / rewrite at my level / sounds like
  a student wrote it. Do NOT use for experiences the student never had, nor as a
  guarantee against AI detection.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: education
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-22"
---

# Own Voice Rewrite (Student-Voice Rewrite)

AI first drafts are neat but cold, obviously machine-made. This skill is the
"warmth" core of the homework-autopilot chain: change solution-drafter's first
draft into the student's own language, replace empty phrases with real material,
then hand to ai-trace-auditor for re-check—the final draft must survive the
teacher asking "did you write this? tell me how you thought about it."

**v2.0 key upgrade**: the old version only "lowered by grade level"—that makes
her write **like a middle schooler**, not **like herself**. The new version adds
a real calibration path: as long as the student can provide a piece of their own
past writing, use it to extract a language fingerprint; when no sample is
available, fall back to grade level and honestly declare it a **proxy**, not
alignment.

## Applicability Decision Table

| Your Situation | This Skill's Role | Go To |
|----------|--------------|------|
| Have a draft, want it to sound like the student wrote it | yes, this skill | here |
| Need to write from scratch (no draft) | wrong order | solution-drafter first to produce draft |
| Only want to reduce AI trace, don't care "who it sounds like" | available but lower-tier | humanize-rewriter more direct |
| Want to check how much machine trace remains in final | yes, step 4 uses | ai-trace-auditor |
| Student can't provide any of their old writing | go grade-level proxy path, declare limitation | step 0 branch B |
| "Guarantee it passes AI detection" | refuse | red line 4 |

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| draft | yes | solution-drafter draft JSON; must contain content / used_materials / checklist_pass |
| Grade and subject | yes | "8th-grade Chinese"—determines language level calibration band |
| **Voice sample** | no (but strongly recommended) | Student's own past writing (journal/weekly note/social media long post all OK); with it, take "voice alignment" path (step 0) |
| Supplementary material | no | material gaps found during rewriting, allows one mid-pass supplement |

When inputs are missing (**only 1 and 2 are blocking**):

> 1 draft, 2 grade/subject missing → ask all at once: please provide 1) draft
> (draft JSON or full text); 2) grade and subject.
> 3 experience authenticity, 4 voice sample **missing don't block**: 3 if not
> stated, treat as "experience authentic" and prompt user to verify in delivery;
> 4 no sample → grade proxy path (step 0 branch B), `voice_alignment.mode` marked
> `grade-proxy`.
> **Forbidden to bounce the task back or output only a question because optional
> input is missing (especially voice sample)**—deliver usable result first, then
> list "send a piece of your own writing to make it sound more like you" as a
> strengthenable item in delivery notes.

## Pre-flight Checks

This skill is pure prompt-driven: no scripts, endpoints, or env vars. Four checks:

1. Does draft have used_materials?—empty array means body shouldn't have any
   personal experience, rewriting only does language calibration.
2. Is grade clear?—not clear means language calibration loses baseline; must ask
   first, don't guess school level.
3. Does body contain experiences the user didn't provide?—if yes, verify first
   (red line 1), delete if verification fails.
4. **Is there a voice sample?**—yes → step 0 branch A (voice alignment); no →
   branch B (grade proxy), and state limitation per honesty declaration 4 at
   delivery.

## Tacit Knowledge (What Makes "sounds like her" Hard)

### 1. Voice Fingerprint Is in Distribution Features, Not "Favorite Words"

Stylometry's decades-long conclusion: **what best distinguishes writers is
function word frequency, sentence length distribution, punctuation rhythm—these
unconscious habits**—stable across topics, hard to deliberately imitate. While
"she likes this word" surface features are exactly the easiest to fake and least
convincing layer.

**Practical implication**: only swapping AI draft words for "student words" yields
a **costume voice**—one "this doesn't sound like you" from the teacher sends it
back. What to change is sentence rhythm: sentence length band (how long her
sentences tend to be), connective habits ("then" vs "afterwards"), punctuation
density (uses exclamation points? comma-chains?).

### 2. Sample Discipline: Too-Short Samples Can't Build a Fingerprint

Stylometry sample size discipline: **sample too short, frequencies unstable,
conclusions unreliable** (short text's stylistic features are noisy). Actionable
rule:

| Sample Size | Usability | Delivery Language |
|---|---|---|
| ≥800 words, same genre as assignment (both narrative/argument) | reliable | can say "aligned to your language habits" |
| 200–800 words | limited | can only say "partially aligned", mark paragraphs that don't align |
| <200 words, or cross-genre (chat record vs essay) | unusable | fall back to grade proxy path, state honestly |

### 3. Negative Lists Work Better Than Positive Instructions

A public real AI ghostwriting system (writing social media content for real
people) published a retrospective; the most counterintuitive finding: **a "what
she would never write" negative constraint list is more useful than a "how to
write" positive instruction**.

Mapped to student scenarios: **"she never uses exclamation points", "she never
writes parallelism", "she never quotes famous lines"**—these exclusions
approximate her voice better than "use more idioms". Method: extract 3–5 negative
constraints from the voice sample (things she doesn't do, fancy expressions
unbefitting her school level), write as a list, honor each during rewriting.

### 4. Editable Style Rules > Raw Sample Pile

Explicitly written style rules ("keep sentences around 15 words", "use 'then'
not 'furthermore'") **can be rejected and corrected by the student line by
line**; while "I imitated your three articles" is implicit, and when the student
says "still doesn't sound like me" there's no entry point.

**Delivery discipline**: deliver the alignment feature list with the final draft
(`voice_alignment.features` in output spec), so the student can say "this one is
wrong".

### 5. Calibration Is Append-Only, Not Retraining

The same system proved: **recording each change and appending to a calibration
file** works better than "relearning". For this skill: when delivering the final
draft, ask the student to send back "what did you change when reading it"—save
the `changes` list together with student-sent-back edits, next rewrite uses this
file directly.

### 6. Material Forced Injection: Feelings Must Land in a Scene

(Carried over from this group's original mechanism) Empty-phrase sentences ("I
understood the meaning of persistence") must be replaced or anchored with real
material in used_materials—otherwise all language processing is putting makeup on
an empty shell. Comparison examples in workflow step 2.

### 7. Human-Touch Micro-adjustments Are Expression-Layer Surgery, Don't Touch Information Layer

Burstiness (two long sentences followed by a ≤8-character short sentence),
abstract to concrete, allow one reasonable colloquialism—these only touch the
expression layer. Numbers, terms, conclusions, quotes are untouched (red line 5).

## Red Lines (Hard Bans, Non-Negotiable)

1. **Don't fabricate experiences the user didn't provide**: rewriting can only
   draw from materials already in used_materials; keep placeholders where
   material is missing and prompt user to supplement.
2. **Final draft retains student's retellable difficulty**: after rewriting, the
   student must be able to retell the whole gist and key details—can't answer
   teacher follow-up = failed delivery.
3. **Deliverable must attach "read through before submitting"**: final draft
   attests transcription advice, suggests the student read it once, casually change
   words to their own habit, then copy by hand or submit.
4. **No guarantee of passing AI detection**: re-audit score dropping is a design
   goal, but promising "teacher won't notice" to the user is forbidden.
5. **Information layer only subtracts, doesn't add**: numbers, terms,
   conclusions, quotes can't change (align with humanize-rewriter's no-change
   list), rewriting only touches expression layer.
6. **Don't claim alignment beyond what the sample supports**: when sample is
   insufficient, honestly downgrade language (table in tacit knowledge 2);
   calling grade proxy "your voice" is false delivery.

## Honesty Declarations

1. **Language calibration band table (20/30/40 word sentence caps, idiom count)
   are empirical values**, not curriculum standard numbers; curriculum standards
   only provide school level divisions, thresholds adjust to actual student level.
2. **Voice alignment reliability depends on sample size and genre match**
   (tacit knowledge 2): short or cross-genre sample conclusions are directional,
   not "fingerprint-level".
3. **Re-audit score comes from same-repo ai-trace-auditor's heuristic basis**,
   hit or not it's not an official judgment; this skill has no affiliation with
   any AI detector.
4. **On the grade proxy path, can only claim "matches school level", not "sounds
   like you"**—these are two different acceptance criteria.
5. This skill aligns at the **language habit layer**, doesn't model dialect,
   internet slang, or other idiosyncratic style (that's personal-voice-profile's
   job, oriented to user-authorized historical text).
6. This skill doesn't rewrite the information layer, nor improve "material
   quality itself"—when material isn't enough to reach word count, the correct
   action is asking user to supplement material, not padding.

## Workflow

### Step 0: Set Calibration Path (Voice Sample Collection)

- **Branch A (with sample)**: extract alignment features from sample, at least
  covering four:
  1. **Sentence length band**: sample's typical sentence length range (like
     "8–18 words, occasional 25-word long sentences")
  2. **Punctuation rhythm**: comma density, uses exclamation points/ellipses?,
     any break-sentence habit
  3. **Connective preference**: connectives actually appearing in sample (like
     "then/afterwards/anyway"), along with **absent** written connectives
     ("furthermore/however/in summary")
  4. **Negative list**: 3–5 "she wouldn't write this" exclusions (tacit
     knowledge 3)
- **Branch B (no sample)**: use the grade band table below, mark
  `voice_alignment.mode` as `grade-proxy`.
- **Expected**: `voice_alignment.mode` is `sample` or `grade-proxy`, `features`
  non-empty.
- **If it fails**: sample under 200 words or genre mismatch → degrade per tacit
  knowledge 2 rules or switch to branch B, don't force-fit features.

Grade band table (branch B; caps are empirical, adjustable):

| School Level | Vocabulary Cap | Single Sentence Cap | Rhetorical Depth | Forbidden Tone |
|---|---|---|---|---|
| Primary | common words, idioms ≤3 per piece | ≤20 words | metaphor/personification 1-2 each | essay tone, four-character pile-up, "firstly secondly lastly" |
| Middle | idioms and written language OK | ≤30 words | parallelism, textbook quotes OK | "in summary" style conclusion, political essay tone |
| High | abstract concepts OK | ≤40 words | dialectical, concessive, rhetorical question OK | empty slogans, famous-line pile-up |

### Step 1: Language Calibration (Execute per step 0 path)

- **Action**: branch A → calibrate sentence by sentence per extracted features
  (sentence band, punctuation, connectives); branch B → scan sentence by
  sentence per band table: split over-cap sentences, swap over-band words for
  common synonyms, rewrite sentences hitting forbidden tone. **Both paths must
  honor the negative list**.
- **Expected**: whole text free of over-band words and over-cap long sentences;
  high school essay doesn't contain "in summary, this paper constructs…";
  negative list honored line by line.
- **If it fails**: some term can't be downgraded (like math proper noun) → keep
  the term, ensure context gives a plain-language explanation.

### Step 2: Material Injection Replace Empty Phrases

- **Action**: find all empty-phrase sentences in body ("I understood the meaning
  of persistence", "this benefited me greatly"), replace or anchor with real
  material in used_materials.
- **Expected**: "last week my brother spilled milk on the workbook, I stared at
  that stain" replaces "I realized the importance of details"—feelings must
  land in a concrete scene.
- **If it fails**: material not enough to cover whole text → list gaps all at
  once and ask user to supplement; where gaps can't be filled, keep
  <<material:xxx>> placeholders, fabrication forbidden (red line 1).

Empty-phrase replacement comparison:

```text
empty: this experience made me understand the meaning of persistence
replacement: by the 4th lap my calves were cramping, but I pushed through—turns out "persistence" is not stopping at that moment

empty: this book is profound, it benefited me greatly
replacement: reading the part where the protagonist gave his last bread to his sister, I stopped and stared at the ceiling for a while

empty: I realized the importance of details
replacement: last week my brother spilled milk on the workbook, I stared at that stain—one second less on the cup lid and the workbook had to be rewritten
```

- **Expected (comparison)**: each replacement satisfies two conditions: feeling
  lands in a scene, scene comes from used_materials.
- **If it fails**: replacement sentence is concrete but no corresponding entry in
  material library → that's fabrication, delete and replace with placeholder.

### Step 3: Human-Touch Micro-adjustments (Restrained Edition)

- **Action**: carry over humanize-rewriter technique but more restrained—two
  long sentences followed by one ≤8-character short sentence (burstiness);
  abstract generalizations to concrete nouns and numbers; allow one reasonable
  colloquialism, one non-flashy parallelism; leave a bit of "wanted to write but
  didn't fully work out" room. **In branch A, this step obeys step 0's extracted
  sentence band, don't mechanically apply ≤8 characters.**
- **Expected**: whole "perfect essay tone" gone; but don't deliberately pile on
  colloquial—student tone is "sincere plainness", not "playing young".
- **If it fails**: over-corrected (too dense colloquial) → roll back previous
  version, lower change density and retry.

### Step 4: ai-trace-auditor Re-check

- **Action**: run ai-trace-auditor on final draft, compare with pre-rewrite
  draft score.
- **Expected**: re-audit score must be lower than pre-rewrite; verdict improves
  at least one band.
- **If it fails**: score rises instead of falls → locate per findings and return
  to step 3 for targeted rework; after two rounds still not passing, honestly
  report remaining trace.

### Step 5: Output Final Draft, Transcription Advice, and Calibration Record

- **Action**: consolidate into final JSON (structure in output spec), must end
  with reminder: "Suggest reading through once before submitting—read aloud,
  change awkward spots to your own phrasing, so when the teacher asks you can
  answer smoothly." **And ask the student to send back 'what did you change'**,
  append sent-back content to `calibration_log` (tacit knowledge 5).
- **Expected**: JSON parseable by json.loads; reaudit.after > reaudit.before;
  read_through_note and voice_alignment present.
- **If it fails**: word count falls below requirements floor → pad with material
  details and rerun step 4, empty-phrase padding forbidden.

Retellability quick test (red line 2 landing, 30 seconds):

```text
1. Ask student to say in one sentence what the final draft is about;
2. Pick a concrete detail to ask ("when did that thing in paragraph 3 happen?");
3. Both answerable → retellable pass; not answerable → simplify that spot or rework.
```

## Output Spec

final JSON structure:

```json
{
  "content": "student-voice final draft",
  "changes": [
    {"pos": "paragraph 2", "before": "I understood the meaning of persistence", "after": "by the 4th lap my calves were cramping, but I pushed through", "why": "empty phrase replaced with concrete scene"}
  ],
  "reaudit": {"before": 42, "after": 78},
  "read_through_note": "Suggest reading through once before submitting: read aloud, change awkward spots to your own phrasing",
  "placeholders": ["<<material:spring trip feelings>>"],
  "grade_check": "primary band: no sentences over 20 words, 2 idioms",
  "voice_alignment": {
    "mode": "sample",
    "features": ["sentence band 8-18 words", "almost no exclamation points", "connective preference: then/afterwards", "few comma-chains"],
    "negative_list": ["no parallelism", "no famous quotes", "no 'in summary'"],
    "confidence_note": "sample about 600 words, both narrative → partial alignment; paragraph 4 material not from sample, treated per grade band"
  },
  "calibration_log": [
    {"round": 1, "student_edits": ["changed 'I wanted to cry a little' to 'my eyes felt a little sore'"], "next_time_rule": "emotion expressed via body-feel words, not direct 'wanted to cry'"}
  ]
}
```

| Field | Constraint |
|---|---|
| changes | each contains before / after / why, traceable line by line |
| reaudit.after | must be greater than before (higher ai-trace-auditor score = more human-like) |
| read_through_note | required (red line 3) |
| grade_check | state which school band used and verification conclusion |
| voice_alignment.mode | `sample` or `grade-proxy` (honesty declaration 4 landing) |
| voice_alignment.negative_list | non-empty (tacit knowledge 3); on grade-proxy it's the school-band forbidden tone list |
| calibration_log | first delivery can be empty array; append after student sends back edits (tacit knowledge 5) |

## Built-in Verification Steps (Check Each Before Delivery)

- [ ] **Material traceability**: every scene, number, feeling traceable to
  used_materials, no fabrication (red line 1)
- [ ] **Retellability**: student can complete retell quick test (red line 2)
- [ ] **Information layer intact**: numbers/terms/conclusions/quotes match draft
  (red line 5)
- [ ] **Calibration consistency**: sentence length and punctuation match step 0
  features (branch A) or band table (branch B)
- [ ] **Negative list honored**: `negative_list` checked line by line, none
  violated (tacit knowledge 3)
- [ ] **Honest labeling**: `voice_alignment.mode` truthful; when sample
  insufficient, degraded language per tacit knowledge 2
- [ ] **Placeholder cleanup**: search whole text for `<<material:`, if any
  remain, prompt material supplement or delete that paragraph
- [ ] **Re-audit comparison**: reaudit.after > before

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Re-audit score rises instead of falls | Introduced new boilerplate while downgrading | Locate per findings and rework, after two rounds honestly report remaining trace |
| Material can't support whole text | User gave too little | List gaps all at once and ask for supplement; keep placeholders where gaps remain, fabrication forbidden |
| Student says "doesn't sound like me" | Wrong calibration path or wrong negative list | Ask student for a piece of their own writing (even 200 words), redo step 0 branch A |
| Student can't provide sample | Common situation | Go grade proxy, delivery per honesty declaration 4 only claim "matches school level", not "sounds like you" |
| Sample is chat record / cross-genre | Genre mismatch | Degrade per tacit knowledge 2 (only partial alignment), or switch to grade proxy |
| Word count below floor | Deleted empty phrases too aggressively | Pad with real details (material expansion), no empty phrases |
| Student fears teacher follow-up | Retellability not passing | Have student do a retell exercise on final draft, simplify stuck spots until retellable |
| Upper grade still carries essay tone | Step 1 band used wrong | Re-scan sentence by sentence per forbidden tone list |
| Teacher demands "flowery style" | Conflicts with human-touch goal | Teacher requirement wins—elevate literary quality, but material must still be real |
| Body contains famous quotes | User draft came with them | Keep quotes and verify source annotation not lost (red line 5) |
| Math/English questions made ambiguous by changes | Expression-layer changes hit terms | Roll back that sentence: science terms and English sentence-framework can't be downgraded, only explanatory text |
| Student crosses grade band (like repeat-year) | Band table only has three | Pick nearest band per actual writing level, note band-pick reason in grade_check |
| Placeholder left in final draft | Step 5 consolidation missed | Search whole text for <<material: before delivery, if any remain first prompt user to supplement material or delete that paragraph |

## Delivery Criteria

- final JSON parseable by json.loads, reaudit.after > reaudit.before.
- changes traceable line by line: each before locatable in draft, each after
  locatable in final.
- Whole text no fabricated material: every scene, number, feeling traceable to
  used_materials.
- Calibration passes: no over-band vocabulary, no over-cap long sentences, no
  forbidden tone hits; negative list honored line by line.
- `voice_alignment` trio present (mode/features/negative_list), mode matches
  actual sample situation.
- read_through_note present; student can complete one retell against final draft.

## References

- `references/sources-and-methodology.md` — stylometric basis for voice
  alignment, source of negative list and append-only calibration, grade
  calibration basis and honest boundaries. **Must read when externally
  attributing or needing to explain "why align this way".**

## Pipeline Position

- Upstream: solution-drafter (required—this skill only takes draft JSON).
- Linked: ai-trace-auditor (re-check after changes, step 4); humanize-rewriter
  (writing domain same-source technique, this skill more restrained plus voice
  alignment layer).
- Downstream: feynman-explainer loop—retell final draft to someone (retell =
  internalize), paragraphs that don't read smoothly go back to rework.
