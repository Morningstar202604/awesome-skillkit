---
name: caveman-stats
description: >-
  Show recorded output and cache-read token usage and mode attribution for
  the current Claude Code session, or locate the host's native usage report.
  Trigger: /caveman-stats.
description_zh: "查看当前会话记录的输出与缓存读取 token 用量及模式归属，或定位宿主的原生用量报告。"
license: MIT
compatibility: 纯提示型，任意支持 SKILL.md 的工具可用；caveman-stats / caveman-compress 的 CLI 能力依赖上游 caveman 安装。
metadata:
  author: "JuliusBrussee/caveman 上游（MIT；仅采用技能面，引擎目录另为 BSL-1.1）"
  version: "1.0.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/JuliusBrussee/caveman/tree/main/skills/caveman-stats"
---

In Claude Code, `src/hooks/caveman-mode-tracker.js` resolves `src/hooks/caveman-stats.js` next to itself and runs it on `/caveman-stats`. The hook does not block the prompt: it supplies the report through `hookSpecificOutput.additionalContext` with an instruction to print it verbatim inside a fenced code block. Do exactly that, and do not calculate, recompute or re-round the numbers yourself.

In Gemini CLI, direct the user to `/stats model` for current session token usage or `/stats session` for session statistics. Gemini custom commands are prompts; they cannot invoke the built-in command or read its live session metrics. Never read Claude Code transcripts as Gemini usage. In other hosts, use a native usage report if one is available; otherwise say that current session usage is unavailable. The Claude reader and its lifetime history apply only to Claude Code. Savings remain unknown in every host without a measured comparison.

The report shows recorded output and cache-read tokens, response counts, and mode attribution where available. Savings are unknown: the transcript has no measured comparison without Caveman. Do not infer saved tokens, percentages, dollars, rule overhead, or a net result from output counts or the current mode.

`--all` and `--since 7d` aggregate the latest recorded output count per session. `--share` reports observed usage with savings unknown. Historical `est_saved_*` fields are ignored; their original history rows remain on disk. The statusline shows the active mode without the retired savings badge.

Original/current memory-file pairs are reported by their measured byte sizes. Those file-size differences do not establish provider token or billing savings. See the upstream project's honesty-notes document (`HONEST-NUMBERS.md`; not bundled here).

---

## 来源与署名 / Source & Attribution

本技能收录自 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman/tree/main/skills/caveman-stats)（MIT）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
