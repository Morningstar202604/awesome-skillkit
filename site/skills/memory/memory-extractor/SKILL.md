---
name: memory-extractor
description: "Use when turning a conversation or document into structured memory candidates: decide what is worth remembering, split facts to fine granularity, deduplicate, and score confidence. Triggers on 记忆抽取, 对话转记忆, 提取记忆条目, memory extraction, extract memories, conversation to memory, candidate extraction, 置信度打分, 细粒度事实. NOT for storing, updating, or retrieving memories — use memory-manager or memory-retriever."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Memory Extractor

对话里九成内容不值得记。本技能解决"哪些值得记、怎么记才干净"：从对话或文档中抽取候选记忆条目，逐条拆到细粒度、去重、打置信度，产出机器可解析的 candidates.json——它只做抽取，不写入库（那是 memory-manager 的事）。

## 输入清单

开工前一次性收集。缺输入时用这句话向用户问一次："要抽取记忆条目，请一次性提供：待抽取的对话或文档原文、记忆归属的 user_id、现有记忆库导出文件（用于去重，没有则跳过去重、标注 NO_DEDUP）。"

| 输入 | 必需 | 说明 |
|---|---|---|
| 对话/文档原文 | 是 | 完整文本或对话记录；不接受"大概聊了什么"的转述 |
| user_id | 是 | 归属主体；多用户对话必须分别标注 |
| 现有记忆库导出 | 否 | 同主题已有条目，用于去重比对；缺失时输出标注 NO_DEDUP |
| schema 约束 | 否 | 若上游 memory-architect 已冻结 schema，按其 type 枚举执行 |

## 前置自检

本技能为纯 prompt 技能，无需探测运行环境，只检查输入完备性：

- 原文与 user_id 是否齐备？任一缺失 → 用问齐话术问一次，不要猜归属。
- 原文是否为转述而非原始记录？转述会引入转述者的归纳失真 → 要求提供原文；拿不到则在输出中整体降一档置信度并标注 `secondhand: true`。
- 现有记忆库导出缺失 → 正常继续，但最终输出标注 NO_DEDUP，交由 memory-manager 补做去重。

## 红线

1. 不推断敏感类别：健康、财务、宗教、政治倾向、性取向等，除非用户在对话中**显式要求**记住，否则一律不抽取——闲聊提到"最近在化疗"不是可抽取的记忆。
2. 推断条目必须标注：凡非用户原话直接支持、由行为或上下文推断的条目，confidence ≤ 0.7 且 content 末尾加 `[inferred]` 标记。
3. evidence_quote 必须是原文逐字引用：抽不出原文引用的条目一律丢弃，不许"凭印象"造证据。
4. 不抽取一次性事务："帮我订周三的会议室"是日程不是记忆，写入记忆库只会制造噪声。
5. 不改写用户立场：原文说"暂时不想用 Vue"不得抽成"用户不喜欢 Vue"。

## 工作流

### 步骤 1：通读并分段

- **动作：** 通读原文，按话题切换点切成片段；每段标注话题标签。
- **预期：** 片段列表，每段有话题标签与行号范围（可追溯到原文）。
- **失败时：** 原文无明确话题边界（如流水账）→ 按固定轮数（经验值 10 轮一段，可调）机械切分。

### 步骤 2：候选抽取

- **动作：** 逐段扫四类信号，每类配标准话术模板：
  - fact（事实）：用户陈述自身情况——"我在上海工作""我用 Python 写后端"。
  - preference（偏好）：表达好恶或要求——"回复尽量短""别用表情符号"。
  - decision（决策）：拍板与选择——"那就定 PostgreSQL""先不做移动端"。
  - project_status（项目状态）：进展与阻塞——"登录模块已经上线""卡在支付回调"。

  判别话术：这句话六个月后还成立吗？成立 → fact 或 preference；只描述某个时间点的落定 → decision；描述"进行到哪" → project_status。带"喜欢/讨厌/别再/尽量" → preference 优先。

- **预期：** 每个候选有原文出处（行号）与类别归属；含糊句（"可能""大概"）降级为待定。
- **失败时：** 一句话含多类信号 → 拆成多条候选分别归类，不许硬塞一条。

### 步骤 3：细粒度拆分

- **动作：** 逐条执行"一条记忆 = 一个可独立成立的事实"：复合句拆开（"用户在上海工作且养猫"拆成两条），条件句拆开（"周一到周五早睡"与"周末熬夜"是两条）。
- **预期：** 每条候选单独成立且无代词残留——把"他""那家公司"替换为具体指代。

拆分示例：

```text
原文："用户在上海做后端开发，家里养了只猫，最近想把数据库从 MySQL 换掉。"
拆分：1) "用户工作地点在上海，岗位是后端开发" (fact)
      2) "用户家里养了一只猫" (fact)
      3) "用户计划替换当前数据库（现为 MySQL）" (project_status)
```

- **失败时：** 拆开后某条失去独立含义 → 合并回去并注明 granularity_note 说明为何不可拆。

### 步骤 4：去重与置信度打分

- **动作：** 与现有记忆库逐条比对（语义等价即视为重复，如"我在上海工作"与"我的工作地点是上海"）。打分规则：用户原话显式说出 = 0.9；多次重复出现的偏好 = 0.95；由行为推断 = 0.6；由单一间接线索推断 = 0.6 以下。
- **预期：** 每条候选有 confidence 数值与打分依据；重复项标记 `duplicate_of` 并携带现有条目 id。
- **失败时：** 现有库缺失（NO_DEDUP 模式）→ 跳过比对，confidence 上限压到 0.8 以留出后续校准空间。

### 步骤 5：输出 candidates.json

- **动作：** 汇总为 JSON 数组，字段名全英文，附一行统计（各类条数、平均置信度）。

```json
[
  {
    "content": "用户工作地点在上海",
    "type": "fact",
    "confidence": 0.9,
    "evidence_quote": "我平时在上海这边上班",
    "granularity_note": "由复合句拆出；另一条为'用户养猫'",
    "user_id": "u_123",
    "duplicate_of": null
  }
]
```

- **预期：** JSON 可被 `json.loads` 直接解析；每条四要素（content/type/confidence/evidence_quote）齐全。
- **失败时：** JSON 校验失败 → 修复引号转义与逗号后重出，禁止交付半结构化文本。

## 参数速查表

| 字段/规则 | 取值 | 说明 |
|---|---|---|
| `type` 枚举 | fact / preference / decision / project_status | 四类之外的信号不抽 |
| 显式事实 confidence | 0.9 | 经验值，可调；多源重复可升至 0.95 |
| 推断条目 confidence | ≤ 0.7 且加 `[inferred]` | 红线 2，不可上调 |
| NO_DEDUP 模式 confidence 上限 | 0.8 | 经验值，可调 |
| evidence_quote | 原文逐字 | 最长一句；跨句引用拆为多条 |
| 话题切段长 | 10 轮/段 | 经验值，可调 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 抽出条目超过原文信息量 | 把推断写成了事实 | 逐条核对 evidence_quote；无原文支撑的降级为推断或删除 |
| 敏感类别混入候选 | 把闲聊提及当成了显式意愿 | 按红线 1 删除；仅当用户原话含"记住/记一下"才保留 |
| 大量重复候选 | 对话中反复强调同一偏好 | 合并为一条，confidence 取多次出现的 0.95 |
| 类别归属拿不准 | 偏好与决策界限模糊 | 看时态：表达好恶为 preference，落定为 decision；仍拿不准按 preference 并在 note 说明 |
| 候选条目远超对话长度合理密度 | 把寒暄和过程性发言也抽了 | 回步骤 2 用"六个月后还成立吗"复筛；单轮对话候选建议不超过 10 条（经验值，可调） |
| evidence_quote 与 content 语义脱节 | 抄错了原文位置 | 逐条回贴行号核对；定位不到的按红线 3 丢弃 |
| user_id 多人混淆 | 群聊未标注说话人 | 停止抽取，要求提供带说话人标注的原文 |
| JSON 超长难维护 | 单次对话产出过多 | 按话题分段输出多个数组，每段独立可解析 |
| 输出条目全是零碎琐事 | 细粒度拆分过了头 | 拆分以"可独立成立"为界，不为拆而拆；琐事在 granularity_note 标 `low_value` 供 memory-manager 降权 |

## 交付标准

- candidates.json 为合法 JSON 数组，每条含 content、type、confidence、evidence_quote、granularity_note、user_id、duplicate_of 七字段。
- 每条 evidence_quote 能在原文中逐字定位（附行号更佳）。
- 敏感类别零条目；推断条目全部 ≤ 0.7 且带 `[inferred]`。
- 复合句全部拆分，无代词残留。
- 附统计行：各类条数、平均 confidence、是否 NO_DEDUP。

## 参考

- `references/sources-and-methodology.md` —— 需要说明细粒度事实原则与两阶段抽取流程的出处（mem0）、如何署名时读；评审核对方法论时也读。

## 链路位置

- 上游：`memory-architect`（schema 与 type 枚举的制定者，本技能按其约束产出）。
- 下游：`memory-manager`（接收本技能的 candidates.json，执行 ADD/UPDATE/DELETE/NOOP 落库决策）。
- 本技能是 memory-systems 链路的"入口工序"：产出质量直接决定下游库的干净程度，宁缺勿滥。
