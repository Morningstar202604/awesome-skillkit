---
name: music-generation
description: >
  Generate music tracks from a text brief through a local generation gateway
  (style, instruments, mood, duration; polling and download included). Use
  when the user asks to 生成音乐 / 做首曲子 / 配乐 / background music /
  generate a song / make BGM / 写段旋律. Do NOT use for text-to-speech,
  audio editing, trimming MP3s, or transcription.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Music Generation (brief → track)

Drive a local generation gateway with curl: submit a music task, poll until
done, download the audio file. No local synthesis tools, no dependency
installs — the gateway renders, you orchestrate.

> ENDPOINT STATUS: VERIFY BEFORE USE — confirm `/api/music/*` paths against
> your gateway's docs before first run; the preflight step below fails fast
> if the route differs or is absent.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| style / mood brief | yes | — | genre + instruments + emotion, one line |
| duration_seconds | no | `30` | keep within your gateway's documented range |
| instrumental | no | `true` | set `false` only if lyrics are provided |
| lyrics | no | — | required when instrumental is false |

If the required input is missing, ask ONCE:

> 请描述想要的音乐：风格（如轻快的企业宣传曲）、主要乐器、情绪。
> 可选告知：时长（默认 30 秒）、是否需要人声歌词（默认纯音乐）。

## Preflight self-check

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$MUSIC_GATEWAY_BASE/api/music/status?task_id=0"
```

Expected: an HTTP code prints. If connection fails OR the path returns 404:
report that the music endpoint is unavailable at $MUSIC_GATEWAY_BASE, show
the exact status code, and STOP. Do not synthesize audio locally as a
substitute.

## Workflow

### Step 1: Resolve the gateway base

```bash
MUSIC_GATEWAY_BASE="${MUSIC_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$MUSIC_GATEWAY_BASE"
```

Expected: prints one URL.

### Step 2: Compose the music brief

Fill three slots in one sentence:

```
[风格流派] + [主导乐器] + [情绪与用途]
```

Example: "轻快的流行电子风，钢琴与合成器主导，用于产品发布会的开场暖场，
积极向上。" Avoid naming artists; describe sonic characteristics instead.

### Step 3: Submit the task

```bash
curl -s -X POST "$MUSIC_GATEWAY_BASE/api/music/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 BRIEF>","params":{"duration":"30","instrumental":true}}'
```

With lyrics: add `"instrumental":false` and `"lyrics":"<LYRICS>"`.

Expected: JSON containing `task_id`. Failure branch — HTTP error or HTML:
retry once verbatim, then report and stop.

### Step 4: Poll until final

```bash
curl -s "$MUSIC_GATEWAY_BASE/api/music/status?task_id=<TASK_ID>"
```

Poll every 10 seconds. Success condition: `is_final == true` AND
`state == "success"`; take `result_url`. Cap at 60 polls (10 min).

### Step 5: Download and deliver

```bash
curl -s -L -o "music_$(date +%Y%m%d_%H%M%S).mp3" "<RESULT_URL>"
ls -lh music_*.mp3
```

Expected: non-empty audio file. Verify size > 0 before claiming success;
report the absolute path plus the brief used.

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| preflight 404 | route name differs on this gateway | check gateway docs; update constants here; tell user |
| preflight connect fail | gateway down | ask user to start it; stop |
| generate rejects lyrics without flag | param mismatch | set instrumental=false explicitly, resubmit once |
| status stays `pending` > 10 min | queue stuck | report task_id, suggest resubmitting |
| `state == "failed"` | brief too vague or lyric policy hit | rewrite brief concretely / shorten lyrics, retry once |
| downloaded file 0 bytes | expired URL | re-poll for fresh result_url, redownload once |

## Delivery standard

Success = a local non-empty audio file named `music_YYYYMMDD_HHMMSS.mp3`,
absolute path reported together with the style brief and duration.
Anything else is not done — say so plainly and show the failure row above.
