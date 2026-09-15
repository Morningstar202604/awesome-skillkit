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

## 输入清单

| 输入 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| raw_input | 是 | 用户原始输入 | — |
| session_id | 否 | 会话标识（跨轮累积用） | auto-<timestamp> |
| project_root | 否 | 项目根目录 | 自动探测 |

缺失时询问模板：「请提供：① 你的需求描述。项目目录和 session_id 我自动处理。」

## 前置自检

```bash
# 探测项目根目录
for dir in . .. ../..; do
  for f in package.json pyproject.toml go.mod Cargo.toml pom.xml build.gradle requirements.txt; do
    [ -f "$dir/$f" ] && echo "$dir" && exit 0
  done
done
echo "."
```

预期：输出项目根路径
若失败：使用当前目录，tech_stack 标记 unknown

---

## 三层瀑布式意图识别

### L0 缓存层（同一 session 内）

```python
# 同一 session 内，同一 intent_type + 相似输入 → 直接返回缓存
cache_key = f"{session_id}:{intent_type}:{hash(normalized_text)}"
if cache.get(cache_key):
    return cache[cache_key]  # <1ms
```

---

### 步骤 1：输入规范化

| 动作 | 说明 |
|------|------|
| 指代消解 | `"它"` → 从 `last_intent.slots` 推断 |
| 省略补全 | `"帮我写"` → `"帮我写代码"` |
| 术语标准化 | `"后端"/"server"/"API"` → `backend` |

输出：`normalized_text`

---

### 步骤 2：L1 规则层（零 LLM，<10ms）

| 规则 | 意图 | 置信度 | 优先级 |
|------|------|--------|--------|
| `删|删除|remove|uninstall|销毁` | destructive | 0.97 | 1 |
| `fix|修[好复]|bug|报错|错误|crash|panic` | fix | 0.95 | 2 |
| `测试|test|单测|单元测试|覆盖率|coverage` | test | 0.90 | 3 |
| `审查|review|code.?review|audit|检[查核]` | review | 0.92 | 4 |
| `规划|拆解|分析.*需求|怎么[做搞]|plan|break.?down` | plan | 0.95 | 5 |
| `重构|refactor|优化代码|整理代码` | refactor | 0.90 | 6 |
| `性能|加速|profiling|bottleneck` | optimize | 0.85 | 7 |
| `设计|架构|设计方案` | design | 0.82 | 8 |
| `迁移|migrate|升级|upgrade|版本升级` | migrate | 0.88 | 9 |
| `写|做|实现|添加|新增|build|create|开发` | implement | 0.88 | 10 |

**逻辑**：按优先级顺序匹配，首个命中且置信度 ≥ 0.85 → 直接输出，跳过 L2/L3。

---

### 步骤 3：L2 Flash LLM（置信度路由）

**模型**：Flash/Mini（如 deepseek-v4-flash, glm-4-flash）

**Prompt 模板**：
```
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

**置信度路由**：
| 置信度 | 动作 |
|--------|------|
| ≥ 0.85 | 接受 → 步骤 4 |
| 0.60 - 0.85 | 澄清协议（§澄清协议） |
| < 0.60 | 升级 L3 |

---

### 步骤 4：槽位填充与证据分级

| 来源 | 证据级 | 示例 |
|------|--------|------|
| 用户明确指定 | 🟢 verified | "修改 auth 模块" → target=auth |
| L1 规则推断 | 🟢 verified | 含"bug"+"crash" → fix.runtime |
| L2 LLM 输出 | 🟡 provisional | L2 推断 target=api |
| 项目上下文 | 🟡 provisional | 从 package.json 推断 tech_stack |
| 模型猜测 | 🔴 assumed | 无证据，必须标注 |

**硬约束**（用户明确指定，不可违反）vs **软约束**（建议但可调整）。

---

### 步骤 5：L3 Pro LLM（复杂场景兜底）

**触发条件**：L2 置信度 < 0.60，或五类复杂场景：
1. 复杂表达（隐含多层需求）
2. 跨轮上下文（"继续上次"）
3. 意图切换（中途改变目标）
4. 多意图分解（一个请求多个子任务）
5. 隐式信息补全（需要项目上下文推断）

**模型**：Pro/推理模型

**Prompt 模板**：
```
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

---

## 方案建议（基于意图类型）

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

---

## 澄清协议

**触发**：L2 置信度 0.60-0.85 且无法消除歧义，或必需槽位缺失。

**追问模板**（一次性问齐，最多 3 个问题）：
```
为准确规划，请确认：
① [问题1]
② [问题2]
③ [问题3]
如暂不确定，可回答"待定"。
```

**最大澄清轮次**：3 轮。超出 → 降级为保守方案，标注所有假设。

---

## 跨轮累积协议

**session 状态文件**：`_session_<session_id>.json`

```json
{
  "session_id": "...",
  "turn": 2,
  "last_intent": {"type": "implement", "slots": {"target": "auth"}},
  "slots_history": [...],
  "pending_slots": ["deadline"]
}
```

**合并策略**：latest-wins + 冲突检测。冲突时标记 provisional 并请用户裁决。

**注入规则**：下一轮输入时，将 `last_intent.slots` 自动注入上下文。

---

## 意图类型缓存

```python
# 同一 session 内，同一 intent_type + 相似输入 → 直接返回缓存
cache_key = f"{session_id}:{intent_type}:{hash(normalized_text[:100])}"
if cache.get(cache_key):
    return cache[cache_key]
```

---

## 失败处置

| 现象 | 处置 |
|------|------|
| L1 无匹配 | 升级 L2 |
| L2 置信度低 | 澄清 或 升级 L3 |
| 澄清超 3 轮 | 降级保守方案，标注所有假设 |
| 项目探测失败 | 继续，tech_stack = unknown |
| session 状态丢失 | 新建 session，无跨轮累积 |

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

## 参考

- references/solution-templates.md —— 各意图类型的方案模板
- references/gotchas.md —— 常见陷阱与反模式
- references/prompt-templates.md —— L2/L3 prompt 模板
- references/examples.md —— 10 个真实案例（含边界场景）