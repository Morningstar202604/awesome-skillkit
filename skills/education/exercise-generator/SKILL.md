---
name: exercise-generator
description: >-
  Generate strict mastery exercises for course checkpoints: open-ended conceptual
  questions (MCQ banned to prevent guessing), difficulty ladder (recall / apply /
  transfer), answer rubric with point bands, and common-trap annotations.
  Machine-checkable block format enforced by exercise_lint.py. Use when the user
  asks to generate exercises / make a quiz / practice questions / question bank /
  exam practice, or automatically after course-designer produces checkpoints. Do
  NOT use for designing the course skeleton (course-designer), nor for teaching
  interactively (feynman-explainer).
license: Apache-2.0
compatibility: Python 3.8+ (exercise_lint.py); no third-party dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: education
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Exercise Generator

Generate **guess-proof strict exercises** for checkpoints. Core discipline:
**open-ended questions primary, multiple choice banned by default**—MCQ can be
guessed right 25% of the time, and guessed-correct scores contaminate "is
mastered" judgment, destroying mastery design.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| checkpoint | yes | course-designer output (judgeable goal) |
| Question type mix | no | default concept explanation 2 + application 2 + transfer 1 |
| Difficulty | no | follows learner profile, no separate easing |

When inputs are missing, ask all at once: "Please provide: 1) checkpoint to
write exercises for (judgeable goal); 2) question count/type mix (default
concept explanation 2 + application 2 + transfer 1); 3) learner difficulty
level (beginner/intermediate/advanced/exam)."

## Pre-flight Checks

```bash
test -f scripts/exercise_lint.py && echo LINT-OK
# python3 scripts/exercise_lint.py --text "### Q1 [recall]\nquestion: x\nreference answer: y\nscoring: z\ncommon trap: w\nrelated: CP1" ; echo "exit=$?"
```

- Expected: `LINT-OK` appears; second command exit code `0` (minimum valid
  block passes). Failure means skill package incomplete, STOP and suggest
  reinstall.
- Without Python, degrade to manual five-field review, note "not machine-linted"
  in delivery.

## Workflow

### Step 1: Write Questions by Difficulty Ladder

| Level | Example Question | Judgment |
|------|----------|------|
| recall | "Define X in your own words, don't copy textbook sentences" | Does it cover core elements |
| apply | "Given scenario S, how would you use X to solve it, write steps" | Do steps correctly use the mechanism |
| transfer | "In superficially unrelated T scenario, which property of X applies" | Does it grasp the invariant |

### Step 2: Output Each Question as Five-Field Block

```markdown
### Q1 [apply]
question: Given <specific scenario>, <question requiring the checkpoint mechanism>
reference answer: <list of key elements; full elements = full points>
scoring: 5-point scale—each key element 1 point + complete expression 1 point; deduct by band for missing elements
common trap: <the pitfall learners most often fall into, checked first when grading>
related: CP2
```

Discipline: **scoring criteria written with the question** (can't invent criteria
when grading); common traps come from the checkpoint's easily confused concepts;
each question marks its checkpoint; passing judgment doesn't cross questions.

### Step 3: Run Exercise Lint (Machine Gate)

```bash
python3 scripts/exercise_lint.py --file assets/sample-quiz.md   # bundled sample (contains ### Q1 [recall] block); replace with your quiz.md
```

Check: five fields complete, difficulty label valid, checkpoint reference
exists; **MCQ banned by default** (anti-guessing is this skill's discipline,
script enforces it). Non-zero exit = violation, fix line by line then rerun until
exit 0.

### Step 4: Chain Handoff

Deliver question bank (lint all green). **Then say: "Question bank ready, can
hand to feynman-explainer for remedial tutoring on failed concepts"**—mastery
loop: fail test → Feynman re-teach → retest.
- Expected: downstream gets lint-passed question bank, each question carries
  scoring criteria and common traps, grading needs no invention.
- If it fails: learner feedback that everyone lost points on a question → return
  to course-designer to recalibrate level (see failure table), not to water down
  questions on the spot.

## Delivery Criteria

- Artifact: question bank markdown (each question a five-field block, starting
  `### Q<N> [difficulty]`, marked with related checkpoint).
- Location: output in conversation alongside checkpoint; when saving to file,
  name `quiz.md` (lint input convention).
- Integrity verification: `python3 scripts/exercise_lint.py --file
  assets/sample-quiz.md   # bundled sample (contains ### Q1 [recall] block);
  replace with your quiz.md` exit code 0 (status: clean); question count and
  type mix match input convention.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Learner guessed right | Used MCQ | Default config already bans MCQ, rerun lint until exit 0 (`--allow-mcq` is violation easing, forbidden) |
| Answer-anchored still scores high | Question stem contains answer keywords | Rewrite stem, scenario-packaged |
| Grading scale drifts | Scoring criteria missing or vague | Five-field block mandatory, element-based scoring |
| Everyone fails | Difficulty above checkpoint goal | Return to course-designer to recalibrate level, not add easy questions |

## References

Mastery quiz design source: see course-designer's sources-and-methodology.md
(shared within pack).
