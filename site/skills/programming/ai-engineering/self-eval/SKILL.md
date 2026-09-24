---
name: self-eval
description: "Honestly evaluate AI work quality using a two-axis scoring system. Use after completing a task, code review, or work session to get an unbiased assessment. Detects score inflation, forces devil's advocate reasoning, and persists scores across sessions. Use when the user runs /self-eval, asks to evaluate my work quality / self-assessment / review this task / check if the score is inflated / honest review / rate my work. Do NOT use for grading user answers or producing production artifacts."
license: Apache-2.0
compatibility: Pure prompt-based; no external tools. May append to `.self-eval-scores.jsonl` in the working directory.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: ai-engineering
  verified-date: "2026-09-09"
---

# Self-Eval: Honest Work Evaluation

Produces an honest, calibrated work assessment. It replaces the AI default of "give everything a 4" with a structured two-axis score, forced devil's-advocate reasoning, and cross-session anti-inflation detection.

Core insight: AI self-evaluation converges on "everything is a 4" because a single axis conflates task difficulty with execution quality. self-eval splits the two axes apart, then combines the score using a fixed matrix the model cannot override.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Context to evaluate | Yes | Work completed in the current session, or a specific task passed via `/self-eval <description>` |
| Historical scores file | No | `.self-eval-scores.jsonl` in the working directory; used for the anti-inflation check if present |

When something is missing, ask for it all at once:
"Please provide: (1) the work to evaluate (default = what was completed in this session; you can use /self-eval <one-line description> to specify); (2) whether to compare against historical scores across sessions (default reads `.self-eval-scores.jsonl`; skip if none). Once confirmed, I'll start."

## Pre-flight Checks

- This skill is pure prompt-driven with no external dependencies; no tools need installing.
- The working directory is writable (used to append to `.self-eval-scores.jsonl`): `test -w .` → writable; otherwise only output the evaluation, skip persistence, and say so.
- If the user passes `$ARGUMENTS` or `/self-eval <content>`, use that content as the evaluation target; otherwise review the entire session history, first summarizing this session's outcome in one sentence before scoring.

## Workflow

### Step 1: Identify and summarize the work

Action: identify completed work from the session history (or passed arguments) and summarize it in one sentence.
Expected: produce a single-line **Task** summary.
On failure: the history is empty or cannot be determined → ask the user to explicitly specify the evaluation target with `/self-eval <description>`.

### Step 2: Score the two axes independently

Action: first score Axis 1 task ambition (Low/Medium/High), then score Axis 2 execution quality (Poor/Adequate/Strong). **Do not pick the score first and reverse-engineer it** — grade each axis separately, then look it up in the matrix.
Expected: both axes get a level + one sentence of rationale.
On failure: the model tends to give "all 4" → force it back to the matrix, capping low ambition at 2.

### Step 3: Devil's advocate (mandatory)

Action: before finalizing, you must write three arguments:
1. **Case for LOWER**: why does this work deserve a lower score? What was easy, dodged, or less ambitious than it looks?
2. **Case for HIGHER**: what was genuinely challenging or exceeded the original plan?
3. **Resolution**: if either argument reveals a mis-graded axis, re-grade and recompute the matrix, then give the final score + 1–2 sentences of rationale (must cover at least one point from each side).
Expected: the three blocks total ≥3 sentences; if fewer, redo.
On failure: fewer than 3 sentences → treat as not truly engaged, redo.

### Step 4: Anti-inflation check

Action: check `.self-eval-scores.jsonl` in the working directory; if it exists, read the most recent 5 entries. If ≥4 of the last 5 are identical → emit a warning.
Expected: print `Warning: Score clustering detected. Last 5 scores: [...]` and ask whether you're anchoring to a default.
On failure: the file does not exist → ask yourself "would an outside observer give me the same rating?" and continue.

### Step 5: Persist and output

Action: append one JSON line to `.self-eval-scores.jsonl`; present the evaluation in the output format below.
Expected: the file is appended (or, if the working directory is not writable, only the output); the output includes Task/Ambition/Execution/Devil's Advocate/Score.
On failure: write fails → still output the evaluation, noting that it was not persisted.

## Two-Axis Scoring Model

### Axis 1: Task ambition (what was done)

Grades difficulty and risk, **not** how well it was done.

- **Low (1)** — safe, familiar, routine. No real risk of failure. E.g., a small config change, a simple refactor, copy-paste with minor edits, a task you were confident about before starting.
- **Medium (2)** — meaningful and with some novelty or challenge. Could partially fail. E.g., implementing a new feature, integrating an unfamiliar API, an architecture change, debugging a tricky problem.
- **High (3)** — ambitious, unfamiliar, or high-risk. There is real risk of total failure. E.g., building from scratch in an unfamiliar domain, redesigning a complex system, a performance-critical optimization, shipping to production under pressure.

**Self-check:** if you were sure you'd succeed before starting, the ambition is Low or Medium, not High.

### Axis 2: Execution quality (how well it was done)

Independent of ambition; grades the actual output quality.

- **Poor (1)** — major failure, incomplete, wrong output, gave up midway. The deliverable did not meet your own standards.
- **Adequate (2)** — completed but with gaps, shortcuts, or lack of rigor. Done, but with obvious room for improvement left behind.
- **Strong (3)** — well executed, thorough, high quality. No obvious improvements left within scope.

### Combined-score matrix

|                        | Poor execution (1) | Adequate execution (2) | Strong execution (3) |
|------------------------|:---:|:---:|:---:|
| **Low ambition (1)**   |  1  |  2  |  2  |
| **Medium ambition (2)**|  2 |  3  |  4  |
| **High ambition (3)**  |  2  |  4  |  5  |

**Read the matrix; do not override it.** The combined score is your score. The devil's advocate may make you re-grade an axis — but you cannot directly override the matrix result.

Key properties:
- Low ambition is capped at 2. However perfectly safe work is done, it is still safe work.
- A 5 requires **both** high ambition **and** strong execution. It should be rare.
- High ambition + poor execution = 2. Bold failure is costly.
- The most common honest score for solid work is 3 (medium ambition, adequate execution).

## Devil's Advocate (Mandatory)

Before finalizing, you must write the three steps above (Lower/Higher/Resolution). If the devil's advocate totals fewer than 3 sentences, you are not truly engaged — redo it.

## Anti-inflation Check

Check `.self-eval-scores.jsonl` in the working directory. If it exists, read the most recent 5 entries; if ≥4 of them are the same number, flag it:
> **Warning: Score clustering detected.** Last 5 scores: [list]. Consider whether you're anchoring to a default.

If it does not exist, ask yourself: "would an outside observer give me the same rating?"

## Score Persistence

After the evaluation, append one line to `.self-eval-scores.jsonl` in the working directory:

```json
{"date":"YYYY-MM-DD","score":N,"ambition":"Low|Medium|High","execution":"Poor|Adequate|Strong","task":"1-sentence summary"}
```

Create the file if it does not exist. This makes cross-session anti-inflation checks possible.

## Output Format

## Self-Evaluation

**Task:** [one-sentence summary of the work]
**Ambition:** [Low/Medium/High] — [one sentence of rationale]
**Execution:** [Poor/Adequate/Strong] — [one sentence of rationale]

**Devil's Advocate:**
- Lower: [why it might deserve a lower score]
- Higher: [why it might deserve a higher score]
- Resolution: [rationale for the final verdict]

**Score: [1-5]** — [one final sentence of rationale]

## Failure Handling Table

| Symptom / error | Cause | Action |
|-----------|------|------|
| Session history empty, no `$ARGUMENTS` | Nothing to evaluate | Ask the user to specify with `/self-eval <description>` |
| Model tends to give "all 4" | Single-axis inertia | Force it back to the matrix; cap low ambition at 2 |
| Devil's advocate <3 sentences | Not truly engaged | Redo the three arguments |
| `.self-eval-scores.jsonl` write fails | Directory not writable | Still output the evaluation, noting it was not persisted |
| ≥4 of the last 5 scores identical | Anchoring to a default | Emit the clustering warning and recalibrate |

## Delivery Criteria

Definition of success: output the five sections Task/Ambition/Execution/Devil's Advocate/Score, with the score derived from the matrix rather than picked directly, and the devil's advocate covering both sides; append one line to `.self-eval-scores.jsonl` if the directory is writable.
Artifact naming/location: `.self-eval-scores.jsonl` (working directory).
Completeness verification: the output Score matches the matrix lookup; the last JSONL line has all fields.

## References

This skill is pure prompt-driven (prompt-only), with no bundled `references/*.md` and no `scripts/`. The scoring matrix, devil's advocate, anti-inflation, and persistence rules are all inlined above.
