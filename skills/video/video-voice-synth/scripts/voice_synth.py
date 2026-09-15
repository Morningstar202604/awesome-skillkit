#!/usr/bin/env python3
"""Video Voice Synthesis (TTS) — 文本转语音。

默认**真实模式**：调用用户自备的 TTS 网关真实产出音频。
`--mock` 或环境变量 `SKILLKIT_MOCK=1` 时生成静音 WAV 占位（仅供下游联调，不可交付）。

真实模式下网关不可达会打印排查指引并退出非 0，绝不静默返回假结果。
网关地址: `--gateway-url` > 环境变量 `GATEWAY_BASE_URL` > 仓库示例默认值。
端点路径与字段名以你的实际部署为准（VERIFY BEFORE USE）。

用法:
  python3 voice_synth.py --text "你好" --voice baby_f01
  python3 voice_synth.py --script script.json           # 批量
  python3 voice_synth.py --text "你好" --mock            # 静音占位
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

# 仓库示例默认值，不是任何厂商的公开端点承诺 —— 以你的实际部署为准
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
    """`--mock` 显式开启，或环境变量 SKILLKIT_MOCK=1/true/yes/on；默认 False（真实模式）。"""
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
        sys.stderr.write(f"[WARN] GATEWAY_TIMEOUT={raw!r} 不是整数，回退为 30。\n")
        return 30


def probe_gateway(base_url: str) -> None:
    """探活：2xx/401/403/404 都说明服务在跑；连不上就给排查指引并退出非 0。"""
    try:
        urllib.request.urlopen(base_url + "/", timeout=5)
    except urllib.error.HTTPError:
        return
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] 无法连接 TTS 网关: {base_url} （{e.__class__.__name__}: {e}）\n"
            f"排查步骤:\n"
            f"  1) 确认服务已启动: curl -sS -m 5 -o /dev/null -w '%{{http_code}}\\n' {base_url}/\n"
            f"  2) 确认地址正确  : export GATEWAY_BASE_URL=http://<host>:<port>  (不带尾斜杠)\n"
            f"  3) 若只需联调下游: 加 --mock 或 SKILLKIT_MOCK=1（产物是静音占位，不可交付）\n"
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
        sys.stderr.write(f"[ERROR] 网关返回 HTTP {e.code} {e.reason}\n响应体: {body}\n")
        sys.exit(4)
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] 请求网关失败: {url} （{e.__class__.__name__}: {e}）\n"
            f"常见原因: 超时（GATEWAY_TIMEOUT 调大）、限流（HTTP 429）、服务崩溃。\n"
        )
        sys.exit(4)


def _mock_synth(text: str, voice: str, output: Optional[str] = None) -> Dict[str, Any]:
    """生成静音 WAV 占位（时长按字数估算，纯下游联调用）。"""
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
        "note": "Mock: 静音占位，不可交付。",
    }


def synthesize_voice(text: str, voice: str = "baby_f01",
                     speed: Optional[float] = None, pitch: Optional[int] = None,
                     output: Optional[str] = None,
                     gateway_url: Optional[str] = None,
                     mock: bool = False) -> Dict[str, Any]:
    """生成 TTS 音频（真实网关 / mock 静音占位）。"""
    voice_conf = VOICES.get(voice, {"pitch": 0, "speed": 1.0})
    speed = speed or voice_conf["speed"]
    pitch = pitch if pitch is not None else voice_conf["pitch"]

    if mock:
        return _mock_synth(text, voice, output)

    if not text.strip():
        sys.stderr.write("[ERROR] 待合成文本为空。\n")
        sys.exit(3)

    base_url = resolve_gateway(gateway_url)
    probe_gateway(base_url)
    payload = {
        "text": text, "voice": voice,
        "speed": speed, "pitch": pitch, "format": "wav",
    }
    audio = post_json(base_url + TTS_PATH, payload, gateway_timeout())
    if not audio:
        sys.stderr.write(f"[ERROR] 网关返回空音频: {base_url}{TTS_PATH}\n")
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
    """按脚本场景批量合成。

    audio_dir: 场景音频输出目录（下游 lip_sync --audio-dir 与 editor
    --audio-dir 依赖同一目录下的 scene_<id>.wav 命名契约）。
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
    parser.add_argument("--gateway-url", help="网关根地址（默认取 GATEWAY_BASE_URL）")
    parser.add_argument("--mock", action="store_true",
                        help="生成静音占位，不调用网关（等价 SKILLKIT_MOCK=1）")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.script:
        if not Path(args.script).is_file():
            sys.stderr.write(f"[ERROR] 脚本文件不存在: {args.script}\n")
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
