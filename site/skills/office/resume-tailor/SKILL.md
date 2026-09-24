---
name: resume-tailor
description: >-
  Tailor a resume to one specific job description: extract JD requirements,
  build a gap matrix, rewrite bullets with metrics (STAR), and output an
  ATS-safe document plus an edit changelog. Use when the user asks to tailor a
  resume / customize CV for a job / rewrite resume for this JD / tailor my
  resume for this JD / optimize my CV / resume customization. Do NOT use for
  writing cover letters, LinkedIn profiles, or fabricating experience.
license: Apache-2.0
compatibility: No special environment needed; accepts plain text or pasted resume.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Resume Tailor (Resume + JD → Tailored Version)

One JD per round. Machine-first principle: every change must trace back to a
line in the JD or evidence in the original resume. Fabrication is a hard ban—
see red lines.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Resume text/file | yes | — | Plain text preferred |
| Job description | yes | — | Paste the full JD, not just the job title |
| Target tone | no | Concise, quantified | e.g. foreign-company English / domestic internet |

When required inputs are missing, ask once:

> Please provide: 1) your full existing resume; 2) the complete JD for the
> target role (including requirements). Optional: Chinese or English, any
> projects you especially want to highlight.

## Pre-flight Checks

No environment probing—no dependencies, endpoints, or env vars. Self-check is
on the input side: do we have both the complete resume and complete JD? Missing
either → ask once as above, then STOP. A JD that only gives a job title ("help
me tailor my resume for product manager") doesn't count as a JD—ask for the
full text first; step 1 can't run without it.

## Red Lines (Hard Bans, Non-Negotiable)

1. Never fabricate experience, level, certificates, or numbers. Quantification
   can only come from facts already in the original resume or from user-confirmed
   answers.
2. Never beautify by hiding authenticity issues (e.g. writing an internship as
   full-time work).
3. Why: background checks and deep interview questioning amplify any fabrication;
   the cost is a revoked offer and industry reputation damage.

## Workflow

### Step 1: Extract JD Requirements

Build a two-column list: hard requirements (education/years/must-have skills) |
soft preferences.

Expected: 5–12 rows, each quoting JD original wording.

### Step 2: Gap Matrix

Judge each JD line against the resume: match (has evidence) / partial (needs
stronger phrasing) / missing (honestly leave blank or suggest user supply real
material).

Expected: no unjudged lines.

### Step 3: Rewrite Bullets

For "partial" matches, rewrite using STAR + numbers:
`verb + what you did + method/scale + verifiable result`.

Rewrite example—before: "responsible for official account operations";
after: "Independently ran official account (3 months), 2 posts/week, followers
grew from 1.2k to 4.6k (+283%)".

Numbers not in source material get `<confirm with you: specific value>`; never
invent one.

### Step 4: ATS Hygiene Check

Single-column layout; standard headings (Education/Experience/Projects/Skills);
no tables, text boxes, or graphics in content; mirror keywords from the JD while
staying truthful; filename `Name_Title_Resume.pdf`.

### Step 5: Deliver Two Artifacts

1. Full tailored resume text; 2. `edit_log.md`, each change recorded as
   `original → revised ← JD basis`, plus a pending-material list (numbers,
   projects) only the user can fill.

Expected: user can accept or reject each change line by line.

## Failure Handling Table

| Symptom | Likely Cause | Action |
|---|---|---|
| Every JD line exceeds resume evidence | Match too low | Say honestly; suggest adjacent roles rather than padding |
| User asks to exaggerate numbers / fabricate certificates | Hits red line | Refuse the change, restate the ban, offer honest strengthening |
| Tailored resume too long | Leftover irrelevant sections | Trim by JD relevance, record each cut in edit_log |
| Key skills completely missing | Real gap | Add to pending list, attach a concrete fast-path |

## Delivery Criteria

Success = tailored resume text + `edit_log.md` tracing every change, zero
unverifiable statements. Missing any item means incomplete—say so honestly.

## Pipeline Handoff

The tailored resume can feed excel-assistant for version comparison, or be
organized meeting-notes style.

## References

- Pure prompt-based, no external reference files needed.
