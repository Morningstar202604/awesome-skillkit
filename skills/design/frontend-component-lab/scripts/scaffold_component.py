#!/usr/bin/env python3
"""
scaffold_component.py — 离线生成一个可运行的 React/TS 组件骨架 + 配套
设计 Token 文件。不联网、不依赖 npm（只产出源码文件，用户自己接工程）。

生成物：
  <out>/<name>.tsx         组件（带 Props 接口 + 基础样式）
  <out>/<name>.module.css CSS Modules（从 token 取值，避免魔法数字）
  <out>/design-tokens.json 设计 token（color/spacing/radius/font）

红线：
- 默认 dry-run 打印文件清单 + 摘要，--write 才落盘
- 不引入任何网络请求 / 密钥
- 幂等：同名组件已存在时，dry-run 提示，--write 需 --force 才覆盖
"""
import argparse
import json
import os
import sys
import textwrap

DEFAULT_TOKENS = {
    "color": {
        "brand": "#2563eb",
        "surface": "#ffffff",
        "surface-muted": "#f5f7fa",
        "text": "#111827",
        "text-muted": "#6b7280",
        "border": "#e5e7eb",
        "danger": "#dc2626",
    },
    "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"},
    "radius": {"sm": "6px", "md": "10px", "lg": "16px"},
    "font": {"size-sm": "13px", "size-md": "15px", "size-lg": "18px", "weight": "400"},
}


def merge_tokens(overrides: dict | None) -> dict:
    """浅合并：用户覆盖同层 key，缺的保留默认。"""
    base = json.loads(json.dumps(DEFAULT_TOKENS))
    if not overrides:
        return base
    for layer, kv in overrides.items():
        if layer in base and isinstance(base[layer], dict) and isinstance(kv, dict):
            base[layer].update(kv)
    return base


def render_tsx(name: str, props: list[str], tokens: dict) -> str:
    if not props:
        props = ["className"]
    iface_body = "\n".join(f"  {p}: string;" for p in props)
    lines = []
    lines.append(f"export interface {name}Props {{")
    lines.append(iface_body)
    lines.append("}")
    lines.append("")
    lines.append(f"import styles from './{name}.module.css';")
    lines.append("")
    lines.append(f"export function {name}(props: {name}Props) {{")
    lines.append(f"  return (")
    lines.append(f"    <div className={{styles.root}} data-component=\"{name}\">")
    lines.append("      {/* TODO: render body */}")
    lines.append(f"      <span className={chr(123)+chr(123)+'styles.title'+chr(125)+chr(125)}>")
    lines.append(f"        {name}")
    lines.append(f"      </span>")
    lines.append(f"    </div>")
    lines.append(f"  );")
    lines.append(f"}}")
    lines.append(f"")
    return "\n".join(lines)


def render_css(name: str, tokens: dict) -> str:
    c = tokens["color"]; s = tokens["spacing"]; r = tokens["radius"]; f = tokens["font"]
    return textwrap.dedent(f"""\
      .root {{
        display: flex;
        flex-direction: column;
        gap: {s['sm']};
        padding: {s['md']};
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: {r['md']};
        color: {c['text']};
        font-size: {f['size-md']};
      }}
      .title {{
        font-size: {f['size-lg']};
        color: {c['brand']};
      }}
      .muted {{
        color: {c['text-muted']};
      }}
      """)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a React/TS component + design tokens (offline)")
    ap.add_argument("--name", required=True, help="PascalCase component name, e.g. PricingCard")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--props", default="", help="comma-separated string props, e.g. title,price")
    ap.add_argument("--tokens", default="", help="path to a JSON overriding design tokens")
    ap.add_argument("--force", action="store_true", help="overwrite if files exist")
    ap.add_argument("--write", action="store_true", help="actually write; default is dry-run")
    args = ap.parse_args()

    name = args.name
    if not (name[:1].isupper() and name.isalnum()):
        print(f"[ERROR] --name must be PascalCase alnum, got {name!r}", file=sys.stderr)
        return 2

    tokens = DEFAULT_TOKENS
    if args.tokens:
        with open(args.tokens, "r", encoding="utf-8") as fh:
            tokens = merge_tokens(json.load(fh))

    props = [p.strip() for p in args.props.split(",") if p.strip()]
    files = {
        f"{name}.tsx": render_tsx(name, props, tokens),
        f"{name}.module.css": render_css(name, tokens),
        "design-tokens.json": json.dumps(tokens, indent=2, ensure_ascii=False),
    }

    conflicts = [os.path.join(args.out, f) for f in files if os.path.exists(os.path.join(args.out, f))]

    print(f"Component: {name} | props: {props or ['(className default)']}")
    print("Files to produce:")
    for fname, content in files.items():
        target = os.path.join(args.out, fname)
        mark = "  (exists)" if target in conflicts else ""
        print(f"  {target}{mark}")

    if conflicts and not args.force:
        print(f"\n[DRY-RUN] {len(conflicts)} file(s) already exist. "
              f"Re-run with --write --force to overwrite, or --write to skip dry-run.")
        if not args.write:
            return 0
        print("[DRY-RUN] (no --write) nothing written.")
        return 0

    if args.write:
        os.makedirs(args.out, exist_ok=True)
        for fname, content in files.items():
            with open(os.path.join(args.out, fname), "w", encoding="utf-8") as fh:
                fh.write(content)
        print(f"\n[WRITE] generated {len(files)} file(s) under {args.out}/")
    else:
        print(f"\n[DRY-RUN] no file written. Re-run with --write (and --force to overwrite) to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
