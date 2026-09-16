---
name: chat-prompt-engineer
description: "Engineer and audit prompts for conversational AI assistants (Doubao, ChatGPT, Kimi, DeepSeek, in-app chat models): the five-element formula (role + background + task + requirements + format) for one-shot task prompts, the five-section skeleton (persona / capability-flow / constraints / output-format / boundary) for agent system prompts, and reverse constraints that cut filler. Two modes: write a prompt from a rough request, or audit an existing prompt / system prompt and report missing elements. Use when the user asks to 写提示词 / 豆包提示词 / 提示词优化 / 智能体人设 / system prompt / 提示词审计 / prompt audit / 让 AI 听话. Do NOT use for text-to-video or image-generation prompts (those structures live in the video-prompt-engineer skill), nor for agent framework code (that is agent-designer)."
license: Apache-2.0
compatibility: Pure prompt-based; the bundled prompt_audit.py needs Python 3.8+ only.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: chat
  pattern: dual-mode
  tier: standard
  verified-date: "2026-09-14"
---

# Chat Prompt Engineer

写、审对话式 AI 助手（豆包 / ChatGPT / Kimi / DeepSeek 等）的提示词。核心是**五要素公式**——聊天模型不读心，缺一个要素它就自由发挥一个，自由发挥就是废话来源。与 `video-prompt-engineer` 的六槽位同构：那边管"画面完整"，这边管"意图完整"。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 模式 | ✓ | `task`（一次性任务提示词）\| `agent`（智能体 system prompt） |
| 粗需求 | write ✓ | 用户原话，哪怕只有一句："帮我写个小红书文案" |
| 目标平台 | ✗ | 默认豆包系通用写法；指定平台套方言（见 references/platform-dialects.md） |
| 受众 / 用途 | ✗ | 缺时主动问一句，不猜 |
| 待审 prompt | audit ✓ | 原文粘贴 |

缺输入时一次性问齐："请提供：① 模式（task 一次性任务 / agent 智能体人设）② 粗需求或待审 prompt 原文 ③ 目标平台与受众（可选，缺则按豆包系通用）。"

## 前置自检

- write 模式：粗需求里有**动词明确的任务**吗？"帮我搞一下这个"没有任务动词，先追问。
- audit 模式：待审文本拿到了吗？没有就先要，不要凭记忆审计。
- agent 模式：确认用户要的是**人设契约**（长期行为规范）而不是单次任务——两者结构完全不同。

## 工作流

### 步骤 1（task 模式）：按五要素填空

```text
[角色 role] + [背景 background] + [任务 task] + [要求 requirements] + [格式 format]
```

规则（每条都有翻车案例背书）：

- 角色**具体到岗位+经验**："你是一名面向新手的 AI 工具教程编辑"，不是"你是助手"
- 背景**回答给谁看、干什么用**——用途直接决定输出风格，"用途是商务邮件"一句顶十句语气词
- 任务动词**具体**："把这段文案改成适合小红书发布的版本"，不写"优化一下"
- 要求**先写反向约束**：字数硬限、禁用词表、"删掉任何一句后意思不完整才算合格"——"不要做什么"比"要做什么"更砍废话
- 格式**锁死结构**："核心结论 1-2 句 → 分点展开 ≤5 点 → 行动建议"，模型输出从此免排版

预期：产出 prompt 五要素齐全；跑 `python3 scripts/prompt_audit.py --prompt "<文本>"` 返回 5/5。

### 步骤 2（agent 模式）：按五段骨架写 system prompt

```markdown
# 人设
你是 [身份 + 领域 + 语气]，具体到"像什么人"。

# 能力与流程
1. [能力名]：什么时候触发 + 怎么做 + 返回什么
2. ...（把思考顺序写成 Step-by-Step，这是智能体变聪明的核心）

# 约束
- 禁止 [AI 腔词汇表]
- 不得 [越界行为]

# 输出格式
[固定结构模板]

# 边界处理
- 超出范围时 [反问 / 拒答 / 免责声明]，不确定时不编造
```

五段对应关系：人设≈CO-STAR 的 Role，能力与流程≈Skills&Tools+Workflow，约束与边界≈Constraints 的正反两面。**先能力后约束、最后兜底**——只写"你是谁"的 system prompt 是空壳。

### 步骤 3（audit 模式）：跑结构审计

```bash
python3 scripts/prompt_audit.py --prompt "<待审文本>"            # task 模式五要素
python3 scripts/prompt_audit.py --prompt "<system prompt>" --mode agent   # 五段骨架
```

预期：输出 JSON，含每个要素 `hit/miss` 与缺失清单。miss 项按要素语义补齐，不堆字数。

### 步骤 4：迭代与交付

长内容任务套**三轮迭代**：第一轮只要大纲骨架 → 第二轮选定部分展开成正文 → 第三轮抛光（删重复、被动改主动、开头加钩子）。一次让模型写全文 = 自己给自己找三轮返工。

## 交付标准

- 产物（task）：五要素齐全的 prompt 原文 + 要素标注版。
- 产物（audit）：JSON 审计报告 + 修复前后对比。
- 产物（agent）：五段齐全的 system prompt + 建议的开场白与预置问题各 3 条（Coze/豆包智能体发布件）。
- 保存位置：直接输出在对话中（本技能不写文件）。
- 完整性验证：task 产物跑 `python3 scripts/prompt_audit.py --prompt "<文本>"` 返回 5/5；agent 产物五段标题齐全；方言条目使用前已按 platform-dialects.md 的核实步骤确认（VERIFY BEFORE USE）。

## 五要素词典（最快查表）

| 要素 | 常用句式 |
|------|----------|
| 角色 | "你是一名 [领域] 的 [岗位]，擅长 [风格]" |
| 背景 | "读者是 [人群]，用途是 [场景]，材料如下：…" |
| 任务 | "帮我把 [输入] 变成 [产出]"（动词具体） |
| 要求 | "字数 ≤N；禁用词：…；每句有信息量；开头直接说事" |
| 格式 | "输出为 [表格/清单/JSON]，结构：结论 → 分点 → 行动" |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 输出全是"在当今社会"式套话 | 缺反向约束 | 加禁用词表 + "开头直接说事，不许铺垫背景" |
| 每次对话风格都不一样 | 缺角色锚定 + 格式锁定 | 把五要素里的角色与格式段复制进对话开头，只换任务内容 |
| 长文逻辑断 | 一次性写全文 | 拆三轮：大纲 → 展开 → 抛光 |
| 智能体答非所问乱编 | system prompt 无边界段 | 补"超出范围时反问，不确定时不编造" |
| 审计 5/5 但输出仍差 | 结构对、选词弱 | 要求段换具体数字与词表，把"生动一些"换成可判定的约束 |

## 参考

- [platform-dialects.md](references/platform-dialects.md) —— 豆包 / Coze / CO-STAR 方言结构与核实链接
- [sources-and-methodology.md](references/sources-and-methodology.md) —— 方法论出处与致谢

## 链条衔接（下游建议）

本技能独立于其它域，是「提示词工程」单点技能，可被任意域的编排器在「先写好 prompt 再执行」时调用；其结构与 video-prompt-engineer 同构但互不链接。建议在 skill_chains.json 中新增 chat 域并登记本技能，例如 chat 域的 prompt_audit 链：chat-prompt-engineer（task / agent 两模式自我审计）。
