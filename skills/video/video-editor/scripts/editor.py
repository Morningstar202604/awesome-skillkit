#!/usr/bin/env python3
"""Video Editor — 视频剪辑/合成/转场/混音。

默认**真实模式**：调用 ffmpeg 真实产出文件。
`--mock` 或环境变量 `SKILLKIT_MOCK=1` 时只输出元数据（不生成文件，仅供下游联调）。

真实模式下 ffmpeg 缺失会打印安装指引并退出非 0，绝不静默返回假结果。

用法:
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
    "  校验          : ffmpeg -version"
)


def mock_enabled(cli_mock: bool = False) -> bool:
    """`--mock` 显式开启，或环境变量 SKILLKIT_MOCK=1/true/yes/on；默认 False（真实模式）。"""
    if cli_mock:
        return True
    return os.environ.get("SKILLKIT_MOCK", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def require_tool(name: str, hint: str) -> None:
    """真实模式依赖的外部工具必须存在，否则给安装指引并退出非 0。"""
    if shutil.which(name):
        return
    sys.stderr.write(
        f"[ERROR] 真实模式需要外部工具 {name}，但 PATH 中未找到。\n"
        f"安装指引:\n  {hint}\n"
        f"若只需联调下游流程，可加 --mock（产物为占位，不会真实生成文件）。\n"
    )
    sys.exit(2)


def run_ffmpeg(cmd: List[str]) -> None:
    """执行 ffmpeg；失败时打印完整命令与 stderr 并退出非 0。"""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(
            f"[ERROR] ffmpeg 执行失败 exit={proc.returncode}\n"
            f"命令: {' '.join(cmd)}\n"
        )
        sys.stderr.write((proc.stderr or "").strip()[-1500:] + "\n")
        sys.exit(proc.returncode or 1)


def _has_audio_stream(path: str) -> bool:
    """用 ffprobe 判断文件是否含音轨（决定混音时能不能拿 [0:a]）。"""
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return bool(proc.stdout.strip())


def _write_concat_list(clips: List[str], concat_file: Path) -> None:
    """concat demuxer 清单；路径统一转成绝对路径并配合 -safe 0 使用。"""
    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{Path(clip).resolve()}'\n")


def add_audio(video: str, audio: List[str], output: Optional[str] = None,
              mock: bool = False) -> Dict:
    """把 audio（1 条或多条）混到 video 上，输出新文件。"""
    out = Path(output or str(Path(video).with_name(Path(video).stem + "_mixed.mp4")))

    if mock:
        return {"output_path": str(out), "video": video,
                "audio": audio, "mock": True}

    require_tool("ffmpeg", FFMPEG_HINT)
    for path in [video] + list(audio):
        if not Path(path).is_file():
            sys.stderr.write(f"[ERROR] 输入文件不存在: {path}\n")
            sys.exit(3)

    cmd: List[str] = ["ffmpeg", "-y", "-nostdin", "-i", video] + \
        sum([["-i", a] for a in audio], [])
    # 视频自带音轨时一起混，否则只挂外部音频
    own = _has_audio_stream(video)
    labels = (["0:a"] if own else []) + [f"{i}:a" for i in range(1, len(audio) + 1)]
    if not labels:
        sys.stderr.write("[ERROR] 没有可混音的音频输入。\n")
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
    """拼接片段；给了 audio 就顺带混音。"""
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
            "note": "Mock: 未调用 ffmpeg，output_path 指向的文件不存在。",
        }

    require_tool("ffmpeg", FFMPEG_HINT)
    if not clips:
        sys.stderr.write("[ERROR] --clips 为空，没有可拼接的输入。\n")
        sys.exit(3)
    missing = [c for c in clips if not Path(c).is_file()]
    if missing:
        sys.stderr.write("[ERROR] 以下片段不存在: " + ", ".join(missing) + "\n")
        sys.exit(3)
    if any(t and t != "cut" for t in transitions):
        sys.stderr.write(
            f"[WARN] 转场 {transitions} 在真实模式尚未实现，本次按 cut（硬切）拼接。\n"
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
    """按脚本场景号收集 scene_<id>.mp4 / scene_<id>.wav，再拼接。"""
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
            f"[ERROR] 在 {clips_dir} 下没有找到任何 scene_*.mp4 片段，无法拼接。\n"
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
                        help="只输出元数据不调用 ffmpeg（等价 SKILLKIT_MOCK=1）")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.script:
        if not Path(args.script).is_file():
            sys.stderr.write(f"[ERROR] 脚本文件不存在: {args.script}\n")
            sys.exit(3)
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = full_pipeline(script, args.clips_dir, args.audio_dir,
                               args.output, mock)
    elif args.clips:
        result = assemble_video(args.clips, args.audio, args.transitions,
                                args.output, mock)
    else:
        parser.error("需要 --script 或 --clips；仅给 --audio 时也必须给 --clips 作为视频轨")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
