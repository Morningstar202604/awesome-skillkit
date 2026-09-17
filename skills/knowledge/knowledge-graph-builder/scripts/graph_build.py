#!/usr/bin/env python3
"""graph_build.py — 从 Markdown 笔记抽取知识图谱，并导出 / 分析。

只用 Python 标准库。图谱是「节点 + 边」的二元结构：

  节点（node） = 一篇笔记（H1 标题为 label，文件路径为 id）
                 + 加粗词抽出的候选实体（`candidate` 节点）
  边（edge）   = `[[wiki 链接]]` 产生的 note→note 关系（rel = "links"）
                 + 加粗词出现在某篇笔记中产生的 note→candidate 关系（rel = "mentions"）

导出格式：
  json    完整图数据，供下游程序消费
  dot     Graphviz，`dot -Tsvg graph.dot -o graph.svg`
  mermaid 直接贴进 Markdown 文档渲染

子命令:
  extract <dir>                       抽取图数据 → graph.json
  export  <dir> --format {json|dot|mermaid}
  analyze <dir>                       图指标：度中心性 top10 / 连通分量 / 孤立节点
"""

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

MARKDOWN_SUFFIXES = {".md", ".markdown", ".txt"}
GRAPH_FILE = "graph.json"

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]*))?\]\]")
# 加粗：**词** 或 __词__；限制长度避免把整段粗体当成实体
BOLD_RE = re.compile(r"\*\*(?!\s)([^*\n]{1,40}?)(?<!\s)\*\*|__(?!\s)([^_\n]{1,40}?)(?<!\s)__")
# 代码块与行内代码里的内容不参与实体抽取（避免把代码标识符当概念）
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


class GraphError(Exception):
    """面向用户的错误。"""


def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise GraphError(f"无法读取 {path}: {e}")


def strip_code(text: str) -> str:
    """去掉代码块与行内代码，防止把 `foo()` 之类的标识符抽成概念实体。"""
    return INLINE_CODE_RE.sub(" ", FENCE_RE.sub(" ", text))


def iter_notes(root: Path):
    """递归产出根目录下所有 Markdown 笔记。跳过隐藏目录与 assets。"""
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in MARKDOWN_SUFFIXES:
            continue
        rel_parts = p.relative_to(root).parts
        if any(part.startswith(".") or part == "assets" for part in rel_parts):
            continue
        yield p


def extract_bold(text: str):
    """抽取加粗词作为候选实体，去重保序，过滤纯数字与过短项。"""
    clean = strip_code(text)
    candidates, seen = [], set()
    for m in BOLD_RE.finditer(clean):
        word = (m.group(1) or m.group(2) or "").strip()
        if not word or word in seen:
            continue
        # 纯数字/纯标点不当实体；单字符英文多为格式残留
        if not re.search(r"[A-Za-z\u4e00-\u9fff]", word):
            continue
        if len(word) == 1 and word.isascii():
            continue
        seen.add(word)
        candidates.append(word)
    return candidates


def build_graph(root: Path) -> dict:
    """扫描笔记，产出 {nodes, edges, meta}。"""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise GraphError(f"目录不存在：{root}")

    notes = []
    for p in iter_notes(root):
        text = read_text(p)
        m = H1_RE.search(text)
        rel = p.relative_to(root).as_posix()
        notes.append({
            "id": rel,
            "label": m.group(1).strip() if m else p.stem,
            "slug": p.stem,
            "text": text,
        })

    if not notes:
        raise GraphError(f"{root} 下没有找到 Markdown 笔记（.md/.markdown/.txt）")

    # 别名表：文件名 slug 与 H1 标题都能作为链接目标
    by_slug = {n["slug"].lower(): n["id"] for n in notes}
    by_label = {n["label"].lower(): n["id"] for n in notes}

    nodes = [{"id": n["id"], "label": n["label"], "type": "note"} for n in notes]
    edges = []
    unresolved = []

    # 候选实体节点：同名加粗词跨笔记合并，形成「概念中枢」
    cand_index: dict[str, str] = {}

    for n in notes:
        for target, _alias in WIKILINK_RE.findall(n["text"]):
            key = target.strip().lower()
            dest = by_slug.get(key) or by_label.get(key)
            if dest and dest != n["id"]:
                edges.append({"source": n["id"], "target": dest, "rel": "links"})
            elif not dest:
                unresolved.append({"from": n["id"], "target": target.strip()})

        for word in extract_bold(n["text"]):
            cid = f"concept:{word.lower()}"
            if cid not in cand_index:
                cand_index[cid] = word
                nodes.append({"id": cid, "label": word, "type": "candidate"})
            edges.append({"source": n["id"], "target": cid, "rel": "mentions"})

    # 去重（同一对节点可能既 links 又 mentions，rel 不同则都保留）
    seen_e, uniq = set(), []
    for e in edges:
        k = (e["source"], e["target"], e["rel"])
        if k not in seen_e:
            seen_e.add(k)
            uniq.append(e)

    return {
        "schema": 1,
        "root_name": root.name,
        "meta": {
            "note_count": len(notes),
            "concept_count": len(cand_index),
            "edge_count": len(uniq),
            "unresolved_links": len(unresolved),
        },
        "nodes": nodes,
        "edges": uniq,
        "unresolved_links": unresolved,
    }


# ---------------------------------------------------------------- 指标计算


def adjacency(graph: dict, rels=None):
    """无向邻接表（图指标按无向图算更贴近「关联紧密程度」的直觉）。"""
    adj = defaultdict(set)
    for n in graph["nodes"]:
        adj[n["id"]]
    for e in graph["edges"]:
        if rels and e["rel"] not in rels:
            continue
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])
    return adj


def degree_centrality(graph: dict):
    """归一化度中心性：deg / (N-1)。"""
    adj = adjacency(graph)
    n = len(graph["nodes"])
    if n <= 1:
        return []
    denom = n - 1
    label = {x["id"]: x["label"] for x in graph["nodes"]}
    kind = {x["id"]: x["type"] for x in graph["nodes"]}
    rows = [
        {
            "id": nid,
            "label": label[nid],
            "type": kind[nid],
            "degree": len(nb),
            "centrality": round(len(nb) / denom, 4),
        }
        for nid, nb in adj.items()
    ]
    rows.sort(key=lambda r: (-r["degree"], r["id"]))
    return rows


def components(graph: dict, rels=None):
    """连通分量（BFS），返回按大小降序的 id 列表的列表。"""
    adj = adjacency(graph, rels)
    seen, comps = set(), []
    for nid in adj:
        if nid in seen:
            continue
        q, group = deque([nid]), []
        seen.add(nid)
        while q:
            cur = q.popleft()
            group.append(cur)
            for nb in adj[cur]:
                if nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        comps.append(sorted(group))
    comps.sort(key=len, reverse=True)
    return comps


# ---------------------------------------------------------------- 导出


def to_dot(graph: dict, note_only=False) -> str:
    """Graphviz DOT。note 用圆角矩形，concept 用椭圆以示区分。"""
    def esc(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')

    lines = [
        "digraph knowledge {",
        '  rankdir=LR;',
        '  node [shape=box, style="rounded,filled", fillcolor="#EAF2FB", '
        'fontname="Helvetica"];',
        '  edge [color="#7A8A99", arrowsize=0.7];',
    ]
    for n in graph["nodes"]:
        if note_only and n["type"] != "note":
            continue
        shape = "box" if n["type"] == "note" else "ellipse"
        fill = "#EAF2FB" if n["type"] == "note" else "#FDF3D8"
        lines.append(
            f'  "{esc(n["id"])}" [label="{esc(n["label"])}", '
            f'shape={shape}, fillcolor="{fill}"];'
        )
    for e in graph["edges"]:
        if note_only and e["rel"] != "links":
            continue
        style = "solid" if e["rel"] == "links" else "dashed"
        lines.append(
            f'  "{esc(e["source"])}" -> "{esc(e["target"])}" [style={style}];'
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_mermaid(graph: dict, note_only=False, max_edges=200) -> str:
    """Mermaid flowchart，可直接贴进 Markdown。

    节点 id 里的路径字符（/ . -）会破坏 Mermaid 语法，
    因此统一映射成 n1、n2…，原标签放在方括号里。
    """
    def esc(s):
        return s.replace('"', "'").replace("[", "(").replace("]", ")")

    keep = [n for n in graph["nodes"] if not note_only or n["type"] == "note"]
    alias = {n["id"]: f"n{i}" for i, n in enumerate(keep)}

    lines = ["```mermaid", "flowchart LR"]
    for n in keep:
        if n["type"] == "note":
            lines.append(f'  {alias[n["id"]]}["{esc(n["label"])}"]')
        else:
            lines.append(f'  {alias[n["id"]]}(["{esc(n["label"])}"])')

    shown = 0
    for e in graph["edges"]:
        if e["source"] not in alias or e["target"] not in alias:
            continue
        if shown >= max_edges:
            lines.append(f"  %% ... 边数超过 {max_edges}，已截断；"
                         f"用 --max-edges 调整或加 --note-only")
            break
        arrow = "-->" if e["rel"] == "links" else "-.->"
        lines.append(f"  {alias[e['source']]} {arrow} {alias[e['target']]}")
        shown += 1
    lines.append("```")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 子命令


def cmd_extract(args) -> int:
    graph = build_graph(Path(args.dir))
    out = Path(args.out) if args.out else Path(args.dir).expanduser() / GRAPH_FILE
    out.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    m = graph["meta"]
    print(f"extracted: {out}")
    print(f"  nodes          : {len(graph['nodes'])} "
          f"(note {m['note_count']} / candidate {m['concept_count']})")
    print(f"  edges          : {m['edge_count']}")
    print(f"  unresolved     : {m['unresolved_links']}")
    print()
    print("  [节点]")
    for n in graph["nodes"]:
        print(f"    ({n['type']:<9}) {n['label']}   [{n['id']}]")
    if graph["unresolved_links"]:
        print()
        print("  [未解析链接]")
        for u in graph["unresolved_links"]:
            print(f"    {u['from']} -> [[{u['target']}]]")
    return 0


def cmd_export(args) -> int:
    graph = build_graph(Path(args.dir))
    fmt = args.format
    if fmt == "json":
        body = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    elif fmt == "dot":
        body = to_dot(graph, note_only=args.note_only)
    elif fmt == "mermaid":
        body = to_mermaid(graph, note_only=args.note_only,
                          max_edges=args.max_edges)
    else:
        raise GraphError(f"未知格式：{fmt}")

    if args.out:
        Path(args.out).write_text(body, encoding="utf-8")
        print(f"exported ({fmt}): {args.out}")
        print(f"  bytes: {len(body.encode('utf-8'))}")
    else:
        sys.stdout.write(body)
    return 0


def cmd_analyze(args) -> int:
    graph = build_graph(Path(args.dir))
    rows = degree_centrality(graph)
    comps = components(graph)

    note_rows = [r for r in rows if r["type"] == "note"]
    isolated = [r for r in rows if r["degree"] == 0]
    top = (note_rows if args.notes_only else rows)[: args.top]

    print(f"analyze: {graph['root_name']}")
    m = graph["meta"]
    print(f"  nodes            : {len(graph['nodes'])} "
          f"(note {m['note_count']} / candidate {m['concept_count']})")
    print(f"  edges            : {m['edge_count']}")
    print(f"  components       : {len(comps)}")
    print(f"  isolated nodes   : {len(isolated)}")
    print()

    print(f"  [度中心性 top {len(top)}]"
          f"{'（仅笔记）' if args.notes_only else ''}  degree / centrality")
    if top:
        width = max(len(r["label"]) for r in top)
        for r in top:
            bar = "█" * min(r["degree"], 30)
            print(f"    {r['label']:<{width}}  {r['degree']:>3}  "
                  f"{r['centrality']:.4f}  {bar}  ({r['type']})")
    else:
        print("    (无)")

    print()
    print("  [连通分量] 按规模降序")
    for i, c in enumerate(comps[:10], 1):
        labels = {n["id"]: n["label"] for n in graph["nodes"]}
        head = ", ".join(labels.get(x, x) for x in c[:6])
        more = f" … 另 {len(c) - 6} 个" if len(c) > 6 else ""
        print(f"    #{i}  size={len(c):<3} {head}{more}")
    if len(comps) > 10:
        print(f"    ... 另有 {len(comps) - 10} 个分量")

    if isolated:
        print()
        print("  [孤立节点] 无任何连边")
        for r in isolated[:15]:
            print(f"    - {r['label']}  ({r['type']})")
        if len(isolated) > 15:
            print(f"    ... 另有 {len(isolated) - 15} 个")

    # 结构诊断：给一句可执行的结论，而不是让用户自己看数字
    print()
    n_nodes = len(graph["nodes"])
    if isolated and len(isolated) == n_nodes:
        # 一条边都没有：分量的「数量」在这里没有信息量，直接说破
        print(f"  [诊断] 图中没有任何连边，{n_nodes} 个节点全部孤立；"
              f"先从建立第一条 [[链接]] 或加粗一个核心概念开始。")
    elif len(comps) > 1 and n_nodes > 3:
        print(f"  [诊断] 图分裂成 {len(comps)} 个分量，"
              f"最大分量覆盖 {len(comps[0])}/{n_nodes} 个节点；"
              f"用 [[链接]] 把孤立部分接进来。")
    else:
        print("  [诊断] 图是单一连通分量，笔记间关联良好。")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="graph_build.py",
        description="从 Markdown 笔记抽取知识图谱并导出/分析（纯标准库）",
        epilog="示例：python3 graph_build.py extract notes/ && "
               "python3 graph_build.py export notes/ --format mermaid",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("extract", help="抽取实体与关系 → graph.json")
    s.add_argument("dir", help="笔记目录")
    s.add_argument("--out", help="输出路径（默认 <dir>/graph.json）")
    s.set_defaults(func=cmd_extract)

    s = sub.add_parser("export", help="导出图数据")
    s.add_argument("dir")
    s.add_argument("--format", choices=["json", "dot", "mermaid"],
                   default="json")
    s.add_argument("--out", help="输出文件；省略则打到 stdout")
    s.add_argument("--note-only", action="store_true",
                   help="只导出笔记间链接，忽略候选实体节点")
    s.add_argument("--max-edges", type=int, default=200,
                   help="mermaid 最大边数（默认 200，超出截断）")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("analyze", help="图指标：中心性/连通分量/孤立节点")
    s.add_argument("dir")
    s.add_argument("--top", type=int, default=10, help="中心性显示条数（默认 10）")
    s.add_argument("--notes-only", action="store_true",
                   help="中心性只统计笔记节点，忽略候选实体")
    s.set_defaults(func=cmd_analyze)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except GraphError as e:
        die(str(e))
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
