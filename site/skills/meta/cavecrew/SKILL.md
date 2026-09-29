---
name: cavecrew
description: >-
  When to delegate to `cavecrew-investigator` (locate code),
  `cavecrew-builder` (1-2 file edit) or `cavecrew-reviewer` (diff review)
  instead of working inline or using `Explore`. Their output is compressed,
  so main context lasts longer.
description_zh: "何时把任务委派给 cavecrew 三件套：定位代码的调查员、1-2 文件改动的建造者、diff 评审者。"
license: MIT
compatibility: 纯提示型，任意支持 SKILL.md 的工具可用；三件套依赖上游 caveman 的 subagent 预设（cavecrew-investigator / cavecrew-builder / cavecrew-reviewer）——本包未附带 agent 定义文件，需先安装上游 caveman 预设，否则按正文派发会路由到不存在的 agent；caveman-stats / caveman-compress 的 CLI 能力同样依赖上游 caveman 安装。
metadata:
  author: "JuliusBrussee/caveman 上游（MIT；仅采用技能面，引擎目录另为 BSL-1.1）"
  version: "1.0.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/JuliusBrussee/caveman/tree/main/skills/cavecrew"
---

Cavecrew = three subagent presets that emit caveman output. Same job as Anthropic defaults (`Explore`, edit-style agents, reviewer); difference is the tool-result they return is compressed, so main context shrinks per delegation.

## When to use cavecrew vs alternatives

| Task | Use |
|---|---|
| "Where is X defined / what calls Y / list uses of Z" | `cavecrew-investigator` |
| Same but you also want suggestions/architecture commentary | `Explore` (vanilla) |
| Surgical edit, ≤2 files, scope obvious | `cavecrew-builder` |
| New feature / 3+ files / cross-cutting refactor | Main thread or `feature-dev:code-architect` |
| Review diff, branch, or file for bugs | `cavecrew-reviewer` |
| Deep code review with rationale + alternatives | `Code Reviewer` (vanilla) |
| One-line answer you already know | Main thread, no subagent |

Rule of thumb: **if you'd want the subagent's output in 1/3 the tokens, pick cavecrew. If you'd want prose, pick vanilla.**

## Why this exists (the real win)

Subagent tool results get injected into main context verbatim. A vanilla `Explore` that returns 2k tokens of prose costs 2k tokens of main-context budget every time. The same finding from `cavecrew-investigator` returns ~700 tokens. Across 20 delegations in one session that's the difference between context exhaustion and finishing the task.

## Output contracts

What main thread can rely on per agent:

**`cavecrew-investigator`**
```
<Header>:
- path:line — `symbol` — short note
totals: <counts>.
```
Or `No match.` Always file-path-first, line-number-attached, backticked symbols. Safe to grep with `path:\d+`.

**`cavecrew-builder`**
```
<path:line-range> — <change ≤10 words>.
verified: <re-read OK | mismatch @ path:line>.
```
Or one of: `too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.` (terminal first token).

**`cavecrew-reviewer`**
```
path:line: <emoji> <severity>: <problem>. <fix>.
totals: N🔴 N🟡 N🔵 N❓
```
Or `No issues.` Findings sorted file → line ascending.

## Chaining patterns

**Locate → fix → verify** (most common):
1. `cavecrew-investigator` returns site list.
2. Main thread picks 1-2 sites, hands paths to `cavecrew-builder`.
3. `cavecrew-reviewer` audits the diff.

**Parallel scout** (when investigation is broad):
Spawn 2-3 `cavecrew-investigator` calls in one message (different angles: defs vs callers vs tests). Aggregate in main thread.

**Single-shot edit** (when site is already known):
Skip investigator. Hand exact path:line to `cavecrew-builder` directly.

## What NOT to do

- Don't use `cavecrew-builder` when you don't already know the file. Spawn investigator first or main thread will eat tokens passing context.
- Don't chain `cavecrew-investigator → cavecrew-builder` for a 5-file refactor. Builder will return `too-big.` and you'll have wasted a turn.
- Don't ask `cavecrew-reviewer` for "general feedback" — it returns findings only, no architecture opinions. Use `Code Reviewer` for that.
- Don't expect prose. Cavecrew output is structured, sometimes terse to the point of cryptic. If a human will read it directly, paraphrase.

## Auto-clarity (inherited)

Subagents drop caveman → normal English for security warnings, irreversible-action confirmations, and any output where fragment ambiguity could be misread. Resume caveman after.

---

## 来源与署名 / Source & Attribution

本技能收录自 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman/tree/main/skills/cavecrew)（MIT）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
