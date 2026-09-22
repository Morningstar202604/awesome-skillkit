#!/usr/bin/env python3
"""lint_skill.py — 单个 SKILL.md 或目录树的规范校验器（awesome-skillkit / Skill Forge）。

八项必查（判定规则见每项 docstring 与 SKILL.md 的检查项表）：

  FM-FIELDS   frontmatter 存在且含 name/description/license/metadata 四块
  NAME-SYNC   name 与目录名一致、kebab-case、不含大写
  DESC-ROUTE  description 含 Use when 与 Do NOT（或中文等价），触发词 >=5 个
  BODY-SECTS  正文含 10 个骨架 H2 标题（输入清单/前置自检/工作流/交付标准/
              失败处置表/参考 为六项硬性）
  BODY-LINES  总行数 < 220（超出报 WARN）
  LANG-CJK    正文去代码块后 CJK 字符占比 < 0.15 报 WARN
  REF-EXISTS  `references/xxx.md` 相对技能目录必须真实存在
  FAIL-TABLE  `## 失败处置表` 下表格行数 >= 4

退出码：存在任一条 FAIL → 1；否则 0。WARN 不影响退出码，便于 CI 直接把本脚本
挂成门禁。

用法：
  python3 lint_skill.py <SKILL.md 路径 | 技能目录 | 技能目录的父目录>
  python3 lint_skill.py skills/ --json
  python3 lint_skill.py skills/meta/skill-finder --verbose

仅用标准库。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 常量与规则

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

#: 正文骨架里必须出现的 H2 标题。前六项是硬性结构，缺一即 FAIL。
REQUIRED_H2 = [
    "输入清单",
    "前置自检",
    "工作流",
    "交付标准",
    "失败处置表",
    "参考",
]
#: 另外四个推荐 H2（总计构成"10 章节骨架"），缺失只报 WARN。
OPTIONAL_H2 = [
    "参数速查表",
    "Prompt 构造公式",
    "常见错误",
    "工作流变体",
]
RECOMMENDED_H2_TOTAL = 10

#: description 里判定"何时使用 / 排除项"的中英等价写法。
USE_WHEN_HINTS = ("use when", "use this", "when the user", "当用户", "何时使用", "触发")
DO_NOT_HINTS = ("do not use", "don't use", "not for", "排除", "不适用", "不要用于")

#: 触发词计数的中英引导语之后的分隔符。
TRIGGER_SPLIT_RE = re.compile(r"[/、,，;；]| or | and ")

BODY_LINE_LIMIT = 220      # 超过报 WARN（仓库硬门禁是 500，这里是技能级自律线）
CJK_RATIO_FLOOR = 0.15     # 正文去代码块后 CJK 占比下限
MIN_FAILTABLE_ROWS = 4     # 失败处置表最少数据行数
MIN_DESC_LEN = 40
MAX_DESC_LEN = 1024

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
FENCE_RE = re.compile(r"^\s*```")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
REF_LINK_RE = re.compile(r"`(references/[A-Za-z0-9._\-/]+\.md)`")
REF_BULLET_RE = re.compile(r"^\s*[-*]\s+`?(references/[A-Za-z0-9._\-/]+\.md)")
#: 目录名里出现这些时不是技能目录，跳过（避免把模板/共享片段当技能报错）。
#: 注意：**不含 `assets`**——`skills/writing/assets/ai-cover-generator` 是被
#: 三个 pack 真实引用的技能，跳过它会让它长期逃过 lint（与 validate_skills.py 口径一致）。
SKIP_DIR_NAMES = {"_common", "__pycache__", "templates"}


class Finding:
    """一条检查结论。level ∈ {PASS, WARN, FAIL}。"""

    def __init__(self, check, level, message, fix=""):
        self.check = check
        self.level = level
        self.message = message
        self.fix = fix

    def as_dict(self):
        return {
            "check": self.check,
            "level": self.level,
            "message": self.message,
            "fix": self.fix,
        }


# ---------------------------------------------------------------- 解析工具


def split_frontmatter(text):
    """返回 (frontmatter 行列表 | None, 正文)。首行必须恰好是 ---。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def parse_simple_yaml(fm_lines):
    """最小 YAML 子集解析：标量、折叠/字面块、一层嵌套 map。

    与仓库 tools/validate_skills.py 同款策略：只认 frontmatter 实际用到的形态，
    不引入 PyYAML 依赖。
    """
    data = {}
    i, n = 0, len(fm_lines)
    while i < n:
        line = fm_lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in ("", ">", ">-", "|", "|-", "|+"):
            block, j = [], i + 1
            while j < n and (fm_lines[j][:1] in (" ", "\t") or not fm_lines[j].strip()):
                block.append(fm_lines[j])
                j += 1
            if val.startswith(">") or val.startswith("|"):
                data[key] = " ".join(s.strip() for s in block if s.strip())
            else:
                sub = {}
                for bl in block:
                    sm = re.match(r"^\s+([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", bl)
                    if sm:
                        sub[sm.group(1)] = sm.group(2).strip().strip("\"'")
                data[key] = sub
            i = j
        else:
            data[key] = val.strip("\"'")
            i += 1
    return data


def strip_code_blocks(body):
    """去掉围栏代码块，返回 (去块后的文本, 被去掉的字符数)。"""
    out, in_fence = [], False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out), len(body) - len("\n".join(out))


def count_trigger_words(desc):
    """从 description 里数中英双语触发词。

    规则：取 "use when" / "当用户" 之后的片段，按 / 、 或 切分，
    统计长度 >= 2 的片段数；两个引导语都找不到时回退为 0。
    """
    low = desc.lower()
    segments = []
    for hint in ("use when", "当用户", "触发"):
        idx = low.find(hint)
        if idx == -1:
            continue
        tail = desc[idx + len(hint):]
        # 到排除项或句末为止
        for stop in ("do not use", "don't use", "排除", "不适用"):
            cut = tail.lower().find(stop)
            if cut != -1:
                tail = tail[:cut]
        segments.append(tail)
    if not segments:
        return 0
    joined = " ".join(segments)
    parts = [p.strip(" 。.”\"'()") for p in TRIGGER_SPLIT_RE.split(joined)]
    return sum(1 for p in parts if len(p) >= 2)


def is_table_row(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def count_table_rows(section_lines):
    """数一张 Markdown 表格的数据行（排除表头与 |---| 分隔行）。"""
    rows = 0
    for line in section_lines:
        if not is_table_row(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c or "---") for c in cells):
            continue                      # 分隔行
        rows += 1
    return max(0, rows - 1)               # 减去表头


def section_slice(body_lines, title):
    """取出 `## <title>` 到下一个同级标题之间的行。"""
    start = None
    for i, line in enumerate(body_lines):
        m = H2_RE.match(line)
        if m and m.group(1).startswith(title):
            start = i + 1
            continue
        if start is not None and H2_RE.match(line):
            return body_lines[start:i]
    return body_lines[start:] if start is not None else []


# ---------------------------------------------------------------- 八项检查


def check_frontmatter_fields(raw, meta, fm_lines):
    """FM-FIELDS：四块是否齐全，description 长度是否在区间内。"""
    findings = []
    if fm_lines is None:
        return [Finding("FM-FIELDS", "FAIL", "缺少或以非 `---` 开头的 frontmatter",
                        "在文件第 1 行写 `---`，补全 name/description/license/metadata 后闭合 `---`")]
    findings.append(Finding("FM-FIELDS", "PASS", "frontmatter 存在且可解析"))
    for key in ("name", "description", "license"):
        if not meta.get(key):
            findings.append(Finding("FM-FIELDS", "FAIL", f"frontmatter 缺少 `{key}`",
                                    f"补 `{key}:` 字段"))
    md = meta.get("metadata")
    if not isinstance(md, dict) or not md:
        findings.append(Finding("FM-FIELDS", "FAIL", "frontmatter 缺少 `metadata` 块",
                                "补 metadata 及 author/version/category/verified-date"))
    else:
        for k in ("version", "category", "verified-date"):
            if k not in md:
                findings.append(Finding("FM-FIELDS", "WARN",
                                        f"metadata.{k} 缺失",
                                        f"补 `{k}:` 便于版本追踪与时效核查"))
    desc = meta.get("description", "") or ""
    if desc and not (MIN_DESC_LEN <= len(desc) <= MAX_DESC_LEN):
        findings.append(Finding("FM-FIELDS", "WARN",
                                f"description 长度 {len(desc)} 超出 {MIN_DESC_LEN}-{MAX_DESC_LEN}",
                                "压缩到 40-1024 字符，删去形容词保留触发语与排除项"))
    return findings


def check_name_sync(skill_dir, meta):
    """NAME-SYNC：name == 目录名、kebab-case、无大写。"""
    name = str(meta.get("name", "") or "")
    # target 为 "." 时 Path(".").name 是空串 → 先 resolve 再取目录名
    dir_name = skill_dir.resolve().name
    if not name:
        return [Finding("NAME-SYNC", "FAIL", "frontmatter 无 `name`", "补 name 字段")]
    findings = []
    if name != dir_name:
        findings.append(Finding("NAME-SYNC", "FAIL",
                                f"name `{name}` 与目录名 `{dir_name}` 不一致",
                                f"把 name 改为 `{dir_name}`，或把目录改名为 `{name}`"))
    if name != name.lower():
        findings.append(Finding("NAME-SYNC", "FAIL", f"name `{name}` 含大写字母",
                                "改为全小写（仅 a-z0-9-）"))
    if not NAME_RE.match(name):
        findings.append(Finding("NAME-SYNC", "FAIL",
                                f"name `{name}` 不符合 kebab-case",
                                "只保留小写字母数字与单个连字符，不以连字符开头/结尾"))
    if not findings:
        findings.append(Finding("NAME-SYNC", "PASS", f"name `{name}` 与目录名一致且合规"))
    return findings


def check_description_routing(meta):
    """DESC-ROUTE：Use when / Do NOT / 触发词 >=5。"""
    desc = str(meta.get("description", "") or "")
    if not desc:
        return [Finding("DESC-ROUTE", "FAIL", "description 为空",
                        "写 what + Use when + 中英触发词(>=5) + Do NOT 排除项")]
    low = desc.lower()
    findings = []
    has_use = any(h in low for h in USE_WHEN_HINTS)
    has_not = any(h in low for h in DO_NOT_HINTS)
    if not has_use:
        findings.append(Finding("DESC-ROUTE", "FAIL", "description 无 `Use when` 或中文等价引导语",
                                "补 `Use when ...` 或 `当用户要求 ... 时使用`"))
    if not has_not:
        findings.append(Finding("DESC-ROUTE", "FAIL", "description 无 `Do NOT` 或中文等价排除项",
                                "补 `Do NOT use for ...`，写清哪些相似请求不该命中本技能"))
    n_trig = count_trigger_words(desc)
    if n_trig < 5:
        findings.append(Finding("DESC-ROUTE", "FAIL",
                                f"触发词仅 {n_trig} 个（要求 >=5）",
                                "在 Use when / 当用户 之后用 `/` 分隔补齐中英触发短语"))
    if not findings:
        findings.append(Finding("DESC-ROUTE", "PASS",
                                f"路由信息完整，触发词 {n_trig} 个"))
    return findings


def check_body_sections(body_lines):
    """BODY-SECTS：六个硬性 H2 + 推荐凑满 10 个骨架标题。"""
    titles = [H2_RE.match(l).group(1) for l in body_lines if H2_RE.match(l)]
    findings = []
    missing = [t for t in REQUIRED_H2 if not any(x.startswith(t) for x in titles)]
    for t in missing:
        findings.append(Finding("BODY-SECTS", "FAIL", f"缺少必需 H2 `## {t}`",
                                f"按骨架补 `## {t}` 一节"))
    if missing:
        return findings
    findings.append(Finding("BODY-SECTS", "PASS", "六个硬性 H2 齐全"))
    extra = len(titles)
    if extra < RECOMMENDED_H2_TOTAL:
        findings.append(Finding("BODY-SECTS", "WARN",
                                f"仅 {extra} 个 H2，距 10 章节骨架差 {RECOMMENDED_H2_TOTAL - extra} 个",
                                "补参数速查表 / 常见错误 / 工作流变体等可选章节"))
    return findings


def check_body_lines(raw):
    """BODY-LINES：总行数 < 220。"""
    n = len(raw.splitlines())
    if n >= BODY_LINE_LIMIT:
        return [Finding("BODY-LINES", "WARN",
                        f"共 {n} 行，超过 {BODY_LINE_LIMIT} 行自律线",
                        "把领域知识移入 references/，正文只留导航与工作流")]
    return [Finding("BODY-LINES", "PASS", f"共 {n} 行")]


def check_language_ratio(body):
    """LANG-CJK：正文去代码块后 CJK 占比 < 0.15 报 WARN。"""
    text, _ = strip_code_blocks(body)
    stripped = re.sub(r"\s", "", text)
    if not stripped:
        return [Finding("LANG-CJK", "WARN", "正文去代码块后为空",
                        "正文至少要有可读的中文说明")]
    ratio = len(CJK_RE.findall(stripped)) / len(stripped)
    if ratio < CJK_RATIO_FLOOR:
        return [Finding("LANG-CJK", "WARN",
                        f"正文 CJK 占比 {ratio:.3f} < {CJK_RATIO_FLOOR}，正文疑似应为中文",
                        "把叙述性段落改为中文；frontmatter 与代码保持英文")]
    return [Finding("LANG-CJK", "PASS", f"正文 CJK 占比 {ratio:.3f}")]


def check_references_exist(skill_dir, raw):
    """REF-EXISTS：正文提到的 `references/*.md` 必须真实存在。"""
    refs = set(REF_LINK_RE.findall(raw))
    refs |= set(REF_BULLET_RE.findall(raw))
    if not refs:
        return [Finding("REF-EXISTS", "WARN", "正文未引用任何 references/*.md",
                        "如有领域知识，拆到 references/ 并从 `## 参考` 链接")]
    findings, broken = [], []
    for r in sorted(refs):
        if not (skill_dir / r).is_file():
            broken.append(r)
    for r in broken:
        findings.append(Finding("REF-EXISTS", "FAIL", f"引用的 `{r}` 不存在",
                                f"创建 {r} 或从正文删除该引用"))
    if not broken:
        findings.append(Finding("REF-EXISTS", "PASS", f"{len(refs)} 个引用全部存在"))
    return findings


def check_fail_table(body_lines):
    """FAIL-TABLE：`## 失败处置表` 数据行 >= 4。"""
    lines = section_slice(body_lines, "失败处置表")
    if not lines:
        return [Finding("FAIL-TABLE", "FAIL", "无 `## 失败处置表` 一节或该节为空",
                        "补一节三列表格：现象/错误码 | 原因 | 处置")]
    rows = count_table_rows(lines)
    if rows < MIN_FAILTABLE_ROWS:
        return [Finding("FAIL-TABLE", "FAIL",
                        f"失败处置表仅 {rows} 行（要求 >= {MIN_FAILTABLE_ROWS}）",
                        "补足至少 4 条真实失败场景（含错误原文与具体处置动作）")]
    return [Finding("FAIL-TABLE", "PASS", f"失败处置表 {rows} 行")]


# ---------------------------------------------------------------- 主流程


def lint_one(skill_md: Path):
    """校验单个 SKILL.md，返回 (skill_md, findings, exit_fail_count)。"""
    raw = skill_md.read_text(encoding="utf-8", errors="ignore")
    fm_lines, body = split_frontmatter(raw)
    meta = parse_simple_yaml(fm_lines) if fm_lines is not None else {}
    if fm_lines is not None and not isinstance(meta.get("metadata"), dict):
        pass
    body_lines = body.splitlines()

    findings = []
    findings += check_frontmatter_fields(raw, meta, fm_lines)
    findings += check_name_sync(skill_md.parent, meta)
    findings += check_description_routing(meta)
    findings += check_body_sections(body_lines)
    findings += check_body_lines(raw)
    findings += check_language_ratio(body)
    findings += check_references_exist(skill_md.parent, raw)
    findings += check_fail_table(body_lines)
    return skill_md, findings


def iter_skill_files(target: Path):
    """把 CLI 参数解析成 SKILL.md 列表（支持单文件 / 技能目录 / 父目录树）。"""
    if target.is_file():
        return [target] if target.name == "SKILL.md" else []
    if (target / "SKILL.md").is_file():
        return [target / "SKILL.md"]
    out = []
    for p in sorted(target.rglob("SKILL.md")):
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        # 样例/模板技能（sample-*）不参与发布，与 validate_skills.py 口径一致。
        if p.parent.name.startswith("sample-"):
            continue
        out.append(p)
    return out


def collect(target: Path):
    """返回 [(skill_md, findings)] 列表。target 不存在时抛 FileNotFoundError。"""
    if not target.exists():
        raise FileNotFoundError(f"路径不存在：{target}")
    results = []
    for md in iter_skill_files(target):
        results.append(lint_one(md))
    return results


def render_text(results, verbose=False):
    """打印人类可读报告，返回 (fail_count, warn_count)。"""
    fail_total = warn_total = 0
    for skill_md, findings in results:
        fails = [f for f in findings if f.level == "FAIL"]
        warns = [f for f in findings if f.level == "WARN"]
        fail_total += len(fails)
        warn_total += len(warns)
        status = "FAIL" if fails else ("WARN" if warns else "PASS")
        print(f"[{status}] {skill_md.parent.name}  ({skill_md})")
        for f in findings:
            if f.level == "PASS" and not verbose:
                continue
            print(f"    {f.level:<4} {f.check:<12} {f.message}")
            if f.level != "PASS" and f.fix:
                print(f"         FIX: {f.fix}")
    print("-" * 68)
    print(f"skills: {len(results)}  FAIL: {fail_total}  WARN: {warn_total}")
    print("RESULT: PASS" if fail_total == 0 else "RESULT: FAIL")
    return fail_total, warn_total


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="lint_skill.py",
        description="校验 SKILL.md 是否符合 awesome-skillkit 规范，输出 PASS/WARN/FAIL 报告。",
    )
    ap.add_argument("target", help="SKILL.md 路径、技能目录，或含多个技能的父目录")
    ap.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    ap.add_argument("--verbose", action="store_true", help="文本模式下也打印 PASS 项")
    args = ap.parse_args(argv)

    try:
        results = collect(Path(args.target))
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    if not results:
        print(f"未找到任何 SKILL.md：{args.target}", file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "skills": [
                {
                    "name": md.parent.name,
                    "path": md.as_posix(),
                    "status": (
                        "FAIL" if any(f.level == "FAIL" for f in fs)
                        else "WARN" if any(f.level == "WARN" for f in fs)
                        else "PASS"
                    ),
                    "findings": [f.as_dict() for f in fs],
                }
                for md, fs in results
            ]
        }
        fails = sum(1 for s in payload["skills"] for f in s["findings"] if f["level"] == "FAIL")
        warns = sum(1 for s in payload["skills"] for f in s["findings"] if f["level"] == "WARN")
        payload["summary"] = {"skills": len(results), "fail": fails, "warn": warns}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if fails else 0

    fail_total, _ = render_text(results, verbose=args.verbose)
    return 1 if fail_total else 0


if __name__ == "__main__":
    sys.exit(main())
