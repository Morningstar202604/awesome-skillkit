#!/usr/bin/env python3
"""drive_ops.py -- 云盘归档的上传计划器、校验清单生成器与列表解析器。

适用于百度网盘 / 阿里云盘 / OneDrive 这类"分片上传 + 秒传"的云盘。
本脚本只做三件**离线**的事：算清楚要传什么、留下校验依据、把响应读成人话。

设计原则
--------
1. **纯函数 + 只读**：`plan-upload` / `checksum-plan` 只读本地目录，
   `parse-list` 只读 JSON 文件。三者都不联网、不写远端。
2. **默认 dry-run**：`plan-upload` 输出的是计划而非动作；真实上传由人确认后执行。
3. **凭证不落盘**：access_token / client_secret 一律从环境变量读取
   （BAIDU_ACCESS_TOKEN / ALIYUN_REFRESH_TOKEN / ONEDRIVE_ACCESS_TOKEN），
   脚本内部从不接触这些值。
4. **删除必须双重确认**：`parse-list` 遇到删除类结果会额外报警示；
   真实删除操作要求用户分别确认"目标路径"与"影响文件数"两次。

子命令
------
  plan-upload   --dir X --remote Y [--prefix P] [--manifest m.json]
  checksum-plan --dir X [--output sha256.txt] [--algo sha256|md5] [--exclude GLOB]
  parse-list    --json f.json [--provider {baidu|aliyun|onedrive}]

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# 云盘平台常量
# ---------------------------------------------------------------------------

# 分片上传的阈值与片大小。三家都提供"简单上传"与"分片上传"两条路径，
# 阈值不同；超过阈值还走简单上传会被直接拒绝。
CHUNK_POLICY = {
    "baidu": {
        "simple_max_mb": 4,      # 4MB 以下走简单上传
        "chunk_mb": 4,           # 分片固定 4MB（平台约定）
        "slice_threshold_mb": 4,
        "note": "百度网盘的 uploadid 接口对超 4MB 文件强制分片，片大小必须是 4MB",
    },
    "aliyun": {
        "simple_max_mb": 100,
        "chunk_mb": 8,
        "slice_threshold_mb": 100,
        "note": "阿里云盘 100MB 以下可单请求上传；以上建议 8MB 分片",
    },
    "onedrive": {
        "simple_max_mb": 250,    # 单请求上传上限 250MB
        "chunk_mb": 10,          # 分片必须是 320KiB 的整数倍，10MB 满足
        "slice_threshold_mb": 250,
        "note": "OneDrive 单请求上传上限 250MB，分片必须为 320KiB 的倍数",
    },
}

# 秒传（instant upload）的原理说明：客户端先算文件内容哈希，
# 服务端若有相同哈希的**整文件**记录则直接建立引用，不传字节。
HASH_ALGO = {
    "baidu": "md5（分片上传时每片单独算 md5，外加整文件 md5 用于秒传）",
    "aliyun": "sha1 + 分段 sha1（阿里云盘用 sha1 而非 md5 做去重键）",
    "onedrive": "quickXorHash（微软自有算法）或 sha256（取决于 API 版本）",
}

# 各家列表响应里"条目数组"的字段名不同。
LIST_KEY = {"baidu": "list", "aliyun": "items", "onedrive": "value"}

# 删除操作的双重确认要求（写进输出，强制使用者看见）。
DELETE_CONFIRM = (
    "删除是不可逆操作：请分两次确认——"
    "① 确认目标路径完全正确；② 确认受影响的文件数量与预期一致。"
    "任一项存疑请改用移动/归档目录，不要删除。"
)

SUPPORTED_ALGOS = ("sha256", "md5", "sha1")


class PlanError(Exception):
    """计划生成失败（输入不合法，非网络问题）。"""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    p = Path(path)
    if not p.is_file():
        raise PlanError(f"{what} 文件不存在: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PlanError(f"{what} 不是合法 JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def fmt_size(n: int) -> str:
    """人类可读体积：B 不带小数，其余保留一位。"""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{int(size)}B" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


# ---------------------------------------------------------------------------
# plan-upload
# ---------------------------------------------------------------------------
def collect_files(root: Path, prefix: str, exclude: list) -> list:
    """遍历目录收集待传文件。

    **跳过符号链接**：跟随链接会让"上传 A 目录"意外把 B 目录的
    大文件也传上去，配额与隐私都不可控。
    """
    if not root.is_dir():
        raise PlanError(f"不是目录: {root}")
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(p.name, pat)
               for pat in exclude):
            continue
        if prefix:
            rel = f"{prefix.rstrip('/')}/{rel}"
        out.append((p, rel))
    return out


def decide_strategy(provider: str, size: int) -> dict:
    """按平台阈值决定简单上传还是分片上传。"""
    pol = CHUNK_POLICY[provider]
    mb = size / (1024 * 1024)
    if mb <= pol["simple_max_mb"]:
        return {"mode": "simple", "chunks": 1, "chunk_size_mb": None}
    chunk_mb = pol["chunk_mb"]
    chunk_bytes = chunk_mb * 1024 * 1024
    chunks = (size + chunk_bytes - 1) // chunk_bytes
    return {"mode": "slice", "chunks": chunks, "chunk_size_mb": chunk_mb}


def build_manifest(root: Path, remote: str, provider: str,
                   files: list) -> dict:
    """生成上传计划（manifest）：文件清单 + 体积 + 目标路径 + 策略。"""
    entries = []
    total = 0
    for path, rel in files:
        size = path.stat().st_size
        total += size
        entries.append({
            "local": str(path),
            "relative": rel,
            "size": size,
            "size_human": fmt_size(size),
            "remote_path": f"{remote.rstrip('/')}/{rel}",
            **decide_strategy(provider, size),
        })
    return {
        "provider": provider,
        "source_dir": str(root.resolve()),
        "remote_root": remote,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file_count": len(entries),
        "total_bytes": total,
        "total_human": fmt_size(total),
        "will_create_dirs": sorted({
            str(Path(e["remote_path"]).parent) for e in entries
        }),
        "files": entries,
    }


def cmd_plan_upload(args) -> int:
    exclude = [x.strip() for x in (args.exclude or "").split(",") if x.strip()]
    root = Path(args.dir)
    files = collect_files(root, args.prefix or "", exclude)

    print(f"# DRY-RUN：上传计划（未上传任何文件）")
    print(f"# 源目录：{root.resolve()}")
    print(f"# 目标云盘：{args.provider}  远端根路径：{args.remote}")
    print(f"# 凭证：从环境变量读取，不落盘、不打印")
    print()

    if not files:
        # 空清单不是成功：没有可上传的文件意味着这次归档什么都不会发生，
        # 直接返回 0 会让调用方误以为"计划已就绪"。返回非 0 并写明原因，
        # 让流水线在这里就停下（否则会带着空计划走到上传步骤才发现）。
        return _die(
            f"目录 {root.resolve()} 内没有可上传的文件（或全部被 --exclude 排除）。"
            "请核对源目录路径与 --exclude 通配符是否过宽。"
        )

    manifest = build_manifest(root, args.remote, args.provider, files)

    print(f"共 {manifest['file_count']} 个文件，合计 {manifest['total_human']}")
    print()
    print("## 文件清单")
    print(f"{'相对路径':<48}{'大小':>10}  {'策略'}")
    for e in manifest["files"]:
        strategy = "simple" if e["mode"] == "simple" else \
            f"slice x{e['chunks']} ({e['chunk_size_mb']}MB/片)"
        rel = e["relative"]
        if len(rel) > 46:
            rel = "..." + rel[-43:]
        print(f"{rel:<48}{e['size_human']:>10}  {strategy}")
    print()

    print("## 将创建的远端目录")
    for d in manifest["will_create_dirs"]:
        print(f"  {d}/")
    print()

    print("## 分片策略依据")
    pol = CHUNK_POLICY[args.provider]
    print(f"- {pol['note']}")
    print(f"- 秒传/去重键算法：{HASH_ALGO[args.provider]}")
    print()

    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"# manifest 已写入 {args.manifest}")
    print("# 未上传任何文件。确认清单后由 AI/用户接凭证执行上传；")
    print("# 上传完成后用 checksum-plan 的结果逐文件比对，验证完整性。")
    return 0


# ---------------------------------------------------------------------------
# checksum-plan
# ---------------------------------------------------------------------------
def hash_file(path: Path, algo: str, block: int = 1 << 20) -> str:
    """流式计算文件摘要，不整文件读进内存。"""
    h = hashlib.new(algo)
    with path.open("rb") as fh:
        while True:
            buf = fh.read(block)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def cmd_checksum_plan(args) -> int:
    algo = args.algo
    if algo not in SUPPORTED_ALGOS:
        return _die(f"不支持的算法 '{algo}'；用 {', '.join(SUPPORTED_ALGOS)}")

    exclude = [x.strip() for x in (args.exclude or "").split(",") if x.strip()]
    root = Path(args.dir)
    if not root.is_dir():
        return _die(f"不是目录: {root}")

    files = collect_files(root, "", exclude)
    if not files:
        # 同 plan-upload：算不出任何摘要不是成功，而是"源目录选错了或全被排除"。
        # 返回 0 会让调用方把空清单当成有效的校验基准，后续 sha256sum -c 会
        # 以 0 行全部通过而掩盖真实问题。
        return _die(
            f"目录 {root.resolve()} 内没有可计算的文件（或全部被 --exclude 排除）。"
            "请核对源目录路径与 --exclude 通配符。"
        )

    lines = []
    total = 0
    for path, rel in files:
        digest = hash_file(path, algo)
        size = path.stat().st_size
        total += size
        # 采用 `hash  *path` 两空格格式：二进制模式标记，便于 sha256sum -c 直接校验
        lines.append(f"{digest}  {rel}")

    header = [
        f"# {algo} 校验清单",
        f"# 源目录: {root.resolve()}",
        f"# 生成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"# 文件数: {len(files)}  合计: {fmt_size(total)}",
        f"# 校验方式: {algo}sum -c <本文件>",
        "",
    ]
    text = "\n".join(header + lines) + "\n"

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"# 已写入 {args.output}")
        print(f"# 算法：{algo}  文件数：{len(files)}  合计：{fmt_size(total)}")
        print(f"# 校验命令：{algo}sum -c {args.output}")
    else:
        sys.stdout.write(text)
    return 0


# ---------------------------------------------------------------------------
# parse-list
# ---------------------------------------------------------------------------
def _norm_entry(provider: str, item: dict) -> dict:
    """把三家列表条目的字段名归一成 (name, size, is_dir, mtime, id)。

    三家的字段名完全不同，且 OneDrive 用 `folder`/`file` 子对象区分类型，
    百度用 `isdir` 整数，阿里用 `type` 字符串。
    """
    if provider == "baidu":
        return {
            "name": Path(item.get("path", "")).name or item.get("server_filename", ""),
            "path": item.get("path", ""),
            "size": item.get("size", 0),
            "is_dir": item.get("isdir") == 1,
            "mtime": item.get("server_mtime", 0),
            "id": item.get("fs_id", ""),
        }
    if provider == "aliyun":
        return {
            "name": item.get("name", ""),
            "path": item.get("path", ""),
            "size": item.get("size", 0),
            "is_dir": item.get("type", "") == "folder",
            "mtime": item.get("updated_at", ""),
            "id": item.get("file_id", ""),
        }
    # onedrive
    is_dir = "folder" in item
    return {
        "name": item.get("name", ""),
        "path": (item.get("parentReference") or {}).get("path", ""),
        "size": (item.get("size", 0) if not is_dir else 0),
        "is_dir": is_dir,
        "mtime": item.get("lastModifiedDateTime", ""),
        "id": item.get("id", ""),
    }


def cmd_parse_list(args) -> int:
    raw = _load_json(args.json, "--json")
    provider = args.provider

    if isinstance(raw, dict):
        items = raw.get(LIST_KEY[provider]) or raw.get("files") or []
    elif isinstance(raw, list):
        items = raw
    else:
        return _die("--json 必须是列表响应对象或条目数组")

    if not items:
        print(f"# {provider} 列表：0 个条目")
        return 0

    entries = [_norm_entry(provider, it) for it in items]
    dirs = [e for e in entries if e["is_dir"]]
    files = [e for e in entries if not e["is_dir"]]
    total = sum(e["size"] for e in files)

    print(f"# {provider} 目录列表：{len(entries)} 个条目"
          f"（目录 {len(dirs)}，文件 {len(files)}，文件合计 {fmt_size(total)}）")
    print()
    print(f"{'类型':<6}{'名称':<40}{'大小':>10}  标识")
    for e in sorted(entries, key=lambda x: (not x["is_dir"], x["name"])):
        kind = "DIR" if e["is_dir"] else "FILE"
        size = "—" if e["is_dir"] else fmt_size(e["size"])
        name = e["name"]
        if len(name) > 38:
            name = name[:35] + "..."
        print(f"{kind:<6}{name:<40}{size:>10}  {e['id']}")

    # 删除操作的双重确认提醒：列表解析是删除前的必经步骤，在此拦一道
    print()
    print(f"# 若准备对这些条目执行删除——{DELETE_CONFIRM}")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="drive_ops.py",
        description="云盘上传计划、校验清单与列表解析（离线只读，不上传不删除）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("plan-upload", help="生成上传计划（不执行上传）")
    s.add_argument("--dir", required=True, help="本地源目录")
    s.add_argument("--remote", required=True, help="远端根路径，如 /archive/2026")
    s.add_argument("--provider", choices=["baidu", "aliyun", "onedrive"],
                   default="baidu")
    s.add_argument("--prefix", default="", help="在相对路径前追加的子路径")
    s.add_argument("--exclude", default="", help="逗号分隔的 glob，如 *.tmp,.DS_Store")
    s.add_argument("--manifest", help="把计划写成 JSON 文件")
    s.set_defaults(func=cmd_plan_upload)

    s = sub.add_parser("checksum-plan", help="生成 sha256/md5/sha1 校验清单")
    s.add_argument("--dir", required=True)
    s.add_argument("--output", help="输出文件；缺省打印到 stdout")
    s.add_argument("--algo", choices=list(SUPPORTED_ALGOS), default="sha256")
    s.add_argument("--exclude", default="")
    s.set_defaults(func=cmd_checksum_plan)

    s = sub.add_parser("parse-list", help="解析云盘列表响应为可读表格")
    s.add_argument("--json", required=True)
    s.add_argument("--provider", choices=["baidu", "aliyun", "onedrive"],
                   default="baidu")
    s.set_defaults(func=cmd_parse_list)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except PlanError as e:
        return _die(str(e))


if __name__ == "__main__":
    sys.exit(main())
