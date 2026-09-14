#!/usr/bin/env python3
"""
Schema Explorer — 从内省查询结果生成库表结构文档

本脚本不连接数据库，只消费「内省查询」的输出（JSON 或 CSV），
把结果渲染成 Markdown 结构文档。这样做的原因：技能需要适配
PostgreSQL / MySQL / SQLite / SQL Server 等多种方言，而连接凭据
与驱动属于用户环境，不应由技能内置。

用法:
    # 1. 先用你的客户端跑内省查询，导出 JSON
    #    （各库的内省 SQL 见 SKILL.md 的 "Schema Introspection Queries" 一节）
    python schema_explorer.py --input columns.json --output SCHEMA.md

    # 2. 直接从 SQLite 库文件内省（唯一内置支持的连接方式）
    python schema_explorer.py --sqlite app.db --output SCHEMA.md

    # 3. 只看某张表
    python schema_explorer.py --sqlite app.db --table users

    # 4. 机器可读输出
    python schema_explorer.py --sqlite app.db --json

退出码: 0 成功 / 2 输入错误 / 3 解析失败
"""

import argparse
import json
import sqlite3
import sys
from collections import OrderedDict
from pathlib import Path

# 各库标准内省查询的期望列名。用户直接用 information_schema 查询即可命中。
EXPECTED_COLUMN_KEYS = ("table_name", "column_name", "data_type")

# 常见类型归类，用于生成速览统计。未命中归为 "other"。
TYPE_FAMILY = OrderedDict(
    [
        ("string", ("char", "text", "clob", "uuid", "enum", "json", "xml")),
        ("numeric", ("int", "decimal", "numeric", "float", "double", "real", "money", "serial")),
        ("temporal", ("date", "time", "timestamp", "interval", "year")),
        ("binary", ("blob", "bytea", "binary", "varbinary")),
        ("boolean", ("bool",)),
    ]
)


def classify_type(data_type: str) -> str:
    """把方言相关的类型名归入大类；未知类型返回 other 而不是猜测。"""
    t = (data_type or "").lower()
    for family, needles in TYPE_FAMILY.items():
        if any(n in t for n in needles):
            return family
    return "other"


def normalize_rows(raw):
    """把多种内省输出格式统一成 list[dict]，键为 table_name/column_name/data_type。

    接受三种输入:
      1. list[dict]                             —— 最常见
      2. {"rows": [...]} / {"columns": [...]}   —— 包了一层信封
      3. CSV 文本（含表头）                      —— 手工导出的兜底
    """
    rows = None
    if isinstance(raw, dict):
        for key in ("rows", "columns", "data", "result"):
            if isinstance(raw.get(key), list):
                rows = raw[key]
                break
        if rows is None:
            # 可能是 {表名: [列...]} 的结构
            maybe = {k: v for k, v in raw.items() if isinstance(v, list)}
            if maybe:
                rows = []
                for table, cols in maybe.items():
                    for c in cols:
                        if isinstance(c, dict):
                            rows.append({"table_name": table, **c})
                if not rows:
                    raise ValueError("无法从该 JSON 结构中定位行数据")
            else:
                raise ValueError("无法从该 JSON 结构中定位行数据")
    elif isinstance(raw, list):
        rows = raw
    elif isinstance(raw, str):
        import csv
        import io

        reader = csv.DictReader(io.StringIO(raw.strip()))
        rows = [dict(r) for r in reader]
    else:
        raise ValueError(f"不支持的输入类型: {type(raw).__name__}")

    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        lower = {str(k).lower(): v for k, v in r.items()}
        missing = [k for k in EXPECTED_COLUMN_KEYS if k not in lower]
        if missing:
            raise ValueError(
                f"行缺少必需字段 {missing}，实际字段: {sorted(lower)}。"
                "请按 SKILL.md 的内省查询取表名/列名/类型三列。"
            )
        out.append(
            {
                "table_name": str(lower["table_name"]),
                "column_name": str(lower["column_name"]),
                "data_type": str(lower["data_type"]),
                "is_nullable": str(
                    lower.get("is_nullable", lower.get("nullable", "unknown"))
                ),
                "column_default": lower.get("column_default", lower.get("default")),
                "ordinal_position": lower.get("ordinal_position"),
                "column_comment": lower.get("column_comment", lower.get("comment")),
            }
        )
    if not out:
        raise ValueError("解析后没有有效的列记录")
    return out


def introspect_sqlite(db_path: str):
    """从 SQLite 文件直接内省。用 PRAGMA（官方稳定接口），不依赖 sqlite_master 解析。"""
    p = Path(db_path)
    if not p.is_file():
        raise FileNotFoundError(f"SQLite 文件不存在: {db_path}")

    conn = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = [r[0] for r in cur.fetchall()]
        rows = []
        for t in tables:
            # PRAGMA table_info 是标识符插值，用引号包裹并对内嵌引号做转义
            safe = t.replace('"', '""')
            for col in cur.execute(f'PRAGMA table_info("{safe}")').fetchall():
                # 0=cid 1=name 2=type 3=notnull 4=dflt_value 5=pk
                rows.append(
                    {
                        "table_name": t,
                        "column_name": col[1],
                        "data_type": col[2] or "UNKNOWN",
                        "is_nullable": "NO" if col[3] else "YES",
                        "column_default": col[4],
                        "ordinal_position": col[0],
                        "is_primary_key": "YES" if col[5] else "NO",
                    }
                )
        return rows
    finally:
        conn.close()


def build_doc(rows, source_note: str, only_table: str = None) -> str:
    """渲染 Markdown 结构文档。"""
    by_table = OrderedDict()
    for r in rows:
        if only_table and r["table_name"] != only_table:
            continue
        by_table.setdefault(r["table_name"], []).append(r)

    if not by_table:
        raise ValueError(
            f"没有匹配的表" + (f": {only_table}" if only_table else "")
        )

    for t, cols in by_table.items():
        cols.sort(
            key=lambda c: (
                c.get("ordinal_position") is None,
                c.get("ordinal_position") or 0,
                c["column_name"],
            )
        )

    total_cols = sum(len(c) for c in by_table.values())
    families = {}
    for cols in by_table.values():
        for c in cols:
            f = classify_type(c["data_type"])
            families[f] = families.get(f, 0) + 1

    L = []
    L.append("# 数据库结构文档")
    L.append("")
    L.append(f"> 数据来源：{source_note}")
    L.append("")
    L.append("## 速览")
    L.append("")
    L.append("| 指标 | 值 |")
    L.append("|------|-----|")
    L.append(f"| 表数量 | {len(by_table)} |")
    L.append(f"| 列总数 | {total_cols} |")
    L.append(
        "| 类型分布 | "
        + "、".join(f"{k} {v}" for k, v in sorted(families.items()))
        + " |"
    )
    L.append("")
    L.append("## 表目录")
    L.append("")
    for t in by_table:
        L.append(f"- [{t}](#{anchor(t)}) — {len(by_table[t])} 列")
    L.append("")

    has_comment = any(c.get("column_comment") for cols in by_table.values() for c in cols)
    has_pk = any(c.get("is_primary_key") for cols in by_table.values() for c in cols)

    for t, cols in by_table.items():
        L.append(f"## {t}")
        L.append("")
        header = ["列名", "类型", "可空", "默认值"]
        if has_pk:
            header.append("主键")
        if has_comment:
            header.append("备注")
        L.append("| " + " | ".join(header) + " |")
        L.append("|" + "---|" * len(header))
        for c in cols:
            cells = [
                f"`{c['column_name']}`",
                f"`{c['data_type']}`",
                c.get("is_nullable", "unknown"),
                "" if c.get("column_default") is None else f"`{c['column_default']}`",
            ]
            if has_pk:
                cells.append(c.get("is_primary_key", ""))
            if has_comment:
                cells.append(c.get("column_comment") or "")
            L.append("| " + " | ".join(str(x) for x in cells) + " |")
        L.append("")

    L.append("---")
    L.append("")
    L.append(
        "*本文件由 schema_explorer.py 生成。结构变更后请重新生成，"
        "不要手工编辑——手改内容会在下次生成时丢失。*"
    )
    L.append("")
    return "\n".join(L)


def anchor(name: str) -> str:
    """GitHub 风格锚点：小写、空格转连字符、去除非字母数字与连字符。"""
    out = name.strip().lower().replace(" ", "-")
    return "".join(ch for ch in out if ch.isalnum() or ch in "-_")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="从内省查询结果生成数据库结构 Markdown 文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="内省结果文件（.json 或 .csv）；- 表示 stdin")
    src.add_argument("--sqlite", help="SQLite 库文件路径（只读方式打开）")
    ap.add_argument("--table", help="只输出指定表")
    ap.add_argument("--output", "-o", help="输出 Markdown 路径；缺省打印到 stdout")
    ap.add_argument("--json", action="store_true", help="输出规范化 JSON 而非 Markdown")
    args = ap.parse_args(argv)

    try:
        if args.sqlite:
            rows = introspect_sqlite(args.sqlite)
            note = f"SQLite 内省 · `{args.sqlite}`"
        else:
            if args.input == "-":
                text = sys.stdin.read()
            else:
                p = Path(args.input)
                if not p.is_file():
                    print(f"错误：输入文件不存在: {args.input}", file=sys.stderr)
                    return 2
                text = p.read_text(encoding="utf-8", errors="replace")
            stripped = text.lstrip()
            raw = json.loads(text) if stripped.startswith(("{", "[")) else text
            rows = normalize_rows(raw)
            note = f"内省导出 · `{args.input}`"
    except FileNotFoundError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"错误：JSON 解析失败: {e}", file=sys.stderr)
        return 3
    except (ValueError, sqlite3.Error) as e:
        print(f"错误：{e}", file=sys.stderr)
        return 3

    if args.json:
        by_table = OrderedDict()
        for r in rows:
            if args.table and r["table_name"] != args.table:
                continue
            by_table.setdefault(r["table_name"], []).append(r)
        if not by_table:
            print(f"错误：没有匹配的表: {args.table}", file=sys.stderr)
            return 3
        payload = {
            "source": note,
            "table_count": len(by_table),
            "column_count": sum(len(v) for v in by_table.values()),
            "tables": [
                {
                    "name": t,
                    "column_count": len(cols),
                    "type_families": _count_families(cols),
                    "columns": cols,
                }
                for t, cols in by_table.items()
            ],
        }
        out = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        try:
            out = build_doc(rows, note, args.table)
        except ValueError as e:
            print(f"错误：{e}", file=sys.stderr)
            return 3

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(out)
    return 0


def _count_families(cols):
    fam = {}
    for c in cols:
        f = classify_type(c["data_type"])
        fam[f] = fam.get(f, 0) + 1
    return fam


if __name__ == "__main__":
    sys.exit(main())
