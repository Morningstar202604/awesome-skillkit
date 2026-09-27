r"""Strong smoke test for journal-adapt (SOTA: column-aware page model + venue rules).

真输入 + 真断言：验证分栏页数模型、参考文献页扣减、摘要上限、必填章节、双盲、禁词、别名。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "journal_adapt.py"
spec = importlib.util.spec_from_file_location("journal_adapt", SCRIPT)
ja = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ja)


def _paper(body_words=5400, abstract_words=150, sections=("Introduction", "Method",
                                                          "Experiments", "Limitations",
                                                          "Conclusion"), bibitems=0,
           extra=""):
    s = "\\begin{abstract}" + " ".join(["word"] * abstract_words) + "\\end{abstract}\n"
    s += "".join(f"\\section{{{x}}}" for x in sections) + "\n"
    s += " ".join(["w"] * body_words) + "\n" + extra
    if bibitems:
        s += ("\\begin{thebibliography}{99}\n"
              + "\n".join(f"\\bibitem{{k{i}}}" for i in range(bibitems))
              + "\n\\end{thebibliography}\n")
    return s


def test_neurips_refs_excluded_from_page_limit():
    """NeurIPS 参考文献不计入 9 页 → billable < total，且 ref_pages 被算出。"""
    r = ja.adapt(_paper(bibitems=90), "neurips")
    assert r["refs_included"] is False
    assert r["ref_pages"] == 2, r
    assert r["est_billable_pages"] < r["est_pages"], r
    assert r["abstract_words"] == 150 and r["abstract_limit"] == 200


def test_ieee_refs_included():
    r = ja.adapt(_paper(bibitems=45), "ieee_conf")
    assert r["refs_included"] is True
    assert r["est_billable_pages"] == r["est_pages"], r


def test_column_aware_words_per_page():
    """1 栏（NeurIPS 600 词/页）与 2 栏（IEEE 950 词/页）对同一正文给出不同页数。"""
    body = _paper(body_words=5700)
    n = ja.adapt(body, "neurips")
    i = ja.adapt(body, "ieee_conf")
    assert n["est_pages"] > i["est_pages"], (n["est_pages"], i["est_pages"])
    assert ja.JOURNAL_SPECS["neurips"]["words_per_page"] == 600
    assert ja.JOURNAL_SPECS["ieee_conf"]["words_per_page"] == 950


def test_abstract_missing_and_too_long():
    r = ja.adapt("\\section{Introduction} no abstract here", "ieee_conf")
    assert any(i["type"] == "missing_abstract" for i in r["issues"]), r["issues"]
    r2 = ja.adapt(_paper(abstract_words=260), "ieee_conf")
    assert any(i["type"] == "abstract_too_long" for i in r2["issues"]), r2["issues"]


def test_required_sections_includes_neurips_limitations():
    r = ja.adapt(_paper(sections=("Introduction", "Method", "Experiments", "Conclusion")),
                 "neurips")
    missing = [i["section"] for i in r["issues"] if i["type"] == "missing_section"]
    assert "Limitations" in missing, r["issues"]


def test_double_blind_anonymity_flag():
    r = ja.adapt(_paper(extra="\\author{Jane Doe, MIT}"), "acm")
    assert r["anonymous_ok"] is False
    assert any(i["type"] == "anonymity" for i in r["issues"]), r["issues"]
    # 匿名写法不应触发
    r2 = ja.adapt(_paper(extra="\\author{Anonymous Submission}"), "acm")
    assert r2["anonymous_ok"] is True, r2["issues"]


def test_banned_phrases_nature():
    r = ja.adapt(_paper(sections=("Introduction", "Results", "Discussion", "Methods"),
                        extra="In this paper we propose a Novel method."), "nature")
    phrases = [i.get("phrase") for i in r["issues"] if i["type"] == "banned"]
    assert phrases, r["issues"]


def test_ref_style_mismatch_detected():
    r = ja.adapt(_paper(extra="\\citep{x}"), "ieee_conf")
    assert any(i["type"] == "ref_style" for i in r["issues"]), r["issues"]
    assert r["ref_style_detected"] == "author-year"


def test_alias_and_template_year():
    r = ja.adapt(_paper(), "nips")
    assert r["target"] == "NeurIPS"
    r2 = ja.adapt(_paper(), "neurips", template_year="2026")
    assert r2["class"] == "neurips_2026", r2["class"]


def test_clean_paper_passes():
    r = ja.adapt(_paper(body_words=4800), "neurips")   # 4800+150 词 / 600 wpp ≈ 8.3p < 9
    assert r["status"] == "pass", r["issues"]
    assert r["score"] == 100


def test_cli_missing_file_rc1():
    r = subprocess.run([sys.executable, str(SCRIPT), "--input", "/no/such.tex"],
                       capture_output=True, text=True, timeout=60, check=False)
    assert r.returncode == 1
    assert json.loads(r.stdout)["status"] == "error"


def test_cli_end_to_end_output():
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d, "d.tex")
        fp.write_text(_paper(), encoding="utf-8")
        outp = Path(d, "r.json")
        r = subprocess.run([sys.executable, str(SCRIPT), "--input", str(fp),
                            "--target", "acl", "--output", str(outp)],
                           capture_output=True, text=True, timeout=60, check=False)
        assert r.returncode == 0, r.stderr
        o = json.loads(outp.read_text(encoding="utf-8"))
        assert o["method"] == "column-aware-estimate"
        assert "notes" in o and o["columns"] == 2
