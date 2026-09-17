from pathlib import Path

for d in sorted(Path("skills").iterdir()):
    if not d.is_dir():
        continue
    subs = sorted(d.rglob("SKILL.md"))
    # 与 validate_skills.iter_skills() 口径一致：只排除 _common/templates 与 sample-*，
    # 保留 assets/ 下的真实技能（如 writing/assets/ai-cover-generator）。
    names = [
        s.parent.name
        for s in subs
        if "_common" not in s.parts
        and "templates" not in s.parts
        and not s.parent.name.startswith("sample")
    ]
    print(f"[{d.name}] ({len(names)}):")
    for n in names:
        print(f"  - {n}")
    print()
