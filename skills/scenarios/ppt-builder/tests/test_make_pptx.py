import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import make_pptx  # noqa: E402

VALID_SPEC = {
    "deck_title": "Test Deck",
    "slides": [
        {"title": "One claim", "bullets": ["a", "b"], "notes": "say this"},
    ],
}


class ValidateSpecTests(unittest.TestCase):
    def test_valid_spec_passes(self):
        self.assertEqual(make_pptx.validate_spec(VALID_SPEC), [])

    def test_missing_deck_title(self):
        bad = {"slides": VALID_SPEC["slides"]}
        errs = make_pptx.validate_spec(bad)
        self.assertTrue(any("deck_title" in e for e in errs))

    def test_empty_slides_rejected(self):
        errs = make_pptx.validate_spec({"deck_title": "x", "slides": []})
        self.assertTrue(any("non-empty array" in e for e in errs))

    def test_too_many_bullets_flagged(self):
        spec = {
            "deck_title": "d",
            "slides": [{"title": "t", "bullets": [f"b{i}" for i in range(6)]}],
        }
        errs = make_pptx.validate_spec(spec)
        self.assertTrue(any("exceeds max 5" in e for e in errs))

    def test_blank_bullet_flagged(self):
        spec = {
            "deck_title": "d",
            "slides": [{"title": "t", "bullets": ["ok", "   "]}],
        }
        errs = make_pptx.validate_spec(spec)
        self.assertTrue(any("non-empty string" in e for e in errs))


class ScriptCliTests(unittest.TestCase):
    def test_cli_rejects_bad_spec_exit2(self):
        bad = Path(__file__).parent / "_bad_spec.json"
        bad.write_text(json.dumps({"slides": []}), encoding="utf-8")
        try:
            rc = subprocess.call(
                [sys.executable, str(SCRIPTS / "make_pptx.py"), str(bad), "out.pptx"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        finally:
            bad.unlink(missing_ok=True)
        self.assertEqual(rc, 2)

    def test_cli_reports_missing_pptx_as_exit3(self):
        """If python-pptx absent, render must exit 3 (not crash)."""
        has_pptx = (
            subprocess.call(
                [sys.executable, "-c", "import pptx"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            == 0
        )
        if has_pptx:
            self.skipTest("python-pptx installed; exit-3 path unreachable")
        good = Path(__file__).parent / "_good_spec.json"
        good.write_text(json.dumps(VALID_SPEC), encoding="utf-8")
        try:
            rc = subprocess.call(
                [sys.executable, str(SCRIPTS / "make_pptx.py"), str(good), "out.pptx"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        finally:
            good.unlink(missing_ok=True)
        self.assertEqual(rc, 3)


if __name__ == "__main__":
    unittest.main()
