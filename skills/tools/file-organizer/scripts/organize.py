#!/usr/bin/env python3
"""organize.py -- 目录体检与整理计划器（scan / plan / apply / dedupe）。

设计原则
--------
1. **只读优先**：`scan` / `plan` / `dedupe` 永不改动磁盘；`apply` 默认 dry-run，
   只有显式 `--yes` 才真正移动文件。
2. **边界封闭**：所有目标路径都经 `_resolve_within` 校验，解析后的真实路径必须
   落在给定目录内部，杜绝 `../` 越界与符号链接逃逸。
3. **不作恶**：不删除任何文件，重复文件只给"保留建议"，删除动作永远留给用户。
4. **快**：判重只读文件前 1KB 做哈希，避免全量读取大文件。

子命令
------
  scan   <dir>                              目录体检（扩展名分布、体积、重复组）
  plan   <dir> --by {type,date,size}        生成整理方案（只打印，不动文件）
  apply  <dir> --by {type,date} [--yes]     执行整理（默认 dry-run）
  dedupe <dir>                              列出重复文件组 + 保留建议

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# 判重时读取的头部字节数。取 1KB 是因为：绝大多数文件格式的魔数与基础元信息
# 都在这段内，足以区分"同大小但不同内容"的文件；再大只会拖慢而不提升判别力。
HEAD_BYTES = 1024

# 体积分档阈值（人类可读的粗粒度分组，按上限升序）。
SIZE_BUCKETS = [
    ("tiny(<10KB)", 10 * 1024),
    ("small(<1MB)", 1024 * 1024),
    ("medium(<10MB)", 10 * 1024 * 1024),
    ("large(<100MB)", 100 * 1024 * 1024),
    ("huge(>=100MB)", None),
]

# 整理时不纳入的目录：这些是工具自身的产物或版本控制内部结构，
# 动它们会破坏仓库/环境状态。
SKIP_DIR_NAMES = {".git", ".svn", ".hg", "__pycache__", ".pytest_cache",
                  ".mypy_cache", ".ruff_cache", ".venv", "node_modules"}


class BoundaryError(Exception):
    """目标路径逃出给定目录边界。"""


def _resolve_within(root: Path, target: Path) -> Path:
    """把 target 解析为绝对真实路径，并断言它仍在 root 内部。

    `Path.resolve()` 会展开符号链接，因此这里能同时挡住 `../` 文本越界和
    指向目录外的软链接——这是本脚本唯一的安全闸门，所有写入/移动路径都必须过它。
    """
    root_real = root.resolve()
    # strict=False：目标文件可能尚不存在（apply 要新建目录）
    target_real = (target if target.is_absolute() else root / target).resolve()
    if target_real != root_real and root_real not in target_real.parents:
        raise BoundaryError(f"{target_real} 逃出了目录边界 {root_real}")
    return target_real


def _iter_files(root: Path):
    """遍历 root 下的普通文件，跳过符号链接与工具目录。"""
    for dirpath, dirnames, filenames in os.walk(root):
        # 原地裁剪 dirnames 才能阻止 os.walk 继续下潜
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.is_symlink() or not p.is_file():
                continue
            yield p


def _head_hash(path: Path) -> str:
    """文件前 HEAD_BYTES 字节的 sha1，读不满也无妨。"""
    h = hashlib.sha1()
    with path.open("rb") as fh:
        h.update(fh.read(HEAD_BYTES))
    return h.hexdigest()


def _fingerprint(path: Path) -> tuple:
    """快速判重指纹 = (文件大小, 前 1KB 哈希)。

    只有大小完全相同的文件才有必要比头部内容；大小不同直接判为不同文件。
    """
    return (path.stat().st_size, _head_hash(path))


def _ext_label(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return ext if ext else "(no-ext)"


def _fmt_size(n: int) -> str:
    """人类可读体积：B 不带小数，其余保留一位。"""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{int(size)}B" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def _size_bucket(n: int) -> str:
    for label, upper in SIZE_BUCKETS:
        if upper is None or n < upper:
            return label
    return SIZE_BUCKETS[-1][0]


def _dup_groups(root: Path):
    """返回 [(fingerprint, [paths...]) ...]，只保留 >=2 个文件的组。

    分组键是 (size, head_hash)：先按大小分桶，桶内再按头部哈希细分，
    因此大小唯一的文件连读都不用读。
    """
    by_size = defaultdict(list)
    for p in _iter_files(root):
        by_size[p.stat().st_size].append(p)
    groups = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for p in paths:
            groups[(size, _head_hash(p))].append(p)
    return sorted(
        ((fp, sorted(ps)) for fp, ps in groups.items() if len(ps) > 1),
        key=lambda kv: (-kv[0][0], str(kv[1][0])),
    )


def _keep_recommendation(paths: list) -> tuple:
    """在重复组里挑保留项：最旧的（mtime 最早）优先，并列取路径最短的。"""
    ranked = sorted(paths, key=lambda p: (p.stat().st_mtime, len(str(p)), str(p)))
    return ranked[0], ranked[1:]


# --------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------
def cmd_scan(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1

    files = list(_iter_files(root))
    if not files:
        print(f"目录 {root.resolve()} 内没有可整理的文件。")
        return 0

    total = sum(p.stat().st_size for p in files)

    by_ext = defaultdict(lambda: [0, 0])
    by_bucket = defaultdict(int)
    for p in files:
        st = p.stat()
        slot = by_ext[_ext_label(p)]
        slot[0] += 1
        slot[1] += st.st_size
        by_bucket[_size_bucket(st.st_size)] += 1

    print(f"# 目录体检: {root.resolve()}")
    print(f"文件总数: {len(files)}    总体积: {_fmt_size(total)}")
    print()

    print("## 按扩展名分组（数量降序）")
    print(f"{'ext':<12}{'count':>8}{'size':>12}")
    for ext, (cnt, size) in sorted(
        by_ext.items(), key=lambda kv: (-kv[1][0], kv[0])
    ):
        print(f"{ext:<12}{cnt:>8}{_fmt_size(size):>12}")
    print()

    print("## 体积分布")
    for label, _ in SIZE_BUCKETS:
        if by_bucket.get(label):
            print(f"{label:<16}{by_bucket[label]:>6} 个")
    print()

    groups = _dup_groups(root)
    wasted = sum(fp[0] * (len(ps) - 1) for fp, ps in groups)
    print("## 重复文件检测（大小 + 前 1KB 哈希）")
    if not groups:
        print("未发现重复文件。")
    else:
        print(f"重复组: {len(groups)}    冗余体积: {_fmt_size(wasted)}")
        for idx, (fp, paths) in enumerate(groups, 1):
            print(f"  [{idx}] {_fmt_size(fp[0])} x{len(paths)}")
            for p in paths:
                print(f"        {p.relative_to(root)}")
        print()
        print("提示：运行 `dedupe <dir>` 获取保留建议。")
    return 0


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------
def _plan_type(p: Path, root: Path) -> Path:
    return Path(_ext_label(p))


def _plan_date(p: Path, root: Path) -> Path:
    return Path(datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m"))


def _plan_size(p: Path, root: Path) -> Path:
    return Path(_size_bucket(p.stat().st_size))


PLANNERS = {"type": _plan_type, "date": _plan_date, "size": _plan_size}


def _build_moves(root: Path, by: str):
    """返回 [(src, dst) ...]；dst 已解决同目录内/已存在目标的重名问题。

    冲突解决策略：`name.ext` 已占用时依次尝试 `name_1.ext`、`name_2.ext`……
    序号单调递增到第一个空位；这样重复运行 plan/apply 不会互相覆盖。
    """
    planner = PLANNERS[by]
    moves = []
    taken = set()
    for p in _iter_files(root):
        bucket = planner(p, root)
        if bucket == Path("."):  # 已经躺在目标桶根下，无需移动
            continue
        dst_dir = _resolve_within(root, bucket)
        candidate = dst_dir / p.name
        counter = 1
        while str(candidate) in taken or (
            candidate.exists() and candidate.resolve() != p.resolve()
        ):
            candidate = dst_dir / f"{p.stem}_{counter}{p.suffix}"
            counter += 1
        taken.add(str(candidate))
        moves.append((p, candidate))
    return sorted(moves, key=lambda m: str(m[0]))


def cmd_plan(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    moves = _build_moves(root, args.by)
    print(f"# 整理计划: {root.resolve()}  (by={args.by})")
    if not moves:
        print("无需移动：所有文件都已在目标位置。")
        return 0
    print(f"共 {len(moves)} 项移动，以下为完整清单（本命令不执行任何移动）：")
    print()
    for src, dst in moves:
        print(f"将把 {src.relative_to(root)} 移到 {dst.relative_to(root)}")
    print()
    print(f"确认无误后执行：apply {root} --by {args.by} --yes")
    return 0


# --------------------------------------------------------------------------
# apply
# --------------------------------------------------------------------------
def cmd_apply(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    if args.by == "size":
        print(
            "ERROR: apply 不支持 --by size。\n"
            "原因：体积是文件属性而非语义分类，按体积归档会让文件失去可检索性。\n"
            "如需按体积观察分布，请用 `scan`，或先 `plan --by size` 人工审阅。",
            file=sys.stderr,
        )
        return 2

    moves = _build_moves(root, args.by)
    if not moves:
        print("无需移动。")
        return 0

    dry = not args.yes
    print(f"# {'DRY-RUN（未改动磁盘）' if dry else 'EXECUTE（真正移动）'}"
          f"  目录={root.resolve()}  by={args.by}")
    print()
    moved = skipped = 0
    for src, dst in moves:
        rel_src = src.relative_to(root)
        rel_dst = dst.relative_to(root)
        if dry:
            print(f"[dry-run] {rel_src} -> {rel_dst}")
            continue
        try:
            _resolve_within(root, dst)
            if dst.exists():
                print(f"[skip] 目标已存在，跳过: {rel_dst}")
                skipped += 1
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"[ok] {rel_src} -> {rel_dst}")
            moved += 1
        except BoundaryError as e:
            print(f"[skip] {e}", file=sys.stderr)
            skipped += 1
        except OSError as e:
            print(f"[skip] {rel_src} 移动失败: {e}", file=sys.stderr)
            skipped += 1

    print()
    if dry:
        print(f"DRY-RUN 结束：计划移动 {len(moves)} 项，磁盘未发生任何变化。")
        print(f"确认后加 --yes 执行：apply {root} --by {args.by} --yes")
    else:
        print(f"完成：移动 {moved} 项，跳过 {skipped} 项。")
    return 0


# --------------------------------------------------------------------------
# dedupe
# --------------------------------------------------------------------------
def cmd_dedupe(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    groups = _dup_groups(root)
    print(f"# 重复文件报告: {root.resolve()}")
    if not groups:
        print("未发现重复文件（判据：大小相同 + 前 1KB 哈希相同）。")
        return 0

    wasted = sum(fp[0] * (len(ps) - 1) for fp, ps in groups)
    print(f"重复组 {len(groups)} 个，冗余体积 {_fmt_size(wasted)}。")
    print("本命令只给建议，不删除任何文件。")
    print()
    for idx, (fp, paths) in enumerate(groups, 1):
        keep, drop = _keep_recommendation(paths)
        print(f"[{idx}] 大小 {_fmt_size(fp[0])}，{len(paths)} 份")
        print(f"    保留: {keep.relative_to(root)}  （最旧 / 路径最短）")
        for p in drop:
            print(f"    可清理: {p.relative_to(root)}")
        print()

    print("清理建议（请人工确认后再执行，本脚本不代劳）：")
    print("  1. 先 `diff` 或二进制比对确认内容确实一致；")
    print("  2. 确认没有其他文件通过硬链接/引用依赖被删的那一份；")
    print("  3. 移动到一个 `_dupes_backup/` 目录观察一段时间再删。")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="organize.py",
        description="目录体检与整理计划器（默认只读，apply 需 --yes）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="扫描目录：扩展名分布、体积、重复文件")
    s.add_argument("dir")
    s.set_defaults(func=cmd_scan)

    s = sub.add_parser("plan", help="生成整理计划（不执行）")
    s.add_argument("dir")
    s.add_argument("--by", choices=["type", "date", "size"], default="type")
    s.set_defaults(func=cmd_plan)

    s = sub.add_parser("apply", help="执行整理（默认 dry-run，--yes 才真正移动）")
    s.add_argument("dir")
    s.add_argument("--by", choices=["type", "date"], default="type")
    s.add_argument("--dry-run", action="store_true",
                   help="显式声明 dry-run（默认行为，仅用于自文档化）")
    s.add_argument("--yes", action="store_true",
                   help="真正执行移动；不加此参数一律 dry-run")
    s.set_defaults(func=cmd_apply)

    s = sub.add_parser("dedupe", help="列出重复文件组与保留建议")
    s.add_argument("dir")
    s.set_defaults(func=cmd_dedupe)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BoundaryError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
