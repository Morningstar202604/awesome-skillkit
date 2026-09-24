#!/usr/bin/env python3
"""Lip Sync -- sync a character's mouth to speech.

**Real mode by default**: calls the user-provided lip-sync gateway to actually produce video.
With `--mock` or the `SKILLKIT_MOCK=1` env var it only emits metadata (generates no files,
for downstream integration testing only).

In real mode, if the gateway is unreachable it prints troubleshooting guidance and exits
non-zero; it never silently returns a fake result.
Gateway URL: `--gateway-url` > env var `GATEWAY_BASE_URL` > the repo example default.
Endpoint paths and field names follow your actual deployment (VERIFY BEFORE USE).

Usage:
  python3 lip_sync.py --face face.png --audio scene_1.wav
  python3 lip_sync.py --face face.png --script script.json --audio-dir tts/
  python3 lip_sync.py --face face.png --audio scene_1.wav --mock
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional

# repo example default; not a commitment to any vendor's public endpoint -- follow your actual deployment
DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:30081"
LIPSYNC_PATH = "/v1/lipsync"


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
    raw = os.environ.get("GATEWAY_TIMEOUT", "120").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        sys.stderr.write(f"[WARN] GATEWAY_TIMEOUT={raw!r} is not an integer; falling back to 120.\n")
        return 120


def require_file(path: str, what: str) -> None:
    if not Path(path).is_file():
        sys.stderr.write(f"[ERROR] {what} not found: {path}\n")
        sys.exit(3)


def probe_gateway(base_url: str) -> None:
    """Liveness probe: 2xx/401/403/404 all mean the service is up; if it cannot be reached, print troubleshooting guidance and exit non-zero."""
    try:
        urllib.request.urlopen(base_url + "/", timeout=5)
    except urllib.error.HTTPError:
        return  # 401/403/404 = the service is up; just a path or auth issue
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] Cannot reach the lip-sync gateway: {base_url} ({e.__class__.__name__}: {e})\n"
            f"Troubleshooting:\n"
            f"  1) Confirm the service is up: curl -sS -m 5 -o /dev/null -w '%{{http_code}}\\n' {base_url}/\n"
            f"  2) Confirm the URL is correct: export GATEWAY_BASE_URL=http://<host>:<port>  (no trailing slash)\n"
            f"  3) If you only need downstream integration: add --mock or SKILLKIT_MOCK=1 (the artifact is a placeholder, not deliverable)\n"
        )
        sys.exit(4)


def post_json(url: str, payload: dict, timeout: int) -> bytes:
    """POST JSON; on any failure print the reason and exit non-zero."""
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


def lip_sync(face_image: str, audio_path: str, output: Optional[str] = None,
             mouth_width: int = 40, mouth_height: int = 30,
             gateway_url: Optional[str] = None, mock: bool = False) -> Dict:
    """Generate a lip-synced video from a character image + audio."""
    out = Path(output or f"lipsync_{Path(audio_path).stem}.mp4")

    if mock:
        return {
            "output_path": str(out),
            "face_image": face_image,
            "audio_path": audio_path,
            "mock": True,
            "mouth_params": {"width": mouth_width, "height": mouth_height},
            "note": "Mock: the gateway was not called; the file at output_path does not exist.",
        }

    base_url = resolve_gateway(gateway_url)
    require_file(face_image, "face image")
    require_file(audio_path, "audio file")
    probe_gateway(base_url)

    payload = {
        "face_image": face_image,
        "audio_path": audio_path,
        "mouth_width": mouth_width,
        "mouth_height": mouth_height,
    }
    video = post_json(base_url + LIPSYNC_PATH, payload, gateway_timeout())
    if not video:
        sys.stderr.write(f"[ERROR] Gateway returned empty content: {base_url}{LIPSYNC_PATH}\n")
        sys.exit(4)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(video)
    return {
        "output_path": str(out),
        "face_image": face_image,
        "audio_path": audio_path,
        "bytes": len(video),
        "mock": False,
    }


def batch_lip_sync(script: dict, face_image: str, audio_dir: str = ".",
                   gateway_url: Optional[str] = None, mock: bool = False) -> Dict:
    """Batch lip-sync by script scene."""
    results = []
    missing = []
    for scene in script.get("scenes", []):
        audio = Path(audio_dir) / f"scene_{scene['id']}.wav"
        if not audio.is_file():
            if not mock:
                missing.append(str(audio))
                continue
            audio = Path(audio_dir) / f"tts_mock_{scene['id']}.wav"

        r = lip_sync(face_image, str(audio),
                     output=str(Path(audio).parent / f"scene_{scene['id']}.mp4"),
                     gateway_url=gateway_url, mock=mock)
        r["scene_id"] = scene["id"]
        results.append(r)

    if missing:
        sys.stderr.write(
            "[ERROR] The following scene audios are missing and cannot be handled in real mode: " + ", ".join(missing) + "\n"
        )
        sys.exit(3)

    return {
        "total_scenes": len(results),
        "results": results,
        "all_generated": len(results) > 0,
        "mock": mock,
    }


def main():
    parser = argparse.ArgumentParser(description="Lip sync face to audio")
    parser.add_argument("--face", required=True, help="Face/character image path")
    parser.add_argument("--audio", help="Audio file path")
    parser.add_argument("--script", help="Script JSON (batch mode)")
    parser.add_argument("--audio-dir", default=".", help="Audio directory for batch")
    parser.add_argument("--output", help="Output path")
    parser.add_argument("--mouth-width", type=int, default=40)
    parser.add_argument("--mouth-height", type=int, default=30)
    parser.add_argument("--gateway-url",
                        help="gateway root URL (defaults to GATEWAY_BASE_URL)")
    parser.add_argument("--mock", action="store_true",
                        help="only emit metadata, do not call the gateway (equivalent to SKILLKIT_MOCK=1)")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.script:
        require_file(args.script, "script file")
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = batch_lip_sync(script, args.face, args.audio_dir,
                                args.gateway_url, mock)
    elif args.audio:
        result = lip_sync(args.face, args.audio, args.output,
                          args.mouth_width, args.mouth_height,
                          args.gateway_url, mock)
    else:
        parser.error("Need --audio or --script")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
