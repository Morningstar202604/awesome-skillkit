#!/usr/bin/env python3
"""Publication Plotter — 学术论文级别绑图 (SciencePlots 风格)。

学习自: garrettj403/SciencePlots (9.2k stars)
支持: IEEE/ACM/NeurIPS 风格, 单栏/双栏, PDF/PNG 输出

用法:
  python3 pub_plotter.py --type line --data results.json --style ieee
  python3 pub_plotter.py --type boxplot --style acm --output fig1.pdf
"""
import argparse
import json
import sys
from pathlib import Path

# Publication-quality style presets (from SciencePlots concepts)
STYLES = {
    "ieee": {
        "figure_width": 5.5,  # inches (single column IEEE)
        "font_size": 8,
        "tick_size": 6,
        "line_width": 1.0,
        "markers": ["o", "s", "^", "D", "v"],
        "colors": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#56B4E9"],
        "grid": "none",
        "background": "white",
    },
    "acm": {
        "figure_width": 6.5,
        "font_size": 9,
        "tick_size": 7,
        "line_width": 1.2,
        "markers": ["o", "s", "^", "D"],
        "colors": ["#0072B2", "#E69F00", "#009E73", "#F0E442"],
        "grid": "both",
        "background": "white",
    },
    "neurips": {
        "figure_width": 6.0,
        "font_size": 10,
        "tick_size": 8,
        "line_width": 1.5,
        "markers": ["o", "s", "^", "D", "P"],
        "colors": ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"],
        "grid": "horizontal",
        "background": "white",
    },
    "colorblind_safe": {
        "figure_width": 6.0,
        "font_size": 10,
        "tick_size": 8,
        "line_width": 1.5,
        "markers": ["o", "s", "^", "D"],
        "colors": ["#0072B2", "#E69F00", "#009E73", "#CC79A7"],
        "grid": "both",
        "background": "white",
    },
}


def setup_style(style_name: str):
    """Apply publication style to matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conf = STYLES.get(style_name, STYLES["ieee"])
    plt.rcParams.update({
        "font.size": conf["font_size"],
        "xtick.labelsize": conf["tick_size"],
        "ytick.labelsize": conf["tick_size"],
        "axes.linewidth": 0.8,
        "lines.linewidth": conf["line_width"],
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "figure.figsize": (conf["figure_width"], conf["figure_width"] * 0.7),
    })
    if conf["grid"] == "none":
        plt.rcParams["axes.grid"] = False
    elif conf["grid"] == "horizontal":
        plt.rcParams["axes.grid"] = True
        plt.rcParams["grid.axis"] = "y"
    else:
        plt.rcParams["axes.grid"] = True

    return plt, conf


def plot_line(data: dict, style: str = "ieee", output: str = None) -> dict:
    """Plot publication-quality line chart."""
    plt, conf = setup_style(style)
    import matplotlib.pyplot as plt

    out = Path(output or "/tmp/fig_pub_line.pdf")
    fig, ax = plt.subplots()

    series = data.get("series", [{"name": "Ours", "values": data.get("y", [0.7, 0.8, 0.9])}])
    xs = data.get("x", list(range(len(series[0].get("values", [0])))))

    for i, s in enumerate(series):
        color = conf["colors"][i % len(conf["colors"])]
        marker = conf["markers"][i % len(conf["markers"])]
        ax.plot(xs, s.get("values", []), label=s.get("name", f"Series {i}"),
                color=color, marker=marker, markersize=4, alpha=0.9)

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend(fontsize=conf["tick_size"], frameon=False)
    fig.savefig(str(out), format="pdf" if str(out).endswith(".pdf") else "png")
    plt.close(fig)

    return {"output": str(out), "style": style, "type": "line",
            "rendered": True, "width_inches": conf["figure_width"]}


def plot_bar(data: dict, style: str = "ieee", output: str = None) -> dict:
    plt, conf = setup_style(style)
    import matplotlib.pyplot as plt

    out = Path(output or "/tmp/fig_pub_bar.pdf")
    fig, ax = plt.subplots()

    labels = data.get("labels", ["A", "B", "C", "D"])
    values = data.get("values", [0.75, 0.80, 0.82, 0.85])
    colors = [conf["colors"][i % len(conf["colors"])] for i in range(len(labels))]

    ax.bar(range(len(values)), values, color=colors, width=0.6)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=conf["tick_size"])
    ax.set_ylabel("Score")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(str(out), format="pdf" if str(out).endswith(".pdf") else "png")
    plt.close(fig)

    return {"output": str(out), "style": style, "type": "bar", "rendered": True}


def plot_boxplot(data: dict, style: str = "ieee", output: str = None) -> dict:
    plt, conf = setup_style(style)
    import matplotlib.pyplot as plt

    out = Path(output or "/tmp/fig_pub_box.pdf")
    fig, ax = plt.subplots()

    groups = data.get("groups", ["Baseline", "Ours"])
    data_g = data.get("data", [[0.8, 0.82, 0.78, 0.81], [0.88, 0.91, 0.85, 0.89]])
    colors = [conf["colors"][i % len(conf["colors"])] for i in range(len(groups))]

    bp = ax.boxplot(data_g, patch_artist=True, widths=0.5)
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i])
        patch.set_alpha(0.7)
    ax.set_xticklabels(groups, fontsize=conf["tick_size"])
    ax.set_ylabel("Score")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(str(out), format="pdf" if str(out).endswith(".pdf") else "png")
    plt.close(fig)

    return {"output": str(out), "style": style, "type": "boxplot", "rendered": True}


def main():
    parser = argparse.ArgumentParser(description="Publication-quality plotter")
    parser.add_argument("--type", default="line", choices=["line", "bar", "boxplot"])
    parser.add_argument("--style", default="ieee", choices=list(STYLES.keys()))
    parser.add_argument("--data", help="Data JSON file")
    parser.add_argument("--output", default=None, help="Output file (.pdf/.png)")
    args = parser.parse_args()

    data = {}
    if args.data and Path(args.data).exists():
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))

    try:
        if args.type == "line":
            result = plot_line(data, args.style, args.output)
        elif args.type == "bar":
            result = plot_bar(data, args.style, args.output)
        else:
            result = plot_boxplot(data, args.style, args.output)
    except ImportError:
        result = {"status": "skipped", "note": "matplotlib not available"}

    result["status"] = "success" if result.get("rendered") else "mock"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
