#!/usr/bin/env python3
"""Video Domain Pipeline — 视频制作全流程编排。

独立领域，不使用编程领域的 skill。

用法:
  python3 video_pipeline.py --concept "宝宝测评手机" --type talking_character
  python3 video_pipeline.py --concept "..." --dry-run
"""
import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    "script": BASE / "script-writer" / "scripts" / "script_writer.py",
    "tts": BASE / "voice-synth" / "scripts" / "voice_synth.py",
    "lipsync": BASE / "lip-sync" / "scripts" / "lip_sync.py",
    "editor": BASE / "editor" / "scripts" / "editor.py",
    "subtitles": BASE / "subtitles" / "scripts" / "subtitles.py",
    "thumbnail": BASE / "thumbnail" / "scripts" / "thumbnail.py",
}


def run_step(name: str, cmd: list, dry_run: bool = False) -> dict:
    if dry_run:
        return {"step": name, "status": "planned", "cmd": " ".join(cmd[:3])}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        status = "success" if r.returncode == 0 else "error"
        data = {}
        if r.returncode == 0 and r.stdout:
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                data = {"raw": r.stdout[:500]}
        return {"step": name, "status": status, "data": data,
                "error": r.stderr[:300] if r.returncode != 0 else None}
    except Exception as e:
        return {"step": name, "status": "error", "error": str(e)}


def run_pipeline(concept: str, video_type: str = "talking_character",
                 duration: int = 30, platform: str = "douyin",
                 face_image: str = None, dry_run: bool = False) -> dict:
    steps = []
    out_dir = Path(f"/tmp/video_{datetime.now().strftime('%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    script_file = out_dir / "script.json"

    # Step 1: Script
    cmd = [sys.executable, str(SCRIPTS["script"]),
           "--concept", concept, "--type", video_type,
           "--duration", str(duration), "--platform", platform]
    if not dry_run:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        script_file.write_text(r.stdout, encoding="utf-8")
    steps.append(run_step("script", cmd, dry_run))

    # Step 2: TTS
    cmd = [sys.executable, str(SCRIPTS["tts"]),
           "--script", str(script_file)]
    steps.append(run_step("tts", cmd, dry_run))

    # Step 3: Lip Sync
    face = face_image or "/tmp/character.png"
    cmd = [sys.executable, str(SCRIPTS["lipsync"]),
           "--face", face, "--script", str(script_file),
           "--audio-dir", str(out_dir)]
    steps.append(run_step("lipsync", cmd, dry_run))

    # Step 4: Assembly
    cmd = [sys.executable, str(SCRIPTS["editor"]),
           "--script", str(script_file),
           "--clips-dir", str(out_dir),
           "--audio-dir", str(out_dir),
           "--output", str(out_dir / "final.mp4")]
    steps.append(run_step("assembly", cmd, dry_run))

    # Step 5: Subtitles
    cmd = [sys.executable, str(SCRIPTS["subtitles"]),
           "--script", str(script_file),
           "--output", str(out_dir / "subs.srt")]
    steps.append(run_step("subtitles", cmd, dry_run))

    # Step 6: Thumbnail
    title = concept
    cmd = [sys.executable, str(SCRIPTS["thumbnail"]),
           "--title", title, "--platform", platform,
           "--output", str(out_dir / "thumb.png")]
    steps.append(run_step("thumbnail", cmd, dry_run))

    success = sum(1 for s in steps if s["status"] == "success")
    return {
        "concept": concept,
        "video_type": video_type,
        "platform": platform,
        "duration": duration,
        "output_dir": str(out_dir),
        "steps": steps,
        "completed": success,
        "total": len(steps),
        "status": "complete" if success == len(steps) else "partial",
    }


def main():
    parser = argparse.ArgumentParser(description="Video production pipeline")
    parser.add_argument("--concept", required=True)
    parser.add_argument("--type", default="talking_character")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--platform", default="douyin")
    parser.add_argument("--face", help="Character face image")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.concept, args.type, args.duration,
                          args.platform, args.face, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Video Pipeline: {args.concept}")
        print(f"Type: {args.type} | Platform: {args.platform} | Duration: {args.duration}s")
        print()
        for s in result["steps"]:
            icon = {"success": "✓", "planned": "□", "error": "✗"}.get(s["status"], "?")
            print(f"  {icon} {s['step']}: {s['status']}")
        print(f"\nCompleted: {result['completed']}/{result['total']}")
        print(f"Output: {result['output_dir']}")


if __name__ == "__main__":
    main()
