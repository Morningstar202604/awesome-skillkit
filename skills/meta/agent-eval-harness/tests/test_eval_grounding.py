import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import eval_harness as eh  # noqa: E402


def _renormalized(weights, dims):
    judged = {k: v for k, v in dims.items() if v is not None}
    total_w = sum(weights[k] for k in judged)
    return round(sum(weights[k] * judged[k] for k in judged) / total_w * 100, 1)


def test_missing_evidence_must_not_get_full_grounding():
    case = {"prompt": "p", "response": "a plausible answer", "expects": {}}
    r = eh.score_case(case, dict(eh.DEFAULT_WEIGHTS), list(eh.FORBIDDEN_DEFAULT))
    assert r["dimensions"]["grounding"] is None, r
    assert "grounding" in r["skipped_dimensions"], r
    assert r["score"] == pytest.approx(
        _renormalized(eh.DEFAULT_WEIGHTS, r["dimensions"]), abs=0.11
    )
    assert r["verdict"] == "pass", r


def test_declared_evidence_still_scores_grounding():
    case = {
        "prompt": "p",
        "response": "the answer relies on fact-a and more",
        "expects": {"evidence": ["fact-a"]},
    }
    r = eh.score_case(case, dict(eh.DEFAULT_WEIGHTS), list(eh.FORBIDDEN_DEFAULT))
    assert isinstance(r["dimensions"]["grounding"], float)
    assert r["dimensions"]["grounding"] > 0.5
    assert "grounding" not in r["skipped_dimensions"], r
    expected = round(
        sum(eh.DEFAULT_WEIGHTS[k] * v for k, v in r["dimensions"].items()), 1
    )
    assert r["score"] == pytest.approx(expected, abs=0.11)
