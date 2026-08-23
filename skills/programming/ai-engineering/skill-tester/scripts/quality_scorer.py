#!/usr/bin/env python3
"""
Quality Scorer - multi-dimensional quality assessment for a skill.

Default mode: 4 dimensions x 25% each:
    Documentation / Code Quality / Completeness / Usability

With --include-security: 5 dimensions x 20% each (adds Security, powered by
security_scorer.SecurityScorer).

Outputs a 0-100 overall score, letter grade (A+..F), tier recommendation
(BASIC/STANDARD/POWERFUL) and an improvement roadmap.

Usage:
    python quality_scorer.py <skill_path> [--json] [--detailed]
                             [--minimum-score N] [--include-security] [--batch]

Exit codes: 0 = at/above threshold, 1 = below threshold,
            2 = within 10 points below threshold (needs improvement).

Stdlib only. Python 3.8+.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from security_scorer import MAX_COMPONENT_SCORE, SecurityScorer  # noqa: E402

GRADE_THRESHOLDS = (
    (95, "A+"), (90, "A"), (85, "A-"), (80, "B+"), (75, "B"), (70, "B-"),
    (65, "C+"), (60, "C"), (55, "C-"), (50, "D"),
)

TIER_SKILL_MD_MIN_LINES = {"BASIC": 100, "STANDARD": 200, "POWERFUL": 300}
TIER_SCRIPTS_LOC = {"BASIC": (100, 300), "STANDARD": (300, 500), "POWERFUL": (500, 800)}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def assign_letter_grade(score: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


class QualityScorer:
    """Score one skill directory across documentation/code/completeness/usability."""

    def __init__(self, skill_path: Path, include_security: bool = False):
        self.skill_path = Path(skill_path)
        self.include_security = include_security

    # ------------------------------------------------------------ helpers

    def _read(self, rel: str) -> str:
        try:
            return (self.skill_path / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def _scripts(self) -> List[Path]:
        scripts_dir = self.skill_path / "scripts"
        return sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else []

    # ------------------------------------------------------------ dimensions

    def score_documentation(self) -> Tuple[float, List[str]]:
        notes: List[str] = []
        skill_md = self._read("SKILL.md")
        readme = self._read("README.md")

        # SKILL.md depth (40%)
        if not skill_md:
            md_score, notes = 0.0, ["SKILL.md missing"]
        else:
            lines = skill_md.count("\n") + 1
            has_frontmatter = bool(FRONTMATTER_RE.match(skill_md.lstrip("\ufeff")))
            code_blocks = skill_md.count("```") // 2
            length_pts = min(lines / 300, 1.0)
            fm_pts = 1.0 if has_frontmatter else 0.4
            example_pts = min(code_blocks / 4, 1.0)
            md_score = round((length_pts * 0.45 + fm_pts * 0.25 + example_pts * 0.30) * 100)
            if not has_frontmatter:
                notes.append("SKILL.md lacks YAML frontmatter (name/description)")
            if code_blocks < 2:
                notes.append("Add more fenced examples to SKILL.md")

        # README (25%)
        chars = len(readme.strip())
        readme_score = 95.0 if chars >= 1000 else 80.0 if chars >= 500 else \
            65.0 if chars >= 200 else 45.0 if chars > 0 else 0.0
        if chars == 0:
            notes.append("README.md missing or empty")

        # references (20%)
        refs_dir = self.skill_path / "references"
        ref_files = list(refs_dir.glob("*")) if refs_dir.is_dir() else []
        ref_chars = sum(len(p.read_text(encoding="utf-8", errors="replace"))
                        for p in ref_files if p.is_file()) or len(ref_files)
        refs_score = 90.0 if ref_chars >= 2000 and len(ref_files) >= 2 else \
            75.0 if len(ref_files) >= 2 else 60.0 if len(ref_files) == 1 else 20.0
        if not ref_files:
            notes.append("No reference documentation in references/")

        # examples in docs (15%)
        example_count = skill_md.lower().count("example")
        ex_score = min(example_count / 4, 1.0) * 100

        doc_score = round(md_score * 0.40 + readme_score * 0.25 +
                          refs_score * 0.20 + ex_score * 0.15)
        return float(doc_score), notes

    def score_code_quality(self) -> Tuple[float, List[str]]:
        notes: List[str] = []
        scripts = self._scripts()
        if not scripts:
            return 0.0, ["No Python scripts found"]

        loc_total = 0
        error_handling_hits = 0
        docstring_hits = 0
        dual_output_hits = 0

        for script in scripts:
            source = script.read_text(encoding="utf-8", errors="replace")
            loc_total += source.count("\n") + 1
            error_handling_hits += len(re.findall(r"\btry\b", source))
            docstring_hits += source.count('"""') // 2
            if "json" in source and ("argparse" in source or "click" in source):
                dual_output_hits += 1

        n = len(scripts)
        avg_loc = loc_total / n
        # LOC relative to tier bands: 100->weak, 500+ -> strong
        loc_score = min(max(avg_loc - 50, 0) / 450, 1.0) * 100
        eh_score = min(error_handling_hits / (n * 3), 1.0) * 100
        ds_score = min(docstring_hits / (n * 3), 1.0) * 100
        do_score = min(dual_output_hits / n, 1.0) * 100

        if error_handling_hits < n:
            notes.append("Sparse error handling (try/except) across scripts")
        if dual_output_hits < n:
            notes.append("Not all scripts support JSON + human output")
        if avg_loc < 100:
            notes.append(f"Scripts are thin (avg {avg_loc:.0f} LOC)")

        score = round(loc_score * 0.25 + eh_score * 0.25 +
                      ds_score * 0.25 + do_score * 0.25)
        return float(score), notes

    def score_completeness(self) -> Tuple[float, List[str]]:
        notes: List[str] = []
        required = ["scripts"]
        recommended = ["assets", "references", "expected_outputs"]
        present_req = sum((self.skill_path / d).is_dir() for d in required)
        present_rec = sum((self.skill_path / d).is_dir() for d in recommended)
        structure = ((present_req / len(required)) * 0.6 +
                     (present_rec / len(recommended)) * 0.4)

        assets = list((self.skill_path / "assets").rglob("*")) \
            if (self.skill_path / "assets").is_dir() else []
        assets_n = len([a for a in assets if a.is_file()])
        expected = list((self.skill_path / "expected_outputs").glob("*")) \
            if (self.skill_path / "expected_outputs").is_dir() else []
        tests = list((self.skill_path / "tests").glob("*.py")) \
            if (self.skill_path / "tests").is_dir() else []

        asset_score = min(assets_n / 3, 1.0) * 100
        exp_score = min(len(expected) / 2, 1.0) * 100
        test_score = min(len(tests) / 1, 1.0) * 100

        if assets_n == 0:
            notes.append("assets/ empty - add sample data")
        if not expected:
            notes.append("expected_outputs/ empty - add golden outputs")
        if not tests:
            notes.append("No automated tests under tests/")

        score = structure * 100 * 0.25 + asset_score * 0.25 + \
            exp_score * 0.25 + test_score * 0.25
        return float(round(score)), notes

    def score_usability(self) -> Tuple[float, List[str]]:
        notes: List[str] = []
        scripts = self._scripts()
        help_scripts = 0
        argparse_scripts = 0
        for script in scripts:
            source = script.read_text(encoding="utf-8", errors="replace")
            argparse_scripts += int(("argparse" in source) or ("click" in source))
            help_scripts += int("help=" in source or "--help" in source)

        n = max(len(scripts), 1)
        cli_score = (argparse_scripts / n) * 70 + (help_scripts / n) * 30
        skill_md = self._read("SKILL.md")
        quickstart = int(bool(re.search(r"quick\s*start|\busage\b", skill_md, re.IGNORECASE)))
        examples = skill_md.count("```") // 2
        qs_score = min(quickstart + examples / 3, 1.0) * 100

        if quickstart == 0:
            notes.append("No Quick Start / Usage section found")
        if examples < 2:
            notes.append("Fewer than 2 runnable examples documented")

        score = cli_score * 0.5 + qs_score * 0.5
        return float(round(score)), notes

    def score_security(self) -> Tuple[float, List[str], Dict[str, Any]]:
        scorer = SecurityScorer(self._scripts())
        raw = scorer.get_overall_score()
        # SecurityScorer works on a 0-25 component scale; map it to percent.
        pct = round(raw["overall_score"] / MAX_COMPONENT_SCORE * 100, 1)
        findings = [f"[security] {f}" for f in raw["findings"]]
        suggestions = [f"[security] {s}" for s in raw["suggestions"]]
        return float(round(pct)), findings + suggestions, raw

    # ------------------------------------------------------------ entry

    def recommend_tier(self) -> str:
        skill_md = self._read("SKILL.md")
        lines = skill_md.count("\n") + 1 if skill_md else 0
        scripts = self._scripts()
        loc = sum(p.read_text(encoding="utf-8", errors="replace").count("\n") + 1
                  for p in scripts) if scripts else 0
        if lines >= TIER_SKILL_MD_MIN_LINES["POWERFUL"] and loc >= TIER_SCRIPTS_LOC["STANDARD"][0]:
            return "POWERFUL"
        if lines >= TIER_SKILL_MD_MIN_LINES["STANDARD"]:
            return "STANDARD"
        return "BASIC"

    def build_roadmap(self, per_dimension_notes: Dict[str, List[str]],
                      dimensions: Dict[str, float]) -> List[str]:
        roadmap: List[str] = []
        for name, score in sorted(dimensions.items(), key=lambda kv: kv[1]):
            for note in per_dimension_notes.get(name, [])[:3]:
                roadmap.append(f"[{name} ({score:.0f})] {note}")
        return roadmap[:8]

    def score(self) -> Dict[str, Any]:
        doc, doc_notes = self.score_documentation()
        code, code_notes = self.score_code_quality()
        comp, comp_notes = self.score_completeness()
        use, use_notes = self.score_usability()

        dimensions = {
            "Documentation": doc,
            "Code Quality": code,
            "Completeness": comp,
            "Usability": use,
        }
        weights = {name: 0.25 for name in dimensions}
        notes = {"Documentation": doc_notes, "Code Quality": code_notes,
                 "Completeness": comp_notes, "Usability": use_notes}
        security_raw: Dict[str, Any] = {}

        if self.include_security:
            sec, sec_notes, security_raw = self.score_security()
            dimensions["Security"] = sec
            weights = {name: 0.20 for name in dimensions}
            notes["Security"] = sec_notes

        overall = round(sum(dimensions[name] * weights[name] for name in dimensions), 1)
        result = {
            "skill_path": str(self.skill_path).replace("\\\\", "/"),
            "overall_score": overall,
            "letter_grade": assign_letter_grade(overall),
            "tier_recommendation": self.recommend_tier(),
            "dimensions": [
                {"name": name, "score": dimensions[name], "weight": weights[name]}
                for name in dimensions
            ],
            "improvement_roadmap": self.build_roadmap(notes, dimensions),
        }
        if security_raw:
            result["security_detail"] = {
                "has_critical_vulnerabilities":
                    security_raw.get("has_critical_vulnerabilities", False),
                "findings": security_raw.get("findings", []),
            }
        return result


def print_report(result: Dict[str, Any], detailed: bool = False) -> None:
    print("=== QUALITY SCORER ===")
    print(f"Skill: {result['skill_path']}")
    print(f"Overall Score: {result['overall_score']}/100 ({result['letter_grade']})")
    print(f"Tier Recommendation: {result['tier_recommendation']}")
    print()
    print("DIMENSIONS:")
    for dim in result["dimensions"]:
        print(f"  {dim['name']:<14} {dim['score']:>6.1f}  (weight {dim['weight']:.0%})")
    if detailed and result["improvement_roadmap"]:
        print("\nIMPROVEMENT ROADMAP:")
        for item in result["improvement_roadmap"]:
            print(f"  - {item}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Multi-dimensional quality scoring for skills."
    )
    parser.add_argument("skill_path",
                        help="Skill directory (or parent dir with --batch)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit machine-readable JSON")
    parser.add_argument("--detailed", action="store_true",
                        help="Include improvement roadmap in text output")
    parser.add_argument("--minimum-score", type=float, default=None, dest="minimum_score",
                        help="Exit non-zero when the score is below this threshold")
    parser.add_argument("--include-security", action="store_true",
                        dest="include_security",
                        help="Add the Security dimension (weights rebalance to 5 x 20%%)")
    parser.add_argument("--batch", action="store_true",
                        help="Score every child directory of skill_path")
    args = parser.parse_args(argv)

    root = Path(args.skill_path)
    if not root.exists():
        msg = f"error: path not found: {root}"
        print(json.dumps({"error": msg}) if args.as_json else msg, file=sys.stderr)
        return 1

    targets = ([p for p in sorted(root.iterdir()) if p.is_dir()]
               if args.batch else [root])
    results = [QualityScorer(t, include_security=args.include_security).score()
               for t in targets]

    if args.as_json:
        payload = results[0] if len(results) == 1 else {"skills": results}
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            print_report(r, detailed=args.detailed)
            print()

    if args.minimum_score is None:
        return 0

    lowest = min(r["overall_score"] for r in results)
    if lowest >= args.minimum_score:
        return 0
    if lowest >= args.minimum_score - 10:
        return 2  # needs improvement
    return 1      # failed


if __name__ == "__main__":
    sys.exit(main())
