#!/usr/bin/env python3
"""
gen_smoke.py — 为「有脚本但缺 test_smoke_*.py」的真实技能生成保守冒烟测试（P0 补覆盖）。

设计（延续自审结论）：
  第二代 run_skill_smoke.py 直跑真实技能自带冒烟测试，但 56 个脚本化技能里只有 20 个 ship 了测试。
  本工具为其余 36 个生成 `scripts/test_smoke_all.py`，保守校验：
    1) 每个脚本 import 时不抛异常（抓 SyntaxError / ImportError / 顶层运行时错）；
    2) `python <script> --help` 不抛未捕获异常（抓 CLI 入口崩溃）。
  生成的是「弱冒烟」：只证明脚本能加载、CLI 入口不崩。手搓强测试（真输入+真断言）应逐步替换它。

用法：
  python tools/gen_smoke.py            # 生成缺失的 test_smoke_all.py
  python tools/gen_smoke.py --dry      # 只打印将生成哪些，不落盘
  python tools/gen_smoke.py --force    # 覆盖重生成已存在的 test_smoke_all.py（修复模板后用）
递归发现 skills/**/scripts/（含 programming/data/etl-builder 这类嵌套技能）。
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(REPO, "skills")
AUTO_NAME = "test_smoke_all.py"


def discover_targets(force=False):
    """返回 [(skill_id, scripts_dir, [script_paths])] 需补/重生成冒烟的技能。

    force=False：跳过任何已含 test_smoke_*.py 的目录（避免覆盖手搓强测试）。
    force=True ：重生成我们自己的 AUTO_NAME（覆盖旧模板产物），但不给仅有手搓测试的目录追加弱测试。
    """
    out = []
    for root, dirs, files in os.walk(SKILLS):
        if os.path.basename(root) != "scripts":
            continue
        pys = [f for f in files if f.endswith(".py")]
        if not pys:
            continue
        has_auto = AUTO_NAME in pys
        has_other = any(f.startswith("test_smoke_") and f != AUTO_NAME for f in pys)
        if not force and (has_auto or has_other):
            continue  # 已有冒烟，跳过
        if force and has_other and not has_auto:
            continue  # 仅有手搓测试，不追加弱测试
        real = [os.path.join(root, f) for f in pys if not f.startswith("test_")]
        if not real:
            continue
        # skill_id = skills 之后两段（domain/skill），嵌套也取最后两段
        rel = os.path.relpath(root, SKILLS)
        parts = rel.split(os.sep)
        sid = os.path.join(*parts[:2]) if len(parts) >= 2 else parts[0]
        out.append((sid, root, real))
    return sorted(out, key=lambda x: x[0])


TPL = '''# -*- coding: utf-8 -*-
r"""Auto-generated smoke test for `{sid}` (tools/gen_smoke.py).

保守校验：每个脚本 import 无异常 + `python <script> --help` 不抛未捕获异常。
手搓强测试（真输入 + 真断言）应逐步替换本文件。
"""
import importlib.util
import subprocess
import sys

from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SCRIPTS = sorted(p for p in SCRIPTS_DIR.glob("*.py") if not p.name.startswith("test_"))


def test_all_scripts_import_cleanly():
    assert SCRIPTS, "no scripts found in scripts/"
    for sp in SCRIPTS:
        try:
            spec = importlib.util.spec_from_file_location(sp.stem, sp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            raise AssertionError(f"{{sp.name}} import failed: {{e}}")


def test_all_scripts_help_no_crash():
    assert SCRIPTS
    for sp in SCRIPTS:
        r = subprocess.run(
            [sys.executable, str(sp), "--help"],
            capture_output=True, text=True, timeout=60,
        )
        out = (r.stdout or "") + (r.stderr or "")
        assert "Traceback" not in out, f"{{sp.name}} --help crashed:\\n{{out[-800:]}}"
        assert r.returncode in (0, 1, 2), f"{{sp.name}} --help unexpected exit {{r.returncode}}"
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只打印，不落盘")
    ap.add_argument("--force", action="store_true", help="覆盖重生成已存在的 test_smoke_all.py")
    args = ap.parse_args()
    targets = discover_targets(force=args.force)
    mode = "[dry] " if args.dry else ("[force] " if args.force else "[gen] ")
    print(f"需补/重生成冒烟的脚本化技能：{len(targets)}")
    for sid, sdir, real in targets:
        fname = os.path.join(sdir, "test_smoke_all.py")
        print(f"  {mode}{sid}  ({len(real)} script(s))")
        if not args.dry:
            with open(fname, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(TPL.format(sid=sid.replace("\\", "/")))
    if not args.dry:
        print(f"\n已生成/重生成 {len(targets)} 个 test_smoke_all.py。下一步：python tools/run_skill_smoke.py")


if __name__ == "__main__":
    main()
