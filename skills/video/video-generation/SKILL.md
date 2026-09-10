---
name: video-generation
description: >
  Generate short videos from text prompts or reference images through a local
  generation gateway (text-to-video and image-to-video with polling and
  download). Use when the user asks to 生成视频 / 做个短视频 / 文生视频 /
  图生视频 / make a video from this text / animate this image / 生成宣传片,
  or wants AI-generated footage. Do NOT use for video editing, subtitle
  burning, screen recording, or downloading existing videos from the web.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Video Generation (text-to-video / image-to-video)

Drive a local generation gateway with curl: submit a task, poll until done,
download the result, hand the file path to the user. No ffmpeg, no Python
media stacks, no dependency installs — the gateway renders, you orchestrate.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| topic / 文案 | yes | — | what the video shows; user text or a one-line brief |
| aspect_ratio | no | `16:9` | `16:9` landscape, `9:16` vertical, `1:1` square |
| duration | no | `6` | seconds; `6` or `10` |
| size | no | `720P` | `720P` or `1080P` |
| reference_image_url | no | — | switches mode to image-to-video |

If any required input is missing, ask ONCE, filling defaults for the rest:

> 请提供：① 视频主题或文案。可选告知：② 画面比例（默认 16:9）、③ 时长
> （默认 6 秒，可选 10）、④ 画质（默认 720P）、⑤ 参考图 URL（有则走图生视频）。

## Preflight self-check

Run before anything else (BASE comes from step 1 of the workflow):

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$VIDEO_GATEWAY_BASE/api/video/status?task_id=0"
```

Expected: any HTTP code printed (gateway reachable). If curl fails to connect
(exit != 0): tell the user the gateway is unreachable at $VIDEO_GATEWAY_BASE,
ask them to start it, and STOP. Do not fall back to local rendering tools.

## Workflow

### Step 1: Resolve the gateway base

```bash
VIDEO_GATEWAY_BASE="${VIDEO_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$VIDEO_GATEWAY_BASE"
```

Expected: prints one URL. If empty after expansion, the shell is broken — stop.

### Step 2: Compose the prompt

Build ONE descriptive paragraph covering action, scene, and mood. Follow the
formula in `references/prompt-recipes.md` (read it whenever the brief is thin
or the user cares about quality). Never send a bare noun phrase as the prompt.

### Step 3: Submit the generation task

Text-to-video:

```bash
curl -s -X POST "$VIDEO_GATEWAY_BASE/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 PROMPT>","params":{"aspect_ratio":"16:9","duration":"6","size":"720P"}}'
```

Image-to-video adds `"images":["<url>"]` inside `params`.

Expected: JSON containing a task id (`task_id`). Extract it and remember it.
Failure branch — HTTP error or HTML instead of JSON: re-run once verbatim;
if it fails again, report the status line to the user and stop (see failures).

### Step 4: Poll until final

```bash
curl -s "$VIDEO_GATEWAY_BASE/api/video/status?task_id=<TASK_ID>"
```

Poll every 10 seconds. Success condition: `is_final == true` AND
`state == "success"`; then `result_url` holds the download address.
`is_final == true` with any other state is a FAILURE — go to Step 6's table.
Do not poll more than 60 times (10 min); time out with a clear report.

### Step 5: Download and deliver

```bash
curl -s -L -o "video_$(date +%Y%m%d_%H%M%S).mp4" "<RESULT_URL>"
ls -lh video_*.mp4
```

Expected: a non-empty .mp4 in the working directory. Verify size > 0 before
claiming success. Report the absolute path to the user.

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| curl cannot connect (preflight) | gateway down | ask user to start it; stop |
| generate returns non-JSON | wrong base URL or proxy | re-check Step 1 value once, retry once, then report |
| status stays `pending` > 10 min | queue stuck | report task_id, suggest resubmitting |
| `state == "failed"` | prompt rejected (often too short) | rewrite prompt per recipes, resubmit once |
| downloaded file 0 bytes | expired/signed-out URL | re-poll status for fresh result_url, redownload once |
| `result_url` missing though success | API shape changed | mark endpoint VERIFY BEFORE USE; report raw JSON to maintainer |

## Delivery standard

Success = a local `.mp4`, size > 0, named `video_YYYYMMDD_HHHHMMSS.mp4`
(timestamped), path reported to the user together with duration/ratio used.
Anything else is not done — say so plainly and show the failure row above.

## References

- `references/prompt-recipes.md` — prompt formula plus strong/weak examples; read before composing any prompt
