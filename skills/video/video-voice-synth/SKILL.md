---
name: video-voice-synth
description: "Text-to-speech for video production via scripts/voice_synth.py: single-line and batch synthesis against a local TTS gateway, per-scene WAV files with the scene_{id}.wav naming contract, six built-in voices (baby/adult/mascot/narrator), --mock silent placeholders for downstream wiring. Use when the script is ready and audio is needed before lip-sync, or when the user asks to voice-over / synthesize speech / text-to-speech / TTS / give the video a voice / text to speech / generate voiceover / synthesize narration. Do NOT use for cloning a real person's voice without documented consent."
license: Apache-2.0
compatibility: Requires the local TTS gateway (default 127.0.0.1:30081) or --mock mode; the script itself needs Python 3.8+ only. No API keys required (gateway auth optional via GATEWAY_API_KEY env).
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Video Voice Synthesis (TTS Voice-over)

Turn script dialogue into audio files. Everything runs through this directory's `scripts/voice_synth.py`: default real mode calls the TTS gateway to actually produce audio; if the gateway is unreachable it prints troubleshooting guidance and exits non-0, never silently returns fake audio; `--mock` only produces silent placeholders for downstream wiring, not deliverable.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| mode | yes | single line (needs text) / batch (needs script JSON) |
| text | single required | Dialogue to synthesize |
| voice | no | default `baby_f01`; see the voice catalog below for all values |
| speed / pitch | no | Defaults to the selected voice's built-in values (see catalog table) |
| script | batch required | Script JSON (from video-script-writer), with `tts_config` and `scenes[].dialogue` |
| audio_dir | batch no | Scene-audio output directory, default current directory |
| output | no | Single-line output path; default `tts_<timestamp>.wav` |

When inputs are missing, ask everything at once: "Please provide: ① dialogue text (or script JSON path) ② voice
(default baby_f01). Optional: speed, output path."

## Pre-flight Checks

- Gateway liveness:
  `curl -sS -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:30081/`
  printing any HTTP code (2xx/401/403/404 all count as alive) passes; connection failure -> have the user
  start the gateway or `export GATEWAY_BASE_URL=http://<host>:<port>` (no trailing slash), STOP.
  Deployment details see [references/gateway-setup.md](references/gateway-setup.md).
- Batch mode: does `test -f <script.json>` pass? If not -> ask the user for the script file, STOP.
- Only for downstream wiring, add `--mock` (or `SKILLKIT_MOCK=1`): the artifact is a silent WAV placeholder,
  **not deliverable**.

## Voice Catalog (Voice x Built-in Parameters)

| Voice ID | Timbre Description | pitch | speed | Best For |
|----------|---------|-------|-------|---------|
| baby_f01 | High-pitched child voice, fast | 5 | 1.3 | Baby podcasts, cute characters |
| baby_f02 | Slightly lower baby voice, slow | 4 | 1.0 | Baby education |
| adult_m01 | Male narrator, steady | 0 | 1.0 | Tutorials, vlogs |
| adult_f01 | Female narrator, warm | 1 | 1.0 | Tutorials, reviews |
| mascot_01 | Enthusiastic, slightly robotic | 2 | 1.1 | Mascot/animated characters |
| narrator_01 | Neutral, clear | 0 | 0.9 | Explainer videos |

(Explicit `--speed`/`--pitch` overrides built-in values; for voice tuning see
[references/voice-config.md](references/voice-config.md).)

## Workflow

### Step 1: Prepare Inputs

Single line: confirm text is non-empty (empty text exits 3). Batch: confirm the script JSON has
`scenes[].dialogue` and `tts_config` (`voice_style`/`speed`); if no `tts_config` -> run on baby_f01 defaults
and tell the user.
Expected: text or JSON in place, voice selected.
If it fails: all dialogues empty -> batch yields 0 results; first go back to the video-script skill to add dialogue.

### Step 2: Single-Line Synthesis

```bash
python3 scripts/voice_synth.py --text "Guess how much I paid for this?" \
  --voice baby_f01 --output tts_test.wav
```

Expected: exit code 0, stdout prints JSON containing `audio_path`, `voice_used`, `speed`,
`pitch`, `bytes` (`mock:false`), and the wav is non-empty.
If it fails: exit 4 -> troubleshoot the gateway per the failure table; run one shortest line first to verify before batching.

### Step 3: Batch Synthesis (Per Scene)

```bash
python3 scripts/voice_synth.py --script script.json --audio-dir audio/
```

Expected: exit code 0, `audio/` contains `scene_<id>.wav` (one file per scene with dialogue),
and stdout JSON has `all_generated == true`. **Naming contract**: `scene_<id>.wav`
is the convention downstream `video-lip-sync --audio-dir` and `video-editor --audio-dir` expect; don't rename it.
If it fails: a scene errors -> locate that `scene_id` in the result JSON's `results[]` and rerun just that line;
`all_generated == false` -> some scene produced nothing; fill each in one by one.

### Step 4: Validate & Deliver

```bash
ls -lh audio/scene_*.wav
```

Expected: all files present and non-empty; each audio's duration roughly matches the script scene's
`duration_sec` (far off -> tune `--speed` and re-synthesize that line). Report the directory and file list to the user.
If it fails: files missing -> rerun the missing scenes per Step 3's result JSON.

## Gateway Protocol (Real Mode)

Gateway address resolution order: `--gateway-url` > env var `GATEWAY_BASE_URL` > default
`http://127.0.0.1:30081` (repo example value; follow the actual deployment).

```text
POST /v1/tts
{"text": "...", "voice": "baby_f01", "speed": 1.3, "pitch": 5, "format": "wav"}
Response: audio binary
```

Auth: when the `GATEWAY_API_KEY` env var is set, it automatically sends an `Authorization: Bearer` header
(credentials only via env vars, never on the command line). Timeout is controlled by `GATEWAY_TIMEOUT` (seconds,
default 30). Endpoint paths and field names follow your actual deployment (VERIFY BEFORE USE).

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------|------|------|
| exit 3: text to synthesize is empty | text is only spaces / omitted | Add text and rerun |
| exit 3: script file missing | Wrong `--script` path | `test -f` to verify the path |
| exit 4: can't reach the gateway | Gateway not started or wrong address | Troubleshoot per the pre-flight probe; confirm `GATEWAY_BASE_URL` has no trailing slash |
| exit 4: gateway returns HTTP 4xx/5xx | Auth / rate limit / service error | Auth via the `GATEWAY_API_KEY` env var; retry 429 later; raise `GATEWAY_TIMEOUT` |
| exit 4: gateway returns empty audio | Server-side error | Retry once; still empty -> report gateway logs to maintainers |
| Audio duration doesn't match the scene | Speed mismatch | Tune `--speed` and re-synthesize just that scene |
| Got a silent wav | Misused `--mock`/SKILLKIT_MOCK=1 | Mock placeholder isn't deliverable; remove mock and rerun real mode |

## Delivery Standard

- Success = real-mode wav output: single line gives the absolute path; batch gives the full set of
  `scene_<id>.wav` (`all_generated == true`), durations matching scene timing, directory list reported.
- Voice / speed / pitch values used are noted in the report (reproducible).
- The mock artifact is not a deliverable — receiving mock JSON counts as incomplete.

## References

- [references/voice-config.md](references/voice-config.md) — voice parameters and pronunciation tuning; read after selecting a voice, before batch synthesis
- [references/gateway-setup.md](references/gateway-setup.md) — local TTS gateway deployment; read when pre-flight checks fail
