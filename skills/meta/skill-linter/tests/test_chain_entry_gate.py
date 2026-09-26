"""RED: every chain domain MUST declare an entry that resolves inside that domain's skills."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_spec = importlib.util.spec_from_file_location(
    "validate_skills", ROOT / "tools" / "validate_skills.py"
)
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)


def make_domain_doc(tmp_path, entry):
    doc = {
        "domains": {
            "demo": {
                "entry": entry,
                "skills": ["foo", "bar"],
                "chains": {"c1": ["foo", "bar"]},
            }
        }
    }
    p = tmp_path / "skill_chains.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def entry_errors(tmp_path, entry):
    make_domain_doc(tmp_path, entry)
    vs.SKILLS_DIR = tmp_path
    vs.issues_global = []
    vs.check_chain_consistency({"foo", "bar"})
    return [i.msg for i in vs.issues_global if "entry" in i.msg]


def test_missing_entry_is_error(tmp_path):
    errs = entry_errors(tmp_path, None)
    assert any("missing entry" in e for e in errs), errs


def test_ghost_entry_is_error(tmp_path):
    errs = entry_errors(tmp_path, "ghost-skill")
    assert any("ghost-skill" in e for e in errs), errs


def test_entry_in_domain_skills_is_clean(tmp_path):
    errs = entry_errors(tmp_path, "foo")
    assert errs == [], errs


def test_path_form_entry_resolves_by_basename(tmp_path):
    errs = entry_errors(tmp_path, "skills/tools/foo")
    assert errs == [], errs


def test_valid_bare_entry_clean(tmp_path):
    errs = entry_errors(tmp_path, "bar")
    assert errs == [], errs
