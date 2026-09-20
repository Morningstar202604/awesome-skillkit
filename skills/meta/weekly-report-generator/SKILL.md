---
name: weekly-report-generator
description: >
  Auto-draft a weekly report from `git log` + `git diff --stat` over a
  look-back window, structured into the three paragraphs every company
  expects (done / blockers / next week), then let the human fill in the
  qualitative bits. Use when the user asks for 周报 / 日报 / 周报模板 /
  自动写周报 / weekly report / status update / sprint 总结. Do NOT use for
  monthly business reviews (different scope) or for performance/HR narratives
  (this is a work-log, not a performance doc).
license: Apache-2.0
compatibility: 纯本地 git 操作；不联网、不碰 remote；默认 dry-run；需 python3 + git
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Weekly Report Generator（周报自动生成）

把一周的 git 活动拉出来，自动填好"做了什么"段，剩下的"卡在哪 / 下周计划"
留占位给你人工补。解决的是：**周报最烦的不是写，是"想不起来这周到底干了啥"**——
本技能替你回忆，你只负责定性判断。

> 红线：纯本地 git + 文件系统；不联网、不 push；默认 dry-run，`--write` 才落盘。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 回溯天数 | 否 | 默认 7 天；周报/双周报可调 |
| 仓库路径 | 否 | 默认当前目录 |
| 作者名 | 否 | 默认 `agent` |
| 卡点 / 下周 | 否 | 不传则留占位；可走 `--input report.json` 结构化喂 |

## 前置自检

1. 当前目录是 git 仓库吗？（脚本会检查 `.git` 存在）
2. 这一周有 commit 吗？没有就"做了什么"段是空的——正常，别误判成 bug。
3. 公司周报有固定模板？把模板段落名对齐 `done/blockers/next`，或用 `--input` 喂。

## 工作流

```bash
# 1. 干跑：看自动填好的"做了什么"段
python3 scripts/gen_report.py --days 7 --repo . --author 张三

# 2. 喂结构化输入（把"卡点/下周"也写好）
python3 scripts/gen_report.py --days 7 --input report.json --write -o weekly.md

# 3. 双周报
python3 scripts/gen_report.py --days 14 --author 张三
```

`report.json` 字段（可选）：
```json
{
  "done": ["修复登录态漂移", "补 2 个安全扫描器"],
  "blockers": "依赖审批流程慢，阻塞 P1 上线",
  "next": "完成 e2e 脚手架接入 CI"
}
```

## 交付标准

- 三段齐全：做了什么（git 自动）/ 卡在哪（人工）/ 下周（人工）
- "做了什么"段按日期分组，每条 = `date author: subject`
- 文件能直接贴进邮件 / 文档系统

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| `is not a git repo` | 路径不对 | 传 `--repo <路径>` |
| "做了什么"段空 | 这一周没 commit | 正常；调大 `--days` 或人工补 |
| 段落对不上公司模板 | 段落名不一样 | 用 `--input` 喂对应字段 |
| 作者名乱 | git 配置 author 不一致 | 传 `--author` 覆盖 |
| 想要月报 | 窗口太长 commit 太多 | 改 `--days 30` 并手动精简 |

## 参考

- 段落约定与 JSON 字段：[references/report-fields.md](references/report-fields.md)

## 链路位置

- 上游：日常 git 工作
- 下游：`meeting-notes`（把周报转成团队同步纪要）
