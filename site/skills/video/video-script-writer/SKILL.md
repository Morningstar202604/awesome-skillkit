---
name: video-script-writer
description: "Write video scripts: dialogue, narration, shot descriptions, timing markers, and platform-compliant titles/captions. Supports multiple video types (talking character, meme, tutorial, vlog, short). Includes a golden-3-second hook discipline, single-CTA rule, and speaking-rate word budgeting. Use when the user needs a script for a video before production, e.g. writing a video script / short-video copy / storyboard script / voice-over script. Do NOT use for generating video files (script text only), nor for scene-by-scene storyboards and prompt pairs (use storyboard-designer)."
license: Apache-2.0
compatibility: "Prompt-based with an optional helper script. scripts/script_writer.py (Python 3.8+, stdlib only) generates a deterministic scene skeleton and — if SKILLKIT_LLM_URL/KEY env vars are set — calls an OpenAI-compatible gateway to write real dialogue. Without the gateway it emits template placeholder lines and labels them honestly (dialogue_source=template). No API keys required."
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-22"
---

# Video Script Writer

Produce production-ready structured video scripts: dialogue, timing, visual direction, platform-compliant titles and tags. **The script text is the only deliverable; no video files are generated.**

The judging standard for short videos is not "well-written copy" but **not being swiped away in the first 3 seconds, and viewers knowing what to do by the end**. Every discipline in this skill revolves around those two points.

## Applicability Decision Table

| Your Situation | Where This Skill Sits | Go To |
|----------|--------------|------|
| Have a concept, want a finished script | yes, this skill | here |
| Have a script, want to break it into storyboards | out of scope | storyboard-designer |
| Want a visual video prompt (not a script) | out of scope | video-prompt-engineer |
| Want copy but not video-related | out of scope | product-copywriter |
| Only gave an empty concept like "shoot a nice video" | note: push back for subject + hook first | pre-flight checks |
| Target duration exceeds the platform cap | note: decide — split episodes or lower the length | failure table |

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| concept | yes | One line of the video concept (subject + hook) |
| video_type | no | `talking_character` / `meme` / `tutorial` / `vlog` / `short`, default `talking_character` |
| duration | no | Target duration (seconds), default 30 |
| platform | no | `douyin` / `bilibili` / `tiktok`, default `douyin` |
| language | no | `zh` / `en`, default `zh` |
| tone | no | `funny` / `educational` / `dramatic`, default `funny` |
| character | no | Character JSON (name / persona / voice_style) |

When any required input is missing, ask everything at once:

> Please provide: ① video concept (one line, incl. subject and hook). Optional: ② type (default talking_character), ③ duration (default 30s), ④ platform (default douyin), ⑤ language (default zh), ⑥ character setting, ⑦ tone (default funny).

## Pre-flight Checks

- Non-empty concept: an empty concept (e.g., "shoot a nice video") is rejected outright; ask for subject and hook.
- Duration within the platform cap: douyin 60s / bilibili 900s / tiktok 600s. Over the cap -> have the user pick: split episodes or lower the duration (the script silently truncates otherwise, see Honest Disclosure 5 — don't accept that by default).
- **Track-selection confirmation (only applies when you actually run the script)**: is the environment configured with `SKILLKIT_LLM_URL` + `SKILLKIT_LLM_KEY`?
  - Configured -> LLM track; the script calls a real model to write dialogue.
  - Not configured -> template track; dialogue is self-describing placeholders (`[Character] Attention grabber about: concept`); **you must tell the user this** and give two choices: configure the gateway and rerun, or take the skeleton and write dialogue by hand.
  - **Pure-prompt mode (not running the script, writing the script directly) skips this item**: just finish the dialogue per the workflow below. **Don't bounce the task back to the user because you "can't check env vars" or "lack config"** — the deliverable is the complete script for this video, not an execution plan or an environment-check conclusion.

## Tacit Knowledge (What Actually Makes or Breaks a Video)

### 1. The First 3 Seconds Are the Golden Window: a Hook Is Not an "Introduction"

Viewers decide stay-or-leave in the first 3 seconds. **The definition of a hook is creating an information gap**, not a self-introduction, not "hello everyone", and not repeating the title.

Six reusable hook types:

| Type | Sentence Skeleton | Suits |
|------|----------|------|
| Pain-point opener | "Does your X always Y?" | tutorials, how-tos |
| Result first | "I used this trick to drop X from A to B" | tutorials, reviews |
| Counterintuitive | "X is actually not the reason for Y" | opinion, explainer |
| Number | "3 moves, the 2nd is the one people get wrong" | lists, tutorials |
| Question | "Why does B always happen when A?" | explainer, story |
| Benefit promise | "By the end of this, you'll be able to X" | tutorials, funnel |

> Numbers in numeric hooks **must be real and verifiable** (Red Line 1); unverifiable ratios like "90% of people get it wrong" are fabrication and are forbidden.

> Sourcing note: the importance of hooks is an industry-wide consensus; but specific numbers like "3-second drop X%" or "completion-rate lift Y%" vary by source with no verifiable origin, so this skill **does not cite percentages**.

### 2. One CTA Per Video

"Like + follow + share + comment + grab the sheet on my homepage" = no CTA at all — attention spread thin equals zero. The right way for funnel-type videos: **every design in the film serves that one ending action**.

### 3. Dialogue Word Count Must Be Budgeted by Speaking Rate

Mandarin voice-over runs at about **4-5 characters/second** (news-anchor delivery is faster). Accordingly:

| Duration | Dialogue Capacity (chars) |
|------|----------------|
| 15s | 60-75 |
| 30s | 120-150 |
| 60s | 240-300 |

The only correct fix for over-capacity is **cutting words**, not "speak faster" — speeding up sacrifices clarity and emotion. (Speaking rate is a common empirical value, not a platform rule; actual hosts vary widely.)

### 4. Voice-Over vs. Picture Division of Labor: Don't Say What Can Be Shown

Information the picture can show shouldn't be repeated in voice-over ("I opened the fridge" + a shot of opening the fridge = double waste). Voice-over only carries the four things the picture can't: **inner thoughts, background context, conclusions, numbers**.

### 5. Loop Design: Ending Feeds Back Into the Beginning

For meme / fast-hit types, make the ending frame or line directly connect back to the opening -> viewers loop it, and completion + engagement both win. Design it by writing the hook sentence so it can be "caught".

### 6. The Cover/Title Promise Must Pay Off in the First 3 Seconds

Promise (what the cover/title says) vs. payoff (what the first 3 seconds deliver) mismatch = swipe-away + negative feedback, a common cause of traffic decay. **Write the cover copy and the first 3 seconds side by side.**

### 7. Compliance Is Not Optional

- Sales/promotion types: avoid advertising-law absolute terms (most, #1, national-level, 100%, etc.) and avoid false efficacy promises.
- All types: avoid engagement bait ("if this gets 10k likes I'll post the next one") — mainstream platform rules explicitly restrict it.
- Medical/health types: must not promise therapeutic effects.
  > Category-specific rules follow the platform's latest public notices; this skill only does risk scanning, not a compliance guarantee (Honest Disclosure 7).

## Red Lines (Hard Bans)

1. **Don't fabricate data or fake promises**: numbers in hooks ("90% get it wrong") must have a source or be rephrased qualitatively; promises like "100k followers in 3 days" are directly forbidden.
2. **Don't write lines the persona couldn't say**: if the character is a snarky coach, write a snarky coach's lines — persona consistency beats literary polish.
3. **Template-track dialogue must not be passed off as finished**: when the script's `dialogue_source=template`, delivery must explicitly state "this is a skeleton; dialogue to be written".
4. **Don't promise traffic results**: this skill guarantees structural compliance and reasonable rhythm; it makes no promise about "going viral".
5. **Single CTA, no stacking** (tacit knowledge 2).

## Honest Disclosure (The Script's Actual Behavior)

`scripts/script_writer.py` is a **skeleton generator + optional LLM dialogue track**. Verified by actual run on 2026-09-22:

1. **LLM dual track**: after configuring `SKILLKIT_LLM_URL` + `SKILLKIT_LLM_KEY` (optional `SKILLKIT_LLM_MODEL`), the script calls an OpenAI-compatible gateway to write dialogue, with each scene's `dialogue_source="llm"`; if unconfigured, `--no-llm`, or the gateway fails -> template placeholder dialogue, `dialogue_source="template"`, and template lines are **self-described as to-be-written** (e.g., `[Character] Payoff: concept (punchline here)`).
2. **Top-level `dialogue_source`** aggregates to three states: `llm` / `mixed` / `template`; on gateway failure, `llm_note` records the reason (no silent impersonation).
3. **The `visual` field is always a placeholder**: `[role: describe visual action here]` — the script doesn't generate visual descriptions; you must fill them in manually or via LLM.
4. **`sfx` is mostly empty**: only the hook / punchline / outro roles have default sound effects; the rest are empty strings.
5. **Duration behavior**: over the platform cap it **silently truncates** and writes `duration_note`; if the target duration is shorter than the scene count it raises to the scene count (>=1s per scene) and writes `duration_note`.
6. **`caption` is auto-assembled tag-style copy** (with emoji prefixes); the script only does length checking (`caption_check`), **not content-compliance review**.
7. **`tts_config.speed`**: tone funny = 1.2, others = 1.0; this is a passed-through generation parameter, not a "suggested speaking rate".
8. **`character.voice_style` is passed through verbatim**; the script doesn't validate whether downstream TTS supports the value.
9. **`status` field**: success is `"success"`; on input errors (missing concept / invalid JSON) the script **prints an error JSON rather than failing silently**, exit code 2.
10. **Invalid `platform` silently falls back to `douyin`**: passing a value other than `douyin/bilibili/tiktok` doesn't error; it's processed under douyin rules (both platform caps and caption caps follow douyin). Watch this when cross-posting.

## Workflow

### Step 1: Concept Convergence & Track Selection

Check the concept and track per the pre-flight checks. The concept must let you read "subject + hook direction".

**The deliverable is a self-contained script JSON** (per-scene dialogue, `visual`/`camera`/`sfx` direction, duration, title and tags all live inside `scenes[]` and top-level fields — downstream lip-sync and editing read by key; a separately opened table isn't read) — not an execution plan, not "please provide more info", not an environment-check conclusion. In pure-prompt mode you write the dialogue completely yourself; track selection only matters in script mode.
Expected: concept non-empty; the user knows whether this run is the LLM track or the template track.
If it fails: concept is vague -> push back for more; don't guess your way through.

### Step 2: Generate the Script

```bash
python3 scripts/script_writer.py --concept "baby reviews a phone" --type talking_character --duration 30 --platform douyin --language zh --tone funny
```

Expected: stdout prints JSON containing `title` / `hook` / `scenes` (id, role, duration_sec, dialogue, dialogue_source, visual, camera, sfx) / `caption` / `total_duration` / `dialogue_source` / `caption_check`; `scenes` total duration = target duration (>=1s each).
If it fails: `status=error` -> read the error field to locate; gateway failure -> check `llm_note` and decide to retry or switch to manual.

### Step 3: Write Visual Elements Back Into Scene Objects (Mandatory)

The script's `visual` values are all placeholders. Per "don't say what can be shown" (tacit knowledge 4), fill them per scene: write **subject + action + shot size/environment** into `scenes[i].visual`, camera movement into `camera`, emotional turning points into `sfx` — **write back into the scene object itself; don't open a separate table and don't leave fields missing** (downstream reads by key).
**`dialogue` holds only speakable lines**; parenthetical action / expression / sound-effect directions belong to the visual layer (`visual`/`sfx`), not into `dialogue`.
Self-contained example (deliver in this shape; all fields embedded):

```json
{ "id": 2, "role": "lead", "duration_sec": 4, "dialogue": "Who am I... where am I...", "dialogue_source": "llm", "visual": "In front of the bathroom mirror, the lead brushes robotically, hollow-eyed, toothpaste foam at the corner of the mouth", "camera": "medium shot; the mirror reflection shows a tired figure behind", "sfx": "mechanical brushing sound" }
```

Expected: every scene object in the delivered JSON has a concrete, executable `visual`, and `dialogue` contains no parenthetical action directions. If it fails: can't write visuals -> that scene has no visual information; consider merging or cutting it.

### Step 4: Budget Dialogue Capacity by Speaking Rate

Count the dialogue characters per scene against tacit-knowledge-3's capacity table. Over capacity -> cut words (prioritize repeated information and adjectives).
Expected: total dialogue chars / duration in [4, 5] chars/sec. If it fails: LLM-track dialogue is universally too long -> rerun with "no more than N characters per scene" in the prompt, or trim manually.

### Step 5: Compliance & Promise-Consistency Check

- Payoff test: does the first 3 seconds (`hook`) deliver what the cover/title (`title`) promises (tacit knowledge 6)?
- Compliance scan: absolute terms / engagement bait / efficacy promises (tacit knowledge 7).
- CTA count: is there exactly one call to action in the film (tacit knowledge 2)?
Expected: all three pass. If it fails: payoff mismatch -> change either title or hook (don't change both, or you can't attribute).

## Script-Type Notes

### Talking Character (talking_character, baby, nailong, etc.)

- Dialogue-driven, 2-4 scenes; one line + one action per scene.
- The punchline lands at 70-80% through (empirical); visuals center on character + props, background minimal.

### Meme / Reaction

- Highest cut rate of all types ([timing-guide.md](references/timing-guide.md) Meme row: 1.5-4s/shot, 8-15 shots for a 30s piece) — **a 15s piece is ~4-8 shots**. Don't cut it into three 5-second blocks: evenly split duration = flat rhythm, the most common meme failure.
- Beats follow "setup -> repeat/escalate -> punchline drop": put the laugh/crash point in the last 1-2 shots (expectation vs. payoff), not an even linear roast; overlay text + audio punchline, at most one line per shot.
- The ending **must** loop back (tacit knowledge 5): the last frame loops to the first.

### Tutorial / Explainer

- Opening 5s gives the result promise (what you'll be able to do) -> steps 20-60s (each step <10s, one action per step) -> closing 5s wrap + single CTA (time splits are empirical).
- **Bilibili vs. douyin differences**: Bilibili viewers have more patience and accept longer setup and deeper explanation; douyin lives or dies in the first 3 seconds — don't bring a Bilibili-style opening to douyin.

## Built-in Verification Steps (Check Each Before Delivery)

- [ ] **3-second hook test**: `hook` is an information gap / tension, not a self-introduction or generic question
- [ ] **Single CTA test**: exactly one call to action in the film
- [ ] **Speaking-rate test**: total dialogue chars / duration in [4, 5] chars/sec
- [ ] **Payoff test**: title/cover promise <-> first-3-seconds consistency
- [ ] **Loop test** (meme): the ending can feed back into the beginning
- [ ] **Compliance scan**: no absolute terms / engagement bait / efficacy promises
- [ ] **Placeholder cleared**: all `visual` placeholders replaced; when `dialogue_source=template`, told the user dialogue is to be written
- [ ] **Fields embedded**: `visual`/`camera`/`sfx` live inside `scenes[]` objects (not replaced by a table); `dialogue` is pure lines

## Failure Remediation Table

| Symptom | Cause | Remedy |
|------|------|------|
| `status=error`, `concept missing` | No input | Push back for a concept |
| `status=error`, `invalid input JSON` | `--json-input` syntax error | Fix the JSON and rerun (rc=2) |
| `llm_note` reports gateway failure | Gateway timeout / bad JSON | Retry; on repeated failure switch to manual dialogue and say so honestly |
| Total duration truncated (`duration_note`) | Over platform cap | Have the user pick: split episodes or lower the duration; don't accept truncation by default |
| A scene's duration_sec = 1 (looks squeezed) | Target duration too short | Confirm whether `duration_note` recorded a raise; if needed, shorten the concept or add duration |
| Dialogue over speaking-rate capacity | The LLM doesn't understand "seconds" | Cut words per tacit knowledge 3; or add a word-count constraint to the gateway prompt and rerun |
| Caption over limit (`caption_check.ok=false`) | Title too long | Trim title or merge tags |
| User wants a "guaranteed hit" | Expectation management | Be clear you make no traffic promises (Red Line 4); instead explain structural compliance |

## Delivery Standard

- Structured script JSON: `title` / `hook` / `scenes[]` (with `dialogue`, `dialogue_source`, `visual`, `camera`, `sfx`, `duration_sec`) / `caption` / `total_duration` — **one self-contained JSON**, visual/sfx direction written inside scene objects, not replaced by a table.
- `dialogue` holds only speakable lines (action / expression / sfx directions go to `visual`/`sfx`).
- `scenes` total duration = target duration; >=1s per scene.
- Each scene's `visual` is executable (not a placeholder); `dialogue_source` labeled honestly.
- Dialogue speaking rate in [4, 5] chars/sec; `caption_check.ok = true`.
- All 8 built-in verification items pass.
- Script text only, no video files; downstream connects to video-voice-synth -> video-lip-sync -> video-editor.

## References

- `references/script-templates.md` — finished templates per type; copy the skeleton before writing.
- `references/timing-guide.md` — rhythm / beat rules and time allocation.
- `references/sources-and-methodology.md` — sources of tacit knowledge 1-7 and sourcing discipline (reject percentage efficacy promises), script-behavior probe records. Read when delivering/attributing/being challenged.
- [cinematography-lexicon.md](../video-prompt-engineer/references/cinematography-lexicon.md) — shot-language lexicon (transitions/actions/performance detail): pick shot-direction words for scripts from this.

## Appendix: CLI Contract (Parameter Quick Reference)

| Parameter | Value | Notes |
|------|------|------|
| `--concept` | str | Required, video concept |
| `--type` | enum | Template type (talking_character/meme/tutorial/vlog/short) |
| `--duration` | int | Target seconds, default 30 |
| `--platform` | enum | douyin/bilibili/tiktok |
| `--language` | zh/en | default zh |
| `--tone` | enum | Tone, default funny |
| `--character` | JSON string | Character setting (name/persona/voice_style) |
| `--json-input` | file | Full JSON input, overrides individual params |
| `--no-llm` | flag | Force the template track (even if a gateway is configured) |
| `--output` | file | Write to a file instead of stdout |
| env | `SKILLKIT_LLM_URL` / `SKILLKIT_LLM_KEY` / `SKILLKIT_LLM_MODEL` | Enabling these turns on the LLM dialogue track |
