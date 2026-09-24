#!/usr/bin/env python3
"""
Schema Explorer -- generate a schema/table-structure document from introspection query results.

This script does not connect to a database; it only consumes the output of an "introspection
query" (JSON or CSV) and renders it into a Markdown structure document. The reason: the skill
must adapt to many dialects (PostgreSQL / MySQL / SQLite / SQL Server), while connection
credentials and drivers belong to the user's environment and should not be baked into the skill.

Usage:
    # 1. First run the introspection query in your client and export JSON
    #    (see the "Schema Introspection Queries" section of SKILL.md for per-dialect SQL)
    python schema_explorer.py --input columns.json --output SCHEMA.md

    # 2. Introspect directly from a SQLite database file (the only built-in connection mode)
    python schema_explorer.py --sqlite app.db --output SCHEMA.md

    # 3. Inspect only one table
    python schema_explorer.py --sqlite app.db --table users

    # 4. Machine-readable output
    python schema_explorer.py --sqlite app.db --json

Exit codes: 0 success / 2 input error / 3 parse failure
"""

import argparse
import json
import sqlite3
import sys
from collections import OrderedDict
from pathlib import Path

# Expected column names for each dialect's standard introspection query. The user can just
# query information_schema and these keys will match.
EXPECTED_COLUMN_KEYS = ("table_name", "column_name", "data_type")

# Common type families, used to generate quick-glance statistics. Anything unmatched goes to "other".
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
    """Bucket a dialect-specific type name into a family; unknown types return "other" rather than being guessed."""
    t = (data_type or "").lower()
    for family, needles in TYPE_FAMILY.items():
        if any(n in t for n in needles):
            return family
    return "other"


def normalize_rows(raw):
    """Normalize several introspection output formats into list[dict] with keys table_name/column_name/data_type.

    Accepts three kinds of input:
      1. list[dict]                             -- most common
      2. {"rows": [...]} / {"columns": [...]}   -- wrapped in an envelope
      3. CSV text (with header)                  -- manual-export fallback
    """
    rows = None
    if isinstance(raw, dict):
        for key in ("rows", "columns", "data", "result"):
            if isinstance(raw.get(key), list):
                rows = raw[key]
                break
        if rows is None:
            # possibly a {table_name: [columns...]} structure
            maybe = {k: v for k, v in raw.items() if isinstance(v, list)}
            if maybe:
                rows = []
                for table, cols in maybe.items():
                    for c in cols:
                        if isinstance(c, dict):
                            rows.append({"table_name": table, **c})
                if not rows:
                    raise ValueError("could not locate row data in this JSON structure")
            else:
                raise ValueError("could not locate row data in this JSON structure")
    elif isinstance(raw, list):
        rows = raw
    elif isinstance(raw, str):
        import csv
        import io

        reader = csv.DictReader(io.StringIO(raw.strip()))
        rows = [dict(r) for r in reader]
    else:
        raise ValueError(f"unsupported input type: {type(raw).__name__}")

    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        lower = {str(k).lower(): v for k, v in r.items()}
        missing = [k for k in EXPECTED_COLUMN_KEYS if k not in lower]
        if missing:
            raise ValueError(
                f"row is missing required fields {missing}; actual fields: {sorted(lower)}. "
                "Please take the table name / column name / type columns per the introspection query in SKILL.md."
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
        raise ValueError("no valid column records after parsing")
    return out


def introspect_sqlite(db_path: str):
    """Introspect directly from a SQLite file. Uses PRAGMA (the official stable interface), not sqlite_master parsing."""
    p = Path(db_path)
    if not p.is_file():
        raise FileNotFoundError(f"SQLite file not found: {db_path}")

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
            # PRAGMA table_info is identifier interpolation; wrap in quotes and escape embedded quotes
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
    """Render the Markdown structure document."""
    by_table = OrderedDict()
    for r in rows:
        if only_table and r["table_name"] != only_table:
            continue
        by_table.setdefault(r["table_name"], []).append(r)

    if not by_table:
        raise ValueError(
            f"no matching table" + (f": {only_table}" if only_table else "")
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
    L.append("# Database Schema Document")
    L.append("")
    L.append(f"> Source: {source_note}")
    L.append("")
    L.append("## Overview")
    L.append("")
    L.append("| Metric | Value |")
    L.append("|--------|-------|")
    L.append(f"| Table count | {len(by_table)} |")
    L.append(f"| Total columns | {total_cols} |")
    L.append(
        "| Type distribution | "
        + ", ".join(f"{k} {v}" for k, v in sorted(families.items()))
        + " |"
    )
    L.append("")
    L.append("## Table Index")
    L.append("")
    for t in by_table:
        L.append(f"- [{t}](#{anchor(t)}) — {len(by_table[t])} columns")
    L.append("")

    has_comment = any(c.get("column_comment") for cols in by_table.values() for c in cols)
    has_pk = any(c.get("is_primary_key") for cols in by_table.values() for c in cols)

    for t, cols in by_table.items():
        L.append(f"## {t}")
        L.append("")
        header = ["Column", "Type", "Nullable", "Default"]
        if has_pk:
            header.append("PK")
        if has_comment:
            header.append("Comment")
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
        "*This file is generated by schema_explorer.py. Regenerate it after any schema change; "
        "do not edit it by hand -- manual edits will be lost on the next generation.*"
    )
    L.append("")
    return "\n".join(L)


def anchor(name: str) -> str:
    """GitHub-style anchor: lowercase, spaces to hyphens, strip non-alphanumeric and non-hyphen characters."""
    out = name.strip().lower().replace(" ", "-")
    return "".join(ch for ch in out if ch.isalnum() or ch in "-_")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Generate a database-schema Markdown document from introspection query results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="introspection result file (.json or .csv); - means stdin")
    src.add_argument("--sqlite", help="SQLite database file path (opened read-only)")
    ap.add_argument("--table", help="output only the specified table")
    ap.add_argument("--output", "-o", help="output Markdown path; defaults to stdout")
    ap.add_argument("--json", action="store_true", help="output normalized JSON instead of Markdown")
    args = ap.parse_args(argv)

    try:
        if args.sqlite:
            rows = introspect_sqlite(args.sqlite)
            note = f"SQLite introspection · `{args.sqlite}`"
        else:
            if args.input == "-":
                text = sys.stdin.read()
            else:
                p = Path(args.input)
                if not p.is_file():
                    print(f"error: input file not found: {args.input}", file=sys.stderr)
                    return 2
                text = p.read_text(encoding="utf-8", errors="replace")
            stripped = text.lstrip()
            raw = json.loads(text) if stripped.startswith(("{", "[")) else text
            rows = normalize_rows(raw)
            note = f"introspection export · `{args.input}`"
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: JSON parsing failed: {e}", file=sys.stderr)
        return 3
    except (ValueError, sqlite3.Error) as e:
        print(f"error: {e}", file=sys.stderr)
        return 3

    if args.json:
        by_table = OrderedDict()
        for r in rows:
            if args.table and r["table_name"] != args.table:
                continue
            by_table.setdefault(r["table_name"], []).append(r)
        if not by_table:
            print(f"error: no matching table: {args.table}", file=sys.stderr)
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
            print(f"error: {e}", file=sys.stderr)
            return 3

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"written to {args.output}")
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
