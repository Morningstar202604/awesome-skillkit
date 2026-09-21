#!/usr/bin/env python3
"""Figure Maker — **DEPRECATED**：本技能已并入 `pub-plotter`。

保留原有 CLI 与 JSON 契约（`--data` / `--type bar|line|boxplot|heatmap` / `--output`），
内部**委托** `pub-plotter/scripts/pub_plotter.py`，因此：
  - 既有外部调用方无需改动即可继续跑；
  - 但会多出 `deprecated: true` / `superseded_by: "pub-plotter"` 字段，且 `heatmap`
    从「返回 unsupported」变为**真实渲染**（pub-plotter 已实现）。

为什么不直接删：仓库内索引（manifest.json / packs / skill_chains.json / 生成站点 site/）
仍按名字引用本技能，且外部可能已固定本 CLI；直接删除会打断它们。
（仓库内**代码**消费者 `paper_pipeline.py` 已迁到 pub-plotter。）
保留薄壳 = 去重实现 + 不破坏消费者 + 显式暴露弃用。

迁移方式：把调用直接换成
  python3 ../pub-plotter/scripts/pub_plotter.py --type heatmap --journal ieee --data d.json
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

PURPLE = "../../pub-plotter/scripts/pub_plotter.py"  # scripts/ -> figure-maker/ -> paper/pub-plotter/

_DISPATCH = {"line": "plot_line", "bar": "plot_bar",
             "boxplot": "plot_boxplot", "heatmap": "plot_heatmap"}


def _load_pub_plotter():
    """按相对路径加载 pub-plotter 的实现（不依赖 sys.path 污染，也不要求包结构）。"""
    target = (Path(__file__).resolve().parent / PURPLE).resolve()
    if not target.exists():
        return None, target
    spec = importlib.util.spec_from_file_location("pub_plotter_impl", target)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, target


def main():
    parser = argparse.ArgumentParser(
        description="Paper figure generator (DEPRECATED — delegates to pub-plotter)")
    parser.add_argument("--data", help="Data JSON file")
    parser.add_argument("--type", default="bar",
                        choices=["bar", "line", "boxplot", "heatmap"])
    parser.add_argument("--output", help="Output file (.pdf/.png)")
    parser.add_argument("--journal", help="透传给 pub-plotter: nature_single|science|ieee|acm|neurips")
    parser.add_argument("--no-colorblind", action="store_true",
                        help="透传给 pub-plotter：关闭色盲安全色板")
    args = parser.parse_args()

    data = {}
    if args.data:
        p = Path(args.data)
        if not p.exists():
            print(json.dumps({"status": "error",
                              "error": f"--data 文件不存在: {args.data}"},
                             ensure_ascii=False))
            return 2
        data = json.loads(p.read_text(encoding="utf-8"))

    mod, target = _load_pub_plotter()
    if mod is None:
        # 诚实降级：委托目标缺失时明确报错，绝不假装成功
        print(json.dumps({"status": "error",
                          "error": f"delegation target missing: {target}",
                          "deprecated": True, "superseded_by": "pub-plotter"},
                         ensure_ascii=False, indent=2))
        return 1

    style = "ieee"
    journal = None
    if args.journal:
        if args.journal not in mod.JOURNAL_WIDTHS:
            print(json.dumps({"status": "error", "error": f"未知 --journal: {args.journal}",
                              "deprecated": True, "superseded_by": "pub-plotter"},
                             ensure_ascii=False, indent=2))
            return 2
        journal = args.journal

    fn = getattr(mod, _DISPATCH[args.type])
    try:
        res = fn(data, style, args.output, not args.no_colorblind, journal)
    except ImportError:
        res = {"status": "skipped", "note": "matplotlib not available；pip install matplotlib"}
    except ValueError as e:
        # 与 pub-plotter 同口径：非法数据（如 heatmap 非二维阵）必须报错，不允许悄悄出图
        print(json.dumps({"status": "error", "error": str(e),
                          "deprecated": True, "superseded_by": "pub-plotter"},
                         ensure_ascii=False, indent=2))
        return 2

    res["status"] = "success" if res.get("rendered") else "mock"
    res["deprecated"] = True
    res["superseded_by"] = "pub-plotter"
    res["deprecation_note"] = (
        "figure-maker is a compatibility shim; call pub-plotter directly "
        "(it additionally supports --journal widths and full type coverage).")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
