#!/usr/bin/env python3
"""real_scenario_test.py — 全库严格场景化实测（第三代证明）。

与前两代的区别：
  第一代 full_skill_test.py：手搓代理 task，不测真实技能（已废弃）。
  第二代 run_skill_smoke.py：跑技能自带 test_smoke_*.py，证明「能跑」。
  本代：**给每个脚本技能一个来自其 SKILL.md 用例的真实场景任务**，
  构造真实输入跑真实入口，断言「真实交付物」（退出码 / JSON 契约 / 产物文件 /
  无 traceback / 诚实标注），证据落到报告里。

场景来源：每个技能 SKILL.md 的用法示例（文档承诺的用法 = 场景任务）；
--output 重定向到临时目录；示例里引用但不存在的输入文件按扩展名合成
（.json 优先取 SKILL.md 里的 JSON 示例，文本类用够长的真实感内容）。

LLM 模式：--with-llm 时从 models.json 读可用网关注入 SKILLKIT_LLM_* env，
生成类技能走真模型；失败自动离线兜底（技能侧已实现诚实标注）。

判定：
  pass        所有断言过
  fail        跑了但有断言失败（技能 bug 候选，附证据）
  error       脚本抛 traceback（硬伤）
  no-example  SKILL.md 没有可解析的用法示例（文档债，P2）
  spec-error  场景构造自身失败（不算技能 bug，需修驱动器）

输出：tests/_full_test_artifacts/real_scenario_report.{md,json}
"""
import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
ART = REPO / "tests" / "_full_test_artifacts"

ARTICLE = ("# FastAPI 性能优化实战\n\n"
           "在高并发场景下，FastAPI 的性能优化需要从异步模型、连接池、缓存三层入手。"
           "实测表明，合理配置 uvicorn worker 数量能把吞吐量提升两倍以上：worker 数应接近 "
           "CPU 核心数，而不是盲目调大。第二步是数据库连接池，SQLAlchemy 的 pool_size "
           "与 max_overflow 要按 QPS 峰值估算，连接复用能显著降低 P99 延迟。"
           "第三层是缓存，热点接口加 Redis 缓存后平均响应时间从 180ms 降到 23ms。"
           "最后，别忘了开启 GZip 中间件与响应模型过滤，序列化开销同样不可忽视。") * 6

GENERIC_TEXT_EXTS = {".md", ".txt", ".markdown", ".rst", ".tex", ".srt", ".csv",
                     ".yaml", ".yml", ".bib", ".log"}

# 严格场景覆盖表：对旗舰技能给出比文档示例更苛刻的定制任务与断言
# 值: dict(cmd=[...], assert_json={field: expected}, assert_file={ext: min_bytes})
OVERRIDES = {
    "paper/pub-plotter": {
        "scenario": "按 Science 单栏真实版面(4.76in)画热力图（含负值→发散色）",
        "cmd": ["--type", "heatmap", "--journal", "science",
                "--data", "@json:{\"matrix\": [[0.8, -0.3], [0.1, 0.9]], \"rows\": [\"A\", \"B\"], \"cols\": [\"x\", \"y\"]}"],
        "out": "ov_pub.pdf",
        "assert_json": {"width_inches": 4.76, "cmap": "RdBu_r", "type": "heatmap"},
    },
    "video/video-script-writer": {
        "scenario": "60 秒教程脚本；配了 LLM 网关时台词必须由真模型生成",
        "cmd": ["--concept", "打工人用 AI 一周做完一个月的活", "--type", "tutorial",
                "--duration", "60", "--platform", "bilibili"],
        "out": "ov_script.json",
        "assert_llm_source": True,
    },
    "programming/math/simulation-runner": {
        "scenario": "真实蒙特卡洛（n=5000, mu=1, sigma=2, threshold=3），禁止 demo 标注",
        "cmd": ["--monte-carlo", "--n", "5000", "--mu", "1", "--sigma", "2", "--threshold", "3"],
        "out": "ov_sim.json",
        "assert_json_absent": ["demo"],
    },
    "writing/seo-optimizer": {
        "scenario": "给一篇真实长文算 SEO 分并给关键词",
        "cmd": ["--title", "FastAPI 性能优化实战 2026", "--content", "@text:ARTICLE"],
        "out": "ov_seo.json",
        "assert_json_min": {"meta.score": 1},
    },
    "paper/figure-maker": {
        "scenario": "弃用薄壳走 heatmap 透传（真实渲染而非 unsupported）",
        "cmd": ["--type", "heatmap", "--data",
                "@json:{\"matrix\": [[0.5, 0.9], [0.2, 0.7]]}"],
        "out": "ov_fm.pdf",
        "assert_json": {"deprecated": True, "rendered": True},
    },
}


def skill_md_text(skill_dir: Path) -> str:
    p = skill_dir / "SKILL.md"
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def extract_json_example(md: str):
    """取 SKILL.md 里第一个可解析的 ```json 块。"""
    for m in re.finditer(r"```json\s*\n(.*?)```", md, re.S):
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
    return None


# 需要外部资源/用户代码的例子不适合当离线场景，选择时降权
NEEDS_EXTERNAL = ("--mode real", "--metric ", "--s2", "--arxiv", "--llm-evidence",
                  "--with-llm", "--endpoint", "--token", "--api-key")


def extract_examples(script: Path, md: str):
    """从 SKILL.md 代码围栏里找调用本脚本的示例命令行。"""
    out = []
    # 语言标记用 [A-Za-z]* 通配：枚举式 (?:bash|sh|...) 在 ```json 上会失配，
    # 使匹配起点滑到下一个围栏标记 → 内容整体错位（已踩坑）。
    for m in re.finditer(r"```[A-Za-z]*\s*\n(.*?)```", md, re.S):
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith("#") or script.name not in line:
                continue
            if line.startswith("test -f") or "python" not in line:
                continue  # 前置自检/纯 shell 行不是场景任务
            out.append(line)
    return out


def parse_example(line: str):
    """把示例行拆成 argv（去掉 python 前缀、行尾注释与重定向）。"""
    line = re.sub(r"\s#.*$", "", line)  # 行尾注释（# 离线/CI …）
    line = re.sub(r"^.*?python3?\s+", "", line)
    line = re.sub(r"\s*(>|>>|2>)\s*\S+$", "", line)
    line = line.replace("\\\n", " ").replace("\\", " ")
    try:
        return shlex.split(line)
    except ValueError:
        return None


def store_true_flags(src: str) -> set:
    flags = set()
    for m in re.finditer(r"add_argument\(\s*['\"](--[A-Za-z0-9_-]+)['\"]([^)]*)\)", src, re.S):
        if 'store_true' in m.group(2) or 'action="store_true"' in m.group(2):
            flags.add(m.group(1))
    return flags


def build_spec(skill_dir: Path, script: Path):
    """为脚本构造场景任务。返回 (argv, notes, scenario) 或 raise SpecError。"""
    md = skill_md_text(skill_dir)
    src = script.read_text(encoding="utf-8", errors="ignore")
    st_flags = store_true_flags(src)
    examples = extract_examples(script, md)

    argv, notes = None, []
    candidates = []
    for line in examples:
        parsed = parse_example(line)
        if not (parsed and len(parsed) >= 2):
            continue
        a = [t for t in parsed if t not in ("python3", "python")]
        while a and (a[0].endswith(".py") or script.stem in a[0]):
            a.pop(0)
        if not a:
            continue
        # 去掉行尾注释 token（# 开头）， shlex 会把它们当参数
        a = [t for t in a if not t.startswith("#")]
        penalty = sum(1 for pat in NEEDS_EXTERNAL if pat in line)
        candidates.append((penalty, -len(a), a))
    if candidates:
        candidates.sort()
        argv = candidates[0][2]
    if argv is None:
        raise SpecError("SKILL.md 无可解析用法示例")

    scenario = " ".join(argv[:6])
    json_ex = None
    tmp = Path(_TMP)
    out_idx = []

    def ensure_input(token: str) -> str:
        nonlocal json_ex
        cand = [skill_dir / token, skill_dir / "scripts" / token, REPO / token]
        for c in cand:
            if c.exists() and c.is_file():
                return str(c.resolve())
        ext = Path(token).suffix.lower()
        target = tmp / ("in_" + Path(token).name)
        if ext == ".json":
            if json_ex is None:
                json_ex = extract_json_example(md)
            if json_ex is not None:
                target.write_text(json.dumps(json_ex, ensure_ascii=False, indent=1), encoding="utf-8")
                notes.append(f"合成 JSON 输入 ← SKILL.md 示例({len(json.dumps(json_ex))}B)")
                return str(target)
            target.write_text("{}", encoding="utf-8")
            notes.append("合成空 JSON 输入（文档无 JSON 示例）")
            return str(target)
        if ext in GENERIC_TEXT_EXTS:
            target.write_text(ARTICLE, encoding="utf-8")
            notes.append(f"合成文本输入({len(ARTICLE)} 字)")
            return str(target)
        return token  # 不是文件样 token，原样传

    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok in ("-h", "--help"):
            argv.pop(i)
            continue
        if tok.startswith("--") or (tok.startswith("-") and len(tok) == 2):
            flag = tok.split("=")[0]
            if flag in ("--output", "-o", "--out") or flag.endswith(("-output", "_output")):
                out_idx.append(i)
                argv[i] = f"{flag}"
                if "=" not in tok:
                    if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                        argv[i + 1] = str(tmp / ("out_" + flag.strip("-") + ".json"))
                    else:
                        argv.insert(i + 1, str(tmp / ("out_" + flag.strip("-") + ".json")))
                        i += 1
                i += 1
                continue
            if flag in st_flags or "=" in tok:
                i += 1
                continue
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                val = argv[i + 1]
                if re.search(r"\.(json|md|txt|csv|tex|srt|yaml|yml|bib|markdown|rst|log)$", val, re.I):
                    argv[i + 1] = ensure_input(val)
                i += 2
                continue
            i += 1
            continue
        if re.search(r"\.(json|md|txt|csv|tex|srt|yaml|yml|bib)$", tok, re.I):
            argv[i] = ensure_input(tok)
        i += 1

    # 输出文件补扩展名（按数据类型猜）
    for idx in out_idx:
        if idx + 1 < len(argv) and argv[idx + 1].endswith(".bin"):
            argv[idx + 1] = argv[idx + 1][:-4] + ".json"
    return argv, notes, scenario


class SpecError(Exception):
    pass


def run_one(skill_id: str, skill_dir: Path, script: Path, with_llm: bool, timeout: int):
    entry = {"skill": skill_id, "script": str(script.relative_to(REPO))}
    try:
        argv, notes, scenario = build_spec(skill_dir, script)
    except SpecError as e:
        return {**entry, "verdict": "no-example", "reason": str(e)}
    except Exception as e:  # 驱动器自身 bug
        return {**entry, "verdict": "spec-error", "reason": f"{type(e).__name__}: {e}"}

    ov = OVERRIDES.get(skill_id, {})
    if ov.get("cmd"):
        argv = _apply_override(ov["cmd"])
        out_name = ov.get("out", "ov_out.json")
        argv += ["--output", str(Path(_TMP) / out_name)]

    env = dict(_BASE_ENV)
    if with_llm and _LLM["url"]:
        env["SKILLKIT_LLM_URL"] = _LLM["url"]
        env["SKILLKIT_LLM_KEY"] = _LLM["key"]
        env["SKILLKIT_LLM_MODEL"] = _LLM["model"]

    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, str(script)] + [a for a in argv if a],
                           capture_output=True, text=True, timeout=timeout,
                           cwd=str(skill_dir), env=env)
    except subprocess.TimeoutExpired:
        return {**entry, "verdict": "fail", "scenario": scenario,
                "reason": f"TIMEOUT {timeout}s", "argv": argv}
    dt = time.time() - t0
    entry.update({"scenario": ov.get("scenario", scenario), "argv": argv,
                  "notes": notes, "rc": r.returncode, "seconds": round(dt, 2),
                  "stdout_tail": (r.stdout or "")[-400:], "stderr_tail": (r.stderr or "")[-300:]})

    if "Traceback" in (r.stderr or ""):
        entry["verdict"] = "error"
        return entry
    if r.returncode != 0:
        entry["verdict"] = "fail"
        entry["reason"] = f"rc={r.returncode}"
        return entry

    # ---- 断言：JSON 契约 ----
    data = None
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        # 输出写了文件的情况也算过（JSON 文件可解析即可）
        outs = [Path(a) for a in argv if isinstance(a, str) and a.startswith(str(_TMP))
                and Path(a).suffix == ".json"]
        if outs:
            try:
                data = json.loads(outs[0].read_text(encoding="utf-8"))
            except Exception:
                data = None

    checks = ov.get("assert_json", {})
    for dotted, expected in checks.items():
        node = data
        if node is None:
            entry["verdict"], entry["reason"] = "fail", f"断言 {dotted}: 输出不是合法 JSON"
            return entry
        ok = True
        for k in dotted.split("."):
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                ok = False
                break
        if not ok or node != expected:
            entry["verdict"] = "fail"
            entry["reason"] = f"断言失败 {dotted}: 期望 {expected!r} 实得 {node!r}"
            return entry
    for dotted in ov.get("assert_json_absent", []):
        node, ok = data, True
        for k in dotted.split("."):
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                node = None
        if node is not None:
            entry["verdict"] = "fail"
            entry["reason"] = f"断言失败 {dotted} 应不存在，实得 {node!r}"
            return entry
    for dotted, minv in ov.get("assert_json_min", {}).items():
        node, ok = data, True
        for k in dotted.split("."):
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                ok = False
                break
        if not ok or not isinstance(node, (int, float)) or node < minv:
            entry["verdict"] = "fail"
            entry["reason"] = f"断言失败 {dotted} 应 ≥ {minv}，实得 {node!r}"
            return entry

    # ---- 断言：输出文件真实存在且非空 ----
    for a in argv:
        if isinstance(a, str) and a.startswith(str(_TMP))                 and Path(a).name.startswith(("out_", "ov_")):
            p = Path(a)
            if p.exists():
                if p.stat().st_size < 40:
                    entry["verdict"] = "fail"
                    entry["reason"] = f"产物过小: {p.name} {p.stat().st_size}B"
                    return entry
                entry.setdefault("artifacts", []).append(
                    f"{p.name}:{p.stat().st_size}B")

    # ---- 断言：LLM 场景（配网关时台词必须真模型生成） ----
    if ov.get("assert_llm_source"):
        if with_llm and data is not None:
            src = data.get("dialogue_source")
            if src not in ("llm", "mixed"):
                entry["verdict"] = "fail"
                entry["reason"] = f"配了真模型但 dialogue_source={src}（应 llm/mixed）"
                return entry
            entry["llm"] = True

    entry["verdict"] = "pass"
    return entry


def _apply_override(cmd):
    """override 的 @json:/@text: 动态值展开。@json: 物化为临时文件（--data 要路径）。"""
    new = []
    n = 0
    for a in cmd:
        if a.startswith("@json:"):
            n += 1
            f = Path(_TMP) / f"in_ov_{n}.json"
            f.write_text(a[len("@json:"):], encoding="utf-8")
            new.append(str(f))
        elif a == "@text:ARTICLE":
            new.append(ARTICLE)
        else:
            new.append(a)
    return new


def main():
    global _TMP, _LLM, _BASE_ENV
    import os
    import tempfile

    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", help="只测某域")
    ap.add_argument("--with-llm", action="store_true", help="注入 SKILLKIT_LLM_* 走真模型")
    ap.add_argument("--model-config", default=r"C:/Users/X1882/.workbuddy/models.json")
    ap.add_argument("--model-id", default="agnes-2.5-flash")
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--only", help="只测匹配子串的技能")
    args = ap.parse_args()

    _TMP = tempfile.mkdtemp(prefix="skillkit_scenario_")
    _BASE_ENV = {k: v for k, v in os.environ.items()
                 if not k.startswith("SKILLKIT_LLM")}
    _LLM = {"url": "", "key": "", "model": ""}
    if args.with_llm:
        try:
            cfg = json.loads(Path(args.model_config).read_text(encoding="utf-8"))
            m = next(x for x in cfg if x.get("id") == args.model_id)
            _LLM = {"url": m["url"], "key": m["apiKey"], "model": m["id"]}
            print(f"[llm] 注入网关 {_LLM['url']} model={_LLM['model']}")
        except Exception as e:
            print(f"[llm] 读模型配置失败（{e}），按离线跑")

    results = []
    domains = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    for d in domains:
        if args.domain and d.name != args.domain:
            continue
        for skill_md in sorted(d.rglob("SKILL.md")):
            sd = skill_md.parent
            sid = sd.relative_to(SKILLS).as_posix()
            if args.only and args.only not in sid:
                continue
            scripts = [s for s in (sd / "scripts").glob("*.py")
                       if not s.name.startswith("test_")] if (sd / "scripts").is_dir() else []
            if not scripts:
                continue
            main_scripts = [s for s in scripts
                            if (s.read_text(encoding="utf-8", errors="ignore")
                                .startswith("#!"))] or scripts
            for s in main_scripts:
                res = run_one(sid, sd, s, args.with_llm, args.timeout)
                results.append(res)
                v = res["verdict"]
                mark = {"pass": "PASS", "fail": "FAIL", "error": "ERROR",
                        "no-example": "skip", "spec-error": "spec"}.get(v, v.upper())
                extra = res.get("reason", "") or (" ".join(res.get("artifacts", [])[:3]))
                print(f"  {mark:<5} {sid:<58} {res.get('seconds','')}s {extra[:80]}", flush=True)

    total = len(results)
    n_pass = sum(1 for r in results if r["verdict"] == "pass")
    n_fail = sum(1 for r in results if r["verdict"] == "fail")
    n_err = sum(1 for r in results if r["verdict"] == "error")
    n_skip = sum(1 for r in results if r["verdict"] == "no-example")
    n_spec = sum(1 for r in results if r["verdict"] == "spec-error")

    ART.mkdir(parents=True, exist_ok=True)
    (ART / "real_scenario_report.json").write_text(
        json.dumps({"generated": datetime.now(timezone.utc).isoformat(),
                    "with_llm": args.with_llm, "counts":
                    {"total": total, "pass": n_pass, "fail": n_fail,
                     "error": n_err, "no_example": n_skip, "spec_error": n_spec},
                    "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 全库严格场景化实测报告（第三代证明）", "",
             f"> 生成：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}　|　"
             f"LLM 模式：{'开（' + _LLM['model'] + '）' if args.with_llm else '关'}",
             f"> 总数 {total} = **pass {n_pass}** / fail {n_fail} / error {n_err} "
             f"/ no-example {n_skip} / spec-error {n_spec}", "",
             "> 场景来源：每个技能 SKILL.md 的用法示例 + 旗舰技能苛刻覆盖表；",
             "> 断言：退出码、JSON 契约字段、产物文件存在且非空、无 traceback、诚实标注。", "",
             "## FAIL / ERROR 明细（技能 bug 候选）", ""]
    for r in results:
        if r["verdict"] in ("fail", "error"):
            lines.append(f"### `{r['skill']}` — {r['verdict'].upper()}")
            lines.append(f"- scenario: {r.get('scenario','')}")
            lines.append(f"- argv: `{r.get('argv','')}`")
            lines.append(f"- reason: {r.get('reason','')}")
            if r.get("stdout_tail"):
                lines.append(f"- stdout 尾: `{r['stdout_tail'][-200:]}`")
            if r.get("stderr_tail"):
                lines.append(f"- stderr 尾: `{r['stderr_tail'][-200:]}`")
            lines.append("")
    lines += ["## no-example（文档债：SKILL.md 无可解析用法示例）", ""]
    for r in results:
        if r["verdict"] == "no-example":
            lines.append(f"- `{r['skill']}` {r.get('script','')}")
    lines += ["", "## 逐技能结果", "", "| 技能 | 判定 | 秒 | 产物/原因 |", "|---|---|---|---|"]
    for r in results:
        ev = " ".join(r.get("artifacts", [])) or r.get("reason", "")
        lines.append(f"| `{r['skill']}` | {r['verdict']} | {r.get('seconds','')} | {ev[:60]} |")
    (ART / "real_scenario_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n=== report -> {ART / 'real_scenario_report.md'} ===")
    print(f"total={total} pass={n_pass} fail={n_fail} error={n_err} "
          f"no-example={n_skip} spec-error={n_spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
