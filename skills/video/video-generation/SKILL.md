---
name: video-generation
description: >
  Generate short videos from text prompts or reference images through a local
  generation gateway (text-to-video and image-to-video with polling and
  download). Use when the user asks to generate a video / make a short video /
  text-to-video / image-to-video / make a video from this text / animate this
  image / generate a promo video, or wants AI-generated footage. Do NOT use
  for video editing, subtitle burning, screen recording, or downloading
  existing videos from the web.
license: Apache-2.0
compatibility: Requires curl and network access to the generation gateway endpoint.
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: media-generation
  verified-date: "2026-09-24"
---

# Video Generation (Text-to-Video / Image-to-Video)

Drive the local generation gateway with curl: submit a task -> poll until done -> download the result -> hand the file path to the user. No ffmpeg needed, no Python media libraries, no dependencies to install — the gateway handles rendering, you handle orchestration.

## Applicability Decision Table

| Your Situation | Use This Skill? | Notes |
|---|---|---|
| Have a text prompt, want AI-generated footage | yes | core text-to-video use case |
| Have a reference image, want to animate it | yes | image-to-video mode |
| Need to stitch clips together into a final edit | no | go to video-editor |
| Need subtitles or captions burned in | no | go to video-subtitles then video-editor |
| Need a per-scene storyboard with prompts | no | go to storyboard-designer first |
| Need a single still image, not video | no | go to image-generation |

## Domain Tacit Knowledge (What Makes a Good Generated Clip)

**1. One action per clip.** Video models can reliably render a single, simple action in 6 seconds. Complex multi-step actions ("walk in, sit down, open the laptop, start typing") fall apart after the first step. If the scene needs multiple actions, split it into multiple clips and stitch them in editing. Rule of thumb: one verb per clip.

**2. State verbs fail; process verbs work.** "Holding a coffee cup" is a state — the model may just show a static frame. "Lifting a coffee cup to take a sip" is a process — the model animates the motion. Always write the action as a process verb (walk, turn, reach, lift, smile), not a state verb (is, holds, stands, sits).

**3. Camera moves must be simple.** One camera move per clip. "Slow push-in" or "static wide shot" works. "Pan right then zoom in then tilt down" produces camera chaos. If the story needs multiple camera angles, generate separate clips and cut between them.

**4. Image-to-video preserves the first frame; text-to-video starts from nothing.** With a reference image, the model animates from that exact starting frame — character likeness, composition, and lighting are locked. Without a reference image, the model invents everything, so character consistency drifts between clips. For talking-character or multi-scene videos, always use image-to-video with a locked reference frame.

**5. 6 seconds is the sweet spot; 10 seconds drifts.** Most current generation models produce 6-second clips with good quality. 10-second clips have more motion drift, warping, and composition changes. For longer content, generate multiple 6-second clips and stitch them — better quality and easier to edit.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| topic / brief | yes | — | What the video is about; the user's own words or a one-line brief |
| aspect_ratio | no | `16:9` | `16:9` landscape, `9:16` vertical, `1:1` square |
| duration | no | `6` | seconds; `6` or `10` |
| size | no | `720P` | `720P` or `1080P` |
| reference_image_url | no | — | Providing it switches to image-to-video mode |

When a required input is missing, ask everything at once; fill in the rest from defaults:

> Please provide: ① video topic or brief. Optionally tell me: ② aspect ratio (default 16:9), ③ duration
> (default 6 seconds, optional 10), ④ quality (default 720P), ⑤ reference image URL (image-to-video if provided).

## Pre-flight Checks

Run first — first resolve the gateway base URL (same command as workflow Step 1), then probe liveness:

```bash
VIDEO_GATEWAY_BASE="${VIDEO_GATEWAY_BASE:-http://127.0.0.1:30080}"
curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$VIDEO_GATEWAY_BASE/api/video/status?task_id=0"
```

Expected: any HTTP code printed (gateway reachable). If it fails: curl exit code non-0 (connection failure) -> tell the user `$VIDEO_GATEWAY_BASE` is unreachable, ask them to start the gateway, STOP; HTTP 404 -> route name doesn't match the deployment; verify the endpoint against the gateway docs before continuing. Don't fall back to local rendering tools.

## Workflow

### Step 1: Confirm the Gateway Address

```bash
VIDEO_GATEWAY_BASE="${VIDEO_GATEWAY_BASE:-http://127.0.0.1:30080}"
echo "$VIDEO_GATEWAY_BASE"
```

Expected: a URL printed, matching the address that passed the pre-flight probe.
If it fails: it expands to empty -> shell anomaly — stop. The URL differs from pre-flight -> trust the value that passed pre-flight; don't switch addresses mid-run.

### Step 2: Write the Prompt

Write one descriptive paragraph following the six-slot structure: `[subject] + [action] + [camera] + [lighting] + [style] + [duration/aspect]`.

Rules (per tacit knowledge above):
- Single process verb, not a state ("walks slowly" not "is standing")
- One camera move, not multiple ("slow push-in" not "pan then zoom")
- Concrete nouns, not adjectives ("rain-soaked neon street" not "cool urban vibe")
- Duration and aspect ratio explicit ("6 seconds, 9:16 vertical")

If the brief is thin or the user cares about quality, read `references/prompt-recipes.md` first for strong/weak examples. Never send a bare noun phrase as a prompt.

### Step 3: Submit the Generation Task

Text-to-video:

```bash
curl -s -X POST "$VIDEO_GATEWAY_BASE/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"<STEP-2 PROMPT>","params":{"aspect_ratio":"16:9","duration":"6","size":"720P"}}'
```

For image-to-video, append `"images":["<url>"]` inside `params`.

Expected: JSON returned containing the task ID (`task_id`); extract and remember it. If it fails: HTTP error or HTML returned instead of JSON -> per the failure table, re-check Step 1's base value and rerun once as-is; if it fails again, report the status line to the user and stop.

### Step 4: Poll Until Terminal State

```bash
curl -s "$VIDEO_GATEWAY_BASE/api/video/status?task_id=<TASK_ID>"
```

Poll every 10 seconds. Success condition: `is_final == true` and `state == "success"`; then `result_url` is the download address. `is_final == true` but any other state means failure — see the failure table below. Polling no more than 60 times (10 minutes); on timeout you must give a clear report.
If it fails: `state == "failed"` -> rewrite per the prompt recipe and resubmit once; still `pending` after 10 minutes -> report `task_id` and suggest resubmitting; success but missing `result_url` -> flag the endpoint "verify before use" and report the raw JSON to maintainers.

### Step 5: Download & Deliver

```bash
curl -s -L -o "video_$(date +%Y%m%d_%H%M%S).mp4" "<RESULT_URL>"
ls -lh video_*.mp4
```

Expected: a non-empty .mp4 appears in the working directory. Confirm file size > 0 before declaring success. Report the absolute path to the user.
If it fails: file is 0 bytes -> `result_url` expired; re-poll for a fresh URL and download again; still 0 -> report honestly as incomplete, attaching the raw response.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| curl can't connect (pre-flight) | Gateway not started | Ask the user to start the gateway; stop |
| generate returns non-JSON | Wrong base URL or a proxy | Re-check Step 1's value, retry once, then report |
| status stays `pending` over 10 minutes | Queue stuck | Report task_id, suggest resubmitting |
| `state == "failed"` | Prompt rejected (usually too short or too vague) | Rewrite with six-slot structure, resubmit once |
| Video has no motion (static frame) | State verb instead of process verb | Change to a process verb (walk/turn/reach), resubmit |
| Camera moves erratically | Multiple camera moves in one prompt | Keep one camera move per clip, resubmit |
| Downloaded file is 0 bytes | URL expired / signature invalid | Re-poll for a fresh result_url, download again |
| Success but missing `result_url` | API structure changed | Flag the endpoint "verify before use"; report raw JSON to maintainers |

## Quality Checklist

- [ ] Gateway reachable and responding
- [ ] Prompt follows six-slot structure (subject + action + camera + lighting + style + duration)
- [ ] Single process verb per clip (not state verbs)
- [ ] Single camera move per clip
- [ ] Duration and aspect ratio explicitly stated
- [ ] Output file exists and is non-empty
- [ ] Aspect ratio matches the requested format

## Delivery Standard

Success = a local `.mp4`, size > 0, named `video_YYYYMMDD_HHMMSS.mp4` (timestamped), with the path and the duration/ratio used reported to the user. Anything else counts as incomplete — say so plainly, and point to the matching row in the failure table above.

## References

- `references/prompt-recipes.md` — prompt formulas and strong/weak examples; read before writing any prompt
