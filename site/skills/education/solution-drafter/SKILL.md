---
name: solution-drafter
description: >-
  Draft a homework solution per assignment type from an assignment-plan: math goes
  analyze→set up→step-by-step→verify with no skipped steps, essays go
  thesis→material allocation→paragraph outline→write, reports stay outline-first,
  English uses sentence frames then fills content; every step shows full working
  and the draft self-checks against every requirement in the plan. Middle stage
  of the homework-autopilot chain — the draft is deliberately AI-neat and must
  pass through own-voice-rewrite. Use when the user asks to draft a solution /
  answer by type / write first draft / solve homework / draft solution. Do NOT use
  without an assignment-plan from assignment-intake, nor during live exams.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: education
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-16"
---

# Solution Drafter (Answer by Type)

First-draft machine. Takes assignment-plan and real material, routes by type to
the corresponding execution template, producing a "neat but AI-flavored"
draft—neatness is this skill's job, human warmth is downstream own-voice-rewrite's
job, two layers not mixed.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| assignment-plan | yes | JSON from assignment-intake; without it, return upstream to run analysis first |
| Real material | yes* | Corresponds to plan.needed_materials; *when materials can't be gathered, placeholder mode allowed |
| Clarification answers | no | User's responses to plan questions |

When inputs are missing, ask all at once:

> Two things still missing: 1) assignment-plan (result of previous step's
> analysis; if not, I'll run assignment-intake first); 2) the parts of the
> material list you can provide. Tell me everything you can't provide, I'll start
> in placeholder mode.

## Pre-flight Checks

This skill is pure prompt-driven: no scripts, endpoints, or env vars. Three checks:

1. Is assignment-plan there? Are type and requirements / scoring_points readable?—
   missing → return upstream, don't start bare.
2. Are materials aligned?—line by line against needed_materials into
   "provided / missing" two columns; missing marked as placeholders, no
   opportunistic fabrication.
3. Is this an exam in progress?—plan.notes or user context shows exam hall →
   triggers red line 1, stop.

## Red Lines (Hard Bans, Non-Negotiable)

1. Exams and in-class quizzes don't use this chain: same source as
   assignment-intake red line 1, effective chain-wide; this skill likewise refuses
   exam-hall requests.
2. used_materials only records real material the user provided: every
   experience, number, data point appearing in body must be traceable to
   used_materials; if not found, delete.
3. Math must verify: math problems without a verification line can't be delivered.
4. Quoting others' content must be attributed: famous lines, sample essay
   fragments, textbook definitions must note source; disguised as original is
   forbidden.
5. Science steps can't skip: skipped step = student can't follow = delivery failure.

## Workflow

### Step 1: Align Plan and Materials

- **Action**: Check needed_materials line by line into "provided / missing" two
  columns; missing items marked <<material:xxx>> in body.
- **Expected**: alignment table complete, no ambiguous ground.
- **If it fails**: user sends new material mid-way → add to used_materials and
  rerun this step.

### Step 2: Route Execution by Type

Enter corresponding template per plan.type, implement plan.plan steps item by
item:

| type | Execution Template | Output Form |
|---|---|---|
| math | analyze (given/asked) → set up → step-by-step → verify | step process + answer + verification line |
| essay | thesis (one-sentence central point) → material to paragraphs → paragraph outline → write | full article + paragraph outline attached |
| diary / reading_response | set date or book → set feeling anchor (which event/plot) → narrative+discussion combined | body + feeling anchor annotation |
| english_writing | review points → sentence frames (1-2 sentences per point) → fill content → grammar self-check | English body + point coverage table |
| handmade_poster | set theme → layout zones (title zone/content zone/illustration zone) → write copy zone by zone | layout plan + per-zone copy |
| slides | set outline (one conclusion per slide) → per-slide points → speaker notes | slide-level outline + per-slide copy |
| survey_report | outline confirm (method/data/analysis/conclusion four paragraphs) → fill paragraph by paragraph | outline + written text |
| lab_report | fill per template order: objective/apparatus/steps/records/conclusion/reflection | six-paragraph report; records section only fills real data |
| other | execute per plan.plan step sequence | matches step sequence |

- **Action (continued)**: after completing each paragraph during template
  execution, look back at plan.requirements to prevent drift.
- **Expected**: output form matches table; essay text doesn't exceed 110% of
  word count cap (empirical, adjustable).
- **If it fails**: template conflicts with plan → plan.requirements wins,
  template yields.

math template minimal example (four steps, none missing):

```text
Problem: Two cities A and B are 360 km apart; a car completes the trip in 3 hours. What is the average speed in km per hour?
  Analyze: given distance 360 km, time 3 hours; find average speed
  Set up: 360 ÷ 3
  Step-by-step: 360 ÷ 3 = 120 (km/hour)
  Verify: 120 × 3 = 360, matches given distance ✓
```

essay template minimal example (outline first):

```text
Problem: "A Small Incident"
  Thesis: a family's care is hidden in small things
  Material allocation: opening scene (spilled milk) → middle (who cleaned it, what I thought) → ending (feelings at the time)
  Outline: 4 paragraphs, one-sentence summary each, expand paragraph by paragraph when writing
```

- **Expected (example comparison)**: own output matches example granularity—each
  step one line, grounded, verifiable or traceable.
- **If it fails**: output granularity clearly coarser than example (one step
  merged three) → split per example and rewrite that part.

### Step 3: Show Complete Process

- **Action**: science each step writes "why do it this way"; essay attaches outline
  after body.
- **Expected**: student can retell each step's basis following the draft.
- **If it fails**: some step you can't explain why yourself → stop and re-solve,
  fudging through is forbidden.

### Step 4: Self-Check Against Requirements Item by Item

- **Action**: turn plan.requirements into checklist items, judge pass / fail line
  by line; go through scoring_points simultaneously.
- **Expected**: checklist_pass covers 100% of requirements; fail items fixed on
  the spot then rechecked.
- **If it fails**: fail that can't be fixed (like insufficient material) → mark
  fail honestly with reason, silent pass-through forbidden.

### Step 5: Output Draft and Hand Off

- **Action**: consolidate into draft JSON (structure in output spec), then say:
  "First draft complete, neat but AI-flavored, continue calling own-voice-rewrite
  to make it student-voice."
- **Expected**: JSON parseable by json.loads; content and checklist_pass
  correspond to the same body.
- **If it fails**: content changed but forgot to sync checklist → rerun step 4,
  delivering stale self-check is forbidden.

## Output Spec

draft JSON structure:

```json
{
  "content": "full first draft (or step-by-step solution)",
  "checklist_pass": {
    "no less than 400 words": "pass",
    "must have scene description": "pass"
  },
  "used_materials": [
    "user provided: last week brother spilled milk on workbook"
  ],
  "outline": "paragraph outline (attached for essay types)",
  "verify_line": "verification line (required for math type)",
  "placeholders": ["<<material:spring trip feelings>>"]
}
```

| Field | Constraint |
|---|---|
| checklist_pass | key corresponds one-to-one to plan.requirements, values only pass / fail |
| used_materials | only real material (red line 2); empty array legal, but body must not contain any personal experience |
| verify_line | required when type=math and verification holds |
| placeholders | matches <<material:xxx>> count in body |

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Math result doesn't verify | Setup or computation error | Return to setup and re-derive, fix until verification passes, "answer roughly right" forbidden |
| Body contains material not provided | Red line 2 bypassed | Delete that spot or replace with placeholder, rerun step 4 |
| Word count over or under | Writing out of control | Over: cut modifier sentences; under: pad with material details, recheck after |
| User directly wants final version | Skipping downstream | Deliver draft and explain: student-voice must go through own-voice-rewrite |
| Problem itself ambiguous | Upstream didn't clarify | Return to assignment-intake to ask more, don't guess-answer |
| Lab report has no real data | Student didn't do experiment | Records section all placeholders, fabricating data forbidden (same source as red line 2) |
| English essay missed points | Point coverage table not aligned | Fill missed points then rerun step 4 |
| Two problems' steps cross-reference confusingly | Problem order mixed | Each problem independent block, renumber |
| type=other has no set template | Upstream categorized as other | Strictly execute per plan.plan sequence, each step a paragraph, no free play |
| Material doesn't match problem timeline | Student misspoke or misremembered | Confirm with user then fix timeline, force-fitting into problem scenario forbidden |
| Hand-copied poster / PPT only wrote copy | Ignored layout dimension | Fill in zone plan or slide-level outline; missing layout doesn't count as delivered |

## Delivery Criteria

- draft JSON parseable by json.loads, checklist_pass covers all requirements.
- When type=math, verify_line exists and verification holds.
- Every personal material in body traceable in used_materials; placeholders
  correspond one-to-one with body placeholders.
- Science each step grounded, no skipped steps; quoted content all attributed.
- First draft explicitly marked "neat but AI-flavored"—this is intentional
  intermediate state, not a defect.

## References

- `references/sources-and-methodology.md` — read when you need to explain math
  four-step solving source (Polya), process writing method source, or external
  attribution.

## Pipeline Position

- Upstream: assignment-intake (required, provides assignment-plan and material list).
- Downstream: own-voice-rewrite (required—draft is "AI-flavored neat version",
  student-voiceization isn't this skill's job).
- Parallel: exercise-generator writes questions from knowledge points; this skill
  answers from questions, opposite direction; course-designer's exam-band
  checkpoints can be practice source for this skill.
