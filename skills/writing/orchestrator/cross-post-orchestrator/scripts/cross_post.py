#!/usr/bin/env python3
"""cross_post.py - 一篇文章多平台发布编排器。

定位：规划器 + 调度器。它不重复实现各平台逻辑，而是：
  1. 读取一份 post.manifest.json（标题、正文、目标平台列表）
  2. `plan`   —— 检查每个平台的前置条件（凭据/账号文件是否就绪），
                 输出执行计划；这是默认行为，绝不联网
  3. `run`    —— 对已有脚本化适配器的平台，调用对应技能的 CLI
                 （wechat_mp_publish.py / juejin_publish.py），且同样
                 遵守对方"默认 dry-run、--execute 才发送"的约定；
                 无脚本的平台（cnblogs/zhihu）输出精确的手工执行清单
  4. `ledger` —— 查看发布台账

用法：
  python cross_post.py plan   --manifest post.manifest.json
  python cross_post.py run    --manifest post.manifest.json [--only wechat_mp]
  python cross_post.py ledger --manifest post.manifest.json

退出码：0 全部就绪/完成；1 配置错误；2 存在需要人工介入的平台。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# 复用发布公共工具（JSON 读写），避免重复造轮子
_common = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "_common"
    )
)
if os.path.isdir(_common) and _common not in sys.path:
    sys.path.insert(0, _common)
from publish_common import load_json, dump_json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 各平台对应的兄弟技能脚本（相对本文件）
ADAPTERS = {
    "wechat_mp": (
        "../wechat/wechat-mp-publisher/scripts/wechat_mp_publish.py",
        ["--title", "{title}"],
    ),
}
SUPPORTED_PLATFORMS = ("wechat_mp", "juejin", "cnblogs", "zhihu")


# ---------- 纯函数（可单测） ----------


def load_manifest(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError("manifest 不存在: %s" % path)
    m = load_json(path)
    for key in ("title", "markdown", "targets"):
        if key not in m:
            raise ValueError("manifest 缺少必填字段: %s" % key)
    for t in m["targets"]:
        if t.get("platform") not in SUPPORTED_PLATFORMS:
            raise ValueError(
                "不支持的平台: %r（支持：%s）"
                % (t.get("platform"), ",".join(SUPPORTED_PLATFORMS))
            )
    return m


def check_readiness(platform: str, manifest_dir: str) -> tuple[bool, str]:
    """返回 (ready, 说明)。只做本地检查，不联网。"""
    if platform == "wechat_mp":
        ok = bool(
            os.environ.get("WECHAT_MP_APPID") and os.environ.get("WECHAT_MP_SECRET")
        )
        return ok, "环境变量 WECHAT_MP_APPID / WECHAT_MP_SECRET"
    if platform == "juejin":
        return bool(os.environ.get("JUEJIN_COOKIE")), "环境变量 JUEJIN_COOKIE"
    if platform == "cnblogs":
        acct = os.path.join(
            manifest_dir,
            "..",
            "..",
            "blog",
            "cnblogs-skill",
            "references",
            "account.local.json",
        )
        return os.path.exists(acct), "cnblogs-skill references/account.local.json"
    if platform == "zhihu":
        state = os.environ.get("ZHIHU_STATE_FILE", "zhihu_state.json")
        return os.path.exists(state), "知乎登录态文件 %s（当前目录）" % state
    return False, "未知平台"


def build_plan(manifest: dict, manifest_dir: str) -> list[dict]:
    plan = []
    md_path = os.path.join(manifest_dir, manifest["markdown"])
    md_exists = os.path.exists(md_path)
    for t in manifest["targets"]:
        if not t.get("enabled", True):
            plan.append(
                {
                    "platform": t["platform"],
                    "status": "skipped",
                    "detail": "manifest 中已禁用",
                }
            )
            continue
        ready, why = check_readiness(t["platform"], manifest_dir)
        status = (
            "blocked-md-missing"
            if not md_exists
            else ("ready" if ready else "missing-credentials")
        )
        plan.append({"platform": t["platform"], "status": status, "detail": why})
    return plan


def render_plan(plan: list[dict]) -> str:
    lines = ["%-14s %-22s %s" % ("平台", "状态", "说明"), "-" * 64]
    for p in plan:
        lines.append("%-14s %-22s %s" % (p["platform"], p["status"], p["detail"]))
    return "\n".join(lines)


def manual_checklist(platform: str, title: str) -> str:
    if platform == "cnblogs":
        return (
            "cnblogs：无独立脚本适配器。按 cnblogs-skill 的 references/publish-api.md "
            "API 流程发文（Cookie+XSRF→POST i.cnblogs.com/api/posts），"
            "发布前运行其 pre-publish-check。"
        )
    if platform == "zhihu":
        return (
            "zhihu：浏览器自动化流程。调用 zhihu-content-manager 技能："
            "/write 页注入 HTML → 发布 → lint 校验。登录态缺失时先人工登录导出 "
            "zhihu_state.json。"
        )
    return ""


def append_ledger(ledger_file: str, entry: dict) -> None:
    ledger = []
    if os.path.exists(ledger_file):
        ledger = load_json(ledger_file)
    entry["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ledger.append(entry)
    with open(ledger_file, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=2)


def adapter_script(platform: str) -> str | None:
    rel = ADAPTERS.get(platform, (None,))[0]
    if not rel:
        return None
    path = os.path.normpath(os.path.join(SCRIPT_DIR, rel))
    return path if os.path.exists(path) else None


# ---------- 命令 ----------


def cmd_plan(args):
    manifest = load_manifest(args.manifest)
    plan = build_plan(manifest, os.path.dirname(os.path.abspath(args.manifest)))
    print(render_plan(plan))
    blocked = [
        p for p in plan if p["status"] in ("missing-credentials", "blocked-md-missing")
    ]
    return 1 if blocked else 0


def cmd_run(args):
    manifest = load_manifest(args.manifest)
    manifest_dir = os.path.dirname(os.path.abspath(args.manifest))
    targets = [
        t
        for t in manifest["targets"]
        if t.get("enabled", True) and (not args.only or t["platform"] == args.only)
    ]
    needs_human = False
    for t in targets:
        platform = t["platform"]
        script = adapter_script(platform)
        if script is None:
            print(
                "[MANUAL] %s\n  %s"
                % (platform, manual_checklist(platform, manifest["title"]))
            )
            needs_human = True
            continue
        cmd = [sys.executable, script, "--execute"]
        if platform == "wechat_mp":
            html_path = os.path.join(manifest_dir, "article.html")
            thumb = t.get("thumb_media_id", "")
            if not (os.path.exists(html_path) and thumb):
                print("[SKIP] wechat_mp 需要 article.html 与 thumb_media_id")
                continue
            cmd += [
                "add-draft",
                "--title",
                manifest["title"],
                "--content-html",
                html_path,
                "--thumb-media-id",
                thumb,
            ]
        elif platform == "juejin":
            md_path = os.path.join(manifest_dir, manifest["markdown"])
            cmd = [
                sys.executable,
                script,
                "publish",
                t.get("article_id", "0"),
                "--title",
                manifest["title"],
                "--markdown-file",
                md_path,
                "--category-id",
                str(t.get("category_id", "6809637773934372878")),
                "--tag-ids",
                ",".join(t.get("tag_ids", [])),
            ]
        print("[RUN]", " ".join(cmd[:6]), "...")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print("[FAIL] %s 退出码 %d" % (platform, result.returncode))
        else:
            append_ledger(
                os.path.join(
                    manifest_dir, manifest.get("ledger_file", "published.ledger.json")
                ),
                {"platform": platform, "title": manifest["title"], "status": "ok"},
            )
    return 2 if needs_human else 0


def cmd_ledger(args):
    manifest = load_manifest(args.manifest)
    lf = os.path.join(
        os.path.dirname(os.path.abspath(args.manifest)),
        manifest.get("ledger_file", "published.ledger.json"),
    )
    if not os.path.exists(lf):
        print("台账为空:", lf)
        return 0
    print(dump_json(load_json(lf)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="多平台发布编排器")
    ap.add_argument("--manifest", required=True, help="post.manifest.json 路径")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("run")
    p.add_argument("--only", default="", help="只跑指定平台")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("ledger")
    p.set_defaults(fn=cmd_ledger)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
