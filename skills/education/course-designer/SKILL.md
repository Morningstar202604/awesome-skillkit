---
name: course-designer
description: >-
  Design a mastery-based course from a topic: learning contract
  (scope/level/target/constraints, <=3 questions), checkpoint breakdown with
  dependency order, per-module study path, and exam-mode adjustments. Chain
  entry of edu-craft — checkpoints feed exercise-generator directly. Use when
  the user asks to design a course / make an outline / study plan / syllabus /
  curriculum / teach me a subject / lesson design. Do NOT use for generating
  exercises (exercise-generator), nor for interactive concept teaching
  (feynman-explainer).
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: education
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Course Designer

Chain entry. Turn a topic into a **mastery-based course package**. Core is
**learning contract first**—without defining "what level counts as mastered," a
course is just a random pile of knowledge points; all the value of mastery design
is in the dependency ordering of checkpoints.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Topic | yes | "Intro to Deep Learning" / "explain photosynthesis to middle schoolers" |
| Learner profile | yes (ask if missing, ≤3 questions) | Current level / target outcome (can explain? can do? can pass exam?) / time budget |
| Constraints | no | Textbook scope, forbidden prerequisites, language |

When inputs are missing, ask all at once (≤3 questions, one round): "Please
add: 1) current level; 2) what you want to be able to do by the end (explain /
do / take exam); 3) weekly time available. If there's textbook scope or
forbidden prerequisites, note those too."

## Pre-flight Checks

This skill is pure prompt-driven: no runtime dependencies, endpoints, or env
vars. Only self-check:

```bash
test -f references/sources-and-methodology.md && echo OK
```

Expected output `OK`; failure means skill package incomplete—mastery design
discipline (step 2 ordering discipline, step 3 depth control) still executable,
note methodology doc missing in delivery.

## Workflow

### Step 1: Establish Learning Contract (≤3 questions)

```markdown
- scope:      what to learn, to what boundary (saying what NOT to learn matters equally)
- level:      beginner / intermediate / advanced / exam
- target:     by the end, what can be explained, what can be built, what can be passed
- constraints: time box / preferred case domain
```

When info is sufficient, state assumptions and continue directly; **don't use
three questions as an opening stall**.

### Step 2: Checkpoint Breakdown (4-6, dependency ordered)

```markdown
CP1 Concept map: can draw X vs Y relationship in your own words
  ↓ (depends on: CP1 vocabulary)
CP2 Core mechanism: can explain why X happens
CP3 Hands-on application: can use X to solve a concrete problem in a given scenario
CP4 Transfer challenge: can apply X to a superficially unrelated new scenario
```

Ordering discipline: **each checkpoint depends only on already-passed
checkpoints**—if forward dependency appears, split and reorder. Each outcome
must be judgeable ("can explain" OK, "understand" not).

### Step 3: Adjust Content by Depth Control

| Level | Content Focus |
|------|----------|
| beginner | vocabulary first, everyday cases, recognition-type questions |
| intermediate | approach comparison, failure modes, application-type questions |
| advanced | edge cases, trade-offs, transfer and synthesis |
| exam | add recall training, timed questions, scoring criteria, common traps |

### Step 4: Chain Handoff

Deliver course package (contract + checkpoints + per-module study path). **Then
say: "Course skeleton ready, continue calling exercise-generator to generate
exercises for each checkpoint, or feynman-explainer for single-concept tutoring"**—
the chain unfolds automatically.
- Expected: downstream gets each checkpoint goal judgeable, dependencies ordered,
  can generate questions directly.
- If it fails: learner mid-feedback that starting point is wrong → return to
  step 1 to recalibrate level, insert bridge module, don't overthrow the whole
  package.

## Delivery Criteria

- Artifact: one course package = learning contract (4 fields) + 4-6 checkpoints
  (with dependency annotations) + per-module study path.
- Location: output directly in conversation (this skill doesn't write files),
  for exercise-generator / feynman-explainer to reference.
- Integrity verification: each checkpoint goal uses "can explain / can build /
  can pass" phrasing (judgeable); dependencies only point to earlier checkpoints;
  total duration ≤ contract time box.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Jump between checkpoints | Forward dependency | Split and reorder, ensure only depends on passed items |
| Learner can't keep up | Starting point above current level | Return to contract to recalibrate level, insert bridge module |
| Outcome not judgeable | Goal written as "understand/familiar" | Rewrite as "can explain / can build / can pass" |
| Course too long to finish | Didn't honor time box | Cut checkpoint count per constraints, keep dependencies intact |

## References

- [sources-and-methodology.md](references/sources-and-methodology.md) — source
  for mastery learning and learning contracts.
