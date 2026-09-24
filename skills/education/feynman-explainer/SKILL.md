---
name: feynman-explainer
description: >-
  Teach one concept interactively via the Feynman loop: simplest-possible
  explanation, one diagnostic question, inspect the learner's answer for gaps,
  repair with analogy or worked example, require teach-back, then a transfer
  challenge — with depth control per learner level. Use when the user asks to
  explain a concept / teach me this / explain in plain language / why don't I
  understand / teach-back, or when exercise results show a failed checkpoint
  needing remedial teaching. Do NOT use for course skeleton design
  (course-designer), nor for generating question banks (exercise-generator).
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

# Feynman Explainer

Single-concept **remedial tutoring**. Core is the Feynman loop—explain, ask,
check, repair, teach-back, transfer, not a link missing. Core belief: **if you
can explain it clearly, you truly understand it**; where the learner can't explain
is where your next paragraph needs repair.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Concept | yes | one concept per loop, don't bundle |
| Learner profile | no | from learning contract; defaults to beginner if missing |
| Blocker clue | no | lost-point elements from exercise grading—aims directly at the blocker if present |

When inputs are missing, ask all at once: "Please provide: 1) concept to explain
(one at a time); 2) learner's current level (defaults to beginner); 3) blocker
clue (like exercise lost-point elements, optional)."

## Pre-flight Checks

This skill is pure prompt-driven: no runtime dependencies, endpoints, or env
vars. Self-check is on input not environment: concept not given → ask all first
then STOP; multiple concepts given at once → split into loops one by one, don't
bundle.

## Workflow

### Step 1: Set Explanation Level by Depth Control

| Level | Explanation Discipline |
|------|----------|
| beginner | Establish vocabulary first (each term with a plain-language sentence), everyday cases, only ask "what/why" |
| intermediate | Compare easily confused approaches, explain failure modes, ask "what scenario breaks" |
| advanced | Go straight to boundaries and trade-offs, ask transfer and synthesis |
| exam | Add timed recall, scoring criteria comparison, common trap list |

### Step 2: Run Feynman Loop (Six Beats, None Missing)

```text
1. Explain: walk through the concept with a minimal usable model (one analogy + one mechanism sentence)
2. Ask: pose one diagnostic question—probes core mechanism, not memory
3. Check: inspect the answer—find missing elements / vague wording / false confidence / hidden assumptions
4. Repair: target the gap with a simpler analogy or a worked example, don't repeat original words
5. Teach-back: require learner to explain back in their own words (without your phrasing)
6. Transfer: switch to a superficially unrelated scenario and ask again
```

### Step 3: Role-Play "Not-Very-Smart Student" (Advanced Teach-Back)

When the learner is stuck, switch modes: you play the student who makes
mistakes, explain a key point of the concept wrong, ask the learner to
correct—**correcting someone else's error exposes deeper understanding than
repeating the right answer**. Learner corrects correctly = passed; can't
correct means the blocker isn't cleared, return to beat 4 with a new analogy.

### Step 4: Close Loop and Chain

Output: concept pass judgment + blocker repair record (which element, what
analogy used). After passing, **hand back to exercise-generator to retest the
checkpoint from a different angle**—mastery loop closes: fail test → Feynman
re-teach → retest.
- Expected: pass judgment grounded (teach-back or correction success), repair
  record traceable to a specific element.
- If it fails: retest still fails → return to beat 2 with a new diagnostic
  question for another round, at most two rounds then honestly report "this
  concept needs a prerequisite knowledge route", hand back to course-designer.

## Delivery Criteria

- Artifact: pass/fail judgment + blocker repair record (blocker element → analogy/
  example used → verification method).
- Location: output directly in conversation (this skill doesn't write files).
- Integrity verification: all six beats completed (with corresponding artifacts);
  pass judgment comes from learner's teach-back or correction performance, not
  self-declared.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Learner can repeat but can't apply | Only did "explain/teach-back", skipped transfer | Add beat 6, switch scenario and ask again |
| Analogy misleads | Analogy too far from mechanism | When switching analogies, explicitly state "where the analogy doesn't match" |
| More confusing the more explained | Poured multiple concepts at once | Return to input discipline: one concept per loop |
| Learner passive throughout | Six beats became a monologue | Each beat must end with a question or teach-back |

## References

Feynman loop and depth control source: see course-designer's
sources-and-methodology.md (shared within pack).
