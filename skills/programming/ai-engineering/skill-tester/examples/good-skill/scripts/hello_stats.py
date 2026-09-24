#!/usr/bin/env python3
"""hello_stats -- the demonstration script for good-skill.

The five disciplines a "qualified skill" script should follow (each maps to one check in
quality_scorer / script_tester):

1. stdlib-only        -- repo policy: scripts under scripts/ may use only the standard library.
2. __main__ guard     -- zero side effects when imported (script_tester runs an AST check).
3. --help self-describes -- provided automatically by argparse; the first entry point for troubleshooting.
4. --json machine-readable -- the prerequisite for CI integration and golden comparison.
5. readable error paths -- even on failure: non-zero exit code + stderr telling the user "what to do next".

Function: given a set of numbers (comma-separated CLI arg, or an --input file, or stdin),
compute basic statistics, with percentile and output-precision control.
"""

import argparse
import json
import sys

DEFAULT_PRECISION = 4


def parse_numbers(raw):
    """Parse a comma-separated number string into a float list; raise ValueError on any bad item.

    >>> parse_numbers("1, 2,3.5")
    [1.0, 2.0, 3.5]
    """
    items = [s.strip() for s in raw.replace("\n", ",").split(",") if s.strip()]
    if not items:
        raise ValueError("empty input")
    return [float(s) for s in items]


def read_numbers_from_path(path):
    """Read numbers from a text file: collect by line; commas/whitespace within a line both split."""
    numbers = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            for token in line.replace(",", " ").split():
                numbers.append(float(token))
    if not numbers:
        raise ValueError(f"no numbers found in {path}")
    return numbers


def percentile(sorted_vals, pct):
    """Linear-interpolation percentile (a simplified version consistent with numpy's default linear method).

    >>> percentile([1.0, 2.0, 3.0, 4.0], 50)
    2.5
    """
    if not 0 <= pct <= 100:
        raise ValueError("percentile must be in [0, 100]")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * pct / 100.0
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def compute_stats(numbers, pcts=(50,)):
    """Compute statistics over a set of numbers; pcts lists the percentiles to output (e.g. 50/90/99)."""
    n = len(numbers)
    mean = sum(numbers) / n
    sorted_vals = sorted(numbers)
    mid = n // 2
    if n % 2:
        median = sorted_vals[mid]
    else:
        median = (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    variance = sum((x - mean) ** 2 for x in numbers) / n
    stats = {
        "count": n,
        "mean": mean,
        "median": median,
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "stddev": variance ** 0.5,
    }
    for pct in pcts:
        stats[f"p{int(pct)}"] = percentile(sorted_vals, pct)
    return stats


def round_stats(stats, precision):
    """Round float values to the given precision (the case where median may be an int is unified by float())."""
    out = {}
    for key, val in stats.items():
        out[key] = round(float(val), precision)
    return out


def render_table(stats, precision):
    """Human-readable table output."""
    lines = ["=== Statistics ==="]
    for key, val in stats.items():
        if isinstance(val, float):
            lines.append(f"{key:>8}: {val:.{precision}f}")
        else:
            lines.append(f"{key:>8}: {val}")
    return "\n".join(lines)


def build_parser():
    ap = argparse.ArgumentParser(
        prog="hello_stats",
        description="Compute basic statistics over a set of numbers (good-skill demo script).",
        epilog="Example: hello_stats 1,2,3.5,4 --json; cat data.txt | hello_stats -",
    )
    ap.add_argument("numbers", nargs="?", default=None,
                    help="comma-separated numbers, e.g. 1,2,3.5; use '-' to read from stdin")
    ap.add_argument("--input", dest="input_path", default=None,
                    help="read numbers from a text file (commas/whitespace within a line split)")
    ap.add_argument("--json", action="store_true", help="emit JSON (machine-readable)")
    ap.add_argument("--percentiles", default="50",
                    help="comma-separated percentile list, e.g. 50,90,99 (default 50)")
    ap.add_argument("--precision", type=int, default=DEFAULT_PRECISION,
                    help=f"float output precision (default {DEFAULT_PRECISION} decimal places)")
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)

    try:
        pcts = [float(p) for p in args.percentiles.split(",") if p.strip()]
    except ValueError:
        print("error: --percentiles accepts only comma-separated numbers, e.g. 50,90,99", file=sys.stderr)
        return 2

    try:
        if args.input_path:
            numbers = read_numbers_from_path(args.input_path)
        elif args.numbers == "-":
            numbers = parse_numbers(sys.stdin.read())
        elif args.numbers:
            numbers = parse_numbers(args.numbers)
        else:
            print("error: missing numbers argument; example: hello_stats 1,2,3.5 or --input data.txt",
                  file=sys.stderr)
            return 2
        stats = compute_stats(numbers, pcts=pcts)
    except ValueError as e:
        print(f"error: cannot parse input ({e}); example: hello_stats 1,2,3.5,4", file=sys.stderr)
        return 2

    stats = round_stats(stats, max(0, args.precision))
    if args.json:
        payload = {"stats": stats, "precision": args.precision}
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        print(render_table(stats, args.precision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
