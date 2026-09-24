#!/usr/bin/env python3
"""Main pipeline -- the full three-tier waterfall intent-recognition flow."""
import json
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(__file__))

from l1_matcher import match, match_all
from llm_client import call_l2, call_l3
from plan_renderer import render_markdown, render_json


def detect_project_root() -> str:
    """Detect the project root directory"""
    for dir in [".", "..", "../.."]:
        for f in ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "requirements.txt"]:
            if os.path.exists(os.path.join(dir, f)):
                return os.path.abspath(dir)
    return os.getcwd()


def detect_tech_stack(root: str) -> str:
    """Detect the tech stack"""
    stacks = []
    if os.path.exists(os.path.join(root, "package.json")):
        stacks.append("javascript/typescript")
    if os.path.exists(os.path.join(root, "pyproject.toml")) or os.path.exists(os.path.join(root, "requirements.txt")):
        stacks.append("python")
    if os.path.exists(os.path.join(root, "go.mod")):
        stacks.append("go")
    if os.path.exists(os.path.join(root, "Cargo.toml")):
        stacks.append("rust")
    return ", ".join(stacks) if stacks else "unknown"


def normalize_input(raw_input: str, last_intent: Optional[Dict[str, Any]] = None) -> str:
    """Input normalization (simplified: coreference resolution + ellipsis completion + term standardization)."""
    text = raw_input.strip()

    # coreference resolution
    if last_intent and last_intent.get("slots"):
        for pronoun in ["it", "this", "that", "the previous one", "just now"]:
            if pronoun in text:
                target = last_intent["slots"].get("target", "")
                if target:
                    text = text.replace(pronoun, target)

    # ellipsis completion
    if text in ["write for me", "do for me", "implement it"]:
        text = text + " code"

    # term standardization
    term_map = {
        "backend": "backend", "server": "backend", "API": "backend", "api": "backend",
        "frontend": "frontend", "client": "frontend", "UI": "frontend",
        "database": "database", "DB": "database", "persistence": "database",
    }
    for src, dst in term_map.items():
        text = text.replace(src, dst)

    return text


def _session_path(session_id: str) -> str:
    """Canonical location of the session file.

    Must stay in sync with session_manager.SESSION_DIR (~/.code_intent_planner/sessions).
    Early versions wrote directly to f"_session_{session_id}.json", i.e. into the caller's
    current working directory -- once a user dropped the skill into a project and ran it, the
    project root was littered with a pile of _session_*.json junk files.
    Can be overridden with SKILLKIT_SESSION_DIR (for testing); otherwise use a fixed location
    under the user's home directory.
    """
    base = os.environ.get("SKILLKIT_SESSION_DIR")
    if base:
        d = base
    else:
        d = os.path.join(os.path.expanduser("~"), ".code_intent_planner", "sessions")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"_session_{session_id}.json")


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load the session state"""
    path = _session_path(session_id)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_session(session_id: str, state: Dict[str, Any]):
    """Save the session state"""
    path = _session_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_clarification_questions(l2_result: Dict[str, Any], missing_slots: list) -> list:
    """Generate clarification questions"""
    slot_questions = {
        "target": "Which module or file needs to be operated on? (e.g. auth, user-service, payment)",
        "scope": "What is the change scope? (new feature development / existing feature change / code refactor / pure config change)",
        "tech_stack": "What is the target tech stack? (e.g. python/fastapi, node/express, go/gin)",
        "deadline": "What is the deadline? (today / this week / this month / not urgent)",
    }
    questions = []
    for slot in missing_slots[:3]:
        if slot in slot_questions:
            questions.append(f"① {slot_questions[slot]}")
    return questions


def run_pipeline(
    raw_input: str,
    session_id: Optional[str] = None,
    project_root: Optional[str] = None,
    skip_normalization: bool = False,
    use_mock: bool = True,
) -> Dict[str, Any]:
    """Run the full pipeline"""

    # initialize
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not project_root:
        project_root = detect_project_root()
    
    tech_stack = detect_tech_stack(project_root)
    session = load_session(session_id)
    last_intent = session.get("last_intent") if session else None
    
    # step 0: cache check
    if session:
        cache_key = f"{session_id}:{last_intent.get('intent_type', '')}:{hash(raw_input[:100])}"
        if cache_key in session.get("cache", {}):
            print(f"[Cache Hit] returning cached result", file=sys.stderr)
            return session["cache"][cache_key]

    # step 1: input normalization
    normalized = raw_input if skip_normalization else normalize_input(raw_input, last_intent)

    # step 2: L1 rule layer
    l1_result = match(normalized)

    # initialize variables
    intent_type = None
    confidence = 0.0
    source_layer = "L1"
    l2_result = {}
    l3_result = {}
    subtype = None

    # three-tier waterfall
    if l1_result["matched"] and l1_result["confidence"] >= 0.85:
        # L1 direct hit
        intent_type = l1_result["intent_type"]
        confidence = l1_result["confidence"]
        source_layer = "L1"
        subtype = l1_result.get("subtype")
        l2_result = {"slots": {}, "description": normalized}
    else:
        # L1 miss, go to L2
        if use_mock:
            os.environ["USE_MOCK_LLM"] = "true"

        l2_result = call_l2(normalized, tech_stack)

        if "error" in l2_result:
            return {"error": f"L2 failed: {l2_result['error']}", "session_id": session_id}

        confidence = l2_result.get("confidence", 0)
        intent_type = l2_result.get("intent_type")
        source_layer = "L2"

        if confidence >= 0.85:
            pass  # L2 accepted directly
        elif confidence >= 0.60:
            # clarification protocol
            missing = [k for k, v in l2_result.get("slots", {}).items() if not v]
            questions = get_clarification_questions(l2_result, missing)
            return {
                "status": "clarification_needed",
                "questions": get_clarification_questions(l2_result, missing),
                "partial_intent": l2_result,
                "session_id": session_id,
            }
        else:
            # confidence < 0.60, go to L3
            l3_result = call_l3(
                raw_input=raw_input,
                normalized_text=normalized,
                tech_stack=tech_stack,
                project_snippet="",
                intent_type=l2_result.get("intent_type", "implement"),
                slots=l2_result.get("slots", {}),
                last_intent=last_intent
            )

            if "error" in l3_result:
                return {"error": f"L3 failed: {l3_result['error']}", "session_id": session_id}

            # merge L3 results
            intent_type = l3_result.get("intent_type")
            confidence = l3_result.get("confidence", 0)
            source_layer = "L3"
            l2_result.update(l3_result)

    # slot merging and evidence grading
    slots = l2_result.get("slots", {})
    if source_layer == "L1":
        # L1 direct hit, no slot info
        slots = {"target": "", "scope": "", "tech_stack": detect_tech_stack(detect_project_root())}
    
    slot_list = []
    for name, value in slots.items():
        if not value:
            continue
        evidence = "provisional"
        if name in ["target", "tech_stack"] and value:
            evidence = "verified" if any(k in raw_input.lower() for k in [value.lower()]) else "provisional"
        slot_list.append({"name": name, "value": value, "evidence": evidence})
    
    # solution recommendation (L1/L2 simple cases use a template; L3 already includes one)
    solution = l2_result.get("solution", "")
    if source_layer == "L1" and not solution:
        solution = get_default_solution(intent_type)

    # assumptions
    assumptions = l2_result.get("assumptions", [])
    if source_layer == "L1" and not assumptions:
        assumptions = []

    # sub-tasks
    sub_tasks = l2_result.get("sub_tasks", [])
    critical_path = l2_result.get("critical_path", [])
    parallel_groups = l2_result.get("parallel_groups", [])

    # constraints
    constraints = l2_result.get("constraints", {"hard": [], "soft": []})

    # build the final result
    result = {
        "intent_type": intent_type,
        "subtype": subtype,
        "confidence": confidence,
        "source_layer": source_layer,
        "description": l2_result.get("description", normalized) if source_layer != "L1" else normalized,
        "slots": slot_list,
        "constraints": constraints if source_layer != "L1" else {"hard": [], "soft": []},
        "sub_tasks": sub_tasks,
        "critical_path": critical_path,
        "parallel_groups": parallel_groups,
        "solution": solution,
        "assumptions": assumptions,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
    }
    
    # update the session
    new_session = {
        "session_id": session_id,
        "turn": (session.get("turn", 0) + 1) if session else 1,
        "last_intent": {
            "type": intent_type,
            "slots": {s["name"]: s["value"] for s in slot_list}
        },
        "slots_history": (session.get("slots_history", []) + [slot_list]) if session else [slot_list],
        "cache": session.get("cache", {}) if session else {},
    }
    # update the cache
    cache_key = f"{session_id}:{intent_type}:{hash(normalized[:100])}"
    new_session["cache"][cache_key] = result
    save_session(session_id, new_session)
    
    return result


def get_default_solution(intent_type: str) -> str:
    """Default solution for an L1 direct hit."""
    solutions = {
        "implement": "design the schema first, then implement model/service, and finally add the API",
        "fix": "reproduce -> locate -> fix -> regression test",
        "refactor": "analyze impact -> write characterization tests -> refactor in small steps -> verify",
        "review": "scan for security/performance/readability -> generate a report",
        "test": "analyze coverage -> add tests -> verify",
        "optimize": "establish a baseline -> profile -> optimize -> regression test",
        "plan": "clarify requirements -> design the approach -> decompose tasks",
        "design": "clarify requirements -> draft the approach -> justify technology choices -> review",
        "migrate": "compatibility analysis -> plan -> pilot -> full rollout",
        "destructive": "risk assessment -> backup -> confirm -> execute -> verify",
        "test": "analyze coverage -> add tests -> verify",
    }
    return solutions.get(intent_type, "follow the standard development process")


def main():
    parser = argparse.ArgumentParser(description="Code Intent Planner -- three-tier waterfall intent recognition")
    parser.add_argument("input", nargs="?", help="user input (natural language)")
    parser.add_argument("--session", "-s", help="Session ID")
    parser.add_argument("--project", "-p", help="project root directory")
    parser.add_argument("--skip-normalization", action="store_true")
    parser.add_argument("--no-mock", action="store_true", help="use a real LLM (requires environment variables configured)")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", help="output file path")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    result = run_pipeline(
        raw_input=args.input,
        session_id=args.session,
        project_root=args.project,
        skip_normalization=args.skip_normalization,
        use_mock=not args.no_mock,
    )
    
    if args.format == "markdown":
        output = render_markdown(result)
    else:
        output = render_json(result)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)

    # on L2/L3 failure, propagate the failure status to the caller rather than treating failure as success
    return 1 if isinstance(result, dict) and "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())