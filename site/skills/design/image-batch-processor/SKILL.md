---
name: image-batch-processor
description: >-
  Batch-process a folder of images locally with Pillow: compress (JPEG quality),
  resize to fit (keep aspect ratio), crop, overlay text/image watermarks with
  position and opacity, convert between jpg/png/webp, and optional OCR to .txt.
  Use when the user asks to batch compress images / resize images in a folder /
  add a watermark / OCR a screenshot / image batch processing / convert images
  to webp / prep platform covers. Do NOT use for generating new images from text
  (use image-generation), posting or uploading to platforms, or pixel-level
  creative editing in a raster editor.
license: Apache-2.0
compatibility: "Python 3.8+; requires Pillow (pip install pillow). --ocr additionally needs pytesseract and a tesseract binary; it degrades to a warning if absent. Reads inputs, writes only to --output; originals are never modified."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  verified-date: "2026-09-25"
---

# Image Batch Processor (Local Pillow Workbench)

Apply a fixed pipeline to every image in a folder in one run: resize -> crop ->
watermark -> compress/convert, writing results to an output directory while
preserving the folder's relative layout. Originals are never touched; `--dry-run`
prints the whole plan before anything is written.

## Applicability Decision Table

| Situation | Use this skill? | Notes |
|---|:---:|---|
| Resize/compress/watermark a whole folder at once | Yes | the core use case |
| Convert a batch to webp or jpg | Yes | `--format` |
| Extract text from screenshots/scans in bulk | Partial | needs pytesseract; warns if absent |
| Generate a new image from a prompt | No | use image-generation |
| Upload/publish to WeChat/Xiaohongshu/Bilibili | No | hand off to a publisher skill |
| Precise single-image retouching | No | use a raster editor |

## Input Checklist

| Input | Required | Default | Notes |
|---|:---:|---|---|
| `--input` | yes | - | image file or directory |
| `--output` | yes | - | results are written here; relative paths preserved |
| `--patterns` | no | jpg,jpeg,png,webp,bmp,tiff | which extensions to process |
| `--recursive` | no | off | descend into subfolders |
| Operation flags | no | - | at least one of resize/crop/watermark/compress/format |

When inputs are missing, ask once: the folder, the target platform or size, and
which operations (compress quality, watermark text, output format).

## Pre-flight Checks

```bash
python3 -c "import PIL; print('Pillow OK')"
df -h "$(dirname "$OUTPUT_DIR")"        # confirm free space for the batch
python3 scripts/batch_process.py --input "$DIR" --output /tmp/preview --dry-run
```

Remind the user that a backup of the originals is wise before large runs; this
script writes only to `--output`, so the source folder stays intact.

## Workflow

### Step 1: Scan
Point `--input` at the folder; add `--recursive` for subfolders. Dry-run lists
every matching image first.

### Step 2: Choose operations
Pick from the Operations Catalog below. Pipeline order is fixed: resize -> crop
-> watermark -> compress/format.

### Step 3: Dry-run preview
```bash
python3 scripts/batch_process.py --input photos/ --output out/ \
    --resize 1920x1080 --compress 80 --dry-run
```
Each line shows source -> destination and the operations applied; nothing writes.

### Step 4: Execute
Drop `--dry-run` to write. One corrupt image is skipped and reported; the batch
continues.

### Step 5: Verify
Spot-check output dimensions/size, open a watermarked sample, and confirm counts
match the dry-run.

## Operations Catalog

| Operation | Flag | Behavior |
|---|---|---|
| Compress | `--compress 80` | re-save as JPEG at quality 1-95 (implies jpg) |
| Resize (fit) | `--resize 1920x1080` or `--resize 1080` | keep aspect ratio; box fits inside, number sets longest side; never upscales |
| Crop | `--crop WxH+X+Y` | exact crop box, e.g. `800x600+100+50` |
| Text watermark | `--watermark-text "..."` | overlay at position, opacity 0.1-1.0, size `--watermark-size` |
| Image watermark | `--watermark-image logo.png` | overlay a PNG at position with opacity |
| Position | `--watermark-position` | center / top-left / top-right / bottom-left / bottom-right |
| Format convert | `--format jpg\|png\|webp` | change container; jpg flattens alpha onto white |

There is no rename flag in this CLI; output names keep the source stem (and may
change extension when `--format`/`--compress` picks jpg).

## OCR

Add `--ocr` to run `pytesseract` on each image and write a sibling `.txt` next to
the output. If pytesseract (or the tesseract binary) is missing, the script
prints a warning and skips OCR without failing the batch.

## Platform Size Quick Reference

Target the platform, then feed the matching box to `--resize` (fit keeps ratio).

| Platform | Recommended size |
|---|---|
| WeChat MP header | ~900x383 (use 896x384) |
| Xiaohongshu cover | 1080x1440 (3:4) |
| Bilibili / Toutiao banner | 1920x1080 (16:9) |
| Open Graph / share card | 1200x630 |
| Zhihu | 1536x1024 (3:2) |

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| `Pillow is required` | Pillow not installed | `pip install pillow` and rerun |
| `[skip] ... cannot identify image file` | Corrupt or unsupported image | That file is skipped; drop it or re-export it |
| `[skip] ... permission denied` | Output not writable | Check `--output` permissions/path, rerun |
| Resize looks stretched | Misreading fit semantics | `--resize` always keeps aspect ratio; use `--crop` for exact pixels |
| Watermark text tiny/huge | Font size mismatch | Tune `--watermark-size`; corner/center anchoring is automatic |
| JPEG output loses transparency | JPEG has no alpha | Transparency is flattened onto white; use `--format png` to keep it |
| `--ocr` does nothing | pytesseract/tesseract absent | `pip install pytesseract` and install the tesseract binary |

## Quality Checklist

- [ ] Pillow installed; output disk has free space
- [ ] `--dry-run` plan lists the right files and operations
- [ ] Originals untouched (output went to `--output`)
- [ ] Resized images kept aspect ratio; crop box within bounds
- [ ] Watermark position/opacity look right on a sample
- [ ] JPEG quality reasonable; webp/png as intended
- [ ] OCR `.txt` files produced when requested
- [ ] Output file count matches dry-run count

## Chain Handoff

- To **image-generation** (video domain): create new base images first, then
  batch-process them for platform sizing/watermarks.
- To **publisher skills** (writing domain): hand the sized images to the
  WeChat/Xiaohongshu/Bilibili publisher for upload.

## References

- `scripts/batch_process.py` — the runnable batch pipeline (flags in `--help`).
- `references/operations-catalog.md` — detailed operation and platform notes.
