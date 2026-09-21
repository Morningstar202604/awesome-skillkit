收到完整输入。以下按工作流直接产出架构决策记录与可执行方案。

---

## 一、需求画像表（五类 × 四要素）

| 记忆类别 | 写入方 | 读取方 | 生命周期 | 隐私等级 |
|---|---|---|---|---|
| **项目状态** | memory-extractor / agent 自写入 | agent 自身（启动时） | 单项目存续期，结束后归档；活跃期 ~30–90 天 | PII-排除（不含客户名） |
| **偏好** | memory-extractor | agent 自身（启动时 + 对话中） | 永久，直到显式覆盖 | PII-脱敏（仅记风格，不记身份） |
| **决策** | memory-extractor | agent 自身（审计/回溯） | 永久 | PII-排除 |
| **事实**（技术栈、环境配置） | memory-extractor | agent 自身（任务启动时） | 永久或技术栈变更时更新 | 无 PII |
| **关系**（与谁对接什么） | memory-extractor | agent 自身（分配任务时） | 关系存续期 ~1 年，过期清理 | **含 PII → 强制脱敏**，客户真实姓名不入记忆，改用 alias_id；schema.pii=true |

> 注：读取方均为 agent 自身，无外部系统；任何可能含客户真实信息的字段（公司名、联系人、项目代号若可反查）一律走脱敏路径。

---

## 二、分层映射 + 存储选型

| 层 | 存放内容 | 生命周期 | 存储介质 | 说明 |
|---|---|---|---|---|
| **working** | 当前任务中间状态、临时笔记 | 单次任务 | agent 运行时变量，不落盘 | 不写入持久层 |
| **core** | 每个项目的"关键上下文"（技术栈、当前里程碑、近期决策、偏好摘要）+ 全局偏好 | 长期常驻，agent 可自编辑 | **SQLite core 表**，每条记录软删除（updated_at + status='archived'） | 每次会话注入，上限 4000 字符 |
| **archival** | 全量决策日志、历史项目状态快照、客户沟通要点（脱敏版）、关系记录 | 永久到 TTL 到期 | **SQLite archival 表**，FTS5 全文索引 | 按需检索，不常驻上下文 |

**选型理由：**
- 千级条目 < 2000 条的上限边缘，但考虑到 3 个项目并行 + 私活，条目增长较快，纯文件全文扫描性能不可接受。
- SQLite 单文件、零服务依赖、FTS5 毫秒级关键词检索，运维成本极低。
- 无向量库，语义检索降级为：FTS5 + 同义词表（如 "React" ↔ "Frontend"，"部署" ↔ "发布"）。
- core 层用同一张 SQLite 数据库的不同表（`core_memories` / `archival_memories`），物理隔离便于按层查询。

---

## 三、Schema 冻结版

```json
{
  "id": "mem_20260916_0001",
  "content": "用户对代码格式要求：始终使用 Prettier，禁止分号",
  "type": "preference",
  "user_id": "u_private_contractor_A",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z",
  "confidence": 0.9,
  "ttl": null,
  "source": "conversation:2026-09-16",
  "pii": true,
  "tags": ["formatting", "private-project-a"],
  "layer": "core",
  "status": "active"
}
```

**字段约束：**
- `id`：`mem_YYYYMMDD_NNNN`，全局唯一，永不复用。
- `type`：限定五类之一。
- `pii`：true 时，`content` 中不得出现真实姓名、邮箱、电话；客户标识只能用 `alias_id`（由 memory-extractor 在抽取阶段替换）。
- `ttl`：preference/decision/fact 类可为 null（永久）；project_status/relation 类默认 180 天。
- `layer`：`core` 或 `archival`，写入时由写入方决定。
- `status`：`active` / `archived` / `deleted`（软删除）。

---

## 四、写读路径

| 决策项 | 规则 |
|---|---|
| **写入时机** | 每轮对话后由 memory-extractor 增量抽取，batch 写入；不实时写入 |
| **载入预算** | core 层每次会话注入上限 **4000 字符**（已确认） |
| **core 层编辑权限** | agent 可自编辑 core 层非 PII 条目；PII 条目（pii=true）只允许 agent 发起**删除请求**，由管线执行实际删除 |
| **archival 层编辑权限** | 受控，仅 pipeline 可写入；agent 只能读取 |
| **PII 处理路径** | 1. 抽取时检测含 PII 内容 → 标记 `pii=true`；2. 写入前调用脱敏函数替换客户真实标识；3. 删除时按 `user_id` 批量软删除 |

---

## 五、遗忘机制

| 规则 | 触发条件 | 动作 |
|---|---|---|
| **TTL 到期** | `ttl` 字段日期已过 | 软删除，`status='deleted'`，日志记录 |
| **降权** | `ttl` 未到期但 `confidence < 0.7` 且 **90 天未被检索** | `confidence *= 0.5`，低于 0.3 时触发 TTL=30 天 |
| **core 层溢出** | core 层总字符 > 4000 | 按 `updated_at` 倒序，删除最早的非关键条目（优先级：preference > decision > fact > project_status） |
| **项目结束** | 用户显式标记项目完成 | 该项目所有 `tags` 含该项目 ID 的条目迁移至 archival，TTL 设为 30 天 |
| **检查频率** | 每次写入后顺带执行 TTL 检查 | 也可定时批处理（每日一次） |

---

## 六、架构决策记录（ADR）

```json
{
  "project": "cross-session-memory-arch",
  "date": "2026-09-16",
  "requirements": [
    {"kind": "project_status", "lifespan": "short", "privacy": "no-pii"},
    {"