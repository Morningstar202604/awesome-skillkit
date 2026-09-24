---
name: meeting-notes
description: >-
  Turn raw meeting transcripts or rough notes into structured minutes:
  decisions, action items with owners and deadlines, open questions, and a
  circulation-ready summary. Use when the user asks to organize meeting notes /
  transcribe meeting record / notes from this transcript / summarize this
  meeting / clean up recording text / meeting minutes / action items. Do NOT
  use for live transcription, audio-to-text conversion, or project status
  reports without meeting content.
license: Apache-2.0
compatibility: No special environment; accepts pasted transcript or notes.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Meeting Notes (Transcript → Minutes)

Machine-first principle: never fabricate owners, dates, or decisions. Anything not
in the transcript is marked `<unspecified>` and listed under open questions.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Transcript / rough notes | yes | — | Pasted text; speaker labels help but optional |
| Meeting metadata | no | — | Date, attendees, meeting purpose |
| Audience | no | All relevant parties | Determines how plain the minutes should be |

When transcript is missing, ask once:

> Please paste the meeting transcript (speech-to-text is fine). Optionally tell
> me: date, attendees, meeting goal, and who the minutes are going to.

## Pre-flight Checks

No environment probing—no dependencies, endpoints, or env vars. Self-check is
on the input side: do we have the transcript? If not, ask once as above, then
STOP. Never start from assumptions about "what the meeting probably decided."

## Workflow

### Step 1: Segment First, Summarize Second

Cut the transcript chronologically into topic blocks (each topic switch = one
block), numbered T1…Tn, each with a one-line topic tag.

Expected: block count matches discussion flow; fragments on the same topic
merged.

### Step 2: Separate Decisions from Discussion

For each block, classify every exchange as:
- **Decision**: clear conclusion with no objections (quote the original key
  sentence as evidence)
- **Discussion**: exchange but no conclusion → goes to open questions
- **Action**: someone says "I'll do / you handle / by next week" → goes to step 3

Expected: zero missed classifications; when ambiguous, quote the original
sentence into open questions rather than guessing intent.

### Step 3: Action Table (Core Deliverable)

| Action Item | Owner | Deadline | Source Topic | Status |
|---|---|---|---|---|

Rule: Owner must be a person named in the transcript, otherwise write `<unassigned>`;
missing deadline writes `<TBD>`; every row must trace to a T-number.

### Step 4: Draft with Fixed Structure

```text
# Minutes YYYY-MM-DD <topic>
Attendees: <list or <unspecified>>
## One-Page Conclusions
<3-5 most important decisions, one line each>
## Decision Details
<by T number, decision + evidence quote>
## Action Items
<Step 3 table>
## Open Questions
<items with no owner / no conclusion, including who must decide>
```

### Step 5: Consistency Check Before Delivery

Verify: every decision has an evidence quote; every action item has owner +
deadline or explicit placeholder; total length ≤ 1/3 of transcript. Find
violations → return to steps 2-3 to fix, don't just delete entries.

## Failure Handling Table

| Symptom | Likely Cause | Action |
|---|---|---|
| Transcript has no speaker labels | Raw ASR output | Infer roles from content; mark uncertain attributions `<inferred>` |
| Two conflicting "decisions" on same topic | Missed a later reversal | Keep both with timestamps, flag in open questions |
| Transcript cuts off mid-topic | Incomplete input | Mark explicitly at end that it ends at Tn |
| User asks to soften a decision | Bias-driven rewrite | Deliver faithful version; user decides whether to change |

## Delivery Criteria

Success = minutes strictly follow step 4 skeleton, action table complete, zero
fabricated facts. Missing any item means incomplete—say so honestly.

## Pipeline Handoff

Action items can feed excel-assistant to build a tracker, or become
project-experience material for resume-tailor.

## References

- Pure prompt-based, no external reference files needed.
