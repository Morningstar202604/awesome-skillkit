#!/usr/bin/env python3
"""Result Visualizer — 把模型结果变成图表。

用法:
  python3 visualizer.py --data results.json --type line --output plot.png
  python3 visualizer.py --data results.json --type scatter --x t --y y
"""
import argparse
import json
import sys
from pathlib import Path


def plot_line(data: dict, output: str = None) -> dict:
    """Generate line chart from time-series data."""
    out = Path(output or "/tmp/plot_line.png")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        xs = data.get("t", data.get("x", list(range(len(data.get("y", data.get("sweep", [0])))))))
        ys = data.get("y", data.get("values"))
        if ys is None:
            sweep = data.get("sweep", [])
            ys = [item.get("value", 0) if isinstance(item, dict) else item for item in sweep]
        if not ys:
            ys = [0]
        if not xs or len(xs) != len(ys):
            xs = list(range(len(ys)))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(xs, ys, "b-o", markersize=3)
        ax.set_title(data.get("title", "Model Results"))
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(out), dpi=150)
        plt.close(fig)
        return {"output": str(out), "type": "line", "rendered": True}
    except ImportError:
        return {"output": str(out), "type": "line", "rendered": False,
                "note": "matplotlib not installed, data saved only"}
    except Exception:
        return {"output": str(out), "type": "line", "rendered": False,
                "note": "plot failed, data is valid"}


def plot_scatter(data: dict, x_key: str = "x", y_key: str = "y",
                 output: str = None) -> dict:
    out = Path(output or "/tmp/plot_scatter.png")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        xs = data.get(x_key, [])
        ys = data.get(y_key, [])
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(xs, ys, alpha=0.6, s=20)
        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)
        fig.tight_layout()
        fig.savefig(str(out), dpi=150)
        plt.close(fig)
        return {"output": str(out), "type": "scatter", "rendered": True}
    except ImportError:
        return {"output": str(out), "rendered": False}


def plot_histogram(data: dict, output: str = None) -> dict:
    out = Path(output or "/tmp/plot_hist.png")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        samples = data.get("samples", data.get("values", [0]))
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(samples, bins=50, edgecolor="black", alpha=0.7)
        ax.set_title("Distribution")
        fig.tight_layout()
        fig.savefig(str(out), dpi=150)
        plt.close(fig)
        return {"output": str(out), "type": "histogram", "rendered": True}
    except ImportError:
        return {"output": str(out), "rendered": False}


def main():
    parser = argparse.ArgumentParser(description="Visualize model results")
    parser.add_argument("--data", required=True, help="Results JSON file")
    parser.add_argument("--type", default="line", choices=["line", "scatter", "histogram"])
    parser.add_argument("--x", default="t")
    parser.add_argument("--y", default="y")
    parser.add_argument("--output", help="Output image path")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(json.dumps({"status": "skipped", "reason": f"data file not found: {args.data}"},
                         ensure_ascii=False, indent=2))
        return

    data = json.loads(data_path.read_text(encoding="utf-8"))

    if args.type == "line":
        result = plot_line(data, args.output)
    elif args.type == "scatter":
        result = plot_scatter(data, args.x, args.y, args.output)
    else:
        result = plot_histogram(data, args.output)

    result["status"] = "success"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
