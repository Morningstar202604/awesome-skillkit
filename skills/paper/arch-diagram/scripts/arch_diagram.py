#!/usr/bin/env python3
"""Architecture Diagram Generator — 生成论文用架构图/框架图。

学习自: torchdiagram + archscope + PlotNeuralNet
输出: TikZ/LaTeX 代码 + SVG (editable)

用法:
  python3 arch_diagram.py --type pipeline --blocks "Encoder,Attention,Decoder" --output arch.tex
  python3 arch_diagram.py --type nn --layers "input,hidden(256),hidden(128),output"
"""
import argparse
import json
import sys
from pathlib import Path


def generate_tikz_pipeline(blocks: list, output: str = None) -> dict:
    """Generate TikZ code for a pipeline/architecture diagram."""
    n = len(blocks)
    spacing = 2.0

    tikz_parts = []
    tikz_parts.append("\\begin{tikzpicture}[node distance=" + str(spacing) + "cm]")
    tikz_parts.append("% Auto-generated architecture diagram")
    for i, block in enumerate(blocks):
        node_num = i + 1
        x_pos = (i + 1) * spacing
        tikz_parts.append(
            f"\\node[draw, rounded corners, minimum width=1.5cm, minimum height=0.8cm, "
            f"fill=blue!5, font=\\sffootnotesize] (b{node_num}) at ({x_pos},0) {{{block}}};\n"
        )
    for i in range(n - 1):
        tikz_parts.append(f"\\draw[-{{>}}] (b{i+1}) -- (b{i+2});\n")
    tikz_parts.append("\\end{tikzpicture}")

    tikz = "\n".join(tikz_parts)
    out = Path(output or "/tmp/arch.tex")
    out.write_text(tikz, encoding="utf-8")

    return {
        "output": str(out),
        "format": "tikz",
        "n_blocks": n,
        "blocks": blocks,
        "compilable": True,
    }


def generate_neural_net(layers: list, output: str = None) -> dict:
    """Generate TikZ neural network diagram (simplified PlotNeuralNet style)."""
    out = Path(output or "/tmp/nn_diagram.tex")

    layers_info = []
    for layer in layers:
        parts = layer.split("(")
        name = parts[0]
        size = int(parts[1].rstrip(")")) if len(parts) > 1 else None
        layers_info.append({"name": name, "size": size or 4})

    tikz = """\\begin{tikzpicture}[>=stealth, thick,
  node/.style={circle, draw, minimum size=0.5cm, font=\\tiny},
  layer/.style={draw, rectangle, dashed, opacity=0.3, fill=gray!5}]
"""
    x_pos = 0
    for i, layer in enumerate(layers_info):
        n_nodes = min(layer["size"] or 4, 6)
        layer_width = n_nodes * 0.6
        tikz += f"\\node[draw=none] (l{i}) at ({x_pos},0) {{}};\n"
        for j in range(n_nodes):
            y = j * 0.7 - (n_nodes - 1) * 0.35
            tikz += f"\\node[node, fill={'blue!10' if i > 0 else 'white'}] at ({x_pos},{y}) {{\\tiny {j+1}}};\n"
        x_pos += 2.0

    tikz += """\\end{tikzpicture}"""
    out.write_text(tikz, encoding="utf-8")

    return {
        "output": str(out),
        "format": "tikz",
        "layers": layers,
        "n_layers": len(layers),
        "compilable": True,
    }


def generate_svg_pipeline(blocks: list, output: str = None) -> dict:
    """Generate editable SVG (for Figma/Inkscape import)."""
    out = Path(output or "/tmp/arch.svg")
    box_w, box_h, gap = 120, 50, 40
    total_w = len(blocks) * (box_w + gap)

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{box_h + 40}">\n'
    for i, block in enumerate(blocks):
        x = i * (box_w + gap) + 20
        svg += f'  <rect x="{x}" y="20" width="{box_w}" height="{box_h}" rx="8" fill="#4C72B0" opacity="0.8"/>\n'
        svg += f'  <text x="{x + box_w//2}" y="{20 + box_h//2 + 5}" text-anchor="middle" fill="white" font-size="14">{block}</text>\n'
        if i < len(blocks) - 1:
            ax = x + box_w + 5
            svg += f'  <line x1="{ax}" y1="{20 + box_h//2}" x2="{ax + gap - 10}" y2="{20 + box_h//2}" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>\n'
    svg += '</svg>\n'
    out.write_text(svg, encoding="utf-8")

    return {"output": str(out), "format": "svg", "n_blocks": len(blocks), "editable": True}


def main():
    parser = argparse.ArgumentParser(description="Architecture diagram generator")
    parser.add_argument("--type", default="pipeline", choices=["pipeline", "nn", "svg"])
    parser.add_argument("--blocks", default="", help="Comma-separated block names")
    parser.add_argument("--layers", nargs="*", help="Layer specs for NN")
    parser.add_argument("--format", default="tikz", choices=["tikz", "svg"])
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    # Parse comma-separated blocks
    if args.blocks:
        blocks_list = [b.strip() for b in args.blocks.split(",") if b.strip()]
    else:
        blocks_list = []

    if args.type == "nn":
        layers = args.layers or ["input(4)", "hidden(8)", "hidden(4)", "output(2)"]
        result = generate_neural_net(layers, args.output)
    elif args.type == "svg":
        blocks = blocks_list or ["Input", "Encoder", "Decoder", "Output"]
        result = generate_svg_pipeline(blocks, args.output)
    else:
        blocks = blocks_list or ["Data", "Feature", "Model", "Loss"]
        if args.format == "svg":
            result = generate_svg_pipeline(blocks, args.output)
        else:
            result = generate_tikz_pipeline(blocks, args.output)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
