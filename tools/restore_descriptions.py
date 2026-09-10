#!/usr/bin/env python3
"""Restore original SKILL.md descriptions from git history.

For each SKILL.md modified in HEAD~1, extract the original description
and replace the generic template description that was applied by the
batch update script.
"""
import subprocess
import re
from pathlib import Path

REPO = Path(__file__).parent.parent
SKILLS_DIR = REPO / "skills" / "programming"


def get_changed_files():
    """Get list of SKILL.md files changed in HEAD~1."""
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--name-only"],
        capture_output=True, text=True, cwd=REPO
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith("SKILL.md")]


def get_original_description(filepath):
    """Extract original description from git HEAD~1 version."""
    result = subprocess.run(
        ["git", "show", f"HEAD~1:{filepath}"],
        capture_output=True, text=True, cwd=REPO
    )
    if result.returncode != 0:
        return None
    
    content = result.stdout
    # Extract the description field from YAML frontmatter
    match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE | re.DOTALL)
    if match:
        desc = match.group(1).strip()
        # Clean up quotes
        desc = desc.strip('"').strip("'")
        return desc
    return None


def get_current_content(filepath):
    """Read current SKILL.md content."""
    full_path = REPO / filepath
    return full_path.read_text(encoding="utf-8")


def replace_description(content, new_description):
    """Replace the generic description with the real one."""
    # Match the description block including the > continuation
    pattern = r'description:\s*>\s*\n\s*Use when the user asks to related tasks for.*?\n'
    replacement = f'description: "{new_description}"\n'
    return re.sub(pattern, replacement, content)


def main():
    files = get_changed_files()
    print(f"Found {len(files)} SKILL.md files to restore")
    
    restored = 0
    skipped = 0
    failed = 0
    
    for filepath in files:
        original_desc = get_original_description(filepath)
        if not original_desc:
            print(f"  SKIP (no original desc): {filepath}")
            skipped += 1
            continue
        
        current = get_current_content(filepath)
        if "Use when the user asks to related tasks" not in current:
            print(f"  SKIP (not generic): {filepath}")
            skipped += 1
            continue
        
        new_content = replace_description(current, original_desc)
        full_path = REPO / filepath
        full_path.write_text(new_content, encoding="utf-8")
        print(f"  RESTORED: {filepath}")
        print(f"    -> {original_desc[:80]}...")
        restored += 1
    
    print(f"\nSummary: {restored} restored, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
