#!/usr/bin/env python3
"""generate_cover.py - 技术文章封面图生成（对接本地图片服务）。

服务契约（与本地 ai-image-gen 服务一致）：
  提交:  POST http://127.0.0.1:30080/api/image/generate
         {"model":"gpt-image-2","prompt":"...","params":{"size":..,"quality":..,"n":1}}
         → 响应含 task_id
  轮询:  GET  /api/image/status?task_id=...
         is_final=true 且 state=="success" 时 result_url 可下载
  下载:  GET result_url → 保存本地；可选 PIL 压缩为 JPG(<1MB) 供平台上传

安全设计：
  - 默认 dry-run：只打印请求计划；--execute 才提交任务
  - 服务不可达时明确报错退出（exit 1），绝不伪造成功输出

用法：
  python generate_cover.py --prompt "..." [--size 1792x1024] [--out cover.png]
                           [--execute] [--timeout 180]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

# 复用发布公共工具（HTTP / 异常 / dry-run），避免重复造轮子
_common = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "_common"
    )
)
if os.path.isdir(_common) and _common not in sys.path:
    sys.path.insert(0, _common)
from publish_common import http_json, PublishError, dry_run_guard, dump_json

DEFAULT_BASE = os.environ.get("IMAGE_API_BASE", "http://127.0.0.1:30080")

# 尺寸约束（来自服务端规则）：宽高为16的倍数、宽高比1:3~3:1、总像素655360~8294400


def validate_size(size: str) -> str:
    try:
        w, h = (int(x) for x in size.lower().split("x"))
    except ValueError:
        raise ValueError("尺寸格式应为 WxH，如 1792x1024")
    if w % 16 or h % 16:
        raise ValueError("宽高必须是 16 的倍数: %s" % size)
    ratio = max(w, h) / min(w, h)
    if ratio > 3:
        raise ValueError("宽高比超出 1:3~3:1: %s" % size)
    if not (655360 <= w * h <= 8294400):
        raise ValueError("总像素超出 655360~8294400: %s (%d)" % (size, w * h))
    return "%dx%d" % (w, h)


def build_generate_payload(prompt: str, size: str, quality: str) -> dict:
    return {
        "model": "gpt-image-2",
        "prompt": prompt,
        "params": {"size": validate_size(size), "quality": quality, "n": 1},
    }


def extract_task_id(data: dict) -> str:
    """容错解析 task_id：支持 {task_id} / {data:{task_id}} / {data:{task:{id}}}。"""
    if isinstance(data.get("task_id"), (str, int)):
        return str(data["task_id"])
    d = data.get("data") or {}
    if isinstance(d, dict):
        if isinstance(d.get("task_id"), (str, int)):
            return str(d["task_id"])
        task = d.get("task")
        if isinstance(task, dict) and task.get("id"):
            return str(task["id"])
    raise ValueError(
        "响应中未找到 task_id，原始内容：%s"
        % json.dumps(data, ensure_ascii=False)[:200]
    )


def poll_should_stop(status: dict) -> tuple[bool, str | None]:
    """返回 (是否结束, result_url 或 None)。"""
    if status.get("is_final"):
        if status.get("state") == "success":
            url = status.get("result_url") or (status.get("data") or {}).get(
                "result_url"
            )
            return True, url
        return True, None
    return False, None


def compress_to_jpg(src: str, dst: str, max_bytes: int = 1024 * 1024) -> str:
    """PIL 压缩到 <max_bytes（可选依赖：无 PIL 时原样返回并提示）。"""
    try:
        from PIL import Image
    except ImportError:
        print("[warn] 未安装 Pillow，跳过压缩（平台上传前请自行压缩）")
        return src
    img = Image.open(src).convert("RGB")
    quality = 90
    while quality >= 50:
        img.save(dst, "JPEG", quality=quality)
        if os.path.getsize(dst) <= max_bytes:
            return dst
        quality -= 10
    return dst


def main(argv=None):
    ap = argparse.ArgumentParser(description="技术文章封面图生成（默认 dry-run）")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--size", default="1792x1024")
    ap.add_argument(
        "--quality", default="auto", choices=["auto", "high", "medium", "low"]
    )
    ap.add_argument("--out", default="cover.png")
    ap.add_argument("--jpg", action="store_true", help="额外压缩出 JPG 版本")
    ap.add_argument("--execute", action="store_true", help="真正提交任务")
    ap.add_argument("--timeout", type=int, default=180, help="轮询超时秒数")
    args = ap.parse_args(argv)

    try:
        payload = build_generate_payload(args.prompt, args.size, args.quality)
    except ValueError as exc:
        print("[error] %s" % exc)
        return 1

    if not dry_run_guard(args.execute):
        print("[PLAN] POST %s/api/image/generate" % DEFAULT_BASE)
        print(dump_json(payload))
        return 0

    # 1. 提交任务
    try:
        resp = http_json("%s/api/image/generate" % DEFAULT_BASE, payload=payload)
    except PublishError as exc:
        print("[error] 图片服务不可达（127.0.0.1:30080）：%s" % exc)
        return 1
    task_id = extract_task_id(resp)
    print("[task] %s 已提交，开始轮询…" % task_id)

    # 2. 轮询
    deadline = time.time() + args.timeout
    result_url = None
    while time.time() < deadline:
        time.sleep(4)
        status = http_json("%s/api/image/status?task_id=%s" % (DEFAULT_BASE, task_id))
        stop, result_url = poll_should_stop(status)
        if stop:
            break
        print("  …生成中")
    if not result_url:
        print("[error] 超时或失败（%ds）" % args.timeout)
        return 1

    # 3. 下载
    urllib.request.urlretrieve(result_url, args.out)
    size_kb = os.path.getsize(args.out) // 1024
    print("[done] %s (%d KB)" % (args.out, size_kb))

    # 4. 可选 JPG 压缩
    if args.jpg:
        jpg = os.path.splitext(args.out)[0] + ".jpg"
        final = compress_to_jpg(args.out, jpg)
        print("[done] %s (%d KB)" % (final, os.path.getsize(final) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
