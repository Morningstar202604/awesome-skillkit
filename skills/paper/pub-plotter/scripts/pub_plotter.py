#!/usr/bin/env python3
"""Publication Plotter -- publication-grade figures (SOTA: font embedding + real journal physical width + colorblind-safe palette).

Aligned with 2026 best practices for publication-grade figures:
  - Font embedding: pdf.fonttype=42 / ps.fonttype=42 (Type 42 subset embedding,
    so arXiv does not reject the figure)
  - Real journal widths (inches): nature_single=3.504 (89mm), nature_double=7.0,
    science=4.76, ieee=3.5, acm=6.5, neurips=6.0 -- default "draw at the target layout width"
  - Colorblind-safe palette (Paul Tol / Okabe-Ito); --style colorblind_safe on by default
  - Optional real scienceplots package: if installed, `plt.style.use(["science","ieee"])`;
    otherwise use a built-in equivalent preset (works offline, identical behavior)

Two-track semantics (honest): matplotlib missing -> status="mock", no image produced,
MUST tell the user; matplotlib present -> status="success" + rendered=true, the artifact
is a real PDF/PNG.
"""
import argparse
import json
import sys
from pathlib import Path

# real journal physical widths (inches); publication-grade figures should align to the target
# layout rather than using a hand-picked figsize
JOURNAL_WIDTHS = {
    "nature_single": 3.504,  # 89 mm
    "nature_double": 7.0,    # full-page double column
    "science": 4.76,
    "ieee": 3.5,
    "acm": 6.5,
    "neurips": 6.0,
}

# colorblind-safe palette (Paul Tol vivid / Okabe-Ito approximation), on for all styles by default
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
    # --style science was once listed as a valid option with no STYLES entry -> it silently
    # fell back to ieee geometry (the same class of silent error as the journal bug).
    # Add the real entry here: Science single-column 4.76 in; geometry is left to scienceplots
    # (a built-in equivalent rcParams is used if it is not installed).
    "science": {"figure_width": JOURNAL_WIDTHS["science"], "font_size": 7, "tick_size": 6,
                "line_width": 1.0, "markers": ["o", "s", "^", "D"], "grid": "none"},
    "colorblind_safe": {"figure_width": 6.0, "font_size": 10, "tick_size": 8,
                        "line_width": 1.5, "markers": ["o", "s", "^", "D"], "grid": "both"},
}


def setup_style(style_name: str, colorblind: bool = True, journal: str = None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conf = STYLES.get(style_name, STYLES["ieee"]).copy()
    # --journal is a "width directive": it must truly override the style preset width.
    # (The old version stuffed journal into the style name; nature_single/science were not in
    #  STYLES -> it silently fell back to the ieee width, i.e. did not draw at the layout width.
    #  That is a silent error, so we explicitly override it and report it in the return value.)
    if journal:
        if journal not in JOURNAL_WIDTHS:
            raise ValueError(f"unknown journal width: {journal}")
        conf["figure_width"] = JOURNAL_WIDTHS[journal]
    rc = {
        "font.size": conf["font_size"],
        "xtick.labelsize": conf["tick_size"],
        "ytick.labelsize": conf["tick_size"],
        "axes.linewidth": 0.8,
        "lines.linewidth": conf["line_width"],
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        # publication-grade core: vector font subset embedding (Type 42); arXiv / journal LaTeX friendly
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.figsize": (conf["figure_width"], conf["figure_width"] * 0.7),
    }
    # prefer the real scienceplots package (closest to official if installed), otherwise a built-in equivalent rcParams
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
                 "tick": conf["tick_size"], "colors": colors, "scienceplots": sci,
                 "journal": journal}


def _save(fig, out):
    import matplotlib.pyplot as plt
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fmt = "pdf" if out.suffix == ".pdf" else "png"
    fig.savefig(str(out), format=fmt)
    plt.close(fig)
    return str(out)


def plot_line(data: dict, style="ieee", output=None, colorblind=True,
              journal: str = None) -> dict:
    plt, c = setup_style(style, colorblind, journal)
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
    res = {"output": _save(fig, out), "style": style, "journal": journal, "type": "line",
           "rendered": True, "width_inches": c["width"],
           "font_embedded": True, "colorblind_safe": colorblind}
    return res


def plot_bar(data: dict, style="ieee", output=None, colorblind=True,
             journal: str = None) -> dict:
    plt, c = setup_style(style, colorblind, journal)
    out = Path(output or "/tmp/fig_pub_bar.pdf")
    fig, ax = plt.subplots(figsize=(c["width"], c["width"] * 0.7))
    labels = data.get("labels", ["A", "B", "C", "D"])
    values = data.get("values", [0.75, 0.80, 0.82, 0.85])
    colors = [c["colors"][i % len(c["colors"])] for i in range(len(labels))]
    errs = data.get("errors")  # optional CI / error bars
    b = ax.bar(range(len(values)), values, color=colors, width=0.6,
               yerr=(errs if errs else None))
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=c["tick"])
    ax.set_ylabel(data.get("ylabel", "Score"))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return {"output": _save(fig, out), "style": style, "journal": journal, "type": "bar",
            "rendered": True, "width_inches": c["width"],
            "font_embedded": True, "colorblind_safe": colorblind}


def plot_boxplot(data: dict, style="ieee", output=None, colorblind=True,
                 journal: str = None) -> dict:
    plt, c = setup_style(style, colorblind, journal)
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
    return {"output": _save(fig, out), "style": style, "journal": journal, "type": "boxplot",
            "rendered": True, "width_inches": c["width"],
            "font_embedded": True, "colorblind_safe": colorblind}


def plot_heatmap(data: dict, style="ieee", output=None, colorblind=True,
                 journal: str = None) -> dict:
    """Heatmap: all-positive -> cividis (colorblind-safe sequential); contains negatives -> RdBu_r (diverging).

    Data contract: {"matrix": [[...]], "rows": [...], "cols": [...], "annotate": true, "cmap": "?"}
    """
    plt, c = setup_style(style, colorblind, journal)
    try:
        import numpy as np
    except ImportError:
        return {"status": "skipped", "note": "numpy not available (required by matplotlib)"}
    out = Path(output or "/tmp/fig_pub_heatmap.pdf")
    matrix = data.get("matrix", [[0.80, 0.72, 0.65], [0.68, 0.85, 0.79]])
    m = np.asarray(matrix, dtype=float)
    if m.ndim != 2:
        raise ValueError(f"heatmap 'matrix' must be 2-D, got shape {m.shape}")
    rows = data.get("rows", [f"r{i}" for i in range(m.shape[0])])
    cols = data.get("cols", [f"c{j}" for j in range(m.shape[1])])
    vmin, vmax = float(m.min()), float(m.max())

    # colorblind-safe default: cividis for all-positive; diverging RdBu_r across zero (overridable via data.cmap)
    if data.get("cmap"):
        cmap = data["cmap"]
    elif vmin < 0:
        cmap = "RdBu_r"
    elif colorblind:
        cmap = "cividis"
    else:
        cmap = "viridis"

    fig, ax = plt.subplots(figsize=(c["width"] * 0.75, c["width"] * 0.55))
    im = ax.imshow(m, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, fontsize=c["tick"], rotation=45, ha="right")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=c["tick"])
    if data.get("annotate", True):
        span = (vmax - vmin) or 1.0
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                frac = (float(m[i, j]) - vmin) / span
                ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center",
                        fontsize=max(c["tick"] - 1, 5),
                        color="black" if frac > 0.55 else "white")
    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(labelsize=c["tick"])
    if data.get("xlabel"):
        ax.set_xlabel(data["xlabel"])
    if data.get("ylabel"):
        ax.set_ylabel(data["ylabel"])
    return {"output": _save(fig, out), "style": style, "journal": journal, "type": "heatmap",
            "rendered": True, "width_inches": c["width"],
            "font_embedded": True, "colorblind_safe": colorblind,
            "cmap": cmap, "shape": [int(m.shape[0]), int(m.shape[1])],
            "value_range": [vmin, vmax], "annotated": bool(data.get("annotate", True))}


def main():
    ap = argparse.ArgumentParser(description="Publication-quality plotter (SOTA)")
    ap.add_argument("--type", default="line",
                    choices=["line", "bar", "boxplot", "heatmap"])
    ap.add_argument("--style", default="ieee",
                    choices=sorted(set(list(STYLES.keys()) + ["science"])))
    ap.add_argument("--journal", help="draw at the real journal width: nature_single|science|ieee|acm|neurips")
    ap.add_argument("--no-colorblind", action="store_true", help="disable the colorblind-safe palette")
    ap.add_argument("--data", help="Data JSON file")
    ap.add_argument("--output", default=None, help="Output file (.pdf/.png)")
    args = ap.parse_args()

    data = {}
    if args.data and Path(args.data).exists():
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    elif args.data:
        print(json.dumps({"status": "error",
                          "error": f"--data file not found: {args.data} (confirm the path first; do not silently fall back to demo data)"},
                         ensure_ascii=False))
        return 2

    # --style and --journal have separate duties: style governs font size / line width / grid;
    # journal only overrides the **physical width**
    style = args.style
    if args.journal and args.journal not in JOURNAL_WIDTHS:
        print(json.dumps({"status": "error", "error": f"unknown --journal: {args.journal}"},
                         ensure_ascii=False))
        return 2
    colorblind = not args.no_colorblind

    try:
        if args.type == "line":
            res = plot_line(data, style, args.output, colorblind, args.journal)
        elif args.type == "bar":
            res = plot_bar(data, style, args.output, colorblind, args.journal)
        elif args.type == "heatmap":
            res = plot_heatmap(data, style, args.output, colorblind, args.journal)
        else:
            res = plot_boxplot(data, style, args.output, colorblind, args.journal)
    except ImportError:
        res = {"status": "skipped", "note": "matplotlib not available; pip install matplotlib"}
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        return 2

    res["status"] = "success" if res.get("rendered") else "mock"
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
