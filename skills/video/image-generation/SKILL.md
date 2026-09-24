---
name: image-generation
description: >
  Generate images from text prompts or reference images through a local
  generation gateway (text-to-image and image-to-image with polling and
  download). Use when the user asks to generate an image / draw a picture /
  text-to-image / image-to-image / edit this photo / create artwork /
  make an illustration / design a cover / product render, or wants AI
  artwork. Do NOT use for screenshot capture, cropping/resizing existing
  files, or OCR — those need local tools, not this skill.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Image Generation (Text-to-Image / Image-to-Image)

Drive the local generation gateway with curl: submit a task -> poll until done -> download the PNG -> hand the file path to the user. No Pillow/OpenCV needed, no dependencies to install — the gateway handles rendering, you handle orchestration.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| scene description | yes | — | What to draw; write it per the prompt formula below |
| size | no | `1024x1024` | Any width/height, both multiples of 16 |
| quality | no | `auto` | `auto` / `high` / `medium` / `low` |
| n | no | `1` | Number of images to generate |
| reference_image_urls | no | — | Up to 14 URLs; providing them switches to image-to-image mode |

Size constraints (verify against the gateway docs before use): both dimensions must be multiples of 16; aspect ratio between 1:3 and 3:1; total pixels between 655360 and 8294400.

Common sizes: 1024x1024, 1024x1536, 1536x1024, 960x1280, 1280x960, 1088x1920, 1920x1088, 2048x2048, 2048x3072, 3072x2048, 1920x2560, 2560x1920, 1440x2560, 2560x1440, 2160x3840, 3840x2160.

When a required input is missing, ask everything at once:

> Please describe the desired image: subject, style, purpose (e.g., cover / illustration / product shot). Optionally tell me:
> size (default 1024x1024), quality (default auto), count (default 1), reference image URLs.

## Pre-flight Checks

First resolve the gateway base URL (same command as workflow Step 1, keep it for later use), then probe liveness:

```bash
IMAGE_GATEWAY_BASE="${IMAGE_GATEWAY_BASE:-http://127.0.0.1:30080}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$IMAGE_GATEWAY_BASE/api/image/status?task_id=0"
```

Expected: any HTTP code printed (gateway reachable). If it fails: curl exit code non-0 -> report a base-URL problem, ask the user to start the gateway, STOP; HTTP 401/403 -> gateway is running but needs auth; confirm credentials come from env vars; HTTP 404 -> route name doesn't match the deployment; verify the endpoint against the gateway docs. Never fall back to a local drawing tool or placeholder file.

## Workflow

### Step 1: Confirm the Gateway Address

```bash
IMAGE_GATEWAY_BASE="${IMAGE_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$IMAGE_GATEWAY_BASE"
```

Expected: a URL printed.
If it fails: it expands to empty -> shell anomaly (or the env var was explicitly set to empty); use the literal base URL and tell the user. The URL differs from the pre-flight probe -> trust the value that passed the pre-flight; don't switch addresses mid-run.

### Step 2: Write the Prompt

Describe objects, style, and text layout precisely — whether the instruction is clear and faithful to detail determines output quality. Structure:

```json
[subject & details] + [style/medium] + [composition & viewpoint] + [text layout requirements, if any]
```

Rules: concrete nouns beat adjectives (write "water droplets on a frosted glass bottle", not "a nice-looking bottle"); state the style once, clearly ("flat illustration, limited four-color palette"); if text must appear in the image, quote the string verbatim and mark its position ("top horizontal text: Spring Launch").

Expected: the prompt contains all four components, and on-image text is already quoted verbatim.
If it fails: can't write concrete nouns (only words like "nice / premium") -> go back to the input checklist and ask the user for a reference object or purpose (cover / illustration / product shot); convert the reference into a concrete description. If the image needs Chinese text and the model renders it unreliably -> switch to a textless base image + post-production layout, and say so in delivery.

### Step 3: Submit the Task

Text-to-image:

```bash
curl -s -X POST "$IMAGE_GATEWAY_BASE/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"<STEP-2 PROMPT>","params":{"size":"1024x1024","quality":"auto","n":1}}'
```

For image-to-image, append `"images":["<url>", ...]` inside `params`.

Expected: JSON returned containing `task_id`. If it fails: HTTP error or HTML returned -> retry once as-is; still failing -> report the status line per the failure table and stop. Returns a size/params error -> adjust the size per the constraints and resubmit once.

### Step 4: Poll Until Terminal State

```bash
curl -s "$IMAGE_GATEWAY_BASE/api/image/status?task_id=<TASK_ID>"
```

Poll every 3-5 seconds. Success condition: `is_final == true` and `state == "success"`; take `result_url`. `is_final == true` but any other state means failure — see the failure table below. Polling cap: 120 times (~8 minutes).
If it fails: `state == "failed"` -> rewrite the prompt with more concrete detail and resubmit once; still not terminal after 8 minutes -> report the `task_id` and suggest resubmitting; `is_final == true` but `result_url` missing -> flag the endpoint "verify before use" and report the raw JSON to maintainers.

### Step 5: Download & Deliver

```bash
curl -s -L -o "image_$(date +%Y%m%d_%H%M%S).png" "<RESULT_URL>"
ls -lh image_*.png
```

Expected: a non-empty .png appears in the working directory. Confirm file size > 0 before declaring success; report the absolute path.
If it fails: file is 0 bytes -> `result_url` expired; re-poll for a fresh URL and download again; still 0 -> report to the user with the raw response; do not pass off a placeholder as success.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| curl can't connect (pre-flight) | Gateway not started | Ask the user to start the gateway; stop |
| generate returns a size/params error | Violates size constraints | Change to a multiple-of-16 size within pixel/ratio bounds, resubmit once |
| status stays `pending` over 8 minutes | Queue stuck | Report task_id, suggest resubmitting |
| `state == "failed"` | Prompt too vague or policy-triggering | Rewrite the prompt with concrete detail, resubmit once |
| Downloaded file is 0 bytes | URL expired | Re-poll for a fresh result_url, download again |
| Success but missing `result_url` | API structure changed | Flag the endpoint "verify before use"; report raw JSON to maintainers |

## Delivery Standard

Success = a local `.png` file, size > 0, named `image_YYYYMMDD_HHMMSS.png` (timestamped), with the absolute path and the size/quality used reported. Anything else counts as incomplete — say so plainly, and point to the matching row in the failure table above.

## References

- This skill is pure prompt-based; no external reference files needed.
