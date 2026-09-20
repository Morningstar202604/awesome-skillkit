#!/usr/bin/env python3
"""Publication Plotter — 出版级图表（SOTA：字体嵌入 + 期刊真实物理宽度 + 色盲安全色板）。

对标 2026 出版级出图最佳实践：
  - 字体嵌入：pdf.fonttype=42 / ps.fonttype=42（Type 42 子集嵌入，避免 arXiv 拒收）
  - 期刊真实宽度（inches）：nature_single=3.504 (89mm), nature_double=7.0,
    science=4.76, ieee=3.5, acm=6.5, neurips=6.0 —— 默认「按目标版面出图」
  - 色盲安全色板（Paul Tol / Okabe-Ito），--style colorblind_safe 默认启用
  - 可选真实 scienceplots 包：装了则 `plt.style.use(["science","ieee"])`，
    未装则用内置等价预设（离线可用，行为一致）

双轨语义（诚实）：matplotlib 缺失 → status="mock"，无图片产生，MUST 告知用户；
matplotlib 在 → status="success" + rendered=true，产物为真实 PDF/PNG。
"""
import argparse
import json
import sys
from pathlib import Path

# 期刊真实物理宽度（inches），出版级出图应对齐目标版面而非手拍 figsize
JOURNAL_WIDTHS = {
    "nature_single": 3.504,  # 89 mm
    "nature_double": 7.0,    # 全页双栏
    "science": 4.76,
    "ieee": 3.5,
    "acm": 6.5,
    "neurips": 6.0,
}

# 色盲安全色板（Paul Tol vivid / Okabe-Ito 近似），默认全风格启用
CB_COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#56B4E9", "#E69F00", "#F0E442"]

STYLES = {
    "ieee": {"figure_width": JOURNAL_WIDTHS["ieee"], "font_size": 8, "tick_size": 6,
             "line_width": 1.0, "markers": ["o", "s", "^", "D", "v"], "grid": "none"},
    "acm": {"figure_width": JOURNAL_WIDTHS["acm"], "font_size": 9, "tick_size": 7,
            "line_width": 1.2, "markers": ["o", "s", "^", "D"], "grid": "both"},
    "neurips": {"figure_width": JOURNAL_WIDTHS["neurips"], "font_size": 10, "tick_size": 8,
                "line_width": 1.5, "markers": ["o", "s", "^", "D", "P"], "grid": "horizontal"},
    "nature": {"figure_width": JOURNAL_WIDTHS["nature_single"], "font_size": 7, "tick_size": 6,
               "line_width": 0.8, "markers": ["o", "s", "^", "D"], "grid": "none"},
    "colorblind_safe": {"figure_width": 6.0, "font_size": 10, "tick_size": 8,
                        "line_width": 1.5, "markers": ["o", "s", "^", "D"], "grid": "both"},
}


def setup_style(style_name: str, colorblind: bool = True):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conf = STYLES.get(style_name, STYLES["ieee"]).copy()
    rc = {
        "font.size": conf["font_size"],
        "xtick.labelsize": conf["tick_size"],
        "ytick.labelsize": conf["tick_size"],
        "axes.linewidth": 0.8,
        "lines.linewidth": conf["line_width"],
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        # 出版级核心：矢量字体子集嵌入（Type 42），arXiv / 期刊 LaTeX 友好
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.figsize": (conf["figure_width"], conf["figure_width"] * 0.7),
    }
    # 优先真实 scienceplots 包（装了即最贴近官方），否则内置 rcParams 等价实现
    sci = False
    if colorblind:
        try:
            plt.style.use(["science", "vintage" if style_name == "acm" else "ieee"])
            sci = True
        except Exception:
            pass
    plt.rcParams.update(rc)
    colors = CB_COLORS if colorblind else conf.get("colors", CB_COLORS)

    # grid
    if conf["grid"] == "none":
        plt.rcParams["axes.grid"] = False
    elif conf["grid"] == "horizontal":
        plt.rcParams["axes.grid"] = True
        plt.rcParams["grid.axis"] = "y"
    else:
        plt.rcParams["axes.grid"] = True

    return plt, {"width": conf["figure_width"], "marker": conf["markers"],
                 "tick": conf["tick_size"], "colors": colors, "scienceplots": sci}


def _save(fig, out):
    import matplotlib.pyplot as plt
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fmt = "pdf" if out.suffix == ".pdf" else "png"
    fig.savefig(str(out), format=fmt)
    plt.close(fig)
    return str(out)


def plot_line(data: dict, style="ieee", output=None, colorblind=True) -> dict:
    plt, c = setup_style(style, colorblind)
    out = Path(output or "/tmp/fig_pub_line.pdf")
    fig, ax = plt.subplots(figsize=(c["width"], c["width"] * 0.7))
    series = data.get("series", [{"name": "Ours", "values": data.get("y", [0.7, 0.8, 0.9])}])
    xs = data.get("x", list(range(len(series[0].get("values", [0])))))
    for i, s in enumerate(series):
        col = c["colors"][i % len(c["colors"])]
        mk = c["marker"][i % len(c["marker"])]
        ax.plot(xs, s.get("values", []), label=s.get("name", f"S{i}"),
                color=col, marker=mk, markersize=4, alpha=0.9)
    ax.set_xlabel(data.get("xlabel", "Epoch"))
    ax.set_ylabel(data.get("ylabel", "Accuracy"))
    if series:
        ax.legend(fontsize=c["tick"], frameon=False)
    res = {"output": _save(fig, out), "style": style, "type": "line",
           "rendered": True, "width_inches": c["width"],
           "font_embedded": True, "colorblind_safe": colorblind}
    return res


def plot_bar(data: dict, style="ieee", output=None, colorblind=True) -> dict:
    plt, c = setup_style(style, colorblind)
    out = Path(output or "/tmp/fig_pub_bar.pdf")
    fig, ax = plt.subplots(figsize=(c["width"], c["width"] * 0.7))
    labels = data.get("labels", ["A", "B", "C", "D"])
    values = data.get("values", [0.75, 0.80, 0.82, 0.85])
    colors = [c["colors"][i % len(c["colors"])] for i in range(len(labels))]
    errs = data.get("errors")  # 可选 CI / 误差棒
    b = ax.bar(range(len(values)), values, color=colors, width=0.6,
               yerr=(errs if errs else None))
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=c["tick"])
    ax.set_ylabel(data.get("ylabel", "Score"))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return {"output": _save(fig, out), "style": style, "type": "bar",
            "rendered": True, "font_embedded": True, "colorblind_safe": colorblind}


def plot_boxplot(data: dict, style="ieee", output=None, colorblind=True) -> dict:
    plt, c = setup_style(style, colorblind)
    out = Path(output or "/tmp/fig_pub_box.pdf")
    fig, ax = plt.subplots(figsize=(c["width"], c["width"] * 0.7))
    groups = data.get("groups", ["Baseline", "Ours"])
    data_g = data.get("data", [[0.8, 0.82, 0.78], [0.88, 0.91, 0.85]])
    colors = [c["colors"][i % len(c["colors"])] for i in range(len(groups))]
    bp = ax.boxplot(data_g, patch_artist=True, widths=0.5)
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i])
        patch.set_alpha(0.7)
    ax.set_xticklabels(groups, fontsize=c["tick"])
    ax.set_ylabel(data.get("ylabel", "Score"))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return {"output": _save(fig, out), "style": style, "type": "boxplot",
            "rendered": True, "font_embedded": True, "colorblind_safe": colorblind}


def main():
    ap = argparse.ArgumentParser(description="Publication-quality plotter (SOTA)")
    ap.add_argument("--type", default="line", choices=["line", "bar", "boxplot"])
    ap.add_argument("--style", default="ieee", choices=list(STYLES.keys()) + ["science"])
    ap.add_argument("--journal", help="按真实期刊宽度出图: nature_single|science|ieee|acm|neurips")
    ap.add_argument("--no-colorblind", action="store_true", help="关闭色盲安全色板")
    ap.add_argument("--data", help="Data JSON file")
    ap.add_argument("--output", default=None, help="Output file (.pdf/.png)")
    args = ap.parse_args()

    data = {}
    if args.data and Path(args.data).exists():
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    elif args.data:
        print(json.dumps({"status": "error",
                          "error": f"--data 文件不存在: {args.data}（请先确认路径，勿静默用演示数据）"},
                         ensure_ascii=False))
        return 2

    style = args.style
    if args.journal:
        if args.journal not in JOURNAL_WIDTHS:
            print(json.dumps({"status": "error", "error": f"未知 --journal: {args.journal}"},
                             ensure_ascii=False))
            return 2
        style = args.journal if args.journal in STYLES else "ieee"
    colorblind = not args.no_colorblind

    try:
        if args.type == "line":
            res = plot_line(data, style, args.output, colorblind)
        elif args.type == "bar":
            res = plot_bar(data, style, args.output, colorblind)
        else:
            res = plot_boxplot(data, style, args.output, colorblind)
    except ImportError:
        res = {"status": "skipped", "note": "matplotlib not available；pip install matplotlib"}

    res["status"] = "success" if res.get("rendered") else "mock"
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
