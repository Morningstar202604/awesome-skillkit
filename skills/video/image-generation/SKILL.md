---
name: image-generation
description: >
  Generate images from text prompts or reference images through a local
  generation gateway (text-to-image and image-to-image with polling and
  download), including platform-specific covers and banners at the right
  dimensions (WeChat MP 896x384, Xiaohongshu 3:4, Bilibili 16:9, Open Graph
  1200x630, and more), with an optional <1MB JPG for upload. Use when the user
  asks to generate an image / draw a picture / text-to-image / image-to-image /
  edit this photo / create artwork / make an illustration / design a cover /
  blog header / article banner / post thumbnail / product render, or wants AI
  artwork or platform cover sizes. Do NOT use for screenshot capture,
  cropping/resizing existing files, posting automation, or OCR — those need
  local tools, not this skill.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
  The optional scripts/generate_cover.py convenience wrapper needs Python 3.8+;
  its --jpg compression flag additionally requires Pillow.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-09-24"
---

# Image Generation (Text-to-Image / Image-to-Image, incl. Platform Covers)

Drive the local generation gateway with curl: submit a task -> poll until done -> download the PNG -> hand the file path to the user. No Pillow/OpenCV needed for the core flow, no dependencies to install — the gateway handles rendering, you handle orchestration. For platform covers/banners you can either drive the curl flow directly, or use the bundled `scripts/generate_cover.py` wrapper, which validates dimensions, prints a dry-run plan first, and can emit a <1MB upload-ready JPG.

## Domain Tacit Knowledge (What Makes a Good Generated Image)

**1. Concrete nouns beat adjectives every time.** "Water droplets on a frosted glass bottle with a citrus slice" produces a specific, high-quality image. "A beautiful refreshing drink" produces a generic stock-photo look. Swap every adjective for a concrete noun or detail before submitting.

**2. State the style once, clearly, at the end.** Don't stack style tags ("photorealistic, cinematic, 8k, ultra detailed, award-winning"). Pick one medium/style and state it clearly: "flat vector illustration, limited three-color palette" or "35mm film photograph, shallow depth of field". More style tags = more confusion, not more quality.

**3. Chinese text in images is unreliable.** Most image models render Latin alphabet well but produce garbled Chinese characters. If the final image needs Chinese text (cover titles, labels), generate a textless base image and add the text in post-production (Canva, Photoshop, or the platform's editor). Never ask the model to render Chinese characters.

**4. Reference images lock style and subject.** Providing 1-2 reference images (image-to-image mode) dramatically improves consistency for series work. Use a style reference to lock the visual tone, and a subject reference to keep character/product likeness consistent across a batch.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| scene description | yes | — | What to draw; write it per the prompt formula below |
| size | no | `1024x1024` | Any width/height, both multiples of 16; for a platform cover use the table below |
| quality | no | `auto` | `auto` / `high` / `medium` / `low` |
| n | no | `1` | Number of images to generate |
| reference_image_urls | no | — | Up to 14 URLs; providing them switches to image-to-image mode |
| --jpg | no | off | (wrapper only) also emit a <1MB JPG; requires Pillow |

Size constraints (verify against the gateway docs before use): both dimensions must be multiples of 16; aspect ratio between 1:3 and 3:1; total pixels between 655360 and 8294400.

Common sizes: 1024x1024, 1024x1536, 1536x1024, 960x1280, 1280x960, 1088x1920, 1920x1088, 2048x2048, 2048x3072, 3072x2048, 1920x2560, 2560x1920, 1440x2560, 2560x1440, 2160x3840, 3840x2160.

When a required input is missing, ask everything at once:

> Please describe the desired image: subject, style, purpose (e.g., cover / illustration / product shot). Optionally tell me:
> target platform and size (see the platform cover table), size (default 1024x1024), quality (default auto), count (default 1), reference image URLs, whether you need a <1MB JPG.

## Platform Cover & Banner Sizes

Pick the platform first, then round to a 16-multiple inside the pixel/ratio bounds. English prompts are most reliable: subject + style + lighting + composition + palette.

| Platform | Recommended prompt elements | Size |
|---|---|---|
| CNBlogs | Dark #0d1117 background + #238636/#58a6ff accents, flat design, no gradient | 1536x1024 (3:2) |
| Zhihu | Scene-based illustration, avoid a pure-gradient "PPT" look | 1536x1024 |
| WeChat MP | Header near 900x383, cropped to a 16-multiple | 896x384 |
| Xiaohongshu | Portrait cover with large text, bright/high-saturation | 1080x1440 (3:4) |
| Toutiao / Baijiahao / Bilibili | Wide feed image, high contrast | 1920x1080 (16:9) |
| Static blog / Open Graph | Share card | 1200x630 |

If the target platform is not in the table, look up its official dimension spec and verify the 16-multiple and pixel bounds; if it does not fit, pick the closest legal size and tell the user. Do not ask the model to render Chinese characters — it produces garbled glyphs; add text in post.

## Pre-flight Checks

First resolve the gateway base URL (same command as workflow Step 1, keep it for later use), then probe liveness:

```bash
IMAGE_GATEWAY_BASE="${IMAGE_GATEWAY_BASE:-http://127.0.0.1:30080}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$IMAGE_GATEWAY_BASE/api/image/status?task_id=0"
```

Expected: any HTTP code printed (gateway reachable). A 4xx on the status probe is normal (the service is up, no params); `000` means it is unreachable. If it fails: curl exit code non-0 -> report a base-URL problem, ask the user to start the gateway, STOP and never fake a result; HTTP 401/403 -> gateway is running but needs auth; confirm credentials come from env vars; HTTP 404 -> route name doesn't match the deployment; verify the endpoint against the gateway docs. Never fall back to a local drawing tool or placeholder file.

When using the wrapper script, also confirm it is present and Python is available:

```bash
test -f scripts/generate_cover.py && echo SCRIPT-OK          # wrapper present
python3 --version                                             # >= 3.8
python3 -c "import PIL; print('PIL-OK')" 2>/dev/null || echo "PIL missing: only affects --jpg"
```

Missing PIL does not block generation; it only breaks `--jpg`.

## Workflow

You have two equivalent paths: drive curl directly (full control), or run the bundled `scripts/generate_cover.py` wrapper (dry-run by default, built-in dimension validation, optional JPG compression). Both hit the same service contract below.

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

### Step 3a: Submit via curl (direct path)

Text-to-image:

```bash
curl -s -X POST "$IMAGE_GATEWAY_BASE/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"<STEP-2 PROMPT>","params":{"size":"1024x1024","quality":"auto","n":1}}'
```

For image-to-image, append `"images":["<url>", ...]` inside `params`.

Expected: JSON returned containing `task_id`. If it fails: HTTP error or HTML returned -> retry once as-is; still failing -> report the status line per the failure table and stop. Returns a size/params error -> adjust the size per the constraints and resubmit once.

### Step 3b: Submit via the wrapper script (cover/banner path, dry-run by default)

The wrapper validates dimensions and prints the submit plan WITHOUT making a network request unless `--execute` is passed:

```bash
# Dry run: prints endpoint + prompt + size + dimension validation, no network
python3 scripts/generate_cover.py --prompt "..." --size 1536x1024

# Execute: submit, poll, download, optionally compress a <1MB JPG
python3 scripts/generate_cover.py --execute \
  --prompt "Dark tech blog cover, isometric illustration of content pipelines across platforms, flat design, #0d1117 background, green #238636 and blue #58a6ff accents" \
  --size 1536x1024 --out cover.png --jpg --timeout 180
```

Wrapper flags: `--prompt` (required), `--size WxH` (default 1792x1024, must pass 16-multiple/ratio/pixel checks), `--quality` (auto/high/medium/low), `--out` (default cover.png), `--jpg` (also emit a <1MB JPG, needs Pillow), `--execute` (without it, only prints the plan), `--timeout` (polling seconds, default 180).

Expected (dry run): prints the submit plan and the dimension validation result, no network. Expected (execute): task submitted -> poll until `is_final=true && state=="success"` -> download to `--out`; a non-empty PNG, and with `--jpg` a sibling <1MB JPG.
If it fails: dimension validation fails -> round to a 16-multiple within the ratio and pixel bounds, rerun; do not proceed with a bad size. Service unreachable (exit 1) -> ask the user to start the 127.0.0.1:30080 service and rerun; never fabricate a placeholder. Polling timeout -> raise `--timeout` and rerun; report the task_id if still stuck. `--jpg` fails -> `pip install pillow` and rerun, or drop `--jpg` and deliver the PNG.

### Step 4: Poll Until Terminal State

```bash
curl -s "$IMAGE_GATEWAY_BASE/api/image/status?task_id=<TASK_ID>"
```

Poll every 3-5 seconds. Success condition: `is_final == true` and `state == "success"`; take `result_url`. `is_final == true` but any other state means failure — see the failure table below. Polling cap: 120 times (~8 minutes). The wrapper polls automatically inside Step 3b.
If it fails: `state == "failed"` -> rewrite the prompt with more concrete detail and resubmit once; still not terminal after 8 minutes -> report the `task_id` and suggest resubmitting; `is_final == true` but `result_url` missing -> flag the endpoint "verify before use" and report the raw JSON to maintainers.

### Step 5: Download & Deliver

```bash
curl -s -L -o "image_$(date +%Y%m%d_%H%M%S).png" "<RESULT_URL>"
ls -lh image_*.png
```

Expected: a non-empty .png appears in the working directory. Confirm file size > 0 before declaring success; report the absolute path.
If it fails: file is 0 bytes -> `result_url` expired; re-poll for a fresh URL and download again; still 0 -> report to the user with the raw response; do not pass off a placeholder as success.

## Service Contract

Matches the local ai-image-gen service (used by both the curl flow and the wrapper):

- **Submit**: `POST /api/image/generate`
  `{"model":"gpt-image-2","prompt":"...","params":{"size":"1792x1024","quality":"auto","n":1}}` -> response contains `task_id` (the wrapper tolerates `{task_id}`, `{data:{task_id}}`, and `{data:{task:{id}}}`).
- **Poll**: `GET /api/image/status?task_id=...`; when `is_final=true && state=="success"`, `result_url` is the download URL.
- **Dimension rules**: width and height are multiples of 16; ratio 1:3 to 3:1; total pixels 655360-8294400 (validated before submit).

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| curl can't connect (pre-flight), or probe prints `000` | Gateway not started | Ask the user to start the gateway; stop; never fake a result |
| generate returns a size/params error, or wrapper dimension validation fails | Violates size constraints | Change to a multiple-of-16 size within pixel/ratio bounds, resubmit once |
| status stays `pending` over 8 minutes / wrapper times out | Queue stuck | Report task_id, suggest resubmitting; raise wrapper `--timeout` |
| `state == "failed"` | Prompt too vague or policy-triggering | Rewrite the prompt with concrete detail, resubmit once |
| Downloaded file is 0 bytes | URL expired | Re-poll for a fresh result_url, download again |
| Success but missing `result_url` | API structure changed | Flag the endpoint "verify before use"; report raw JSON to maintainers |
| `--jpg` compression fails | Pillow not installed | `pip install pillow` and rerun, or drop `--jpg` and deliver the PNG |
| Garbled text in the image | Prompt asked the model to render Chinese characters | Describe the scene only; add text in post |

## Quality Checklist

- [ ] Gateway reachable and responding
- [ ] Prompt has all four components (subject + style + composition + text if any)
- [ ] Concrete nouns used instead of vague adjectives
- [ ] Style stated once, clearly (not a stack of tags)
- [ ] Size is a multiple of 16, within ratio and pixel bounds
- [ ] Platform cover size matches the intended platform (table above)
- [ ] No Chinese text requested in the prompt (add text in post)
- [ ] Output file exists and is non-empty
- [ ] Aspect ratio matches the intended use case

## Delivery Standard

Success = a local `.png` file, size > 0, named `image_YYYYMMDD_HHMMSS.png` (timestamped) or whatever `--out` names (e.g. `cover.png`), with the absolute path and the size/quality used reported. With `--jpg`, a sibling <1MB JPG ready to upload. Verify with `ls -lh <out>` (non-zero bytes) and eyeball that the subject matches the prompt. Anything else counts as incomplete — say so plainly, and point to the matching row in the failure table above. If the service is unreachable, exit with an error — never pass a placeholder as success.

## References

- [scripts/generate_cover.py](scripts/generate_cover.py) — optional wrapper: dimension validation, dry-run plan, submit, poll, download, and <1MB JPG compression.
- This skill is otherwise pure prompt-based; no external reference files needed.
