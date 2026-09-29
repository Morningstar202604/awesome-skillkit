# Probe: are the "discipline blocks" in expert-teams member files byte-identical?
# Strategy: in each member agent file, find the span starting at the line that
# contains the marker phrase and ending right before the next '## ' heading or
# a '---' separator; hash it. If all hashes are identical, the block is safe to
# collapse into a single protocol reference.
import hashlib
import re
from pathlib import Path

MARKER = "实时监测"
root = Path("expert-teams/teams")

def extract_block(text: str):
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if MARKER in ln and ln.lstrip().startswith(("-", "###", "##")):
            start = i
            break
    if start is None:
        return None
    # walk back to include immediately preceding sibling lines of same list
    end = start
    for j in range(start, len(lines)):
        ln = lines[j]
        if j > start and (ln.startswith("## ") or ln.strip() == "---" or
                          (ln.startswith("# ") and not ln.startswith("###"))):
            end = j
            break
        end = j + 1
    return "\n".join(lines[start:end])

blocks = {}
for f in sorted(root.glob("*/agents/*.md")):
    if f.name.endswith("team-lead.md"):
        continue
    t = f.read_text(encoding="utf-8")
    b = extract_block(t)
    if b:
        blocks[str(f)] = b

hashes = {}
for f, b in blocks.items():
    hashes.setdefault(hashlib.sha256(b.encode("utf-8")).hexdigest()[:12], []).append(f)

print(f"member files with a {MARKER!r} block: {len(blocks)}")
print(f"distinct byte-identical variants: {len(hashes)}")
for h, fs in sorted(hashes.items(), key=lambda kv: -len(kv[1])):
    print(f"  {h}: {len(fs)} files")
    if len(fs) == len(blocks) or len(fs) > 30:
        print("    --- sample from", fs[0], "---")
        print(blocks[fs[0]][:1500])
