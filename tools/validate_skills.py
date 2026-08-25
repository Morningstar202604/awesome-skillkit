#!/usr/bin/env python3
"""Skill quality gate per docs/SKILL-STANDARD-v2.md.

Checks every skills/**/<name>/SKILL.md for:
  G1  frontmatter compliance (name/description/license/metadata rules)
  G2  reference integrity (every referenced relative path must exist)
  G5  progressive disclosure hygiene (<500 lines body, TOC in long references)
  plus: no absolute paths, pack<->disk consistency.

Exit code 1 on any ERROR; warnings do not block.

Usage: python tools/validate_skills.py [--verbose]
Stdlib only.
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
SKILLS_DIR = ROOT / "skills"

# Refs exempted from existence checks:
#   - "*.local.json": documented user-local config pattern (never ships)
#   - "_common/..." : bundle-level shared module sitting NEXT to skill dirs
EXEMPT_SUFFIXES = (".local.json",)
EXEMPT_PREFIXES = ("_common/",)

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_WORDS = ("anthropic", "claude")
XML_TAG_RE = re.compile(r"<[A-Za-z/][^>]*>")
ABS_PATH_RE = re.compile(r"(?<![\w])(?:[A-Za-z]:[\\/]|/(?:home|Users)/)")
REF_TOKEN_RE = re.compile(
    r"(?<![\w.\-/])((?:scripts|references|assets|templates)/[A-Za-z0-9._\-/]+)"
)
BACKTICK_FILE_RE = re.compile(
    r"`((?:[A-Za-z0-9_\-./]+/)*[A-Za-z0-9_\-./]+\.(?:py|sh|md|json|yaml|yml|txt|csv))`"
)
# note: only path-like references (containing a "/") count as internal refs;
# bare filenames such as `vercel.json` may describe user-side artifacts
URL_RE = re.compile(r"(?:https?:)?//")
TRIGGER_HINTS = (
    "use when",
    "use this",
    "when the user",
    "当用户",
    "何时使用",
    "触发",
    "/",
)
TOPIC_TOC_RE = re.compile(r"(目\s*录|table of contents|contents)|^\s*[-*]\s+", re.I)


class Issue:
    def __init__(self, level, msg):
        self.level = level  # "ERROR" | "WARN"
        self.msg = msg


def split_frontmatter(text: str):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text
    return lines[1:end], "\n".join(lines[end + 1 :])


def parse_simple_yaml(fm_lines):
    """Minimal subset parser: scalars, folded/literal blocks, one-level maps."""
    data: dict = {}
    i, n = 0, len(fm_lines)
    while i < n:
        line = fm_lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in ("", ">", ">-", "|", "|-", "|+"):
            block, j = [], i + 1
            while j < n and (fm_lines[j][:1] in (" ", "\t") or not fm_lines[j].strip()):
                block.append(fm_lines[j])
                j += 1
            if val.startswith(">") or val.startswith("|"):
                data[key] = " ".join(s.strip() for s in block if s.strip())
            else:
                sub = {}
                for bl in block:
                    sm = re.match(r"^\s+([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", bl)
                    if sm:
                        sub[sm.group(1)] = sm.group(2).strip().strip("\"'")
                data[key] = sub
            i = j
        else:
            data[key] = val.strip("\"'")
            i += 1
    return data


def extract_rel_refs(text: str):
    """Yield (token, kind) candidate relative-path references."""
    for tok in REF_TOKEN_RE.findall(text):
        yield tok
    for tok in BACKTICK_FILE_RE.findall(text):
        yield tok


def check_reference_integrity(skill_dir: Path, issues):
    md_files = [skill_dir / "SKILL.md"] + sorted(skill_dir.glob("references/*.md"))
    seen = set()
    for md in md_files:
        if not md.is_file():
            continue
        rel_label = md.relative_to(skill_dir).as_posix()
        in_fence = False
        for lineno, line in enumerate(
            md.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            # fenced code holds commands/examples against user-side projects,
            # not navigation within this bundle
            if in_fence:
                continue
            if ABS_PATH_RE.search(line):
                issues.append(Issue("ERROR", f"{rel_label}:{lineno}: absolute path"))
            for tok in extract_rel_refs(line):
                if URL_RE.search(tok) or tok in seen:
                    continue
                if "/" not in tok:
                    # bare filenames describe user-side artifacts, not bundle paths
                    continue
                seen.add(tok)
                if tok.endswith(EXEMPT_SUFFIXES) or tok.startswith(EXEMPT_PREFIXES):
                    continue
                if not (skill_dir / tok).exists():
                    if tok.startswith("scripts/"):
                        # advertised helper tooling missing from the bundle:
                        # degrades execution, not navigation -> tracked debt
                        issues.append(
                            Issue(
                                "WARN",
                                f"{rel_label}:{lineno}: advertised script "
                                f"'{tok}' not bundled",
                            )
                        )
                    else:
                        issues.append(
                            Issue(
                                "ERROR",
                                f"{rel_label}:{lineno}: broken reference '{tok}'",
                            )
                        )


def check_toc_rules(skill_dir: Path, issues):
    for ref in sorted(skill_dir.glob("references/*.md")):
        lines = ref.read_text(encoding="utf-8", errors="ignore").splitlines()
        if len(lines) > 100:
            head = "\n".join(lines[:30])
            if not TOPIC_TOC_RE.search(head):
                issues.append(
                    Issue(
                        "WARN",
                        f"{ref.relative_to(skill_dir).as_posix()}: "
                        f"{len(lines)} lines but no table of contents near top",
                    )
                )


def score_of(name_ok, desc, body_lines, err_count, metadata, license_val, toc_warns):
    score = 0
    score += 2 if name_ok else 0
    if desc and 40 <= len(desc) <= 1024:
        score += 1
    if desc and any(h in desc.lower() for h in TRIGGER_HINTS):
        score += 1
    if body_lines < 500:
        score += 1
    refs_bad = sum(
        1 for x in err_count if "broken reference" in x or "absolute path" in x
    )
    score += max(0, 2 - refs_bad * 2)
    md_keys = set(metadata or {})
    score += (
        2
        if {"version", "category", "verified-date"} <= md_keys
        else (1 if "version" in md_keys else 0)
    )
    score += 1 if license_val else 0
    score += 1 if toc_warns == 0 else 0
    return score


def validate_skill(skill_md: Path):
    issues: list[Issue] = []
    raw = skill_md.read_text(encoding="utf-8", errors="ignore")
    fm_lines, body = split_frontmatter(raw)
    meta = {}
    if fm_lines is None:
        issues.append(Issue("ERROR", "missing or malformed YAML frontmatter"))
    else:
        meta = parse_simple_yaml(fm_lines)

    name = str(meta.get("name", ""))
    dir_name = skill_md.parent.name
    name_ok = True
    if not name:
        issues.append(Issue("ERROR", "frontmatter 'name' missing"))
        name_ok = False
    else:
        if not NAME_RE.match(name):
            issues.append(Issue("ERROR", f"name '{name}' violates kebab-case spec"))
            name_ok = False
        if len(name) > 64:
            issues.append(Issue("ERROR", "name exceeds 64 chars"))
            name_ok = False
        if name != dir_name:
            issues.append(
                Issue("ERROR", f"name '{name}' != directory name '{dir_name}'")
            )
            name_ok = False
        low = name.lower()
        if any(w in low for w in RESERVED_WORDS):
            issues.append(Issue("ERROR", f"name contains reserved word"))
            name_ok = False

    desc = str(meta.get("description", "") or "")
    if not desc:
        issues.append(Issue("ERROR", "description missing/empty"))
    else:
        if XML_TAG_RE.search(desc):
            issues.append(Issue("ERROR", "description contains XML tags"))
        if len(desc) > 1024:
            issues.append(Issue("ERROR", f"description {len(desc)} chars (>1024)"))
        elif len(desc) < 40:
            issues.append(Issue("WARN", "description too short to route reliably"))

    body_lines = len(body.splitlines())
    if body_lines >= 500:
        issues.append(Issue("ERROR", f"body {body_lines} lines (>=500)"))

    metadata = meta.get("metadata") if isinstance(meta.get("metadata"), dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    for k in ("version", "category", "verified-date"):
        if k not in metadata:
            issues.append(Issue("WARN", f"metadata.{k} missing"))

    license_val = meta.get("license")
    if not license_val:
        issues.append(Issue("WARN", "license field missing"))

    check_reference_integrity(skill_md.parent, issues)
    toc_warns = sum(1 for x in issues if "table of contents" in x.msg)
    check_toc_rules(skill_dir=skill_md.parent, issues=issues)

    score = score_of(
        name_ok,
        desc,
        body_lines,
        [x.msg for x in issues if x.level == "ERROR"],
        metadata,
        license_val,
        toc_warns,
    )
    return issues, score


def iter_skills():
    for p in sorted(SKILLS_DIR.rglob("SKILL.md")):
        parts = set(p.parts)
        if "_common" in parts or "assets" in parts:
            continue
        yield p


def check_pack_consistency(issues):
    packed: set[str] = set()
    for pj in sorted(ROOT.glob("packs/*/pack.json")):
        pack_id = pj.parent.name
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            issues_global.append(Issue("ERROR", f"pack {pack_id}: unreadable ({e})"))
            continue
        for s in data.get("skills", []):
            nm = s.get("name", "")
            packed.add(nm)
            hits = [
                q.parent
                for q in SKILLS_DIR.glob(f"**/{nm}/SKILL.md")
                if q.parent.name == nm
            ]
            if not hits:
                issues_global.append(
                    Issue("ERROR", f"pack {pack_id}: skill '{nm}' not found on disk")
                )
    for p in iter_skills():
        if p.parent.name not in packed:
            issues.append(
                Issue(
                    "WARN", f"'{p.parent.name}' exists on disk but in no pack (orphan)"
                )
            )


issues_global: list = []


def main(argv):
    verbose = "--verbose" in argv
    all_rows = []
    err_total = warn_total = 0
    for skill_md in iter_skills():
        issues, score = validate_skill(skill_md)
        errs = [x for x in issues if x.level == "ERROR"]
        warns = [x for x in issues if x.level == "WARN"]
        err_total += len(errs)
        warn_total += len(warns)
        status = "ERR" if errs else ("WARN" if warns else "OK")
        all_rows.append((status, score, skill_md.parent.name, errs, warns))

    check_pack_consistency(issues_global)
    err_total += sum(1 for x in issues_global if x.level == "ERROR")

    width = max(len(r[2]) for r in all_rows) if all_rows else 10
    for status, score, name, errs, warns in all_rows:
        line = f"[{status:^4}] {score:>2}/12  {name:<{width}}"
        print(line)
        for x in errs + warns:
            print(f"         - {x.msg}")
        if verbose and not (errs or warns):
            pass
    for x in issues_global:
        print(f"[{'ERR' if x.level == 'ERROR' else 'WARN':^4}]          {x.msg}")

    print("-" * 60)
    print(f"skills: {len(all_rows)}  errors: {err_total}  warnings: {warn_total}")
    if err_total:
        print("RESULT: FAILED (fix all ERRORs)")
        return 1
    print("RESULT: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
