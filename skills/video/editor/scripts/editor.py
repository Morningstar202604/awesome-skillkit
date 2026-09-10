#!/usr/bin/env python3
"""Video Editor — 视频剪辑/合成/转场/特效。

用法:
  python3 editor.py --clips clip1.mp4 clip2.mp4 --output final.mp4
  python3 editor.py --script script.json --clips-dir /tmp/clips/ --audio-dir /tmp/tts/
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

MOCK_MODE = True


def assemble_video(clips: List[str], audio: List[str] = None,
                   transitions: List[str] = None, output: str = None) -> Dict:
    """Assemble clips into final video (mock or real)."""
    out = Path(output or "/tmp/final_video.mp4")

    if MOCK_MODE:
        result = {
            "output_path": str(out),
            "clips_used": len(clips),
            "audio_tracks": len(audio or []),
            "transitions": transitions or [],
            "mock": True,
            "note": "Mock: no actual FFmpeg run. Install ffmpeg for real assembly.",
        }
        return result

    import subprocess
    # Build FFmpeg concat
    concat_file = out.with_suffix(".txt")
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
           "-i", str(concat_file), "-c", "copy", str(out)]
    subprocess.run(cmd, capture_output=True, check=True)
    return {"output_path": str(out), "clips_used": len(clips), "mock": False}


def add_audio(video: str, audio: str, output: str = None) -> Dict:
    """Mux audio onto video."""
    out = Path(output or video.replace(".mp4", "_mixed.mp4"))
    if MOCK_MODE:
        return {"output_path": str(out), "mock": True, "video": video, "audio": audio}
    import subprocess
    cmd = ["ffmpeg", "-y", "-i", video, "-i", audio,
           "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)]
    subprocess.run(cmd, capture_output=True, check=True)
    return {"output_path": str(out), "mock": False}


def full_pipeline(script: dict, clips_dir: str = "/tmp/clips",
                  audio_dir: str = "/tmp/tts", output: str = None) -> Dict:
    """Full assembly: clips + audio + subtitles + thumbnail."""
    scenes = script.get("scenes", [])
    clips = []
    audios = []

    for scene in scenes:
        sid = scene["id"]
        clip = Path(clips_dir) / f"scene_{sid}.mp4"
        audio = Path(audio_dir) / f"scene_{sid}.wav"
        if clip.exists() or MOCK_MODE:
            clips.append(str(clip))
        if audio.exists() or MOCK_MODE:
            audios.append(str(audio))

    result = assemble_video(clips, audios, output=output)
    result["scenes"] = len(scenes)
    result["title"] = script.get("title", "untitled")
    return result


def main():
    parser = argparse.ArgumentParser(description="Video editor / assembler")
    parser.add_argument("--clips", nargs="*", help="Clip files to assemble")
    parser.add_argument("--audio", nargs="*", help="Audio files to mix")
    parser.add_argument("--script", help="Script JSON for full pipeline")
    parser.add_argument("--clips-dir", default="/tmp/clips")
    parser.add_argument("--audio-dir", default="/tmp/tts")
    parser.add_argument("--output", default="/tmp/final_video.mp4")
    parser.add_argument("--transitions", nargs="*", help="Transition types")
    args = parser.parse_args()

    if args.script:
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = full_pipeline(script, args.clips_dir, args.audio_dir, args.output)
    elif args.clips:
        result = assemble_video(args.clips, args.audio, args.transitions, args.output)
    elif args.audio and len(args.audio) == 1:
        result = add_audio(args.clips[0] if args.clips else "/tmp/clip.mp4",
                           args.audio[0], args.output)
    else:
        parser.error("Need --clips, --script, or --audio")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
