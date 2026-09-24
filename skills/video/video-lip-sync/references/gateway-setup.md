# Lip Sync Gateway Integration (video-lip-sync)

This skill uses a "**bring-your-own-gateway**" model: **the repo does not provide, and does not embed,
any vendor endpoint**. You must deploy or designate a lip-sync service yourself and tell the script about it.

> **Endpoints depend on your actual deployment and must be confirmed before running.** The
> `127.0.0.1:30081`, path `/v1/lipsync`, and field name `mouth_width` appearing in this document are
> all **repo example defaults** (from the initial constants in this skill's scripts), not any vendor's
> public API promise. **VERIFY BEFORE USE**: override these values with your own service docs or `curl`
> probe results before executing—see Section 3.

## Table of Contents

0. Integration model and upfront disclaimers / 1. Environment variable conventions / 2. Request and response conventions / 3. Three-step connectivity probe
4. Failure handling table / 5. Async tasks and queueing / 6. Mock mode boundaries / 7. Security red lines

## 0. Integration model and upfront disclaimers

| Item | Notes |
|---|---|
| Who provides the endpoint | The user. The repo does not build in, recommend, or guarantee any third-party address |
| Credential source | Environment variables only; forbidden from being written into SKILL.md, scripts, or Git |
| Default behavior | The script defaults to **real mode**; if the gateway is unreachable it errors out (non-zero), it does not silently fabricate |
| Fallback | Only `--mock` or `SKILLKIT_MOCK=1` uses fake data, and the output carries `"mock": true` |

First self-check step (run before any troubleshooting):

```bash
echo "BASE=${GATEWAY_BASE_URL:-<not set>}  TIMEOUT=${GATEWAY_TIMEOUT:-120}"
[ -n "$GATEWAY_API_KEY" ] && echo "KEY=set (length ${#GATEWAY_API_KEY})" || echo "KEY=not set"
```

Expected: BASE is your gateway root address (e.g. `http://127.0.0.1:30081`), and KEY has at least a
value. If BASE is `<not set>`, set the environment variables per Section 1 first—don't fudge with the
script's defaults.

## 1. Environment variable conventions

The names below are **convention examples for this repo**, not industry standards; if your gateway
requires different names (e.g. `LIPSYNC_ENDPOINT`), defer to your deployment and only change the
variable name the script reads, in the same place.

| Variable | Example value | Required | Notes |
|---|---|---|---|
| `GATEWAY_BASE_URL` | `http://127.0.0.1:30081` | Yes | Gateway root address, **no trailing slash**, no path |
| `GATEWAY_API_KEY` | (your key) | Depends on gateway | Passed only via environment variable; the script sends it in the `Authorization` header |
| `GATEWAY_TIMEOUT` | `120` | No | Per-request timeout in seconds; lip rendering is usually slower than TTS, so default generously |

How to set (effective for the current shell, not written to disk):

```bash
export GATEWAY_BASE_URL="http://127.0.0.1:30081"   # ← change to your actual address
export GATEWAY_API_KEY="..."
export GATEWAY_TIMEOUT=120
```

Before writing into `~/.zshrc` / `~/.bashrc`, first confirm the machine is not shared by multiple people.

## 2. Request and response conventions

**VERIFY BEFORE USE**: below is the request body this skill's scripts currently send; field names
must match your deployed service. How to verify: check the OpenAPI / README of the service you use,
or `curl "$GATEWAY_BASE_URL/openapi.json"` against the gateway root (it returns the API definition if present).

```
POST {GATEWAY_BASE_URL}/v1/lipsync
Content-Type: application/json
Authorization: Bearer ${GATEWAY_API_KEY}     # omit if the gateway needs no auth

{
  "face_image": "character.png",   # relative path; some implementations require base64 or an upload URL
  "audio_path": "scene_1.wav",
  "mouth_width": 40,
  "mouth_height": 30
}
```

Success criteria (all three must hold):

1. HTTP status `2xx`;
2. `Content-Type` is a video type (e.g. `video/mp4`);
3. After saving, `ffprobe -v error -show_entries format=duration -of default=nw=1 out.mp4` yields a
   duration **approximately equal to** the input audio duration (error ≤ 0.3s).

Criterion 3 is the easiest to miss: a 200 returned but the duration doesn't match will throw off all
later concatenation—always validate.

## 3. Three-step connectivity probe

Execute in order; **if any step fails, stop there and fix it**—don't jump to the next step.

```bash
# Step 1: is the port reachable (independent of any business path)?
curl -sS -m 5 -o /dev/null -w "HTTP=%{http_code} connect=%{time_connect}s\n" "$GATEWAY_BASE_URL/"
# Expected: HTTP is any of 200/401/403/404 (means the service is running);
# Failure signatures: curl: (7) Failed to connect = service not started or wrong address → check process and port
#                     curl: (28) Operation timed out = blocked by firewall/security group → check whether the listen address is 127.0.0.1 or 0.0.0.0

# Step 2: health-check path (path names depend on your service; common ones are /health /healthz /v1/health)
for p in /health /healthz /v1/health; do
  printf "%-12s " "$p"; curl -sS -m 5 -o /dev/null -w "%{http_code}\n" "$GATEWAY_BASE_URL$p"
done
# Expected: at least one returns 200. All 404 = wrong path names, check your service docs

# Step 3: real liveness check (use the shortest audio, confirm auth and the render pipeline both work)
curl -sS -m "$GATEWAY_TIMEOUT" -o probe.mp4 -w "HTTP=%{http_code} total=%{time_total}s\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
  -d '{"face_image":"character.png","audio_path":"scene_1.wav","mouth_width":40,"mouth_height":30}' \
  "$GATEWAY_BASE_URL/v1/lipsync"
# Expected: HTTP=200 and probe.mp4 is non-empty (ls -l probe.mp4 shows > 0 bytes)
```

If `ls -l probe.mp4` is 0 bytes, treat it as failure even if HTTP is 200.

## 4. Failure handling table

| Symptom | Cause | Action |
|---|---|---|
| `curl: (7) Failed to connect` | Service not started / wrong address or port | Confirm the process is running, the listen address, and the port; locally use `ss -ltnp \| grep 30081` |
| `curl: (28) timed out` | Firewall/security group, or rendering took longer than `-m` | First widen `-m` and retry; then check network policy |
| HTTP `401` | Missing or wrong `GATEWAY_API_KEY` | Re-export; note that `$` and spaces in the key need quoting |
| HTTP `403` | Key has no permission for this endpoint / IP allowlist | Check server-side permission config |
| HTTP `404` | Wrong path | Loop-probe paths in Step 2; defer to your service docs |
| HTTP `422` / `400` | Request body field mismatch | Compare the Section 2 fields against your service definition field by field |
| HTTP `429` | Rate limited | Lower concurrency; process serially with `sleep 1` between scenes |
| HTTP `5xx` | Server internal error (common: model not loaded, out of VRAM) | Check server logs; retry once, and if still failing, switch to `--mock` for a delivery placeholder |
| 200 returned but video is 0 bytes | Server produced an empty response | Treat as failure; don't carry an empty file into the downstream pipeline |
| Returned video duration doesn't match the audio | Wrong frame-rate/duration parameters | Compare the two with `ffprobe`; check the `frame_rate` config |

## 5. Async tasks and queueing

Some self-hosted gateways are **asynchronous**: they first return a task ID, then you poll for the
result. Recognition: the response is JSON (not video binary) and contains fields like
`task_id` / `job_id` / `status`.

Polling template (field names depend on your service, **VERIFY BEFORE USE**):

```bash
# Submit → get task_id (assume it returns {"task_id":"abc123"})
TASK=$(curl -sS -m 30 -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
  -H "Content-Type: application/json" -d @payload.json \
  "$GATEWAY_BASE_URL/v1/lipsync" | python3 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")

# Poll: at most 60 tries × 5 seconds = 5 minutes
for i in $(seq 1 60); do
  S=$(curl -sS -m 10 -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
        "$GATEWAY_BASE_URL/v1/tasks/$TASK" | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])")
  echo "try=$i status=$S"
  [ "$S" = "succeeded" ] && break
  [ "$S" = "failed" ] && { echo "task failed"; exit 1; }
  sleep 5
done
```

Key point: **you must set a maximum retry count** and distinguish `queued` / `running` /
`succeeded` / `failed`. Infinite polling hangs the whole pipeline.

## 6. Mock mode boundaries

With `--mock` or `SKILLKIT_MOCK=1`, the script **only produces metadata JSON and generates no
video**, with `"mock": true` in the output. Its only legitimate uses: a placeholder when integrating
downstream steps (concatenation, subtitles), and gateway-free self-testing in CI.

**Never** treat mock output as a deliverable—the file `"output_path"` points to doesn't exist.
Before delivery, confirm the file actually exists with `ls -l <output_path>`, and that the result
does not have `mock` set to `true`.

## 7. Security red lines

- Keys only go through environment variables; never into scripts, Git, or logs (when troubleshooting, print the length instead of the content).
- Treat files returned by the gateway as **untrusted input**: constrain the directory before saving (e.g. fixed output to an `output/` subdirectory); don't splice paths directly from filenames in the response.
- Deleting, overwriting, or publishing externally is irreversible—confirm with the user before doing so.
