---
name: format-converter
description: >-
  One entry point for format conversion: documents via pandoc, images via Pillow
  (with resize and quality), audio/video via ffmpeg, plus directory batch mode.
  Probes every external dependency first and prints the exact install command
  when something is missing. Use when the user asks to convert file format /
  png to jpg / batch convert images / compress image size / video transcode /
  format conversion / media conversion utility. Do NOT use for editing file
  contents, extracting archives, or OCR of scanned documents.
license: Apache-2.0
compatibility: "Python 3.8+. Image mode requires Pillow (pip install pillow). Document mode requires pandoc. Media mode requires ffmpeg. Batch mode defaults to dry-run and needs --yes to write."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Format Converter (Unified Format Conversion Entry)

Solves "this file I have needs to become another format"—three pipelines
(document/image/audio-video) collapsed into one command.

**Core judgment: probe dependencies first, then convert.** Three pipelines each
depend on external tools (pandoc / Pillow / ffmpeg); missing any yields only a
`command not found`—so before each subcommand runs, find the binary or library;
when missing, print **the exact install command for the current OS** and exit
with code 4. Never ship a half-done product pretending it succeeded.

## Input Checklist

| Input | Required | Notes |
|------|:---:|------|
| Input file / directory | yes | `doc`/`image`/`media` take two positional args `<in> <out>`; `batch` takes one directory |
| Target format | yes | Inferred from output extension (`.docx`/`.jpg`/`.mp4`…); `batch` uses `--to <ext>` |
| `--width` / `--quality` | no | Image only: proportional scale width, JPEG/WebP quality 1-100 |
| `--vcodec` / `--acodec` | no | Media only: e.g. `libx264` / `aac` |
| `--yes` | no | `batch` defaults to dry-run; must add to write to disk |

When inputs are missing, ask all at once: "Please provide: 1) source file or
directory path; 2) target format; 3) whether to limit width/lower quality for
images; 4) whether batch (if so, see dry-run first). Defaults: single file
converts directly, batch previews first."

## Pre-flight Checks

```bash
python3 --version                                        # expected >= 3.8
test -f scripts/convert.py && echo SCRIPT_OK             # expected prints SCRIPT_OK
python3 -c "import PIL; print('PIL_OK', PIL.__version__)" 2>/dev/null || echo "PIL missing: pip3 install pillow"
command -v pandoc || echo "pandoc missing: only doc subcommand affected"
command -v ffmpeg || echo "ffmpeg missing: only media subcommand affected"
```

Three external dependencies are **checked on demand**: converting images only
doesn't need pandoc/ffmpeg; script enforces this logic.

## Workflow

### Step 1: Determine Which Pipeline

| Source → Target | Pipeline | Command |
|-----------|------|------|
| `.md` → `.docx` / `.pdf` / `.html` | doc | `doc` |
| `.docx` → `.md` / `.epub` | doc | `doc` |
| `.png` → `.jpg` / `.webp` (with resize) | image | `image` |
| `.mov` → `.mp4` / `.webm` (with transcode) | media | `media` |
| Batch of same-type files in directory | any above | `batch --to <ext>` |

Expected: after determining pipeline, go to corresponding step. Reading key:
**cross-pipeline conversion (e.g. `.mp4`→`.jpg` frame extraction) is out of
scope**.
If it fails: source/target combo not in table (e.g. `.mp4`→`.jpg`) →
cross-pipeline; tell user this tool doesn't do it and give the corresponding
professional command (frame extraction: `ffmpeg -i in.mp4 -frames:v 1 out.jpg`);
wrong output extension → script reports "cannot infer format from extension" with
exit code 3; switch to a supported extension.

### Step 2: Single-File Conversion

```bash
# documents
# python3 scripts/convert.py doc report.md report.docx
# images: scale to 800 width, quality 85
python3 scripts/convert.py image assets/sample.png assets/sample-converted.jpg --width 800 --quality 85   # bundled sample image (offline conversion when PIL available)
# media
# python3 scripts/convert.py media clip.mov clip.mp4 --vcodec libx264 --acodec aac
```

Expected: first prints `$ <actual command executed>`, then on success prints
`OK: <in> <original size/mode> -> <out> <new size> (<bytes>)`.

If it fails: exit code 4 + `pandoc not found` → install per printed command then
rerun (Mac: `brew install pandoc`, Debian/Ubuntu: `sudo apt-get install pandoc`,
Windows: `winget install --id JohnMacFarlane.Pandoc`); exit code 2 + `output path
same as input` → choose a different output name; script refuses self-overwrite.

### Step 3: Batch Conversion (Preview First)

```bash
python3 scripts/convert.py batch assets --to jpg   # bundled sample directory dry run (default no disk write)
```

Expected: line-by-line `[dry-run] (image) a.png -> _converted.jpg/a.jpg`, ending
"no disk changes". Cross-pipeline files are explicitly skipped with reason noted,
e.g. `[skip: cross-pipeline media->image] clip.mp4`.

If it fails: `0 candidate files` → directory has no source files for target
pipeline; check `--to` spelling.

### Step 4: Write to Disk After Confirmation

```bash
python3 scripts/convert.py batch "$TARGET_DIR" --to jpg --yes
```

Expected: prints `OK:` per file, ending "success N, failed M", artifacts land in
`_converted.jpg/`. In batch mode, a single file failure **doesn't interrupt**
the rest; failures show in ending count.

If it fails: `failed` count > 0 → review `[fail]` lines one by one; failures
from missing dependencies say which dependency.

### Step 5: Accept Artifacts

```bash
ls -l "$TARGET_DIR/_converted.jpg/"                    # count should match "success N"
python3 -c "
from PIL import Image; import glob
for f in sorted(glob.glob('$TARGET_DIR/_converted.jpg/*.jpg')):
    im = Image.open(f); print(f, im.width, im.height, im.format)
"
```

Expected: every file opens, size/format matches expectation.
If it fails: `ls` count less than "success N" → some artifacts overwritten by
same name; add `--overwrite` or switch `--outdir` and rerun; PIL can't open a
file → that artifact is corrupt (usually interrupted mid-conversion); delete and
reconvert single-file.

## Dependency and Install Reference

| Dependency | Used For | macOS | Debian/Ubuntu | Windows |
|------|------|-------|---------------|---------|
| pandoc | `doc` | `brew install pandoc` | `sudo apt-get install pandoc` | `winget install --id JohnMacFarlane.Pandoc` |
| Pillow | `image` | `pip3 install pillow` | `pip3 install pillow` | `pip install pillow` |
| ffmpeg | `media` | `brew install ffmpeg` | `sudo apt-get install ffmpeg` | `winget install --id Gyan.FFmpeg` |

Install commands printed by script on missing dependencies match the table above,
auto-selected by current OS.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Exit code 4, `pandoc/ffmpeg not found` | External binary not installed | Install per printed command, confirm with `<tool> --version`, rerun |
| Exit code 4, `image conversion needs Pillow` | Missing Python library | `python3 -m pip install pillow` |
| Exit code 2, `output path same as input` | `<in>` and `<out>` point to same file | Change output filename |
| Exit code 1, `input file not found` | Wrong path | Verify actual path with `ls` |
| Exit code 3, `cannot infer format from extension` | Rare format not registered | Use `pandoc -f <from> -t <to>` explicitly |
| JPEG output errors `cannot write mode RGBA` | Source has alpha channel | Script already converts to RGB; if using library manually, `convert("RGB")` |
| `[skip: cross-pipeline media->image]` | Want frame extraction from video | This tool doesn't; use `ffmpeg -i in.mp4 -frames:v 1 out.jpg` |
| batch all `[skip: target exists]` | Already converted last time | Add `--overwrite`, or specify new `--outdir` |

## Delivery Criteria

**Success definition**: command exit code 0 and prints `OK:`; batch mode "failed
0".

**Artifact naming**: single file uses caller-provided `<out>`; batch mode is
`<original filename minus ext>.<target ext>`.

**Location**: single file writes to specified output path; batch defaults to
`<dir>/_converted<ext>/`, can change with `--outdir`.

**Integrity verification**:

```bash
test -s "$OUT" && echo "non-empty artifact OK"          # reject 0-byte artifacts
python3 -c "
from PIL import Image; im = Image.open('$OUT'); im.verify(); print('image decodable OK')
" 2>/dev/null || true
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" 2>/dev/null   # media duration non-empty
```

## References

- `scripts/convert.py` — run it for four subcommands; `require_binary`/`require_pillow` are dependency gates.
- `references/sources-and-methodology.md` — design rationale for dependency probing, cross-pipeline rejection, and batch fault tolerance.
