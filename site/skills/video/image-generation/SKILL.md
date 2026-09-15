---
name: image-generation
description: >
  Generate images from text prompts or reference images through a local
  generation gateway (text-to-image and image-to-image with polling and
  download). Use when the user asks to 生成图片 / 画一张 / 文生图 /
  图生图 / 改图 / generate an image of / create a picture / edit this photo,
  or wants AI artwork, illustrations, covers, or product renders.
  Do NOT use for screenshot capture, cropping/resizing existing files,
  or OCR — those need local tools, not this skill.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-08-26"
---

# Image Generation (text-to-image / image-to-image)

Drive a local generation gateway with curl: submit a task, poll until done,
download the PNG, hand the file path to the user. No Pillow/OpenCV, no
dependency installs — the gateway renders, you orchestrate.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| subject description | yes | — | what the image shows; see prompt formula below |
| size | no | `1024x1024` | any WxH where both are multiples of 16 |
| quality | no | `auto` | `auto` / `high` / `medium` / `low` |
| n | no | `1` | number of images |
| reference_image_urls | no | — | up to 14 URLs; switches mode to image-to-image |

Size constraints (VERIFY BEFORE USE against your gateway docs):
both dimensions must be multiples of 16; aspect ratio within 1:3–3:1;
total pixels between 655360 and 8294400.

Common sizes: 1024x1024, 1024x1536, 1536x1024, 960x1280, 1280x960,
1088x1920, 1920x1088, 2048x2048, 2048x3072, 3072x2048, 1920x2560,
2560x1920, 1440x2560, 2560x1440, 2160x3840, 3840x2160.

If the required input is missing, ask ONCE:

> 请描述想要的画面：主体、风格、用途（如封面/插画/产品图）。可选告知：
> 尺寸（默认 1024x1024）、画质（默认 auto）、数量（默认 1）、参考图 URL。

## Preflight self-check

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$IMAGE_GATEWAY_BASE/api/image/status?task_id=0"
```

Expected: an HTTP code prints (gateway reachable). If connection fails:
report the base URL problem, ask the user to start the gateway, STOP.
Never fall back to drawing tools or placeholder files.

## Workflow

### Step 1: Resolve the gateway base

```bash
IMAGE_GATEWAY_BASE="${IMAGE_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$IMAGE_GATEWAY_BASE"
```

Expected: prints one URL.

### Step 2: Compose the prompt

Describe objects, style, and any text layout precisely — instruction clarity
and detail fidelity dominate output quality. Structure:

```
[主体与细节] + [风格/媒介] + [构图与视角] + [文字排版要求，如有]
```

Rules: concrete nouns over adjectives ("磨砂玻璃瓶上的水珠" not
"好看的瓶子"); state style once clearly ("扁平插画、有限四色"); if the image
must contain text, quote the exact string and its position ("顶部横排文字：
春季上新").

### Step 3: Submit the task

Text-to-image:

```bash
curl -s -X POST "$IMAGE_GATEWAY_BASE/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"<STEP-2 PROMPT>","params":{"size":"1024x1024","quality":"auto","n":1}}'
```

Image-to-image adds `"images":["<url>", ...]` inside `params`.

Expected: JSON containing `task_id`. Failure branch — HTTP error or HTML:
retry once verbatim, then report the status line and stop.

### Step 4: Poll until final

```bash
curl -s "$IMAGE_GATEWAY_BASE/api/image/status?task_id=<TASK_ID>"
```

Poll every 3–5 seconds. Success condition: `is_final == true` AND
`state == "success"`; take `result_url`. `is_final == true` with any other
state is FAILURE — use the table below. Cap at 120 polls (≈8 min).

### Step 5: Download and deliver

```bash
curl -s -L -o "image_$(date +%Y%m%d_%H%M%S).png" "<RESULT_URL>"
ls -lh image_*.png
```

Expected: non-empty .png in the working directory. Verify size > 0 before
claiming success; report the absolute path.

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| curl cannot connect (preflight) | gateway down | ask user to start it; stop |
| generate returns size/param error | constraint violation | fix size to multiples-of-16 + pixel/ratio bounds, resubmit once |
| status stays `pending` > 8 min | queue stuck | report task_id, suggest resubmitting |
| `state == "failed"` | prompt too vague or violating policy | rewrite prompt with concrete details, resubmit once |
| downloaded file 0 bytes | expired URL | re-poll for fresh result_url, redownload once |
| `result_url` missing though success | API shape changed | mark endpoint VERIFY BEFORE USE; report raw JSON to maintainer |

## Delivery standard

Success = a local `.png`, size > 0, named `image_YYYYMMDD_HHMMSS.png`
(timestamped), absolute path reported together with size/quality used.
Anything else is not done — say so plainly and show the failure row above.
