#!/usr/bin/env python3
"""quality_audit.py — 全库内容级质量审计（第二轴：跑得通 ≠ 写得对）。

run_skill_smoke.py 证明「脚本能跑」；本工具找「跑得通但结果悄悄不对 / 文档与实现脱节」：
  A. 宣传-实现脱节：SKILL.md 提的 --flag 在本技能任何脚本里都没实现（假宣传）；
     反向：脚本有的核心 --flag 却没写进 SKILL.md（文档缺口）。
  B. 静默回退风险：用户参数被默认值吞掉却报成功的可疑代码路径。
  C. 诚实性：unsupported / TODO / FIXME / placeholder / mock / except-pass 吞错。
  D. 退出码契约：main() 存在但没用 sys.exit()（失败恒 0，编排层门禁被绕过）。
  E. 弱测试盘点：自动生成的 test_smoke_all.py（2 断言）债务分布。

输出：tests/_full_test_artifacts/quality_audit.json + quality_audit.md
只报有证据的行号级问题，不臆造；每条带 sev（P0/P1/P2）。
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
ART = REPO / "tests" / "_full_test_artifacts"

FLAG_DEF = re.compile(r"add_argument\(\s*['\"](--[A-Za-z0-9_-]+)")
FLAG_MENTION = re.compile(r"(?<![\w-])(--[A-Za-z][A-Za-z0-9_-]{2,})")
SILENT_TERNARY = re.compile(
    r"args\.(\w+)\s+if\s+args\.\1\s+in\s+\w+\s+else\s+\w+")          # 覆盖值当枚举名查表
SILENT_GETVAR = re.compile(
    r"=\s*args\.(\w+)\s+if\s+args\.\1\s+else\s+.+")                  # 用户没给就静默换默认
EXCEPT_PASS = re.compile(r"except\s*(?:Exception)?\s*:\s*\n\s*pass")
BARE_EXCEPT = re.compile(r"except\s*:")
# 真·未完成实现的信号（字符串字面量被返回/赋值为状态、显式 NotImplementedError）
STUB_STATUS = re.compile(
    r"""(?:=\s*|return\s+)f?["'](unsupported|not_implemented|not-implemented)["']"""
    r"|raise\s+NotImplementedError")
TODO_MARK = re.compile(r"#\s*(TODO|FIXME)\b")
MOCK_WORD = re.compile(r"\bmock\b", re.I)
MAIN_DEF = re.compile(r"def main\s*\(")
SYS_EXIT = re.compile(r"sys\.exit\s*\(")
# SKILL.md 里提到这些外部工具的行，其 flag 属于外部 CLI，不算本技能假宣传
EXTERNAL_TOOL = re.compile(
    r"\b(git|docker|npm|npx|pnpm|yarn|eslint|tsc|pylint|pip|pipx|pytest|curl|wget|make|cargo|"
    r"mvn|gradle|gh|playwright|kubectl|helm|terraform|latexmk|pdflatex|chktex|vale|ffmpeg|"
    r"code|conda|uv|poetry|ruff|black|isort|mypy|sphinx|doxygen)\b")
UNIVERSAL_FLAGS = {"--help", "--version", "--verbose", "--debug", "--quiet", "--yes",
                   "--no-sandbox", "--noEmit", "--no-cache", "--force", "--color", "--json"}


def parse_fm(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm


def audit_skill(skill_dir: Path):
    rel = skill_dir.relative_to(REPO).as_posix()
    parts = rel.split("/")
    domain, name = parts[1], parts[-1]
    findings = []

    def add(sev, where, msg):
        findings.append({"sev": sev, "skill": f"{domain}/{name}", "where": where, "msg": msg})

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return findings, {}
    md_text = skill_md.read_text(encoding="utf-8", errors="ignore")
    fm = parse_fm(md_text)
    deprecated = "deprecated" in (fm.get("tier", "") + md_text[:2000].lower())

    scripts = sorted((skill_dir / "scripts").glob("*.py")) if (skill_dir / "scripts").is_dir() else []
    if not scripts:
        return findings, {"kind": "prompt-only"}

    # ---- 收集脚本事实 ----
    defined_flags, script_flag_doc, per_script = set(), set(), {}
    for sp in scripts:
        try:
            src = sp.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        flags = set(FLAG_DEF.findall(src))
        defined_flags |= flags
        script_flag_doc |= {f for f in flags if not f.startswith(("--debug", "--verbose"))}
        lines = src.splitlines()
        info = {"flags": sorted(flags), "hits": []}

        for i, line in enumerate(lines, 1):
            st = f"scripts/{sp.name}:{i}"
            for m in SILENT_TERNARY.finditer(line):
                info["hits"].append(("P0", st,
                    f"静默回退：args.{m.group(1)} 被当枚举名查表后吃默认值（paper 域 --journal 同款病灶）：{line.strip()[:110]}"))
            for m in SILENT_GETVAR.finditer(line):
                info["hits"].append(("P1", st,
                    f"可选性静默换默认：args.{m.group(1)} 未给时静默用默认值，需确认是否硬报错更合适：{line.strip()[:110]}"))
            if EXCEPT_PASS.search(line + (lines[i] if i < len(lines) else "")):
                info["hits"].append(("P1", st, f"except-pass 吞错：{line.strip()[:110]}"))
            if BARE_EXCEPT.search(line):
                info["hits"].append(("P0", st, f"裸 except：{line.strip()[:110]}"))
            if MOCK_WORD.search(line) and "status" in line:
                info["hits"].append(("P2", st, f"mock 轨（确认 SKILL.md 有诚实声明）：{line.strip()[:110]}"))
            if STUB_STATUS.search(line):
                info["hits"].append(("P1", st, f"未完成实现（状态字面量/NotImplementedError）：{line.strip()[:110]}"))
            if TODO_MARK.search(line):
                info["hits"].append(("P2", st, f"TODO/FIXME 待办标记：{line.strip()[:110]}"))
        if MAIN_DEF.search(src) and not SYS_EXIT.search(src):
            info["hits"].append(("P1", f"scripts/{sp.name}",
                                "def main() 存在但无 sys.exit(main()) → 失败恒退出 0，编排层门禁被绕过"))
        else:
            # 有 sys.exit 也要查 __main__ 守卫是否真的用它收尾（模板字符串里的 sys.exit 不算）
            guard = re.search(
                r'if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*\n(?P<body>(?:[ \t]+.*\n?)+)', src)
            if guard and MAIN_DEF.search(src):
                body = guard.group("body")
                if not re.search(r"(sys\.exit|raise\s+SystemExit)", body):
                    info["hits"].append(("P1", f"scripts/{sp.name}",
                                        "__main__ 守卫未用 sys.exit 收尾 → 失败恒退出 0（sys.exit 只出现在别处，如生成模板）"))
        per_script[sp.name] = info

    # ---- A1. SKILL.md 宣传的 flag 是否实现（deprecated 薄壳豁免——文档可提正典的 flag） ----
    md_flags = set(FLAG_MENTION.findall(md_text)) - UNIVERSAL_FLAGS
    ghosts = md_flags - defined_flags
    if ghosts and not deprecated:
        md_lines = md_text.splitlines()
        for f in sorted(ghosts):
            ctx_lines = [ln for ln in md_lines if f in ln]
            # flag 出现在外部工具命令行（git/npm/…）或提到其他技能的行 → 非本技能假宣传
            if any(EXTERNAL_TOOL.search(ln) for ln in ctx_lines):
                continue
            cross = any(re.search(r"(另一个技能|正典|迁移|superseded|deprecat)", ln) for ln in ctx_lines)
            add("P2" if cross else "P1", "SKILL.md",
                f"宣传了 --{f.lstrip('-')} 但本技能脚本未实现（假宣传/待核对）")
    # ---- A2. 脚本核心 flag 没写进 SKILL.md（文档缺口，P2） ----
    undoc = script_flag_doc - md_flags - {"--help"}
    if undoc and not deprecated:
        add("P2", "SKILL.md", f"脚本实现但文档未提的 flag：{', '.join(sorted(undoc))}")

    # ---- 汇总脚本内 hits ----
    for sp_name, info in per_script.items():
        for sev, st, msg in info["hits"]:
            add(sev, st, msg)

    # ---- E. 弱测试盘点 ----
    tests = list((skill_dir / "scripts").glob("test_smoke_*.py"))
    weak = [t.name for t in tests
            if t.name == "test_smoke_all.py"
            and t.read_text(encoding="utf-8", errors="ignore").count("def test_") <= 2]
    meta = {"kind": "scripted", "scripts": len(scripts), "tests": len(tests), "weak_tests": len(weak)}
    if weak:
        add("P2", "scripts", f"弱冒烟测试（自动生成 2 断言）：{', '.join(weak)}")
    return findings, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", help="只审某个域")
    ap.add_argument("--sev", default="P0,P1,P2", help="输出包含的级别")
    args = ap.parse_args()
    want = set(args.sev.split(","))

    all_findings, stats = [], {}
    domains = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    for d in domains:
        if args.domain and d.name != args.domain:
            continue
        for skill_dir in sorted(d.rglob("SKILL.md")):
            f, meta = audit_skill(skill_dir.parent)
            all_findings.extend(f)
            stats[f"{d.name}/{skill_dir.parent.name}"] = meta

    counts = {s: sum(1 for x in all_findings if x["sev"] == s) for s in ("P0", "P1", "P2")}
    by_skill = {}
    for f in all_findings:
        if f["sev"] in want:
            by_skill.setdefault(f["skill"], []).append(f)

    ART.mkdir(parents=True, exist_ok=True)
    (ART / "quality_audit.json").write_text(
        json.dumps({"generated": datetime.now(timezone.utc).isoformat(),
                    "counts": counts, "findings": all_findings, "stats": stats},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 全库内容级质量审计（quality_audit）", "",
             f"> 生成：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}　|　"
             f"P0={counts['P0']}　P1={counts['P1']}　P2={counts['P2']}",
             "> 口径：跑得通 ≠ 写得对。专找静默回退 / 假宣传 / 吞错 / 退出码契约 / 弱测试。", ""]
    for sev in ("P0", "P1", "P2"):
        items = [f for f in all_findings if f["sev"] == sev and f["sev"] in want]
        if not items:
            continue
        lines += [f"## {sev}（{len(items)} 条）", ""]
        for f in items:
            lines.append(f"- **`{f['skill']}`** `{f['where']}` — {f['msg']}")
        lines.append("")
    if not any(f["sev"] in want for f in all_findings):
        lines.append("- （无发现）")
    (ART / "quality_audit.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"audited skills: {len(stats)} | findings: P0={counts['P0']} "
          f"P1={counts['P1']} P2={counts['P2']}")
    print(f"-> {ART / 'quality_audit.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
