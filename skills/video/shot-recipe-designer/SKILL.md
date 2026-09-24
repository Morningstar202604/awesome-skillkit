---
name: shot-recipe-designer
description: "Design a cinematic shot list from recipe cards: each shot gets a purpose, energy level, duration, camera move, and exit transition — 12 proven recipe cards (establishing shot, insert close-up, 2.5D parallax push, title card, match cut, reaction cutaway and more). Use when the user asks to design shots / produce a shot list / shot list / camera-move design / transition design / make the film cinematic for a promo, short film, or product video. Do NOT use for writing dialogue or narration (use video-script-writer), nor for generating the video itself."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts, no API keys.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Shot Recipe Designer

Assemble a shot list from "shot recipe cards". Every shot answers three questions: **why it exists (purpose), what rhythm it has (energy), how long it runs (duration)** — a shot that can't answer any of them should be cut.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| storyboard / beat sheet | yes | Output from storyboard-designer, or an equivalent scene description |
| tone | no | cinematic / energetic / calm / playful; inferred from content by default |
| aspect ratio | no | 16:9 by default |

## Pre-flight Checks

- The recipe-card file is on disk: `test -f references/shot-recipes.md` — after picking a card you must read the original card; if missing -> STOP and report the repo is incomplete.
- Do you have the beat sheet? Without a storyboard-designer output, first have the user give scene descriptions and mark the duration of each beat; if neither exists -> ask everything at once per the input checklist; don't invent beats.
- If you plan to use beat-sync-cut and have no BGM/BPM info -> see row 3 of the failure table; ask first.

## Workflow

### Step 1: Pick a Recipe for Each Beat

Choose from the 12 cards in [shot-recipes.md](references/shot-recipes.md). Card order: first lock the **hook shot** and the **closing shot** (the two ends make or break it), then pair the middle beats with development shots.

Expected: exactly 1 primary card per beat; the hook beat may stack 1 auxiliary card.
If it fails: a beat wants two cards -> split into two shots; don't suture them together.

### Step 2: Instantiate Per the Card Formula

Each card gives a parameter formula (e.g., for a parallax push: "foreground layer moves 1.2x, background layer 0.8x"). Copy the formula verbatim, swapping in the user's content — **determinism first; don't improvise camera-move parameters**.

Expected: every shot's camera parameters are directly executable, no model improvisation needed.
If it fails: a formula variable can't be filled (insufficient frame info) -> go back to the input checklist and ask; don't invent parameters.

### Step 3: Mark the Transition Chain

Fill the shot list's last column with exit transitions, per the rules:
- Within the same scene -> hard cut
- Time jump -> match cut
- Mood shift -> dissolve <=0.5s
- At most 1 transition effect in the whole film (e.g., film-burn); restraint is part of cinematic feel.

Expected: every row has an exit transition, and effect transitions <= 1 across the whole film.
If it fails: a 2nd effect appears -> delete the less important one and change it to a hard cut.

### Step 4: Output the Shot List

Fixed table (column order must not change):

```markdown
| # | Duration | Recipe Card | Camera Move | One-Line Frame | Sound | Exit Transition |
|---|----------|-------------|-------------|----------------|-------|------------------|
| 1 | 3s | establishing-wide | slow push-in | rainy-night neon street | rain fade-in | hard cut |
```

Expected: total film duration = beat-sheet total +/-10%.
If it fails: out of tolerance -> recompute per row 2 of the failure table; cut middle beats first.

## Twelve Recipe Cards (Quick Reference; See References for Detail)

| Card | Use | Energy | Duration |
|----|------|------|------|
| establishing-wide | Opening tone-setting | low | 3-4s |
| hook-pop-in | First-3-seconds hook | high | 1-2s |
| insert-closeup | Emphasize detail | medium | 1-2s |
| parallax-push | Flat image to dimensional | medium | 3-4s |
| title-card | Title / chapter card | low | 2-3s |
| match-cut | Time/space jump | medium | 2-3s |
| reaction-cutaway | Emotional reaction | medium | 1-2s |
| process-montage | Compress a process | medium-high | 3-5s |
| reveal-pan | Reveal the whole | low-medium | 3-4s |
| beat-sync-cut | Beat-synced rapid cuts | high | 0.5-1s x N |
| final-frame-hold | Closing freeze | low | 2s |
| cta-endcard | Call-to-action end card | medium | 2-3s |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|------|------|------|
| Whole film is a run of high-energy shots | Showing off | Force in a low-energy card (title-card / final-frame-hold) for breathing room |
| Shot durations exceed total | Cards not converted | Recompute per "total = overall +/-10%"; cut middle beats first |
| Beat-sync cuts don't match the BGM | No BPM info | Ask the user for the BGM or choose "BGM TBD" and mark beat-sync-cut as "lock frame rate before render" |
| The generation model doesn't support that camera move | Dialect differences | Downgrade to a basic move the model can execute (push/pull/static); keep card params in the list for later implementation |

## Delivery Standard

- One shot-list table, all 7 columns present, # sequential
- Each row's recipe-card name can be found in the original card at references/shot-recipes.md
- Total duration within +/-10%

## References

- [shot-recipes.md](references/shot-recipes.md) — the 12 complete recipe cards (camera-move parameter formulas + common pitfalls); read the matching original card after selecting
- [sources-and-methodology.md](references/sources-and-methodology.md) — open-source provenance and credits for the shot-card methodology

## Chain Handoff (Downstream Suggestions)

This skill takes the beat sheet / storyboard from storyboard-designer and outputs a shot list for video-prompt-engineer to write per-shot prompts. It's recommended as the upstream planning step in video-domain chains. Currently a standalone skill; handoff is descriptive only — no cross-directory hard links.
