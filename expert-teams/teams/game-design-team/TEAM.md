# Game Design Team - 游戏设计交付专家团

> 场景：游戏设计全流程交付——从玩法设计、关卡、数值平衡、叙事、经济系统到原型开发、美术指导与 QA 评审，强文档、可原型、重平衡。

## 团队定位
- **输入**：游戏概念/题材、目标平台、核心玩法卖点、玩家画像、范围约束
- **输出**：经评审门禁的 GDD、玩法文档、关卡/数值/经济方案、可玩原型与美术方向，附平衡表与测试结论
- **核心价值**：10 人分工、玩法先行、数值与经济并行、原型验证、qa + reviewer 双门禁收口，主理人只做拆解调度验收

## 成员架构（10 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 游戏统筹 | `game-team-lead` | 任务拆解、设计范围、角色分派、阶段门禁 | 所有游戏设计需求入口 |
| 玩法设计师 | `game-gameplay-designer` | 核心循环、规则、操作、玩家动机 | "核心玩法是什么"、"怎么玩" |
| 关卡设计师 | `game-level-designer` | 关卡布局、难度曲线、引导、节奏 | "设计一关"、"关卡难度曲线" |
| 数值平衡师 | `game-balance-designer` | 数值公式、成长曲线、属性平衡、掉落 | "数值平衡"、"伤害公式" |
| 叙事设计师 | `game-narrative-designer` | 世界观、剧情、角色、对话、任务叙事 | "世界观"、"剧情怎么讲" |
| 游戏经济设计 | `game-economy-designer` | 货币体系、产出消耗、商店、通胀控制 | "经济系统"、"货币循环" |
| 原型开发 | `game-prototype-developer` | 可玩原型、机制验证、灰盒测试 | "做个原型试试" |
| 游戏美术指导 | `game-art-director` | 美术风格、视觉规范、色彩、UI 方向 | "美术风格"、"视觉方向" |
| 游戏 QA | `game-qa` | 功能测试、bug 复现、边界用例、回归 | "测试这个原型"、"找 bug" |
| 游戏评审 | `game-reviewer` | 玩法乐趣/平衡/完整度门禁（只读） | "这个设计好玩吗" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程** | "从概念到可玩原型" | 拆解 → 玩法（gameplay-designer）→ 数值+经济并行（balance + economy）→ 关卡（level）+ 叙事（narrative）+ 美术方向（art-director）→ 原型（prototype-developer）→ qa 测试 + reviewer 门禁（清零后）→ 交付 |
| **W2 仅设计文档** | "只要 GDD/玩法方案" | 拆解 → gameplay-designer 出核心循环 → balance + economy 并行 → narrative/art 补充 |
| **W3 仅原型验证** | "验证某个机制好不好玩" | 拆解 → gameplay-designer 定机制 → prototype-developer 做灰盒 → qa 测 + reviewer 评乐趣 |

## 协作机制
- **小步提交**：先出核心循环文档再做原型；数值与经济用表格小步迭代
- **门禁规则（唯一口径）**：原型/方案完成 → game-qa（功能/bug）+ game-reviewer（乐趣/平衡/完整度）并行评审 → **reviewer 无 critical/major 后** → 主理人交付。数值/经济方案须经 balance/economy 交叉核对。
- **驳回机制**：同一设计被驳回 2 次以上，停下来重查核心循环或玩家动机，而非重复调表
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不亲自写 GDD/做原型，只做拆解、调度、验收
- 数值与经济公式必须可复算，不拍脑袋定数字
- 评审结论以 qa/reviewer 回报为准，不脑补"应该好玩"
- 设计文档术语统一，接口/规则写清楚不留"到时再定"

> **协作接口**：可对接 software-dev-team（原型/正式工程实现）、visual-design-team（美术资源）、data-analysis-team（上线后平衡数据复盘）；典型跨场景触发词：游戏 GDD、玩法设计、数值平衡、游戏经济、原型。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全流程做游戏设计（Team-lead 为入口）
teams/game-design-team/agents/game-team-lead "帮我设计一款俯视角 roguelike 小游戏，从玩法到原型全走一遍"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/game-design-team/agents/game-gameplay-designer "设计核心玩法循环"
# teams/game-design-team/agents/game-level-designer "设计第一关布局和难度曲线"
# teams/game-design-team/agents/game-balance-designer "出一套伤害与成长数值表"
# teams/game-design-team/agents/game-narrative-designer "搭世界观和主线剧情"
# teams/game-design-team/agents/game-economy-designer "设计双货币经济循环"
# teams/game-design-team/agents/game-prototype-developer "做一个移动的灰盒原型"
# teams/game-design-team/agents/game-art-director "定卡通渲染的美术风格"
# teams/game-design-team/agents/game-qa "测试这个原型找 bug"
# teams/game-design-team/agents/game-reviewer "评审这个设计好不好玩"
```
