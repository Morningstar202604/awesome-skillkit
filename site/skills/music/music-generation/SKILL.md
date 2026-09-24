---
name: music-generation
description: >
  Generate music tracks from a text brief through a local generation gateway
  (style, instruments, mood, duration; polling and download included). Use
  when the user asks to generate music / make a track / score / background music /
  generate a song / make BGM / write a melody / music generation /
  composition / audio / MIDI / soundtrack. Do NOT use for text-to-speech,
  audio editing, trimming MP3s, or transcription.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Music Generation (Brief → Audio Track)

Drive the local generation gateway with curl: submit a music task, poll until it finishes, and download the audio file. No local synthesis tools, no dependencies to install — rendering happens on the gateway side; you handle the orchestration.

> ENDPOINT STATUS: VERIFY BEFORE USE — before the first run, confirm the
> `/api/music/*` paths against your gateway docs; the pre-flight self-check below fails fast when the routes differ or are missing.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| Style/mood brief | Yes | — | Genre + instruments + mood, one sentence |
| duration_seconds | No | `30` | Keep within the range noted in the gateway docs |
| instrumental | No | `true` | Set `false` only when lyrics are provided |
| lyrics | No | — | Required when instrumental is false |

When a required item is missing, ask once:

> Please describe the music you want: the style (e.g. upbeat corporate theme), the main instruments, and the mood.
> Optionally tell me: the duration (default 30 seconds) and whether you want vocal lyrics (default instrumental).

## Pre-flight Self-check

First resolve the gateway base URL (same command as workflow step 1), then probe it:

```bash
MUSIC_GATEWAY_BASE="${MUSIC_GATEWAY_BASE:-http://127.0.0.1:30080}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$MUSIC_GATEWAY_BASE/api/music/status?task_id=0"
```

Expected: prints an HTTP status code. On failure: connection failed (curl exits non-zero) → report that the music endpoint at `$MUSIC_GATEWAY_BASE` is unavailable, ask the user to start the gateway, and STOP; returns 404 → that gateway's route name differs; check the gateway docs, update this file's constants, and tell the user, then STOP. Never substitute a local synthesis on your own.

## Workflow

### Step 1: Determine the Gateway Base URL

```bash
MUSIC_GATEWAY_BASE="${MUSIC_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$MUSIC_GATEWAY_BASE"
```

Expected: prints a URL that matches the one the pre-flight probe passed.
On failure: if it expands empty, the shell is abnormal → stop; if it disagrees with the pre-flight, use the value that passed pre-flight.

### Step 2: Compose the Music Brief

Fill three slots in one sentence:

```json
[genre] + [lead instrument] + [mood and use case]
```

Example: "upbeat pop-electronic, led by piano and synths, used as the opening warm-up for a product launch,
positive and uplifting." Do not name artists; use descriptive sound characteristics instead.

Expected: the brief fills all three slots and names no artist.
On failure: a slot cannot be filled (only "nice background music") → go back to the input checklist and ask for style/instruments/mood; the full lexicon is in [music-style-lexicon.md](references/music-style-lexicon.md), use the five-slot Style formula and the mood×BPM mapping to fill it in.

### Step 3: Submit the Task

```bash
curl -s -X POST "$MUSIC_GATEWAY_BASE/api/music/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 BRIEF>","params":{"duration":"30","instrumental":true}}'
```

With lyrics: add `"instrumental":false` and `"lyrics":"<LYRICS>"`.

Expected: JSON containing `task_id`. On failure: an HTTP error or HTML returned → retry once as-is, then report and stop; a lyrics submission rejected (parameter mismatch) → explicitly set `"instrumental":false` and resubmit once.

### Step 4: Poll to a Terminal State

```bash
curl -s "$MUSIC_GATEWAY_BASE/api/music/status?task_id=<TASK_ID>"
```

Poll every 10 seconds. Success condition: `is_final == true` and
`state == "success"`; take the `result_url`. Cap at 60 tries (10 minutes).
On failure: `state == "failed"` → make the brief more concrete or shorten the lyrics and retry once; still `pending` after 10 minutes → report the `task_id` and suggest resubmitting.

### Step 5: Download and Deliver

```bash
curl -s -L -o "music_$(date +%Y%m%d_%H%M%S).mp3" "<RESULT_URL>"
ls -lh music_*.mp3
```

Expected: a non-empty audio file. Verify the size > 0 before claiming success;
report the absolute path and the brief used.
On failure: a 0-byte file → the `result_url` expired; re-poll for a new URL and download once more; still 0 → report honestly that it is incomplete, do not pass off a placeholder audio.

## Failure Handling Table

| Symptom | Likely cause | Action |
|---|---|---|
| Pre-flight 404 | That gateway's route name differs | Check the gateway docs; update this file's constants; tell the user |
| Pre-flight connection failed | The gateway is not started | Ask the user to start it; stop |
| A lyrics submission rejected without the flag | Parameter mismatch | Explicitly set instrumental=false and resubmit once |
| status stuck at `pending` for a long time (>10 min) | The queue is jammed | Report the task_id and suggest resubmitting |
| `state == "failed"` | The brief is too vague or it hit a lyrics policy | Make the brief more concrete / shorten the lyrics and retry once |
| The downloaded file is 0 bytes | The URL expired | Re-poll for a new result_url and download once more |

## Delivery Standards

Success = a local non-empty audio file `music_YYYYMMDD_HHMMSS.mp3`, with the absolute path reported plus the style brief and duration. Missing any one means incomplete — say so honestly and point to the corresponding row above.

## Chain Handoff (downstream suggestion)

This skill produces BGM / scoring, which can feed the music-generation step of the video domain's meme / talking_character chains (the video domain chains already register music-generation, but this skill is not listed in the skills list, making it a drifter). Suggest registering this skill in the video domain's skills list to complete the handoff. The handoff is descriptive only.

## References

- [music-style-lexicon.md](references/music-style-lexicon.md) — the music-style lexicon: the five-slot Style formula, genre-family seeds, mood×BPM mapping, the full set of structure/vocal/instrument tags, production-aesthetic words, and a negative list plus ready-made seeds (check this first when filling a style brief)
