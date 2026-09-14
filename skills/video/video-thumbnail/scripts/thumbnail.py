#!/usr/bin/env python3
"""Thumbnail Designer — 生成视频封面/缩略图。

默认**真实模式**：
  - `--video` 走 ffmpeg 抽帧；
  - 其余走用户自备的图像生成网关。
`--mock` 或环境变量 `SKILLKIT_MOCK=1` 时只输出布局元数据（不生成文件，仅供下游联调）。

真实模式下 ffmpeg / 网关缺失会打印指引并退出非 0，绝不静默返回假结果。
网关地址: `--gateway-url` > 环境变量 `GATEWAY_BASE_URL` > 仓库示例默认值。

用法:
  python3 thumbnail.py --video final.mp4 --output thumb.png
  python3 thumbnail.py --title "宝宝测评" --style funny --output cover.png
  python3 thumbnail.py --title "宝宝测评" --mock
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
    "  校验          : ffmpeg -version"
)

# 仓库示例默认值，不是任何厂商的公开端点承诺 —— 以你的实际部署为准
DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:30080"
GENERATE_PATH = "/v1/generate"

# 平台封面规格（2026 年常见值；发布前请核对平台最新规范）
PLATFORM_SPECS = {
    "douyin": {"width": 1080, "height": 1920, "ratio": "9:16", "max_size_kb": 2048},
    "bilibili": {"width": 1920, "height": 1080, "ratio": "16:9", "max_size_kb": 2048},
    "tiktok": {"width": 1080, "height": 1920, "ratio": "9:16", "max_size_kb": 2048},
    "youtube": {"width": 1280, "height": 720, "ratio": "16:9", "max_size_kb": 2048},
}


def mock_enabled(cli_mock: bool = False) -> bool:
    """`--mock` 显式开启，或环境变量 SKILLKIT_MOCK=1/true/yes/on；默认 False（真实模式）。"""
    if cli_mock:
        return True
    return os.environ.get("SKILLKIT_MOCK", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def require_tool(name: str, hint: str) -> None:
    if shutil.which(name):
        return
    sys.stderr.write(
        f"[ERROR] 真实模式需要外部工具 {name}，但 PATH 中未找到。\n"
        f"安装指引:\n  {hint}\n"
        f"若只需联调下游流程，可加 --mock（产物为占位，不会真实生成文件）。\n"
    )
    sys.exit(2)


def resolve_gateway(cli_url: Optional[str] = None) -> str:
    url = cli_url or os.environ.get("GATEWAY_BASE_URL") or DEFAULT_GATEWAY_BASE_URL
    return url.rstrip("/")


def probe_gateway(base_url: str) -> None:
    """探活：2xx/401/403/404 都说明服务在跑；连不上就给排查指引并退出非 0。"""
    try:
        urllib.request.urlopen(base_url + "/", timeout=5)
    except urllib.error.HTTPError:
        return
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] 无法连接图像生成网关: {base_url} （{e.__class__.__name__}: {e}）\n"
            f"排查步骤:\n"
            f"  1) 确认服务已启动: curl -sS -m 5 -o /dev/null -w '%{{http_code}}\\n' {base_url}/\n"
            f"  2) 确认地址正确  : export GATEWAY_BASE_URL=http://<host>:<port>  (不带尾斜杠)\n"
            f"  3) 若只需联调下游: 加 --mock 或 SKILLKIT_MOCK=1（产物为占位，不可交付）\n"
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
        sys.stderr.write(f"[ERROR] 网关返回 HTTP {e.code} {e.reason}\n响应体: {body}\n")
        sys.exit(4)
    except Exception as e:
        sys.stderr.write(
            f"[ERROR] 请求网关失败: {url} （{e.__class__.__name__}: {e}）\n"
            f"常见原因: 超时、限流（HTTP 429）、服务崩溃。\n"
        )
        sys.exit(4)


def _layout(spec: dict, style: str) -> dict:
    """封面文字布局参数（经验值；竖屏文字下移避让平台 UI）。"""
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
    """按平台规格生成封面（真实模式调用图像生成网关）。"""
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["douyin"])
    out = Path(output or f"thumbnail_{platform}.png")

    if mock:
        return {
            "output_path": str(out), "title": title, "style": style,
            "platform": platform, "spec": spec,
            "character_image": character_image,
            "layout": _layout(spec, style), "mock": True,
            "note": "Mock: 未调用网关，output_path 指向的文件不存在。",
        }

    base_url = resolve_gateway(gateway_url)
    if character_image and not Path(character_image).is_file():
        sys.stderr.write(f"[ERROR] 角色图不存在: {character_image}\n")
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
        sys.stderr.write(f"[ERROR] 网关返回空内容: {base_url}{GENERATE_PATH}\n")
        sys.exit(4)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    result = {"output_path": str(out), "title": title, "platform": platform,
              "spec": spec, "layout": _layout(spec, style), "mock": False}
    size_kb = out.stat().st_size / 1024
    if size_kb > spec["max_size_kb"]:
        sys.stderr.write(
            f"[WARN] 封面 {size_kb:.0f} KB 超过平台上限 {spec['max_size_kb']} KB，"
            f"请转 JPG 或降低质量后重导。\n"
        )
    return result


def extract_frame(video_path: str, timestamp: float = 0.5,
                  output: Optional[str] = None, mock: bool = False) -> Dict:
    """从视频抽一帧作为封面底图。"""
    out = Path(output or "thumb_frame.png")

    if mock:
        return {"output_path": str(out), "source": video_path,
                "timestamp": timestamp, "mock": True}

    require_tool("ffmpeg", FFMPEG_HINT)
    if not Path(video_path).is_file():
        sys.stderr.write(f"[ERROR] 视频文件不存在: {video_path}\n")
        sys.exit(3)

    # -ss 在 -i 之前 = 快速定位；片头常是黑场，默认 0.5s 可能仍偏早
    cmd = ["ffmpeg", "-y", "-nostdin", "-ss", str(timestamp), "-i", video_path,
           "-frames:v", "1", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(
            f"[ERROR] ffmpeg 抽帧失败 exit={proc.returncode}\n"
            f"命令: {' '.join(cmd)}\n"
        )
        sys.stderr.write((proc.stderr or "").strip()[-1500:] + "\n")
        sys.exit(proc.returncode or 1)
    if not out.is_file() or out.stat().st_size == 0:
        sys.stderr.write(f"[ERROR] 抽帧结果为空: {out}（试试把 --timestamp 调大）\n")
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
                        help="抽帧时间点（秒），避开片头黑场建议 >=1.0")
    parser.add_argument("--output", help="Output path")
    parser.add_argument("--gateway-url", help="网关根地址（默认取 GATEWAY_BASE_URL）")
    parser.add_argument("--mock", action="store_true",
                        help="只输出元数据不调用网关/ffmpeg（等价 SKILLKIT_MOCK=1）")
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
