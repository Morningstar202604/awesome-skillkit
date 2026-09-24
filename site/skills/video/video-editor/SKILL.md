---
name: video-editor
description: "Assemble video clips with transitions, mix audio tracks, add effects, and produce final video. Supports FFmpeg-based real editing and mock mode. Use after lip-sync clips are ready, before subtitle/thumbnail steps. Use when the user asks to edit a video / stitch clips / assemble a final cut / add background music / composite video / add transitions / audio mix / cut video / stitch clips. Do NOT use for generating footage from text (use video-generation)."
license: Apache-2.0
compatibility: Requires FFmpeg for real editing; mock mode works without. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Editor / Assembly

Combine clips, mix audio, add transitions, and produce a publishable final cut. Default is **real mode**: call `scripts/editor.py` (underpinned by ffmpeg) to actually produce a file; `--mock` or `SKILLKIT_MOCK=1` only outputs metadata, intended solely for downstream integration testing, not for delivery.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| clips | yes | List of clip paths to stitch (order = stitching order) |
| output | yes | Final-cut output path, e.g. `final.mp4` |
| audio | no | Background music / voice-over files, multiple allowed |
| transitions | no | Transition type between clips: `fade` / `cut` / `slide`, default `cut` |
| script | no | Whole-chain JSON (batch mode, incl. clips/audio descriptions) |

When any required input is missing, ask everything at once:

> Please provide: ① clip file list (paths); ② final-cut output path. Optional: ③ background music, ④ transition type (default cut), ⑤ whole-chain script JSON.

## Pre-flight Checks

```bash
command -v ffmpeg >/dev/null && echo "ffmpeg ok" || echo "ffmpeg MISSING"
for f in clip1.mp4 clip2.mp4; do test -f "$f" && echo "found $f" || echo "MISSING $f"; done
```

Probes: ① `ffmpeg` installed (required in real mode); ② every `clips` file exists; ③ the directory containing `output` is writable.
Any failure -> give a fix and STOP: ffmpeg missing prints install guidance (`sudo apt install -y ffmpeg` / `brew install ffmpeg`, verify with `ffmpeg -version`); missing files report the specific filename; do not silently fall back to placeholder files.

## Workflow

### Step 1: Collect and Validate Clips

Action: list `clips`, confirm each file exists and decodes (`ffprobe -v error "<clip>"` exit code 0).
Expected: the clip list is non-empty, and every file passes `ffprobe`.
If it fails: file missing / decode failure -> report the filename and STOP; don't skip the clip and keep stitching.

### Step 2: Run the Editing Script (Real Mode)

Action:

```bash
python3 scripts/editor.py --clips clip1.mp4 clip2.mp4 --audio bgm.mp3 --output final.mp4 --transitions fade cut --mock   # --mock is for integration testing only (placeholder artifact, not deliverable); remove --mock for real output (needs ffmpeg)
```

Expected: exit code 0; `final.mp4` exists and `ls -l final.mp4` shows size > 0.
If it fails: non-0 exit -> read stderr; `ffmpeg: command not found` see pre-flight to reinstall; transition type unsupported -> downgrade to `cut` and rerun.

### Step 3: Batch Chain (Optional)

Action:

```bash
python3 scripts/editor.py --script script.json --clips-dir clips/ --audio-dir tts/ --output final.mp4
```

Expected: exit code 0, assembling all clips and audio per `script.json`.
If it fails: missing JSON field -> read stderr to locate, fill in the `clips`/`audio` keys and rerun.

### Step 4: Validate the Final Cut

Action:

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 final.mp4
```

Expected: prints the final-cut duration (seconds), within <= 0.5s of the script's target.
If it fails: duration noticeably short -> check whether `--clips` missed a clip, add it back and restitch.

## Underlying FFmpeg Recipes

The script already wraps common operations; when you need manual tuning, the recipes below match `references/ffmpeg-recipes.md`:

```bash
# Concatenate (generate clips.txt: one file '<path>' per line)
ffmpeg -f concat -safe 0 -i clips.txt -c copy combined.mp4

# Mix BGM (duck to 0.3 volume, then mix with the original audio)
ffmpeg -i combined.mp4 -i bgm.mp3 -filter_complex \
  "[1:a]volume=0.3[bgm];[0:a][bgm]amix=inputs=2" final.mp4

# Crossfade between clips
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "xfade=transition=fade:duration=0.5" output.mp4
```

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--clips` | file list | Order = stitching order |
| `--audio` | file list | Mixed with picture; see recipes for volume |
| `--transitions` | fade/cut/slide | Between clips, default cut |
| `--script` | JSON file | Whole-chain batch mode (overrides individual params) |
| `--clips-dir` / `--audio-dir` | directory | Clips/audio directories for batch mode, default `clips`/`tts` |
| `--output` | path | Final-cut path, default `final_video.mp4` |
| `--mock` | flag | Only outputs metadata, no file generation (downstream integration) |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| `ffmpeg: command not found` | Not installed | Install ffmpeg and rerun (see pre-flight) |
| Script exits non-0 | Clip missing / decode failure | Read stderr to locate the specific file |
| Final cut too short | A clip was omitted from the stitch | Check the `--clips` list and complete it |
| Final cut silent | No `--audio` passed | Add `--audio bgm.mp3` and re-mix |
| Overwriting an existing file | User has a same-named final cut | Confirm with the user before overwriting (irreversible write) |

## Delivery Standard

- `final.mp4` exists, `ls -l` size > 0, duration matches target (within <= 0.5s).
- Real mode is default; `--mock` only produces a metadata placeholder, not deliverable as the final output.
- Before irreversible writes (overwriting a user's existing same-named final cut), you must confirm with the user.

## References

- `references/ffmpeg-recipes.md` — underlying ffmpeg recipes for stitching / mixing / transitions and manual-tuning examples; consult when you need fine-tuning beyond the script's wrappers.
