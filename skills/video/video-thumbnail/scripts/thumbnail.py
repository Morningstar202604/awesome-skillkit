#!/usr/bin/env python3
"""Thumbnail Designer -- generate a video cover / thumbnail.

**Real mode by default**:
  - `--video` uses ffmpeg to extract a frame;
  - otherwise it calls the user-provided image-generation gateway.
With `--mock` or the `SKILLKIT_MOCK=1` env var it only emits layout metadata (generates no
files, for downstream integration testing only).

In real mode, if ffmpeg / the gateway is missing it prints guidance and exits non-zero; it
never silently returns a fake result.
Gateway URL: `--gateway-url` > env var `GATEWAY_BASE_URL` > the repo example default.

Usage:
  python3 thumbnail.py --video final.mp4 --output thumb.png
  python3 thumbnail.py --title "toddler review" --style funny --output cover.png
  python3 thumbnail.py --title "toddler review" --mock
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional

FFMPEG_HINT = (
    "Debian/Ubuntu : sudo apt update && sudo apt install -y ffmpeg\n"
    "  macOS         : brew install ffmpeg\n"
    "  verify        : ffmpeg -version"
)

# repo example default; not a commitment to any vendor's public endpoint -- follow your actual deployment
DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:30080"
GENERATE_PATH = "/v1/generate"

# platform cover specs (common 2026 values; verify the platform's latest rules before publishing)
PLATFORM_SPECS = {
    "douyin": {"width": 1080, "height": 1920, "ratio": "9:16", "max_size_kb": 2048},
    "bilibili": {"width": 1920, "height": 1080, "ratio": "16:9", "max_size_kb": 2048},
    "tiktok": {"width": 1080, "height": 1920, "ratio": "9:16", "max_size_kb": 2048},
    "youtube": {"width": 1280, "height": 720, "ratio": "16:9", "max_size_kb": 2048},
}


def mock_enabled(cli_mock: bool = False) -> bool:
    """`--mock` explicitly on, or the env var SKILLKIT_MOCK=1/true/yes/on; default False (real mode)."""
    if cli_mock:
        return True
    return os.environ.get("SKILLKIT_MOCK", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def require_tool(name: str, hint: str) -> None:
    if shutil.which(name):
        return
    sys.stderr.write(
        f"[ERROR] Real mode requires the external tool {name}, but it is not on PATH.\n"
        f"Install instructions:\n  {hint}\n"
        f"If you only need to integrate downstream, add --mock (the artifact is a placeholder, no file is really generated).\n"
    )
    sys.exit(2)


def resolve_gateway(cli_url: Optional[str] = None) -> str:
    url = cli_url or os.environ.get("GATEWAY_BASE_URL") or DEFAULT_GATEWAY_BASE_URL
    return url.rstrip("/")


def probe_gateway(base_url: str) -> None:
    """Liveness probe: 2xx/401/403/404 all mean the service is up; if it cannot be reached, print troubleshooting guidance and exit non-zero."""
    try:
        urllib.request.urlopen(base_url + "/", timeout=5)
    except urllib.error.HTTPError:
        return
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] Cannot reach the image-generation gateway: {base_url} ({e.__class__.__name__}: {e})\n"
            f"Troubleshooting:\n"
            f"  1) Confirm the service is up: curl -sS -m 5 -o /dev/null -w '%{{http_code}}\\n' {base_url}/\n"
            f"  2) Confirm the URL is correct: export GATEWAY_BASE_URL=http://<host>:<port>  (no trailing slash)\n"
            f"  3) If you only need downstream integration: add --mock or SKILLKIT_MOCK=1 (the artifact is a placeholder, not deliverable)\n"
        )
        sys.exit(4)


def post_json(url: str, payload: dict, timeout: int = 60) -> bytes:
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
            f"Common causes: timeout, rate limiting (HTTP 429), service crash.\n"
        )
        sys.exit(4)


def _layout(spec: dict, style: str) -> dict:
    """Cover text layout parameters (empirical; on vertical video the text is pushed down to avoid platform UI)."""
    return {
        "text_position": "bottom_center" if spec["ratio"] == "9:16" else "center",
        "font_size": 72 if spec["width"] >= 1920 else 48,
        "text_color": "#FFFFFF",
        "text_shadow": True,
        "badge": "NEW" if style == "funny" else None,
    }


def design_thumbnail(title: str, style: str = "funny", platform: str = "douyin",
                     character_image: Optional[str] = None,
                     output: Optional[str] = None,
                     gateway_url: Optional[str] = None,
                     mock: bool = False) -> Dict:
    """Generate a cover per platform spec (real mode calls the image-generation gateway)."""
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["douyin"])
    out = Path(output or f"thumbnail_{platform}.png")

    if mock:
        return {
            "output_path": str(out), "title": title, "style": style,
            "platform": platform, "spec": spec,
            "character_image": character_image,
            "layout": _layout(spec, style), "mock": True,
            "note": "Mock: the gateway was not called; the file at output_path does not exist.",
        }

    base_url = resolve_gateway(gateway_url)
    if character_image and not Path(character_image).is_file():
        sys.stderr.write(f"[ERROR] Character image not found: {character_image}\n")
        sys.exit(3)
    probe_gateway(base_url)

    payload = {
        "prompt": f"Video thumbnail for '{title}', {style} style, "
                  f"{platform} format {spec['ratio']}",
        "width": spec["width"],
        "height": spec["height"],
    }
    img = post_json(base_url + GENERATE_PATH, payload)
    if not img:
        sys.stderr.write(f"[ERROR] Gateway returned empty content: {base_url}{GENERATE_PATH}\n")
        sys.exit(4)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    result = {"output_path": str(out), "title": title, "platform": platform,
              "spec": spec, "layout": _layout(spec, style), "mock": False}
    size_kb = out.stat().st_size / 1024
    if size_kb > spec["max_size_kb"]:
        sys.stderr.write(
            f"[WARN] Cover {size_kb:.0f} KB exceeds the platform limit {spec['max_size_kb']} KB; "
            f"convert to JPG or lower the quality and re-export.\n"
        )
    return result


def extract_frame(video_path: str, timestamp: float = 0.5,
                  output: Optional[str] = None, mock: bool = False) -> Dict:
    """Extract a frame from the video as the cover base image."""
    out = Path(output or "thumb_frame.png")

    if mock:
        return {"output_path": str(out), "source": video_path,
                "timestamp": timestamp, "mock": True}

    require_tool("ffmpeg", FFMPEG_HINT)
    if not Path(video_path).is_file():
        sys.stderr.write(f"[ERROR] Video file not found: {video_path}\n")
        sys.exit(3)

    # -ss before -i = fast seek; the opening is often black, so the default 0.5s may still be too early
    cmd = ["ffmpeg", "-y", "-nostdin", "-ss", str(timestamp), "-i", video_path,
           "-frames:v", "1", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(
            f"[ERROR] ffmpeg frame extraction failed exit={proc.returncode}\n"
            f"Command: {' '.join(cmd)}\n"
        )
        sys.stderr.write((proc.stderr or "").strip()[-1500:] + "\n")
        sys.exit(proc.returncode or 1)
    if not out.is_file() or out.stat().st_size == 0:
        sys.stderr.write(f"[ERROR] Extracted frame is empty: {out} (try raising --timestamp)\n")
        sys.exit(3)

    return {"output_path": str(out), "source": video_path,
            "timestamp": timestamp, "mock": False}


def main():
    parser = argparse.ArgumentParser(description="Video thumbnail designer")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--style", default="funny",
                        choices=["funny", "professional", "dramatic", "cute"])
    parser.add_argument("--platform", default="douyin")
    parser.add_argument("--character", help="Character image path")
    parser.add_argument("--video", help="Extract frame from video")
    parser.add_argument("--timestamp", type=float, default=0.5,
                        help="frame timestamp (seconds); >=1.0 recommended to avoid the black opening")
    parser.add_argument("--output", help="Output path")
    parser.add_argument("--gateway-url", help="gateway root URL (defaults to GATEWAY_BASE_URL)")
    parser.add_argument("--mock", action="store_true",
                        help="only emit metadata, do not call the gateway/ffmpeg (equivalent to SKILLKIT_MOCK=1)")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.video:
        result = extract_frame(args.video, args.timestamp, args.output, mock)
    elif args.title:
        result = design_thumbnail(args.title, args.style, args.platform,
                                  args.character, args.output,
                                  args.gateway_url, mock)
    else:
        parser.error("Need --video or --title")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
