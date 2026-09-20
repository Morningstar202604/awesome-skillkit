---
name: session-handoff
description: >
  Compress a long in-flight session into a cold-start handoff doc so a fresh
  agent (or a future-you, or a teammate) can pick up with zero context: goal,
  done, next, gotchas, key files, one-page cheat sheet. Use when the user asks
  to 交接 / 会话交接 / 把现状写清楚给下一个 / handoff / 冷启动接手 / 上下文压缩.
  Do NOT use for long-term memory across projects (use memory-architect) or for
  final deliverable reports (this is an internal relay, not a finished doc).
license: Apache-2.0
compatibility: 纯本地 Markdown 生成；离线、无网络、无凭证；默认 dry-run
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Session Handoff（长会话冷启动交接）

把一段跑到一半的长会话，压成一份**下一个 agent 零上下文也能接手**的
交接文档。改造自 mattpocock/skills 的 `handoff` 思路，裁剪为离线 Markdown
生成器 + 一份"一页纸速记"骨架。

核心判断：**接手方最大的成本不是读代码，是"猜你做到哪、卡在哪、别踩哪些坑"**。
本技能把这三件事显式化：`下一步(按序)`、`已知坑/不要重蹈`、`关键文件路径`。

> 红线：默认 dry-run 打印预览；`--write` 才落盘；零网络、零凭证。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 目标 | 是 | 原始意图（为什么开始这活） |
| 已完成 | 是 | 做了什么、到哪一步 |
| 下一步 | 是 | 按序待办 |
| 已知坑 | 强烈建议 | 踩过的坑 / 别重蹈的弯路 |
| 关键文件 | 建议 | `--file` 可重复传路径 |
| 运行/验证方式 | 建议 | 接手方怎么跑起来、怎么验 |

结构化输入也可走 `--input handoff.json`（字段：title/done/next/gotchas/files/repo/verify/blocker），优先级高于同名命令行参数。

## 前置自检

1. "下一步"是否**按序可执行**（不是"继续做"这种空话）？
2. "已知坑"是否具体到能避开（不是"注意别出错"）？
3. 关键文件是否给的是**路径**而非"某个文件"？

## 工作流

```bash
# 1. 干跑：预览交接文档
python3 scripts/make_handoff.py --title "P1 域修复" --goal "修 domain 三方不一致" \
  --done "git mv 5 个 skill；build 143→145" --next "补 CHANGELOG；跑 validate" \
  --gotcha "heredoc 里 Python r''' 会撞 shell EOF" --file skills/ --repo awesome-skillkit

# 2. 落盘
python3 scripts/make_handoff.py ... --write -o handoff.md

# 3. 走 JSON 结构化输入
python3 scripts/make_handoff.py --input handoff.json --write -o handoff.md
```

## 交付标准

- 六段齐全：目标 / 已完成 / 下一步 / 已知坑 / 关键文件 / 一页纸速记
- "下一步"逐条可执行、有序号
- 接手方只读这份 md，能说出：在哪个仓库、怎么跑、现在卡哪、别踩什么坑

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| 段落全 [待填] | 没喂信息 | 至少喂 goal/done/next |
| JSON 输入没生效 | 字段名拼错 | 按 references/handoff-fields.md 对齐 |
| 交接文档太薄 | "下一步"是空话 | 改成动词开头的有序步骤 |
| 接手方还是懵 | 关键文件没给路径 | `--file` 传绝对/仓库相对路径 |

## 参考

- JSON 字段说明：[references/handoff-fields.md](references/handoff-fields.md)

## 链路位置

- 上游：任意跑到一半的 agent 会话
- 下游：`memory-architect`（要把本次经验沉淀成长期记忆时）
