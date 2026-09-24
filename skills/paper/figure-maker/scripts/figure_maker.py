#!/usr/bin/env python3
"""Figure Maker -- **DEPRECATED**: this skill has been merged into `pub-plotter`.

The original CLI and JSON contract are kept (`--data` / `--type bar|line|boxplot|heatmap` /
`--output`); internally it **delegates to** `pub-plotter/scripts/pub_plotter.py`, so:
  - existing external callers keep running with no changes;
  - but the output gains `deprecated: true` / `superseded_by: "pub-plotter"` fields, and
    `heatmap` changes from "returns unsupported" to **real rendering** (pub-plotter already implements it).

Why not delete it outright: the in-repo indexes (manifest.json / packs / skill_chains.json /
the generated site/ still reference this skill by name, and external callers may have pinned
this CLI; deleting it would break them. (The in-repo **code** consumer `paper_pipeline.py`
has already migrated to pub-plotter.) Keeping the thin shim = de-duplicated implementation +
no broken consumers + explicit deprecation surface.

Migration: switch the call directly to
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
    """Load the pub-plotter implementation by relative path (no sys.path pollution, no package layout required)."""
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
    parser.add_argument("--journal", help="passed through to pub-plotter: nature_single|science|ieee|acm|neurips")
    parser.add_argument("--no-colorblind", action="store_true",
                        help="passed through to pub-plotter: disable the colorblind-safe palette")
    args = parser.parse_args()

    data = {}
    if args.data:
        p = Path(args.data)
        if not p.exists():
            print(json.dumps({"status": "error",
                              "error": f"--data file not found: {args.data}"},
                             ensure_ascii=False))
            return 2
        data = json.loads(p.read_text(encoding="utf-8"))

    mod, target = _load_pub_plotter()
    if mod is None:
        # honest degradation: when the delegation target is missing, error explicitly; never pretend success
        print(json.dumps({"status": "error",
                          "error": f"delegation target missing: {target}",
                          "deprecated": True, "superseded_by": "pub-plotter"},
                         ensure_ascii=False, indent=2))
        return 1

    style = "ieee"
    journal = None
    if args.journal:
        if args.journal not in mod.JOURNAL_WIDTHS:
            print(json.dumps({"status": "error", "error": f"unknown --journal: {args.journal}",
                              "deprecated": True, "superseded_by": "pub-plotter"},
                             ensure_ascii=False, indent=2))
            return 2
        journal = args.journal

    fn = getattr(mod, _DISPATCH[args.type])
    try:
        res = fn(data, style, args.output, not args.no_colorblind, journal)
    except ImportError:
        res = {"status": "skipped", "note": "matplotlib not available; pip install matplotlib"}
    except ValueError as e:
        # same contract as pub-plotter: invalid data (e.g. a heatmap that is not a 2-D array) must error, never silently emit a plot
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
