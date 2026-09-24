# Methodology sources and design trade-offs

> When to read: when you want to extend field translation rules, add platform mappings, or understand "why not just write a crontab."
> Command parameters are in SKILL.md; this file only covers design rationale.

## Idea sources (distilled from public methodology; no code copied)

| This script's approach | Idea distilled from |
|--------------|--------------|
| Translate the expression into plain language before executing | The change-management convention of "restate before acting": confirming shared understanding with a different formulation before executing is the cheapest way to catch misunderstanding |
| Generate but don't install | The config-management tool "render + human apply" model; crontab has no version control, no undo stack—writing it in is high-risk |
| Next-fire-time preview | The common interaction of `systemd-analyze calendar` and cloud-vendor cron previewers: use concrete moments instead of abstract field combinations |
| Absolute path + redirect warning | The classic distillation of cron ops experience (cron's PATH and mail mechanism are its two most famous pitfalls) |
| Validate syntax before output | The compiler-frontend approach: do syntax/semantic checks first, then emit target code, avoiding handing bad config downstream |

## Key trade-offs

**Why a built-in parser rather than using croniter as the sole implementation?** croniter can compute times but **produces no Chinese description**,
and the "plain-language confirmation" is this skill's core value. Division of labor: the built-in parser handles field expansion and translation (zero-dependency,
always available), croniter handles the precise next fire time (optional; if missing, degrade and clearly tell the user precision has dropped).

**Why no time prediction for `@reboot`?** It has no predictable time point—when the machine reboots is unknowable.
The early implementation had croniter compute it, and it threw an error outright; now it's blocked early with the note "triggers only on startup."

**Why does `cron-add` check for absolute paths in the command?** This is the #1 failure cause of scheduled tasks,
and its manifestation is **silent non-execution**—the user sees no error. Putting the check at generation time
costs almost nothing and pays off hugely.

**Why does the warning distinguish "no `--log` specified" from "no redirect in the command"?** The two have different fixes:
the former just needs `--log` (the script auto-adds the redirect), the latter needs changing the command itself.
An earlier version conflated them, causing a warning even when `--log` was specified—a false positive.

**Why does field translation handle tiers like "weekday" / "weekend"?** Translating `* * * * 1-5` verbatim to
"Monday, Tuesday, Wednesday, Thursday, Friday" is poorly readable and easy to gloss over; reducing it to "weekday" is closer to the user's mental model.
The criterion must be **exact match** (exactly those five/two), otherwise fall back to itemized listing, avoiding false reduction.

## cron field semantics essentials (implementation basis)

| Field | Range | Common pitfall |
|------|---------|--------|
| Minute | 0-59 | `*/5` is every 5 minutes, not "the 5th minute" |
| Hour | 0-23 | **No 24**; `0` is midnight |
| Day of month | 1-31 | When constrained together with "day of week," cron semantics are **OR** not AND |
| Month | 1-12 | 0 not supported |
| Day of week | 0-7 | **0 and 7 are both Sunday**; 1 is Monday (not Sunday) |
| Special | `@reboot` `@daily` `@hourly`, etc. | `@reboot` has no fixed moment |

The OR relationship when day-of-month and day-of-week are both constrained is the most counterintuitive point in cron semantics; the script marks it explicitly in the description.

## Official documentation

- `crontab(5)` man page (field definitions and `@` special expressions): <https://man7.org/linux/man-pages/man5/crontab.5.html>
- `cron(8)` man page (environment variables and mail mechanism): <https://man7.org/linux/man-pages/man8/cron.8.html>
- Apple `launchd.plist` man page (`StartCalendarInterval`, `StandardOutPath`): <https://www.manpagez.com/man/5/launchd.plist/>
- Apple `launchctl` man page (`load`/`kickstart`): <https://www.manpagez.com/man/1/launchctl/>
- Microsoft `schtasks` command reference: <https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks>
- Microsoft Task Scheduler XML schema: <https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema>
- croniter project (`croniter` expression iterator): <https://github.com/pallets-eco/croniter>
