---
name: video-lip-sync
description: "Synchronize character mouth movements with TTS audio. Takes a face image + audio file, generates lip-synced video. Gateway-based with mock fallback. Use when the user asks for lip sync / mouth-sync / digital human talking / make a photo talk / talking head video / make the avatar talk. Do NOT use for voice synthesis (see video-voice-synth), subtitle generation (see video-subtitles), or generic video editing."
license: Apache-2.0
compatibility: Requires local lip-sync gateway at 127.0.0.1:30081 or mock mode. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Lip Sync

Sync a character's front-facing image with TTS dry audio into a lip-sync video. Default is **real mode**: call `scripts/lip_sync.py` against a user-provided lip-sync gateway to actually produce video; `--mock` or `SKILLKIT_MOCK=1` only outputs metadata, intended solely for downstream integration testing, not for delivery.

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

## Workflow

### Step 1: Single Clip Lip-Sync (Real Mode)

Action:

```bash
python3 scripts/lip_sync.py --face character.png --audio scene_1.wav --output lipsync_scene_1.mp4
```

Expected: exit code 0; `lipsync_scene_1.mp4` exists and `ls -l` size > 0; duration ~= audio duration.
If it fails: gateway 4xx/5xx -> check `references/gateway-setup.md` for endpoint fields; mouth barely moves -> swap in clean dry audio (no BGM) and reroll; warped lip output -> tune `--mouth-width/--mouth-height` and retry.

### Step 2: Batch Sync

Action:

```bash
python3 scripts/lip_sync.py --face character.png --script script.json --audio-dir tts/ --output lipsync.mp4
```

Expected: one lip-sync video per scene, exit code 0.
If it fails: a scene's audio is missing -> report which one; add the corresponding file in `audio-dir` and rerun.

### Step 3: Mock Integration (Optional, Downstream Wiring Only)

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
| Mouth box misaligned | Bad mouth dimensions | Tune `--mouth-width/--mouth-height` |
| Endpoint field mismatch | Deployment differs from default | Check `references/gateway-setup.md`; mark endpoint path/fields `VERIFY BEFORE USE` |
| Overwriting an existing file | User has a same-named output | Confirm with the user before overwriting (irreversible write) |

## Delivery Standard

- Per-scene `lipsync_*.mp4` exists, `ls -l` size > 0, duration matches the corresponding audio.
- Real mode is default; `--mock` only produces a placeholder, not deliverable as the final output.
- Use the same character image as voice-synth, keeping lip-sync and voice consistent and preventing face drift.

## References

- `references/gateway-setup.md` — lip-sync gateway deployment, endpoint paths, and field-name verification (deployments vary widely; check against the doc before running).
