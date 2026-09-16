---
name: code-intent-planner
description: "Three-tier waterfall intent recognition (L1 regex <10ms, L2 Flash LLM, L3 Pro LLM) that classifies user intent into 10 types, decomposes tasks, and produces execution plans with evidence grading. Use when the user describes a coding task and needs structured planning before implementation. 当用户要求 理清需求 / 出实施计划 / 把模糊需求变具体 时使用。 Do NOT use for implementing the planned code itself (planning and orchestration only)."
license: Apache-2.0
compatibility: Requires network access and docker. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: intent-planner
  tier: powerful
  verified-date: "2026-09-09"
---

# Code Intent Planner

将编程需求识别为结构化意图 + 任务分解 + 方案建议。
三层瀑布：L1 规则（<10ms） → L2 Flash LLM（置信度路由） → L3 Pro LLM（复杂场景）。
所有命令均在技能目录（本文件所在目录）下执行。

## 输入清单

| 输入 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| raw_input | 是 | 用户原始输入（自然语言） | — |
| session_id | 否 | 会话标识（跨轮累积用） | 自动生成 session_<时间戳> |
| project_root | 否 | 项目根目录 | 自动探测（见前置自检） |

缺失时一次性问齐：「请提供：① 你的需求描述。项目目录和 session_id 我自动处理。」

## 前置自检

依次执行；致命项失败 → 修复后 STOP，不带病继续。

```bash
# 1. Python 可用（致命）
python3 --version          # 预期：Python 3.x；失败 → 安装 python3 后 STOP

# 2. 脚本就位（致命；必须在技能目录执行）
test -f scripts/pipeline.py && echo OK   # 预期：OK；失败 → cd 到技能目录重试，仍失败 STOP

# 3. 探测项目根目录（非致命；脚本内建同款逻辑）
for dir in . .. ../..; do
  for f in package.json pyproject.toml go.mod Cargo.toml pom.xml build.gradle requirements.txt; do
    [ -f "$dir/$f" ] && echo "$dir" && exit 0
  done
done
echo "."
```

- 探测 3 预期：输出项目根路径。若失败（无工程标记文件）：使用当前目录，tech_stack 标记 unknown（显式降级，可继续）。
- 仅 `--no-mock`（真实 LLM）时需要：`test -n "$LLM_API_KEY"` 预期非空；失败 → 导出 `LLM_API_KEY`（必要时 `LLM_BASE_URL`/`LLM_MODEL`）后重试。凭据只走环境变量，不写入文件或命令行。
- 默认 mock 模式（`USE_MOCK_LLM=true`）：不发真实网络请求，先跑通流程再切换真实 LLM。

## 参数速查表

`python3 scripts/pipeline.py`（run）：

| 参数 | 取值 | 说明 |
|------|------|------|
| input（位置参数） | 自然语言文本 | 用户原始输入；缺省时打印帮助并 exit 1 |
| --session / -s | 字符串 | Session ID，跨轮累积 |
| --project / -p | 目录路径 | 项目根目录 |
| --skip-normalization | 开关 | 跳过输入规范化 |
| --no-mock | 开关 | 使用真实 LLM（需 LLM_API_KEY 等环境变量） |
| --format / -f | markdown / json | 输出格式，默认 markdown |
| --output / -o | 文件路径 | 写入文件；缺省打印到 stdout |

## 工作流

### 步骤 1：运行三层瀑布流水线

动作（run）：

```bash
# 默认 mock，先验证流程
python3 scripts/pipeline.py "帮我给 auth 模块加登录" --format json
# 真实 LLM（配置好环境变量后）
python3 scripts/pipeline.py "帮我给 auth 模块加登录" --no-mock --format json
# 复用会话（跨轮累积）
python3 scripts/pipeline.py "继续，加上注册" -s session_20260916_100000 --format json
```

预期：stdout 输出 JSON，含 `intent_type`、`confidence`、`source_layer`、`slots`、`sub_tasks`，退出码 0。
若失败：退出码 1 且 JSON 含 `error` 字段（如 `L2 失败: ...`/`L3 失败: ...`）→ 查失败处置表；`--format markdown` 时渲染为计划文档。

### 步骤 2：输入规范化与缓存检查（脚本自动执行）

动作（read 内部逻辑）：依次做缓存命中检查 → 指代消解（"它/这个/那个" 用上一轮 `last_intent.slots.target` 替换）→ 省略补全（"帮我写" → "帮我写代码"）→ 术语标准化（"后端/server/API" → backend）。
预期：得到 `normalized_text`；同一 session 内相同 intent_type + 相似输入直接命中缓存（cache_key = `session_id:intent_type:hash(normalized[:100])`），不再调 LLM。
若失败（无缓存）：正常进入 L1。

### 步骤 3：L1 规则层判定（零 LLM，<10ms）

按优先级顺序匹配，首个命中且置信度 ≥ 0.85 → 直接输出（`source_layer=L1`），跳过 L2/L3：

| 规则 | 意图 | 置信度 | 优先级 |
|------|------|--------|--------|
| `删\|删除\|remove\|uninstall\|销毁` | destructive | 0.97 | 1 |
| `fix\|修[好复]\|bug\|报错\|错误\|crash\|panic` | fix | 0.95 | 2 |
| `测试\|test\|单测\|单元测试\|覆盖率\|coverage` | test | 0.90 | 3 |
| `审查\|review\|code.?review\|audit\|检[查核]` | review | 0.92 | 4 |
| `规划\|拆解\|分析.*需求\|怎么[做搞]\|plan\|break.?down` | plan | 0.95 | 5 |
| `重构\|refactor\|优化代码\|整理代码` | refactor | 0.90 | 6 |
| `性能\|加速\|profiling\|bottleneck` | optimize | 0.85 | 7 |
| `设计\|架构\|设计方案` | design | 0.82 | 8 |
| `迁移\|migrate\|升级\|upgrade\|版本升级` | migrate | 0.88 | 9 |
| `写\|做\|实现\|添加\|新增\|build\|create\|开发` | implement | 0.88 | 10 |

预期：输出 intent_type + confidence；注意 design(0.82) 低于 0.85 阈值，实际会落入 L2 复核。
若失败（无匹配）→ 升级 L2。

### 步骤 4：L2 Flash LLM 与置信度路由

模型：Flash/Mini（如 deepseek-v4-flash, glm-4-flash）。Prompt 模板（脚本注入）：

```text
分析用户编程意图，仅返回 JSON：
{
  "intent_type": "<implement|fix|refactor|review|test|optimize|plan|design|migrate|destructive>",
  "confidence": <0.0-1.0>,
  "description": "<需求简述>",
  "slots": {"target": "", "scope": "", "tech_stack": ""},
  "assumptions": ["<假设1>"]
}

用户输入："{normalized_text}"
项目技术栈：{tech_stack}
```

置信度路由：

| 置信度 | 动作 |
|--------|------|
| ≥ 0.85 | 接受 → 步骤 6 |
| 0.60 - 0.85 | 澄清协议（见下） |
| < 0.60 | 升级 L3 |

预期：返回可解析 JSON。若失败（error 字段）→ 失败处置表（多为 LLM 端点/密钥问题）。

### 步骤 5：L3 Pro LLM 兜底（复杂场景）

触发：L2 置信度 < 0.60，或五类复杂场景：① 复杂表达（隐含多层需求）② 跨轮上下文（"继续上次"）③ 意图切换（中途改变目标）④ 多意图分解（一个请求多个子任务）⑤ 隐式信息补全（需要项目上下文推断）。
模型：Pro/推理模型。Prompt 模板（脚本注入）：

```text
你是架构师，将需求分解为可执行任务。仅返回 JSON：

原始输入："{raw_input}"
规范化后："{normalized_text}"
技术栈：{tech_stack}
项目结构片段：
{project_structure_snippet}

已知意图：{intent_type}
已知槽位：{slots_json}

{
  "intent_type": "...",
  "confidence": <0.0-1.0>,
  "sub_tasks": [
    {"id": "T1", "description": "...", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"}
  ],
  "critical_path": ["T1", "T3"],
  "parallel_groups": [["T2", "T4"]],
  "solution": "推荐实现路径",
  "assumptions": [{"text": "...", "impact": "medium", "evidence": "provisional"}]
}
```

预期：JSON 含 `sub_tasks`/`critical_path`/`parallel_groups`。若失败 → 失败处置表。

### 步骤 6：解读输出并渲染交付物

槽位证据分级（输出 `slots[].evidence` 字段）：

| 来源 | 证据级 | 示例 |
|------|--------|------|
| 用户明确指定 | verified | "修改 auth 模块" → target=auth |
| L1 规则推断 | verified | 含"bug"+"crash" → fix.runtime |
| L2 LLM 输出 | provisional | L2 推断 target=api |
| 项目上下文 | provisional | 从 package.json 推断 tech_stack |
| 模型猜测 | assumed | 无证据，必须标注 |

硬约束（用户明确指定，不可违反）优先于软约束（建议，可调整）。
按意图类型的推荐实现路径：

| 意图类型 | 推荐实现路径 |
|---------|-------------|
| implement.feature | design → implement → test |
| implement.api | API 契约先行 → 各层实现 |
| fix.runtime | 复现 → 定位 → 修复 → 回归测试 |
| fix.security | 评估影响 → 修复 → 安全扫描 → 升级依赖 |
| refactor | 分析影响 → 保护测试 → 小步重构 → 验证 |
| test.coverage | 分析盲区 → 补充测试 → 验证 |
| optimize | baseline → profiling → 优化 → 回归 |
| design | 需求澄清 → 方案草稿 → 选型论证 → 评审 |
| migrate | 兼容性分析 → 计划 → 试点 → 全量 |
| destructive | 风险评估 → 备份 → 确认 → 执行 → 验证 |

详见 [references/solution-templates.md](references/solution-templates.md)。
destructive 意图属安全红线：任何删除/销毁动作前必须先备份并征得用户明确确认。

动作（run）：`python3 scripts/pipeline.py "<raw_input>" --format markdown -o plans/<session_id>_<YYYYMMDD>.md`
预期：生成 Markdown 计划文档。
若失败：plans/ 目录不存在 → 先 `mkdir -p plans` 再重跑。

---

## 澄清协议

**触发**：L2 置信度 0.60-0.85 且无法消除歧义，或必需槽位缺失（此时流水线返回 `status=clarification_needed` + `questions` 列表）。

**追问模板**（一次性问齐，最多 3 个问题）：
```text
为准确规划，请确认：
① [问题1]
② [问题2]
③ [问题3]
如暂不确定，可回答"待定"。
```

**最大澄清轮次**：3 轮。超出 → 降级为保守方案，标注所有假设。

---

## 跨轮累积与会话

- 状态文件真实位置：`~/.code_intent_planner/sessions/_session_<session_id>.json`（可用环境变量 `SKILLKIT_SESSION_DIR` 覆盖；脚本不会把会话文件写进项目目录，也不要手动编辑）。

```json
{
  "session_id": "...",
  "turn": 2,
  "last_intent": {"type": "implement", "slots": {"target": "auth"}},
  "slots_history": [...],
  "cache": {...}
}
```

- 合并策略：latest-wins + 冲突检测。冲突时标记 provisional 并请用户裁决。
- 注入规则：下一轮输入时，将 `last_intent.slots` 自动注入上下文。

---

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------|------|------|
| L1 无匹配 | 输入不含规则关键词 | 正常分支：升级 L2 |
| L2 置信度 0.60-0.85 | 输入歧义 | 走澄清协议；最多 3 轮，超出 → 降级保守方案并标注所有假设 |
| L2 置信度 < 0.60 | 复杂/多意图输入 | 升级 L3 |
| 退出码 1，JSON 含 `L2 失败: ...` / `L3 失败: ...` | LLM 端点不可达或密钥无效 | 检查 `LLM_API_KEY`/`LLM_BASE_URL`/`LLM_MODEL`；或先用默认 mock 模式验证流程 |
| 打印帮助 + exit 1 | 未提供 input 位置参数 | 提供 raw_input 后重跑 |
| 项目探测失败 | 目录无工程标记文件 | 继续，tech_stack = unknown |
| session 状态丢失 | 状态目录被清理/换机器 | 新建 session，无跨轮累积 |

---

## 输出格式

### 结构化 JSON

```json
{
  "intent_type": "implement",
  "confidence": 0.92,
  "source_layer": "L2",
  "description": "实现用户认证模块",
  "slots": [
    {"name": "target", "value": "auth", "evidence": "verified"},
    {"name": "scope", "value": "login+register", "evidence": "provisional"}
  ],
  "constraints": {"hard": [], "soft": ["use JWT"]},
  "sub_tasks": [
    {"id": "T1", "description": "设计用户数据模型", "depends_on": [], "priority": "P0", "effort": "S", "risk": "low"}
  ],
  "critical_path": ["T1"],
  "solution": "先设计 schema，再实现 model，最后加 API",
  "assumptions": [{"text": "使用 PostgreSQL", "impact": "medium", "evidence": "provisional"}],
  "session_id": "...",
  "timestamp": "2026-09-08T10:00:00Z"
}
```

### Markdown 计划文档

保存路径：`plans/<session_id>_<YYYYMMDD>.md`

结构：
1. 需求概述
2. 已知约束（硬/软）
3. 任务分解表
4. 关键路径
5. 可并行组
6. 假设与待确认
7. 推荐方案

---

## 交付标准

- 成功定义：退出码 0，输出 JSON 无 `error` 字段且含 `intent_type`/`confidence`/`source_layer`；返回 `status=clarification_needed` + 问题列表同样是合法产出。
- 产物命名：Markdown 计划 `plans/<session_id>_<YYYYMMDD>.md`；JSON 结果按需用 `-o` 指定落盘路径。
- 保存位置：计划文档存项目根 `plans/`；会话状态由脚本写入 `~/.code_intent_planner/sessions/`。
- 完整性验证：`python3 -m json.tool <输出>.json` 可解析；计划文档含上述 7 节；`source_layer` 与实际路由层一致；所有 `assumed` 证据级假设均已显式标注。

---

## 参考

- references/solution-templates.md —— 步骤 6 选定意图类型后读，套用对应方案模板
- references/prompt-templates.md —— 需要调整 L2/L3 prompt（换模型/改输出字段）时读
- references/gotchas.md —— 结果异常或置信度系统性偏低时读（常见陷阱与反模式）
- references/examples.md —— 校准判读标准时读（10 个真实案例，含边界场景）
