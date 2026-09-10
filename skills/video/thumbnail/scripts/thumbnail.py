#!/usr/bin/env python3
"""Thumbnail Designer — 生成视频封面/缩略图。

用法:
  python3 thumbnail.py --video final.mp4 --output thumb.png
  python3 thumbnail.py --text "宝宝测评" --style funny --output cover.png
"""
import argparse
import json
import sys
from pathlib import Path

MOCK_MODE = True
GATEWAY_URL = "http://127.0.0.1:30080"

# Platform thumbnail specs
PLATFORM_SPECS = {
    "douyin": {"width": 1080, "height": 1920, "ratio": "9:16", "max_size_kb": 2048},
    "bilibili": {"width": 1920, "height": 1080, "ratio": "16:9", "max_size_kb": 2048},
    "tiktok": {"width": 1080, "height": 1920, "ratio": "9:16", "max_size_kb": 2048},
    "youtube": {"width": 1280, "height": 720, "ratio": "16:9", "max_size_kb": 2048},
}


def design_thumbnail(title: str, style: str = "funny",
                     platform: str = "douyin",
                     character_image: str = None,
                     output: str = None) -> dict:
    """Design a video thumbnail/cover."""
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["douyin"])
    out = Path(output or f"/tmp/thumbnail_{platform}.png")

    if MOCK_MODE:
        result = {
            "output_path": str(out),
            "title": title,
            "style": style,
            "platform": platform,
            "spec": spec,
            "character_image": character_image,
            "mock": True,
            "layout": {
                "text_position": "bottom_center" if spec["ratio"] == "9:16" else "center",
                "font_size": 72 if spec["width"] >= 1920 else 48,
                "text_color": "#FFFFFF",
                "text_shadow": True,
                "badge": "NEW" if style == "funny" else None,
            },
            "note": "Mock: use image-generation skill or FFmpeg to create actual thumbnail.",
        }
        return result

    import urllib.request
    payload = json.dumps({
        "prompt": f"Video thumbnail for '{title}', {style} style, {platform} format {spec['ratio']}",
        "width": spec["width"],
        "height": spec["height"],
    }).encode()
    req = urllib.request.Request(f"{GATEWAY_URL}/v1/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        img = resp.read()
        out.write_bytes(img)
        return {"output_path": str(out), "mock": False}


def extract_frame(video_path: str, timestamp: float = 0.5,
                  output: str = None) -> dict:
    """Extract a frame from video as thumbnail base."""
    out = Path(output or "/tmp/thumb_frame.png")
    if MOCK_MODE:
        return {"output_path": str(out), "source": video_path,
                "timestamp": timestamp, "mock": True}

    import subprocess
    cmd = ["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
           "-vframes", "1", str(out)]
    subprocess.run(cmd, capture_output=True, check=True)
    return {"output_path": str(out), "source": video_path, "mock": False}


def main():
    parser = argparse.ArgumentParser(description="Video thumbnail designer")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--style", default="funny",
                        choices=["funny", "professional", "dramatic", "cute"])
    parser.add_argument("--platform", default="douyin")
    parser.add_argument("--character", help="Character image path")
    parser.add_argument("--video", help="Extract frame from video")
    parser.add_argument("--output", help="Output path")
    args = parser.parse_args()

    if args.video:
        result = extract_frame(args.video, output=args.output)
    else:
        result = design_thumbnail(args.title, args.style, args.platform,
                                  args.character, args.output)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
