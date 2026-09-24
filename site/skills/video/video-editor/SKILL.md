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

## Editing Rhythm and Pacing

Rhythm is the invisible half of editing. Below are the empirical shot-duration ranges that keep viewers engaged by genre; use them to sanity-check any assembled cut.

### Shot Duration by Genre

| Genre | Average Shot Length | Notes |
|---|---|---|
| Talking head / interview | 4-8s | Prefer hard cuts; cut on dialogue pauses |
| Fast-cut shorts (Douyin/TikTok) | 0.5-1.5s | Hook in first 1.5s; cut every 1-2s during energy |
| Vlog / lifestyle | 2-4s | Mix of hard cuts and J/L-cuts |
| Cinematic / short film | 3-6s | Longer holds; match cuts and dissolves |
| Explainer / tutorial | 2-5s | Cutaways to B-roll; let the reader catch up |
| Music video | 0.5-2s | Beat-synced; speed ramps on drops |

### The 3-Second Rule for Shorts

For vertical short-form (Douyin/TikTok/Reels), **if a shot holds longer than 3 seconds without a cut, motion change, or graphic overlay, the viewer will likely scroll away**. Audit the cut: any shot over 3s must either contain internal motion (camera move, action, graphic) or be a deliberate emotional hold.

### Montage Pacing

- Build: shots get slightly shorter as energy rises (4s -> 3s -> 2s -> 1.5s).
- Peak: shortest cuts land on the beat drop.
- Release: hold on a 3-5s shot after the peak to let the breath come back.

### Holding on Emotional Beats

Punchlines, reveals, and reactions need **hold time after the beat**, not before. Cut to the reaction shot and let it sit 0.5-1.5s before the next cut. Cutting immediately on the punchline kills the laugh.

### Cutting on Action vs. on Dialogue

- **Cut on action**: cut in the middle of a movement (hand halfway up, head halfway turned). The viewer's eye follows the motion and misses the cut. Default for B-roll and montage.
- **Cut on dialogue**: cut at a pause between sentences, never mid-word. For talking-head, leave 2-5 frames of silence around the cut so the edit does not sound clipped.

## Audio-Video Sync

### Lip-Sync Verification

After assembly, scrub the first and last 0.5s of every spoken line. If lip motion leads audio by more than ~40ms (1 frame at 24fps), resync: shift the audio track by the offset using `ffmpeg -itsoffset`. A drift of >80ms is perceptible to most viewers.

### Cutting on Dialogue Pauses

Never cut across a spoken word. Find the natural breath / pause between sentences and place the cut there. If no pause exists, use a J-cut (next clip's audio begins 0.3-0.5s before the video cut) to smooth over it.

### Music Beat Mapping

If BPM is known, beat interval = 60 / BPM seconds. For 120 BPM that is 0.5s. Snap cuts (and transition midpoints) to the nearest beat grid line. On-beat cuts feel powerful; off-beat (between beats) feel conversational. Action/energy on the downbeat; dialogue on the off-beat.

### Audio Ducking Under Voice

When voice-over or dialogue plays over background music, lower the music so the voice sits on top:

```bash
# Duck BGM to 0.25 volume under voice, sidechain-style (simple version)
ffmpeg -i combined.mp4 -i bgm.mp3 -filter_complex \
  "[1:a]volume=0.25[bgm];[0:a][bgm]amix=inputs=2:duration=shortest" final.mp4
```

Target: voice at 0dB RMS, BGM at -18 to -24 dB relative. If the music feels louder than the speech, lower BGM further.

### Ambient Sound Continuity Across Cuts

A hard cut that drops ambient noise (room tone) in and out sounds like a jump. Lay 0.5-1.0s of room tone under every cut so the ambience does not discontinuously switch. If source clips have mismatched ambient levels, normalize them first with loudnorm.

## Transition Execution

When `transition-designer` delivers a transition plan, execute it here. The workhorse filter is FFmpeg `xfade` (video) paired with `acrossfade` (audio).

### Cross-Dissolve

```bash
# 0.5s cross-dissolve between clip1 and clip2, offset = duration of clip1 - 0.5
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=4.5[v]; \
   [0:a][1:a]acrossfade=d=0.5[a]" \
  -map "[v]" -map "[a]" out.mp4
```

Offset math: `offset = duration(clip1) - transition_duration`. This is the point in clip1's timeline where the dissolve begins.

### Fade In / Fade Out (opening and closing)

```bash
# Fade in from black over the first 1.0s
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=1.0" out.mp4
# Fade out to black over the last 1.0s (assume total duration T)
ffmpeg -i input.mp4 -vf "fade=t=out:st=$(echo "$T - 1.0" | bc):d=1.0" out.mp4
```

### Wipe (left / right / circle)

```bash
# Wipe right-to-left over 0.4s
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=wiperight:duration=0.4:offset=4.6[v]" out.mp4
```

Common xfade transition names: `fade`, `fadeblack`, `fadewhite`, `wiperight`, `wipeleft`, `wipeup`, `wipedown`, `slideleft`, `slideright`, `circleopen`, `circleclose`, `radial`, `circlecrop`, `diagtl`, `diagtr`, `diagbl`, `diagbr`.

### Chaining Multiple Transitions

For N clips with K transitions, chain offsets. If each clip is 5s and each transition is 0.5s:

- Transition 1 offset = 5 - 0.5 = 4.5
- Transition 2 offset = (5 + 5 - 0.5) - 0.5 = 9.0
- Transition k offset = sum of previous clip lengths - (k-1)*duration - duration

For more than 2 clips, build the filter graph explicitly or use a script to generate it. Test with `--mock` first to verify offsets.

### J-Cut and L-Cut

```bash
# J-cut: next clip's audio starts 0.8s before its video
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "[1:a]adelay=800|800[a2]; \
   [0:a][a2]acrossfade=d=0.8[a]" out.mp4

# L-cut: previous clip's audio continues 1.0s into next video
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "[0:a]apad=pad_dur=1[a1]; \
   [a1][1:a]acrossfade=d=1.0[a]" out.mp4
```

### Motion-Effect Overlay Execution

When `motion-effects-designer` delivers a motion spec, execute overlays with `overlay`, `drawtext`, and `fade`:

```bash
# Animated lower-third text sliding in over 0.3s, holding, then fading out
ffmpeg -i clip.mp4 -vf \
  "drawtext=text='Jane Doe':fontcolor=white:fontsize=36:x=(w-tw)/2:y=h-120:\
   alpha='if(lt(t,0.3),t/0.3,if(lt(t,3.0),1,if(lt(t,3.5),(3.5-t)/0.3,0)))'" out.mp4
```

For particles, light leaks, or grain, overlay a stock loop clip with `blend=screen`:

```bash
ffmpeg -i clip.mp4 -i particles.mp4 -filter_complex \
  "[1:v]scale=1080:1920[pt];[0:v][pt]blend=all_mode=screen:all_opacity=0.6" out.mp4
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
| Audio pop / click at cut | Waveform discontinuity at edit point | Add 20-50ms `acrossfade` or use a J/L-cut to smooth |
| Lip-sync drift >80ms | Audio offset between source clips | Shift audio with `-itsoffset` by the measured offset |
| Cut feels jarring / viewers notice it | No motion match across the cut; same framing | Apply the transition plan from `transition-designer`; add cutaway or J-cut |
| Music and cuts feel off-grid | Cuts not on beat | Re-map cuts to nearest beat grid line (see Audio-Video Sync) |
| BGM drowns out voice | Music too loud under dialogue | Duck BGM to -18 to -24 dB relative (see Audio Ducking) |

## Delivery Standard

- `final.mp4` exists, `ls -l` size > 0, duration matches target (within <= 0.5s).
- Real mode is default; `--mock` only produces a metadata placeholder, not deliverable as the final output.
- Before irreversible writes (overwriting a user's existing same-named final cut), you must confirm with the user.

## References

- `references/ffmpeg-recipes.md` — underlying ffmpeg recipes for stitching / mixing / transitions and manual-tuning examples; consult when you need fine-tuning beyond the script's wrappers.
- FFmpeg xfade filter docs: https://ffmpeg.org/ffmpeg-filters.html#xfade (transition names and offset math)
- FFmpeg drawtext / overlay / blend filter docs for motion graphics execution.

## Chain Handoff

This skill is the **execution** stage of the video production pipeline. It consumes planning artifacts from upstream design skills and produces the final cut.

**Upstream planning skills (call these before editing when a deliberate design is wanted):**

- **transition-designer** — produces the per-boundary transition plan (transition type, duration, beat sync). If the user already has a transition plan, execute it directly with the FFmpeg `xfade` recipes in the Transition Execution section. If no plan exists and the user wants default cuts, proceed without it.
- **motion-effects-designer** — produces the motion spec (animated text, lower thirds, charts, particles, overlays). Execute overlays with `drawtext`, `overlay`, and `blend=screen` per the Motion-Effect Overlay Execution recipe.

**Other upstream inputs:**
- `video-generation` / `image-generation` — source clips and stills to stitch.
- `video-lip-sync` — lip-synced dialogue clips.
- `video-voice-synth` — voice-over audio track.
- `storyboard-designer` — ordered shot list with timings.

**Downstream:**
- `video-subtitles` — captions and subtitles are burned in after the cut is locked; timing should respect the transition plan's beat grid.
- `video-thumbnail` — grabs a still frame from the final cut; avoid choosing a frame mid-transition.

Typical chain: video-script-writer -> storyboard-designer -> (transition-designer + motion-effects-designer) -> video-editor (this skill) -> video-subtitles -> video-thumbnail.
