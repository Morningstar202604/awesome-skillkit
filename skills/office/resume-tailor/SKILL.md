---
name: resume-tailor
description: >
  Tailor a resume to one specific job description: extract JD requirements,
  build a gap matrix, rewrite bullets with metrics (STAR), and output an
  ATS-safe document plus an edit changelog. Use when the user asks to 改简历 /
  简历定制 / 针对这个岗位改简历 / tailor my resume for this JD /
  optimize my CV. Do NOT use for writing cover letters, LinkedIn profiles,
  or fabricating experience.
license: Apache-2.0
compatibility: No special environment needed; accepts plain text or pasted resume.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Resume Tailor（简历 + JD → 定制版）

一轮只处理一个 JD。机器优先原则：每处改动必须能追溯到 JD 的某一行，或原简历中的某条证据。虚构是硬性禁令——见红线。

## 输入清单

| 输入 | 必填 | 默认 | 说明 |
|---|---|---|---|
| 简历文本/文件 | 是 | — | 纯文本优先 |
| 岗位描述 | 是 | — | 粘贴完整 JD，不是只给职位名 |
| 目标语气 | 否 | 简洁量化 | 如：外企英文 / 国内互联网 |

缺必填项时，只问一次：

> 请提供：① 现有简历全文；② 目标岗位的完整 JD（含任职要求）。
> 可选：希望中文还是英文、有无特别想突出的项目。

## 前置自检

无需探测环境——没有依赖、没有端点、没有环境变量。自检在输入侧：完整简历和完整 JD 都拿到了吗？缺任一项就按上面只问一次，然后 STOP。只有职位名的 JD（"帮我改简历，投产品经理"）不算 JD——先要全文，步骤 1 才可能做。

## 红线（硬性禁令，不可协商）

1. 不得虚构经历、职级、证书或数字。量化只能来自原简历已有事实或向用户提问确认。
2. 不得隐瞒真实性问题的美化（如把实习写成工作）。
3. 原因：背调与面试深挖会放大任何造假，代价是 offer 作废乃至行业口碑。

## 工作流

### 步骤 1：提取 JD 要求

建一张两列表：硬性要求（学历/年限/必备技能）｜软性优先项。

预期：5–12 行，每行引用 JD 原话。

### 步骤 2：差距矩阵

把 JD 每一行对照简历判定：匹配(有证据) / 部分(需强化表述) /
缺失(只能诚实留白或建议用户补充真实素材)。

预期：没有未判定的行。

### 步骤 3：重写条目

对"部分"匹配项，用 STAR + 数字重写：
`动词 + 做了什么 + 方法/规模 + 可验证结果`。

改写示例——前："负责公众号运营"；
后："独立运营公众号（3 个月），周更 2 篇，粉丝从 1.2k 增至 4.6k（+283%）"。

源材料里没有的数字，插入 `<待你确认：具体数值>`，绝不编一个。

### 步骤 4：ATS 卫生检查

单栏排版；标准标题（教育经历/工作经历/项目/技能）；
内容不放表格、文本框或图形；在真实的前提下从 JD 镜像关键词；
文件命名 `姓名_岗位_简历.pdf`。

### 步骤 5：交付两件产物

① 定制后的简历全文；② `edit_log.md`，每条改动记为
`原文 → 改后 ← JD依据`，另附一份只有用户能补的待补充清单
（数字、项目）。

预期：用户能对每处改动逐条接受或拒绝。

## 失败处置表

| 现象 | 可能原因 | 处置 |
|---|---|---|
| JD 每行都超出简历证据 | 匹配度太低 | 如实说明；建议相邻岗位而不是注水 |
| 用户要求夸大数字/编造证书 | 触碰红线 | 拒绝该改动，重申禁令，提供诚实的强化方案 |
| 定制后简历过长 | 遗留的无关板块 | 按 JD 相关度裁剪，每处删减记入 edit_log |
| 关键技能完全缺失 | 真实差距 | 加入待补充清单，附一条快速补齐的具体路径 |

## 交付标准

成功 = 定制后的简历文本 + 每条改动可追溯的 `edit_log.md`，零不可验证的表述。缺任何一项即未完成——如实说明。

## 链条衔接（下游建议）

本技能属 office / productivity 类单点技能；定制后的简历可继续用 excel-assistant 做版本对照、meeting-notes 风格整理。建议在 skill_chains.json 中新增 office（或 productivity）域并登记本技能。衔接仅为文字描述。

## 参考

- 本技能为纯提示型，无需外部参考文件。
