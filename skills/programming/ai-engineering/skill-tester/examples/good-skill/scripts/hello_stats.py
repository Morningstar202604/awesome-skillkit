#!/usr/bin/env python3
"""hello_stats — good-skill 的演示脚本。

一个"合格技能"的脚本应满足的五条纪律（每条都对应 quality_scorer /
script_tester 的一个检查项）：

1. stdlib-only        —— 仓库政策：scripts/ 下的脚本只允许标准库。
2. __main__ guard     —— 被 import 时零副作用（script_tester 做 AST 检查）。
3. --help 自描述      —— argparse 自动提供，排障第一入口。
4. --json 机器可读    —— CI 集成与 golden 比对的前提。
5. 错误路径可读       —— 失败也要退出码非 0 + stderr 给出"下一步怎么办"。

功能：对一组数字（逗号分隔的 CLI 参数、或 --input 文件、或 stdin）
计算基本统计量，支持百分位与输出精度控制。
"""

import argparse
import json
import sys

DEFAULT_PRECISION = 4


def parse_numbers(raw):
    """把逗号分隔的数字串解析为浮点列表；任何一项非法即抛 ValueError。

    >>> parse_numbers("1, 2,3.5")
    [1.0, 2.0, 3.5]
    """
    items = [s.strip() for s in raw.replace("\n", ",").split(",") if s.strip()]
    if not items:
        raise ValueError("empty input")
    return [float(s) for s in items]


def read_numbers_from_path(path):
    """从文本文件读数字：按行收集，行内逗号/空白分隔均可。"""
    numbers = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            for token in line.replace(",", " ").split():
                numbers.append(float(token))
    if not numbers:
        raise ValueError(f"no numbers found in {path}")
    return numbers


def percentile(sorted_vals, pct):
    """线性插值百分位（与 numpy 默认 linear 法一致的简化版）。

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
    """对一组数字计算统计量；pcts 指定要输出的百分位（如 50/90/99）。"""
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
    """把浮点值按精度取整（保留 median 可能是 int 的情形由 float() 统一）。"""
    out = {}
    for key, val in stats.items():
        out[key] = round(float(val), precision)
    return out


def render_table(stats, precision):
    """人类可读的表格输出。"""
    lines = ["=== 统计结果 ==="]
    for key, val in stats.items():
        if isinstance(val, float):
            lines.append(f"{key:>8}: {val:.{precision}f}")
        else:
            lines.append(f"{key:>8}: {val}")
    return "\n".join(lines)


def build_parser():
    ap = argparse.ArgumentParser(
        prog="hello_stats",
        description="对一组数字计算基本统计量（good-skill 演示脚本）。",
        epilog="示例：hello_stats 1,2,3.5,4 --json；cat data.txt | hello_stats -",
    )
    ap.add_argument("numbers", nargs="?", default=None,
                    help="逗号分隔的数字，如 1,2,3.5；用 '-' 表示从 stdin 读")
    ap.add_argument("--input", dest="input_path", default=None,
                    help="从文本文件读数字（行内逗号/空白分隔）")
    ap.add_argument("--json", action="store_true", help="输出 JSON（机器可读）")
    ap.add_argument("--percentiles", default="50",
                    help="逗号分隔的百分位列表，如 50,90,99（默认 50）")
    ap.add_argument("--precision", type=int, default=DEFAULT_PRECISION,
                    help=f"浮点输出精度（默认 {DEFAULT_PRECISION} 位小数）")
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)

    try:
        pcts = [float(p) for p in args.percentiles.split(",") if p.strip()]
    except ValueError:
        print("error: --percentiles 只接受逗号分隔的数字，如 50,90,99", file=sys.stderr)
        return 2

    try:
        if args.input_path:
            numbers = read_numbers_from_path(args.input_path)
        elif args.numbers == "-":
            numbers = parse_numbers(sys.stdin.read())
        elif args.numbers:
            numbers = parse_numbers(args.numbers)
        else:
            print("error: 缺少 numbers 参数；示例：hello_stats 1,2,3.5 或 --input data.txt",
                  file=sys.stderr)
            return 2
        stats = compute_stats(numbers, pcts=pcts)
    except ValueError as e:
        print(f"error: 输入无法解析（{e}）；示例：hello_stats 1,2,3.5,4", file=sys.stderr)
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
