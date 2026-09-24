#!/usr/bin/env python3
"""graph_build.py -- extract a knowledge graph from Markdown notes, and export /
analyze it.

Uses only the Python standard library. The graph is a binary structure of
"nodes + edges":

  node  = a note (H1 heading as label, file path as id)
          + candidate entities pulled out of bold words (`candidate` nodes)
  edge  = note->note relation from `[[wiki links]]` (rel = "links")
          + note->candidate relation from a bold word appearing in a note
            (rel = "mentions")

Export formats:
  json    full graph data for downstream programs
  dot     Graphviz, `dot -Tsvg graph.dot -o graph.svg`
  mermaid paste straight into a Markdown doc to render

Subcommands:
  extract <dir>                       extract graph data -> graph.json
  export  <dir> --format {json|dot|mermaid}
  analyze <dir>                       graph metrics: degree-centrality top10 /
                                      connected components / isolated nodes
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
# Bold: **word** or __word__; length-limited so a whole bold paragraph is not
# treated as an entity.
BOLD_RE = re.compile(r"\*\*(?!\s)([^*\n]{1,40}?)(?<!\s)\*\*|__(?!\s)([^_\n]{1,40}?)(?<!\s)__")
# Content inside code blocks and inline code does not participate in entity extraction
# (so code identifiers are not mistaken for concepts).
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


class GraphError(Exception):
    """User-facing error."""


def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise GraphError(f"cannot read {path}: {e}")


def strip_code(text: str) -> str:
    """Remove code blocks and inline code, so identifiers like `foo()` are not extracted as concept entities."""
    return INLINE_CODE_RE.sub(" ", FENCE_RE.sub(" ", text))


def iter_notes(root: Path):
    """Yield all Markdown notes under the root recursively. Skip hidden dirs and assets."""
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in MARKDOWN_SUFFIXES:
            continue
        rel_parts = p.relative_to(root).parts
        if any(part.startswith(".") or part == "assets" for part in rel_parts):
            continue
        yield p


def extract_bold(text: str):
    """Extract bold words as candidate entities, deduplicated in order, filtering pure numbers and too-short items."""
    clean = strip_code(text)
    candidates, seen = [], set()
    for m in BOLD_RE.finditer(clean):
        word = (m.group(1) or m.group(2) or "").strip()
        if not word or word in seen:
            continue
        # pure numbers / pure punctuation are not entities; single ascii chars are usually formatting residue
        if not re.search(r"[A-Za-z\u4e00-\u9fff]", word):
            continue
        if len(word) == 1 and word.isascii():
            continue
        seen.add(word)
        candidates.append(word)
    return candidates


def build_graph(root: Path) -> dict:
    """Scan notes and produce {nodes, edges, meta}."""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise GraphError(f"directory does not exist: {root}")

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
        raise GraphError(f"no Markdown notes (.md/.markdown/.txt) found under {root}")

    # Alias table: both the filename slug and the H1 heading can be link targets
    by_slug = {n["slug"].lower(): n["id"] for n in notes}
    by_label = {n["label"].lower(): n["id"] for n in notes}

    nodes = [{"id": n["id"], "label": n["label"], "type": "note"} for n in notes]
    edges = []
    unresolved = []

    # Candidate-entity nodes: same-named bold words merge across notes to form a "concept hub"
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

    # Deduplicate (the same node pair may be both links and mentions; keep both if rel differs)
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


# ---------------------------------------------------------------- Metrics


def adjacency(graph: dict, rels=None):
    """Undirected adjacency list (graph metrics are computed on the undirected graph to
    better match the intuition of "how tightly things are connected")."""
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
    """Normalized degree centrality: deg / (N-1)."""
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
    """Connected components (BFS), returned as a list of id-lists sorted by size descending."""
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


# ---------------------------------------------------------------- Export


def to_dot(graph: dict, note_only=False) -> str:
    """Graphviz DOT. notes use rounded rectangles, concepts use ellipses to distinguish them."""
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
    """Mermaid flowchart, paste straight into Markdown.

    Path characters in node ids (/ . -) break Mermaid syntax, so they are mapped
    uniformly to n1, n2..., with the original label in square brackets.
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
            lines.append(f"  %% ... edges exceed {max_edges}, truncated; "
                         f"adjust with --max-edges or add --note-only")
            break
        arrow = "-->" if e["rel"] == "links" else "-.->"
        lines.append(f"  {alias[e['source']]} {arrow} {alias[e['target']]}")
        shown += 1
    lines.append("```")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- Subcommands


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
    print("  [nodes]")
    for n in graph["nodes"]:
        print(f"    ({n['type']:<9}) {n['label']}   [{n['id']}]")
    if graph["unresolved_links"]:
        print()
        print("  [unresolved links]")
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
        raise GraphError(f"unknown format: {fmt}")

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

    print(f"  [degree-centrality top {len(top)}]"
          f"{' (notes only)' if args.notes_only else ''}  degree / centrality")
    if top:
        width = max(len(r["label"]) for r in top)
        for r in top:
            bar = "█" * min(r["degree"], 30)
            print(f"    {r['label']:<{width}}  {r['degree']:>3}  "
                  f"{r['centrality']:.4f}  {bar}  ({r['type']})")
    else:
        print("    (none)")

    print()
    print("  [connected components] descending by size")
    for i, c in enumerate(comps[:10], 1):
        labels = {n["id"]: n["label"] for n in graph["nodes"]}
        head = ", ".join(labels.get(x, x) for x in c[:6])
        more = f" ... and {len(c) - 6} more" if len(c) > 6 else ""
        print(f"    #{i}  size={len(c):<3} {head}{more}")
    if len(comps) > 10:
        print(f"    ... and {len(comps) - 10} more components")

    if isolated:
        print()
        print("  [isolated nodes] no edges at all")
        for r in isolated[:15]:
            print(f"    - {r['label']}  ({r['type']})")
        if len(isolated) > 15:
            print(f"    ... and {len(isolated) - 15} more")

    # Structural diagnosis: give an actionable conclusion instead of making the user read numbers
    print()
    n_nodes = len(graph["nodes"])
    if isolated and len(isolated) == n_nodes:
        # no edges at all: the "number of components" carries no information here, say it plainly
        print(f"  [diagnosis] there are no edges in the graph; all {n_nodes} nodes are isolated. "
              f"Start by adding the first [[link]] or bolding a core concept.")
    elif len(comps) > 1 and n_nodes > 3:
        print(f"  [diagnosis] the graph splits into {len(comps)} components; "
              f"the largest covers {len(comps[0])}/{n_nodes} nodes. "
              f"Use [[links]] to connect the isolated parts.")
    else:
        print("  [diagnosis] the graph is a single connected component; notes are well interlinked.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="graph_build.py",
        description="Extract a knowledge graph from Markdown notes and export/analyze it (pure stdlib)",
        epilog="example: python3 graph_build.py extract notes/ && "
               "python3 graph_build.py export notes/ --format mermaid",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("extract", help="extract entities and relations -> graph.json")
    s.add_argument("dir", help="notes directory")
    s.add_argument("--out", help="output path (default <dir>/graph.json)")
    s.set_defaults(func=cmd_extract)

    s = sub.add_parser("export", help="export graph data")
    s.add_argument("dir")
    s.add_argument("--format", choices=["json", "dot", "mermaid"],
                   default="json")
    s.add_argument("--out", help="output file; defaults to stdout")
    s.add_argument("--note-only", action="store_true",
                   help="export only note-to-note links, ignoring candidate-entity nodes")
    s.add_argument("--max-edges", type=int, default=200,
                   help="max mermaid edges (default 200; truncated beyond)")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("analyze", help="graph metrics: centrality / components / isolated nodes")
    s.add_argument("dir")
    s.add_argument("--top", type=int, default=10, help="centrality rows to show (default 10)")
    s.add_argument("--notes-only", action="store_true",
                   help="centrality counts only note nodes, ignoring candidate entities")
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
