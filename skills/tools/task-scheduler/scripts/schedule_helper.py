#!/usr/bin/env python3
"""schedule_helper.py -- plain-language translation and safe rollout helper for cron expressions.

Positioning: **only generates and explains; never writes into your crontab for you.**

Design principles
-----------------
1. **Print, don't install**: `cron-add` only emits a crontab line you can paste and the install
   steps; the actual write is left to the user -- silently editing the user's scheduled tasks is
   high-risk.
2. **Plain language first**: `cron-check` translates `0 9 * * 1` into "every Monday 09:00", so
   the user can confirm in natural language before running it that they didn't write it backwards.
3. **Runs without deps**: prefer croniter to compute the real next fire time; when it isn't
   installed, degrade to pure syntax-spec parsing (still emits an English description) instead
   of erroring out.

Subcommands
-----------
  cron-add  --name X --schedule "0 9 * * *" --cmd "..." [--log PATH]
  cron-list [--file PATH]
  cron-check "0 9 * * 1" [--count N]

Python >= 3.8. croniter optional (degrades when missing).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime

# field value ranges (minute hour day month weekday), matching POSIX crontab(5)
FIELD_RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]

FIELD_NAMES = ["minute", "hour", "day", "month", "dow"]

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

# in cron, both 0 and 7 mean Sunday
DOW_NAMES = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu",
             5: "Fri", 6: "Sat", 7: "Sun"}

# common shortcuts; on a hit, prefer a "plain-language" reading over per-field translation
PRESETS = {
    "*/1 * * * *": "every minute",
    "* * * * *": "every minute",
    "0 * * * *": "every hour on the hour",
    "0 0 * * *": "every day at 00:00 (midnight)",
    "0 9 * * *": "every day at 09:00",
    "0 0 * * 1": "every Monday at 00:00",
    "@daily": "every day at 00:00 (@daily)",
    "@hourly": "every hour on the hour (@hourly)",
    "@weekly": "every Sunday at 00:00 (@weekly)",
    "@monthly": "on the 1st of every month at 00:00 (@monthly)",
    "@reboot": "at every system boot",
    "@yearly": "every Jan 1 at 00:00 (@yearly)",
    "@annually": "every Jan 1 at 00:00 (@annually)",
}

SPECIALS = {"@reboot", "@yearly", "@annually", "@monthly", "@weekly",
            "@daily", "@midnight", "@hourly"}


class CronSyntaxError(ValueError):
    """Syntax error in a cron expression."""


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------
def _expand_field(token: str, lo: int, hi: int) -> list:
    """Expand a single field into its concrete value list; supports the * , - / four syntaxes."""
    values = []
    for part in token.split(","):
        part = part.strip()
        if not part:
            raise CronSyntaxError(f"empty field item (check for a stray comma): {token!r}")
        step = 1
        if "/" in part:
            head, _, step_s = part.partition("/")
            if not step_s.isdigit() or int(step_s) == 0:
                raise CronSyntaxError(f"step must be a positive integer: {part!r}")
            step = int(step_s)
            part = head or "*"
        if part == "*":
            start, end = lo, hi
        elif "-" in part.lstrip("-"):
            lo_s, _, hi_s = part.partition("-")
            if not lo_s.isdigit() or not hi_s.isdigit():
                raise CronSyntaxError(f"range bounds must be numbers: {part!r}")
            start, end = int(lo_s), int(hi_s)
            if start > end:
                raise CronSyntaxError(f"range start is greater than end: {part!r}")
        else:
            if not part.isdigit():
                # allow 3-letter names like JAN/MON only as a hint, not a full mapping
                if re.fullmatch(r"[A-Za-z]{3}", part):
                    raise CronSyntaxError(
                        f"3-letter month/weekday abbreviations {part!r} are not yet "
                        f"supported; use a number instead"
                    )
                raise CronSyntaxError(f"unrecognized field: {part!r}")
            start = end = int(part)
        if start < lo or end > hi:
            raise CronSyntaxError(
                f"value {start}-{end} is outside the allowed range {lo}-{hi} (field: {part!r})"
            )
        values.extend(range(start, end + 1, step))
    return sorted(set(values))


def parse_cron(expr: str) -> dict:
    """Parse into {field_name: [values]}; raises CronSyntaxError on failure."""
    expr = expr.strip()
    if expr.startswith("@"):
        if expr not in SPECIALS:
            raise CronSyntaxError(f"unknown special expression: {expr!r}")
        return {"special": expr}
    parts = expr.split()
    if len(parts) != 5:
        raise CronSyntaxError(
            f"expected 5 fields, got {len(parts)}. Format: min hour day month dow"
        )
    out = {}
    for name, token, (lo, hi) in zip(FIELD_NAMES, parts, FIELD_RANGES):
        # dow accepts both 0 and 7 as Sunday, so the upper bound is relaxed to 7
        real_hi = 7 if name == "dow" else hi
        out[name] = _expand_field(token, lo, real_hi)
    return out


# --------------------------------------------------------------------------
# plain-language description
# --------------------------------------------------------------------------
def _collapse(values: list) -> str:
    """Collapse an arithmetic-progression list that covers the whole range into `*/step`, else return empty."""
    if len(values) < 3:
        return ""
    step = values[1] - values[0]
    if step <= 0 or values != list(range(values[0], values[-1] + 1, step)):
        return ""
    if values[0] != 0:
        return ""
    return f"*/{step}"


def _fmt_hhmm(hours: list, minutes: list) -> str:
    """Render the hour/minute lists into a compact HH:MM string; return empty when the combination is too large."""
    if len(hours) * len(minutes) > 8:
        return ""
    times = [f"{h:02d}:{m:02d}" for h in hours for m in minutes]
    return ", ".join(times)


def describe(expr: str) -> str:
    """Translate a cron expression into an English description."""
    expr = expr.strip()
    if expr in PRESETS:
        return PRESETS[expr]
    parsed = parse_cron(expr)

    if "special" in parsed:
        return PRESETS.get(parsed["special"], f"special expression {parsed['special']}")

    minutes, hours = parsed["minute"], parsed["hour"]
    doms, months, dows = parsed["day"], parsed["month"], parsed["dow"]

    every_minute = len(minutes) == 60
    hour_part = ""
    if not every_minute:
        hour_part = _fmt_hhmm(hours, minutes)

    # weekday
    dow_part = ""
    if len(dows) < 7:
        # normalize first (0 and 7 are equivalent), then order Mon..Sun per convention
        normalized = sorted(set(0 if x == 7 else x for x in dows))
        normalized.sort(key=lambda d: (d == 0, d))   # put Sunday last
        seq = [DOW_NAMES[d] for d in normalized]
        if len(seq) == 1:
            dow_part = f"every {seq[0]}"
        elif seq == ["Mon", "Tue", "Wed", "Thu", "Fri"]:
            dow_part = "every weekday"
        elif seq == ["Sat", "Sun"]:
            dow_part = "every weekend"
        else:
            dow_part = ", ".join(seq)

    # day / month
    dom_part = ""
    if len(doms) < 31:
        days = ", ".join(str(d) for d in doms)
        dom_part = f"on day {days} of the month"
    if len(months) < 12:
        month_str = ", ".join(MONTH_NAMES.get(m, str(m)) for m in months)
        if dom_part:
            # "on day 29 of the month" -> "on the 29th of Feb": drop "of the month" and attach
            # the month name, avoiding an awkward "of Feb of the month"
            dom_part = f"on the {dom_part[len('on day '):]} of {month_str}"
        else:
            dom_part = f"in {month_str}"

    # assemble: frequency prefix + time
    if every_minute:
        prefix = "every minute"
    elif hour_part:
        if dow_part:
            prefix = f"{dow_part} at {hour_part}"
        elif dom_part:
            prefix = f"{dom_part} at {hour_part}"
        elif len(hours) == 24:
            prefix = f"every hour at minute {', '.join(str(m) for m in minutes)}"
        else:
            prefix = f"every day at {hour_part}"
    else:
        # too many time combos: fall back to a "step / range" style description
        h_step = _collapse(hours)
        if h_step:
            n = h_step.lstrip("*/")
            h_desc = "every hour" if n == "1" else f"every {n} hours"
        elif len(hours) > 1:
            h_desc = f"{hours[0]:0d}:00-{hours[-1]:02d}:00 window"
        else:
            h_desc = f"at {hours[0]:02d}:00"
        m_step = _collapse(minutes)
        if m_step:
            m_desc = f" every {m_step.lstrip('*/')} min"
        elif len(minutes) == 60:
            m_desc = " every minute"
        else:
            m_desc = f" at minute {', '.join(str(m) for m in minutes)}"
        # when the hours cover the whole day, no need to say "every day"; "every hour" already implies it
        prefix = f"{h_desc}{m_desc}" if len(hours) == 24 \
            else f"every day, in the {h_desc} window,{m_desc}"
        if dow_part:
            prefix = f"{dow_part}, {prefix}"
        elif dom_part:
            prefix = f"{dom_part}, {prefix}"

    if dom_part and dow_part:
        prefix = f"{dom_part} or {dow_part} (cron semantics are OR) at {hour_part or ''}".strip()
    return prefix


# --------------------------------------------------------------------------
# next fire time
# --------------------------------------------------------------------------
PROBES = {"@reboot"}


def next_runs(expr: str, count: int, base: datetime | None = None):
    """Return (times, source). times is None when it cannot be computed exactly."""
    base = base or datetime.now()
    if expr.strip() in PROBES:
        # @reboot has no predictable time point; croniter errors out, so block it early
        return None, "this expression has no predictable fire time (only fires at boot)"
    try:
        from croniter import croniter
    except ImportError:
        return None, "croniter is not installed"
    try:
        it = croniter(expr, base)
        return [it.get_next(datetime) for _ in range(count)], "croniter"
    except (ValueError, KeyError) as e:
        raise CronSyntaxError(f"croniter rejected the expression: {e}") from e


# --------------------------------------------------------------------------
# cron-add
# --------------------------------------------------------------------------
def cmd_cron_add(args) -> int:
    # validate the expression first, so a syntax error doesn't get written into crontab (cron silently ignores bad lines)
    try:
        parsed = parse_cron(args.schedule)
    except CronSyntaxError as e:
        print(f"ERROR: invalid expression: {e}", file=sys.stderr)
        return 2

    log_path = args.log or f"/var/log/{args.name}.log"
    cmd = args.cmd
    warn = []
    # find the executable by walking tokens: skip VAR=VAL leading assignments and env expansion
    tokens = [t for t in cmd.split() if "=" not in t.split("/")[0] or "/" in t]
    exe = ""
    for t in tokens:
        if t.startswith("-") or "$" in t:
            continue
        exe = t
        break
    if exe and not exe.startswith("/") and not exe.startswith("${"):
        warn.append(
            f"`{exe}` in the command is not an absolute path -- cron's PATH is only "
            "/usr/bin:/bin, so a relative command name will fail on someone else's machine. "
            f"Run `which {exe}` to find the full path before writing it in."
        )
    if not re.search(r"(>>?\s*\S+)|2>&1", cmd) and not args.log:
        warn.append(
            "The command has no output redirection and no --log was given -- cron will mail "
            "it, and left unread it fills up /var/mail over time. Add `--log <path>` or append "
            f"`>> {log_path} 2>&1` manually."
        )
    if not exe:
        warn.append("Could not identify an executable in the command; please double-check manually.")

    line = f"{args.schedule} {cmd}"
    if args.log:
        line += f" >> {args.log} 2>&1"

    print("# crontab line to be added (this command does not write it for you)")
    print()
    print(f"# {args.name} -- {describe(args.schedule)}")
    print(line)
    print()
    print("## install steps")
    print()
    print("  crontab -l > /tmp/cron.bak              # back up existing tasks first")
    print("  crontab -l | { cat; echo '<line above>'; } | crontab -")
    print("  crontab -l                              # confirm it was written")
    print()
    print("## why this was not written automatically")
    print("  Silently editing the user's scheduled tasks is high-risk, and crontab writes have")
    print("  no undo stack, so it's hard to recover the prior state on error. Please paste the line above.")
    print()

    if warn:
        print("## issues found during the check (fix before adding)")
        for w in warn:
            print(f"  - {w}")
        print()
    return 0


# --------------------------------------------------------------------------
# cron-list
# --------------------------------------------------------------------------
def _read_crontab(args) -> tuple:
    """Return (text, source note)."""
    if args.file:
        from pathlib import Path
        p = Path(args.file)
        if not p.is_file():
            return None, f"file not found: {p}"
        return p.read_text(encoding="utf-8", errors="ignore"), f"file {p}"
    exe = shutil.which("crontab")
    if not exe:
        return None, ("there is no `crontab` command on this system (cron unavailable). "
                      "On macOS use launchd instead (see the three-platform differences table in SKILL.md); "
                      "on Windows use Task Scheduler / schtasks.")
    proc = subprocess.run([exe, "-l"], capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        if "no crontab" in err.lower():
            return "", "the current user has no crontab yet (empty)"
        return None, f"`crontab -l` failed: {err or proc.returncode}"
    return proc.stdout, "`crontab -l`"


def cmd_cron_list(args) -> int:
    text, source = _read_crontab(args)
    if text is None:
        print(f"ERROR: {source}", file=sys.stderr)
        print("  -> this skill provides parsing and generation help; it cannot list tasks in a cron-less environment.",
              file=sys.stderr)
        return 1

    print(f"# current scheduled tasks (source: {source})")
    print()
    if not text.strip():
        print("(empty: the current user has no scheduled tasks)")
        return 0

    rows = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            rows.append(("comment", line.lstrip("# ").strip(), ""))
            continue
        # support NAME=value environment-variable lines
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", line):
            key, _, val = line.partition("=")
            rows.append(("env", key, val))
            continue
        parts = line.split(None, 5)
        if line.startswith("@"):
            expr, cmd = parts[0], " ".join(parts[1:])
        elif len(parts) >= 6:
            expr, cmd = " ".join(parts[:5]), parts[5]
        else:
            rows.append(("unparsed", line[:50], ""))
            continue
        try:
            meaning = describe(expr)
        except CronSyntaxError as e:
            meaning = f"syntax error: {e}"
        rows.append(("task", expr, meaning))
        rows.append(("", "", cmd))

    width = max((len(r[2]) for r in rows if r[0] == "task"), default=18)
    print(f"{'expr':<18}{'meaning':<34}command")
    print("-" * 78)
    for kind, a, b in rows:
        if kind == "task":
            print(f"{a:<18}{b:<34}")
        elif kind == "":
            print(f"{'':<18}{'':<34}{b}")
        elif kind == "env":
            print(f"[env] {a}={b}")
        elif kind == "comment":
            print(f"[comment] {a}")
        else:
            print(f"[{kind}] {a}")
    return 0


# --------------------------------------------------------------------------
# cron-check
# --------------------------------------------------------------------------
def cmd_cron_check(args) -> int:
    expr = args.expression
    print(f"expression: {expr}")
    try:
        meaning = describe(expr)
    except CronSyntaxError as e:
        print(f"ERROR: invalid expression: {e}", file=sys.stderr)
        return 2
    print(f"meaning   : {meaning}")
    print()

    try:
        times, source = next_runs(expr, args.count)
    except CronSyntaxError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if times is None:
        print(f"next fire times: cannot be computed exactly ({source})")
        print("  -> exact prediction needs croniter: python3 -m pip install croniter")
        print("  -> the English description above comes from the built-in parser and is still reliable.")
        return 0

    print(f"next {len(times)} fire times (via {source}, timezone=local):")
    for t in times:
        wd = DOW_NAMES[t.weekday() + 1]
        print(f"  {t.strftime('%Y-%m-%d %H:%M:%S')}  {wd}")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="schedule_helper.py",
        description="plain-language translation and rollout helper for cron expressions "
                    "(only generates and explains; never writes into crontab)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("cron-add", help="generate a crontab line and install steps (does not write automatically)")
    s.add_argument("--name", required=True, help="task name (used in comments and the default log name)")
    s.add_argument("--schedule", required=True, help='e.g. "0 9 * * *"')
    s.add_argument("--cmd", required=True, help="the command to run (absolute path recommended)")
    s.add_argument("--log", default=None, help="where output goes, e.g. ~/logs/job.log")
    s.set_defaults(func=cmd_cron_add)

    s = sub.add_parser("cron-list", help="parse crontab -l output into a readable table")
    s.add_argument("--file", default=None, help="parse a given file instead (for offline review)")
    s.set_defaults(func=cmd_cron_list)

    s = sub.add_parser("cron-check", help="explain an expression and show the next fire times")
    s.add_argument("expression")
    s.add_argument("--count", type=int, default=5, help="how many runs to predict, default 5")
    s.set_defaults(func=cmd_cron_check)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
