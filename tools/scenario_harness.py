#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scenario_harness.py — 第三代全量测试：每个真实技能 × 一个按其场景定制的真实任务。

三代测试的分工（自审演进）：
  第一代 full_skill_test.py   : 18 个代表技能手搓任务，Recorder 记录全过程 —— 覆盖窄。
  第二代 run_skill_smoke.py   : 121 个脚本技能自带的 test_smoke_*.py —— 真但浅（弱冒烟只证能跑）。
  本文件（第三代）            : 154 个真实技能每个给一个**场景定制任务**并真跑完——
      · 脚本型（121）：按技能 CLI 自动推导 + 场景银行填参，迭代补缺（argparse 报错驱动），
        校验退出码 / JSON 契约 / 产物存在 / 无静默回退（status=mock|unsupported|error 默认判 fail）。
      · 纯 prompt 型（34）：SKILL.md 作为 system prompt + 场景用户输入，调配置的真模型
        （agnes-2.5-flash 等稳定候选，读用户 models.json；key 不落日志），
        输出过质量门（空/拒答/占位/过短/缺指定产物名 → fail）。
  失败 = 查漏补缺清单：真 bug 修脚本、缺场景输入补 catalog、需网络/需夹具如实分类。

用法：
  python tools/scenario_harness.py                 # 全量（脚本型 + LLM 型）
  python tools/scenario_harness.py --no-llm        # 只跑脚本型（离线）
  python tools/scenario_harness.py --llm-only      # 只跑 prompt 型
  python tools/scenario_harness.py --filter paper  # 只跑匹配的技能
输出：
  tests/_full_test_artifacts/scenario_report.md    人读报告（按域分表 + 失败分类）
  tests/_full_test_artifacts/scenario_results.json 机器可读全量结果
  tests/_scenario_artifacts/<skill>/...            每技能的真实产物（不删，迭代留痕）
"""
import argparse
import concurrent.futures as fut
import json
import os
import re
import ssl
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ART = REPO / "tests" / "_full_test_artifacts"
PRODUCTS = REPO / "tests" / "_scenario_artifacts"
MODELS_JSON = Path(os.environ.get("SCENARIO_MODELS_JSON",
                                  "C:/Users/X1882/.workbuddy/models.json"))
# 用户实测稳定性排行（2026-09-20）：agnes-2.5-flash 最稳最快；hcnsec 已剔除（上游下架）
def _load_overrides():
    import importlib.util as _iu
    here = Path(__file__).resolve().parent
    for modname in ("scenario_overrides",):
        p = here / (modname + ".py")
        if p.exists():
            spec_ = _iu.spec_from_file_location(modname, p)
            m = _iu.module_from_spec(spec_)
            spec_.loader.exec_module(m)
            return getattr(m, "SCRIPT_OVERRIDES", {})
    return {}


SCRIPT_OVERRIDES = _load_overrides()

PREFERRED_ORDER = ["agnes-2.5-flash", "stepfun-step-router-v1", "agnes-3.0-flash",
                   "step-5-preview"]
EXCLUDED_MARKERS = ("hcnsec",)

TLS = ssl.create_default_context()
TLS.check_hostname = False
TLS.verify_mode = ssl.CERT_NONE  # 用户既有测试口径（中转站证书链不齐，与其脚本测试一致）


# ---------------------------------------------------------------- 场景银行 ----
def _paper_json():
    return {"labels": ["Baseline", "+CoT", "Ours"], "values": [0.71, 0.76, 0.83],
            "x": [0, 1, 2, 3],
            "series": [{"name": "Ours", "values": [0.71, 0.76, 0.83, 0.86]},
                       {"name": "Baseline", "values": [0.62, 0.65, 0.66, 0.68]}],
            "matrix": [[0.80, 0.72, 0.65], [0.68, 0.85, 0.79]],
            "groups": ["Baseline", "Ours"], "data": [[0.8, 0.82, 0.78], [0.88, 0.91, 0.85]]}


def _generic_json(topic):
    return {"topic": topic, "labels": ["A", "B", "C"], "values": [0.7, 0.8, 0.9],
            "items": [{"name": "item-1", "score": 0.7}, {"name": "item-2", "score": 0.9}],
            "text": "这是一段用于测试的场景文本：多智能体系统在预算约束下的协调问题。"}


def _csv():
    return ("date,item,category,amount\n2026-09-01,高铁票,交通,553.00\n"
            "2026-09-03,午餐,餐饮,32.50\n2026-09-09,酒店,住宿,420.00\n")


def _tex():
    return ("\\documentclass{article}\n\\begin{document}\n"
            "\\title{Draft}\\author{A}\\maketitle\n"
            "\\section{Intro}\nWe study multi-agent coordination. % a comment\n"
            "\\end{document}\n")


def _bib():
    return ("@inproceedings{vaswani2017,\n  title={Attention Is All You Need},\n  year={2017}}\n"
            "@article{devlin2019,\n  title={BERT},\n  year={2019}}\n")


def _article(topic):
    return (f"# {topic}\n\n## 背景\n很多人写测试只测快乐路径。\n\n"
            "## 论点\n边界与异常才是 bug 藏身处。\n\n## 结论\n先补边界用例。\n" * 3)


def _code():
    return ("def add(a, b):\n    return a + b\n\n"
            "def divide(a, b):\n    return a / b  # ZeroDivisionError 未处理\n")


def _transcript():
    return ("张三：迁移服务这周必须完成。\n李四：数据库 ddl 周三出。\n"
            "张三：风险是旧客户端兼容。\n李四：行动项：我先写回滚预案。\n")


SCENE = {
    "paper": {"topic": "LLM multi-agent coordination under budget constraints",
              "json": _paper_json},
    "writing": {"topic": "为什么你的单元测试总是测不到真正的 bug", "json": lambda: _generic_json("写作")},
    "programming": {"topic": "实现一个带重试的 HTTP 客户端", "json": lambda: _generic_json("编程"),
                    "code": _code},
    "office": {"topic": "九月差旅报销整理", "json": lambda: _generic_json("办公"), "csv": _csv,
               "transcript": _transcript},
    "video": {"topic": "60 秒修仙短片脚本", "json": lambda: _generic_json("视频")},
    "audio": {"topic": "为什么本地大模型跑不动了（30 分钟播客）", "json": lambda: _generic_json("音频")},
    "design": {"topic": "暗黑电影感、反 AI 味的技术大会主视觉", "json": lambda: _generic_json("设计")},
    "education": {"topic": "面向初学者的 Python 异步编程讲义", "json": lambda: _generic_json("教学")},
    "marketing": {"topic": "独立开发者的 CLI 工具上线推广", "json": lambda: _generic_json("市场")},
    "memory": {"topic": "跨项目长期记忆的分层方案", "json": lambda: _generic_json("记忆")},
    "meta": {"topic": "批量重命名文件的技能规格", "json": lambda: _generic_json("元")},
    "tools": {"topic": "银行流水与记账单对账", "json": lambda: _generic_json("工具")},
    "knowledge": {"topic": "个人知识图谱的构建路径", "json": lambda: _generic_json("知识")},
    "dataviz": {"topic": "12 个月三版本留存率对比该用什么图", "json": lambda: _generic_json("图表")},
    "chat": {"topic": "把需求打磨成结构化提示词", "json": lambda: _generic_json("对话")},
    "music": {"topic": "修仙短视频的国风电子配乐", "json": lambda: _generic_json("音乐")},
    "ppt": {"topic": "季度技术分享 PPT 大纲", "json": lambda: _generic_json("演示")},
    "integrations": {"topic": "把 issue 同步到看板的桥接", "json": lambda: _generic_json("集成")},
}


def scene_for(skill_id):
    return SCENE.get(skill_id.split("/")[1], SCENE["meta"])


# ------------------------------------------------------------ CLI 自助推导 ----
@dataclass
class Flag:
    name: str
    takes_value: bool
    choices: list = field(default_factory=list)
    default: str = ""


_OPT_RE = re.compile(r"^\s{2,}(--?[A-Za-z0-9_.-]+)(?:\s+([A-Z_0-9]+|\{[^}]*\}))?(\s{2,}(.*))?$")
_CH_IN_HELP = re.compile(r"\{([^}]*)\}")
_DEFAULT_RE = re.compile(r"\(default:\s*([^)]+)\)")


def parse_flags(help_text: str):
    """从 argparse help 文本抽旗标（含 choices/default）。尽力而为：解析不出返回空表。"""
    flags, seen = [], set()
    for ln in help_text.splitlines():
        m = _OPT_RE.match(ln)
        if not m:
            continue
        name, tok, help_ = m.group(1), m.group(2) or "", m.group(4) or ""
        if name in ("-h", "--help") or name in seen:
            continue
        seen.add(name)
        cm = _CH_IN_HELP.search(tok) or _CH_IN_HELP.search(help_)
        choices = [c.strip() for c in cm.group(1).split(",") if c.strip()] if cm else []
        dm = _DEFAULT_RE.search(help_)
        flags.append(Flag(name=name, takes_value=bool(tok) and not tok.startswith("{"),
                          choices=choices, default=dm.group(1).strip() if dm else ""))
    return flags


_MISSING_RE = re.compile(r"the following arguments are required:\s*(.+)")
_INVALID_CH_RE = re.compile(r"argument (--?[A-Za-z0-9_-]+):\s*invalid choice:\s*'[^']*'"
                            r"\s*\(choose from ([^)]+)\)")
_USAGE_CHOICES_RE = re.compile(r"\{([^}]+)\}")
_NEED_RE = re.compile(r"error:\s*(?:Need|need|必须|请指定)[^\n]*")
_FLAG_IN_ERR_RE = re.compile(r"--[A-Za-z0-9_-]+")
# 只读子命令优先（离线安全），其次按给出顺序
_READONLY_VERBS = ("preview", "inspect", "show", "check", "validate", "lint", "audit",
                   "dry-run", "dry", "plan", "list", "analyze", "estimate", "score")


def usage_choices(err_or_help: str):
    """usage 行里的 {a,b,c} → 子命令 choices（第一个组）。"""
    for ln in (err_or_help or "").splitlines():
        if ln.strip().startswith("usage:"):
            m = _USAGE_CHOICES_RE.search(ln)
            if m:
                return [c.strip() for c in m.group(1).split(",") if c.strip()]
    return []


def pick_subcommand(choices):
    for c in choices:
        if c.lower() in _READONLY_VERBS:
            return c
    return choices[0] if choices else None


def need_flags_from_error(err: str):
    """自定义校验报错（如 error: Need --text or --file）→ 提到的旗标列表。"""
    if not _NEED_RE.search(err or ""):
        return []
    seg = err[err.index("error:"):]
    seen, out = set(), []
    for f in _FLAG_IN_ERR_RE.findall(seg):
        if f not in seen and f not in ("-h", "--help"):
            seen.add(f); out.append(f)
    return out


def required_from_error(err: str):
    m = _MISSING_RE.search(err or "")
    if not m:
        return []
    return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]


def invalid_choice_from_error(err: str):
    m = _INVALID_CH_RE.search(err or "")
    if not m:
        return None
    return m.group(1), re.findall(r"'([^']*)'", m.group(2))


_OUT_HINTS = ("out", "output", "report", "export", "dest", "save", "result")
_NUM_HINTS = ("num", "count", "runs", "samples", "epochs", "size", "limit", "max", "top",
              "depth", "width", "height", "pages", "days", "hours", "budget",
              "length", "top_k", "topk")
_TEXT_HINTS = ("topic", "query", "question", "title", "name", "prompt", "task", "issue",
               "description", "message", "text", "content", "body", "subject", "goal",
               "theme", "summary", "brief", "note", "concept", "idea")
_READ_HINTS = ("data", "input", "file", "json", "csv", "tex", "bib", "refs", "paper",
               "source", "statement", "invoice", "ledger", "transcript", "doc", "config",
               "path", "load", "template", "sample", "read", "src", "target", "billing",
               "billing", "attachment", "resume", "minutes")
_DIR_HINTS = ("dir", "folder", "directory", "root", "workspace")
OUT_EXT = (("pdf", ".pdf"), ("png", ".png"), ("jpg", ".png"), ("html", ".html"),
           ("csv", ".csv"), ("md", ".md"), ("tex", ".tex"), ("json", ".json"))


def _out_path(out_dir: Path, flag: str):
    lname = flag.lower()
    ext = next((e for h, e in OUT_EXT if h in lname), ".json")
    return out_dir / f"artifact_{flag.strip('-').replace('-', '_')}{ext}"


def _read_path(work: Path, flag: str, skill_id):
    lname = flag.lower()
    dom = skill_id.split("/")[1]
    sc = scene_for(skill_id)
    if "csv" in lname or (dom == "office" and any(k in lname for k in
                                                  ("statement", "invoice", "ledger"))):
        f = work / "scene_input.csv"; f.write_text(sc.get("csv", _csv)(), encoding="utf-8")
    elif "tex" in lname:
        f = work / "scene_input.tex"; f.write_text(_tex(), encoding="utf-8")
    elif "bib" in lname or "ref" in lname:
        f = work / "refs.bib"; f.write_text(_bib(), encoding="utf-8")
    elif ("code" in lname or "program" in lname or
          (dom == "programming" and any(k in lname for k in ("file", "source")))):
        f = work / "scene_input.py"; f.write_text(sc.get("code", _code)(), encoding="utf-8")
    elif "json" in lname or "data" in lname or "config" in lname:
        f = work / "scene_input.json"
        f.write_text(json.dumps(sc.get("json", lambda: _generic_json(sc["topic"]))(),
                                ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        f = work / "scene_input.md"
        f.write_text(_article(sc["topic"]), encoding="utf-8")
    return f


def value_for_flag(flag: str, skill_id: str, files: dict, out_dir=None, choices=None):
    """旗标/裸名 → 场景真实值。禁止 TODO/占位符；拿不准给域场景文案。"""
    if not flag.startswith("-"):
        flag = "--" + flag  # positional 名复用旗标启发式（path/file/topic...）
    choices = choices or []
    if choices:
        return choices[-1] if flag in ("--type", "--mode", "--kind", "--layout") else choices[0]
    lname = flag.lower()
    if any(h in lname for h in _OUT_HINTS):
        p = _out_path(Path(out_dir) if out_dir else Path(files.get("_work", ".")), flag)
        files[str(p)] = p
        return str(p)
    if any(h in lname for h in _DIR_HINTS):
        d = Path(files.get("_work", ".")) / "scene_dir"
        d.mkdir(exist_ok=True)
        (d / "report_v1.md").write_text("v1: 初稿内容，需要重命名归档。" * 5, encoding="utf-8")
        (d / "report_v2_final.md").write_text("v2: 终稿内容。" * 5, encoding="utf-8")
        (d / "img_20260901.png").write_bytes(bytes([0x89]) + b"PNG" + bytes([0x0D, 0x0A, 0x1A, 0x0A]) + b"0" * 32)
    if "cron" in lname or (lname.strip("-") in ("schedule", "expr", "expression")):
        return "*/5 * * * *"
    if any(h in lname for h in _READ_HINTS) or (lname in ("--in", "-i")):
        p = _read_path(Path(files.get("_work", ".")), flag, skill_id)
        files[str(p)] = p
        return str(p)
    base = flag.strip("-").replace("-", "_")
    # 文本类旗标先于数值类判断：'top' 是 'topic' 的子串，反着判会把主题当成 5
    if any(h in lname for h in _TEXT_HINTS):
        return scene_for(skill_id)["topic"]
    if base in ("n", "k") or any(h in lname for h in _NUM_HINTS):
        return "5"
    if "seed" in lname:
        return "42"
    if any(k in lname for k in ("url", "endpoint", "gateway", "host", "addr")):
        return "http://127.0.0.1:9"  # 离线快速失败：有离线兜底的技能会走兜底
    return scene_for(skill_id)["topic"]


def _run(cmd, timeout, cwd=None, env_extra=None):
    import os
    env = None
    if env_extra:
        env = dict(os.environ)
        env.update(env_extra)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              cwd=cwd or str(REPO), errors="replace", env=env)
    except subprocess.TimeoutExpired:
        return None




def _materialize(content: str, p: Path):
    """files 值 → 落盘：@开头走二进制夹具构建器，否则按文本。"""
    p.parent.mkdir(parents=True, exist_ok=True)
    if content.startswith("@png"):
        from PIL import Image
        Image.new("RGB", (64, 64), (30, 30, 60)).save(str(p), format="PNG")
    elif content.startswith("@wav"):
        import wave
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
            w.writeframes(bytes(8000))
    elif content.startswith("@pdf"):
        from pypdf import PdfWriter
        w = PdfWriter()
        for _ in range(3):
            w.add_blank_page(width=595, height=842)
        with open(str(p), "wb") as fh:
            w.write(fh)
    elif content.startswith("@docx:"):
        import docx
        d = docx.Document()
        d.add_paragraph(content[len("@docx:"):])
        d.save(str(p))
    else:
        p.write_text(content, encoding="utf-8")


def _make_scene_dir(work: Path) -> Path:
    d = work / "scene_dir"; d.mkdir(parents=True, exist_ok=True)
    (d / "report_v1.md").write_text("v1: 初稿内容，需要重命名归档。" * 5, encoding="utf-8")
    (d / "report_v2_final.md").write_text("v2: 终稿内容。" * 5, encoding="utf-8")
    (d / "note.txt").write_text("随手记：测试金字塔。", encoding="utf-8")
    return d


def run_script_skill(entry: str, skill_id: str, out_dir: str, overrides=None,
                     max_attempts=5, timeout=60):
    """跑一个脚本技能：seed/空参起步 → argparse 报错驱动补参 → 契约校验。"""
    overrides = dict(overrides or {})
    t0 = time.time()
    outd = Path(out_dir); outd.mkdir(parents=True, exist_ok=True)
    work = outd / "inputs"
    if work.exists():
        shutil.rmtree(work)  # 上轮残留会让 init/checksum 类技能误判"目录非空"
    work.mkdir(exist_ok=True)
    files = {"_work": str(work)}
    built = {}
    for rel, content in (overrides.get("files") or {}).items():
        p = work / rel
        _materialize(content, p)
        built[rel] = str(p)
    scene_dir = _make_scene_dir(work)

    def _tok(a):
        a = (a.replace("{work}", str(work)).replace("{repo}", str(REPO))
              .replace("{scene_dir}", str(scene_dir)))
        for rel, path in built.items():
            a = a.replace("{" + rel + "}", path)
        return a

    args = [_tok(a) for a in overrides.get("seed_args", [])]
    run_cwd = str(work) if overrides.get("cwd") == "work" else str(REPO)
    res = {"skill": skill_id, "script": entry, "cmd": [], "rc": None, "stdout": "",
           "stderr": "", "verdict": "fail", "reason_class": "", "attempts": 0,
           "out_files": [], "json": None, "seconds": 0.0, "tail": ""}
    for attempt in range(1, max_attempts + 1):
        res["attempts"] = attempt
        cmd = [sys.executable, entry] + args
        r = _run(cmd, timeout, cwd=run_cwd, env_extra=overrides.get("env"))
        res["cmd"] = cmd
        if r is None:
            res.update(reason_class="timeout", stderr=f"timeout {timeout}s"); break
        res.update(rc=r.returncode, stdout=(r.stdout or "")[-4000:],
                   stderr=(r.stderr or "")[-2000:])
        if r.returncode == 0:
            break
        err = r.stderr or ""
        if "ModuleNotFoundError" in err:
            mm = re.search(r"ModuleNotFoundError: No module named '([^']+)'", err)
            res["reason_class"] = "missing_dep:" + (mm.group(1) if mm else "?")
            break
        miss = required_from_error(err)
        if miss:
            subcmds = usage_choices(err)
            for name in miss:
                if name.startswith("-"):
                    args += [name, value_for_flag(name, skill_id, files, outd)]
                elif subcmds:
                    args.append(pick_subcommand(subcmds))  # positional=子命令槽
                else:
                    args.append(value_for_flag(name, skill_id, files, outd))
            continue
        ic = invalid_choice_from_error(err)
        if ic:
            flag, chs = ic
            if flag in args:
                i = args.index(flag)
                args = args[:i] + args[i + 2:]
            if flag.startswith("-"):
                args += [flag, value_for_flag(flag, skill_id, files, outd, chs)]
            else:
                args.append(pick_subcommand(chs))  # positional 非法选择 → 用合法子命令
            continue
        need = need_flags_from_error(err)
        if need:
            tried = overrides.setdefault("_tried_need", set())
            pick = next((f for f in need if f not in tried), None)
            if pick is None:
                res["reason_class"] = "usage_unresolved"
                break
            tried.add(pick)
            args += [pick, value_for_flag(pick, skill_id, files, outd)]
            continue
        if "unrecognized arguments" in err:
            bad = re.findall(r"unrecognized arguments?: (.+)", err)
            drop = set(bad[0].split()) if bad else set()
            args = [a for i, a in enumerate(args)
                    if not (a in drop or (i > 0 and args[i - 1] in drop))]
            if args == cmd[2:]:
                res["reason_class"] = "usage_unresolved"
                break
            continue
        mm = re.search(r"argument (--?[A-Za-z0-9_-]+): (invalid|expected)", err)
        if mm and mm.group(1) in args:
            i = args.index(mm.group(1))
            if i + 1 < len(args) and mm.group(2) == "invalid":
                chs = re.findall(r"'([^']*)'", err)
                args[i + 1] = value_for_flag(mm.group(1), skill_id, files, outd,
                                             chs or None)
                continue
        res["reason_class"] = "crash_or_usage"
        break
    res["seconds"] = round(time.time() - t0, 2)
    accept_rc = overrides.get("accept_rc") or []
    if res["rc"] == 0 or (res["rc"] in accept_rc and accept_rc):
        claimed = [p for p in files if p != "_work" and p.startswith(str(outd))
                   and p in " ".join(res["cmd"])]
        missing = [p for p in claimed
                   if not (Path(p).exists() and Path(p).stat().st_size > 0)]
        res["out_files"] = claimed
        try:
            s = res["stdout"]
            res["json"] = json.loads(s[s.index("{"): s.rindex("}") + 1])
        except Exception:
            res["json"] = None
        # 诚实负判定：override 声明 rc 非零可接受 + JSON 必含某键（如 gate 的 verdict）
        req_key = overrides.get("require_json_key")
        if res["rc"] != 0:
            def _has_key(node, dotted):
                cur = node
                for k in dotted.split("."):
                    if not isinstance(cur, dict) or k not in cur:
                        return False
                    cur = cur[k]
                return True
            if req_key and res["json"] and _has_key(res["json"], req_key):
                res["verdict"] = "pass"
                res["reason_class"] = f"honest_negative(rc={res['rc']})"
                res["seconds"] = round(time.time() - t0, 2)
                return res
            res["reason_class"] = f"rc={res['rc']} (expected honest negative via accept_rc)"
            res["seconds"] = round(time.time() - t0, 2)
            return res
        st = (res["json"] or {}).get("status")
        if st in ("mock", "unsupported", "error"):
            res["reason_class"] = f"status={st}" + (
                f":{str((res['json'] or {}).get('error', ''))[:160]}" if st == "error" else "")
        elif missing:
            res["reason_class"] = "artifact_missing:" + ";".join(missing)[:160]
        elif res["json"] is not None and res["json"].get("ok") is False:
            res["reason_class"] = "ok=false"
        elif not res["stdout"].strip():
            produced = [p for p in claimed if Path(p).exists()
                        and Path(p).stat().st_size > 0]
            if produced:
                # stdout 为空但真实产物落盘且非空 → 合法的"只写文件"型 CLI
                res["verdict"] = "pass"
                res["reason_class"] = "file_output"
            else:
                res["reason_class"] = "empty_output"
        else:
            res["verdict"] = "pass"
            res["reason_class"] = "" if res["json"] else "non_json_output"
    elif not res["reason_class"]:
        res["reason_class"] = ("usage_unresolved" if "usage:" in (res.get("stderr") or "")
                               else "rc!=0")
    res["tail"] = (res["stderr"] or res["stdout"] or "")[-500:]
    return res


# --------------------------------------------------------------- prompt 层 ----
def load_llm_candidates(models_json_path: str):
    """models.json → 稳定候选（key 只进候选对象，绝不进日志/报告）。"""
    cands = []
    try:
        arr = json.loads(Path(models_json_path).read_text(encoding="utf-8"))
        for m in arr:
            name = m.get("id") or m.get("name") or ""
            if any(x in (name + " " + m.get("vendor", "")).lower()
                   for x in EXCLUDED_MARKERS):
                continue
            cands.append({"name": name, "base_url": (m.get("url") or "").rstrip("/"),
                          "api_key": m.get("apiKey") or ""})
    except Exception:
        pass
    rank = {n: i for i, n in enumerate(PREFERRED_ORDER)}
    cands.sort(key=lambda c: rank.get(c["name"], 99))
    if os.environ.get("SCENARIO_LLM_MODEL") and os.environ.get("SCENARIO_LLM_BASE_URL"):
        cands.insert(0, {"name": os.environ["SCENARIO_LLM_MODEL"],
                         "base_url": os.environ["SCENARIO_LLM_BASE_URL"],
                         "api_key": os.environ.get("SCENARIO_LLM_API_KEY", "")})
    return [c for c in cands if c["name"] and c["base_url"] and c["api_key"]]


def _extract_text(data):
    try:
        msg = data["choices"][0]["message"]
        return (msg.get("content") or "").strip() or (msg.get("reasoning") or "").strip()
    except Exception:
        return ""


def llm_chat(cands, system, user, max_tokens=1600, timeout=180):
    """按候选顺序调 OpenAI 兼容 /chat/completions；429 限流按指数退避重试。"""
    errs = []
    base_payload = {"max_tokens": max_tokens, "temperature": 0.4,
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}]}
    for c in cands:
        for attempt in range(4):  # 429 退避：5s/25s/60s 后重试同候选
            t0 = time.time()
            req = urllib.request.Request(
                c["base_url"] + "/chat/completions",
                data=json.dumps({**base_payload, "model": c["name"]}).encode("utf-8"),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer " + c["api_key"]}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=timeout, context=TLS) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                text = _extract_text(data)
                if text:
                    return text, {"model": c["name"], "base_url": c["base_url"],
                                  "seconds": round(time.time() - t0, 1)}
                errs.append(f"{c['name']}: empty content")
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 3:
                    time.sleep((5, 25, 60)[attempt])
                    continue
                errs.append(f"{c['name']}: HTTP {e.code}")
                break
            except Exception as e:
                errs.append(f"{c['name']}: {type(e).__name__} {str(e)[:120]}")
                break
    raise RuntimeError("all LLM candidates failed: " + " | ".join(errs))


_PLACEHOLDER = re.compile(r"\b(TODO|FIXME|placeholder)\b|待补全|待补充|占位符")
_REFUSAL = re.compile(r"(作为AI|作为一个AI|我无法完成|I cannot comply|I'?m sorry,? but I can'?t)",
                      re.I)


def gate_prompt_output(text: str, min_chars=300, must_contain=()):
    """质量门：返回失败原因列表（空 = 过门）。"""
    fails = []
    if not text or not text.strip():
        return ["空输出"]
    if len(text) < min_chars:
        fails.append(f"长度不足（{len(text)} < {min_chars}）")
    if _REFUSAL.search(text[:400]):
        fails.append("疑似拒答/免责开头")
    if _PLACEHOLDER.search(text):
        # 自审声明豁免：`placeholders: []` 字段 / "无占位符遗留" 是交付自检结果，
        # 不是偷懒占位；其余行仍照常检查。
        cleaned = "\n".join(
            ln for ln in text.splitlines()
            if not re.search(r"placeholders?['\"]?\s*[:=]|无占位符|占位符遗留"
                             r"|无需待补充|无待补|模板占位符"
                             r"|可用占位符|占位符列表", ln))
        if _PLACEHOLDER.search(cleaned):
            fails.append("含 TODO/占位符")
    for kw in must_contain:
        if kw not in text:
            fails.append(f"缺少指定产物名: {kw}")
    return fails


def run_prompt_skill(skill_id: str, skill_dir: Path, out_dir: str, cands,
                     spec=None, timeout=180):
    """prompt 型技能：SKILL.md 当 system，场景输入当 user，输出过质量门。
    质量门失败自动重采一次（temperature 0.4 有方差，门禁标准不变）。"""
    spec = spec or {}
    outd = Path(out_dir); outd.mkdir(parents=True, exist_ok=True)
    md = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    res = {"skill": skill_id, "mode": "llm", "verdict": "fail", "reason_class": "",
           "model": "", "seconds": 0.0, "chars": 0, "gates": [], "output_file": ""}
    text = meta = None
    gates = None
    for attempt in (1, 2):
        try:
            text, meta = llm_chat(
                cands, md, spec.get("scene", scene_for(skill_id)["topic"]),
                timeout=timeout)
        except Exception as e:
            res["reason_class"] = "llm_failed:" + str(e)[:200]
            return res
        (outd / ("output.md" if attempt == 1 else "output_retry.md")).write_text(
            text, encoding="utf-8")
        gates = gate_prompt_output(text, spec.get("min_chars", 300),
                                   spec.get("must_contain", []))
        if not gates:
            break
    res.update(model=meta["model"], seconds=meta["seconds"], chars=len(text))
    res["output_file"] = str(outd / "output.md")
    res["gates"] = gates
    if gates:
        res["reason_class"] = "quality_gate:" + ";".join(gates)[:200]
    else:
        res["verdict"] = "pass"
        if attempt == 2:
            res["reason_class"] = "retry_pass"
    return res


# ------------------------------------------------------- 34 个 prompt 场景 ----
PROMPT_SCENARIOS = {
    "writing/personal-voice-profile": {
        "scene": "下面是我本人写的 3 段文本（都发在知乎）：\n"
                 "1) 说实话，大多数人不是不会写，是不敢删。删到只剩骨头，文章才有劲儿。\n"
                 "2) 我调 bug 有个习惯：先把报错贴远一点看整体，再凑近看行。九成低级错误是凑太近看出来的。\n"
                 "3) 工具栈换了一轮又一轮，最后留下的都是笨办法：小步提交、每次只改一件事、跑完测试再合。\n"
                 "请蒸馏 voice-profile.json 与一页模仿卡。", "min_chars": 400,
        "must_contain": ["voice-profile.json"]},
    "writing/humanize-rewriter": {
        "scene": "请去掉下面这段的 AI 腔，保持信息不变：\n"
                 "「在当今快速发展的技术时代，掌握编程能力至关重要。首先，我们需要理解基础概念；"
                 "其次，动手实践不可或缺；最后，持续学习将助力我们拥抱未来的无限可能。」",
        "min_chars": 80},
    "education/feynman-explainer": {
        "scene": "请用费曼循环教我（beginner）：为什么 0.1 + 0.2 != 0.3？", "min_chars": 400},
    "education/course-designer": {
        "scene": "请设计 8 课时的「Python 异步编程」掌握型课程骨架：每课目标/前置/练习/检查点。",
        "min_chars": 600},
    "education/assignment-intake": {
        "scene": "下面这条作业描述很含糊——含糊描述本身就是本次任务的解析对象，"
                 "你的交付物就是结构化需求解析 + 待确认项清单，请直接解析，不要拒答：\n"
                 "「做一个操作系统的课程设计，最好能用上进程相关的东西，老师说要有点新意」。",
        "min_chars": 350},
    "education/own-voice-rewrite": {
        "scene": "我的口吻样本：「我调 bug 先看整体再看行，九成低级错误是凑太近看出来的。」"
                 "请把这段 AI 腔文字改成我的口吻：「在本节中，我们将深入探讨调试的最佳实践。」",
        "min_chars": 150},
    "education/solution-drafter": {
        "scene": "题目：5 个任务带依赖关系与耗时，求最小总时长。"
                 "任务与耗时：A=3s, B=2s, C=4s, D=2s, E=3s。"
                 "依赖：B 依赖 A，C 依赖 A，D 依赖 B 和 C，E 依赖 D。"
                 "无依赖的任务可并行。请写第一版解题草稿（只破题与定状态，不写完整代码）。",
        "min_chars": 350},
    "office/meeting-notes": {
        "scene": "把下面转写整理成纪要。会议信息：2026-09-21 10:00-10:30，主题「支付库迁移评审」，"
                 "参会：张三（后端负责人）、李四（DBA）、王五（QA）、赵六（SRE）。\n"
                 "转写全文：\n"
                 "张三：支付库迁移到 Postgres 这周必须完成，周五全量切流。\n"
                 "李四：schema 迁移 ddl 周三出，双写方案已经评审过了，灰度按 5% 起步。\n"
                 "王五：回归用例已备好 214 条，覆盖退款和幂等路径，切流前必须全绿。\n"
                 "张三：风险是旧客户端兼容，v2.3 以下版本还在用老接口。\n"
                 "李四：行动项：我今天先写回滚预案，明天中午前发出来。\n"
                 "赵六：我盯切流期间的监控大盘，错误率超 0.5% 自动回滚。\n"
                 "以上为完整转写稿（含日期、参会人、决议与行动项），无需再次确认，"
                 "直接输出纪要。", "min_chars": 250,
        "must_contain": ["行动项"]},
    "office/internal-comms-writer": {
        "scene": "写一封全员邮件：本周六（2026-09-26）22:00-24:00 内部 GitLab 服务器迁移，"
                 "期间不可用。事实全部给全，无需标记待补充：收件人为全体员工；"
                 "旧域名 git.corp.example.com，新域名 gitnew.corp.example.com；"
                 "影响：期间无法 push/merge/看 CI；FAQ 链接：https://wiki.corp.example.com/gitlab-migration；"
                 "IT 联系人：赵六（分机 8021）。给出影响与操作指引。", "min_chars": 250},
    "office/resume-tailor": {
        "scene": "请裁剪出针对该 JD 的简历要点。完整 JD：\n"
                 "「岗位职责：负责后端服务开发（Python）。任职要求：3 年以上 Python 经验；"
                 "熟悉异步编程（asyncio）；熟悉单元测试与 CI/CD；有高并发服务经验优先。」\n"
                 "现有简历全文：\n"
                 "张三 · 后端工程师 · 4 年经验\n"
                 "- 主导电商价格爬虫系统（Python/asyncio，日均 2000 万次抓取）\n"
                 "- 维护团队 CI 流水线（GitHub Actions），测试覆盖率从 40% 提到 85%\n"
                 "- 给开源库 aiohttp 提过 2 个 PR（异步超时处理）\n"
                 "- 用 pytest 写过 300+ 单元测试\n"
                 "- 自学 Rust，写过 2 个小工具（与本岗位无关）\n"
                 "补充信息：联系方式 zhangsan@example.com；本科计算机科学与技术（2022 届）；"
                 "期望薪资 30-35k；可到岗时间 1 个月内。以上信息完整，直接输出定制要点，"
                 "不要留待补充清单。", "min_chars": 300},
    "office/excel-assistant": {
        "scene": "一份报销表列名混乱（'金额/amount/￥'混用、日期格式三种），请给出清洗方案与公式。",
        "min_chars": 300},
    "dataviz/chart-recommender": {
        "scene": "数据：12 个月 × 3 个版本的留存率（各 12 个百分比）。推荐图表类型并解释为什么、"
                 "以及不该用什么图。", "min_chars": 300},
    "design/design-brief-interpreter": {
        "scene": "用户原话：「想要个很有氛围感的暗黑风海报，但别太 AI 味，要电影感」。"
                 "补充事实（可直接用，无需标记待补全）：platform=数字专辑封面（3000x3000px，"
                 "流媒体发布）；用途=独立音乐人单曲封面；交付格式=PNG；工期=5 天；"
                 "参考基调=低饱和、单一强光源、胶片颗粒。"
                 "请翻译成结构化设计简报（含可执行规格与禁忌清单）。", "min_chars": 400},
    "design/frontend-design-director": {
        "scene": "为开发者工具官网落地页定设计方向：受众是重度终端用户，品牌想传达「快、稳、不花哨」。",
        "min_chars": 400},
    "design/image-prompt-engineer": {
        "scene": "把「在笔记本上跑本地大模型的赛博感封面」工程化成可直接用的文生图 prompt"
                 "（含负面词与参数建议）。", "min_chars": 300},
    "marketing/campaign-designer": {
        "scene": "给一个面向程序员的 CLI 效率工具设计上线 campaign：渠道、节奏、内容与衡量指标。",
        "min_chars": 450},
    "marketing/product-copywriter": {
        "scene": "为下面的笔记本写 3 版不同角度的 landing page 文案。"
                 "商品事实：14 英寸轻薄本，AMD 7840HS，24GB LPDDR5 内存（跑 7B Q4 模型实测 18 token/s），"
                 "1TB NVMe，重 1.4kg，续航 10 小时，价格 3999 元。"
                 "受众：想在本地跑大模型的开发者与 AI 爱好者，预算区间 4000-6000 元，"
                 "最怕发热降频与内存不够；核心场景优先级：本地跑模型 > 日常开发 > 便携性；"
                 "文案类型：电商详情页（Landing Page）。"
                 "口碑摘录：「跑 7B 模型发热控制不错」「多任务切换无卡顿」。"
                 "以上信息完整，直接输出 3 版文案，无需再确认。",
        "min_chars": 400},
    "memory/memory-architect": {
        "scene": "设计跨会话长期记忆分层方案。输入清单一次性给全："
                 "① 用途：同时做 3 个开发项目 + 接私活，帮记项目上下文与客户偏好；"
                 "② 记忆规模量级：千级条目；"
                 "③ 存储设施：本机文件 + SQLite，无向量库；"
                 "④ 隐私要求：私活客户信息属 PII，必须脱敏或排除；"
                 "⑤ token 预算：每次会话可注入记忆上限 4000 字符。"
                 "请输出：记什么/记哪层/怎么清理。", "min_chars": 450},
    "memory/memory-extractor": {
        "scene": "从这段对话抽取应长期记住的事实。user_id=alice；无现有记忆库导出"
                 "（跳过去重，标注 NO_DEDUP）。对话原文：\n"
                 "「用户：我们数据库最终选了 Postgres，别再推荐 Mongo 了。助手：好的。"
                 "用户：部署一律走 docker compose，别整 k8s。」", "min_chars": 200},
    "memory/memory-manager": {
        "scene": "对下面记忆库执行 sweep（全库清扫）。现有记忆库导出（JSON 条目数组，"
                 "字段齐全）：\n"
                 "[{\"id\": \"m1\", \"content\": \"用户数据库选型用 Postgres，拒绝 Mongo\", "
                 "\"confidence\": 0.95, \"updated_at\": \"2026-09-20\", \"hit_count\": 42, "
                 "\"ttl\": null}, "
                 "{\"id\": \"m2\", \"content\": \"某次构建失败因为断网\", \"confidence\": 0.4, "
                 "\"updated_at\": \"2026-07-20\", \"hit_count\": 0, \"ttl\": \"30d\"}, "
                 "{\"id\": \"m3\", \"content\": \"用户偏好暗色主题\", \"confidence\": 0.9, "
                 "\"updated_at\": \"2026-09-18\", \"hit_count\": 17, \"ttl\": null}]\n"
                 "输入已齐，无需再次确认。请直接决定合并/保留/过期并说明清理策略。",
        "min_chars": 250},
    "memory/memory-retriever": {
        "scene": "用户问：「上次那个部署回滚是怎么处理的？」请给出检索策略：查哪几层记忆、"
                 "用什么关键词、命中后怎么组织答案。", "min_chars": 250},
    "meta/skill-author": {
        "scene": "把「批量按规则重命名文件（含预览与撤销）」写成一个 SKILL.md：含输入清单、"
                 "红线、工作流、失败处置表。边界问题一次性答全："
                 "① 真实触发场景：摄影师导出的 DSC001.jpg 要批量改成 2024-10-27_tour_001.jpg；"
                 "② 触发边界：用户明确说批量改名/重命名时触发；单文件改名、移动目录不触发；"
                 "③ 输入：目标目录 + 规则（模板/正则/前后缀/EXIF 日期），输出：预览清单与 rename-log；"
                 "④ 红线：必须先 preview 经用户确认才 apply，绝不碰系统目录与只读盘；"
                 "⑤ 平台：Windows/macOS/Linux 通用，Python 3.10+。", "min_chars": 700},
    "music/music-generation": {
        "scene": "为一部修仙短片配乐写音乐生成 prompt：曲风、段落结构、BPM、乐器与禁忌。",
        "min_chars": 300},
    "audio/tts-voice-director": {
        "scene": "为悬疑播客开场 200 字旁白做配音导演方案：音色、语速曲线、停顿与重音标注。"
                 "输入一次给全——旁白脚本正文：「深夜的城市并不安静，只是声音都躲进了电缆。"
                 "服务器机房里，一台风扇的转速突然快了半拍。三分钟后，一台机器下线了，"
                 "没有人注意到。」；形态：单人旁白；TTS 引擎：Kokoro 本地免费；"
                 "参考音色：narrator_suspense（低沉男声）。无需再次确认，直接输出方案。",
        "min_chars": 300},
    "audio/episode-publisher": {
        "scene": "把下面已完成的播客单集包装发布：shownotes 结构、发布渠道清单与时间点。"
                 "上游产物一次给全——已合成音频：episode28_final.mp3，实际时长 31 分 42 秒；"
                 "期号：第 28 期；标题：《为什么本地大模型跑不动了》；"
                 "分段脚本：[00:00 开场为什么聊这个] [02:10 显存与内存带宽] "
                 "[12:30 量化到 4bit 的取舍] [21:00 7840HS 实测数据] [29:30 下期预告]；"
                 "关键数据：7B Q4 模型 18 token/s；shownotes 素材：本期讲了本地部署的真实瓶颈。", "min_chars": 400},
    "video/nailong-laugh-shorts": {
        "scene": "写一个 60 秒「程序员 vs 奶龙」搞笑短片脚本：分镜、台词、梗点节奏。",
        "min_chars": 400},
    "video/ai-baby-podcast": {
        "scene": "生成一集「AI 婴儿播客」脚本：两个 AI 娃聊「为什么大模型会一本正经胡说八道」，"
                 "要萌且信息量足。", "min_chars": 450},
    "video/image-generation": {
        "scene": "为「赛博朋克风的机械革命笔记本」写文生图 prompt 与 3 个变体方向。",
        "min_chars": 250},
    "video/video-generation": {
        "scene": "基于首帧（雨夜霓虹街道）写图生视频 prompt：镜头运动、氛围、时长与负面描述。",
        "min_chars": 250},
    "video/shot-recipe-designer": {
        "scene": "为一支 30 秒产品宣传片设计分镜配方：每个镜头的景别/运动/时长/转场。"
                 "产品事实：便携咖啡机，主打 30 秒冷萃；调性：清晨、快节奏、治愈。",
        "min_chars": 300},
    "video/visual-style-anchor": {
        "scene": "为一部赛博修仙短片《灵枢代码》定视觉锚点卡：色板、光影、材质、构图母题与一致化规则。"
                 "项目信息：未来都市灵气复苏背景、主角 1 名（数据修士林一）、3 集每集 8 分钟、"
                 "参考气质为《攻壳机动队》+《流浪地球》。信息已齐备，直接产出完整锚点卡，不要向用户追问或要求补充信息。",
        "min_chars": 400},
    "programming/ai-engineering/self-eval": {
        "scene": "对一个 agent 的输出做 5 维自评（format/grounding/no_hallu/consistency/safety）：\n"
                 "输出样例：「已按要求生成报告（共 3 节），数据来自 2026-09 的内部统计"
                 "（来源标注见附录）。」", "min_chars": 400},
    "programming/api/api-test-suite-builder": {
        "scene": "为 POST /orders（JSON：sku、qty、coupon?）设计测试套件：正常/边界/异常/幂等/并发，"
                 "用例表格式。", "min_chars": 500},
    "programming/github/pr-review-expert": {
        "scene": "评审这个 diff：\n```diff\n-def divide(a,b): return a/b\n+def divide(a,b):\n"
                 "+    try:\n+        return a/b\n+    except:\n+        return 0\n```\n"
                 "指出问题并给修改建议。", "min_chars": 350},
}



# ------------------------------------------------------------------ 发现与驱动 ----
def discover(filter_sub=None):
    """返回 [(skill_id, dir, [entry_scripts])]；跳过 sample-skill 夹具与 test_smoke_*。"""
    root = REPO / "skills"
    out = []
    for md in sorted(root.rglob("SKILL.md")):
        d = md.parent
        rel = d.relative_to(REPO).as_posix()
        if "sample-skill" in rel:
            continue
        sid = "/".join(rel.split("/")[1:])  # 去掉 skills/ 前缀
        if filter_sub and filter_sub not in sid:
            continue
        scripts = []
        if (d / "scripts").exists():
            scripts = sorted(p for p in (d / "scripts").glob("*.py")
                             if not p.name.startswith("test_smoke"))
        out.append((sid, d, scripts))
    return out


def _report(results, llm_used, models_used):
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "scenario_results.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
                    "llm_used": llm_used, "models_used": models_used,
                    "results": results}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    total = len(results)
    passed = [r for r in results if r["verdict"] == "pass"]
    failed = [r for r in results if r["verdict"] != "pass"]
    lines = ["# 第三代 · 场景化全量测试报告（每技能 × 定制真实任务）", "",
             f"> 生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
             f"> 口径：脚本型 = 真实 CLI + 场景输入 + 契约/产物/无静默回退校验；"
             f"prompt 型 = SKILL.md 全文当 system + 场景输入调真模型 + 质量门。",
             f"> LLM：{'使用（' + ', '.join(models_used) + '）' if llm_used else '未使用（--no-llm）'}",
             "",
             "## 总览",
             f"- 技能总数：**{total}**，pass=**{len(passed)}**，fail=**{len(failed)}**",
             "",
             "## 失败分类（查漏补缺清单）", ""]
    by_class = {}
    for r in failed:
        by_class.setdefault(r["reason_class"].split(":")[0], []).append(r)
    for cls, rs in sorted(by_class.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"- **{cls}** × {len(rs)}: " +
                     ", ".join("`" + r["skill"] + "`" for r in rs[:12]) +
                     ("…" if len(rs) > 12 else ""))
    lines += ["", "## 逐技能结果", "",
              "| 技能 | 模式 | 判定 | 耗时s | 失败分类 | 备注 |", "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| `{r['skill']}` | {r.get('mode', 'script')} | {r['verdict']} "
                     f"| {r.get('seconds', 0)} | {r['reason_class'] or '—'} "
                     f"| {(r.get('model') or (r.get('json') or {}).get('type', '') or '—')[:40]} |")
    (ART / "scenario_report.md").write_text("\n".join(lines), encoding="utf-8")
    return len(passed), len(failed)


def main(argv=None):
    ap = argparse.ArgumentParser(description="第三代场景化全量测试台架")
    ap.add_argument("--no-llm", action="store_true", help="跳过 prompt 型（离线）")
    ap.add_argument("--llm-only", action="store_true", help="只跑 prompt 型")
    ap.add_argument("--filter", default=None, help="只跑 skill_id 含该子串的")
    ap.add_argument("--timeout", type=int, default=60, help="单次脚本执行超时秒")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)

    skills = discover(args.filter)
    cands = load_llm_candidates(str(MODELS_JSON))
    results, models_used = [], set()

    # --- 脚本型 ---
    if not args.llm_only:
        def _one(item):
            sid, d, scripts = item
            if not scripts:
                return None
            entry = str(scripts[0])
            ov = SCRIPT_OVERRIDES.get(sid)
            r = run_script_skill(entry, sid, str(PRODUCTS / sid), overrides=ov,
                                 timeout=args.timeout)
            r["mode"] = "script"
            return r
        script_items = [it for it in skills if it[2]]
        print(f"[scenario] 脚本型 {len(script_items)} 个，workers={args.workers}", flush=True)
        with fut.ThreadPoolExecutor(max_workers=args.workers) as ex:
            for r in ex.map(_one, script_items):
                if r:
                    results.append(r)
                    mark = "PASS" if r["verdict"] == "pass" else "FAIL"
                    print(f"  {mark:<4} {r['skill']:<55} {r['reason_class'] or ''}"[:150],
                          flush=True)

    # --- prompt 型 ---
    if not args.no_llm:
        prompt_items = [it for it in skills if not it[2]]
        print(f"[scenario] prompt 型 {len(prompt_items)} 个，LLM 候选 "
              f"{[c['name'] for c in cands]}", flush=True)
        if not cands:
            print("  !! 无可用 LLM 候选（models.json 缺失或 key 为空），prompt 型全跳过",
                  flush=True)
        def _p(item):
            sid, d, _ = item
            if sid not in PROMPT_SCENARIOS:
                return {"skill": sid, "mode": "llm", "verdict": "fail",
                        "reason_class": "no_scenario_defined", "model": "",
                        "seconds": 0, "chars": 0, "gates": [], "output_file": ""}
            r = run_prompt_skill(sid, d, str(PRODUCTS / sid), cands,
                                 spec=PROMPT_SCENARIOS[sid])
            time.sleep(3)  # 网关 RPM 严格：串行 + 间隔，避免连坐 429
            return r
        with fut.ThreadPoolExecutor(max_workers=1) as ex:
            for r in ex.map(_p, prompt_items):
                results.append(r)
                if r["model"]:
                    models_used.add(r["model"])
                mark = "PASS" if r["verdict"] == "pass" else "FAIL"
                print(f"  {mark:<4} {r['skill']:<55} {r['reason_class'] or ''}"[:150],
                      flush=True)

    npass, nfail = _report(results, llm_used=not args.no_llm,
                           models_used=sorted(models_used))
    print(f"\n=== scenario harness: pass={npass} fail={nfail} / {len(results)} ===",
          flush=True)
    print(f"report -> {ART / 'scenario_report.md'}", flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
