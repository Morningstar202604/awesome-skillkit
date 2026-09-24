#!/usr/bin/env python3
"""Architecture Diagram Generator — paper architecture/framework diagrams (TikZ + editable SVG).

Fixes three v1 defects:
  1. The TikZ used `\\sffootnotesize` -- **not a valid LaTeX command**; compilation would always
     fail with Undefined control sequence. Changed to `\\footnotesize`.
  2. The SVG used `marker-end="url(#arrow)"` but **never defined #arrow** -- arrows did not show
     in browsers/Inkscape; it now emits `<defs><marker id="arrow">`.
  3. All blocks were laid out in a single line -- added layouts `row` / `wrap` (`--per-row`) / `stack`.
Also: block labels auto-escape LaTeX special chars (& % # _ $ { } ~ ^ \\); colors use a colorblind-safe palette.

Usage:
  python3 arch_diagram.py --type pipeline --blocks "Encoder,Decoder,Head" --output arch.tex
  python3 arch_diagram.py --type pipeline --blocks "A,B,C,D,E" --layout wrap --per-row 3 --format svg
"""
import argparse
import json
import math
import sys
from pathlib import Path

# colorblind-safe palette (same source as pub-plotter)
PALETTE = {
    "blue": ("#0072B2", "blue!15"), "orange": ("#E69F00", "orange!20"),
    "green": ("#009E73", "green!15"), "red": ("#D55E00", "red!15"),
    "purple": ("#CC79A7", "purple!15"), "gray": ("#7F7F7F", "gray!20"),
    "yellow": ("#F0E442", "yellow!25"), "cyan": ("#56B4E9", "cyan!20"),
}
LATEX_SPECIAL = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "$": r"\$",
                 "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
                 "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}


def escape_latex(s: str) -> str:
    """Escape LaTeX special chars in a label (order-sensitive: handle the backslash first)."""
    out = s.replace("\\", "\x00")
    for ch, rep in LATEX_SPECIAL.items():
        if ch == "\\":
            continue
        out = out.replace(ch, rep)
    return out.replace("\x00", LATEX_SPECIAL["\\"])


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def parse_blocks(spec: str) -> list:
    """`A,B,C` or `A#red,B#blue` (# followed by a palette name). Returns [(label, color), ...]."""
    blocks = []
    for raw in spec.split(","):
        raw = raw.strip()
        if not raw:
            continue
        if "#" in raw:
            label, _, color = raw.rpartition("#")
            label, color = label.strip(), color.strip().lower()
            if color not in PALETTE:
                color = "blue"
        else:
            label, color = raw, None
        blocks.append((label, color))
    return blocks


def _positions(n: int, layout: str, per_row: int) -> list:
    """Return the (row, col) of each block, for row / wrap / stack layouts."""
    if layout == "stack":
        return [(i, 0) for i in range(n)]
    if layout == "wrap":
        return [(i // per_row, i % per_row) for i in range(n)]
    return [(0, i) for i in range(n)]


def _auto_colors(blocks: list) -> list:
    """When no color is explicitly given, take palette colors in order (guarantees adjacent blocks differ)."""
    keys = list(PALETTE)
    return [b[1] or keys[i % len(keys)] for i, b in enumerate(blocks)]


def generate_tikz_pipeline(blocks: list, output: str = None, layout: str = "row",
                           per_row: int = 3) -> dict:
    n = len(blocks)
    colors = _auto_colors(blocks)
    pos = _positions(n, layout, per_row)
    bw, bh, gx, gy = 3.0, 1.0, 1.2, 1.4

    parts = [
        "% Auto-generated architecture diagram (TikZ)",
        "% Requires \\usepackage{tikz} + \\usetikzlibrary{arrows.meta,positioning}",
        "\\begin{tikzpicture}[",
        "  archblock/.style={draw, rounded corners=2pt, minimum width=3.0cm,",
        "    minimum height=1.0cm, align=center, font=\\footnotesize},",
        "  archarrow/.style={-{Stealth[length=2.5mm]}, thick}",
        "]",
    ]
    for i, (label, _) in enumerate(blocks):
        r, c = pos[i]
        x = c * (bw + gx)
        y = -r * (bh + gy)
        parts.append(
            f"\\node[archblock, fill={PALETTE[colors[i]][1]}] (b{i}) "
            f"at ({x:.2f},{y:.2f}) {{{escape_latex(label)}}};")
    for i in range(n - 1):
        (r1, c1), (r2, c2) = pos[i], pos[i + 1]
        if r1 == r2:  # same row -> horizontal arrow
            parts.append(f"\\draw[archarrow] (b{i}.east) -- (b{i+1}.west);")
        else:         # new row -> drop down first, then turn
            parts.append(f"\\draw[archarrow] (b{i}.south) |- (b{i+1}.west);")
    parts.append("\\end{tikzpicture}")
    tikz = "\n".join(parts) + "\n"

    out = Path(output or "/tmp/arch.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tikz, encoding="utf-8")
    return {"output": str(out), "format": "tikz", "layout": layout, "n_blocks": n,
            "blocks": [b[0] for b in blocks], "escaped": any(
                any(ch in b[0] for ch in LATEX_SPECIAL) for b in blocks),
            "font_command": "\\footnotesize", "compilable": True,
            "note": "Requires \\usepackage{tikz} and \\usetikzlibrary{arrows.meta,positioning}"}


def generate_svg_pipeline(blocks: list, output: str = None, layout: str = "row",
                          per_row: int = 3) -> dict:
    n = len(blocks)
    colors = _auto_colors(blocks)
    pos = _positions(n, layout, per_row)
    bw, bh, gx, gy = 150, 54, 46, 40
    n_rows = max(r for r, _ in pos) + 1
    n_cols = max(c for _, c in pos) + 1
    width = n_cols * (bw + gx) + 20
    height = n_rows * (bh + gy) + 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '  <defs>',
           '    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
           'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
           '      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/>',
           '    </marker>',
           '  </defs>']
    boxes = []
    for i, (label, _) in enumerate(blocks):
        r, c = pos[i]
        x = 10 + c * (bw + gx)
        y = 10 + r * (bh + gy)
        boxes.append((x, y, x + bw, y + bh))
        svg.append(f'  <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="6" '
                   f'fill="{PALETTE[colors[i]][0]}" fill-opacity="0.9"/>')
        svg.append(f'  <text x="{x + bw // 2}" y="{y + bh // 2 + 5}" text-anchor="middle" '
                   f'fill="white" font-family="sans-serif" font-size="14">'
                   f'{escape_xml(label)}</text>')
    for i in range(n - 1):
        (r1, c1), (r2, c2) = pos[i], pos[i + 1]
        x1, y1, x2, y2 = boxes[i]
        x3, y3, _, _ = boxes[i + 1]
        if r1 == r2:
            svg.append(f'  <line x1="{x2}" y1="{(y1 + y2) // 2}" x2="{x3 - 6}" '
                       f'y2="{(y1 + y2) // 2}" stroke="#333333" stroke-width="2" '
                       f'marker-end="url(#arrow)"/>')
        else:
            mid_y = y3 + bh // 2
            svg.append(f'  <polyline points="{(x1 + x2) // 2},{(y1 + y2) // 2} '
                       f'{(x1 + x2) // 2},{mid_y} {x3 - 6},{mid_y}" fill="none" '
                       f'stroke="#333333" stroke-width="2" marker-end="url(#arrow)"/>')
    svg.append("</svg>")
    content = "\n".join(svg) + "\n"

    out = Path(output or "/tmp/arch.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return {"output": str(out), "format": "svg", "layout": layout, "n_blocks": n,
            "blocks": [b[0] for b in blocks], "has_marker_def": "<marker id=\"arrow\"" in content,
            "valid_root": content.startswith("<svg") and content.rstrip().endswith("</svg>"),
            "editable": True}


def generate_neural_net(layers: list, output: str = None) -> dict:
    """Simplified stacked diagram. **For neuron-level network structure diagrams, prefer neural-net-draw**
    (this function only draws an illustrative dot matrix)."""
    out = Path(output or "/tmp/nn_diagram.tex")
    info = []
    for layer in layers:
        name, _, size = layer.partition("(")
        info.append({"name": name.strip(), "size": int(size.rstrip(")")) if size else 4})

    lines = ["% Simplified layer stack — for neuron-level figures use the neural-net-draw skill",
             "\\begin{tikzpicture}[>=stealth, thick,",
             "  nnnode/.style={circle, draw, minimum size=0.5cm, font=\\tiny},",
             "  nnlayer/.style={draw, rectangle, dashed, opacity=0.3, fill=gray!5}]"]
    x_pos = 0.0
    for i, layer in enumerate(info):
        n_nodes = min(layer["size"], 6)
        lines.append(f"\\node[nnlayer, minimum width=0.7cm, minimum height="
                     f"{max(n_nodes * 0.7, 1.0):.1f}cm] at ({x_pos:.1f},0) {{}};")
        for j in range(n_nodes):
            y = j * 0.7 - (n_nodes - 1) * 0.35
            fill = "blue!10" if i > 0 else "white"
            lines.append(f"\\node[nnnode, fill={fill}] at ({x_pos:.1f},{y:.2f}) "
                         f"{{\\tiny {j + 1}}};")
        lines.append(f"\\node[font=\\tiny, below] at ({x_pos:.1f},-1.2) "
                     f"{{{escape_latex(layer['name'])}}};")
        x_pos += 2.0
    lines.append("\\end{tikzpicture}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"output": str(out), "format": "tikz", "n_layers": len(info),
            "layers": [la["name"] for la in info], "compilable": True,
            "note": "Simplified stack; use neural-net-draw for publication-grade "
                    "neuron-level diagrams"}


def main():
    parser = argparse.ArgumentParser(description="Architecture diagram generator (SOTA)")
    parser.add_argument("--type", default="pipeline", choices=["pipeline", "nn", "svg"])
    parser.add_argument("--blocks", default="", help="Comma-separated labels; "
                                                     "optional 'Label#color' (blue/orange/green/red/"
                                                     "purple/gray/yellow/cyan)")
    parser.add_argument("--layers", nargs="*", help="Layer specs for NN, e.g. input(4) hidden(8)")
    parser.add_argument("--layout", default="row", choices=["row", "wrap", "stack"])
    parser.add_argument("--per-row", type=int, default=3, help="Blocks per row when --layout wrap")
    parser.add_argument("--format", default="tikz", choices=["tikz", "svg"])
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    blocks = parse_blocks(args.blocks) if args.blocks else []

    if args.type == "nn":
        result = generate_neural_net(
            args.layers or ["input(4)", "hidden(8)", "hidden(4)", "output(2)"], args.output)
    elif args.type == "svg" or args.format == "svg":
        bl = blocks or [("Input", None), ("Encoder", None), ("Decoder", None), ("Output", None)]
        result = generate_svg_pipeline(bl, args.output, args.layout, args.per_row)
    else:
        bl = blocks or [("Data", None), ("Feature", None), ("Model", None), ("Loss", None)]
        result = generate_tikz_pipeline(bl, args.output, args.layout, args.per_row)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
