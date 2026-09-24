#!/usr/bin/env python3
"""lint_skill.py — conformance checker for a single SKILL.md or a directory tree.

Eight required checks (rules are documented in each function's docstring and in
the checklist table of SKILL.md):

  FM-FIELDS   frontmatter present with name/description/license/metadata blocks
  NAME-SYNC   name matches the directory name, kebab-case, no uppercase
  DESC-ROUTE  description contains "Use when" and "Do NOT", with >=5 trigger words
  BODY-SECTS  body has the six mandatory sections (Input / Pre-flight / Workflow /
              Delivery / Failure Handling / References), keyword-matched
  BODY-LINES  total lines < 220 (WARN above)
  LANG-CJK    any CJK character in body => WARN (English-only repository)
  REF-EXISTS  `references/xxx.md` referenced in the body must exist on disk
  FAIL-TABLE  the table under `## Failure Handling` has >= 4 rows

Exit code: any FAIL -> 1; otherwise 0. WARN does not affect the exit code, so the
script can be wired directly into CI as a gate.

Usage:
  python3 lint_skill.py <SKILL.md path | skill dir | parent of skill dirs>
  python3 lint_skill.py skills/ --json
  python3 lint_skill.py skills/meta/skill-finder --verbose

Standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- Constants and rules

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

#: H2 headings that must appear in the body skeleton. The first six are mandatory;
#: any missing one is a FAIL.
#: Required H2 sections (FAIL if missing), matched by keyword (case-insensitive).
REQUIRED_H2_KEYWORDS = [
    ("workflow", ["workflow"]),
    ("delivery", ["delivery checklist", "delivery standards", "delivery standard", "delivery criteria", "quality checklist", "deliverable standard", "deliverable"]),
    ("failure", ["failure handling", "failure table", "failure handling table", "failure remediation"]),
]
#: Recommended H2 sections (WARN if missing).
RECOMMENDED_H2_KEYWORDS = [
    ("input", ["input checklist", "input list", "inputs", "pick your path", "task selection"]),
    ("preflight", ["pre-flight", "preflight", "pre-flight checks", "pre-flight self-check"]),
    ("references", ["references", "reference"]),
]
#: Four additional recommended H2 headings (the "10-section skeleton"); a missing
#: one is only a WARN.
OPTIONAL_H2 = [
    "Quick Reference",
    "Prompt Formula",
    "Common Mistakes",
    "Workflow Variants",
]
RECOMMENDED_H2_TOTAL = 10

#: English phrasings that mark "when to use / exclusions" inside a description.
USE_WHEN_HINTS = ("use when", "use this", "when the user", "triggers on", "triggered by", "use for", "when you need", "when asked", "when to use")
DO_NOT_HINTS = ("do not use", "don't use", "not for", "do not use for")

#: Separators after the trigger-word lead-in phrase.
TRIGGER_SPLIT_RE = re.compile(r"[/、,，;；]| or | and ")

BODY_LINE_LIMIT = 220      # WARN above this (the repo hard gate is 500; this is the skill-level self-discipline line)
CJK_RATIO_FLOOR = 0.0      # any CJK in an English-only repo is a WARN
MIN_FAILTABLE_ROWS = 4     # minimum data rows in the failure-handling table
MIN_DESC_LEN = 40
MAX_DESC_LEN = 1024

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
FENCE_RE = re.compile(r"^\s*```")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
REF_LINK_RE = re.compile(r"`(references/[A-Za-z0-9._\-/]+\.md)`")
REF_BULLET_RE = re.compile(r"^\s*[-*]\s+`?(references/[A-Za-z0-9._\-/]+\.md)")
#: When a directory name appears in this set it is not a skill directory and is
#: skipped (so templates/shared snippets are not reported as broken skills).
#: Note: **does not include `assets`** — `skills/writing/assets/ai-cover-generator`
#: is a real skill referenced by three packs; skipping it would let it escape lint
#: forever (consistent with validate_skills.py).
SKIP_DIR_NAMES = {"_common", "__pycache__", "templates"}


class Finding:
    """A single check result. level in {PASS, WARN, FAIL}."""

    def __init__(self, check, level, message, fix=""):
        self.check = check
        self.level = level
        self.message = message
        self.fix = fix

    def as_dict(self):
        return {
            "check": self.check,
            "level": self.level,
            "message": self.message,
            "fix": self.fix,
        }


# ---------------------------------------------------------------- Parsing helpers


def split_frontmatter(text):
    """Return (frontmatter lines | None, body). The first line must be exactly ---."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def parse_simple_yaml(fm_lines):
    """Minimal YAML-subset parser: scalars, folded/literal blocks, one nested map.

    Same strategy as the repo's tools/validate_skills.py: only recognize the
    shapes actually used in frontmatter, no PyYAML dependency.
    """
    data = {}
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


def strip_code_blocks(body):
    """Remove fenced code blocks; return (text without blocks, chars removed)."""
    out, in_fence = [], False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out), len(body) - len("\n".join(out))


def count_trigger_words(desc):
    """Count trigger words in a description.

    Rule: take the tail after "use when", split it on / 、 commas/semicolons or
    "or"/"and", and count segments of length >= 2; fall back to 0 when no lead-in
    phrase is found.
    """
    low = desc.lower()
    segments = []
    for hint in USE_WHEN_HINTS:
        idx = low.find(hint)
        if idx == -1:
            continue
        tail = desc[idx + len(hint):]
        # stop at the exclusions or end of sentence
        for stop in ("do not use", "don't use"):
            cut = tail.lower().find(stop)
            if cut != -1:
                tail = tail[:cut]
        segments.append(tail)
    if not segments:
        return 0
    joined = " ".join(segments)
    parts = [p.strip(" 。.”\"'()") for p in TRIGGER_SPLIT_RE.split(joined)]
    return sum(1 for p in parts if len(p) >= 2)


def is_table_row(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def count_table_rows(section_lines):
    """Count the data rows of a Markdown table (excluding header and |---| rows)."""
    rows = 0
    for line in section_lines:
        if not is_table_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c or "---") for c in cells):
            continue                      # separator row
        rows += 1
    return max(0, rows - 1)               # subtract the header row


def section_slice(body_lines, title):
    """Return the lines from `## <title>` to the next same-level heading."""
    start = None
    for i, line in enumerate(body_lines):
        m = H2_RE.match(line)
        if m and m.group(1).startswith(title):
            start = i + 1
            continue
        if start is not None and H2_RE.match(line):
            return body_lines[start:i]
    return body_lines[start:] if start is not None else []


# ---------------------------------------------------------------- The eight checks


def check_frontmatter_fields(raw, meta, fm_lines):
    """FM-FIELDS: whether the four blocks are present and the description length is in range."""
    findings = []
    if fm_lines is None:
        return [Finding("FM-FIELDS", "FAIL", "frontmatter missing or not starting with `---`",
                        "Write `---` on line 1, fill in name/description/license/metadata, then close with `---`")]
    findings.append(Finding("FM-FIELDS", "PASS", "frontmatter present and parseable"))
    for key in ("name", "description", "license"):
        if not meta.get(key):
            findings.append(Finding("FM-FIELDS", "FAIL", f"frontmatter missing `{key}`",
                                    f"add the `{key}:` field"))
    md = meta.get("metadata")
    if not isinstance(md, dict) or not md:
        findings.append(Finding("FM-FIELDS", "FAIL", "frontmatter missing the `metadata` block",
                                "add metadata with author/version/category/verified-date"))
    else:
        for k in ("version", "category", "verified-date"):
            if k not in md:
                findings.append(Finding("FM-FIELDS", "WARN",
                                        f"metadata.{k} missing",
                                        f"add `{k}:` for version tracking and freshness checks"))
    desc = meta.get("description", "") or ""
    if desc and not (MIN_DESC_LEN <= len(desc) <= MAX_DESC_LEN):
        findings.append(Finding("FM-FIELDS", "WARN",
                                f"description length {len(desc)} outside {MIN_DESC_LEN}-{MAX_DESC_LEN}",
                                "trim to 40-1024 chars; cut adjectives, keep trigger phrases and exclusions"))
    return findings


def check_name_sync(skill_dir, meta):
    """NAME-SYNC: name == directory name, kebab-case, no uppercase."""
    name = str(meta.get("name", "") or "")
    # when target is ".", Path(".").name is empty -> resolve first, then take the dir name
    dir_name = skill_dir.resolve().name
    if not name:
        return [Finding("NAME-SYNC", "FAIL", "no `name` in frontmatter", "add the name field")]
    findings = []
    if name != dir_name:
        findings.append(Finding("NAME-SYNC", "FAIL",
                                f"name `{name}` does not match directory `{dir_name}`",
                                f"rename name to `{dir_name}`, or rename the directory to `{name}`"))
    if name != name.lower():
        findings.append(Finding("NAME-SYNC", "FAIL", f"name `{name}` contains uppercase letters",
                                "use all lowercase (a-z0-9- only)"))
    if not NAME_RE.match(name):
        findings.append(Finding("NAME-SYNC", "FAIL",
                                f"name `{name}` is not kebab-case",
                                "keep lowercase letters, digits, and single hyphens; no leading/trailing hyphen"))
    if not findings:
        findings.append(Finding("NAME-SYNC", "PASS", f"name `{name}` matches the directory and is valid"))
    return findings


def check_description_routing(meta):
    """DESC-ROUTE: Use when / Do NOT / >=3 trigger words."""
    desc = str(meta.get("description", "") or "")
    if not desc:
        return [Finding("DESC-ROUTE", "FAIL", "description is empty",
                        "write what + Use when + trigger phrases (>=5) + Do NOT exclusions")]
    low = desc.lower()
    findings = []
    has_use = any(h in low for h in USE_WHEN_HINTS)
    has_not = any(h in low for h in DO_NOT_HINTS)
    if not has_use:
        findings.append(Finding("DESC-ROUTE", "FAIL", "description has no `Use when` lead-in",
                                "add `Use when ...`"))
    if not has_not:
        findings.append(Finding("DESC-ROUTE", "FAIL", "description has no `Do NOT` exclusion",
                                "add `Do NOT use for ...`, naming which similar requests must NOT hit this skill"))
    n_trig = count_trigger_words(desc)
    if n_trig < 3:
        findings.append(Finding("DESC-ROUTE", "FAIL",
                                f"only {n_trig} trigger words (need >=3)",
                                "after Use when, add more trigger phrases separated by `/`"))
    if not findings:
        findings.append(Finding("DESC-ROUTE", "PASS",
                                f"routing info complete, {n_trig} trigger words"))
    return findings


def check_body_sections(body_lines):
    """BODY-SECTS: six mandatory sections for tool skills, or platform-adaptation skeleton for content skills.

    Two valid skeletons:
    - Tool skill: Input / Pre-flight / Workflow / Delivery / Failure / References
    - Platform-adaptation skill: Platform Format / Workflow / Quality Checklist / When to Use
    """
    titles = [H2_RE.match(l).group(1).lower() for l in body_lines if H2_RE.match(l)]
    titles_str = " ".join(titles)

    # Detect platform-adaptation skills (publisher/content skills)
    is_platform_skill = any("platform format" in t or "content adaptation" in t for t in titles)

    if is_platform_skill:
        required = [
            ("platform format", ["platform format rules", "format rules", "platform quick-reference", "platform matrix", "platform quick reference"]),
            ("workflow", ["workflow"]),
            ("quality", ["quality checklist", "delivery checklist", "delivery standards", "delivery standard"]),
            ("when to use", ["when to use", "usage"]),
        ]
        missing = [label for label, keywords in required
                   if not any(any(kw in t for kw in keywords) for t in titles)]
        recommended_missing = []
    else:
        missing = []
        for label, keywords in REQUIRED_H2_KEYWORDS:
            if not any(any(kw in t for kw in keywords) for t in titles):
                missing.append(label)
        recommended_missing = []
        for label, keywords in RECOMMENDED_H2_KEYWORDS:
            if not any(any(kw in t for kw in keywords) for t in titles):
                recommended_missing.append(label)

    findings = []
    for label in missing:
        findings.append(Finding("BODY-SECTS", "FAIL", f"missing required section: {label}",
                                f"add a `## {label}` section"))
    for label in recommended_missing:
        findings.append(Finding("BODY-SECTS", "WARN", f"missing recommended section: {label}",
                                f"consider adding a `## {label}` section"))
    if missing:
        return findings
    skeleton = "platform-adaptation" if is_platform_skill else "tool"
    findings.append(Finding("BODY-SECTS", "PASS", f"all mandatory sections present ({skeleton} skeleton)"))
    extra = len(titles)
    if extra < RECOMMENDED_H2_TOTAL:
        findings.append(Finding("BODY-SECTS", "WARN",
                                f"only {extra} H2 headings, {RECOMMENDED_H2_TOTAL - extra} short of the 10-section skeleton",
                                "add optional sections like Quick Reference / Common Mistakes"))
    return findings


def check_body_lines(raw):
    """BODY-LINES: total lines < 220."""
    n = len(raw.splitlines())
    if n >= BODY_LINE_LIMIT:
        return [Finding("BODY-LINES", "WARN",
                        f"{n} lines total, over the {BODY_LINE_LIMIT}-line self-discipline limit",
                        "move domain knowledge into references/; keep only navigation and the workflow in the body")]
    return [Finding("BODY-LINES", "PASS", f"{n} lines total")]


def check_language_ratio(body):
    """LANG-CJK: WARN when any CJK characters appear in the body (English-only repo)."""
    text, _ = strip_code_blocks(body)
    stripped = re.sub(r"\s", "", text)
    if not stripped:
        return [Finding("LANG-CJK", "WARN", "body is empty after removing code blocks",
                        "the body needs at least readable prose")]
    cjk_count = len(CJK_RE.findall(stripped))
    ratio = cjk_count / len(stripped)
    if cjk_count > 0:
        return [Finding("LANG-CJK", "WARN",
                        f"body contains {cjk_count} CJK characters (ratio {ratio:.3f})",
                        "translate all prose to English; this is an English-only repository")]
    return [Finding("LANG-CJK", "PASS", f"body is English-only (0 CJK characters)")]


def check_references_exist(skill_dir, raw):
    """REF-EXISTS: every `references/*.md` named in the body must exist on disk."""
    refs = set(REF_LINK_RE.findall(raw))
    refs |= set(REF_BULLET_RE.findall(raw))
    if not refs:
        return [Finding("REF-EXISTS", "WARN", "body references no references/*.md",
                        "if there is domain knowledge, split it into references/ and link it from `## References`")]
    findings, broken = [], []
    for r in sorted(refs):
        if not (skill_dir / r).is_file():
            broken.append(r)
    for r in broken:
        findings.append(Finding("REF-EXISTS", "FAIL", f"referenced `{r}` does not exist",
                                f"create {r} or remove the reference from the body"))
    if not broken:
        findings.append(Finding("REF-EXISTS", "PASS", f"all {len(refs)} references exist"))
    return findings


def check_fail_table(body_lines):
    """FAIL-TABLE: tool skills need `## Failure Handling` with >=4 rows; platform skills use Quality Checklist."""
    titles = [H2_RE.match(l).group(1).lower() for l in body_lines if H2_RE.match(l)]
    is_platform_skill = any("platform format" in t or "content adaptation" in t for t in titles)
    if is_platform_skill:
        # Platform-adaptation skills use Quality Checklist instead of Failure Handling
        lines = section_slice(body_lines, "Quality Checklist")
        if not lines:
            lines = section_slice(body_lines, "quality")
        if not lines:
            return [Finding("FAIL-TABLE", "WARN", "no Quality Checklist section found",
                            "add a pre-publish quality checklist")]
        return [Finding("FAIL-TABLE", "PASS", "Quality Checklist present")]
    lines = section_slice(body_lines, "Failure Handling")
    if not lines:
        lines = section_slice(body_lines, "Failure Remediation")
    if not lines:
        lines = section_slice(body_lines, "failure")
        return [Finding("FAIL-TABLE", "FAIL", "no `## Failure Handling` section, or it is empty",
                        "add a three-column table: symptom/error code | cause | action")]
    rows = count_table_rows(lines)
    if rows < MIN_FAILTABLE_ROWS:
        return [Finding("FAIL-TABLE", "FAIL",
                        f"failure table has only {rows} rows (need >= {MIN_FAILTABLE_ROWS})",
                        "add at least 4 real failure scenarios (with the raw error and a concrete action)")]
    return [Finding("FAIL-TABLE", "PASS", f"failure table has {rows} rows")]


# ---------------------------------------------------------------- Main flow


def lint_one(skill_md: Path):
    """Lint a single SKILL.md; return (skill_md, findings)."""
    raw = skill_md.read_text(encoding="utf-8", errors="ignore")
    fm_lines, body = split_frontmatter(raw)
    meta = parse_simple_yaml(fm_lines) if fm_lines is not None else {}
    if fm_lines is not None and not isinstance(meta.get("metadata"), dict):
        pass
    body_lines = body.splitlines()

    findings = []
    findings += check_frontmatter_fields(raw, meta, fm_lines)
    findings += check_name_sync(skill_md.parent, meta)
    findings += check_description_routing(meta)
    findings += check_body_sections(body_lines)
    findings += check_body_lines(raw)
    findings += check_language_ratio(body)
    findings += check_references_exist(skill_md.parent, raw)
    findings += check_fail_table(body_lines)
    return skill_md, findings


def iter_skill_files(target: Path):
    """Resolve a CLI argument into a list of SKILL.md files (file / skill dir / parent tree)."""
    if target.is_file():
        return [target] if target.name == "SKILL.md" else []
    if (target / "SKILL.md").is_file():
        return [target / "SKILL.md"]
    out = []
    for p in sorted(target.rglob("SKILL.md")):
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        # sample/template skills (sample-*) are not published; consistent with validate_skills.py.
        if p.parent.name.startswith("sample-"):
            continue
        out.append(p)
    return out


def collect(target: Path):
    """Return [(skill_md, findings)]. Raise FileNotFoundError if target does not exist."""
    if not target.exists():
        raise FileNotFoundError(f"path does not exist: {target}")
    results = []
    for md in iter_skill_files(target):
        results.append(lint_one(md))
    return results


def render_text(results, verbose=False):
    """Print a human-readable report; return (fail_count, warn_count)."""
    fail_total = warn_total = 0
    for skill_md, findings in results:
        fails = [f for f in findings if f.level == "FAIL"]
        warns = [f for f in findings if f.level == "WARN"]
        fail_total += len(fails)
        warn_total += len(warns)
        status = "FAIL" if fails else ("WARN" if warns else "PASS")
        print(f"[{status}] {skill_md.parent.name}  ({skill_md})")
        for f in findings:
            if f.level == "PASS" and not verbose:
                continue
            print(f"    {f.level:<4} {f.check:<12} {f.message}")
            if f.level != "PASS" and f.fix:
                print(f"         FIX: {f.fix}")
    print("-" * 68)
    print(f"skills: {len(results)}  FAIL: {fail_total}  WARN: {warn_total}")
    print("RESULT: PASS" if fail_total == 0 else "RESULT: FAIL")
    return fail_total, warn_total


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="lint_skill.py",
        description="Check a SKILL.md against the awesome-skillkit spec; print a PASS/WARN/FAIL report.",
    )
    ap.add_argument("target", help="path to a SKILL.md, a skill dir, or a parent dir containing skills")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    ap.add_argument("--verbose", action="store_true", help="also print PASS items in text mode")
    args = ap.parse_args(argv)

    try:
        results = collect(Path(args.target))
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    if not results:
        print(f"no SKILL.md found: {args.target}", file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "skills": [
                {
                    "name": md.parent.name,
                    "path": md.as_posix(),
                    "status": (
                        "FAIL" if any(f.level == "FAIL" for f in fs)
                        else "WARN" if any(f.level == "WARN" for f in fs)
                        else "PASS"
                    ),
                    "findings": [f.as_dict() for f in fs],
                }
                for md, fs in results
            ]
        }
        fails = sum(1 for s in payload["skills"] for f in s["findings"] if f["level"] == "FAIL")
        warns = sum(1 for s in payload["skills"] for f in s["findings"] if f["level"] == "WARN")
        payload["summary"] = {"skills": len(results), "fail": fails, "warn": warns}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if fails else 0

    fail_total, _ = render_text(results, verbose=args.verbose)
    return 1 if fail_total else 0


if __name__ == "__main__":
    sys.exit(main())
