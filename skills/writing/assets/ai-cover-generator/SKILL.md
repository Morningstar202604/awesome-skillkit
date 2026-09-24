---
name: ai-cover-generator
description: >
  Generates AI cover images and inline illustrations for articles across content
  platforms. Calls a local image-generation service to produce covers at the
  right dimensions (16-multiple, platform-specific ratios) and can compress to
  a <1MB JPG for easy upload. Use when the user asks to generate a cover image,
  article illustration, blog header, post thumbnail, generate a cover, create a
  blog illustration, or needs platform-specific image dimensions for Zhihu,
  WeChat MP, CNBlogs, Juejin, Xiaohongshu, etc. Do NOT use for cropping/editing
  existing images, OCR, video covers, or posting automation.
license: Apache-2.0
compatibility: Python 3.8+; the `--jpg` compression flag requires Pillow. A
  local image-generation service must be reachable at 127.0.0.1:30080.
metadata:
  author: awesome-skillkit
  version: "2.0"
  category: writing/assets
  pattern: single-task
  tier: standard
  verified-date: "2026-09-24"
---

# AI Cover Image Generator

## Overview

This skill produces cover images and inline illustrations for platform-adapted
articles. It submits a text-to-image task to a local image-generation service,
polls for completion, downloads the result, and optionally compresses it to a
<1MB JPG that is ready to upload to Zhihu, WeChat MP, CNBlogs, and other
platforms. It is a content-creation tool, not a posting tool.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| `--prompt` | yes | English prompt works best: subject + style + lighting + composition + palette |
| `--size WxH` | no | Must satisfy 16-multiple, ratio 1:3 to 3:1, total pixels 655360-8294400 |
| `--quality` | no | `auto` / `high` / `medium` / `low`; default `auto` |
| `--out` | no | Output path, e.g. `cover.png`; otherwise the script picks a location |
| `--jpg` | no | Also produce a <1MB compressed JPG (requires Pillow) |
| `--timeout` | no | Polling timeout in seconds; default 180 |

If required inputs are missing, ask once: "Please give me (1) the image concept
(or the style you want), (2) the target platform and size, (3) whether you need
a <1MB JPG. Defaults: `--size 1536x1024`, `--quality auto`, dry-run."

## Pre-Flight Checks

```bash
python3 --version                                                        # >= 3.8
test -f scripts/generate_cover.py && echo SCRIPT-OK                      # script present
python3 -c "import PIL; print('PIL-OK')" 2>/dev/null || echo "PIL missing: only affects --jpg"
curl -s -o /dev/null -w '%{http_code}\n' "${IMAGE_API_BASE:-http://127.0.0.1:30080}/api/image/status"
```

- Expect `SCRIPT-OK`; otherwise the skill package is incomplete — STOP and
  reinstall.
- Missing `PIL` does not block image generation; it only breaks `--jpg`.
- A 4xx response on the status probe is normal (gateway is up, no params); a
  `000` means the service is unreachable — tell the user to start the service,
  STOP, **do not fake a result**.

## Workflow

### Step 1: Preview the plan (dry-run by default)

```bash
python3 scripts/generate_cover.py --prompt "..." --size 1536x1024
```

Expected: prints the submit plan (endpoint, prompt, size, params) and the
dimension validation result, **without making a network request**.

If it fails: dimension validation fails — round to a 16-multiple within the
ratio and pixel bounds, then rerun; do not proceed with a bad size. Missing
`--prompt` — add it and rerun.

### Step 2: Submit and wait for completion

```bash
python3 scripts/generate_cover.py --execute \
  --prompt "Dark tech blog cover, isometric illustration of content pipelines across platforms, flat design, #0d1117 background, green #238636 and blue #58a6ff accents" \
  --size 1536x1024 --out cover.png --jpg --timeout 180
```

Expected: task submitted -> poll until `is_final=true && state=="success"` ->
download to `--out`; produces a non-empty PNG, and with `--jpg` a sibling <1MB
JPG.

- `--jpg`: additionally compresses a <1MB JPG (Zhihu / WeChat MP uploads prefer
  small files).
- If the service is unreachable, exit 1 — it never pretends success.

If it fails: service unreachable (exit 1) — ask the user to start the
127.0.0.1:30080 service and rerun; **do not fabricate a placeholder image**.
Polling timeout — raise `--timeout` and rerun; if still no result, report the
task_id to the service maintainer. `--jpg` compression failed —
`pip install pillow` and rerun, or drop `--jpg` and deliver the PNG. Downloaded
file is 0 bytes — repoll for a fresh `result_url` and download again.

### Step 3: Pick prompt and size by platform

| Platform | Recommended prompt elements | Size |
|---|---|---|
| CNBlogs | Dark #0d1117 background + #238636/#58a6ff accents, flat design, no gradient | 1536x1024 (3:2) |
| Zhihu | Scene-based illustration, avoid pure-gradient "PPT" look | 1536x1024 |
| WeChat MP | Header near 900x383 cropped to 16-multiple (e.g. 896x384) | 896x384 |
| Xiaohongshu | Portrait cover with large text, bright/high-saturation | 1080x1440 (3:4) |
| Toutiao / Baijiahao / Bilibili | Wide feed image, high contrast | 1920x1080 (16:9) |
| Static blog | Open Graph share card | 1200x630 |

English prompts are most reliable: subject + style + lighting + composition +
palette.

If the target platform is not in the table, look up its official dimension spec
and verify the 16-multiple and pixel bounds; if it does not fit, pick the
closest legal size and tell the user. Do not ask the model to render Chinese
characters — it produces garbled glyphs; add text in post.

## Service Contract

Matches the local ai-image-gen service:

- **Submit**: `POST /api/image/generate`
  `{"model":"gpt-image-2","prompt":"...","params":{"size":"1792x1024","quality":"auto","n":1}}`
- **Poll**: `GET /api/image/status?task_id=...`; when
  `is_final=true && state=="success"`, `result_url` is the download URL.
- **Dimension rules**: width and height are multiples of 16; ratio 1:3 to 3:1;
  total pixels 655360-8294400 (validated before submit).

## Parameter Cheat-Sheet

| Flag | Values | Description |
|---|---|---|
| `--prompt` | string | Image description; English works best |
| `--size` | `WxH` | Must pass 16-multiple / ratio / pixel checks |
| `--quality` | auto/high/medium/low | Default `auto` |
| `--out` | path | Where the image is saved |
| `--jpg` | flag | Also output a <1MB JPG (needs Pillow) |
| `--execute` | flag | Without it, only prints the plan, no network |
| `--timeout` | seconds | Polling timeout; default 180 |

## Failure Handling

| Symptom | Cause | Fix |
|---|---|---|
| Service unreachable, exit 1 | Local image service not started | Ask user to start 127.0.0.1:30080 and rerun; never fake a placeholder |
| Dimension validation fails | Width/height not 16-multiple / ratio or pixel out of bounds | Round to a 16-multiple inside the pixel bounds and rerun |
| Polling timeout | Queue stuck or `--timeout` too short | Raise timeout and rerun; report task_id if still stuck |
| `--jpg` fails | Pillow not installed | `pip install pillow` and rerun, or drop `--jpg` and deliver PNG |
| Downloaded file is 0 bytes | `result_url` expired | Repoll for a fresh `result_url` and download again |
| Garbled text in the image | Prompt asked the model to render Chinese characters | Describe the scene only; add text in post |

## Deliverable Standard

- **Success**: the `--out` file exists and is non-empty; with `--jpg`, a
  sibling <1MB JPG is ready to upload.
- **Naming**: `cover.png` / `cover.jpg` (or whatever `--out` names).
- **Location**: wherever `--out` points; default is the caller's cwd.
- **Verification**: `ls -lh <out>` confirms non-zero bytes; eyeball that the
  subject matches the prompt.
- **If the service is unreachable, exit with an error — never pass a placeholder
  as success.**

## Integration With Other Skills

- The "generate illustration" step inside `cnblogs-skill`, `zhihu-content-manager`,
  and other platform skills calls this skill.
- The produced JPG path is handed to the user for manual upload to the target
  platform.

## Reference

- [scripts/generate_cover.py](scripts/generate_cover.py) — main script: dimension
  validation, submit, poll, download, and JPG compression.
