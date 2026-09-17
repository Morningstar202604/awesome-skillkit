#!/usr/bin/env python3
"""schedule_helper.py -- cron 表达式的人话翻译与安全落地辅助。

定位：**只生成与解释，不替你写入 crontab。**

设计原则
--------
1. **打印而非安装**：`cron-add` 只输出可直接粘贴的 crontab 行与安装步骤，
   真正的写入动作留给用户——静默改用户的定时任务是高风险行为。
2. **人话优先**：`cron-check` 把 `0 9 * * 1` 翻译成"每周一 09:00"，
   让用户在执行前能用自然语言确认自己没写反。
3. **无依赖也能跑**：优先用 croniter 计算真实的下次触发时间；
   未安装时降级为纯语法规格解析（仍能输出中文描述），而不是直接报错。

子命令
------
  cron-add  --name X --schedule "0 9 * * *" --cmd "..." [--log PATH]
  cron-list [--file PATH]
  cron-check "0 9 * * 1" [--count N]

Python >= 3.8。croniter 可选（缺失时降级）。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime

# 字段取值范围（分钟 小时 日 月 星期），与 POSIX crontab(5) 一致
FIELD_RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]

FIELD_NAMES = ["分钟", "小时", "日", "月", "星期"]

MONTH_NAMES = {
    1: "1月", 2: "2月", 3: "3月", 4: "4月", 5: "5月", 6: "6月",
    7: "7月", 8: "8月", 9: "9月", 10: "10月", 11: "11月", 12: "12月",
}

# cron 里 0 和 7 都表示星期日
DOW_NAMES = {0: "周日", 1: "周一", 2: "周二", 3: "周三", 4: "周四",
             5: "周五", 6: "周六", 7: "周日"}

# 常见简写，命中时优先给"人话"而不是逐字段翻译
PRESETS = {
    "*/1 * * * *": "每分钟",
    "* * * * *": "每分钟",
    "0 * * * *": "每小时整点",
    "0 0 * * *": "每天 00:00（午夜）",
    "0 9 * * *": "每天 09:00",
    "0 0 * * 1": "每周一 00:00",
    "@daily": "每天 00:00（@daily）",
    "@hourly": "每小时整点（@hourly）",
    "@weekly": "每周日 00:00（@weekly）",
    "@monthly": "每月 1 日 00:00（@monthly）",
    "@reboot": "每次系统启动时",
    "@yearly": "每年 1 月 1 日 00:00（@yearly）",
    "@annually": "每年 1 月 1 日 00:00（@annually）",
}

SPECIALS = {"@reboot", "@yearly", "@annually", "@monthly", "@weekly",
            "@daily", "@midnight", "@hourly"}


class CronSyntaxError(ValueError):
    """cron 表达式语法错误。"""


# --------------------------------------------------------------------------
# 解析
# --------------------------------------------------------------------------
def _expand_field(token: str, lo: int, hi: int) -> list:
    """把单个字段展开为具体取值列表，支持 * , - / 四种语法。"""
    values = []
    for part in token.split(","):
        part = part.strip()
        if not part:
            raise CronSyntaxError(f"空字段项（检查多余的逗号）: {token!r}")
        step = 1
        if "/" in part:
            head, _, step_s = part.partition("/")
            if not step_s.isdigit() or int(step_s) == 0:
                raise CronSyntaxError(f"步长必须是正整数: {part!r}")
            step = int(step_s)
            part = head or "*"
        if part == "*":
            start, end = lo, hi
        elif "-" in part.lstrip("-"):
            lo_s, _, hi_s = part.partition("-")
            if not lo_s.isdigit() or not hi_s.isdigit():
                raise CronSyntaxError(f"区间必须是数字: {part!r}")
            start, end = int(lo_s), int(hi_s)
            if start > end:
                raise CronSyntaxError(f"区间起点大于终点: {part!r}")
        else:
            if not part.isdigit():
                # 允许 JAN/MON 之类的名字只做提示，不做完整映射
                if re.fullmatch(r"[A-Za-z]{3}", part):
                    raise CronSyntaxError(
                        f"暂不支持月份/星期英文缩写 {part!r}，请改用数字"
                    )
                raise CronSyntaxError(f"无法识别的字段: {part!r}")
            start = end = int(part)
        if start < lo or end > hi:
            raise CronSyntaxError(
                f"取值 {start}-{end} 超出允许范围 {lo}-{hi}（字段: {part!r}）"
            )
        values.extend(range(start, end + 1, step))
    return sorted(set(values))


def parse_cron(expr: str) -> dict:
    """解析为 {field_name: [values]}；失败抛 CronSyntaxError。"""
    expr = expr.strip()
    if expr.startswith("@"):
        if expr not in SPECIALS:
            raise CronSyntaxError(f"未知的特殊表达式: {expr!r}")
        return {"special": expr}
    parts = expr.split()
    if len(parts) != 5:
        raise CronSyntaxError(
            f"字段数应为 5，实际 {len(parts)} 个。格式：分 时 日 月 星期"
        )
    out = {}
    for name, token, (lo, hi) in zip(FIELD_NAMES, parts, FIELD_RANGES):
        # 星期同时接受 0 和 7 表示周日，所以上界放宽到 7
        real_hi = 7 if name == "星期" else hi
        out[name] = _expand_field(token, lo, real_hi)
    return out


# --------------------------------------------------------------------------
# 人话描述
# --------------------------------------------------------------------------
def _collapse(values: list) -> str:
    """把等差且覆盖整个范围的取值列表压成 `*/step` 形式，否则返回空串。"""
    if len(values) < 3:
        return ""
    step = values[1] - values[0]
    if step <= 0 or values != list(range(values[0], values[-1] + 1, step)):
        return ""
    if values[0] != 0:
        return ""
    return f"*/{step}"


def _fmt_hhmm(hours: list, minutes: list) -> str:
    """把小时/分钟列表写成紧凑的 HH:MM 串；组合过多时返回空串。"""
    if len(hours) * len(minutes) > 8:
        return ""
    times = [f"{h:02d}:{m:02d}" for h in hours for m in minutes]
    return "、".join(times)


def describe(expr: str) -> str:
    """把 cron 表达式翻译成中文描述。"""
    expr = expr.strip()
    if expr in PRESETS:
        return PRESETS[expr]
    parsed = parse_cron(expr)

    if "special" in parsed:
        return PRESETS.get(parsed["special"], f"特殊表达式 {parsed['special']}")

    minutes, hours = parsed["分钟"], parsed["小时"]
    doms, months, dows = parsed["日"], parsed["月"], parsed["星期"]

    every_minute = len(minutes) == 60
    hour_part = ""
    if not every_minute:
        hour_part = _fmt_hhmm(hours, minutes)

    # 星期
    dow_part = ""
    if len(dows) < 7:
        # 先归一化（0 与 7 同义），再按"周一到周日"的中文习惯排序
        normalized = sorted(set(0 if x == 7 else x for x in dows))
        normalized.sort(key=lambda d: (d == 0, d))   # 周日排到最后
        seq = [DOW_NAMES[d] for d in normalized]
        if len(seq) == 1:
            dow_part = f"每{seq[0]}"
        elif seq == ["周一", "周二", "周三", "周四", "周五"]:
            dow_part = "工作日"
        elif seq == ["周六", "周日"]:
            dow_part = "周末"
        else:
            dow_part = "、".join(seq)

    # 日 / 月
    dom_part = ""
    if len(doms) < 31:
        days = "、".join(str(d) for d in doms)
        dom_part = f"每月 {days} 日"
    if len(months) < 12:
        month_str = "、".join(MONTH_NAMES.get(m, f"{m}月") for m in months)
        if dom_part:
            # "每月 29 日" -> "2月的 29 日"：去掉"每月"换上月名，避免"2月 的 29 日"
            dom_part = f"{month_str}的 {dom_part[len('每月 '):]}"
        else:
            dom_part = month_str

    # 组装：频率前缀 + 时间
    if every_minute:
        prefix = "每分钟"
    elif hour_part:
        if dow_part:
            prefix = f"{dow_part} {hour_part}"
        elif dom_part:
            prefix = f"{dom_part} {hour_part}"
        elif len(hours) == 24:
            prefix = f"每小时的第 {', '.join(str(m) for m in minutes)} 分"
        else:
            prefix = f"每天 {hour_part}"
    else:
        # 时刻组合过多，退化为"步长/时段"式描述
        h_step = _collapse(hours)
        if h_step:
            n = h_step.lstrip("*/")
            h_desc = "每小时" if n == "1" else f"每 {n} 小时"
        elif len(hours) > 1:
            h_desc = f"{hours[0]:02d}-{hours[-1]:02d} 时段"
        else:
            h_desc = f"{hours[0]:02d} 时"
        m_step = _collapse(minutes)
        if m_step:
            m_desc = f"每 {m_step.lstrip('*/')} 分钟"
        elif len(minutes) == 60:
            m_desc = "每分钟"
        else:
            m_desc = f"第 {', '.join(str(m) for m in minutes)} 分"
        # 小时为全天时不必写"每天"，"每小时"本身已含全天含义
        prefix = f"{h_desc}{m_desc}" if len(hours) == 24 \
            else f"每天 {h_desc}内{m_desc}"
        if dow_part:
            prefix = f"{dow_part} {prefix}"
        elif dom_part:
            prefix = f"{dom_part} {prefix}"

    if dom_part and dow_part:
        prefix = f"{dom_part}与{dow_part}（cron 语义为「或」） {hour_part or ''}".strip()
    return prefix


# --------------------------------------------------------------------------
# 下次触发时间
# --------------------------------------------------------------------------
PROBES = {"@reboot"}


def next_runs(expr: str, count: int, base: datetime | None = None):
    """返回 (times, source)。times 为 None 表示无法精确计算。"""
    base = base or datetime.now()
    if expr.strip() in PROBES:
        # @reboot 没有可预测的时间点，croniter 会直接抛错，这里提前挡掉
        return None, "该表达式没有可预测的时间点（仅在启动时触发）"
    try:
        from croniter import croniter
    except ImportError:
        return None, "croniter 未安装"
    try:
        it = croniter(expr, base)
        return [it.get_next(datetime) for _ in range(count)], "croniter"
    except (ValueError, KeyError) as e:
        raise CronSyntaxError(f"croniter 拒绝该表达式: {e}") from e


# --------------------------------------------------------------------------
# cron-add
# --------------------------------------------------------------------------
def cmd_cron_add(args) -> int:
    # 先验证表达式，避免把语法错误写进 crontab（cron 会静默忽略坏行）
    try:
        parsed = parse_cron(args.schedule)
    except CronSyntaxError as e:
        print(f"ERROR: 表达式非法: {e}", file=sys.stderr)
        return 2

    log_path = args.log or f"/var/log/{args.name}.log"
    cmd = args.cmd
    warn = []
    # 逐 token 找可执行体：跳过 VAR=VAL 前置赋值与环境变量展开
    tokens = [t for t in cmd.split() if "=" not in t.split("/")[0] or "/" in t]
    exe = ""
    for t in tokens:
        if t.startswith("-") or "$" in t:
            continue
        exe = t
        break
    if exe and not exe.startswith("/") and not exe.startswith("${"):
        warn.append(
            f"命令里的 `{exe}` 不是绝对路径——cron 的 PATH 只有 "
            "/usr/bin:/bin，相对命令名在别人的机器上必然失败。"
            f"先 `which {exe}` 查出全路径再写进来。"
        )
    if not re.search(r"(>>?\s*\S+)|2>&1", cmd) and not args.log:
        warn.append(
            "命令没有重定向输出，且未指定 --log——cron 会把它当邮件发，"
            "长期无人看会撑满 /var/mail。建议加 `--log <路径>` 或手动追加 "
            f"`>> {log_path} 2>&1`。"
        )
    if not exe:
        warn.append("未能从命令中识别出可执行体，请人工核对。")

    line = f"{args.schedule} {cmd}"
    if args.log:
        line += f" >> {args.log} 2>&1"

    print("# 将要添加的 crontab 行（本命令不会自动写入）")
    print()
    print(f"# {args.name} —— {describe(args.schedule)}")
    print(line)
    print()
    print("## 安装步骤")
    print()
    print("  crontab -l > /tmp/cron.bak              # 先备份现有任务")
    print("  crontab -l | { cat; echo '<上一行内容>'; } | crontab -")
    print("  crontab -l                              # 确认已写入")
    print()
    print("## 本次未自动写入的原因")
    print("  静默修改用户定时任务属高风险操作；且 crontab 的写入无撤销栈，")
    print("  出错后难以判断原状态。请人工粘贴上面那一行。")
    print()

    if warn:
        print("## 检查中发现的问题（建议修掉再加）")
        for w in warn:
            print(f"  - {w}")
        print()
    return 0


# --------------------------------------------------------------------------
# cron-list
# --------------------------------------------------------------------------
def _read_crontab(args) -> tuple:
    """返回 (文本, 来源说明)。"""
    if args.file:
        from pathlib import Path
        p = Path(args.file)
        if not p.is_file():
            return None, f"文件不存在: {p}"
        return p.read_text(encoding="utf-8", errors="ignore"), f"文件 {p}"
    exe = shutil.which("crontab")
    if not exe:
        return None, ("当前系统没有 `crontab` 命令（cron 不可用）。"
                      "macOS 请改用 launchd（见 SKILL.md 三平台差异表）；"
                      "Windows 请用任务计划程序 schtasks。")
    proc = subprocess.run([exe, "-l"], capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        if "no crontab" in err.lower():
            return "", "当前用户尚无 crontab（空）"
        return None, f"`crontab -l` 失败: {err or proc.returncode}"
    return proc.stdout, "`crontab -l`"


def cmd_cron_list(args) -> int:
    text, source = _read_crontab(args)
    if text is None:
        print(f"ERROR: {source}", file=sys.stderr)
        print("  → 本技能提供的是解析与生成辅助，无法在无 cron 的环境列出任务。",
              file=sys.stderr)
        return 1

    print(f"# 当前定时任务（来源：{source}）")
    print()
    if not text.strip():
        print("（空：当前用户没有任何定时任务）")
        return 0

    rows = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            rows.append(("注释", line.lstrip("# ").strip(), ""))
            continue
        # 支持 NAME=value 环境变量行
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", line):
            key, _, val = line.partition("=")
            rows.append(("环境变量", key, val))
            continue
        parts = line.split(None, 5)
        if line.startswith("@"):
            expr, cmd = parts[0], " ".join(parts[1:])
        elif len(parts) >= 6:
            expr, cmd = " ".join(parts[:5]), parts[5]
        else:
            rows.append(("无法解析", line[:50], ""))
            continue
        try:
            meaning = describe(expr)
        except CronSyntaxError as e:
            meaning = f"语法错误: {e}"
        rows.append(("任务", expr, meaning))
        rows.append(("", "", cmd))

    width = max((len(r[2]) for r in rows if r[0] == "任务"), default=18)
    print(f"{'表达式':<18}{'含义':<34}命令")
    print("-" * 78)
    for kind, a, b in rows:
        if kind == "任务":
            print(f"{a:<18}{b:<34}")
        elif kind == "":
            print(f"{'':<18}{'':<34}{b}")
        elif kind == "环境变量":
            print(f"[env] {a}={b}")
        elif kind == "注释":
            print(f"[注释] {a}")
        else:
            print(f"[{kind}] {a}")
    return 0


# --------------------------------------------------------------------------
# cron-check
# --------------------------------------------------------------------------
def cmd_cron_check(args) -> int:
    expr = args.expression
    print(f"表达式: {expr}")
    try:
        meaning = describe(expr)
    except CronSyntaxError as e:
        print(f"ERROR: 表达式非法: {e}", file=sys.stderr)
        return 2
    print(f"含义  : {meaning}")
    print()

    try:
        times, source = next_runs(expr, args.count)
    except CronSyntaxError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if times is None:
        print(f"下次触发时间: 无法精确计算（{source}）")
        print("  → 精确预测需要 croniter：python3 -m pip install croniter")
        print("  → 上面的中文描述由内置解析器给出，仍是可靠的。")
        return 0

    print(f"未来 {len(times)} 次触发时间（依据 {source}，时区=本机）:")
    for t in times:
        wd = DOW_NAMES[t.weekday() + 1]
        print(f"  {t.strftime('%Y-%m-%d %H:%M:%S')}  {wd}")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="schedule_helper.py",
        description="cron 表达式的人话翻译与落地辅助（只生成与解释，不写入 crontab）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("cron-add", help="生成 crontab 行与安装步骤（不自动写入）")
    s.add_argument("--name", required=True, help="任务名（用于注释与日志默认名）")
    s.add_argument("--schedule", required=True, help='如 "0 9 * * *"')
    s.add_argument("--cmd", required=True, help="要执行的命令（建议用绝对路径）")
    s.add_argument("--log", default=None, help="输出去向，如 ~/logs/job.log")
    s.set_defaults(func=cmd_cron_add)

    s = sub.add_parser("cron-list", help="解析 crontab -l 输出为可读表格")
    s.add_argument("--file", default=None, help="改为解析指定文件（便于离线查看）")
    s.set_defaults(func=cmd_cron_list)

    s = sub.add_parser("cron-check", help="解释表达式并给出下次触发时间")
    s.add_argument("expression")
    s.add_argument("--count", type=int, default=5, help="预测次数，默认 5")
    s.set_defaults(func=cmd_cron_check)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
