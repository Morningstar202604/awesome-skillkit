---
name: caveman-help
description: >-
  Quick-reference card for caveman modes, skills and commands. Trigger:
  /caveman-help or "caveman help".
description_zh: "caveman 模式、技能与命令的速查卡；触发于 /caveman-help 或「caveman help」。"
license: MIT
compatibility: 纯提示型，任意支持 SKILL.md 的工具可用；caveman-stats / caveman-compress 的 CLI 能力依赖上游 caveman 安装。
metadata:
  author: "JuliusBrussee/caveman 上游（MIT；仅采用技能面，引擎目录另为 BSL-1.1）"
  version: "1.0.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/JuliusBrussee/caveman/tree/main/skills/caveman-help"
---

# Caveman Help

Display this reference card when invoked. One-shot — do NOT change mode, write flag files, or persist anything. Output in caveman style.

## Modes

| Mode | Trigger | What change |
|------|---------|-------------|
| **Lite** | `/caveman lite` | Drop filler. Keep sentence structure. |
| **Full** | `/caveman` | Drop articles, filler, pleasantries, hedging. Fragments OK. Default. |
| **Ultra** | `/caveman ultra` | Extreme compression. Bare fragments. Tables over prose. |
| **Wenyan-Lite** | `/caveman wenyan-lite` | Classical Chinese style, light compression. |
| **Wenyan-Full** | `/caveman wenyan-full` | Full 文言文. Maximum classical terseness. |
| **Wenyan-Ultra** | `/caveman wenyan-ultra` | Extreme. Ancient scholar on a budget. |

Mode stick until changed or session end.

## Skills

| Skill | Trigger | What it do |
|-------|---------|-----------|
| **caveman-commit** | `/caveman-commit` | Terse commit messages. Conventional Commits. ≤50 char subject. |
| **caveman-review** | `/caveman-review` | One-line PR comments: `L42: bug: user null. Add guard.` |
| **caveman-compress** | `/caveman-compress <file>` | Compress .md files to caveman prose. Saves ~46% input tokens. |
| **caveman-help** | `/caveman-help` | This card. |

## Deactivate

Say "stop caveman" or "normal mode". Resume anytime with `/caveman`.

## Language

Keep user's language by default — reply in the language user writes, never switch regardless of example text or multilingual context elsewhere. Compress the style, not the language. Technical terms, code, commands, commit types, and exact error strings stay verbatim unless user ask for translation.

## Configure Default Mode

Default mode = `full`. Change it:

**Environment variable** (highest priority):
```bash
export CAVEMAN_DEFAULT_MODE=ultra
```

**Config file** (`~/.config/caveman/config.json`):
```json
{ "defaultMode": "lite" }
```

Set `"off"` to disable auto-activation on session start. User can still activate manually with `/caveman`.

Resolution: env var > config file > `full`.

## More

Full docs: https://github.com/JuliusBrussee/caveman

---

## 来源与署名 / Source & Attribution

本技能收录自 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman/tree/main/skills/caveman-help)（MIT）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
