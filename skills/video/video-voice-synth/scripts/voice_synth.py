#!/usr/bin/env python3
"""Video Voice Synthesis (TTS) -- text-to-speech.

**Real mode by default**: calls the user-provided TTS gateway to actually produce audio.
With `--mock` or the `SKILLKIT_MOCK=1` env var it generates a silent WAV placeholder
(downstream integration testing only, not deliverable).

In real mode, if the gateway is unreachable it prints troubleshooting guidance and exits
non-zero; it never silently returns a fake result.
Gateway URL: `--gateway-url` > env var `GATEWAY_BASE_URL` > the repo example default.
Endpoint paths and field names follow your actual deployment (VERIFY BEFORE USE).

Usage:
  python3 voice_synth.py --text "Hello" --voice baby_f01
  python3 voice_synth.py --script script.json           # batch
  python3 voice_synth.py --text "Hello" --mock          # silent placeholder
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import Any, Dict, Optional

# repo example default; not a commitment to any vendor's public endpoint -- follow your actual deployment
DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:30081"
TTS_PATH = "/v1/tts"

VOICES = {
    "baby_f01": {"desc": "High-pitched child", "pitch": 5, "speed": 1.3},
    "baby_f02": {"desc": "Slower baby", "pitch": 4, "speed": 1.0},
    "adult_m01": {"desc": "Male narrator", "pitch": 0, "speed": 1.0},
    "adult_f01": {"desc": "Female narrator", "pitch": 1, "speed": 1.0},
    "mascot_01": {"desc": "Enthusiastic mascot", "pitch": 2, "speed": 1.1},
    "narrator_01": {"desc": "Neutral clear", "pitch": 0, "speed": 0.9},
}


def mock_enabled(cli_mock: bool = False) -> bool:
    """`--mock` explicitly on, or the env var SKILLKIT_MOCK=1/true/yes/on; default False (real mode)."""
    if cli_mock:
        return True
    return os.environ.get("SKILLKIT_MOCK", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def resolve_gateway(cli_url: Optional[str] = None) -> str:
    url = cli_url or os.environ.get("GATEWAY_BASE_URL") or DEFAULT_GATEWAY_BASE_URL
    return url.rstrip("/")


def gateway_timeout() -> int:
    raw = os.environ.get("GATEWAY_TIMEOUT", "30").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        sys.stderr.write(f"[WARN] GATEWAY_TIMEOUT={raw!r} is not an integer; falling back to 30.\n")
        return 30


def probe_gateway(base_url: str) -> None:
    """Liveness probe: 2xx/401/403/404 all mean the service is up; if it cannot be reached, print troubleshooting guidance and exit non-zero."""
    try:
        urllib.request.urlopen(base_url + "/", timeout=5)
    except urllib.error.HTTPError:
        return
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] Cannot reach the TTS gateway: {base_url} ({e.__class__.__name__}: {e})\n"
            f"Troubleshooting:\n"
            f"  1) Confirm the service is up: curl -sS -m 5 -o /dev/null -w '%{{http_code}}\\n' {base_url}/\n"
            f"  2) Confirm the URL is correct: export GATEWAY_BASE_URL=http://<host>:<port>  (no trailing slash)\n"
            f"  3) If you only need downstream integration: add --mock or SKILLKIT_MOCK=1 (the artifact is a silent placeholder, not deliverable)\n"
        )
        sys.exit(4)


def post_json(url: str, payload: dict, timeout: int) -> bytes:
    api_key = os.environ.get("GATEWAY_API_KEY", "").strip()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "ignore")[:500]
        except Exception:
            pass
        sys.stderr.write(f"[ERROR] Gateway returned HTTP {e.code} {e.reason}\nBody: {body}\n")
        sys.exit(4)
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] Request to gateway failed: {url} ({e.__class__.__name__}: {e})\n"
            f"Common causes: timeout (raise GATEWAY_TIMEOUT), rate limiting (HTTP 429), service crash.\n"
        )
        sys.exit(4)


def _mock_synth(text: str, voice: str, output: Optional[str] = None) -> Dict[str, Any]:
    """Generate a silent WAV placeholder (duration estimated from character count; for downstream integration only)."""
    duration = max(0.5, len(text) * 0.15)
    sample_rate = 24000
    num_samples = int(duration * sample_rate)
    out = Path(output or f"tts_mock_{int(time.time())}.wav")

    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)

    return {
        "audio_path": str(out), "text": text, "voice_used": voice,
        "mock": True, "duration_sec": round(duration, 2),
        "sample_rate": sample_rate,
        "note": "Mock: silent placeholder, not deliverable.",
    }


def synthesize_voice(text: str, voice: str = "baby_f01",
                     speed: Optional[float] = None, pitch: Optional[int] = None,
                     output: Optional[str] = None,
                     gateway_url: Optional[str] = None,
                     mock: bool = False) -> Dict[str, Any]:
    """Generate TTS audio (real gateway / mock silent placeholder)."""
    voice_conf = VOICES.get(voice, {"pitch": 0, "speed": 1.0})
    speed = speed or voice_conf["speed"]
    pitch = pitch if pitch is not None else voice_conf["pitch"]

    if mock:
        return _mock_synth(text, voice, output)

    if not text.strip():
        sys.stderr.write("[ERROR] Text to synthesize is empty.\n")
        sys.exit(3)

    base_url = resolve_gateway(gateway_url)
    probe_gateway(base_url)
    payload = {
        "text": text, "voice": voice,
        "speed": speed, "pitch": pitch, "format": "wav",
    }
    audio = post_json(base_url + TTS_PATH, payload, gateway_timeout())
    if not audio:
        sys.stderr.write(f"[ERROR] Gateway returned empty audio: {base_url}{TTS_PATH}\n")
        sys.exit(4)

    out = Path(output or f"tts_{int(time.time())}.wav")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(audio)
    return {
        "audio_path": str(out), "text": text, "voice_used": voice,
        "speed": speed, "pitch": pitch, "bytes": len(audio), "mock": False,
    }


def batch_synth(script: Dict, gateway_url: Optional[str] = None,
                mock: bool = False, audio_dir: str = ".") -> Dict[str, Any]:
    """Batch-synthesize by script scene.

    audio_dir: the output directory for scene audio (the downstream lip_sync --audio-dir and
    editor --audio-dir rely on the scene_<id>.wav naming contract in the same directory).
    """
    results = []
    conf = script.get("tts_config", {})
    for scene in script.get("scenes", []):
        dialogue = scene.get("dialogue", "")
        if not dialogue:
            continue
        r = synthesize_voice(
            text=dialogue,
            voice=conf.get("voice_style", "baby_f01"),
            speed=conf.get("speed", 1.0),
            output=str(Path(audio_dir) / f"scene_{scene['id']}.wav"),
            gateway_url=gateway_url,
            mock=mock,
        )
        r["scene_id"] = scene["id"]
        r["planned_duration"] = scene.get("duration_sec", 0)
        results.append(r)

    return {
        "total_scenes": len(results),
        "results": results,
        "all_generated": all(r.get("audio_path") for r in results),
        "mock": mock,
    }


def main():
    parser = argparse.ArgumentParser(description="TTS voice synthesis")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--voice", default="baby_f01", choices=list(VOICES.keys()))
    parser.add_argument("--speed", type=float)
    parser.add_argument("--pitch", type=int)
    parser.add_argument("--script", help="Script JSON file (batch mode)")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--audio-dir", default=".",
                        help="Batch mode: directory to write scene_<id>.wav")
    parser.add_argument("--gateway-url", help="gateway root URL (defaults to GATEWAY_BASE_URL)")
    parser.add_argument("--mock", action="store_true",
                        help="generate a silent placeholder, do not call the gateway (equivalent to SKILLKIT_MOCK=1)")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.script:
        if not Path(args.script).is_file():
            sys.stderr.write(f"[ERROR] Script file not found: {args.script}\n")
            sys.exit(3)
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = batch_synth(script, args.gateway_url, mock, args.audio_dir)
    elif args.text:
        result = synthesize_voice(args.text, args.voice, args.speed, args.pitch,
                                  args.output, args.gateway_url, mock)
    else:
        parser.error("Need --text or --script")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
