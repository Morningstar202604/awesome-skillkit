from pathlib import Path

for d in sorted(Path("skills").iterdir()):
    if not d.is_dir():
        continue
    subs = sorted(d.rglob("SKILL.md"))
    names = [s.parent.name for s in subs if "assets" not in str(s.parts) and "sample" not in s.parent.name]
    print(f"[{d.name}] ({len(names)}):")
    for n in names:
        print(f"  - {n}")
    print()
