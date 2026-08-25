#!/usr/bin/env python3
"""One-shot migration: bring every skill frontmatter up to SKILL-STANDARD-v2 §1.

Adds, when missing:
  license: Apache-2.0
  metadata.version / metadata.category / metadata.verified-date

Safety:
  - EOL-aware (preserves CRLF/LF exactly)
  - refuses to grow a file by more than 8 lines (anti-corruption guard)
  - idempotent: writes only when content actually changes
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
TODAY = date.today().isoformat()
VERSION = "1.0"
MAX_GROWTH = 8


def pack_categories():
    m = {}
    for pj in sorted(ROOT.glob("packs/*/pack.json")):
        data = json.loads(pj.read_text(encoding="utf-8"))
        for s in data.get("skills", []):
            m.setdefault(s["name"], pj.parent.name)
    return m


def fm_bounds(lines):
    """Return (start, end_exclusive) of frontmatter block, or None."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return (0, i + 1)
    return None


def migrate(path: Path, category: str):
    raw = path.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    had_trailing_nl = raw.endswith("\n")
    lines = raw.splitlines()

    bounds = fm_bounds(lines)
    if bounds is None:
        return ["SKIP: no frontmatter"]
    start, end = bounds

    actions = []

    # --- locate top-level keys and the metadata block -------------------
    lic_idx = meta_idx = None
    meta_end = None
    meta_keys = set()
    for i in range(start + 1, end - 1):
        line = lines[i]
        if re.match(r"^[A-Za-z][A-Za-z0-9_-]*:\s*", line):
            key = line.split(":", 1)[0]
            if key == "license":
                lic_idx = i
            elif key == "metadata":
                meta_idx = i
                meta_end = i + 1
            elif meta_idx is not None and meta_end == i:
                pass
        elif meta_idx is not None and re.match(r"^\s+[A-Za-z][A-Za-z0-9_-]*:\s*", line):
            mk = line.strip().split(":", 1)[0]
            meta_keys.add(mk)
            meta_end = i + 1
        elif meta_idx is not None and not line.strip():
            # blank line inside metadata block: keep block open
            meta_end = i + 1

    inserts_tail = []  # appended just before closing ---
    need_meta = {"version": VERSION, "category": category, "verified-date": TODAY}

    if lic_idx is None:
        inserts_tail.append("license: Apache-2.0")
        actions.append("+license")

    if meta_idx is None:
        block = ["metadata:"]
        for k, v in need_meta.items():
            if k not in meta_keys:
                block.append(f'  {k}: "{v}"')
        inserts_tail.extend(block)
        actions.append("+metadata{all}")
    else:
        missing = [k for k in need_meta if k not in meta_keys]
        if missing:
            extra = [f'  {k}: "{need_meta[k]}"' for k in missing]
            lines[meta_end:meta_end] = extra
            end += len(extra)
            actions.append("+metadata.{" + ",".join(missing) + "}")

    if inserts_tail:
        lines[end - 1 : end - 1] = inserts_tail

    # --- anti-corruption guard ------------------------------------------
    growth = len(lines) - len(raw.splitlines())
    if growth > MAX_GROWTH:
        return [f"ABORT: would grow by {growth} lines"]

    new_raw = eol.join(lines) + ("\n" if had_trailing_nl else "")
    if new_raw == raw:
        return actions  # nothing changed
    path.write_bytes(new_raw.encode("utf-8"))
    return actions


def main():
    cats = pack_categories()
    touched = clean = skipped = 0
    for p in sorted(SKILLS.rglob("SKILL.md")):
        parts = set(p.parts)
        if "_common" in parts or "assets" in parts:
            continue
        cat = cats.get(p.parent.name, "uncategorized")
        try:
            acts = migrate(p, cat)
        except Exception as e:  # noqa: BLE001
            print(f"{p.parent.name}: EXCEPTION {e}")
            skipped += 1
            continue
        real = [a for a in acts if not a.startswith(("SKIP", "ABORT"))]
        if any(a.startswith(("SKIP", "ABORT", "EXCEPTION")) for a in acts):
            print(f"{p.parent.name}: {acts[-1]}")
            skipped += 1
        elif real:
            touched += 1
            print(f"{p.parent.name}: {', '.join(real)}")
        else:
            clean += 1
    print(f"\nmigrated: {touched}, already compliant: {clean}, skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
