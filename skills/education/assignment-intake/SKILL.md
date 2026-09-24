---
name: assignment-intake
description: >-
  Parse a homework assignment into a machine-usable assignment-plan JSON:
  identify the type via a 9-type decision table (essay / diary / reading
  response / math / english writing / handmade poster / slides / survey report /
  lab report), extract hard requirements (word count, format, deadline,
  must-include, forbidden items) with per-item evidence, map scoring dimensions,
  and list the personal materials the student must supply. Entry point of the
  homework-autopilot chain; output feeds solution-drafter. Use when the user asks
  for assignment intake / homework analysis / parse assignment requirements /
  break down homework / solve homework. Do NOT use during live exams or quizzes,
  nor for pure tutoring questions without a graded deliverable.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: education
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Assignment Intake (Assignment Analysis and Breakdown)

"Help me do my homework" can't start from one sentence. This skill breaks the
assignment text into a machine-executable assignment plan: what type, what the
teacher cares about (hard requirements), where the points are (scoring points),
and which real materials the student still needs—outputting an assignment-plan
JSON that is the foundation of the homework-autopilot chain.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Assignment text | yes | Photo transcription / direct paste / oral transcription all OK; doesn't accept "you know, that essay the teacher mentioned" paraphrase |
| Grade and subject | yes | "5th-grade Chinese"—determines default scoring dimensions and downstream language level calibration |
| Existing material | no | Experiences / feelings / data the student already thought of; missing doesn't block, filled by step 5 list |

When required items are missing, ask all at once (one round, no second
follow-up):

> Please provide: 1) the assignment text (photo transcription or full paste);
> 2) grade and subject; 3) deadline (no need to answer if written in the
> original). Any existing ideas, experiences, or data can be sent along; if not,
> no problem—I'll list what's still missing in the plan.

## Pre-flight Checks

This skill is pure prompt-driven: no scripts, endpoints, or env vars. Before
starting, verify three points:

1. Is the assignment text complete?—If transcription ends with "..." or "and
   more after", get the full text first before breaking it down; a half
   assignment's requirements will definitely be missing.
2. Are grade and subject clear?—Both missing isn't complete; scoring point
   mapping depends on school level.
3. Is this an exam in progress?—User sends the assignment while in an exam,
   in-class quiz, or timed homework → triggers red line 1, stop immediately.

## Red Lines (Hard Bans, Non-Negotiable)

1. Exams and in-class quizzes don't use this chain: any request to break down an
   assignment during an exam, quiz, or timed homework is refused, with an
   explanation that this is a post-class homework flow.
2. Never fabricate personal experiences: experiences/feelings/data listed in
   needed_materials that the user didn't provide are simply not there—prefer
   starting with placeholder gaps over inventing "my grandma" or "last week's
   competition" details.
3. Only break down, don't answer: this skill forbids outputting any answer
   content; answering is downstream solution-drafter's job.
4. Requirements traceable line by line: every hard requirement must attach an
   original-text quote (evidence); items not in the original are marked
   not_specified; don't invent "teacher asked for 800 words".

## Workflow

### Step 1: Ingest Assignment Text

- **Action**: Get original text and grade/subject, note source (photo
  transcription / paste / oral).
- **Expected**: complete text in hand, grade/subject clear.
- **If it fails**: transcription has garbled chars or missing pages → point out
  the gap and ask user to resend; ask clearly once, don't guess character by
  character.

### Step 2: Type Identification (Decision Table)

- **Action**: Judge line by line per the table below, take the first matching
  row; output a single type.

| Type | Criterion (match if satisfied) | Typical Wording Signals |
|---|---|---|
| essay | Has title or topic + requires writing + no "reading/viewing/survey" qualifier | "write an essay", "no less than 600 words" |
| diary | Title or requirement includes diary/weekly journal + has date or "record a day/week" | "write a diary", "one weekly journal" |
| reading_response | Requires writing feelings about a book, article, or film | "thoughts after reading XX", "viewing response" |
| math | Has specific numbers and question, answer verifiable | "solve", "set up and calculate", "word problem" |
| english_writing | Question in English and requires writing | "Write a passage about..." |
| handmade_poster | Requires hand-made or digital layout with text and images | "hand-copied poster", "blackboard newspaper", "illustrated" |
| slides | Requires multi-page presentation in slides | "make a PPT", "no less than 8 pages" |
| survey_report | Requires collecting data, questionnaire, or interview then writing | "survey", "questionnaire", "collect stats" |
| lab_report | Has experiment steps or observation record template | "lab report", "objective", "procedure" |

- **Expected**: type unique; composite assignments (like "survey + PPT
  presentation") split into main plan + secondary plan, marked primary / secondary.
- **If it fails**: none of the nine types match → categorize as other, note
  uncertainties in notes and ask user to confirm; don't force-fit.

### Step 3: Extract Hard Requirements

- **Action**: Extract line by line from original: word count, format (manuscript
  paper / lined notebook / page count), deadline, must-include points (like
  "must have scene description"), forbidden items (like "real school name must
  not appear").
- **Expected**: requirements[] each contains item + evidence (original quote) +
  status (specified / not_specified).
- **If it fails**: original doesn't mention some dimension at all → that item's
  status is not_specified; don't invent by convention.

### Step 4: Map Scoring Points

- **Action**: Give default scoring dimensions by type, each written as a
  judgeable checkpoint:

| Type | Default Scoring Dimensions |
|---|---|
| essay / diary / reading_response | Thesis on topic / structure complete / material real and specific / writing quality and presentation |
| math | Setup correct / steps complete / computation accurate / has verification |
| english_writing | Points covered / grammar accurate / varied sentence structure / proper conventions |
| handmade_poster / slides | Theme prominent / layout structure / content substantial / text-image coordination |
| survey_report | Method explained / data real / analysis grounded / conclusion matches data |
| lab_report | Steps complete / records truthful / conclusion matches observation / has reflection |

- **Expected**: scoring_points[] total 3-6 items, all judgeable ("has
  verification" is OK, "well written" is not).
- **If it fails**: teacher gave explicit scoring criteria → replace default
  dimensions wholesale with teacher criteria, note source: teacher.

### Step 5: Real Materials List (Key Step)

- **Action**: List personal real materials the student must provide to complete
  this assignment, targeted by type: essay/diary needs personal experience and
  feelings at the time; reading_response needs evidence of actually reading
  (most memorable plot); math needs the original problem text (students copying
  the problem wrong is most common); survey_report needs actually collected
  data; lab_report needs real experiment records.
- **Expected**: needed_materials[] each contains material + why +
  how_to_provide; accept what can be given on the spot, rest go to placeholders.
- **If it fails**: user says "make it up" → triggers red line 2, explain why
  not, then start with missing materials.

### Step 6: Output Plan and Hand Off

- **Action**: Consolidate into assignment-plan JSON (structure in output spec),
  then say: "Analysis complete, continue calling solution-drafter to answer by
  type."
- **Expected**: JSON parseable by json.loads; plan[] corresponds one-to-one with
  scoring points.
- **If it fails**: JSON serialization fails → fix escaping and re-output;
  delivering half-structured text is forbidden.

## Output Spec

assignment-plan JSON structure:

```json
{
  "type": "essay",
  "grade_subject": "5th-grade Chinese",
  "requirements": [
    {"item": "no less than 400 words", "evidence": "original: no less than 400 words", "status": "specified"}
  ],
  "scoring_points": ["thesis on topic", "structure complete", "material real and specific", "writing quality and presentation"],
  "needed_materials": [
    {"material": "a small personal experience", "why": "core material for narrative essay", "how_to_provide": "tell orally or list 2-3 candidates"}
  ],
  "plan": ["determine thesis and material", "outline paragraphs", "write"],
  "notes": "composite assignments mark primary/secondary here"
}
```

| Field | Constraint |
|---|---|
| type | One of step 2 decision table enum values (essay / diary / reading_response / math / english_writing / handmade_poster / slides / survey_report / lab_report / other) |
| requirements[].status | specified / not_specified, no third state allowed |
| scoring_points | 3-6 items, all judgeable |
| needed_materials | Empty array allowed (when materials complete), but no fabricated content allowed |
| plan | Step sequence, matches solution-drafter execution order |

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Photo transcription has typos | Blurry photo / handwriting | Point out suspicious spots for user to confirm; numbers and problem conditions must be human-confirmed |
| Composite type | "survey + presentation" combo | Main plan marked primary, secondary part secondary, downstream executes separately |
| Materials can't be gathered | User won't provide | Start with missing materials, plan marks <<material:brief>> placeholders, never fabricate |
| Teacher criteria conflict with default dimensions | Step 4 used default table | Replace wholesale with teacher criteria, note source: teacher |
| Vague problem ("write an article") | Missing type and word count | Categorize as other, ask type and word count clearly then output plan |
| User asks for help during exam | Hits red line 1 | Refuse and explain boundary, provide no breakdown or answer |
| User only wants answer, not plan | Skipping foundation | Insist on assignment-plan first—answering without requirements can't self-check |
| Oral problem not fully remembered | Student memory lapse | Ask user to check workbook or group notice to complete, don't break down on "roughly like this" |

## Delivery Criteria

- assignment-plan JSON parseable by json.loads, six top-level fields complete.
- Each requirement carries evidence and can be located in original; not_specified
  marked honestly.
- Type identification grounded: can point to which row and which criterion in
  the decision table matched.
- needed_materials only contains "student must provide" items, no fabricated
  material.
- Student can understand the plan—what to do for this assignment, what's being
  checked, what's missing—three things on one page.

## References

- `references/sources-and-methodology.md` — read when you need to explain type
  classification basis, scoring dimension source (Bloom's taxonomy), or external
  attribution.

## Pipeline Position

- Upstream: teacher-assigned original (photo / paste / oral); mirrors
  exercise-generator (teacher-side question writing)—that generates questions
  from knowledge points, this reconstructs requirements from questions.
- Downstream: solution-drafter (required, receives this skill's assignment-plan
  and materials list).
- Red line reminder: exams and in-class quizzes don't use this chain; no skill
  in the chain is exempt.
