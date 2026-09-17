#!/usr/bin/env python3
"""dashboard.py — CSV 体检 → 仪表盘方案 → 自包含 HTML 仪表盘。

只用 Python 标准库（csv / json / statistics / datetime / html）。

关键约束：**产出的 HTML 不依赖任何 CDN**。
图表用内联的纯 SVG 生成（服务端算好坐标直接写死进 HTML），
因此断网、内网、离线交付都能正常显示。

子命令:
  inspect   <csv>                            列类型推断 / 缺失率 / 分布摘要
  recommend <csv>                            基于列特征推荐布局，输出 Markdown 方案
  build     <csv> --out dashboard.html       生成自包含单文件仪表盘
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

# 列类型
T_NUM, T_DATE, T_CAT, T_TEXT = "numeric", "date", "categorical", "text"

MAX_SCAN_ROWS = 50000          # 超过此数只抽样，避免大文件把内存吃满
CAT_UNIQUE_RATIO = 0.5         # 唯一值占比低于此值且不同值 <=20 → 分类
CAT_MAX_UNIQUE = 20

DATE_PATTERNS = [
    ("%Y-%m-%d", re.compile(r"^\d{4}-\d{2}-\d{2}$")),
    ("%Y/%m/%d", re.compile(r"^\d{4}/\d{2}/\d{1,2}$")),
    ("%Y-%m", re.compile(r"^\d{4}-\d{2}$")),
    ("%d/%m/%Y", re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")),
    ("%Y-%m-%d %H:%M:%S", re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$")),
]

# 定性色板（对比度友好、色盲相对安全），与 chart-recommender 的推荐保持一致
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52",
           "#8172B3", "#937860", "#DA8BC3", "#8C8C8C"]


class DashError(Exception):
    """面向用户的错误。"""


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- CSV 读取


def load_csv(path: Path):
    """读 CSV → (headers, rows, encoding_note)。宽容处理 BOM 与编码。"""
    if not path.is_file():
        raise DashError(f"CSV 不存在：{path}")

    text, used = None, None
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            text = path.read_text(encoding=enc)
            used = enc
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if text is None:
        raise DashError(f"无法解码 {path}，请另存为 UTF-8")

    sample = text[:65536]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel  # 单列或极简文件嗅探失败，退回默认

    reader = csv.reader(text.splitlines(), dialect)
    try:
        headers = next(reader)
    except StopIteration:
        raise DashError(f"{path} 是空文件")

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


# ---------------------------------------------------------------- 类型推断


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
    """推断单列类型并汇总特征。"""
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
    """min/max/mean/median/四分位。四分位用线性插值（与常见统计软件一致）。"""
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


# ---------------------------------------------------------------- 推荐逻辑


def recommend_layout(cols):
    """按列特征给出布局建议。返回 (kpis, charts, notes)。"""
    nums = [c for c in cols if c["type"] == T_NUM]
    dates = [c for c in cols if c["type"] == T_DATE]
    cats = [c for c in cols if c["type"] == T_CAT]

    kpis, charts, notes = [], [], []

    # 没有严格分类列时退一步：文本列也可能适合当维度轴。
    # 判据是「唯一值相对总行数不接近行数」——若每个值都唯一（如主键、UUID），
    # 它其实是标识符而不是维度，画成条形图每根柱都只有一个样本，没有意义。
    # 行数从列画像反推：唯一值不会超过行数，取各列唯一值的最大值作为上界。
    rows_count = max((c["unique"] for c in cols), default=0)
    if not cats and len(cols) <= 3 and rows_count > 0:
        cand = [c for c in cols
                if c["type"] == T_TEXT and 1 < c["unique"] <= rows_count * 0.8]
        if cand:
            cats = [dict(cand[0], type=T_CAT)]
            notes.append(f"列「{cand[0]['name']}」未达分类列的严格判据，"
                         f"但取值重复度高，已按维度轴处理；"
                         f"若它其实是唯一标识符，请忽略这张图。")

    for c in nums[:4]:
        s = c.get("stats", {})
        kpis.append({
            "column": c["name"],
            "value": s.get("mean"),
            # 副信息与主数值用同一套格式化，避免卡片上「4.9万」配「48990.39」两套精度
            "secondary": f"中位数 {fmt_num(s.get('median', 0))} · "
                         f"合计 {fmt_num(s.get('mean', 0) * s.get('count', 0))}",
            "why": "数值列，均值+中位数适合做概览指标卡",
        })
    if len(nums) > 4:
        notes.append(f"数值列有 {len(nums)} 个，指标卡只取前 4 个（{', '.join(x['name'] for x in nums[:4])}），"
                     f"其余 {len(nums) - 4} 个放进明细表，避免首屏被卡片淹没。")

    date_col, num_col, cat_col = (dates[0] if dates else None,
                                  nums[0] if nums else None,
                                  cats[0] if cats else None)

    if date_col and num_col:
        charts.append({
            "kind": "折线图", "x": date_col["name"], "y": num_col["name"],
            "why": f"时间列「{date_col['name']}」配数值列「{num_col['name']}」→ 趋势是首选表达",
            "priority": "主图",
        })
    if cat_col and num_col:
        # 横条/竖柱的判据是「类别名平均长度」而非类别数：
        # 6 个四字中文标签比 12 个单字母标签更需要水平排布
        avg_len = sum(len(str(k)) for k, _ in cat_col["top_values"]) / max(
            1, len(cat_col["top_values"]))
        orient = "水平条形图" if (cat_col["unique"] > 8 or avg_len > 4) else "垂直柱状图"
        charts.append({
            "kind": orient, "x": cat_col["name"], "y": num_col["name"],
            "why": f"分类「{cat_col['name']}」({cat_col['unique']} 类，"
                   f"标签均长 {avg_len:.1f} 字符) 与数值比大小；"
                   f"{'标签较长，水平排布不用旋转' if orient.startswith('水平') else '标签短且类别少，竖柱可读'}",
            "priority": "副图",
        })
    if cat_col and not num_col:
        charts.append({
            "kind": "条形图（计数）", "x": cat_col["name"], "y": "记录数",
            "why": "只有分类列时，统计各类频次是唯一有信息量的聚合",
            "priority": "主图",
        })
    if len(nums) >= 2:
        charts.append({
            "kind": "散点图", "x": nums[0]["name"], "y": nums[1]["name"],
            "why": f"两个数值列「{nums[0]['name']}」「{nums[1]['name']}」→ 相关性用散点，"
                   f"比任何聚合图都保留更多信息",
            "priority": "可选",
        })
    if not charts:
        charts.append({
            "kind": "明细表", "x": cols[0]["name"] if cols else "-", "y": "-",
            "why": "没有可聚合的数值/分类/日期列，先出明细表",
            "priority": "主图",
        })
        notes.append("这份 CSV 缺少数值列或分类列，无法出图；确认数据是否导出有误。")

    for c in cols:
        # 1% 就值得说：聚合值（尤其合计与均值）会因缺失被系统性低估，
        # 而读者无法从图上看出这一点，必须在交付时明确交代
        if c["missing_rate"] >= 0.01:
            level = "严重" if c["missing_rate"] > 0.3 else "需注意"
            notes.append(f"列「{c['name']}」缺失率 {c['missing_rate']:.1%}（{level}），"
                         f"涉及该列的均值/合计已排除空缺行，图表需注明"
                         f"「缺失数据未计入」，否则读者会误读趋势。")
    if cat_col and cat_col["unique"] > 20:
        notes.append(f"分类列「{cat_col['name']}」有 {cat_col['unique']} 个取值，"
                     f"条形图只显示 top 12，其余归入「其他」。")
    if num_col and "stats" in num_col:
        s = num_col["stats"]
        if s["max"] > 0 and s["median"] > 0 and s["max"] > s["median"] * 20:
            notes.append(f"列「{num_col['name']}」最大值是其中位数的 "
                         f"{s['max'] / s['median']:.0f} 倍，分布极度右偏；"
                         f"若在图上直接画会被离群点压扁，考虑对数轴或截断并标注。")

    return kpis, charts, notes


# ---------------------------------------------------------------- 纯 SVG 图

W, H = 640, 330
# PAD_T=52 是给图题带（26px）留出的净空：刻度标签若与标题同高会视觉粘连
PAD_L, PAD_R, PAD_T, PAD_B = 76, 20, 52, 46


def svg_open(w=W, h=H):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" '
            f'role="img" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif">')


def fmt_num(v):
    """人类可读的数值格式：避免科学计数法，大数加千分位缩写。

    8000000 这类数字用 {:g} 会变成 8e+06，读者要在脑子里换算数量级；
    改成 800万 / 8.0M 之后，轴上数字可以直接比较。
    """
    av = abs(v)
    if av >= 1e8:
        return f"{v / 1e8:.2f}亿"
    if av >= 1e4:
        return f"{v / 1e4:.1f}万"
    if av >= 1000:
        return f"{v:,.0f}"
    if av >= 1:
        return f"{v:.0f}" if float(v).is_integer() else f"{v:.2f}"
    if av == 0:
        return "0"
    return f"{v:.3f}"


def nice_ticks(vmin, vmax, n=5):
    """给出可读的刻度值（1/2/5 × 10^k 步长）。"""
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
    """图题独占顶部一条带：标题若与 y 轴刻度同高会重叠。"""
    return (f'<rect x="0" y="0" width="{W}" height="26" fill="#FBFCFD"/>'
            f'<text x="12" y="17" font-size="12.5" font-weight="600" '
            f'fill="#374151">{esc(title)}</text>')


def axis_y(vmin, vmax, ticks, plot_h, top, fmt=None):
    """y 轴：网格线 + 刻度标签。默认用人类可读的数值格式。"""
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
    """折线图：按日期序画折线 + 面积填充。"""
    if not values:
        return empty_chart(title, "无有效数据")
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

    step = max(1, n // 6)  # x 轴标签抽样，避免挤成一团
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
    """条形图：默认水平（长分类名更易读）。"""
    if not values:
        return empty_chart(title, "无有效数据")

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
    """散点图：用于两个数值列的相关性。"""
    if not xs:
        return empty_chart(title, "无有效数据")
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


# ---------------------------------------------------------------- HTML 组装

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
    """把数据与纯 SVG 图表拼成一个自包含 HTML 文件。"""
    # 视需求挑数据：优先时间列做折线，其次分类列做条形
    nums = [c for c in cols if c["type"] == T_NUM]
    dates = [c for c in cols if c["type"] == T_DATE]
    cats = [c for c in cols if c["type"] == T_CAT]

    def col_idx(name):
        return headers.index(name)

    blocks = []

    # 1) 折线：日期 + 数值
    if dates and nums:
        di, vi = col_idx(dates[0]["name"]), col_idx(nums[0]["name"])
        pairs = []
        for r in rows:
            d, v = parse_date(r[di]), to_float(r[vi])
            if d and v is not None:
                pairs.append((d, v))
        pairs.sort(key=lambda p: p[0])
        # 同日期聚合求均值，避免一天多笔时折线回折
        agg = {}
        for d, v in pairs:
            agg.setdefault(d.strftime("%Y-%m-%d"), []).append(v)
        labels = list(agg)[-60:]
        values = [round(statistics.fmean(agg[k]), 4) for k in labels]
        blocks.append(("折线图", chart_line(labels, values,
                                            f"{nums[0]['name']} 随时间变化（{dates[0]['name']}）",
                                            dates[0]["name"]),
                       f"主图：{dates[0]['name']} × {nums[0]['name']}"))

    # 2) 条形：分类聚合数值之和
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
            # 类别多于 6 时改水平条，标签才不会挤在一起
            horiz = len(labs) > 6
            note = f"副图：{cats[0]['name']} 维度的构成对比"
            # 数值差异很小时，竖柱的高度差肉眼几乎看不出，
            # 而柱顶的数值标签才是有效信息；水平条配合值的排布更易比较
            vmax, vmin = max(vals), min(vals)
            if vmin > 0 and vmax / vmin < 1.25:
                note += f"（各类别差异 <25%，柱高近乎相同，请以数值为准）"
            blocks.append(("条形图",
                           chart_bar(labs, vals,
                                     f"按 {cats[0]['name']} 汇总的 {nums[0]['name']}",
                                     f"合计 {nums[0]['name']}", horizontal=horiz),
                           note))
    elif cats:
        ci = col_idx(cats[0]["name"])
        cnt = Counter(r[ci].strip() for r in rows if r[ci].strip())
        top = cnt.most_common(12)
        if top:
            labs = [k for k, _ in top]
            vals = [v for _, v in top]
            blocks.append(("条形图",
                           chart_bar(labs, vals, f"{cats[0]['name']} 频次分布",
                                     "记录数", horizontal=len(labs) > 6),
                           f"主图：按 {cats[0]['name']} 计数"))

    # 3) 散点：两个数值列
    if len(nums) >= 2:
        xi, yi = col_idx(nums[0]["name"]), col_idx(nums[1]["name"])
        xs, ys = [], []
        for r in rows:
            a, b = to_float(r[xi]), to_float(r[yi])
            if a is not None and b is not None:
                xs.append(a)
                ys.append(b)
        if len(xs) >= 3:
            blocks.append(("散点图",
                           chart_scatter(xs[:400], ys[:400],
                                         f"{nums[0]['name']} vs {nums[1]['name']}",
                                         nums[0]["name"], nums[1]["name"]),
                           "可选：两数值列的相关性，保留原始分布"))

    # KPI 卡片
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

    # 明细表（最多 200 行，前端可滚动）
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
        note_html = f'<div class="note"><strong>数据提示</strong><ul>{items}</ul></div>'

    # 内联数据快照：便于用户核对与二次开发，也证明文件自包含
    snapshot = {
        "rows": len(rows),
        "columns": [{"name": c["name"], "type": c["type"],
                     "missing_rate": c["missing_rate"], "unique": c["unique"]}
                    for c in cols],
    }
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{esc(title)}</h1>
<div class="sub">{len(rows)} 行 · {len(headers)} 列 · 生成于 {stamp} · 自包含单文件（无外部依赖）</div>
{kpi_html}
<div class="grid">{chart_html}</div>
<h2 style="font-size:15px;margin:22px 0 8px">明细数据（前 200 行）</h2>
{table_html}
{note_html}
<footer>由 dashboard.py 生成 · 图表为内联 SVG，离线可用 ·
<script type="application/json" id="dash-meta">{json.dumps(snapshot, ensure_ascii=False)}</script>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- 子命令


def cmd_inspect(args) -> int:
    p = Path(args.csv)
    headers, rows, enc, trunc = load_csv(p)
    cols = profile_table(headers, rows)

    print(f"inspect: {p}")
    print(f"  rows      : {len(rows)}{' (已截断抽样)' if trunc else ''}")
    print(f"  columns   : {len(headers)}")
    print(f"  encoding  : {enc}")
    print()
    print("  [列画像]")
    print(f"    {'列名':<20} {'类型':<12} {'缺失':>8} {'唯一值':>7}  摘要")
    for c in cols:
        if c["type"] == T_NUM and "stats" in c:
            s = c["stats"]
            summ = (f"min={fmt_num(s['min'])} max={fmt_num(s['max'])} "
                    f"mean={fmt_num(s['mean'])} median={fmt_num(s['median'])} "
                    f"q1={fmt_num(s['q1'])} q3={fmt_num(s['q3'])}")
        elif c["type"] == T_DATE and "range" in c:
            summ = f"{c['range']['min']} → {c['range']['max']}"
        elif c["type"] == T_CAT:
            summ = "top: " + ", ".join(f"{k}({v})" for k, v in c["top_values"][:3])
        else:
            summ = "自由文本，不建议直接入图"
        print(f"    {c['name']:<20} {c['type']:<12} {c['missing_rate']:>7.1%} "
              f"{c['unique']:>7}  {summ}")
    return 0


def cmd_recommend(args) -> int:
    p = Path(args.csv)
    headers, rows, _, _ = load_csv(p)
    cols = profile_table(headers, rows)
    kpis, charts, notes = recommend_layout(cols)

    out = [f"# 仪表盘设计方案：{p.name}", ""]
    out.append(f"数据规模：{len(rows)} 行 × {len(headers)} 列。")
    out.append("")
    out.append("## 指标卡（首屏概览）")
    out.append("")
    out.append("| 列 | 主数值 | 副信息 | 为什么 |")
    out.append("|---|---|---|---|")
    for k in kpis:
        v = f"{k['value']:g}" if k.get("value") is not None else "—"
        out.append(f"| {k['column']} | {v} | {k['secondary']} | {k['why']} |")
    if not kpis:
        out.append("| — | — | — | 没有数值列，不出指标卡 |")
    out.append("")
    out.append("## 图表方案")
    out.append("")
    out.append("| 优先级 | 图型 | X / 维度 | Y / 度量 | 为什么这么选 |")
    out.append("|---|---|---|---|---|")
    for c in charts:
        out.append(f"| {c['priority']} | {c['kind']} | {c['x']} | {c['y']} | {c['why']} |")
    out.append("")
    out.append("## 布局建议")
    out.append("")
    out.append("```")
    out.append("┌──────────────────────────────────────────────┐")
    out.append("│ 标题 + 数据规模/时间范围                       │")
    out.append("├──────────┬──────────┬──────────┬─────────────┤")
    out.append("│ 指标卡 1  │ 指标卡 2  │ 指标卡 3  │ 指标卡 4     │")
    out.append("├──────────┴──────────┴──────────┴─────────────┤")
    out.append("│ 主图：趋势（占整行，最高视觉权重）              │")
    out.append("├────────────────────────┬─────────────────────┤")
    out.append("│ 副图：构成对比          │ 副图：明细/相关性     │")
    out.append("└────────────────────────┴─────────────────────┘")
    out.append("```")
    out.append("")
    out.append("首屏只放「一眼能看懂」的 3-4 个信息块；"
               "明细表放页面底部，供核查用，不与图表争注意力。")
    if notes:
        out.append("")
        out.append("## 数据注意事项")
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

    title = args.title or f"{p.stem} 数据仪表盘"
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
    print(f"  charts    : {len(charts)}  内联 SVG")
    print(f"  external  : {len(external)} 个外部引用"
          f"{'（应为 0，文件自包含）' if not external else ' ← 异常：' + ', '.join(external)}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="dashboard.py",
        description="CSV 体检 → 仪表盘方案 → 自包含离线 HTML（纯标准库）",
        epilog="示例：python3 dashboard.py inspect data.csv && "
               "python3 dashboard.py build data.csv --out dash.html",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("inspect", help="列类型推断 / 缺失率 / 分布摘要")
    s.add_argument("csv")
    s.set_defaults(func=cmd_inspect)

    s = sub.add_parser("recommend", help="输出 Markdown 仪表盘设计方案")
    s.add_argument("csv")
    s.set_defaults(func=cmd_recommend)

    s = sub.add_parser("build", help="生成自包含单文件 HTML 仪表盘")
    s.add_argument("csv")
    s.add_argument("--out", default="dashboard.html", help="输出 HTML 路径")
    s.add_argument("--title", help="仪表盘标题")
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
