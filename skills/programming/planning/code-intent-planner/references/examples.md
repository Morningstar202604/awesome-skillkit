# 典型输入输出案例库

> 来源：真实用户使用 `code-intent-planner` 的对话记录 + 边缘场景测试
> 用途：训练触发词、验证输出格式、帮助模型理解边界

---

## 案例 1：L1 直接命中（fix + 多关键词）

**输入：**
```
帮我修复一下，一登录就 crash，报错 panic: runtime error: invalid memory address
```

**L1 匹配：** `fix|修[好复]|bug|报错|错误|crash|panic` → 命中 fix，置信度 0.95

**输出：**
```json
{
  "intent_type": "fix",
  "subtype": "runtime",
  "confidence": 0.95,
  "source_layer": "L1",
  "description": "修复登录时 crash 的 runtime panic",
  "slots": [
    {"name": "target", "value": "", "evidence": "assumed"},
    {"name": "scope", "value": "login", "evidence": "verified"},
    {"name": "tech_stack", "value": "", "evidence": "assumed"}
  ],
  "constraints": {"hard": [], "soft": []},
  "solution": "先复现 → 定位堆栈 → 修复空指针 → 回归测试"
}
```

**渲染后 Markdown：**
```markdown
# 任务计划 — fix_login_crash

**意图类型：** fix.runtime
**置信度：** 0.95（来源：L1）

## 需求概述
修复登录时 crash 的 runtime panic

## 推荐方案
先复现 → 定位堆栈 → 修复空指针 → 回归测试
```

---

## 案例 2：L1 未命中，L2 Flash 处理（implement + 含技术栈）

**输入：**
```
我想做一个类似 Vercel 的部署平台，支持一键部署 Next.js 项目，用 Go 写后端
```

**L1 匹配：** `build|create|开发` → 命中 implement，但置信度 0.88 < 需要确认
→ 升级 L2

**L2 输出（Mock）：**
```json
{
  "intent_type": "implement",
  "subtype": "feature",
  "confidence": 0.90,
  "description": "实现类 Vercel 的一键部署平台",
  "slots": {
    "target": "deployment-platform",
    "scope": "Next.js auto-deploy",
    "tech_stack": "Go backend"
  },
  "assumptions": [
    {"text": "使用 PostgreSQL 存储部署记录", "impact": "medium", "evidence": "provisional"},
    {"text": "前端用 React + TypeScript", "impact": "medium", "evidence": "provisional"}
  ]
}
```

**输出（Markdown）：**
```markdown
# 任务计划 — deployment_platform

**意图类型：** implement.feature
**置信度：** 0.90（来源：L2）

## 需求概述
实现类 Vercel 的一键部署平台，支持 Next.js

## 任务分解
| ID | 任务 | 依赖 | 优先级 | 预估 | 风险 |
|----|------|------|--------|------|------|
| T1 | 设计部署调度模型 | — | P0 | M | medium |
| T2 | 实现 Git webhook 接收 | T1 | P0 | M | medium |
| T3 | 实现构建流水线 | T2 | P0 | L | high |
| T4 | 实现容器部署 | T3 | P1 | L | high |
| T5 | 前端管理面板 | T3 | P2 | M | medium |

## 关键路径
T1 → T2 → T3 → T4

## 假设
| 假设 | 置信度 | 影响 |
|------|--------|------|
| 使用 PostgreSQL | 🟡 provisional | medium |
| 前端用 React+TS | 🟡 provisional | medium |
```

---

## 案例 3：多意图并存（primary + secondary）

**输入：**
```
查一下这个接口为啥报错，顺便帮我加个缓存层
```

**L1 匹配结果：**
| 规则 | 意图 | 优先级 |
|------|------|--------|
| `报错` | fix | 2 |
| `加` | implement | 10 |

**输出（多意图）：**
```json
{
  "primary_intent": "fix",
  "secondary_intents": ["implement"],
  "multi_intent": true,
  "recommendation": "先定位报错原因（fix），再设计缓存层（implement）",
  "sub_tasks": [
    {"id": "T1", "description": "复现接口报错", "priority": "P0", "depends_on": []},
    {"id": "T2", "description": "定位根因并修复", "priority": "P0", "depends_on": ["T1"]},
    {"id": "T3", "description": "设计缓存方案", "priority": "P1", "depends_on": ["T2"]},
    {"id": "T4", "description": "实现缓存层", "priority": "P1", "depends_on": ["T3"]}
  ]
}
```

---

## 案例 4：跨轮累积（session 记忆）

**第 1 轮：**
```
> 帮我设计一个用户权限系统，用 RBAC 模型，Python FastAPI
```
**输出：**
```json
{
  "session_id": "s1",
  "turn": 1,
  "intent_type": "design",
  "slots": {"target": "auth-system", "scope": "RBAC", "tech_stack": "python/fastapi"}
}
```

**第 2 轮：**
```
> 再加个基于角色的接口权限校验，不需要数据库那块了
```
**注入上下文：** `{target: auth-system, scope: RBAC, tech_stack: python/fastapi}`
**增量识别：** `{target: auth-system, scope: rbac+permission-check}`

**输出（合并）：**
```json
{
  "session_id": "s1",
  "turn": 2,
  "intent_type": "implement",
  "slots": {
    "target": "auth-system",
    "scope": "RBAC + 接口权限校验",
    "tech_stack": "python/fastapi",
    "excludes": "数据库部分"
  }
}
```

---

## 案例 5：澄清协议触发

**输入：**
```
帮我做个东西
```

**L1 匹配：** `做` → implement（置信度 0.88 ≥ 0.85）→ 直接命中

但如果 L2 返回置信度 0.70（灰色区间）：
**输出：**
```json
{
  "status": "clarification_needed",
  "questions": [
    "① 需要实现什么功能或模块？（如：用户认证、订单管理）",
    "② 改动范围是？（新功能开发 / 现有功能修改 / 代码重构）",
    "③ 目标技术栈是什么？（如：python/fastapi、node/express）"
  ],
  "partial_intent": {
    "intent_type": "implement",
    "confidence": 0.70,
    "description": "需求模糊，需澄清"
  }
}
```

---

## 案例 6：复杂表述 → L3 深度推理

**输入：**
```
我现在有个电商系统，用户下单后会调用库存服务扣减库存，但高并发下经常库存超卖，
而且退款后库存没恢复。想先分析一下瓶颈在哪里，再出优化方案，技术栈是 Java Spring Boot + Redis。
```

**分析：**
- L1 命中 `优化` → optimize（置信度 0.85）
- 但包含多意图：分析瓶颈 + 优化方案 + 涉及库存/退款/高并发
- L2 置信度可能 < 0.60 → 升级 L3

**L3 输出：**
```json
{
  "intent_type": "optimize",
  "confidence": 0.88,
  "description": "电商库存超卖问题：高并发扣减 + 退款恢复双重问题",
  "sub_tasks": [
    {"id": "T1", "description": "复现超卖场景，建立性能基线", "priority": "P0", "risk": "high"},
    {"id": "T2", "description": "Profiling 定位库存扣减热点", "priority": "P0", "risk": "high"},
    {"id": "T3", "description": "分析 Redis 缓存策略是否合理", "priority": "P1", "risk": "medium"},
    {"id": "T4", "description": "设计乐观锁/分布式锁方案", "priority": "P1", "risk": "medium"},
    {"id": "T5", "description": "设计退款库存恢复机制", "priority": "P1", "risk": "medium"},
    {"id": "T6", "description": "压测验证优化效果", "priority": "P2", "risk": "low"}
  ],
  "critical_path": ["T1", "T2", "T4"],
  "parallel_groups": [["T3", "T5"]],
  "solution": "先 profiling 定位瓶颈，再决定锁方案（Redis 原子操作 vs 分布式锁）"
}
```

---

## 案例 7：destructive 意图（高风险，人工确认）

**输入：**
```
把 users 表里所有 created_at 超过一年的数据都删掉
```

**L1 匹配：** `删|删除` → destructive（置信度 0.97）

**输出（安全强化版）：**
```json
{
  "intent_type": "destructive",
  "confidence": 0.97,
  "risk_level": "high",
  "requires_confirmation": true,
  "confirmation_message": "⚠️ 检测到 destructive 意图：删除 users 表超过一年的数据。此操作不可逆。请确认：\n1. 是否已备份相关数据？\n2. 删除范围是否正确？\n3. 是否有依赖此数据的报表/缓存？\n\n回复 '确认删除' 继续，否则中断。",
  "fallback_solution": "先用 SELECT 确认影响行数，再用 DELETE 分批次执行，每批验证后继续"
}
```

---

## 案例 8：英文输入

**输入：**
```
I need to refactor the authentication module to support OAuth2, and also add unit tests for the new login endpoint
```

**L1 匹配：**
- `refactor` → refactor（优先级 6）
- `add` → implement（优先级 10）

**多意图输出：**
```json
{
  "primary_intent": "refactor",
  "secondary_intents": ["implement"],
  "recommendation": "先重构 auth 模块支持 OAuth2，再写单元测试"
}
```

---

## 案例 9：口语化/模糊输入

**输入：**
```
这个功能怎么搞
```

**L1 匹配：** `怎么[做搞]` → plan（置信度 0.95）

**输出：**
```json
{
  "intent_type": "plan",
  "confidence": 0.95,
  "description": "需求规划：功能实现路径分析",
  "solution": "需求澄清 → 技术方案设计 → 任务分解 → 优先级排序"
}
```

---

## 案例 10：边界情况（无匹配）

**输入：**
```
今天天气不错啊
```

**L1 匹配：** 无命中

**输出：**
```json
{
  "matched": false,
  "intent_type": null,
  "confidence": 0.0,
  "source_layer": "L1",
  "recommendation": "upgrade_to_L2"
}
```

**行为：** 提示用户澄清需求，或交给 L2 做宽泛意图识别。

---

## 案例来源说明

| 案例 | 来源 | 提取方式 |
|------|------|----------|
| 案例 1,2,3 | 真实用户对话（脱敏） | 从 opencode 会话日志提取 |
| 案例 4 | XIntent 跨轮测试用例 | 参考 XIntent session 测试 |
| 案例 5 | 澄清协议测试 | 构造低置信度 L2 输出 |
| 案例 6 | 实际生产问题 | 来自电商系统优化需求 |
| 案例 7 | 安全规范 | 参考 Ship-Gate destructive 规则 |
| 案例 8,9,10 | 边界测试 | 构造极端输入验证鲁棒性 |
