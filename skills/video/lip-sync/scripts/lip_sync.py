#!/usr/bin/env python3
"""Lip Sync — 将角色口型与语音同步。

用法:
  python3 lip_sync.py --face face.png --audio /tmp/scene_1.wav
  python3 lip_sync.py --script script.json --audio-dir /tmp/tts_output/
"""
import argparse
import json
import sys
from pathlib import Path

MOCK_MODE = True
GATEWAY_URL = "http://127.0.0.1:30081/v1/lipsync"


def lip_sync(face_image: str, audio_path: str,
             output: str = None, mouth_width: int = 40,
             mouth_height: int = 30) -> dict:
    """Generate lip-synced video from face image + audio."""
    if MOCK_MODE:
        out = Path(output or f"/tmp/lipsync_{Path(audio_path).stem}.mp4")
        # Mock: just record metadata
        result = {
            "output_path": str(out),
            "face_image": face_image,
            "audio_path": audio_path,
            "mock": True,
            "mouth_params": {"width": mouth_width, "height": mouth_height},
            "note": "Mock mode: no actual video generated. Set MOCK_MODE=False + gateway for real output.",
        }
        return result

    import urllib.request
    payload = json.dumps({
        "face_image": face_image,
        "audio_path": audio_path,
        "mouth_width": mouth_width,
        "mouth_height": mouth_height,
    }).encode()
    req = urllib.request.Request(GATEWAY_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        video = resp.read()
        out = Path(output or f"/tmp/lipsync_{Path(audio_path).stem}.mp4")
        out.write_bytes(video)
        return {
            "output_path": str(out),
            "face_image": face_image,
            "audio_path": audio_path,
            "mock": False,
        }


def batch_lip_sync(script: dict, face_image: str,
                   audio_dir: str = "/tmp") -> dict:
    """Batch lip-sync for all scenes."""
    results = []
    for scene in script.get("scenes", []):
        audio = Path(audio_dir) / f"scene_{scene['id']}.wav"
        if not audio.exists() and MOCK_MODE:
            audio = Path(audio_dir) / f"tts_mock_{scene['id']}.wav"

        r = lip_sync(face_image, str(audio))
        r["scene_id"] = scene["id"]
        results.append(r)

    return {
        "total_scenes": len(results),
        "results": results,
        "all_generated": len(results) > 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Lip sync face to audio")
    parser.add_argument("--face", required=True, help="Face/character image path")
    parser.add_argument("--audio", help="Audio file path")
    parser.add_argument("--script", help="Script JSON (batch mode)")
    parser.add_argument("--audio-dir", default="/tmp", help="Audio directory for batch")
    parser.add_argument("--output", help="Output path")
    parser.add_argument("--mouth-width", type=int, default=40)
    parser.add_argument("--mouth-height", type=int, default=30)
    args = parser.parse_args()

    if args.script:
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = batch_lip_sync(script, args.face, args.audio_dir)
    elif args.audio:
        result = lip_sync(args.face, args.audio, args.output,
                          args.mouth_width, args.mouth_height)
    else:
        parser.error("Need --audio or --script")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
