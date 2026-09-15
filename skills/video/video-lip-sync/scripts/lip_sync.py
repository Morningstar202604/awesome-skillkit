#!/usr/bin/env python3
"""Lip Sync — 将角色口型与语音同步。

默认**真实模式**：调用用户自备的 lip-sync 网关真实产出视频。
`--mock` 或环境变量 `SKILLKIT_MOCK=1` 时只输出元数据（不生成文件，仅供下游联调）。

真实模式下网关不可达会打印排查指引并退出非 0，绝不静默返回假结果。
网关地址: `--gateway-url` > 环境变量 `GATEWAY_BASE_URL` > 仓库示例默认值。
端点路径与字段名以你的实际部署为准（VERIFY BEFORE USE）。

用法:
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

# 仓库示例默认值，不是任何厂商的公开端点承诺 —— 以你的实际部署为准
DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:30081"
LIPSYNC_PATH = "/v1/lipsync"


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
    raw = os.environ.get("GATEWAY_TIMEOUT", "120").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        sys.stderr.write(f"[WARN] GATEWAY_TIMEOUT={raw!r} 不是整数，回退为 120。\n")
        return 120


def require_file(path: str, what: str) -> None:
    if not Path(path).is_file():
        sys.stderr.write(f"[ERROR] {what}不存在: {path}\n")
        sys.exit(3)


def probe_gateway(base_url: str) -> None:
    """探活：2xx/401/403/404 都说明服务在跑；连不上就给排查指引并退出非 0。"""
    try:
        urllib.request.urlopen(base_url + "/", timeout=5)
    except urllib.error.HTTPError:
        return  # 401/403/404 = 服务在跑，只是路径或鉴权问题
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] 无法连接 lip-sync 网关: {base_url} （{e.__class__.__name__}: {e}）\n"
            f"排查步骤:\n"
            f"  1) 确认服务已启动: curl -sS -m 5 -o /dev/null -w '%{{http_code}}\\n' {base_url}/\n"
            f"  2) 确认地址正确  : export GATEWAY_BASE_URL=http://<host>:<port>  (不带尾斜杠)\n"
            f"  3) 若只需联调下游: 加 --mock 或 SKILLKIT_MOCK=1（产物为占位，不可交付）\n"
        )
        sys.exit(4)


def post_json(url: str, payload: dict, timeout: int) -> bytes:
    """POST JSON；任何失败都打印原因并退出非 0。"""
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


def lip_sync(face_image: str, audio_path: str, output: Optional[str] = None,
             mouth_width: int = 40, mouth_height: int = 30,
             gateway_url: Optional[str] = None, mock: bool = False) -> Dict:
    """由角色图 + 音频生成口型同步视频。"""
    out = Path(output or f"lipsync_{Path(audio_path).stem}.mp4")

    if mock:
        return {
            "output_path": str(out),
            "face_image": face_image,
            "audio_path": audio_path,
            "mock": True,
            "mouth_params": {"width": mouth_width, "height": mouth_height},
            "note": "Mock: 未调用网关，output_path 指向的文件不存在。",
        }

    base_url = resolve_gateway(gateway_url)
    require_file(face_image, "角色图")
    require_file(audio_path, "音频文件")
    probe_gateway(base_url)

    payload = {
        "face_image": face_image,
        "audio_path": audio_path,
        "mouth_width": mouth_width,
        "mouth_height": mouth_height,
    }
    video = post_json(base_url + LIPSYNC_PATH, payload, gateway_timeout())
    if not video:
        sys.stderr.write(f"[ERROR] 网关返回空内容: {base_url}{LIPSYNC_PATH}\n")
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
    """按脚本场景批量口型同步。"""
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
            "[ERROR] 以下场景音频缺失，真实模式无法处理: " + ", ".join(missing) + "\n"
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
                        help="网关根地址（默认取 GATEWAY_BASE_URL）")
    parser.add_argument("--mock", action="store_true",
                        help="只输出元数据不调用网关（等价 SKILLKIT_MOCK=1）")
    args = parser.parse_args()
    mock = mock_enabled(args.mock)

    if args.script:
        require_file(args.script, "脚本文件")
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
