开始执行全库清扫（sweep）模式。先做前置自检与快照统计。

## 前置自检

- 库为合法 JSON 数组，每条含 id → 通过。
- sweep 模式无需候选，跳过候选校验。
- 无需 purge 删除指令。

## 快照统计

| 条目标 | 内容摘要 | confidence | updated_at | hit_count | ttl |
|---|---|---|---|---|---|
| m1 | 数据库选型用 Postgres，拒绝 Mongo | 0.95 | 2026-09-20 | 42 | null |
| m2 | 某次构建失败因为断网 | 0.40 | 2026-07-20 | 0 | 30d |
| m3 | 用户偏好暗色主题 | 0.90 | 2026-09-18 | 17 | null |

库前条数：**3**

参考日期取 `2026-09-20`（以库中最新日期为基准，符合"TTL 扫帚：ttl 字段早于今天"的语义）。

---

## 步骤 1：TTL 扫帚

规则：`ttl` 字段早于今天的条目 DELETE。

- m1：ttl=null → 不触发。
- m2：ttl="30d" → 需判断是否已过期。按惯例 `30d` 表示从 **创建/首次入库** 起算 30 天。库中无 `created_at`，保守用 `updated_at` = 2026-07-20 作为参考起点，则过期日为 **2026-08-19**。参考日 2026-09-20 已超出 → **DELETE**。
- m3：ttl=null → 不触发。

**TTL 删除：1 条（m2）**

---

## 步骤 2：衰减扫帚

规则：超过 90 天未命中 且 confidence < 0.7 → confidence × 0.8；跌破 0.4 → DELETE。

剩余条目：m1、m3（m2 已删）。

- m1：updated_at=2026-09-20，距参考日 0 天 → 未超 90 天 → 不衰减。
- m3：updated_at=2026-09-18，距参考日 2 天 → 未超 90 天 → 不衰减。

**衰减操作：0 条**

---

## 步骤 3：压缩扫帚

规则：同主题（同 user_id + type + tags）条目 > 10 条时压缩。本库仅 2 条，且无 user_id/type/tags 字段表明可分组 → **跳过压缩**。

**压缩操作：0 条**

---

## 步骤 4：执行四操作并生成审计日志

本次实际只发生 1 次 DELETE，其余为 NOOP（保留）。

```json
{
  "date": "2026-09-20",
  "mode": "sweep",
  "operations": [
    {
      "op": "DELETE",
      "target_id": "m2",
      "before": "{\"id\": \"m2\", \"content\": \"某次构建失败因为断网\", \"confidence\": 0.4, \"updated_at\": \"2026-07-20\", \"hit_count\": 0, \"ttl\": \"30d\"}",
      "after": null,
      "reason": "TTL expired: ttl=30d from 2026-07-20, expired 2026-08-19, reference date 2026-09-20"
    },
    {
      "op": "NOOP",
      "target_id": "m1",
      "before": "{\"id\": \"m1\", \"content\": \"用户数据库选型用 Postgres，拒绝 Mongo\", \"confidence\": 0.95, \"updated_at\": \"2026-09-20\", \"hit_count\": 42, \"ttl\": null}",
      "after": null,
      "reason": "TTL not set; within 90-day decay window; high hit count"
    },
    {
      "op": "NOOP",
      "target_id": "m3",
      "before": "{\"id\": \"m3\", \"content\": \"用户偏好暗色主题\", \"confidence\": 0.9, \"updated_at\": \"2026-09-18\", \"hit_count\": 17, \"ttl\": null}",
      "after": null,
      "reason": "TTL not set; within 90-day decay window; high hit count"
    }
  ],
  "sweep": {
    "ttl_deleted": 1,
    "decayed": 0,
    "compacted_topics": 0
  },
  "stats": {
    "before": 3,
    "after": 2
  }
}
```

## 更新后记忆库

```json
[
  {"id": "m1", "content": "用户数据库选型用 Postgres，拒绝 Mongo", "confidence": 0.95, "updated_at": "2026-09-20", "hit_count": 42, "ttl": null},
  {"id": "m3", "content": "用户偏好暗色主题", "confidence": 0.9, "updated_at": "2026-09-18", "hit_count": 17, "ttl": null}
]
```

## 清理策略说明

1. **TTL 扫帚**是本次主要删除来源：m2 带 `ttl=30d`，以 `updated_at` 2026-07-20 为起点，30 天后即 2026-08-19 已过期，参考日 2026-09-20 已超期约 1 个月 → 果断删除。该条目 confidence 仅 0.4，本就低可信，属于"一次性偶发事件"类噪音记忆，留之无益。
2. **衰减扫帚**未触发：m1、m3 均为近期（2 天内）更新且命中频次高，不在 90 天衰减窗口内。
3. **压缩扫帚**未触发：条目数远少于 10 条阈值，且缺乏 user_id/type/tags 维度进行主题分组。
4. **审计合规**：所有操作写入 `operations.json`，DELETE 保留 before 全文以便回溯；purge 式删除权在本例中由系统 TTL 策略自动触发，非用户显式指令，但仍留完整日志。

库条数由 3 → 2，无悬空项，无冲突未决项。