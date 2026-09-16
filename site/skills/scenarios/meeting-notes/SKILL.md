---
name: meeting-notes
description: >
  Turn raw meeting transcripts or rough notes into structured minutes:
  decisions, action items with owners and deadlines, open questions, and a
  circulation-ready summary. Use when the user asks to 整理会议纪要 /
  会议记录 / notes from this transcript / summarize this meeting /
  把录音转的文字整理一下. Do NOT use for live transcription, audio-to-text
  conversion, or project status reports without meeting content.
license: Apache-2.0
compatibility: No special environment; accepts pasted transcript or notes.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Meeting Notes（文字记录 → 会议纪要）

机器优先原则：绝不编造负责人、日期或决议。文字记录里没有的，一律标 `<未明确>` 并列入待明确问题。

## 输入清单

| 输入 | 必填 | 默认 | 说明 |
|---|---|---|---|
| 文字记录 / 粗略笔记 | 是 | — | 粘贴的文本；有发言人标签更好，可选 |
| 会议元信息 | 否 | — | 日期、参会人、会议目的 |
| 读者 | 否 | 全体相关人 | 决定纪要的直白程度 |

缺文字记录时，只问一次：

> 请粘贴会议文字记录（语音转写稿即可）。可选告知：日期、参会人、
> 会议目标，以及纪要发给谁。

## 前置自检

无需探测环境——没有依赖、没有端点、没有环境变量。自检在输入侧：文字记录拿到了吗？没有就按上面只问一次，然后 STOP。绝不从"会议大概定了什么"的假设出发。

## 工作流

### 步骤 1：先分段，后总结

把文字记录按时间顺序切成议题块（话题每切换一次算一块），编号 T1…Tn，每块配一行话题标签。

预期：块数与讨论走向吻合；同一话题的碎片要合并。

### 步骤 2：区分决议与讨论

对每个块，把每段交流归类为：
- **决议**：有明确结论且无人反对（记录原话关键句作为证据）
- **讨论**：有交换但无结论 → 归入 open questions
- **行动**：有人说"我来/你去/下周前" → 进入步骤 3

预期：零漏分类；有歧义时，把原句引用进待明确问题，而不是猜意图。

### 步骤 3：行动表（交付物的核心）

| 行动项 | Owner | 截止 | 来源议题 | 状态 |
|---|---|---|---|---|

规则：Owner 必须是 transcript 里点名的人，否则写 `<待指派>`；
deadline 缺失写 `<待定>`；每行必须能在 T 编号中找到出处。

### 步骤 4：按固定结构成稿

```text
# 会议纪要 YYYY-MM-DD <主题>
参会：<名单或<未明确>>
## 一页结论
<3–5 条最重要的决议，每条一行>
## 决议明细
<按 T 编号，决议+证据原话>
## 行动项
<Step 3 表格>
## 待明确问题
<无主/无结论事项，含需要谁来拍板>
```

### 步骤 5：交付前一致性检查

核对：每条决议都有证据原话；每个行动项都有负责人+截止时间或显式占位符；总长度 ≤ 文字记录的 1/3。发现违规回到步骤 2–3 修，不许直接删条目。

## 失败处置表

| 现象 | 可能原因 | 处置 |
|---|---|---|
| 文字记录无发言人标签 | 原始 ASR 输出 | 从内容推断角色，不确定的归属标 `<推断>` |
| 同一话题出现两条冲突"决议" | 漏看了后面的反转 | 两条都保留并带时间戳，在待明确问题中标注 |
| 文字记录在话题中途截断 | 输入不完整 | 在结尾明确标注截止到 Tn |
| 用户要求弱化某条决议 | 带倾向的改写 | 交付忠实版本；改不改由用户自己定 |

## 交付标准

成功 = 纪要严格遵循步骤 4 的骨架，行动表完整，零编造事实。缺任何一项即未完成——如实说明。

## 链条衔接（下游建议）

本技能属 office / productivity 类单点技能；产出的 action items 可继续喂给 excel-assistant 做跟踪表，或作为 resume-tailor 的项目经历素材。建议在 skill_chains.json 中新增 office（或 productivity）域并登记本技能。衔接仅为文字描述。
