#!/usr/bin/env python3
"""project_analyzer.py — project context analyzer

Reads the project structure, tech stack, and code style to provide context for code_generator.
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


# tech-stack marker files
TECH_MARKERS: Dict[str, List[str]] = {
    "python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
    "javascript": ["package.json"],
    "typescript": ["tsconfig.json", "package.json"],
    "go": ["go.mod"],
    "rust": ["Cargo.toml"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "node_express": ["package.json"],
    "python_fastapi": ["pyproject.toml", "requirements.txt"],
    "python_django": ["manage.py", "requirements.txt"],
    "python_flask": ["requirements.txt"],
}


def detect_project_root(start_dir: str = ".") -> str:
    """Detect the project root directory"""
    for dir in [start_dir, "..", "../..", "../../.."]:
        abs_dir = os.path.abspath(dir)
        for marker in ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "pom.xml", "manage.py"]:
            if os.path.exists(os.path.join(abs_dir, marker)):
                return abs_dir
    return os.getcwd()


def detect_tech_stack(project_root: str) -> Dict[str, Any]:
    """Detect the tech stack"""
    stacks = {}
    root = Path(project_root)
    
    # check framework markers
    framework_markers = {
        "fastapi": ["main.py", "app.py"],
        "django": ["manage.py", "wsgi.py"],
        "flask": ["app.py", "flask_app.py"],
    }
    
    for framework, markers in framework_markers.items():
        if any((root / m).exists() for m in markers):
            stacks[f"python_{framework}"] = True
    
    # check package.json dependencies
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            with open(pkg_json, encoding="utf-8") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "express" in deps:
                stacks["node_express"] = True
            if "next" in deps:
                stacks["nextjs"] = True
            if "react" in deps:
                stacks["react"] = True
            if "vue" in deps:
                stacks["vue"] = True
        except json.JSONDecodeError:
            pass
    
    # check requirements.txt dependencies
    req_txt = root / "requirements.txt"
    if req_txt.exists():
        content = req_txt.read_text(encoding="utf-8").lower()
        if "fastapi" in content:
            stacks["python_fastapi"] = True
        if "django" in content:
            stacks["python_django"] = True
        if "flask" in content:
            stacks["python_flask"] = True
    
    # check go.mod
    go_mod = root / "go.mod"
    if go_mod.exists():
        content = go_mod.read_text(encoding="utf-8")
        if "gin-gonic" in content or "gin" in content:
            stacks["go_gin"] = True
        elif "fiber" in content:
            stacks["go_fiber"] = True
    
    stacks["primary"] = _detect_primary(stacks)
    return stacks


def _detect_primary(stacks: Dict[str, Any]) -> str:
    """Detect the primary tech stack"""
    if stacks.get("python_fastapi"):
        return "python/fastapi"
    if stacks.get("python_django"):
        return "python/django"
    if stacks.get("python_flask"):
        return "python/flask"
    if stacks.get("node_express"):
        return "node/express"
    if stacks.get("nextjs"):
        return "node/nextjs"
    if stacks.get("react"):
        return "node/react"
    if stacks.get("vue"):
        return "node/vue"
    if stacks.get("go_gin"):
        return "go/gin"
    if stacks.get("go_fiber"):
        return "go/fiber"
    return "unknown"


def get_directory_structure(root: str, max_depth: int = 3) -> List[str]:
    """Get the directory structure (first max_depth levels)"""
    structure = []
    root_path = Path(root)
    
    for path in root_path.rglob("*"):
        if path.is_dir():
            rel = path.relative_to(root_path)
            depth = len(rel.parts)
            if depth <= max_depth:
                indent = "  " * (depth - 1)
                structure.append(f"{indent}{rel.name}/")
    
    return structure[:30]  # cap the number of entries


def get_code_style_samples(root: str, max_files: int = 3, max_lines: int = 50) -> List[str]:
    """Get code-style samples"""
    samples = []
    root_path = Path(root)
    
    # find representative files by language
    extensions = [".py", ".ts", ".js", ".go", ".rs"]
    excluded_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build"}
    
    for ext in extensions:
        if len(samples) >= max_files:
            break
        for path in root_path.rglob(f"*{ext}"):
            if any(excl in str(path) for excl in excluded_dirs):
                continue
            if path.is_file() and path.stat().st_size > 100:  # skip empty files
                try:
                    content = path.read_text(encoding="utf-8")
                    lines = content.split("\n")[:max_lines]
                    samples.append(f"### {path.relative_to(root_path)}\n```python\n" + "\n".join(lines) + "\n```")
                except (UnicodeDecodeError, OSError):
                    continue
    
    return samples


def get_existing_modules(root: str) -> List[str]:
    """Get the list of existing modules"""
    modules = []
    root_path = Path(root)
    
    # find subdirectories under src/ or lib/
    for dir_name in ["src", "lib", "app", "pkg"]:
        dir_path = root_path / dir_name
        if dir_path.exists():
            for child in dir_path.iterdir():
                if child.is_dir() and not child.name.startswith(("_", ".", "__")):
                    modules.append(child.name)
    
    # also find top-level modules
    for pattern in ["*.py", "*.ts", "*.js", "*.go"]:
        for path in root_path.glob(pattern):
            if path.is_file() and not path.name.startswith(("_", ".")):
                modules.append(path.stem)
    
    return list(set(modules))


def analyze_project(project_root: Optional[str] = None) -> Dict[str, Any]:
    """Full project analysis"""
    if not project_root:
        project_root = detect_project_root()
    
    return {
        "project_root": project_root,
        "tech_stack": detect_tech_stack(project_root),
        "directory_structure": get_directory_structure(project_root),
        "code_style_samples": get_code_style_samples(project_root),
        "existing_modules": get_existing_modules(project_root),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Project context analyzer")
    parser.add_argument("--root", "-r", help="Project root directory")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    result = analyze_project(args.root)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Project root: {result['project_root']}")
        print(f"Tech stack: {result['tech_stack']['primary']}")
        print(f"Frameworks: {list(result['tech_stack'].keys())}")
        print(f"Existing modules: {result['existing_modules']}")
        print(f"\nDirectory structure:")
        for line in result["directory_structure"]:
            print(line)
