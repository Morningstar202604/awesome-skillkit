# Agent 系统使用手册 - AGENTS.md

> **18 个专家团队 + 核心单兵** = 220 个 agent（团队成员 219 + project-director）。按**场景**组织，每个团队自包含，不拆单兵池。

> **路径基准**：本手册及本目录所有文档中的相对路径（`teams/...`、`skills/...`、`SKILLS_INDEX.md`、`orchestration-protocol.md`、`project-director` 等）均以**本目录（`expert-teams/`）为根**；在 `awesome-skillkit` 仓库根引用或派发子 agent 时加 `expert-teams/` 前缀（如 `expert-teams/teams/hr-team/agents/hr-team-lead`、`expert-teams/orchestration-protocol.md`）。

---

## 快速开始

### 1. 复杂/跨场景需求 → 找 **project-director**
> 「帮我写篇论文并配套实现代码」「做个 Web 应用还要写技术文档」

在支持子 agent 调度的框架中，把 `project-director` 作为入口派发，它会自动路由到对应团队：
```text
project-director   # 输入："帮我写篇论文并配套实现代码"
```

### 2. 明确单一场景 → 直调 Team-lead
> Agent ID 为相对**本目录**的路径（即 `teams/<team>/agents/<name>`，平台中立标识符；在仓库根使用时加 `expert-teams/` 前缀）；短名不可用（直接用 `academic-team-lead` 这类短名会找不到对应定义）。

在支持子 agent 调度的框架中，按路径 ID 派发 Team-lead：
```text
<team-lead-path>   # 输入："任务描述"
```
| 场景 | Team-lead 路径 ID | 典型触发 |
|------|-------------------|----------|
| 学术论文全流程 | `teams/academic-paper-team/agents/academic-team-lead` | "写论文"、"投稿"、"审稿回复" |
| Web 应用全链路 | `teams/fullstack-web-team/agents/fullstack-team-lead` | "做 Web 应用"、"上线"、"重构" |
| 数学建模国赛 | `teams/math-modeling-team/agents/math-team-lead` | "托管国赛赛题"、"建模求解"、"赛前特训" |
| 软件开发交付 | `teams/software-dev-team/agents/software-team-lead` | "实现 XX 模块"、"评审 PR"、"补测试" |
| 视觉设计 | `teams/visual-design-team/agents/visual-team-lead` | "做海报"、"设计Logo"、"电商主图"、"信息图" |
| 内容写作 | `teams/content-writing-team/agents/content-team-lead` | "写公众号"、"小红书文案"、"短视频脚本"、"标题" |
| 视频制作 | `teams/video-production-team/agents/video-team-lead` | "做短视频"、"宣传片"、"口播"、"分镜"、"剪辑" |
| 数据分析 | `teams/data-analysis-team/agents/data-analysis-team-lead` | "分析留存"、"A/B实验"、"数据看板"、"指标体系" |
| 市场营销 | `teams/marketing-team/agents/marketing-team-lead` | "营销方案"、"活动策划"、"品牌定位"、"增长黑客" |
| 电商运营 | `teams/ecommerce-ops-team/agents/ecommerce-ops-team-lead` | "选品"、"Listing优化"、"店铺运营"、"定价策略" |
| 产品管理 | `teams/product-team/agents/product-team-lead` | "写PRD"、"用户调研"、"产品路线图"、"竞品分析" |
| 财务会计 | `teams/finance-team/agents/finance-team-lead` | "财务分析"、"预算编制"、"税务筹划"、"成本控制" |
| 人力资源 | `teams/hr-team/agents/hr-team-lead` | "写JD"、"面试评估"、"绩效方案"、"培训设计" |
| 法律合规 | `teams/legal-compliance-team/agents/legal-team-lead` | "审查合同"、"个保法合规"、"知识产权"、"劳动法" |
| 翻译本地化 | `teams/translation-team/agents/translation-team-lead` | "翻译文档"、"产品本地化"、"字幕翻译"、"术语管理" |
| 教育培训 | `teams/education-training-team/agents/education-team-lead` | "设计课程"、"出题"、"课件制作"、"学习路径" |
| 音频播客 | `teams/audio-podcast-team/agents/audio-team-lead` | "做播客"、"音频剪辑"、"配音指导"、"音效设计" |
| 游戏设计 | `teams/game-design-team/agents/game-team-lead` | "游戏设计"、"数值平衡"、"关卡设计"、"GDD" |

### 3. 团队内部单兵 → 经 Team-lead 按 Workflow 派发（子 agent）
其余成员不作为入口直调；由 Team-lead 按 Workflow 在内部编排派发。仅当用户明确指定单兵时，Team-lead 可在支持子 agent 调度的框架中按路径 ID 直达：
```text
# 子 agent 调度同样按路径 ID 派发（示例）
teams/academic-paper-team/agents/academic-topic-strategist
teams/academic-paper-team/agents/academic-writer
teams/fullstack-web-team/agents/core-architect
teams/fullstack-web-team/agents/fullstack-frontend-engineer
teams/math-modeling-team/agents/math-modeler
teams/math-modeling-team/agents/math-solver
teams/software-dev-team/agents/software-architect
teams/software-dev-team/agents/software-tester
```
- 学术团队前缀：`teams/academic-paper-team/agents/`
- 全栈团队前缀：`teams/fullstack-web-team/agents/`
- 数学建模团队前缀：`teams/math-modeling-team/agents/`
- 软件开发团队前缀：`teams/software-dev-team/agents/`
- 视觉设计团队前缀：`teams/visual-design-team/agents/`
- 内容写作团队前缀：`teams/content-writing-team/agents/`
- 视频制作团队前缀：`teams/video-production-team/agents/`
- 数据分析团队前缀：`teams/data-analysis-team/agents/`
- 市场营销团队前缀：`teams/marketing-team/agents/`
- 电商运营团队前缀：`teams/ecommerce-ops-team/agents/`
- 产品管理团队前缀：`teams/product-team/agents/`
- 财务会计团队前缀：`teams/finance-team/agents/`
- 人力资源团队前缀：`teams/hr-team/agents/`
- 法律合规团队前缀：`teams/legal-compliance-team/agents/`
- 翻译本地化团队前缀：`teams/translation-team/agents/`
- 教育培训团队前缀：`teams/education-training-team/agents/`
- 音频播客团队前缀：`teams/audio-podcast-team/agents/`
- 游戏设计团队前缀：`teams/game-design-team/agents/`
- core-* 单兵（core-architect / core-code-reviewer / core-security-auditor / core-test-engineer）在 fullstack 目录；core-researcher、core-fact-checker（跨团队通用事实核查官，只读）在 academic 目录

---

## 团队 Workflow 对照表

### Academic Team（学术论文）
| Workflow | 触发场景 | 执行 Phases |
|----------|----------|-------------|
| **W1 全链路** | "写完整论文"、"从选题到投稿" | 1→2→3(并行分支)→4→5→6→7→8 |
| **W2 快速选题** | "这个题行不行"、"缺什么创新" | 1 |
| **W3 稿件打磨** | "已有初稿要润色/查逻辑/出图" | 3(并行分支)→4 |
| **W4 审稿备战** | "拿到审稿意见要回复" | 5→7 |
| **W5 投稿定稿** | "投哪个刊"、"格式对不对" | 6→8 |

### Fullstack Team（全栈 Web）
| Workflow | 触发场景 | 执行 Phases |
|----------|----------|-------------|
| **W1 全链路** | "从零做个 Web 应用上线" | 1→2→3→4→5→6→7 |
| **W2 绿地脚手架** | "快速起步，先跑起来" | 1+2+3（不可跳过 Phase 2） |
| **W3 加固既有代码** | "安全/性能/质量/无障碍加固" | 5+6 |
| **W4 仅接口与数据** | "只做 API 设计 + 数据建模" | 2 |
| **W5 发布就绪** | "冲刺上线，CI/CD/部署" | 4 |

### Math Modeling Team（数学建模国赛）
| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **A 完整国赛** | "拿到赛题、要全程托管" | Phase 0(选题+数据/文献并行)→1(建模)→2(求解→出图串行)→3(写作)→4(复现+质检并行) |
| **B 单题攻坚** | "只卡在某问/某步" | 按卡点直派对应成员（选题→lead；数据→data-analyst；建模→modeler；求解→solver；写作→writer；终检→qa） |
| **C 赛前特训** | "还没比赛，练真题/补短板" | 指定真题跑通 Phase 0→1→2→3，Phase 4 自查打分 |

### Software Dev Team（软件开发交付）
| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程** | "新功能从零到交付" | 拆解 → 设计(architect+api+database 并行) → 实现(frontend/backend 并行) → 门禁(security+qa+reviewer+quality 并行) → tester 收口(全绿才过) → 交付 |
| **W2 仅设计** | "只出架构方案/接口契约" | 拆解 → 设计（ADR + api 契约 + 数据模型） |
| **W3 仅评审+测试** | "对现有代码跑门禁" | 门禁四员并行 → tester 收口 |

### Visual Design Team（视觉设计）
| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 完整设计流程** | "从零做一套品牌视觉/活动主视觉" | brief拆解 → 色彩字体体系 → 主视觉/KV → 延展物料(电商/社媒/印刷) → 评审质检 → 素材交付 |
| **W2 单品类设计** | "只做一张海报/一个Logo/一套电商图" | 按品类直派对应设计师（海报→poster-designer；Logo→logo-designer；电商→ecommerce-designer） |
| **W3 评审质检** | "对已有设计稿做评审/合规检查" | design-reviewer 只读评审 → asset-manager 素材与版权合规检查 |

### Content Writing Team（内容写作）
| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 完整内容生产** | "从选题到发布的全流程内容" | 策略选题 → 标题工程 → 创作(长文/社媒/文案) → 编辑校对 → 多平台适配 → 质检合规 |
| **W2 单篇写作** | "只写一篇公众号/小红书/脚本" | 按体裁直派（长文→article-writer；社媒→social-media-writer；脚本→short-video-scriptwriter；文案→copywriter） |
| **W3 质检合规** | "对已有稿件做质检/合规/查重" | content-reviewer 只读质检 → editor 结构优化 |

### Video Production Team（视频制作）
| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 完整视频制作** | "从策划到成片的全流程" | 策划脚本 → 分镜 → 制作(动画/拍摄) → 剪辑 → 包装动效 → 音频 → 字幕 → 调色 → 质检 → 数据复盘 |
| **W2 短视频快产** | "快速出一条短视频/信息流" | short-form-expert 主导：钩子脚本 → 快剪 → 字幕 → 质检 |
| **W3 成片质检复盘** | "对已有成片做质检/数据复盘" | video-quality-reviewer 只读质检 → video-performance-analyst 完播与数据复盘 |

---

## 交互协议（必读）

### 输入规范
- Team-lead 派发成员时，自动传递 `checkpoint-N.md` + 上阶段完整产出
- 成员声明 `## 输入规范`，说明接收什么格式/字段
- 用户直调成员时，需自备上一阶段产出或告知「无前序」

### 交接模板（4 块，缺一不可）
1. **阶段产出** —— 完整原文/代码/报告
2. **关键决策** —— 3 条，含取舍理由/代价
3. **遗留风险** —— H/M/L 分级 + 是否需下一环节兜住
4. **给下一阶段** —— 3 个重点，明确交接什么、别漏什么

### 监测与断路
- **停滞**：产出为空/重复/无关
- **死循环**：连续 2 次同义反复
- **卡死**：连续 **3 轮对话无实质新增**
- 触发 → 立即报告卡点 → 断路切换（换成员/降级 Workflow/拆任务/回退 checkpoint/请用户决策）

### 技能调用
- Phase 开工前扫描 `SKILLS_INDEX.md`，关键词匹配 + `team_context`
- **调用失败/未安装 → 退回通用经验，不阻塞**
- Team-lead 可指定优先 skill，成员必须遵守

---

## 文件结构

```
expert-teams/（awesome-skillkit 子目录；本目录即「路径基准」的根；纯 Markdown 资产，平台中立）
├── project-director.md          # 总调度入口（18 场景路由）
├── orchestration-protocol.md    # 共享编排协议（门禁/回炉≤2/断路/交接四块，18 lead 必须引用）
├── export-agents.py             # 导出脚本：导出 system prompt 文本 / JSON 到 dist/
├── export-platforms.py          # 平台原生包：OpenCode / Claude Code / Cursor / Gemini → dist/
├── effectiveness.py             # 团队有效性门禁（verify.py 第 7 节调用）
├── tests/                       # 单测：导出产物结构 + 有效性门禁（python -m unittest）
├── build-site.py                # 官网生成：从仓库实装统计生成 site/index.html
├── dist/                        # 导出产物（gitignore，不入库）
├── SKILLS_INDEX.md              # 技能索引（100 个，含归属团队）
├── AGENTS.md                    # 本文档
├── skills/                      # 通用 skill（14 个，全团队共用）
├── site/                        # 官网：template.html + index.html（生成产物）
└── teams/                       # 18 支团队（219 专家）
    ├── academic-paper-team/     # 19 专家 · 7 skill
    ├── fullstack-web-team/      # 19 专家 · 11 skill
    ├── math-modeling-team/      # 9 专家 · 2 skill
    ├── software-dev-team/       # 12 专家 · 绑定 3 通用 skill
    ├── visual-design-team/      # 14 专家 · 6 skill
    ├── content-writing-team/    # 14 专家 · 6 skill
    ├── video-production-team/   # 14 专家 · 6 skill
    ├── data-analysis-team/      # 12 专家 · 5 skill
    ├── marketing-team/          # 12 专家 · 5 skill
    ├── ecommerce-ops-team/      # 12 专家 · 5 skill
    ├── product-team/            # 12 专家 · 5 skill
    ├── finance-team/            # 10 专家 · 4 skill
    ├── hr-team/                 # 10 专家 · 4 skill
    ├── legal-compliance-team/   # 10 专家 · 4 skill
    ├── translation-team/        # 10 专家 · 4 skill
    ├── education-training-team/ # 10 专家 · 4 skill
    ├── audio-podcast-team/      # 10 专家 · 4 skill
    └── game-design-team/        # 10 专家 · 4 skill
    # 每支团队结构：agents/（专家 .md）+ skills/（SKILL.md）+ TEAM.md（编排）
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 需求同时涉及论文+代码 | 找 `project-director`，并行派发两团队 |
| 想跳过某 Phase | 告知 Team-lead，需用户确认裁剪 |
| 成员卡死/死循环 | Team-lead 自动触发断路，汇报给用户 |
| Skill 未安装 | 自动回退通用经验，日志记录 fallback |
| 想用特定 skill | 在需求中指定「优先用 xxx skill」 |
| 需要回滚 | 宿主具备 git/bash 时：Team-lead 按 `checkpoint-N.md` 记录回退（`git tag phase-N` 固化）；无该能力宿主按 checkpoint 记录人工回退（分层见 `orchestration-protocol.md`） |
| 版本追踪 | fullstack / academic 团队 lead 在 Phase 结束写 `versions.md`（非全局保证，其余团队按需） |

---

## 维护清单

- [ ] 新增团队/成员 → 更新 `SKILLS_INDEX.md` + `AGENTS.md` + 对应 `TEAM.md`
- [ ] Skill 版本升级 → 更新 `SKILLS_INDEX.md` 优先级/位置
- [ ] Workflow 变更 → 同步更新 Team-lead 文档 + `TEAM.md`
- [ ] 核心单兵能力变更 → 同步更新 `project-director` 路由表
