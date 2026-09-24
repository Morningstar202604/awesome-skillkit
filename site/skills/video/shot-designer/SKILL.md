---
name: shot-designer
description: >
  Design cinematic shots and write cross-model text-to-video prompts. Two
  modes: (A) assemble a shot list from 12 recipe cards (establishing-wide,
  hook-pop-in, insert-closeup, parallax-push, title-card, match-cut,
  reaction-cutaway, process-montage, reveal-pan, beat-sync-cut,
  final-frame-hold, cta-endcard), each with energy and duration; or (B) build a
  custom six-slot prompt (subject + action + camera + lighting + style +
  duration/aspect) and audit it with bundled prompt_audit.py. Includes a full
  camera-design reference: shot sizes ECU to ELS, angles, moves, composition.
  Use when the user asks to design shots / produce a shot list / write a video
  prompt / text-to-video prompt / prompt audit / camera-move design /
  transition design / make footage cinematic for a promo, short film, or product
  video. Do NOT use for generating the video itself, writing dialogue or
  narration (use video-script-writer), or static image prompts (image-generation
  owns those).
license: Apache-2.0
compatibility: Pure prompt-based design; the bundled scripts/prompt_audit.py needs Python 3.8+ only.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-24"
---

# Shot Designer (Shot Lists + Six-Slot Video Prompts)

One skill for the two jobs that used to be split: picking a cinematic shot list from recipe cards, and writing/auditing a single six-slot text-to-video prompt. Every shot answers three questions: **why it exists (purpose), what rhythm it has (energy), how long it runs (duration)** — a shot that can't answer any of them should be cut. For prompts, models can't read minds: every missing slot gets improvised, and improvisation is where wasted clips come from.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| mode | yes | `cards` (build a shot list from recipe cards) or `prompt` (write/audit a six-slot prompt) |
| storyboard / beat sheet | cards required | Output from storyboard-designer, or equivalent scene descriptions with beat durations |
| scene description | prompt required | One-line frame: subject + action + environment |
| tone | no | cinematic / energetic / calm / playful; inferred from content by default |
| aspect ratio | no | 16:9 by default |
| duration | no | Default 5s (prompt mode) |
| target model | no | Default generic six-slot structure; if seedance/kling/veo/sora/runway is named, apply its dialect (see Model Dialect notes) |
| prompt to audit | audit required | Paste the original text; don't audit from memory |

When required inputs are missing, ask everything at once per the table; don't invent beats or slots.

## Pre-flight Checks

- cards mode: do you have the beat sheet? Without one, first have the user give scene descriptions and mark each beat's duration. If you plan to use beat-sync-cut and have no BGM/BPM info, ask first (see the failure table).
- prompt mode: does the scene description have a subject? A subjectless description like "shoot a nice-looking shot" is rejected outright.
- audit mode: do you have the original prompt text? If not, ask for it first.
- Confirm the audit script is present: `test -f scripts/prompt_audit.py && echo AUDIT-OK`; if missing, the bundle is incomplete — STOP and report.

## Camera Design Reference

Pick one shot size, one angle, and at most one camera move per shot. Stacking moves ("slow push-in and orbit") makes the model wander.

### Shot sizes (from tight to wide)

| Shot size | What it shows | When to use |
|---|---|---|
| Extreme close-up (ECU / macro) | A detail, an eye, a prop | Emphasize a key object/number/button; the hook |
| Close-up (CU) | Face and emotion | Reaction, tension, a line delivery |
| Medium close-up (MCU) | Chest up | Interview, reaction cutaway |
| Medium shot (MS) | Waist up, action subject | Dialogue, the working subject |
| Full shot (FS) | Whole body plus environment | A person acting in a space |
| Wide / establishing (WS) | The place | Opening tone-setting, orientation |
| Extreme wide shot (ELS) | Vast environment, small subject | Scale, isolation, finale reveal |

### Camera angles

| Angle | Effect | When to use |
|---|---|---|
| Eye-level | Neutral, natural | Default; conversation, most narrative |
| High angle (looking down) | Smaller, vulnerable, observed | A character at a low point, vulnerability |
| Low angle (looking up) | Powerful, imposing, grand | A hero, a product, a looming threat |
| Dutch (canted frame) | Unease, instability | Tension, a wrong-turn moment |
| Bird's-eye (straight down) | Abstract pattern, symmetry | A layout, a tabletop, a graphic beat |
| Worm's-eye (extreme low) | Monumental, vertiginous | Looking up at a tower, a towering figure |

### Camera movement (one verb per shot)

| Move | Meaning | When to use |
|---|---|---|
| Pan | Rotate horizontally (fixed position) | Reveal a vista, follow a side-to-side action |
| Tilt | Rotate vertically (fixed position) | Up a tall subject, down to a detail |
| Dolly | Physical push in / pull out | Intimacy (push-in) or reveal (pull-back) |
| Truck | Lateral physical move | Track alongside a moving subject |
| Pedestal | Physical rise / lower | Crane up for a big reveal |
| Zoom | Focal-length change (no travel) | Quick emphasis; less cinematic than dolly |
| Rack focus | Shift focus between near and far planes | Draw attention between two subjects |
| Handheld | Organic micro-shake | Documentary, urgency (AI can blur it) |
| Gimbal | Smooth, steady follow | Fluid product/character tracking |
| Drone | Aerial / FPV move | Establishing, fly-through transitions |
| Static / locked-off | No move | The safest default when unsure |

Speed is a dial: slow / steady / fast. Give one direction ("slow pan to the right").

### Composition rules

| Rule | Apply it like this |
|---|---|
| Rule of thirds | Place the subject at an intersection; leave headroom |
| Leading lines | Use roads, rails, light strips to pull the eye to the subject |
| Framing | Nest the subject inside a doorway, window, arch, or foreground element |
| Depth | Layer foreground / midground / background for dimensionality |
| Negative space | Leave breathing room in the direction the subject looks/moves |

## Workflow

### Mode A — Build a shot list from recipe cards

**Step A1: Pick a recipe for each beat.** Choose from the 12 cards below. First lock the **hook shot** and the **closing shot** (the two ends make or break it), then pair the middle beats with development shots. Expect exactly 1 primary card per beat; the hook beat may stack one auxiliary card. If a beat wants two cards, split it into two shots.

**Step A2: Instantiate per the card formula.** Each card gives a parameter formula; copy it verbatim, swapping in the user's content — determinism first, don't improvise camera-move parameters. If a formula variable can't be filled (not enough frame info), go back to the input checklist and ask.

**Step A3: Mark the transition chain.** Fill the exit-transition column: within the same scene -> hard cut; time jump -> match cut; mood shift -> dissolve <=0.5s. At most one effect transition in the whole film (e.g. a film-burn); restraint is part of cinematic feel. A second effect appears -> delete the less important one and change it to a hard cut.

**Step A4: Output the shot list.** Fixed 7-column table (column order must not change):

```markdown
| # | Duration | Recipe Card | Camera Move | One-Line Frame | Sound | Exit Transition |
|---|----------|-------------|-------------|----------------|-------|------------------|
| 1 | 3s | establishing-wide | slow push-in | rainy-night neon street | rain fade-in | hard cut |
```

Expect total film duration = beat-sheet total +/-10%. Out of tolerance -> recompute, cut middle beats first.

### Mode B — Write or audit a six-slot prompt

**Step B1 (write): Fill in the six slots.**

```text
[subject] + [action] + [camera] + [lighting] + [style] + [duration/aspect]
```

Example (copy the block and swap words):

```text
A young woman in a black hoodie walks through a rainy neon-lit street,
slow push-in from mid shot to close-up, night exterior with cyan-orange
neon spill and wet-reflective asphalt, cinematic live-action look,
5 seconds, 9:16 vertical.
```

Rules: the action is single and completable in one shot ("sit down and light a lighter" is two actions -> split into two prompts); one phrase per slot, a prompt is a parameter table not a script; numbers are explicit ("5 seconds", never "a few seconds"); use concrete action verbs (`strides`, `ignites`, `grips`) not vague ones (`moves`, `acts`, `reacts`); give 1-2 micro-expressions per shot, never more.

**Step B2: Self-check with the audit script.**

```bash
python3 scripts/prompt_audit.py --prompt "<text>" --mode write
```

Expect 6/6 slots hit. Below 6/6 -> read the missing list and fill each slot before delivering; don't carry misses forward.

**Step B3 (audit an existing prompt): Run the structural audit.**

```bash
python3 scripts/prompt_audit.py --prompt "<text to audit>"
```

Expect JSON output with each slot's hit/miss and a missing list. Fill misses per the remediation table. Empty/whitespace prompt -> the script errors; go get the real prompt text.

**Step B4: Apply the model dialect (only when a model is named).** Check the Model Dialect notes below and, when the user names a specific model, follow its marker syntax. Model syntax changes monthly — verify against the official prompt guide before use; if unverified, deliver the generic six-slot structure and note "dialect not verified".

## Twelve Recipe Cards

| Card | Use | Energy | Duration | Formula / pitfall |
|---|---|---|---|---|
| establishing-wide | Opening tone-setting | low | 3-4s | wide establishing + slow push-in (<=5%/s); don't push too fast |
| hook-pop-in | First-3-seconds hook | high | 1-2s | ECU start + quick pull-back reveal; give contrast before subject |
| insert-closeup | Emphasize a detail | medium | 1-2s | static macro, shallow DOF; only insert objects that pay off later |
| parallax-push | Flat image to dimensional | medium | 3-4s | foreground 1.2x / midground 1.0x / background 0.8x; <=3 layers |
| title-card | Title / chapter card | low | 2-3s | pure layout + micro letter-spacing; place between high-energy beats |
| match-cut | Time/space jump | medium | 2-3s each | end-frame A matches start-frame B; use dissolve if match <60% |
| reaction-cutaway | Emotional reaction | medium | 1-2s | MCU static, micro-expression; keep <= half the line's length |
| process-montage | Compress a process | medium-high | 3-5s | same framing x N steps, 0.8-1s each; cap at 6 steps |
| reveal-pan | Reveal the whole | low-medium | 3-4s | start 70% occluded, steady pan; keep pan speed even |
| beat-sync-cut | Beat-synced rapid cuts | high | 0.5-1s x N | max-contrast adjacent frames; needs BGM BPM first |
| final-frame-hold | Closing freeze | low | 2s | final frame still (or 2% push); compose as a cover still |
| cta-endcard | Call-to-action end card | medium | 2-3s | static layout + one fading element; keep CTA to one line |

Energy curve self-check: arrange the 12 energies (low/medium/high) into a wave. All-high = audience fatigue; all-low = audience scrolls away. Force in a low-energy card (title-card / final-frame-hold) for breathing room.

## Six-Slot Dictionary (Fastest Lookup)

| Slot | Common phrases |
|---|---|
| subject | identity + outfit + expression: "a young woman in a black hoodie, tired eyes" |
| action | single verb phrase: "walks slowly toward camera" / "ignites a blue lighter" |
| camera | shot size + angle + one move: "extreme close-up, low angle, slow push-in" |
| lighting | time of day + source + contrast: "golden hour backlight" / "high-contrast noir, practical neon" |
| style | medium texture: "cinematic live-action" / "stop-motion feel" / "90s camcorder" |
| duration/aspect | "5 seconds, 9:16 vertical" |

## Model Dialect Notes (VERIFY BEFORE USE)

The audit script only checks the generic six slots (model-invariant). Dialect conformance is a second, manual layer — both are required. When unsure, use only the generic six slots + explicit duration/aspect and skip all special markers (a wrong marker is worse than none).

- **Sora / Veo**: block by shot/subject/action/setting/camera/lighting; Veo uses noun-style negatives (`cartoon, blur`, not `no blur`); fixed duration tiers; dialogue goes in its own block.
- **Runway**: lead with camera movement and rhythm; `--motion` dial 1-6; iterate in order (composition -> light -> action).
- **Seedance**: marker system `( )` weight / `{ }` branch / 【 】 audio — confirm against the official guide; supports multi-stage prompts up to ~30s.
- **Kling**: subject/action/camera in separate clauses; concrete physical verbs work best; supports tail-frame chaining.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| Audit below 6/6 | A slot is empty | Read the missing list, fill each slot one at a time; don't invent — ask the user for environment/time of day |
| Subject's face changes every frame | Vague subject / no reference | Add a character-card description or the model's reference-image slot |
| The action doesn't happen | Action written as a state | "holding a lit lighter" -> "ignites the lighter" (write the process) |
| Camera wanders erratically | Two moves stacked | Keep exactly one camera-move verb per prompt |
| Whole film is all high-energy shots | Showing off | Force in a low-energy card (title-card / final-frame-hold) |
| Shot durations exceed total | Cards not converted | Recompute to total +/-10%; cut middle beats first |
| Beat-sync cuts miss the BGM | No BPM info | Ask for the BGM, or mark beat-sync-cut as "lock frame rate before render" |
| Model doesn't support that move | Dialect limits | Downgrade to a basic move (push/pull/static); keep card params for later |
| Audit 6/6 but generation is poor | Right structure, weak words | Swap adjectives for concrete nouns: "beautiful lighting" -> "cyan neon spill" |

## Delivery Standard

- cards mode: one shot-list table with all 7 columns, # sequential; each recipe name maps to a card above; total duration within +/-10%.
- prompt mode: an English prompt with all 6 slots, plus a slot-by-slot mapping; audit mode delivers the JSON hit/miss report plus a side-by-side fixed prompt.
- Any dialect entry applied must be verified per the notes above; otherwise note "dialect not verified".

## References

- [scripts/prompt_audit.py](scripts/prompt_audit.py) — six-slot structural audit (subject/action/camera/lighting/style/duration); emits per-slot hit/miss JSON.
- This skill otherwise carries its domain knowledge inline above (camera design, 12 recipe cards, six-slot dictionary).
