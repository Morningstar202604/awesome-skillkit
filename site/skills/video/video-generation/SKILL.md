---
name: video-generation
description: >
  Generate short videos from text prompts or reference images through a local
  generation gateway (text-to-video and image-to-video with polling and
  download). Use when the user asks to generate a video / make a short video /
  text-to-video / image-to-video / make a video from this text / animate this
  image / generate a promo video, or wants AI-generated footage. Do NOT use
  for video editing, subtitle burning, screen recording, or downloading
  existing videos from the web.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Video Generation (Text-to-Video / Image-to-Video)

Drive the local generation gateway with curl: submit a task -> poll until done -> download the result -> hand the file path to the user. No ffmpeg needed, no Python media libraries, no dependencies to install — the gateway handles rendering, you handle orchestration.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| topic / brief | yes | — | What the video is about; the user's own words or a one-line brief |
| aspect_ratio | no | `16:9` | `16:9` landscape, `9:16` vertical, `1:1` square |
| duration | no | `6` | seconds; `6` or `10` |
| size | no | `720P` | `720P` or `1080P` |
| reference_image_url | no | — | Providing it switches to image-to-video mode |

When a required input is missing, ask everything at once; fill in the rest from defaults:

> Please provide: ① video topic or brief. Optionally tell me: ② aspect ratio (default 16:9), ③ duration
> (default 6 seconds, optional 10), ④ quality (default 720P), ⑤ reference image URL (image-to-video if provided).

## Pre-flight Checks

Run first — first resolve the gateway base URL (same command as workflow Step 1), then probe liveness:

```bash
VIDEO_GATEWAY_BASE="${VIDEO_GATEWAY_BASE:-http://127.0.0.1:30080}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$VIDEO_GATEWAY_BASE/api/video/status?task_id=0"
```

Expected: any HTTP code printed (gateway reachable). If it fails: curl exit code non-0 (connection failure) -> tell the user `$VIDEO_GATEWAY_BASE` is unreachable, ask them to start the gateway, STOP; HTTP 404 -> route name doesn't match the deployment; verify the endpoint against the gateway docs before continuing. Don't fall back to local rendering tools.

## Workflow

### Step 1: Confirm the Gateway Address

```bash
VIDEO_GATEWAY_BASE="${VIDEO_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$VIDEO_GATEWAY_BASE"
```

Expected: a URL printed, matching the address that passed the pre-flight probe.
If it fails: it expands to empty -> shell anomaly — stop. The URL differs from pre-flight -> trust the value that passed pre-flight; don't switch addresses mid-run.

### Step 2: Write the Prompt

Write just one descriptive paragraph covering action, scene, and mood. Follow the formula in `references/prompt-recipes.md` (read it first if the brief is thin or the user cares about quality). Never send a bare noun phrase as a prompt.

### Step 3: Submit the Generation Task

Text-to-video:

```bash
curl -s -X POST "$VIDEO_GATEWAY_BASE/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 PROMPT>","params":{"aspect_ratio":"16:9","duration":"6","size":"720P"}}'
```

For image-to-video, append `"images":["<url>"]` inside `params`.

Expected: JSON returned containing the task ID (`task_id`); extract and remember it. If it fails: HTTP error or HTML returned instead of JSON -> per the failure table, re-check Step 1's base value and rerun once as-is; if it fails again, report the status line to the user and stop.

### Step 4: Poll Until Terminal State

```bash
curl -s "$VIDEO_GATEWAY_BASE/api/video/status?task_id=<TASK_ID>"
```

Poll every 10 seconds. Success condition: `is_final == true` and `state == "success"`; then `result_url` is the download address. `is_final == true` but any other state means failure — see the failure table below. Polling no more than 60 times (10 minutes); on timeout you must give a clear report.
If it fails: `state == "failed"` -> rewrite per the prompt recipe and resubmit once; still `pending` after 10 minutes -> report `task_id` and suggest resubmitting; success but missing `result_url` -> flag the endpoint "verify before use" and report the raw JSON to maintainers.

### Step 5: Download & Deliver

```bash
curl -s -L -o "video_$(date +%Y%m%d_%H%M%S).mp4" "<RESULT_URL>"
ls -lh video_*.mp4
```

Expected: a non-empty .mp4 appears in the working directory. Confirm file size > 0 before declaring success. Report the absolute path to the user.
If it fails: file is 0 bytes -> `result_url` expired; re-poll for a fresh URL and download again; still 0 -> report honestly as incomplete, attaching the raw response.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| curl can't connect (pre-flight) | Gateway not started | Ask the user to start the gateway; stop |
| generate returns non-JSON | Wrong base URL or a proxy | Re-check Step 1's value, retry once, then report |
| status stays `pending` over 10 minutes | Queue stuck | Report task_id, suggest resubmitting |
| `state == "failed"` | Prompt rejected (usually too short) | Rewrite per the recipe, resubmit once |
| Downloaded file is 0 bytes | URL expired / signature invalid | Re-poll for a fresh result_url, download again |
| Success but missing `result_url` | API structure changed | Flag the endpoint "verify before use"; report raw JSON to maintainers |

## Delivery Standard

Success = a local `.mp4`, size > 0, named `video_YYYYMMDD_HHMMSS.mp4` (timestamped), with the path and the duration/ratio used reported to the user. Anything else counts as incomplete — say so plainly, and point to the matching row in the failure table above.

## References

- `references/prompt-recipes.md` — prompt formulas and strong/weak examples; read before writing any prompt
