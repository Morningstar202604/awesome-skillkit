---
name: spec-driven-workflow
description: "Use when the user asks to write specs before code, define acceptance criteria, plan features before implementation, generate tests from specifications, or follow spec-first development practices. 当用户要求 写规格说明 / 验收标准 / 规格驱动开发 时使用。 Do NOT use for free-form coding without a written spec."
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: cicd
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Spec-Driven Workflow

Enforce spec-first development: write the specification BEFORE any code, validate it, extract test stubs from acceptance criteria, then implement one criterion at a time. Every line of code traces back to a spec requirement.

**The Iron Law:**

```text
NO CODE WITHOUT AN APPROVED SPEC.
NO EXCEPTIONS. NO "QUICK PROTOTYPES." NO "I'LL DOCUMENT IT LATER."
```

Why spec-first: catching ambiguity in a spec costs minutes, in production costs days; the spec is the definition of done; acceptance criteria translate 1:1 into test cases.

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 功能名称与描述 | 是 | 生成 spec 模板的种子，如 `--name "User Authentication" --description "OAuth 2.0 login flow"` |
| 需求来源 | 是 | 用户访谈要点、既有代码、约束（性能预算/安全/兼容性） |
| 测试框架 | 否 | pytest / jest / go-test（test_extractor 的 `--framework`），缺省 pytest |
| spec 存放路径 | 否 | 如 specs/ 下按功能命名（见交付标准），缺省按项目惯例 |
| spec 状态 | 实现阶段必需 | Draft / In Review / **Approved**（未 Approved 不得实现） |

输入缺失时一次性问齐："请提供：① 功能名称与一句话描述；② 关键需求/约束/明确不做什么；③ 测试框架（pytest/jest/go-test）。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。

# 2. 两个工具脚本存在
ls scripts/spec_generator.py scripts/test_extractor.py
# 预期：两个文件名（在技能目录内执行）。失败→cd 到技能目录；仍缺→STOP 回报。
# 注意：本技能没有 spec_validator.py——spec 完整性由工作流步骤 3 的 checklist 人工校验。

# 3. 参考模板在位
ls references/spec_format_guide.md references/acceptance_criteria_patterns.md references/bounded_autonomy_rules.md
# 预期：三个文件名。缺失→STOP 回报仓库不完整。
```

## 工作流

### 步骤 1：收集需求

- **动作**：访谈用户（解决什么问题、用户是谁、成功长什么样、明确不建什么）；读既有代码理解现状；记录约束与全部未知项。
- **预期**：能用 2 分钟向不熟悉项目的人讲清这个功能；未知项已列成清单。
- **若失败**：需求方答复不了核心问题 → 按"有界自治规则"（见参考）升级提问，STOP。

### 步骤 2：生成并撰写 spec

```bash
python3 scripts/spec_generator.py --name "User Authentication" --description "OAuth 2.0 login flow" --output specs/auth.md
```

- **动作**：以生成的模板为基础填满全部 9 个节（不适用也写 "N/A — 理由"）：Title/Metadata、Context、Functional Requirements（RFC 2119 关键词，FR-N 编号）、Non-Functional Requirements（可度量阈值）、Acceptance Criteria（Given/When/Then，每个 AC 引用至少一个 FR-*/NFR-*）、Edge Cases（EC-N，覆盖每个外部依赖的失败模式）、API Contracts（TS 风格接口，含成功与错误响应）、Data Models（表格式：字段/类型/约束）、Out of Scope（显式排除+理由）。
- **预期**：spec 文件生成于 `--output` 指定路径，且 9 节全部非空、编号完整。
- **若失败**：生成器输出缺节 → 按参考 `spec_format_guide.md` 的模板手工补齐。

### 步骤 3：校验 spec

逐项核对手工 checklist（本技能无自动 validator，此 checklist 即门禁）：

- [ ] 每条 functional requirement 至少有一个 acceptance criterion
- [ ] 每条 acceptance criterion 机器可验证（无主观措辞）
- [ ] API contracts 覆盖需求中提到的全部端点
- [ ] Data models 覆盖需求中提到的全部实体
- [ ] Edge cases 覆盖每个外部依赖的失败模式
- [ ] Out of scope 显式记录了"考虑过但排除"的内容
- [ ] Non-functional requirements 均有可度量阈值

- **预期**：七项全勾。
- **若失败**：任一项不满足 → 修订 spec 后重新核对；提交评审，状态达到 **Approved** 才进步骤 4。

### 步骤 4：从验收标准生成测试

```bash
python3 scripts/test_extractor.py --file specs/auth.md --framework pytest --output tests/test_auth.py
```

- **动作**：从 spec 的 acceptance criteria 与 edge cases 提取测试桩（定义断言，不含实现）；`--json` 可输出结构化清单。
- **预期**：测试文件生成于 `--output` 指定路径，全部测试以 "not implemented" 或等价方式失败（TDD 红灯）。
- **若失败**：提取结果遗漏某 AC → 手工补测试桩，使每个 AC 与 EC 都有对应测试。

### 步骤 5：逐条实现

- **动作**：选最简单的一条 AC → 最小代码使其测试通过 → 跑全量测试防回归 → commit → 下一条。
- **预期**：每条 AC 的测试逐个转绿；全量测试无回归。
- **若失败**：实现中发现 spec 缺需求 → STOP，先更新 spec 并回到步骤 3 重新评审；绝不顺手实现 spec 外内容。

### 步骤 6：自审

实现标记完成前核对：

- [ ] 每条 AC 有通过的测试；每条 EC 有测试
- [ ] 无范围蔓延（spec 外内容要么删掉要么先更新 spec）
- [ ] API 契约与实现逐字段一致（名称、类型、状态码）
- [ ] spec 定义的每个错误响应都有测试触发
- [ ] NFR 有证据达标（benchmark/压测/profiling）
- [ ] 数据库 schema 与 spec 一致；Out of Scope 未泄漏进实现

- **预期**：六项全勾。
- **若失败**：任一项不过 → 修复后重审，不得声明完成。

### 有界自治（贯穿全程）

STOP and ask：范围蔓延（spec 里没有的东西，即使"显然需要"）、歧义超 30%、需要破坏性变更、涉及鉴权/加密/PII、性能指标无法度量、跨团队依赖未确认。
Continue autonomously：spec 明确无歧义、全部 AC 有通过测试且只在重构内部、改动非破坏、实现是 AC 的直接翻译、错误处理沿用代码库既有模式。
升级时必须给：被阻塞的需求编号、具体问题、带 Pros/Cons 的选项、推荐项、等待影响。见 `references/bounded_autonomy_rules.md`。

## 工具速查

| Script | Purpose | Key Flags |
|--------|---------|-----------|
| `spec_generator.py` | 从功能名/描述生成 spec 模板 | `--name`（必填）, `--description`, `--output/-o`, `--format md\|json` |
| `test_extractor.py` | 从验收标准提取测试桩 | `--file/-f`, `--framework pytest\|jest\|go-test`, `--output/-o`, `--json` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| 提取的测试遗漏 AC | spec 的 Given/When/Then 格式不规范 | 对照 `references/acceptance_criteria_patterns.md` 重写该 AC，重新提取 |
| spec 评审后被拒但已有代码 | 违反 Iron Law 先行编码 | 停止实现，按评审结论重写 spec，代码作废或重做 |
| 实现需 spec 外改动 | 范围蔓延 | STOP → 更新 spec → 重新评审；禁止先斩后奏 |
| NFR 无法验证 | 阈值不可度量 | 回步骤 3 把阈值改写为可度量指标（如 "p95 < 500ms"） |
| `spec_generator.py` 报 `--name` 缺失 | 必填参数遗漏 | 补 `--name` 重跑 |

## 交付标准

- 成功定义：Approved 状态的 spec（9 节齐全、编号完整）+ 全部测试桩 + 测试全绿 + 自审 checklist 全勾。
- 产物命名：spec 存 `specs/<feature>.md`；测试存 `tests/test_<feature>.py`（或对应框架惯例）。
- 保存位置：项目内如上路径，或用户指定位置。
- 完整性验证：`python3 scripts/test_extractor.py --file specs/<feature>.md --json` 输出的 AC/EC 清单与 spec 中的编号一一对应；测试文件中每个测试名可追溯到某个 AC 或 EC 编号。

## 参考

- `references/spec_format_guide.md` — 9 节完整模板、好/坏需求模式对照、CRUD/Integration/Migration 类型模板与 Password Reset 完整示例；步骤 2 写 spec 前读。
- `references/acceptance_criteria_patterns.md` — Given/When/Then 验收标准模式库（auth/CRUD/search/upload/payment 等）；AC 写不出或被评审打回时读。
- `references/bounded_autonomy_rules.md` — 何时停下提问 vs 自主推进的完整决策矩阵；执行中遇到边界情况时读。

## Anti-Patterns

| # | 反模式 | 后果 | 规则 |
|---|---|---|---|
| 1 | 评审未通过就开写代码 | 评审改动后代码实现的是被否决的设计 | spec 状态为 Approved 前不实现 |
| 2 | 模糊验收标准（"响应快""体验好"） | 无法测试 | 机器可验证才可保留，否则重写 |
| 3 | 缺 edge cases | 开发者临场发明错误处理 | 每个外部依赖至少一条失败场景 |
| 4 | 事后补 spec | 那是文档不是规格，抓不住设计错误 | 代码后写的只能标注为文档 |
| 5 | spec 外镀金 | 未经测试与评审的 bonus 代码 | 不在 spec 就不建；另立新 spec |
| 6 | AC 不引用任何 FR/NFR | 孤儿标准，或缺需求或属多余 | 每个 AC 必须引用至少一个 FR-*/NFR-* |
| 7 | 跳过校验直接开工 | 缺节在实现期才暴露，阻塞 | 步骤 3 checklist 全勾前不进步骤 4 |

## Cross-References

- **`engineering-team/tdd-guide`** — red-green-refactor 纪律、覆盖率分析；步骤 4 之后使用。
- **`engineering/focused-fix`** — 规格驱动实现出现系统性问题时用于诊断。
- **`engineering/rag-architect`** — 功能涉及检索/知识系统时的技术设计。
