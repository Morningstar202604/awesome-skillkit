#!/usr/bin/env python3
"""批量更新 skill 到 v3 标准

用法:
  python update_skills.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


# v3 标准 frontmatter
V3_FRONTMATTER_TEMPLATE = """---
name: {name}
description: >
  {description}
license: Apache-2.0
compatibility: {compatibility}
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: {category}
  pattern: {pattern}
  tier: {tier}
  verified-date: "{verified_date}"
---
"""


def detect_category(skill_dir: Path) -> str:
    """根据目录结构检测品类"""
    parts = skill_dir.parts
    for i, part in enumerate(parts):
        if part == "programming":
            if i + 1 < len(parts):
                return parts[i + 1]
    return "programming"


def detect_pattern(skill_dir: Path, skill_name: str) -> str:
    """根据 skill 名称检测模式"""
    patterns = {
        "planner": "intent-planner",
        "generator": "code-generator",
        "search": "web-search",
        "reviewer": "code-reviewer",
        "guide": "workflow",
        "builder": "pipeline-builder",
        "architect": "architecture",
        "manager": "workflow",
    }
    
    for keyword, pattern in patterns.items():
        if keyword in skill_name:
            return pattern
    
    return "single-task"


def detect_tier(skill_dir: Path, skill_name: str) -> str:
    """根据 skill 复杂程度检测 tier"""
    has_script = (skill_dir / "scripts").exists()
    has_test = any(skill_dir.glob("test*.py")) or (skill_dir / "tests").exists()
    has_ref = (skill_dir / "references").exists()
    
    if has_script and has_test and has_ref:
        return "expert"
    elif has_script:
        return "powerful"
    return "basics"


def detect_compatibility(skill_dir: Path, skill_name: str) -> str:
    """检测兼容性要求"""
    compat_parts = []
    
    # 检查脚本依赖
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for py_file in scripts_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "requests" in content or "httpx" in content:
                compat_parts.append("network access")
            if "playwright" in content:
                compat_parts.append("Playwright")
            if "docker" in content.lower():
                compat_parts.append("docker")
    
    if not compat_parts:
        return "Pure prompt-based; may read project structure via Bash."
    
    return f"Requires {' and '.join(compat_parts)}. No API keys required."


def update_skill_frontmatter(skill_dir: Path) -> bool:
    """更新单个 skill 的 frontmatter"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False
    
    content = skill_md.read_text(encoding="utf-8")
    
    # 提取当前信息
    name_match = re.search(r"name:\s*(.+)", content)
    desc_match = re.search(r"description:\s*(.+?)(?=\n\w|$)", content, re.DOTALL)
    
    skill_name = skill_dir.name
    
    # 构建新的 frontmatter
    new_frontmatter = V3_FRONTMATTER_TEMPLATE.format(
        name=skill_name,
        description=f"Use when the user asks to related tasks for {skill_name}. Do NOT use for unrelated tasks.",
        compatibility=detect_compatibility(skill_dir, skill_name),
        category=detect_category(skill_dir),
        pattern=detect_pattern(skill_dir, skill_name),
        tier=detect_tier(skill_dir, skill_name),
        verified_date="2026-09-09",
    )
    
    # 替换 frontmatter
    if content.startswith("---"):
        end_marker = content.find("---", 3)
        if end_marker > 0:
            new_content = new_frontmatter + "\n" + content[end_marker + 3:].lstrip()
            skill_md.write_text(new_content, encoding="utf-8")
            return True
    
    return False


def ensure_directory_structure(skill_dir: Path):
    """确保目录结构存在"""
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    
    # 创建 .gitignore
    gitignore = skill_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "_session_*.json\n"
            "_search_cache_*.json\n"
            "__pycache__/\n"
            "*.pyc\n",
            encoding="utf-8"
        )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="批量更新 skills 到 v3 标准")
    parser.add_argument("--root", "-r", default=".", help="根目录")
    parser.add_argument("--dry-run", action="store_true", help="只打印不修改")
    args = parser.parse_args()
    
    root = Path(args.root)
    programming_dir = root / "skills" / "programming"
    
    if not programming_dir.exists():
        print(f"Error: {programming_dir} not found")
        sys.exit(1)
    
    updated = []
    skipped = []
    
    for skill_dir in sorted(programming_dir.rglob("SKILL.md")):
        skill_dir = skill_dir.parent
        if skill_dir.name == "sample-skill":
            continue
        
        print(f"Processing: {skill_dir.name}")
        
        # 确保目录结构
        ensure_directory_structure(skill_dir)
        
        # 更新 frontmatter
        if args.dry_run:
            print(f"  [dry-run] Would update frontmatter")
        else:
            if update_skill_frontmatter(skill_dir):
                updated.append(skill_dir.name)
                print(f"  ✓ Updated")
            else:
                skipped.append(skill_dir.name)
                print(f"  - Skipped")
    
    print(f"\nDone! Updated: {len(updated)}, Skipped: {len(skipped)}")
    if updated:
        print(f"Updated: {', '.join(updated)}")


if __name__ == "__main__":
    main()
