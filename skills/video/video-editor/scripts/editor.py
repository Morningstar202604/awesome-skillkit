#!/usr/bin/env python3
"""Video Editor -- video editing / compositing / transitions / audio mixing.

**Real mode by default**: calls ffmpeg to actually produce files.
With `--mock` or the `SKILLKIT_MOCK=1` env var it only emits metadata (generates no files,
for downstream integration testing only).

In real mode, if ffmpeg is missing it prints install instructions and exits non-zero; it never
silently returns a fake result.

Usage:
  python3 editor.py --clips clip1.mp4 clip2.mp4 --output final.mp4
  python3 editor.py --clips clip1.mp4 --audio bgm.mp3 --output final.mp4
  python3 editor.py --script script.json --clips-dir clips/ --audio-dir tts/
  python3 editor.py --clips clip1.mp4 --mock
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

FFMPEG_HINT = (
    "Debian/Ubuntu : sudo apt update && sudo apt install -y ffmpeg\n"
    "  macOS         : brew install ffmpeg\n"
    "  verify        : ffmpeg -version"
)


def mock_enabled(cli_mock: bool = False) -> bool:
    """`--mock` explicitly on, or the env var SKILLKIT_MOCK=1/true/yes/on; default False (real mode)."""
    if cli_mock:
        return True
    return os.environ.get("SKILLKIT_MOCK", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def require_tool(name: str, hint: str) -> None:
    """The external tools required by real mode must exist; otherwise print install instructions and exit non-zero."""
    if shutil.which(name):
        return
    sys.stderr.write(
        f"[ERROR] Real mode requires the external tool {name}, but it is not on PATH.\n"
        f"Install instructions:\n  {hint}\n"
        f"If you only need to integrate downstream, add --mock (the artifact is a placeholder, no file is really generated).\n"
    )
    sys.exit(2)


def run_ffmpeg(cmd: List[str]) -> None:
    """Run ffmpeg; on failure print the full command and stderr and exit non-zero."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(
            f"[ERROR] ffmpeg failed exit={proc.returncode}\n"
            f"Command: {' '.join(cmd)}\n"
        )
        sys.stderr.write((proc.stderr or "").strip()[-1500:] + "\n")
        sys.exit(proc.returncode or 1)


def _has_audio_stream(path: str) -> bool:
    """Use ffprobe to decide whether the file has an audio track (determining whether [0:a] is available on mixing)."""
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return bool(proc.stdout.strip())


def _write_concat_list(clips: List[str], concat_file: Path) -> None:
    """concat demuxer manifest; paths are normalized to absolute paths and used with -safe 0."""
    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{Path(clip).resolve()}'\n")


def add_audio(video: str, audio: List[str], output: Optional[str] = None,
              mock: bool = False) -> Dict:
    """Mix audio (one or more tracks) onto a video, outputting a new file."""
    out = Path(output or str(Path(video).with_name(Path(video).stem + "_mixed.mp4")))

    if mock:
        return {"output_path": str(out), "video": video,
                "audio": audio, "mock": True}

    require_tool("ffmpeg", FFMPEG_HINT)
    for path in [video] + list(audio):
        if not Path(path).is_file():
            sys.stderr.write(f"[ERROR] input file not found: {path}\n")
            sys.exit(3)

    cmd: List[str] = ["ffmpeg", "-y", "-nostdin", "-i", video] + \
        sum([["-i", a] for a in audio], [])
    # mix the video's own audio track too if present, otherwise only attach the external audio
    own = _has_audio_stream(video)
    labels = (["0:a"] if own else []) + [f"{i}:a" for i in range(1, len(audio) + 1)]
    if not labels:
        sys.stderr.write("[ERROR] No audio input to mix.\n")
        sys.exit(3)

    if len(labels) == 1:
        cmd += ["-map", "0:v", "-map", labels[0],
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    else:
        fc = "".join(f"[{l}]" for l in labels) + \
            f"amix=inputs={len(labels)}:duration=first[a]"
        cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    run_ffmpeg(cmd)
    return {"output_path": str(out), "video": video, "audio": audio, "mock": False}


def assemble_video(clips: List[str], audio: Optional[List[str]] = None,
                   transitions: Optional[List[str]] = None,
                   output: Optional[str] = None, mock: bool = False) -> Dict:
    """Concatenate clips; if audio is given, mix it in as well."""
    out = Path(output or "final_video.mp4")
    transitions = transitions or []
    audio = audio or []

    if mock:
        return {
            "output_path": str(out),
            "clips_used": len(clips),
            "audio_tracks": len(audio),
            "transitions": transitions,
            "mock": True,
            "note": "Mock: ffmpeg was not called; the file at output_path does not exist.",
        }

    require_tool("ffmpeg", FFMPEG_HINT)
    if not clips:
        sys.stderr.write("[ERROR] --clips is empty; nothing to concatenate.\n")
        sys.exit(3)
    missing = [c for c in clips if not Path(c).is_file()]
    if missing:
        sys.stderr.write("[ERROR] The following clips do not exist: " + ", ".join(missing) + "\n")
        sys.exit(3)
    if any(t and t != "cut" for t in transitions):
        sys.stderr.write(
            f"[WARN] Transitions {transitions} are not implemented in real mode yet; this run uses hard cuts.\n"
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    concat_file = out.with_name(out.stem + "_concat.txt")
    combined = out.with_name(out.stem + "_concat" + out.suffix)
    _write_concat_list(clips, concat_file)
    run_ffmpeg(["ffmpeg", "-y", "-nostdin", "-f", "concat", "-safe", "0",
                "-i", str(concat_file), "-c", "copy", str(combined)])
    concat_file.unlink(missing_ok=True)

    if not audio:
        combined.replace(out)
        return {"output_path": str(out), "clips_used": len(clips),
                "audio_tracks": 0, "transitions": transitions, "mock": False}

    result = add_audio(str(combined), audio, output=str(out), mock=mock)
    combined.unlink(missing_ok=True)
    result.update({"clips_used": len(clips), "audio_tracks": len(audio),
                   "transitions": transitions, "mock": False})
    return result


def full_pipeline(script: dict, clips_dir: str = "clips",
                  audio_dir: str = "tts", output: Optional[str] = None,
                  mock: bool = False) -> Dict:
    """Collect scene_<id>.mp4 / scene_<id>.wav by script scene id, then concatenate."""
    scenes = script.get("scenes", [])
    clips: List[str] = []
    audios: List[str] = []

    for scene in scenes:
        sid = scene["id"]
        clip = Path(clips_dir) / f"scene_{sid}.mp4"
        audio = Path(audio_dir) / f"scene_{sid}.wav"
        if clip.is_file() or mock:
            clips.append(str(clip))
        if audio.is_file() or mock:
            audios.append(str(audio))

    if not mock and not clips:
        sys.stderr.write(
            f"[ERROR] No scene_*.mp4 clips found under {clips_dir}; cannot concatenate.\n"
        )
        sys.exit(3)

    result = assemble_video(clips, audios, output=output, mock=mock)
    result["scenes"] = len(scenes)
    result["title"] = script.get("title", "untitled")
    return result


def main():
    parser = argparse.ArgumentParser(description="Video editor / assembler")
    parser.add_argument("--clips", nargs="*", help="Clip files to assemble")
    parser.add_argument("--audio", nargs="*", help="Audio files to mix")
    parser.add_argument("--script", help="Script JSON for full pipeline")
    parser.add_argument("--clips-dir", default="clips")
    parser.add_argument("--audio-dir", default="tts")
    parser.add_argument("--output", default="final_video.mp4")
    parser.add_argument("--transitions", nargs="*", help="Transition types")
    parser.add_argument("--mock", action="store_true",
                        help="only emit metadata, do not call ffmpeg (equivalent to SKILLKIT_MOCK=1)")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.script:
        if not Path(args.script).is_file():
            sys.stderr.write(f"[ERROR] Script file not found: {args.script}\n")
            sys.exit(3)
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = full_pipeline(script, args.clips_dir, args.audio_dir,
                               args.output, mock)
    elif args.clips:
        result = assemble_video(args.clips, args.audio, args.transitions,
                                args.output, mock)
    else:
        parser.error("Provide --script or --clips; when only --audio is given you must also give --clips as the video track")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
