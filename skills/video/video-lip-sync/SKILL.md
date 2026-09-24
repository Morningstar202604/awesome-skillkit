---
name: video-lip-sync
description: "Synchronize character mouth movements with TTS audio. Takes a face image + audio file, generates lip-synced video. Gateway-based with mock fallback. Use when the user asks for lip sync / mouth-sync / digital human talking / make a photo talk / talking head video / make the avatar talk. Do NOT use for voice synthesis (see video-voice-synth), subtitle generation (see video-subtitles), or generic video editing."
license: Apache-2.0
compatibility: Requires local lip-sync gateway at 127.0.0.1:30081 or mock mode. No API keys required.
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-24"
---

# Video Lip Sync

Sync a character's front-facing image with TTS dry audio into a lip-sync video. Default is **real mode**: call `scripts/lip_sync.py` against a user-provided lip-sync gateway to actually produce video; `--mock` or `SKILLKIT_MOCK=1` only outputs metadata, intended solely for downstream integration testing, not for delivery.

## Applicability Decision Table

| Your Situation | Use This Skill? | Notes |
|---|---|---|
| Have a character image + TTS audio, need a talking-head clip | yes | core use case |
| Need batch lip-sync for all scenes in a script | yes | use `--script` batch mode |
| Only need voice-over audio (no face) | no | go to video-voice-synth |
| Need to edit/stitch lip-sync clips into a final video | no | go to video-editor |
| Real person's face + audio (deepfake risk) | refuse | portrait rights / platform policy; use AI-generated character images only |

## Domain Tacit Knowledge (What Separates Good Lip Sync From Uncanny Valley)

**1. Input audio quality is 80% of the result.** Lip-sync models track phonemes from the audio waveform. Background music, reverb, and muffled audio confuse the phoneme tracker, producing rubber-mouth or frozen-lip output. The single most important pre-flight check: the audio must be dry, clean TTS output with no BGM, no noise reduction artifacts, and no clipping. If the TTS export has reverb or background music, re-export from the TTS tool with those effects turned off before running lip sync.

**2. The reference image must be a straight-on front face.** Lip-sync models assume the face is roughly parallel to the camera. A 3/4 side profile, a tilted head, or a mouth obscured by a hand/prop produces warped or invisible lip movement. The ideal reference: front-facing, neutral expression, mouth slightly closed, good even lighting on the face, no facial hair or glasses that obscure the mouth region.

**3. Mouth-box tuning is a precision adjustment, not a guess.** The default 40x30 pixel box works for most 512x512 character images, but every face is different. If the mouth barely moves: first confirm the audio is clean (tacit knowledge 1), then expand the box (e.g. `--mouth-width 50 --mouth-height 35`). If the lower face distorts or the jaw warps: shrink the box. Iterate on one short line (1-2 seconds) before batch-generating all scenes.

**4. Long clips drift; split at punctuation.** Most lip-sync models degrade after 8-10 seconds: lip sync desynchronizes, the face warps, or the head drifts. For scenes longer than 8 seconds, split the audio at a natural pause (comma, period, breath), generate two clips, and stitch them in editing. This is the #1 cause of "the second half of the video looks wrong" complaints.

**5. Consistency = same face image every time.** For multi-scene talking-character videos, use the exact same reference face image for every scene. Switching to a different "good angle" mid-series causes visible face drift between clips — viewers notice immediately. Lock the reference image in the character card and reuse it verbatim across all lip-sync runs.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| face_image | yes | Path to the character's front-facing image (use the same one as voice-synth to prevent face drift) |
| audio | yes (single) or `script` (batch) | TTS dry audio, no BGM / no reverb |
| output | no | Output path, default `lipsync_<face>.mp4` |
| mouth_width / mouth_height | no | Mouth region box size (pixels), default `40` / `30` |
| gateway_url | no | Gateway root address, overrides `GATEWAY_BASE_URL` |

When any required input is missing, ask everything at once:

> Please provide: ① character front-facing image path; ② dry-audio file path (or batch script JSON). Optional: ③ output path, ④ mouth box size (default 40x30).

## Pre-flight Checks

```bash
GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-http://127.0.0.1:30081}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$GATEWAY_BASE_URL/v1/lipsync"
```

Probes: ① gateway reachable (required in real mode; skipped in mock mode); ② `face_image` and `audio` files exist; ③ `python3` available.
Expected: in real mode an HTTP code is printed (gateway online). Any failure -> fix and STOP: gateway unreachable prompts to start the service or set `GATEWAY_BASE_URL`; missing files report the specific filename; never silently return fake results.

Additional quality pre-checks (do manually):
- Is the audio dry? (no BGM, no reverb, no background noise)
- Is the face image front-facing? (not 3/4 side, not tilted)
- Is the mouth visible? (not covered by hand, prop, or facial hair)

## Workflow

### Step 1: Test With One Short Clip

Start with one short test line (1-3 seconds) to verify quality before batch processing.

```bash
python3 scripts/lip_sync.py --face character.png --audio test_line.wav --output lipsync_test.mp4
```

Expected: exit code 0; `lipsync_test.mp4` exists and `ls -l` size > 0; duration ~= audio duration.
If it fails: gateway 4xx/5xx -> check `references/gateway-setup.md` for endpoint fields; mouth barely moves -> swap in clean dry audio (no BGM) and reroll; warped lip output -> tune `--mouth-width/--mouth-height` and retry.

Review the test clip: does the mouth movement match the speech rhythm? Are the lips visible and not warped? If the test passes, proceed to Step 2. If not, fix the issue (audio quality, mouth box, image angle) before generating more clips.

### Step 2: Batch Sync

```bash
python3 scripts/lip_sync.py --face character.png --script script.json --audio-dir tts/ --output lipsync.mp4
```

Expected: one lip-sync video per scene, exit code 0.
If it fails: a scene's audio is missing -> report which one; add the corresponding file in `audio-dir` and rerun.

For scenes longer than 8 seconds, split the audio at a natural pause and generate two clips per scene, then note in the delivery that these need stitching in video-editor.

### Step 3: Quality Review

For each generated clip, check:
- Lip movement matches the audio rhythm (not frozen, not rubbery)
- The face is not warped or distorted
- Duration matches the audio duration within 0.5s
- No artifacts at the frame edges

### Step 4: Mock Integration (Optional, Downstream Wiring Only)

Action: append `--mock` (or `SKILLKIT_MOCK=1`).
Expected: only metadata JSON output, no video file generated.
If it fails: non-mock but gateway down -> non-0 exit; then either start the gateway or explicitly use `--mock`.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--face` | path | Required, character front-facing image |
| `--audio` | path | Single audio (either this or `--script`) |
| `--script` | JSON | Batch-mode script |
| `--audio-dir` | directory | Batch audio directory, default `.` |
| `--output` | path | Output video path |
| `--mouth-width` / `--mouth-height` | int | Mouth box size, default 40 / 30 |
| `--gateway-url` | URL | Overrides `GATEWAY_BASE_URL` and env vars |
| `--mock` | flag | Silent placeholder (metadata only) |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| Gateway unreachable | Service not started | Start the gateway / set `GATEWAY_BASE_URL`, or explicitly use `--mock` |
| Mouth barely moves | Audio has BGM / is muffled | Swap in clean dry audio, retry with punctuation breaks |
| Mouth box misaligned | Bad mouth dimensions | Tune `--mouth-width/--mouth-height`; iterate on a 1-2s test line first |
| Lip sync drifts in second half | Clip too long (>8s) | Split at a natural pause, generate two clips, stitch in editing |
| Face warps or distorts | Reference image angle wrong | Use a front-facing, neutral-expression image; no tilted heads or side profiles |
| Endpoint field mismatch | Deployment differs from default | Check `references/gateway-setup.md`; mark endpoint path/fields `VERIFY BEFORE USE` |
| Overwriting an existing file | User has a same-named output | Confirm with the user before overwriting (irreversible write) |
| All clips have different faces | Different reference images used | Lock one reference image; reuse verbatim across all scenes |

## Quality Checklist

- [ ] Gateway reachable and responding (real mode only)
- [ ] Face image is front-facing, mouth visible, good lighting
- [ ] Audio is dry (no BGM, no reverb, clean TTS)
- [ ] Test clip (1-3s) passes quality review before batch
- [ ] All scene clips generated; each duration matches its audio
- [ ] No obvious lip drift or face warping
- [ ] Same reference image used for all scenes
- [ ] Long scenes (>8s) split at natural pauses
- [ ] Mock mode not used for final delivery

## Delivery Standard

- Per-scene `lipsync_*.mp4` exists, `ls -l` size > 0, duration matches the corresponding audio.
- Real mode is default; `--mock` only produces a placeholder, not deliverable as the final output.
- Use the same character image as voice-synth, keeping lip-sync and voice consistent and preventing face drift.
- All clips pass the quality checklist above.

## References

- `references/gateway-setup.md` — lip-sync gateway deployment, endpoint paths, and field-name verification (deployments vary widely; check against the doc before running).
