# TTS Gateway Integration (video-voice-synth)

This skill uses a "**bring-your-own-gateway**" model: **the repo does not provide, and does not embed,
any TTS vendor endpoint**. You must deploy or designate a TTS service yourself and tell the script about it.

> **Endpoints depend on your actual deployment and must be confirmed before running.** The
> `127.0.0.1:30081`, path `/v1/tts`, and field names `speed` / `pitch` / `format` appearing in this
> document are all **repo example defaults** (from the initial constants in this skill's scripts),
> not any vendor's public API promise. **VERIFY BEFORE USE**: override them with your service docs or
> `curl` probe results before executing—see Section 3.

## Table of Contents

0. Pre-flight self-check / 1. Environment variable conventions / 2. Request and response conventions / 3. Three-step connectivity probe
4. Failure handling table / 5. Batch synthesis and concurrency / 6. Mock mode boundaries / 7. Security red lines

## 0. Pre-flight self-check

```bash
command -v ffprobe >/dev/null && echo "ffprobe=OK" || echo "ffprobe=missing (duration validation unavailable)"
echo "BASE=${GATEWAY_BASE_URL:-<not set>}  TIMEOUT=${GATEWAY_TIMEOUT:-30}"
[ -n "$GATEWAY_API_KEY" ] && echo "KEY=set (length ${#GATEWAY_API_KEY})" || echo "KEY=not set"
```

Expected: BASE is your gateway root address, ffprobe is available (used to validate audio duration).
If BASE is `<not set>`, set it per Section 1 first—don't fudge it with the script's built-in defaults.

## 1. Environment variable conventions

The names below are **convention examples for this repo**, not industry standards; if your gateway
requires different names, defer to your deployment and change only the line where the script reads
the variable.

| Variable | Example value | Required | Notes |
|---|---|---|---|
| `GATEWAY_BASE_URL` | `http://127.0.0.1:30081` | Yes | Gateway root address, **no trailing slash, no path** |
| `GATEWAY_API_KEY` | (your key) | Depends on gateway | Sent via the `Authorization` header, never written to disk |
| `GATEWAY_TIMEOUT` | `30` | No | Per-request timeout in seconds; raise for long text based on character count (see Section 5) |
| `TTS_OUTPUT_FORMAT` | `wav` | No | Target audio container; downstream lip-sync generally expects `wav` |

```bash
export GATEWAY_BASE_URL="http://127.0.0.1:30081"   # ← change to your actual address
export GATEWAY_API_KEY="..."
export GATEWAY_TIMEOUT=30
```

## 2. Request and response conventions

**VERIFY BEFORE USE**: below is the request body this skill's scripts currently send. Field names,
value ranges, and voice IDs (e.g. `baby_f01`) **must match your deployed service**—especially the
voice IDs, which come from this skill's Voice Catalog table and are only valid if your gateway has
registered a voice with the same name.

```
POST {GATEWAY_BASE_URL}/v1/tts
Content-Type: application/json
Authorization: Bearer ${GATEWAY_API_KEY}

{
  "text": "Guess how much I paid for this?",
  "voice": "baby_f01",
  "speed": 1.2,
  "pitch": 3,
  "format": "wav"
}
```

Success criteria (all three must hold):

1. HTTP `2xx`;
2. The response body is audio binary (not a JSON error object)—use `file out.wav` to check it's recognized as audio;
3. `ffprobe -v error -show_entries format=duration -of default=nw=1 out.wav` yields a
   **reasonable duration** (rule of thumb: Chinese ≈ 4–6 chars/sec; this is a guideline value,
   calibrate against your actual voice).

**Voice list verification** (do once before batch synthesis):

```bash
curl -sS -m 10 -H "Authorization: Bearer ${GATEWAY_API_KEY}" "$GATEWAY_BASE_URL/v1/voices"
# If the endpoint exists it returns available voices; 404 means this gateway has no directory endpoint → test-synthesize 1 short sentence per voice
```

If the returned list doesn't contain IDs like `baby_f01`, don't put it in the script—it will definitely fail.

## 3. Three-step connectivity probe

```bash
# Step 1: is the service running?
curl -sS -m 5 -o /dev/null -w "HTTP=%{http_code} connect=%{time_connect}s\n" "$GATEWAY_BASE_URL/"
# Expected: any of 200/401/403/404.
# (7) Failed to connect = not started or wrong address; (28) timed out = firewall/security group

# Step 2: health check (path depends on your service)
for p in /health /healthz /v1/health /docs; do
  printf "%-12s " "$p"; curl -sS -m 5 -o /dev/null -w "%{http_code}\n" "$GATEWAY_BASE_URL$p"
done

# Step 3: real liveness check (one short sentence is enough, confirms auth + synthesis pipeline)
curl -sS -m "$GATEWAY_TIMEOUT" -o probe.wav -w "HTTP=%{http_code} total=%{time_total}s\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
  -d '{"text":"test","voice":"baby_f01","speed":1.0,"pitch":0,"format":"wav"}' \
  "$GATEWAY_BASE_URL/v1/tts"
ls -l probe.wav && file probe.wav
```

Expected: Step 3 shows HTTP=200, and `file probe.wav` output contains `WAV` / `RIFF` / `Audio`.
If `file` shows `ASCII text` or `JSON`, the server returned an error message—`cat probe.wav` to see
the specific reason.

## 4. Failure handling table

| Symptom | Cause | Action |
|---|---|---|
| `curl: (7) Failed to connect` | Service not started / wrong port | Confirm process and port: `ss -ltnp \| grep 30081` |
| `curl: (28) timed out` | Network blocked, or text too long causing render timeout | Increase `GATEWAY_TIMEOUT`; split long sentences into shorter ones and synthesize separately |
| HTTP `401` | Key missing or wrong | Re-export; use single quotes if the key contains `$` or spaces |
| HTTP `403` | No permission for this endpoint / IP allowlist | Check server-side permission config |
| HTTP `404` | Wrong path | Loop-probe paths in Step 2 |
| HTTP `422` / `400` | Field mismatch (often `voice` value not in the voice table) | Verify the ID using the voice-list endpoint in Section 2 |
| HTTP `429` | Rate limited | Serialize + `sleep 0.5` between requests; reduce concurrency in batch mode |
| HTTP `5xx` | Server error (model not loaded, out of VRAM) | Check server logs; retry once, and if still failing, use `--mock` as a placeholder |
| 200 but file is JSON text | Server returned an error object | `cat` the file and look at the message field |
| 200 but duration abnormally short (<0.3s) | Empty text or encoding issue | Check whether JSON is UTF-8; for Chinese, do nothing beyond `\uXXXX` escaping |
| Silent audio (all-zero samples) | Synthesis failed but silence was returned | Criterion: `ffprobe -af volumedetect` and check `mean_volume`; near -91 dB means empty |

## 5. Batch synthesis and concurrency

Batch mode synthesizes item by item according to the script's `scenes`, outputting `scene_<id>.wav`.
Key points:

1. **Prefer serial.** Self-hosted gateways are often single-GPU; concurrency easily triggers 5xx or 429;
   get serial working before adding concurrency.
2. **Scale timeout by character count.** Rule of thumb: `GATEWAY_TIMEOUT = 15 + chars × 0.2` seconds;
   split long sentences first.
3. **Save and validate each item to disk.** Immediately after each synthesis, run `ffprobe` to get the
   duration and compare with the script's `duration_sec`; record any deviation > 0.5s—downstream
   lip-sync and picture timing will drift along with it.
4. **Don't abort the whole run on failure**: record the failed scene ids, then re-run the failures after
   everything else finishes.

Re-run example (retry failed scenes individually):

```bash
python3 - <<'PY'
import json, pathlib
for p in sorted(pathlib.Path(".").glob("scene_*.wav")):
    print(p.name, p.stat().st_size)
PY
# Expected: every scene has a file and size > 0; any zero-length file needs a re-run
```

## 6. Mock mode boundaries

With `--mock` or `SKILLKIT_MOCK=1`, the script generates **silent WAVs** (duration estimated from
character count) and outputs `"mock": true`. Legitimate uses: downstream lip-sync / concatenation
pipeline integration testing, CI self-testing without a gateway.

**Never** treat mock audio as a deliverable: it's a silent file of all-zero samples. Before delivery,
confirm: `ffprobe -v error -af volumedetect -f null -` shows `mean_volume` well above -91 dB, and
the result does not have `mock` set to `true`.

## 7. Security red lines

- Keys only go through environment variables; never into scripts, Git, or plaintext logs (print only the length).
- Treat text input as untrusted: don't splice user text directly into shell commands; use JSON serialization.
- Overwriting existing audio or deleting files is irreversible—confirm with the user before doing so.
