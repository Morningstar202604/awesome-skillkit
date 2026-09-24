---
name: task-scheduler
description: >-
  Translate cron expressions into plain language, preview next fire times,
  generate safe crontab lines, and map the same schedule onto Linux cron, macOS
  launchd, and Windows Task Scheduler. Use when the user asks to schedule a
  recurring job / crontab syntax / run this every day / cron expression / daily
  scheduled task / automation scheduling. Do NOT use for one-off delayed commands
  (use `at` or `sleep`), long-running daemons, or in-process job queues like
  Celery.
license: Apache-2.0
compatibility: "Python 3.8+ stdlib for description and crontab parsing. croniter is optional and only improves next-fire-time precision (pip install croniter). The helper never writes to crontab itself; it prints the line for the user to install."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: tools
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Task Scheduler (Scheduled Tasks)

Solves the "run automatically every interval" implementation problem across
Linux / macOS / Windows three platforms.

**Core judgment: scheduled task failure is almost never cron itself—it's the
execution environment.** A command that works in an interactive shell fails in
crontab—because it gets a **minimal environment** (PATH only `/usr/bin:/bin`,
no shell aliases, none of your `~/.bashrc` settings). So this skill's first
action is to translate the expression into plain language for user confirmation;
second action is to hard-code the command with "absolute path + output
redirection" two rules, avoiding three major failure causes.

**This skill doesn't write to crontab for you.** `cron-add` only prints
ready-to-paste lines and install steps—once a scheduled task is wrong (e.g.
missing a asterisk means running every second), consequences are severe and
there's no undo stack; the human confirmation gate can't be skipped.

## Input Checklist

| Input | Required | Notes |
|------|:---:|------|
| Trigger time | yes | cron expression, e.g. `0 9 * * 1` (every Monday 09:00). Unsure → user says in plain words first, skill translates |
| Command to execute | yes | `--cmd`. Must be **absolute path**, recommend redirecting output |
| Task name | no | `--name`, used for comment and default log name, e.g. `backup` |
| Log destination | no | `--log <path>`; if not given, command itself must include `>> ... 2>&1` |
| Target platform | no | Default Linux cron; macOS/Windows see difference table below |

When inputs are missing, ask all at once: "Please provide: 1) how often to run
(say it in plain words); 2) what command to run (full path); 3) which log file
output goes to; 4) target Linux, macOS, or Windows. Default: Linux cron, log at
`~/logs/<name>.log`."

## Pre-flight Checks

```bash
python3 --version                                    # expected >= 3.8
test -f scripts/schedule_helper.py && echo SCRIPT_OK # expected prints SCRIPT_OK
python3 -c "import croniter; print('croniter OK')" 2>/dev/null || echo "croniter missing: only affects next-fire-time precision"
command -v crontab || echo "no crontab: this machine isn't a cron environment (macOS uses launchd / Windows uses schtasks)"
crontab -l 2>&1 | head -3                            # see existing tasks first, avoid overwrite
```

Missing `croniter` and `crontab` don't affect "expression translation" core
capability; script auto-degrades and notes it.

## Workflow

### Step 1: Translate Expression to Plain Language, Confirm Understanding First

```bash
python3 scripts/schedule_helper.py cron-check "0 9 * * 1"
```

Expected: prints `meaning : every Monday 09:00`, then lists next 5 fire times
(with day of week).

**This step can't be skipped.** In `0 9 * * 1`, `1` is Monday not Sunday,
`* * * * *` is every minute—most accidents come from misremembering field
meaning or wrong field count.

If it fails: `field count should be 5, got 6` → count spaces; `value 99 out of
allowed range 0-23` → hour field written wrong.

### Step 2: Generate Crontab Line

```bash
python3 scripts/schedule_helper.py cron-add \
  --name backup --schedule "0 3 * * *" \
  --cmd "/usr/bin/python3 /home/me/backup.py" --log "/home/me/logs/backup.log"
```

Expected: prints comment line + crontab line + backup/install steps. If command
has risks, appends "issues found during check".

If it fails: `ERROR: invalid expression` and exit code 2 → return to step 1 to
fix; "not an absolute path" warning → first `which <cmd>` to find full path then
rerun.

### Step 3: Check Existing Tasks, Avoid Accidental Overwrite

```bash
python3 scripts/schedule_helper.py cron-list
```

Expected: table lists expressions, plain-language meaning, commands. Lines with
syntax errors are marked `syntax error: ...`.

If it fails: `current system has no crontab command` → this machine isn't a cron
environment; switch to step 5's corresponding plan.

### Step 4: Human Install and Verify

```bash
crontab -l > /tmp/cron.bak        # always back up first
crontab -l | { cat; echo '0 3 * * * /usr/bin/python3 /home/me/backup.py >> /home/me/logs/backup.log 2>&1'; } | crontab -
crontab -l                        # confirm written
```

Expected: `crontab -l` output shows the line just added.

**Verify**: temporarily set the time to 2 minutes later and run once, confirm
the log file is actually written—tasks in `crontab -e` don't error; if wrong
they just **silently never execute**.

If it fails: task doesn't trigger → troubleshoot per "three major failure causes"
below.

### Step 5: Non-Linux Platforms Use Corresponding Plan

See three-platform difference table below, translate the same semantics over.

Expected: user gets equivalent scheduled config on target platform (plist /
schtasks command).
If it fails: target platform can't map expression semantics one-to-one (e.g.
launchd's `StartCalendarInterval` doesn't support complex combos beyond pure
"every N minutes within time window") → split into multiple triggers or switch
to `StartInterval`, and honestly tell user that platform's capability boundary;
don't force a seemingly equivalent config.

## Three-Platform Difference Table

| Dimension | Linux cron | macOS launchd | Windows Task Scheduler |
|------|-----------|---------------|---------------------|
| Config location | `crontab -e` | `~/Library/LaunchAgents/*.plist` | `taskschd.msc` GUI |
| Time syntax | `0 9 * * 1` | `StartCalendarInterval` dict | XML `Triggers` or `schtasks /sc` |
| CLI creation | see step 4 | `launchctl load <plist>` | `schtasks /create /tn X /tr CMD /sc daily /st 09:00` |
| Environment vars | **almost empty**, needs explicit `PATH=` | similarly minimal, in plist's `EnvironmentVariables` | runs as service account, env ≠ logged-in user |
| Output destination | default emails (easily fills `/var/mail`) | `StandardOutPath`/`StandardErrorPath` | task history or redirect |
| Needs login? | no | **user-level Agent requires logged in**; system-level Daemon doesn't | configurable "run whether user logged on or not" |
| View method | `crontab -l` | `launchctl list \| grep <label>` | `schtasks /query /tn X /v /fo list` |
| Manual trigger | no built-in; temporarily change time | `launchctl kickstart -k gui/$(id -u)/<label>` | `schtasks /run /tn X` |
| Typical pitfall | PATH missing, no redirect | Agent not loaded, plist syntax error silently ignored | account permissions, "run only when logged on" |

One-line selection: **Linux servers use cron; macOS desktop prefers launchd
(cron still works but Apple marks it legacy); Windows uses schtasks or Task
Scheduler GUI.**

## Three Major Causes of Scheduled Task Failure

### Cause One: Missing Environment Variables

cron gets an almost-empty environment—`PATH` usually only `/usr/bin:/bin`,
nothing you `export` in `~/.zshrc`.

**Diagnosis**: command works typed in terminal, but in crontab reports `command
not found` or can't read some variable.

**Action**: explicitly declare at top of crontab (one assignment per line, don't
use `export`):

```bash
PATH=/usr/local/bin:/usr/bin:/bin
MY_API_KEY=xxx
```

Or let the script load environment itself: `/usr/bin/env bash -lc '/usr/bin/python3 /path/job.py'`.

### Cause Two: Path Not Absolute

cron's **working directory is the current user's home** (not your project
directory), and PATH is minimal, so `python3 job.py` without full path
inevitably fails.

**Diagnosis**: error contains `no such file or directory`, or log can't find
files referenced by relative path.

**Action**: commands, files in arguments, resources referenced inside scripts
**all change to absolute paths**; add `cd /absolute/project/dir || exit 1` at
script top.

### Cause Three: Insufficient Permissions

cron runs as your user but **doesn't inherit sudo permissions**, and can't access
resources needing interactive authorization (like macOS TCC-protected
directories, keychains needing unlock).

**Diagnosis**: error contains `Permission denied`, `Operation not permitted`; or
task appears to succeed but did nothing.

**Action**: check file and directory permissions (`ls -l`), confirm no reliance
on interactive input; tasks needing elevation use `sudo crontab -e` (system-level)
rather than writing `sudo` in user tasks—there's no terminal in cron, so `sudo`
always hangs waiting for password.

## Failure Handling Table

| Symptom | Cause | Action |
|------|------|------|
| Task doesn't run at all, no error | Expression wrong, cron silently ignores | `cron-check` to re-verify; check field count, hour field has `99` |
| `command not found` | PATH missing the command | Add `PATH=` at top of crontab, or change to absolute path |
| `No such file or directory` | Relative path / wrong working directory | All to absolute paths; `cd /abs/path` first in script |
| `Permission denied` | Insufficient permissions or needs interactive auth | `ls -l` to check permissions; don't use `sudo` in cron |
| `/var/mail` flooded | Output not redirected, cron sends as email | Append `>> /path/job.log 2>&1` to command or add `--log` |
| macOS plist no response | Agent not loaded, or user not logged in | `launchctl load` then `list` to confirm; switch to system-level Daemon |
| Windows task doesn't run | Account permissions / "run only when logged on" not unchecked | Check task history; change to "run whether user logged on or not" with account |
| `croniter rejects expression` | Expression beyond croniter support range | Use `cron-check` built-in parser to see plain-language description; syntax still judged |

## Delivery Criteria

**Success definition**: `cron-check` output plain-language meaning matches user's
spoken intent, and the line is visible in `crontab -l`.

**Artifacts**: a ready-to-paste crontab line (with comment), or corresponding
platform's plist / schtasks command.

**Location**: Linux in user crontab (visible via `crontab -l`); always `crontab
-l > /tmp/cron.bak` backup before install.

**Integrity verification**:

```bash
crontab -l | grep -F "<command fragment just added>"      # confirm written
ls -l "<--log specified log path>"                       # should appear after one trigger and keep growing
grep CRON /var/log/syslog | tail -5                      # on Debian/Ubuntu see if cron actually called it
```

## References

- `scripts/schedule_helper.py` — run it for cron-add / cron-list / cron-check; `describe` is the translation core.
- `references/sources-and-methodology.md` — basis for field translation rules, degradation strategy, and three-platform semantic mapping.
