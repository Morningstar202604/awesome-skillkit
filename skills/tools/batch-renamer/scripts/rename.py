#!/usr/bin/env python3
"""rename.py -- 批量重命名：预演、执行、回滚三件套。

设计原则
--------
1. **预演是默认动作**：不带 `--yes` 一律只打印"旧名 -> 新名"，不动磁盘。
2. **冲突即跳过**：目标名已被占用时整条跳过并报告，绝不静默覆盖。
3. **必定留痕**：每次真实执行都追加 `rename-log.txt`，`--undo` 依据它回滚。
4. **两阶段改名**：先把所有源文件改成临时名，再改成终名，避免 a<->b 互换时
   中途撞名——这是批量重命名最经典的事故来源。

子命令
------
  preview <dir> [改名规则]          预览（默认动作，不执行）
  apply   <dir> [改名规则] --yes    执行
  undo    <dir> [--log PATH]        依据日志回滚

改名规则（可组合，按固定顺序应用）
--------------------------------  --pattern "IMG_{n:03d}.{ext}"   模板：{n} 序号 / {ext} 扩展名 / {stem} 原名 / {date}
  --regex "OLD" "NEW"              正则替换（对文件名词干，Python re 语法）
  --prefix "P" / --suffix "S"      加前后缀（作用于名干，在扩展名之前）
  --exif-date                      JPG/TIFF 按 EXIF DateTimeOriginal，失败回退 mtime
  --lower / --upper                名干转小写 / 大写

Stdlib + optional Pillow (--exif-date). Python >= 3.8.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

LOG_NAME = "rename-log.txt"

SKIP_DIR_NAMES = {".git", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
                  ".venv", "node_modules"}

IMAGE_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".heic", ".webp"}

# 临时名统一前缀，撤销/中断后靠它识别"改到一半"的文件
TMP_PREFIX = ".rename_tmp_"


class BoundaryError(Exception):
    """目标路径逃出给定目录边界。"""


def _resolve_within(root: Path, target: Path) -> Path:
    """canonicalize 后断言仍在 root 内部（同时挡住 ../ 与逃逸符号链接）。"""
    root_real = root.resolve()
    target_real = (target if target.is_absolute() else root / target).resolve()
    if target_real != root_real and root_real not in target_real.parents:
        raise BoundaryError(f"{target_real} 逃出了目录边界 {root_real}")
    return target_real


def _iter_files(root: Path):
    for dirpath, dirnames, filenames in sorted(__import__("os").walk(root)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.is_symlink() or not p.is_file():
                continue
            if name == LOG_NAME or name.startswith(TMP_PREFIX):
                continue
            yield p


# --------------------------------------------------------------------------
# EXIF 取日期
# --------------------------------------------------------------------------
def _exif_date(path: Path) -> tuple:
    """返回 (datetime, 来源说明)。Pillow 缺失或读不到 EXIF 时回退 mtime。"""
    if path.suffix.lower() in IMAGE_EXTS:
        try:
            from PIL import Image  # 延迟导入：不用 --exif-date 时无需安装
        except ImportError:
            return (
                datetime.fromtimestamp(path.stat().st_mtime),
                "mtime (Pillow 未安装)",
            )
        try:
            with Image.open(path) as im:
                exif = im.getexif()
                # 36867 = DateTimeOriginal；306 = DateTime
                raw = exif.get(36867) or exif.get(306)
                if raw:
                    dt = datetime.strptime(str(raw).strip(), "%Y:%m:%d %H:%M:%S")
                    return dt, "EXIF"
        except Exception:  # 损坏图 / 非常规 EXIF 一律回退，不影响其余文件
            pass
    return datetime.fromtimestamp(path.stat().st_mtime), "mtime"


# --------------------------------------------------------------------------
# 名字计算
# --------------------------------------------------------------------------
def _apply_text_rules(stem: str, args) -> str:
    """按固定顺序应用文本类规则：regex -> prefix/suffix -> case。"""
    out = stem
    if args.regex:
        old, new = args.regex
        try:
            out = re.sub(old, new, out)
        except re.error as e:
            raise ValueError(f"正则语法错误: {e}") from e
    if args.prefix:
        out = f"{args.prefix}{out}"
    if args.suffix:
        out = f"{out}{args.suffix}"
    if args.lower:
        out = out.lower()
    if args.upper:
        out = out.upper()
    return out


def _apply_pattern(pattern: str, path: Path, index: int, dt: datetime | None) -> str:
    """模板替换。支持 {n} / {ext} / {stem} / {date}，均可带 Python 格式规格。

    例：`IMG_{n:03d}.{ext}` 里的 `{n:03d}` 会走标准 format 的补零逻辑；
    `{date}` 不带规格时默认 `%Y%m%d`，带规格时改用该 strftime 串（如 `{date:%Y-%m}`）。
    未知占位符直接报错，避免静默生成一堆同名字符串。
    """
    base_date = dt or datetime.fromtimestamp(path.stat().st_mtime)
    fields = {
        "n": index,
        "ext": path.suffix.lstrip("."),
        "stem": path.stem,
        "date": base_date.strftime("%Y%m%d"),
    }
    placeholder = re.compile(r"\{([a-z]+)(?::([^}]*))?\}")

    def repl(m):
        key, spec = m.group(1), m.group(2)
        if key not in fields:
            raise ValueError(
                f"未知占位符 {{{key}}}；支持：{{n}} {{ext}} {{stem}} {{date}}"
            )
        if spec is None:
            return str(fields[key])
        if key == "date":
            # 对日期而言，规格串是 strftime 模板而非 format 规格
            return base_date.strftime(spec)
        if key == "n":
            try:
                return format(int(fields[key]), spec)
            except ValueError as e:
                raise ValueError(f"序号格式 `{spec}` 非法: {e}") from e
        return format(fields[key], spec)

    return placeholder.sub(repl, pattern)


def _pattern_uses(pattern: str, field: str) -> bool:
    """判断模板里是否真的用到了某个占位符。

    只在用到 `{n}` 时才消耗序号，避免生成带空洞的编号；只在用到 `{date}`
    时才去读 EXIF，省掉无谓的图片解码。
    """
    return f"{{{field}" in pattern


def compute_plan(root: Path, args) -> list:
    """返回 [(src, dst, note) ...]，已剔除"无需改名"的项。"""
    files = list(_iter_files(root))
    if not files:
        return []

    dates = {}
    if args.exif_date:
        for p in files:
            dates[p] = _exif_date(p)

    # 序号只在真正用到 {n} 时才自增：否则被跳过的文件会白白吃掉一个号，
    # 产生 IMG_000, IMG_002 这样的空洞。
    counter = args.start
    uses_n = bool(args.pattern) and _pattern_uses(args.pattern, "n")
    uses_date = bool(args.pattern) and _pattern_uses(args.pattern, "date")
    plan = []
    for p in files:
        stem = _apply_text_rules(p.stem, args)
        note = ""
        if args.pattern:
            dt = dates.get(p, (None, ""))[0]
            index = counter if uses_n else 0
            try:
                new_name = _apply_pattern(args.pattern, p, index, dt)
            except ValueError as e:
                raise SystemExit(f"ERROR: {e}")
            if uses_n:
                counter += 1
        else:
            new_name = f"{stem}{p.suffix}"
        if args.exif_date and not args.pattern:
            dt, src = dates[p]
            new_name = f"{dt.strftime('%Y%m%d')}_{new_name}"
            note = f"[{src}]"
        elif args.exif_date and uses_date:
            note = f"[{dates[p][1]}]"

        if new_name == p.name:
            # 已经合规则：不占序号，但也不移动
            continue
        plan.append((p, _resolve_within(root, Path(new_name)), note))
    return plan


def _detect_conflicts(root: Path, plan: list) -> tuple:
    """把计划拆成 (可执行, 冲突)。冲突 = 目标已存在，或两条计划撞同一个目标名。"""
    wanted = {}
    ok, conflicts = [], []
    for src, dst, note in plan:
        existing = dst.exists() and dst.resolve() != src.resolve()
        collides = wanted.get(str(dst))
        if existing:
            conflicts.append((src, dst, note, f"目标已存在 {dst.name}"))
        elif collides is not None:
            conflicts.append(
                (src, dst, note, f"与本批次的 {collides.name} 撞名")
            )
        else:
            wanted[str(dst)] = src
            ok.append((src, dst, note))
    return ok, conflicts


# --------------------------------------------------------------------------
# preview / apply
# --------------------------------------------------------------------------
def cmd_preview(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    plan = compute_plan(root, args)
    print(f"# 重命名预览: {root.resolve()}")
    print("（本命令不执行任何改动）")
    print()
    if not plan:
        print("无需改名：所有文件名都符合目标规则。")
        return 0
    ok, conflicts = _detect_conflicts(root, plan)
    pairs = [(src.relative_to(root).as_posix(), dst.relative_to(root).as_posix())
             for src, dst, _ in ok]
    width = max((len(a) for a, _ in pairs), default=10)
    for (rel_s, rel_d), (_, _, note) in zip(pairs, ok):
        print(f"  {rel_s:<{width}}  ->  {rel_d} {note}")
    if conflicts:
        print()
        print(f"## 冲突跳过 {len(conflicts)} 项（不会执行）")
        for src, dst, _, why in conflicts:
            print(f"  [skip:{why}] {src.relative_to(root)} -> "
                  f"{dst.relative_to(root)}")
    print()
    print(f"合计：将改名 {len(ok)} 项，跳过 {len(conflicts)} 项。")
    print(f"确认后执行：apply {root} <相同规则> --yes")
    return 0


def _write_log(root: Path, entries: list) -> Path:
    """追加一行一条 JSON 记录；用 JSON 而非分隔符文本，防止文件名含空格/引号时解析崩。"""
    log_path = root / LOG_NAME
    with log_path.open("a", encoding="utf-8") as fh:
        for old, new in entries:
            fh.write(json.dumps({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "from": old, "to": new,
            }, ensure_ascii=False) + "\n")
    return log_path


def cmd_apply(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    if not args.yes:
        print("拒绝执行：apply 必须显式加 --yes 才会改动磁盘。")
        print("先跑 preview 检视计划：")
        print(f"  preview {root} <相同规则>")
        return 2

    plan = compute_plan(root, args)
    if not plan:
        print("无需改名。")
        return 0
    ok, conflicts = _detect_conflicts(root, plan)

    print(f"# 执行重命名: {root.resolve()}")
    print()
    done = []
    # 阶段一：全部改成临时名，彻底消除 a<->b 互换时的中途撞名
    staged = []
    try:
        for src, dst, note in ok:
            tmp = src.with_name(f"{TMP_PREFIX}{len(staged)}{src.suffix}")
            try:
                _resolve_within(root, tmp)
                src.rename(tmp)
                staged.append((src, tmp, dst, note))
            except (BoundaryError, OSError) as e:
                print(f"[skip] {src.relative_to(root)} 暂存失败: {e}", file=sys.stderr)
        # 阶段二：临时名 -> 终名
        for src, tmp, dst, note in staged:
            try:
                if dst.exists():
                    print(f"[skip] 目标已出现，回退: {dst.relative_to(root)}",
                          file=sys.stderr)
                    tmp.rename(src)
                    continue
                tmp.rename(dst)
                print(f"[ok] {src.relative_to(root)} -> {dst.relative_to(root)} {note}")
                done.append((src.relative_to(root).as_posix(),
                             dst.relative_to(root).as_posix()))
            except OSError as e:
                print(f"[skip] {src.relative_to(root)} 改名失败: {e}", file=sys.stderr)
                if tmp.exists():
                    tmp.rename(src)
    except KeyboardInterrupt:
        # 中断兜底：把还停在临时名的文件改回去，不让目录处于半改名状态
        for src, tmp, _dst, _n in staged:
            if tmp.exists():
                tmp.rename(src)
        print("\n已中断：暂存中的文件已还原，日志未写入。", file=sys.stderr)
        return 130

    if done:
        log_path = _write_log(root, done)
        print()
        print(f"完成：改名 {len(done)} 项，跳过 {len(conflicts)} 项。")
        print(f"变更日志：{log_path}（回滚命令：undo {root}）")

    if conflicts:
        print()
        print(f"## 冲突跳过 {len(conflicts)} 项")
        for src, dst, _, why in conflicts:
            print(f"  [skip:{why}] {src.relative_to(root)} -> {dst.relative_to(root)}")
    return 0


# --------------------------------------------------------------------------
# undo
# --------------------------------------------------------------------------
def cmd_undo(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    log_path = Path(args.log) if args.log else root / LOG_NAME
    if not log_path.is_file():
        print(f"ERROR: 找不到日志 {log_path}", file=sys.stderr)
        return 1

    records = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            print(f"WARN: 跳过无法解析的日志行: {line[:60]}", file=sys.stderr)

    if not records:
        print("日志为空，无可回滚内容。")
        return 0

    if not args.yes:
        print(f"# 回滚预览（{len(records)} 条记录，逆序执行）")
        print()
        for rec in reversed(records):
            print(f"  {rec['to']}  ->  {rec['from']}")
        print()
        print(f"确认后执行：undo {root} --yes")
        return 0

    print("# 执行回滚")
    print()
    reverted, stuck = [], []
    for rec in reversed(records):
        cur = _resolve_within(root, Path(rec["to"]))
        orig = _resolve_within(root, Path(rec["from"]))
        if not cur.exists():
            print(f"[skip] 已不存在: {rec['to']}", file=sys.stderr)
            stuck.append(rec)
            continue
        if orig.exists():
            print(f"[skip] 原名已被占用，无法回滚: {rec['from']}", file=sys.stderr)
            stuck.append(rec)
            continue
        try:
            orig.parent.mkdir(parents=True, exist_ok=True)
            cur.rename(orig)
            print(f"[ok] {rec['to']} -> {rec['from']}")
            reverted.append(rec)
        except OSError as e:
            print(f"[skip] {rec['to']} 回滚失败: {e}", file=sys.stderr)
            stuck.append(rec)

    # 已回滚的记录从日志剔除，保留无法回滚的，避免重复 undo 出乱子
    remaining = [r for r in records if r in stuck]
    log_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in remaining),
        encoding="utf-8",
    )
    print()
    print(f"回滚完成：还原 {len(reverted)} 项，未处理 {len(stuck)} 项。")
    print(f"日志已更新：{log_path} 剩余 {len(remaining)} 条")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rename.py",
        description="批量重命名（preview 默认 / apply 需 --yes / undo 回滚）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_rules(sp):
        sp.add_argument("dir")
        sp.add_argument("--pattern", help="模板，如 'IMG_{n:03d}.{ext}'")
        sp.add_argument("--regex", nargs=2, metavar=("OLD", "NEW"),
                        help="正则替换，作用于名干")
        sp.add_argument("--prefix", default=None, help="名干前缀")
        sp.add_argument("--suffix", default=None, help="名干后缀")
        sp.add_argument("--exif-date", action="store_true",
                        help="按 EXIF 拍摄日期加 YYYYMMDD_ 前缀（失败回退 mtime）")
        sp.add_argument("--lower", action="store_true")
        sp.add_argument("--upper", action="store_true")
        sp.add_argument("--start", type=int, default=1, help="序号起始值（默认 1）")

    s = sub.add_parser("preview", help="预览重命名结果（默认动作，不执行）")
    add_rules(s)
    s.set_defaults(func=cmd_preview)

    s = sub.add_parser("apply", help="执行重命名（必须 --yes）")
    add_rules(s)
    s.add_argument("--yes", action="store_true", help="确认执行")
    s.set_defaults(func=cmd_apply)

    s = sub.add_parser("undo", help="依据 rename-log.txt 回滚")
    s.add_argument("dir")
    s.add_argument("--log", default=None, help="自定义日志路径")
    s.add_argument("--yes", action="store_true", help="确认回滚")
    s.set_defaults(func=cmd_undo)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "lower", False) and getattr(args, "upper", False):
        print("ERROR: --lower 与 --upper 互斥。", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except BoundaryError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
