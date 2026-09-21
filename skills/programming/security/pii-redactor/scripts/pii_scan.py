#!/usr/bin/env python3
import argparse, hashlib, re, sys, os, pathlib
RE_ID_CARD   = re.compile(r"(?<!\d)(\d{17}[\dXx])(?!\d)")
RE_PHONE     = re.compile(r"(?<!\d)(\+?86[-\s]?)?(1[3-9]\d{9})(?!\d)")
RE_EMAIL     = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
RE_BANK_CARD = re.compile(r"(?<!\d)(\d{13,19})(?!\d)")
RE_CREDIT    = re.compile(r"(?<![0-9A-Za-z])([A-Z0-9]{2}\d{6}[A-Z0-9]{10})(?![0-9A-Za-z])")
PROV = "\u5317\u4eac\u6caa\u6666\u6052\u5f00\u6cb3\u5e7f\u5c71\u897f\u5ddd\u8572\u6e58\u76d1\u7ea2\u6f5c\u5c71\u4e1c\u5317\u5b81\u5385\u83b1\u6d99\u6d9e\u8d64\u6d9d\u6770\u6e14\u5370\u8499\u808c\u7518\u9752\u8d35\u5ddd\u897f\u85cf"
RE_PLATE = re.compile(r"([" + PROV + r"][A-Z])\d{4,5}[A-Z0-9\u6302\u5b66\u8b66\u6e2f\u4f7f\u9886]")
RE_ADDR = re.compile(r"(" + PROV + r"[\u7701\u5e02]?[\u4e00-\u9fa5]{2,20}(\u8def|\u8857|\u9053|\u5cf0|\u53f7)[\u4e00-\u9fa5\d]{0,20})")
NAME_KEYS = re.compile(r"(\u59d3\u540d|\u8054\u7cfb\u4eba|\u5ba2\u6237\u540d|\u7528\u6237\u5b9e\u540d|applicant|full[_]?name)\s*[:\uff1a=]\s*([\u4e00-\u9fa5A-Za-z\u00b7]{2,15})")
ID_WEIGHTS = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
ID_CHECK = "10X98765432"
def luhn_ok(s):
    total, alt = 0, False
    for ch in reversed(s):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0
def idcard_ok(s):
    if len(s) != 18 or not s[:17].isdigit():
        return False
    ssum = sum(int(c) * w for c, w in zip(s[:17], ID_WEIGHTS))
    return ID_CHECK[ssum % 11] == s[17].upper()
def credit_ok(s):
    # 统一社会信用代码前 2 位为登记管理部门代码，纯数字开头多为身份证误配，排除
    return len(s) == 18 and any(c.isalpha() for c in s[:2])
def mask_phone(v):
    p = v[-11:] if len(v) >= 11 else v
    return p[:3] + "****" + p[7:] if len(p) >= 11 else "***"
MASKERS = {
    "id_card":     lambda v: v[:4] + "*" * (len(v) - 8) + v[-4:],
    "phone":       mask_phone,
    "email":       lambda v: (v[0] + "***" + v[v.index("@"):]) if "@" in v else v[0] + "***",
    "bank_card":   lambda v: v[:4] + "*" * (len(v) - 8) + v[-4:],
    "plate":       lambda v: v[:2] + "*" * (len(v) - 3) + v[-1],
    "credit_code": lambda v: v[:8] + "*" * (len(v) - 8),
    "address":     lambda v: "[ADDR MASKED]",
    "name":        lambda v: "[NAME MASKED]",
}
def checkers(no_heur):
    base = {
        "id_card":     (RE_ID_CARD,    lambda v: idcard_ok(v)),
        "phone":       (RE_PHONE,      lambda v: True),
        "email":       (RE_EMAIL,      lambda v: True),
        "bank_card":   (RE_BANK_CARD,  lambda v: luhn_ok(v)),
        "credit_code": (RE_CREDIT,     credit_ok),
        "plate":       (RE_PLATE,      lambda v: True),
    }
    if not no_heur:
        base["address"] = (RE_ADDR,   lambda v: True)
        base["name"]    = (NAME_KEYS, lambda v: True)
    return base
def scan_line(line, cats, no_heur):
    hits = []
    rules = checkers(no_heur)
    for cat in cats:
        rule = rules.get(cat)
        if not rule:
            continue
        pat, ok = rule
        for m in pat.finditer(line):
            val = m.group(0)
            for g in reversed(m.groups()):
                if g is not None:
                    val = g
                    break
            if not ok(val):
                continue
            hits.append((m.start(), m.end(), cat, val))
    return hits
def apply_hits(line, hits, strategy):
    for start, end, cat, val in sorted(hits, reverse=True):
        if strategy == "hash":
            repl = hashlib.sha256(val.encode()).hexdigest()[:8]
        elif strategy == "replace":
            # 完全占位符：不留任何原值片段（mask 会保留首尾位，hash 保留可关联指纹）
            repl = "[REDACTED:%s]" % cat
        else:
            repl = MASKERS[cat](val)
        line = line[:start] + repl + line[end:]
    return line
def collect_files(path):
    p = pathlib.Path(path)
    if p.is_file():
        return [p]
    if not p.exists():
        print("PATH NOT FOUND: " + path, file=sys.stderr)
        sys.exit(1)
    exts = {".log", ".txt", ".json", ".csv", ".md"}
    out = []
    for root, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if pathlib.Path(f).suffix in exts:
                out.append(pathlib.Path(root) / f)
    return out
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strategy", choices=["mask", "hash", "replace"], default="mask")
    ap.add_argument("--out", default=None)
    ap.add_argument("--categories", default=None)
    ap.add_argument("--no-heuristics", action="store_true")
    a = ap.parse_args()
    if not a.dry_run and a.out is None:
        a.out = a.path + ".redacted" if not os.path.isdir(a.path) else None
        if a.out is None:
            print("PERM: directory redaction requires --out", file=sys.stderr)
            sys.exit(2)
    cats = ([c.strip() for c in a.categories.split(",") if c.strip()] if a.categories
            else list(checkers(a.no_heuristics).keys()))
    files = collect_files(a.path)
    total, redact_buf = 0, []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print("SKIP %s: %s" % (f, e), file=sys.stderr)
            continue
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            hits = scan_line(line, cats, a.no_heuristics)
            if hits:
                total += len(hits)
                if a.dry_run:
                    cat, val = hits[0][2], hits[0][3]
                    print("L%d\t%s\t%s\t%s" % (i + 1, cat, MASKERS[cat](val), str(f)))
        if not a.dry_run:
            redact_buf.append("".join(apply_hits(l, scan_line(l, cats, a.no_heuristics), a.strategy) for l in lines))
    if a.dry_run:
        print("SUMMARY: %d hits across %d files" % (total, len(files)))
    else:
        if len(files) > 1:
            # 多文件合并输出必须保留文件边界，否则消费方无法还原归属
            parts = []
            for f, buf in zip(files, redact_buf):
                parts.append("===== %s =====\n%s" % (str(f).replace("\n", "_"), buf))
            payload = "\n".join(parts)
        else:
            payload = redact_buf[0]
        pathlib.Path(a.out).write_text(payload, encoding="utf-8")
        print("REDACTED: %s (%d hits %s)" % (a.out, total, a.strategy))
    return 0
if __name__ == "__main__":
    sys.exit(main())
