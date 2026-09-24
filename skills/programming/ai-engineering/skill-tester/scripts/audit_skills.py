#!/usr/bin/env python3
"""
Audit Skills -- batch audit of every skill in a repository.

Inside the skill-tester skill, this chains the three scripts "validate + score +
security check" together, runs them over every skill under a directory, and emits
a summary report.

Division of labor with tools/validate_skills.py (the repo-level gate):
  - tools/validate_skills.py -- the awesome-skillkit repo's own compliance gate,
                                with rules hard-coded against this repo's
                                SKILL-STANDARD-v2;
  - this script              -- a generic auditor that can point at any skill
                                directory and additionally runs a security score;
                                suited to reviewing someone else's skill repo.

Usage:
    python3 audit_skills.py /path/to/skills
    python3 audit_skills.py /path/to/skills --json
    python3 audit_skills.py /path/to/skills --min-score 75 --fail-under
    python3 audit_skills.py /path/to/skills --no-security

Exit codes: 0 all pass / 1 some item below threshold (only with --fail-under) / 2 bad arguments
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "skill_validator.py"
SCORER = SCRIPT_DIR / "quality_scorer.py"
SECURITY = SCRIPT_DIR / "security_scorer.py"

# per-subprocess timeout (seconds). A skill directory may be large, but a single skill must not hang the whole audit.
CALL_TIMEOUT = 60


def find_skills(root: Path):
    """Find every skill directory under root (dirs containing SKILL.md), sorted by path."""
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted({p.parent for p in root.rglob("SKILL.md")})


def run_json(script: Path, target: Path, extra=None):
    """Invoke a sub-script and parse its JSON output.

    Returns (data, error_message). A non-zero exit from the sub-script is not a
    failure -- the validator uses the exit code to mean "non-compliant", but the
    JSON is still valid, so read stdout rather than the exit code.
    """
    if not script.is_file():
        return None, f"missing script {script.name}"
    cmd = [sys.executable, str(script), str(target), "--json"]
    if extra:
        cmd.extend(extra)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CALL_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None, f"{script.name} timed out (>{CALL_TIMEOUT}s)"

    out = proc.stdout.strip()
    if not out:
        err = (proc.stderr or "").strip().splitlines()
        return None, f"{script.name} produced no output" + (f": {err[-1]}" if err else "")
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, f"{script.name} output is not JSON (first 80 chars: {out[:80]})"


def pick(data, *keys):
    """From sub-script output, take the first present key in priority order."""
    if not isinstance(data, dict):
        return None
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return None


def audit_one(skill_dir: Path, with_security: bool):
    """Audit a single skill; return a result dict."""
    rec = {
        "name": skill_dir.name,
        "path": str(skill_dir),
        "quality_score": None,
        "letter_grade": None,
        "tier": None,
        "compliance_level": None,
        "security_score": None,
        "security_issues": [],
        "errors": [],
        "warnings": [],
    }

    vdata, verr = run_json(VALIDATOR, skill_dir)
    if verr:
        rec["errors"].append(verr)
    else:
        rec["compliance_level"] = pick(vdata, "compliance_level", "level", "status")
        # sub-check results may contain error/warning lists
        checks = pick(vdata, "checks")
        if isinstance(checks, dict):
            for cname, cval in checks.items():
                if isinstance(cval, dict):
                    if cval.get("status") in ("fail", "error", "FAIL"):
                        rec["errors"].append(f"{cname}: {cval.get('message', 'fail')}")
                    elif cval.get("status") in ("warn", "warning", "WARN"):
                        rec["warnings"].append(f"{cname}: {cval.get('message', 'warn')}")
        for key, bucket in (("errors", "errors"), ("warnings", "warnings")):
            v = pick(vdata, key)
            if isinstance(v, list):
                rec[bucket].extend(str(x) for x in v)

    sdata, serr = run_json(SCORER, skill_dir)
    if serr:
        rec["errors"].append(serr)
    else:
        rec["quality_score"] = pick(sdata, "overall_score", "score", "total_score")
        rec["letter_grade"] = pick(sdata, "letter_grade", "grade")
        rec["tier"] = pick(sdata, "tier_recommendation", "tier")

    if with_security:
        secdata, secerr = run_json(SECURITY, skill_dir)
        if secerr:
            rec["warnings"].append(secerr)
        else:
            rec["security_score"] = pick(secdata, "overall_score", "score")
            issues = pick(secdata, "issues", "findings")
            if isinstance(issues, list):
                rec["security_issues"] = [
                    (i.get("message") or i.get("description") or str(i))
                    if isinstance(i, dict)
                    else str(i)
                    for i in issues
                ]

    return rec


def fmt_score(v):
    if v is None:
        return "  n/a"
    return f"{v:>5.1f}" if isinstance(v, (int, float)) else f"{v:>5}"


def print_table(records, min_score):
    print("=" * 84)
    print(f"{'Skill':<34}{'Quality':>7}{'Grade':>6}{'Tier':>12}{'Security':>7}  Status")
    print("-" * 84)
    for r in sorted(records, key=lambda x: (x["quality_score"] is None, x["quality_score"] or 0)):
        q = r["quality_score"]
        below = min_score is not None and (q is None or q < min_score)
        if r["errors"]:
            status = "FAIL"
        elif below:
            status = f"BELOW<{min_score}"
        elif r["warnings"]:
            status = "warn"
        else:
            status = "ok"
        grade = r["letter_grade"] or "-"
        tier = (r["tier"] or "-")[:11]
        print(
            f"{r['name'][:33]:<34}{fmt_score(q)}{str(grade):>6}"
            f"{tier:>12}{fmt_score(r['security_score']):>7}  {status}"
        )
    print("-" * 84)

    total = len(records)
    failing = [r for r in records if r["errors"]]
    below = [
        r
        for r in records
        if min_score is not None
        and (r["quality_score"] is None or r["quality_score"] < min_score)
    ]
    scored = [r["quality_score"] for r in records if r["quality_score"] is not None]
    avg = sum(scored) / len(scored) if scored else 0
    print(f"Total skills: {total}   avg score: {avg:.1f}   validation failures: {len(failing)}", end="")
    if min_score is not None:
        print(f"   below {min_score}: {len(below)}")
    else:
        print()

    for r in records:
        if r["errors"] or r["warnings"]:
            print(f"\n[{r['name']}]")
            for e in r["errors"]:
                print(f"  ERROR  {e}")
            for w in r["warnings"][:5]:
                print(f"  WARN   {w}")
            if len(r["warnings"]) > 5:
                print(f"  WARN   ... {len(r['warnings']) - 5} more")
    print("=" * 84)
    return failing, below


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Batch-audit every skill under a directory (validate + score + security)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("root", help="skill root directory, or a single skill directory")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--min-score", type=float, default=None, help="quality score floor used to flag items below target")
    ap.add_argument(
        "--fail-under",
        action="store_true",
        help="exit 1 when any item is below --min-score or fails validation (for CI)",
    )
    ap.add_argument("--no-security", action="store_true", help="skip the security score (faster)")
    ap.add_argument("--limit", type=int, default=None, help="audit only the first N skills (for debugging)")
    args = ap.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: directory not found: {root}", file=sys.stderr)
        return 2

    skills = find_skills(root)
    if args.limit:
        skills = skills[: args.limit]
    if not skills:
        print(f"error: no skill directory containing SKILL.md found under {root}", file=sys.stderr)
        return 2

    records = [audit_one(d, not args.no_security) for d in skills]

    if args.json:
        scored = [r["quality_score"] for r in records if r["quality_score"] is not None]
        payload = {
            "root": str(root),
            "skill_count": len(records),
            "average_quality_score": round(sum(scored) / len(scored), 2) if scored else None,
            "validation_failures": sum(1 for r in records if r["errors"]),
            "min_score": args.min_score,
            "skills": records,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        failing = [r for r in records if r["errors"]]
        below = [
            r
            for r in records
            if args.min_score is not None
            and (r["quality_score"] is None or r["quality_score"] < args.min_score)
        ]
    else:
        failing, below = print_table(records, args.min_score)

    if args.fail_under and (failing or below):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
