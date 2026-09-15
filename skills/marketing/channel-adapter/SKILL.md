---
name: channel-adapter
description: "Adapt finished marketing copy into per-channel variants with machine-checked fit: built-in channel constraint table (word budgets, line limits, CTA counts, banned patterns) for Xiaohongshu notes, Douyin spoken scripts, WeChat moments, email subjects, and search-ad headlines; audit each variant with channel_fit_check.py. Final chain step of growth-marketing. Use when the user asks to 适配渠道 / 一稿多发 / 改成小红书 / 抖音口播稿 / 朋友圈文案 / 邮件标题 / channel variants. Do NOT use for writing the base copy (product-copywriter), nor for planning the campaign calendar (campaign-designer)."
license: Apache-2.0
compatibility: Python 3.8+ (channel_fit_check.py); no third-party dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: marketing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Channel Adapter

链条收口。一稿多发不是复制粘贴——**每个渠道有自己的物理约束**（字数预算/行数/CTA 数/语气规范）。约束错了平台直接限流或审核不过。本技能改写 + 机器校验双保险。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 基础文案 | ✓ | product-copywriter 的产出 |
| 目标渠道 | ✓ | xhs / douyin-spoken / moments / email-subject / search-ad（可多选） |
| 渠道角色 | ✗ | campaign-designer 的渠道矩阵角色（拉新/承接/私域） |

## 工作流

### 步骤 1：查渠道约束表（脚本内置，改写前先看）

| 渠道 | 硬约束 | 语气规范 |
|------|--------|----------|
| 小红书笔记 | 正文 ≤1000 字；标题 ≤20 字；CTA ≤1 处 | 像朋友分享，禁硬广腔 |
| 抖音口播 | 15 秒 ≈60 字；前 3 秒必须有钩子 | 口语短句，禁书面语 |
| 朋友圈 | ≤6 行；首行即钩子 | 人格化，禁排版符号堆砌 |
| 邮件主题 | ≤30 字符（移动端截断线） | 无感叹号堆叠 |
| 搜索广告标题 | ≤30 字符；含核心关键词 | 名词式卖点 |

### 步骤 2：按渠道改写（不是缩写）

- 约束是**物理边界**，适配是**重排信息架构**：小红书先场景后产品、抖音前 3 秒给冲突、搜索广告关键词前置
- 每个变体保留源文案的证据链数字——改写不改事实
- 双渠道同发时语气差异最大化（种草像朋友、搜索像说明书）

### 步骤 3：跑适配校验（机器守门）

```bash
python3 channel_fit_check.py --file variant.md --channel xhs
python3 channel_fit_check.py --text "30 字内的搜索标题" --channel search-ad
```

输出 JSON：字数/行数/CTA 数逐项 pass/fail + 修复建议。非零退出码 = 有 fail，改完重跑。

### 步骤 4：交付与链条闭环

交付：渠道变体包（每渠道一份 + 校验报告）。**链条收口**——"文案 → 战役 → 渠道变体"三步走完；某渠道表现差时带数据回 campaign-designer 调矩阵。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 小红书限流 | 硬广腔/违禁词 | 语气改分享体；极限词清零 |
| 抖音完播率低 | 前 3 秒没钩子 | 重写口播开头，冲突前置 |
| 邮件打开率低 | 主题被移动端截断 | 按字符上限重写主题 |
| 校验全过但转化差 | 事实无证据链 | 回 product-copywriter 补证据，不是渠道的锅 |

## 参考

直复营销框架出处见 product-copywriter 的 sources-and-methodology.md（同包共享）。
