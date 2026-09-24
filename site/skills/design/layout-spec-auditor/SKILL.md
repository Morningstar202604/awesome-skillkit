---
name: layout-spec-auditor
description: >-
  Audit a generated image (or its plan) against a design spec and platform layout
  rules: aspect ratio match, minimum resolution, safe-area margins for text,
  platform file-size limits, and text-budget compliance. Reads the actual image
  file with Pillow when available, or audits declared dimensions. Use when the
  user asks to check image specs / verify dimensions / audit an image / layout
  audit / cover spec / image compliance, or automatically after generating an
  image in the visual-design-studio chain. Do NOT use for judging aesthetics (that
  is design critique), nor for writing prompts.
license: Apache-2.0
compatibility: Python 3.8+; Pillow optional (needed only when auditing an actual image file).
metadata:
  author: "awesome-skillkit"
  version: "1.1"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Layout Spec Auditor

Chain gatekeeper. After the image is generated, it passes three gates before
delivery: **is the ratio right, is resolution enough, is text safe**. The canvas
agreed at the spec stage—off by 1% at delivery means rework.

## Domain Tacit Knowledge (Four Things to Know Before Auditing)

**1. Safe-area numbers come from measured platform UI positions, not empirical
mysticism.** This skill's "8% on all sides / 15% bottom" corresponds to measured
fact: Douyin and Bilibili covers **overlay duration labels in the lower-left**,
vertical platforms have progress bars and interaction buttons at bottom,
Xiaohongshu/Douyin feed cards have rounded-corner cropping—text or subject landing
in these areas gets covered by UI, not "slightly cropped". Different platforms'
overlay positions differ, so look up by platform, don't apply universal values.

**2. Contrast isn't an aesthetic issue, it's a compliance issue.** WCAG 2.x
quantitative floor: body text vs background **4.5:1** (AA), large text and UI
components **3:1**, AAA 7:1. This isn't editorial preference—WebAIM's million-page
annual scans show for years running, **insufficient contrast is the #1 web
accessibility violation (about 80% of home pages hit in recent scans)**. Same for
text burned into images: on-image title vs background contrast below 4.5:1 is
unreadable in bright-screen/thumbnail size; audit records it as "compliance
failure", not "style suggestion".

**3. Color-vision redundancy: about 8% of men have color-vision deficiency.**
Color blindness isn't rare (US National Eye Institute epidemiology: about 8% of
men, about 0.5% of women); red-green contrast is the most common failure combo.
If the image has information encoded only by color (status, category, before/
after comparison), add one audit check: is the information still distinguishable
after grayscale (desaturate the screenshot and glance, costs 10 seconds).
"Pass/fail" markers coded only by red/green are recorded as fail.

**4. The squint test is structural check, not aesthetic judgment.** This skill
doesn't judge aesthetics (that's design critique's job), but "is the first-glance
landing the subject" is a **structural** problem: shrink the image to thumb size
(or squint blur), if the first place the eye lands isn't the subject specified
in the spec, hierarchy failed—this directly corresponds to Gestalt contrast
principle and the universal squint test, is judgeable, and therefore belongs in
spec audit scope.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| Image file | one of two | actual output image (reads real size when Pillow available) |
| Declared dimensions | one of two | W×H when only a plan exists (pure audit calculation) |
| Design spec | yes | design-brief-interpreter output, platform field governs |

When inputs are missing, ask all at once: "Please provide: 1) actual image file
path (when image exists) or declared W×H (plan stage only); 2) target platform
name (determines acceptance spec)."

## Pre-flight Checks

```bash
test -f scripts/spec_audit.py && echo SCRIPT-OK
python3 -c "import PIL" 2>/dev/null && echo PIL-OK || echo PIL-MISSING
```

- Expected: `SCRIPT-OK` must appear; failure means skill package incomplete, STOP
  and suggest reinstall.
- `PIL-OK` only required when auditing a real image file (`--image`); when output
  is `PIL-MISSING`, fix by one of two options: `pip install pillow`, or switch to
  declared-dimensions mode (`--width/--height` pure calculation, doesn't read
  file). This machine confirms `spec_audit.py` without `--image` doesn't import
  PIL; declared-dimensions mode truly doesn't depend on Pillow.

## Workflow

### Step 1: Run Spec Audit Script

```bash
python3 scripts/spec_audit.py --image cover.png --platform wechat-header
python3 scripts/spec_audit.py --width 1080 --height 1440 --platform xhs-portrait
python3 scripts/spec_audit.py --image cover.png --platform wechat-header --text-chars 14
python3 scripts/spec_audit.py --width 900 --height 383 --expect 900x383 --file-mb 0.4   # numbers self-consistent → all pass (change any value to demo fail)
```

Output JSON: each item `pass/fail` and fix suggestion; exit 2 = usage error (like
missing `--image` or `--width/--height`), other non-zero exit = has fail items.

**Parameter discipline (measured)**: `--width/--height` and `--image` **must give
one of them**—only passing `--expect 900x383` returns `{"error": "need --image or
--width/--height"}` and exit 2. `--expect` is "custom target when platform not in
library", must pair with `--width/--height` (or `--image`), can't replace the
audited dimensions alone.

### Step 2: Check Against Platform Spec Table (Script Built-In)

Built-in spec library covers mainstream Chinese and overseas platforms (WeChat
header 900x383 / Xiaohongshu 3:4 vertical 1080x1440 and 1:1 square / Bilibili
cover 1146x717 / Douyin vertical 1080x1920 / YouTube thumbnail 1280x720 ≤2MB etc).
When platform not in library, use `--expect WxH` **paired with** `--width/--height`
to declare target W×H (see step 1 item 4 example).

### Step 3: Text Safe-Area Human Review

Script gives suggested values, human makes final call:

- All-side whitespace ≥ 8% of canvas short edge (platform UI controls cover
  edges—measured basis in tacit knowledge 1)
- Key text avoids bottom 15% (most platforms' info overlay area); Douyin/Bilibili
  covers additionally avoid lower-left duration label area
- On-image text total ≤ spec text field budget; over → return to image-prompt-engineer
  to cut text, don't shrink font to cram
- Text-to-background contrast ≥ 4.5:1 (WCAG AA, tacit knowledge 2); information
  encoded only by color does grayscale redundancy check (tacit knowledge 3)
- Thumbnail check: shrink image to thumb size, first-glance landing = spec subject
  (squint test, tacit knowledge 4)

### Step 4: Fail Items Flow Back

Size wrong → return to design-brief-interpreter to revise spec platform field then
rerun chain; text over budget → return to image-prompt-engineer to revise text
segment; **audit doesn't pass, can't deliver**.

## Delivery Criteria

- Artifact: audit result JSON (each item pass/fail and suggestion) + one-sentence
  conclusion (all pass deliverable / list fail items and handoff direction).
- Location: output directly in conversation; audited image file location unchanged.
- Integrity verification: script exit code 0 = all pass; non-zero exit must give
  item-by-item handling, "deliver with defects" forbidden.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Ratio off by a bit | Model doesn't precisely output target size | Crop to target ratio (keep subject centered), audit again |
| Resolution insufficient | Small image upscaled for delivery | Return to prompt to raise size params and regenerate, stretching/upscaling forbidden |
| Text covered by UI | Stepped on platform overlay area | Move composition focus per 8%/15% safe-area rules; Douyin/Bilibili additionally avoid lower-left (tacit knowledge 1) |
| On-image text unreadable at thumbnail | Insufficient contrast or font too small | Raise text/background contrast per WCAG 4.5:1 (tacit knowledge 2), or return to spec to cut text and enlarge |
| Red-green status markers indistinguishable in grayscale | Color-only encoding (tacit knowledge 3) | Record fail; add icon/shape/text redundancy encoding then re-audit |
| First-glance landing not subject | Hierarchy failed (tacit knowledge 4) | Record fail and flow back to spec: pull three size/luminance levels apart, accent only on subject |
| File over platform limit | Lossless PNG too large | Convert to compressed format and re-export; platform limits in spec table |

## Platform Spec Quick Reference (6 Common)

| Platform | Size | Ratio | Limit |
|------|------|------|------|
| WeChat header | 900x383 | 2.35:1 | ≤5MB |
| Xiaohongshu vertical | 1080x1440 | 3:4 | ≤32MB |
| Bilibili cover | 1146x717 | 1.6:1 | ≤5MB |
| Douyin vertical | 1080x1920 | 9:16 | — |
| YouTube thumbnail | 1280x720 | 16:9 | ≤2MB |
| Zhihu article header | landscape 16:9 | 16:9 | — |

Full table and update method see script's `PLATFORM_SPECS` (PR directly edits
table + run tests).

## References

- [scripts/spec_audit.py](scripts/spec_audit.py) — run platform spec audit: ratio/
  resolution/safe area/file size, output item-by-item pass/fail JSON
