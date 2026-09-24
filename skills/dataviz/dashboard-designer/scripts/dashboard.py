#!/usr/bin/env python3
"""dashboard.py -- CSV health-check -> dashboard plan -> self-contained HTML dashboard.

Uses only the Python standard library (csv / json / statistics / datetime / html).

Key constraint: **the produced HTML depends on no CDN.**
Charts are generated as inline pure SVG (coordinates are computed server-side and baked
straight into the HTML), so it renders fine offline, on an intranet, or in air-gapped delivery.

Subcommands:
  inspect   <csv>                            column-type inference / missing rate / distribution summary
  recommend <csv>                            recommend a layout from column features, print a Markdown plan
  build     <csv> --out dashboard.html       generate a self-contained single-file dashboard
"""

import argparse
import csv
import html
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# column types
T_NUM, T_DATE, T_CAT, T_TEXT = "numeric", "date", "categorical", "text"

MAX_SCAN_ROWS = 50000          # beyond this we sample only, so huge files don't exhaust memory
CAT_UNIQUE_RATIO = 0.5         # unique-value ratio below this and distinct values <=20 -> categorical
CAT_MAX_UNIQUE = 20

DATE_PATTERNS = [
    ("%Y-%m-%d", re.compile(r"^\d{4}-\d{2}-\d{2}$")),
    ("%Y/%m/%d", re.compile(r"^\d{4}/\d{2}/\d{1,2}$")),
    ("%Y-%m", re.compile(r"^\d{4}-\d{2}$")),
    ("%d/%m/%Y", re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")),
    ("%Y-%m-%d %H:%M:%S", re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$")),
]

# qualitative palette (contrast-friendly, reasonably colorblind-safe), consistent with the chart-recommender's picks
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52",
           "#8172B3", "#937860", "#DA8BC3", "#8C8C8C"]


class DashError(Exception):
    """A user-facing error."""


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- CSV loading


def load_csv(path: Path):
    """Read CSV -> (headers, rows, encoding_note). Tolerant of BOM and encoding."""
    if not path.is_file():
        raise DashError(f"CSV not found: {path}")

    text, used = None, None
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            text = path.read_text(encoding=enc)
            used = enc
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if text is None:
        raise DashError(f"could not decode {path}; please re-save as UTF-8")

    sample = text[:65536]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel  # single-column or minimal file; sniffing failed, fall back to default

    reader = csv.reader(text.splitlines(), dialect)
    try:
        headers = next(reader)
    except StopIteration:
        raise DashError(f"{path} is an empty file")

    headers = [h.strip() or f"col{i}" for i, h in enumerate(headers)]
    rows, truncated = [], False
    for i, r in enumerate(reader):
        if i >= MAX_SCAN_ROWS:
            truncated = True
            break
        if len(r) < len(headers):
            r = r + [""] * (len(headers) - len(r))
        rows.append(r[: len(headers)])

    return headers, rows, used, truncated


# ---------------------------------------------------------------- type inference


def parse_date(s: str):
    s = s.strip()
    for fmt, rx in DATE_PATTERNS:
        if rx.match(s):
            try:
                return datetime.strptime(s.replace("T", " "), fmt if "%H" in fmt
                                         else fmt)
            except ValueError:
                continue
    return None


def to_float(s: str):
    s = s.strip().replace(",", "").replace("_", "")
    s = s.rstrip("%")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def profile_column(name: str, values):
    """Infer a single column's type and summarize its features."""
    total = len(values) or 1
    nonblank = [v.strip() for v in values if v and v.strip()]
    missing = len(values) - len(nonblank)

    nums = [to_float(v) for v in nonblank]
    n_num = sum(1 for x in nums if x is not None)
    dates = [parse_date(v) for v in nonblank]
    n_date = sum(1 for x in dates if x is not None)

    uniq = Counter(nonblank)
    n_uniq = len(uniq)

    if n_num / total >= 0.9:
        ctype = T_NUM
    elif n_date / total >= 0.9:
        ctype = T_DATE
    elif n_uniq <= CAT_MAX_UNIQUE or (n_uniq / total) < CAT_UNIQUE_RATIO:
        ctype = T_CAT
    else:
        ctype = T_TEXT

    col = {
        "name": name,
        "type": ctype,
        "missing": missing,
        "missing_rate": round(missing / total, 4),
        "unique": n_uniq,
        "top_values": uniq.most_common(5),
    }

    if ctype == T_NUM:
        vals = sorted(x for x in nums if x is not None)
        if vals:
            col["stats"] = numeric_summary(vals)
    if ctype == T_DATE:
        ds = [d for d in dates if d]
        if ds:
            col["range"] = {"min": min(ds).strftime("%Y-%m-%d"),
                            "max": max(ds).strftime("%Y-%m-%d")}
    return col


def numeric_summary(vals):
    """min/max/mean/median/quartiles. Quartiles use linear interpolation (consistent with common stats software)."""
    n = len(vals)
    if n == 1:
        v = vals[0]
        return {"min": v, "max": v, "mean": v, "median": v,
                "q1": v, "q3": v, "stdev": 0.0, "count": 1}

    def pct(p):
        k = (n - 1) * p
        lo, hi = int(k), min(int(k) + 1, n - 1)
        return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)

    return {
        "min": round(vals[0], 4),
        "max": round(vals[-1], 4),
        "mean": round(statistics.fmean(vals), 4),
        "median": round(pct(0.5), 4),
        "q1": round(pct(0.25), 4),
        "q3": round(pct(0.75), 4),
        "stdev": round(statistics.stdev(vals), 4) if n > 1 else 0.0,
        "count": n,
    }


def profile_table(headers, rows):
    return [profile_column(h, [r[i] for r in rows]) for i, h in enumerate(headers)]


# ---------------------------------------------------------------- recommendation logic


def recommend_layout(cols):
    """Recommend a layout from column features. Return (kpis, charts, notes)."""
    nums = [c for c in cols if c["type"] == T_NUM]
    dates = [c for c in cols if c["type"] == T_DATE]
    cats = [c for c in cols if c["type"] == T_CAT]

    kpis, charts, notes = [], [], []

    # When there is no strict categorical column, fall back: a text column may still work as a
    # dimension axis. The test is "unique values are not close to the row count" -- if every
    # value is unique (e.g. a primary key, a UUID), it is really an identifier, not a dimension;
    # as a bar chart every bar would have a single sample and mean nothing.
    # Row count is derived from the column profiles: unique values can't exceed the row count,
    # so take the max unique count across columns as an upper bound.
    rows_count = max((c["unique"] for c in cols), default=0)
    if not cats and len(cols) <= 3 and rows_count > 0:
        cand = [c for c in cols
                if c["type"] == T_TEXT and 1 < c["unique"] <= rows_count * 0.8]
        if cand:
            cats = [dict(cand[0], type=T_CAT)]
            notes.append(f"Column '{cand[0]['name']}' does not meet the strict categorical "
                         f"criterion but repeats values often, so it is treated as a dimension "
                         f"axis; if it is actually a unique identifier, ignore this chart.")

    for c in nums[:4]:
        s = c.get("stats", {})
        kpis.append({
            "column": c["name"],
            "value": s.get("mean"),
            # secondary info uses the same formatting as the main value, so a card doesn't pair
            # "49.0K" with "48990.39" (two precisions)
            "secondary": f"median {fmt_num(s.get('median', 0))} · "
                         f"total {fmt_num(s.get('mean', 0) * s.get('count', 0))}",
            "why": "numeric column; mean + median suit an overview KPI card",
        })
    if len(nums) > 4:
        notes.append(f"There are {len(nums)} numeric columns; KPI cards take only the first 4 "
                     f"({', '.join(x['name'] for x in nums[:4])}), and the other {len(nums) - 4} go "
                     f"into the detail table, so the first screen isn't swamped by cards.")

    date_col, num_col, cat_col = (dates[0] if dates else None,
                                  nums[0] if nums else None,
                                  cats[0] if cats else None)

    if date_col and num_col:
        charts.append({
            "kind": "line chart", "x": date_col["name"], "y": num_col["name"],
            "why": f"date column '{date_col['name']}' paired with numeric '{num_col['name']}' -> "
                   f"a trend is the first-choice encoding",
            "priority": "primary",
        })
    if cat_col and num_col:
        # horizontal vs vertical is decided by "average category-label length", not category count:
        # six four-character Chinese labels need horizontal layout more than twelve single-letter ones
        avg_len = sum(len(str(k)) for k, _ in cat_col["top_values"]) / max(
            1, len(cat_col["top_values"]))
        orient = "horizontal bar" if (cat_col["unique"] > 8 or avg_len > 4) else "vertical column"
        charts.append({
            "kind": orient, "x": cat_col["name"], "y": num_col["name"],
            "why": f"category '{cat_col['name']}' ({cat_col['unique']} categories, "
                   f"avg label length {avg_len:.1f} chars) vs a numeric value; "
                   f"{'long labels, horizontal so no rotation needed' if orient.startswith('horizontal') else 'short labels and few categories, vertical columns readable'}",
            "priority": "secondary",
        })
    if cat_col and not num_col:
        charts.append({
            "kind": "bar (count)", "x": cat_col["name"], "y": "record count",
            "why": "with only a categorical column, counting per-category frequency is the only informative aggregation",
            "priority": "primary",
        })
    if len(nums) >= 2:
        charts.append({
            "kind": "scatter", "x": nums[0]["name"], "y": nums[1]["name"],
            "why": f"two numeric columns '{nums[0]['name']}' / '{nums[1]['name']}' -> a scatter for "
                   f"correlation keeps more information than any aggregated chart",
            "priority": "optional",
        })
    if not charts:
        charts.append({
            "kind": "detail table", "x": cols[0]["name"] if cols else "-", "y": "-",
            "why": "no aggregatable numeric/categorical/date column; show a detail table first",
            "priority": "primary",
        })
        notes.append("This CSV lacks numeric or categorical columns and cannot be charted; check whether the data was exported correctly.")

    for c in cols:
        # even 1% is worth flagging: aggregates (especially totals and means) are systematically
        # underestimated by missingness, and the reader can't see this from the chart, so it
        # must be stated explicitly at delivery
        if c["missing_rate"] >= 0.01:
            level = "severe" if c["missing_rate"] > 0.3 else "note"
            notes.append(f"Column '{c['name']}' missing rate {c['missing_rate']:.1%} ({level}); "
                         f"means/totals on this column already excluded blank rows, and the chart "
                         f"should note 'missing data excluded', or readers will misread the trend.")
    if cat_col and cat_col["unique"] > 20:
        notes.append(f"Categorical column '{cat_col['name']}' has {cat_col['unique']} values; "
                     f"the bar chart shows only the top 12, the rest grouped as 'Other'.")
    if num_col and "stats" in num_col:
        s = num_col["stats"]
        if s["max"] > 0 and s["median"] > 0 and s["max"] > s["median"] * 20:
            notes.append(f"Column '{num_col['name']}''s max is "
                         f"{s['max'] / s['median']:.0f}x its median, extremely right-skewed; "
                         f"plotting it directly gets squashed by outliers, consider a log axis or truncation with a note.")

    return kpis, charts, notes


# ---------------------------------------------------------------- pure SVG charts

W, H = 640, 330
# PAD_T=52 leaves headroom for the title band (26px): tick labels would visually collide with a title on the same line
PAD_L, PAD_R, PAD_T, PAD_B = 76, 20, 52, 46


def svg_open(w=W, h=H):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" '
            f'role="img" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif">')


def fmt_num(v):
    """Human-readable number format: avoid scientific notation; add thousands abbreviations for big numbers.

    A number like 8000000 becomes 8e+06 under {:g}, forcing the reader to mentally compute the
    order of magnitude; once shown as 8.0M, axis labels can be compared directly.
    """
    av = abs(v)
    if av >= 1e8:
        return f"{v / 1e8:.2f}B"
    if av >= 1e4:
        return f"{v / 1e4:.1f}K"
    if av >= 1000:
        return f"{v:,.0f}"
    if av >= 1:
        return f"{v:.0f}" if float(v).is_integer() else f"{v:.2f}"
    if av == 0:
        return "0"
    return f"{v:.3f}"


def nice_ticks(vmin, vmax, n=5):
    """Return readable tick values (1/2/5 x 10^k steps)."""
    if vmax == vmin:
        vmax = vmin + 1
    raw = (vmax - vmin) / max(1, n)
    mag = 10 ** (len(str(int(abs(raw)))) - 1) if raw >= 1 else 10 ** (-1)
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step >= raw:
            break
    start = step * int(vmin / step)
    ticks, v = [], start
    while v <= vmax + step * 0.5:
        if v >= vmin - step * 0.5:
            ticks.append(round(v, 6))
        v += step
    return ticks or [vmin, vmax]


def esc(s):
    return html.escape(str(s), quote=True)


def chart_header(title):
    """The title occupies its own top band; a title on the same line as the y-axis ticks would overlap."""
    return (f'<rect x="0" y="0" width="{W}" height="26" fill="#FBFCFD"/>'
            f'<text x="12" y="17" font-size="12.5" font-weight="600" '
            f'fill="#374151">{esc(title)}</text>')


def axis_y(vmin, vmax, ticks, plot_h, top, fmt=None):
    """y-axis: gridlines + tick labels. Uses the human-readable number format by default."""
    out = []
    span = (vmax - vmin) or 1
    for t in ticks:
        y = top + plot_h - (t - vmin) / span * plot_h
        out.append(f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}" '
                   f'stroke="#E6E9ED" stroke-width="1"/>')
        label = fmt(t) if fmt else fmt_num(t)
        out.append(f'<text x="{PAD_L - 8}" y="{y + 4:.1f}" text-anchor="end" '
                   f'font-size="10.5" fill="#6B7280">{esc(label)}</text>')
    return "".join(out)


def chart_line(labels, values, title, ylabel=""):
    """Line chart: draw the line in date order + area fill."""
    if not values:
        return empty_chart(title, "no valid data")
    vmin, vmax = min(values), max(values)
    if vmin > 0:
        vmin = 0
    ticks = nice_ticks(vmin, vmax)
    vmin, vmax = min(vmin, ticks[0]), max(vmax, ticks[-1])
    plot_h = H - PAD_T - PAD_B
    span = (vmax - vmin) or 1
    n = len(values)

    def px(i):
        return PAD_L if n == 1 else PAD_L + (W - PAD_L - PAD_R) * i / (n - 1)

    def py(v):
        return PAD_T + plot_h - (v - vmin) / span * plot_h

    pts = [(px(i), py(v)) for i, v in enumerate(values)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = (f'{PAD_L},{PAD_T + plot_h} ' + line +
            f' {pts[-1][0]:.1f},{PAD_T + plot_h}')

    step = max(1, n // 6)  # sample x-axis labels so they don't crowd together
    xlabels = "".join(
        f'<text x="{px(i):.1f}" y="{H - PAD_B + 16}" text-anchor="middle" '
        f'font-size="10" fill="#6B7280">{esc(labels[i])}</text>'
        for i in range(0, n, step)
    )

    return (
        svg_open() + f'<title>{esc(title)}</title>'
        + chart_header(title)
        + axis_y(vmin, vmax, ticks, plot_h, PAD_T)
        + f'<polygon points="{area}" fill="{PALETTE[0]}" opacity="0.14"/>'
        + f'<polyline points="{line}" fill="none" stroke="{PALETTE[0]}" '
          f'stroke-width="2" stroke-linejoin="round"/>'
        + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{PALETTE[0]}"/>'
                  for x, y in pts[:80])
        + xlabels
        + f'<text x="{PAD_L}" y="{H - 8}" font-size="10" fill="#6B7280">{esc(ylabel)}</text>'
        + "</svg>"
    )


def chart_bar(labels, values, title, ylabel="", horizontal=False):
    """Bar chart: horizontal by default (long category names read better)."""
    if not values:
        return empty_chart(title, "no valid data")

    if horizontal:
        row_h = max(18, min(34, (H - PAD_T - PAD_B) // max(1, len(values))))
        height = PAD_T + PAD_B + row_h * len(values)
        plot_w = W - PAD_L - PAD_R - 60
        vmax = max(values) or 1
        parts = [svg_open(h=height),
                 f'<title>{esc(title)}</title>',
                 chart_header(title)]
        for i, (lab, v) in enumerate(zip(labels, values)):
            y = PAD_T + i * row_h
            bw = plot_w * (v / vmax)
            parts.append(f'<text x="{PAD_L - 8}" y="{y + row_h * 0.65:.1f}" '
                         f'text-anchor="end" font-size="11" fill="#374151">{esc(lab)}</text>')
            parts.append(f'<rect x="{PAD_L}" y="{y + 3:.1f}" width="{max(1, bw):.1f}" '
                         f'height="{row_h - 9:.1f}" rx="3" fill="{PALETTE[0]}"/>')
            parts.append(f'<text x="{PAD_L + bw + 6:.1f}" y="{y + row_h * 0.65:.1f}" '
                         f'font-size="10" fill="#6B7280">{esc(fmt_num(v))}</text>')
        parts.append(f'<text x="{PAD_L}" y="{height - 8}" font-size="10" '
                     f'fill="#6B7280">{esc(ylabel)}</text>')
        parts.append("</svg>")
        return "".join(parts)

    vmin, vmax = 0, max(values)
    ticks = nice_ticks(vmin, vmax)
    vmax = max(ticks)
    plot_h = H - PAD_T - PAD_B
    span = vmax or 1
    slot = (W - PAD_L - PAD_R) / max(1, len(values))
    bw = min(46, slot * 0.62)

    parts = [svg_open(), f'<title>{esc(title)}</title>',
             chart_header(title),
             axis_y(vmin, vmax, ticks, plot_h, PAD_T)]
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = PAD_L + slot * i + (slot - bw) / 2
        h = plot_h * (v / span)
        parts.append(f'<rect x="{x:.1f}" y="{PAD_T + plot_h - h:.1f}" width="{bw:.1f}" '
                     f'height="{max(1, h):.1f}" rx="3" fill="{PALETTE[0]}"/>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{H - PAD_B + 16}" text-anchor="middle" '
                     f'font-size="10" fill="#6B7280">{esc(str(lab)[:12])}</text>')
    parts.append(f'<text x="{PAD_L}" y="{H - 8}" font-size="10" fill="#6B7280">{esc(ylabel)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def chart_scatter(xs, ys, title, xlabel="", ylabel=""):
    """Scatter: for the correlation between two numeric columns."""
    if not xs:
        return empty_chart(title, "no valid data")
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax = xmin + 1
    if ymin == ymax:
        ymax = ymin + 1
    plot_h = H - PAD_T - PAD_B
    plot_w = W - PAD_L - PAD_R

    xs_lab = nice_ticks(xmin, xmax, 4)
    parts = [svg_open(), f'<title>{esc(title)}</title>',
             chart_header(title),
             axis_y(ymin, ymax, nice_ticks(ymin, ymax), plot_h, PAD_T)]
    for t in xs_lab:
        x = PAD_L + (t - xmin) / (xmax - xmin) * plot_w
        if PAD_L <= x <= W - PAD_R:
            parts.append(f'<text x="{x:.1f}" y="{H - PAD_B + 16}" text-anchor="middle" '
                         f'font-size="10" fill="#6B7280">{esc(fmt_num(t))}</text>')
    for x, y in zip(xs, ys):
        cx = PAD_L + (x - xmin) / (xmax - xmin) * plot_w
        cy = PAD_T + plot_h - (y - ymin) / (ymax - ymin) * plot_h
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" '
                     f'fill="{PALETTE[2]}" opacity="0.65"/>')
    parts.append(f'<text x="{PAD_L}" y="{H - 8}" font-size="10" fill="#6B7280">'
                 f'{esc(xlabel)}{" / " + esc(ylabel) if ylabel else ""}</text>')
    parts.append("</svg>")
    return "".join(parts)


def empty_chart(title, msg):
    return (svg_open(h=170) + f'<title>{esc(title)}</title>'
            + chart_header(title)
            + f'<text x="{W // 2}" y="95" text-anchor="middle" font-size="12" fill="#9CA3AF">{esc(msg)}</text>'
            + "</svg>")


# ---------------------------------------------------------------- HTML assembly

CSS = """
:root{--bg:#F7F8FA;--card:#FFF;--ink:#1F2937;--muted:#6B7280;--line:#E6E9ED}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font-family:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,"Noto Sans SC",sans-serif;
line-height:1.55;padding:24px}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--muted);font-size:13px;margin-bottom:20px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:20px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.kpi .lab{font-size:12px;color:var(--muted);margin-bottom:6px}
.kpi .val{font-size:24px;font-weight:650;letter-spacing:-.02em}
.kpi .sec{font-size:11px;color:var(--muted);margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.why{font-size:11px;color:var(--muted);margin-top:6px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
th{background:#F1F3F6;font-weight:600;font-size:12px;color:#374151;position:sticky;top:0}
.wrap{max-height:340px;overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}
.note{background:#FFF8E6;border:1px solid #F0D9A0;border-radius:8px;padding:10px 14px;
font-size:12.5px;color:#7A5B12;margin-top:16px}
.note ul{margin:6px 0 0;padding-left:18px}
footer{color:var(--muted);font-size:11px;margin-top:22px;text-align:center}
"""


def build_html(headers, rows, cols, kpis, charts, notes, title):
    """Assemble the data and pure-SVG charts into one self-contained HTML file."""
    # pick the data by need: prefer a date column for a line, then a categorical column for bars
    nums = [c for c in cols if c["type"] == T_NUM]
    dates = [c for c in cols if c["type"] == T_DATE]
    cats = [c for c in cols if c["type"] == T_CAT]

    def col_idx(name):
        return headers.index(name)

    blocks = []

    # 1) line: date + numeric
    if dates and nums:
        di, vi = col_idx(dates[0]["name"]), col_idx(nums[0]["name"])
        pairs = []
        for r in rows:
            d, v = parse_date(r[di]), to_float(r[vi])
            if d and v is not None:
                pairs.append((d, v))
        pairs.sort(key=lambda p: p[0])
        # aggregate same-day values to their mean, so the line doesn't zig-zag with multiple rows per day
        agg = {}
        for d, v in pairs:
            agg.setdefault(d.strftime("%Y-%m-%d"), []).append(v)
        labels = list(agg)[-60:]
        values = [round(statistics.fmean(agg[k]), 4) for k in labels]
        blocks.append(("line chart", chart_line(labels, values,
                                            f"{nums[0]['name']} over time ({dates[0]['name']})",
                                            dates[0]["name"]),
                       f"primary: {dates[0]['name']} x {nums[0]['name']}"))

    # 2) bar: categorical aggregated by numeric sum
    if cats and nums:
        ci, vi = col_idx(cats[0]["name"]), col_idx(nums[0]["name"])
        agg = {}
        for r in rows:
            k, v = r[ci].strip(), to_float(r[vi])
            if k and v is not None:
                agg[k] = agg.get(k, 0.0) + v
        top = sorted(agg.items(), key=lambda kv: -kv[1])[:12]
        if top:
            labs = [k for k, _ in top]
            vals = [round(v, 4) for _, v in top]
            # switch to horizontal bars when there are more than 6 categories, so labels don't crowd
            horiz = len(labs) > 6
            note = f"secondary: composition across the {cats[0]['name']} dimension"
            # when the numeric differences are tiny, vertical bar height differences are nearly
            # invisible, while the value labels on top are the real information; horizontal bars
            # beside the values are easier to compare
            vmax, vmin = max(vals), min(vals)
            if vmin > 0 and vmax / vmin < 1.25:
                note += f" (categories differ by <25%, bar heights near-identical; trust the numbers)"
            blocks.append(("bar chart",
                           chart_bar(labs, vals,
                                     f"{nums[0]['name']} by {cats[0]['name']}",
                                     f"total {nums[0]['name']}", horizontal=horiz),
                           note))
    elif cats:
        ci = col_idx(cats[0]["name"])
        cnt = Counter(r[ci].strip() for r in rows if r[ci].strip())
        top = cnt.most_common(12)
        if top:
            labs = [k for k, _ in top]
            vals = [v for _, v in top]
            blocks.append(("bar chart",
                           chart_bar(labs, vals, f"{cats[0]['name']} frequency",
                                     "record count", horizontal=len(labs) > 6),
                           f"primary: count by {cats[0]['name']}"))

    # 3) scatter: two numeric columns
    if len(nums) >= 2:
        xi, yi = col_idx(nums[0]["name"]), col_idx(nums[1]["name"])
        xs, ys = [], []
        for r in rows:
            a, b = to_float(r[xi]), to_float(r[yi])
            if a is not None and b is not None:
                xs.append(a)
                ys.append(b)
        if len(xs) >= 3:
            blocks.append(("scatter",
                           chart_scatter(xs[:400], ys[:400],
                                         f"{nums[0]['name']} vs {nums[1]['name']}",
                                         nums[0]["name"], nums[1]["name"]),
                           "optional: correlation of two numeric columns, preserves the raw distribution"))

    # KPI cards
    kpi_html = ""
    if kpis:
        cards = "".join(
            f'<div class="kpi"><div class="lab">{esc(k["column"])}</div>'
            f'<div class="val">{esc(fmt_num(k["value"]))}</div>'
            f'<div class="sec">{esc(k["secondary"])}</div></div>'
            for k in kpis if k.get("value") is not None
        )
        kpi_html = f'<div class="kpis">{cards}</div>'

    chart_html = ""
    for kind, svg, why in blocks:
        chart_html += (f'<div class="card">{svg}'
                       f'<div class="why">{esc(why)}</div></div>')

    # detail table (at most 200 rows; scrollable on the front end)
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
        for r in rows[:200]
    )
    table_html = (f'<div class="wrap"><table><thead><tr>{head}</tr></thead>'
                  f'<tbody>{body}</tbody></table></div>')

    note_html = ""
    if notes:
        items = "".join(f"<li>{esc(n)}</li>" for n in notes)
        note_html = f'<div class="note"><strong>Data notes</strong><ul>{items}</ul></div>'

    # inline data snapshot: lets the user verify and rebuild, and proves the file is self-contained
    snapshot = {
        "rows": len(rows),
        "columns": [{"name": c["name"], "type": c["type"],
                     "missing_rate": c["missing_rate"], "unique": c["unique"]}
                    for c in cols],
    }
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{esc(title)}</h1>
<div class="sub">{len(rows)} rows · {len(headers)} columns · generated {stamp} · self-contained single file (no external dependencies)</div>
{kpi_html}
<div class="grid">{chart_html}</div>
<h2 style="font-size:15px;margin:22px 0 8px">Detail data (first 200 rows)</h2>
{table_html}
{note_html}
<footer>Generated by dashboard.py · charts are inline SVG, usable offline ·
<script type="application/json" id="dash-meta">{json.dumps(snapshot, ensure_ascii=False)}</script>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- subcommands


def cmd_inspect(args) -> int:
    p = Path(args.csv)
    headers, rows, enc, trunc = load_csv(p)
    cols = profile_table(headers, rows)

    print(f"inspect: {p}")
    print(f"  rows      : {len(rows)}{' (sampled/truncated)' if trunc else ''}")
    print(f"  columns   : {len(headers)}")
    print(f"  encoding  : {enc}")
    print()
    print("  [column profiles]")
    print(f"    {'column':<20} {'type':<12} {'missing':>8} {'unique':>7}  summary")
    for c in cols:
        if c["type"] == T_NUM and "stats" in c:
            s = c["stats"]
            summ = (f"min={fmt_num(s['min'])} max={fmt_num(s['max'])} "
                    f"mean={fmt_num(s['mean'])} median={fmt_num(s['median'])} "
                    f"q1={fmt_num(s['q1'])} q3={fmt_num(s['q3'])}")
        elif c["type"] == T_DATE and "range" in c:
            summ = f"{c['range']['min']} -> {c['range']['max']}"
        elif c["type"] == T_CAT:
            summ = "top: " + ", ".join(f"{k}({v})" for k, v in c["top_values"][:3])
        else:
            summ = "free text, not recommended for direct charting"
        print(f"    {c['name']:<20} {c['type']:<12} {c['missing_rate']:>7.1%} "
              f"{c['unique']:>7}  {summ}")
    return 0


def cmd_recommend(args) -> int:
    p = Path(args.csv)
    headers, rows, _, _ = load_csv(p)
    cols = profile_table(headers, rows)
    kpis, charts, notes = recommend_layout(cols)

    out = [f"# dashboard design plan: {p.name}", ""]
    out.append(f"Data size: {len(rows)} rows x {len(headers)} columns.")
    out.append("")
    out.append("## KPI cards (first-screen overview)")
    out.append("")
    out.append("| column | main value | secondary | why |")
    out.append("|---|---|---|---|")
    for k in kpis:
        v = f"{k['value']:g}" if k.get("value") is not None else "-"
        out.append(f"| {k['column']} | {v} | {k['secondary']} | {k['why']} |")
    if not kpis:
        out.append("| - | - | - | no numeric columns, no KPI cards |")
    out.append("")
    out.append("## chart plan")
    out.append("")
    out.append("| priority | chart type | X / dimension | Y / measure | why this choice |")
    out.append("|---|---|---|---|---|")
    for c in charts:
        out.append(f"| {c['priority']} | {c['kind']} | {c['x']} | {c['y']} | {c['why']} |")
    out.append("")
    out.append("## layout suggestion")
    out.append("")
    out.append("```")
    out.append("+----------------------------------------------+")
    out.append("| title + data size / time range               |")
    out.append("+----------+----------+----------+-------------+")
    out.append("| KPI 1    | KPI 2    | KPI 3    | KPI 4       |")
    out.append("+----------+----------+----------+-------------+")
    out.append("| primary: trend (full row, highest weight)     |")
    out.append("+------------------------+---------------------+")
    out.append("| secondary: composition | secondary: detail / |")
    out.append("|                        | correlation         |")
    out.append("+------------------------+---------------------+")
    out.append("```")
    out.append("")
    out.append("The first screen holds only 3-4 information blocks that are readable at a glance; "
               "the detail table sits at the bottom for verification and doesn't compete with the charts.")
    if notes:
        out.append("")
        out.append("## data notes")
        out.append("")
        for n in notes:
            out.append(f"- {n}")
    print("\n".join(out))
    return 0


def cmd_build(args) -> int:
    p = Path(args.csv)
    headers, rows, _, _ = load_csv(p)
    cols = profile_table(headers, rows)
    kpis, charts, notes = recommend_layout(cols)

    title = args.title or f"{p.stem} dashboard"
    html_text = build_html(headers, rows, cols, kpis, charts, notes, title)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")

    size_kb = len(html_text.encode("utf-8")) / 1024
    external = re.findall(r'(?:src|href)="(?!#)([^"]+)"', html_text)
    print(f"built: {out}")
    print(f"  bytes     : {size_kb:.1f} KB")
    print(f"  rows      : {len(rows)}")
    print(f"  kpis      : {len(kpis)}")
    print(f"  charts    : {len(charts)}  inline SVG")
    print(f"  external  : {len(external)} external reference(s)"
          f"{' (should be 0; file is self-contained)' if not external else ' <- anomaly: ' + ', '.join(external)}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="dashboard.py",
        description="CSV health-check -> dashboard plan -> self-contained offline HTML (pure stdlib)",
        epilog="example: python3 dashboard.py inspect data.csv && "
               "python3 dashboard.py build data.csv --out dash.html",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("inspect", help="column-type inference / missing rate / distribution summary")
    s.add_argument("csv")
    s.set_defaults(func=cmd_inspect)

    s = sub.add_parser("recommend", help="print a Markdown dashboard design plan")
    s.add_argument("csv")
    s.set_defaults(func=cmd_recommend)

    s = sub.add_parser("build", help="generate a self-contained single-file HTML dashboard")
    s.add_argument("csv")
    s.add_argument("--out", default="dashboard.html", help="output HTML path")
    s.add_argument("--title", help="dashboard title")
    s.set_defaults(func=cmd_build)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except DashError as e:
        die(str(e))
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
