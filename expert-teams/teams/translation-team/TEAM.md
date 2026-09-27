# Translation Team - 翻译与本地化交付专家团

> 场景：跨语言翻译与本地化全流程交付——从原文解析、术语统一、双向互译、技术文档翻译、文化适配到校对与 QA 收口，强门禁、术语一致、可追溯。

## 团队定位
- **输入**：待翻译原文（文档/软件界面/字幕/营销文案）、目标语种、术语表、风格要求、上下文领域
- **输出**：经术语统一、文化适配、校对与 QA 门禁后交付的目标语文本，附术语变更记录与长度/格式约束说明
- **核心价值**：10 人分工、术语先行（terminologist 建表）、互译并行、proofreader + qa-reviewer 双门禁收口，主理人只做拆解调度验收

## 成员架构（10 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 翻译统筹 | `translation-team-lead` | 任务拆解、语种分派、术语口径、阶段门禁 | 所有翻译/本地化需求入口 |
| 中英译 | `translation-zh-to-en` | 中文→英文直译与地道化，输出英文母语感译文 | "翻成英文"、"中译英" |
| 英中译 | `translation-en-to-zh` | 英文→中文流畅化，符合中文表达习惯 | "翻成中文"、"英译中" |
| 技术翻译 | `translation-technical` | 技术文档/API 文档/代码注释的术语准确翻译 | "技术文档翻译"、"API 文档本地化" |
| 本地化经理 | `translation-localization-manager` | 翻译项目排期、资源协调、交付物格式与流程把控 | "本地化项目"、"多语种排期" |
| 术语专家 | `translation-terminologist` | 建立/维护术语表、强制一致性、处理同义词与歧义词 | "术语统一"、"这个词怎么译" |
| 校对 | `translation-proofreader` | 错漏/语法/标点/数字单位/格式校对，不重写 | "校对译文"、"检查翻译错误" |
| 文化适配 | `translation-cultural-adaptor` | 文化梗/计量单位/日期格式/法规禁忌本地化改写 | "本地化"、"这个老外看不懂" |
| 翻译 QA | `translation-qa-reviewer` | 忠实度/流畅度/术语一致/漏译增译门禁（只读） | "翻译质量把关" |
| 字幕翻译 | `translation-subtitle` | 字幕时间轴适配、单行长度、口语化、断句 | "字幕翻译"、"视频字幕本地化" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程** | "一篇文档从原文到交付译文" | 拆解 → 术语（terminologist 建表）→ 翻译（zh-to-en/en-to-zh/technical 按语种并行）→ 文化适配（cultural-adaptor）→ 校对（proofreader）→ QA 门禁（qa-reviewer 清零 critical/major 后）→ 交付 |
| **W2 技术文档翻译** | "API 文档/技术手册本地化" | 拆解 → 术语（terminologist）→ technical 翻译 → proofreader 校对 → qa-reviewer 门禁收口 |
| **W3 字幕本地化** | "视频字幕多语化" | 拆解 → terminologist 术语 → subtitle 翻译（按时间轴断句）→ cultural-adaptor 口语化适配 → proofreader + qa-reviewer 门禁 |

## 协作机制
- **小步提交**：按章节/段落分批交付，每批可独立校验，避免一次性大稿返工
- **门禁规则（唯一口径）**：翻译完成 → proofreader 校对（错漏/格式）+ qa-reviewer 门禁（忠实度/术语/漏增译）并行 → **qa-reviewer 无 critical/major 后** → 主理人交付。文化类内容须经 cultural-adaptor 确认文化适配。
- **驳回机制**：同一批译文被驳回 2 次以上，停下来重查原文歧义或术语表，而非重复派单
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不亲自译稿，只做拆解、调度、验收
- 术语以 terminologist 术语表为唯一口径，禁止译者各自发挥同一术语
- 不脑补原文：原文歧义或缺失时显式标注 [原文存疑]，不擅自补全
- QA 结论以 qa-reviewer 回报为准，不脑补"应该没问题"

> **协作接口**：可对接 content-writing-team（译文回写为目标语内容）、software-dev-team（界面/文档随版本更新）、video-production-team（字幕时间轴对接）；典型跨场景触发词：文档本地化、软件界面翻译、字幕翻译、术语统一。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全流程翻译（Team-lead 为入口）
teams/translation-team/agents/translation-team-lead "把这份产品手册翻成英文，全流程走一遍"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/translation-team/agents/translation-zh-to-en "把这段中文翻成地道英文"
# teams/translation-team/agents/translation-en-to-zh "把这段英文翻成流畅中文"
# teams/translation-team/agents/translation-technical "翻译这份 API 文档"
# teams/translation-team/agents/translation-localization-manager "排一个多语种本地化计划"
# teams/translation-team/agents/translation-terminologist "建一份云计算术语对照表"
# teams/translation-team/agents/translation-proofreader "校对这份译文"
# teams/translation-team/agents/translation-cultural-adaptor "把这个营销文案做美式本地化"
# teams/translation-team/agents/translation-qa-reviewer "对这批译文做质量门禁"
# teams/translation-team/agents/translation-subtitle "把这集视频字幕翻成英文"
```
