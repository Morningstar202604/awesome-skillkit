## Sweep 执行报告

**模式：** 全库清扫（sweep）  
**执行时间：** 2026-09-20（基于库内最新日期推断）  
**库条数：** 3 → 1（净删除 2 条）

---

### 逐条裁决

| ID | 操作 | 理由 |
|---|---|---|
| m1 | **NOOP** | 置信度 0.95、近期命中、无 TTL → 保留 |
| m2 | **DELETE** | TTL "30d" 早于今日过期；且 confidence=0.4 已低于删除阈值，双重命中 |
| m3 | **NOOP** | 置信度 0.9、近期更新、高命中 → 保留 |

---

### 三把扫帚执行明细

**1. TTL 扫帚**  
- 扫描条目：3 条  
- 命中过期：1 条（m2，ttl="30d"，到期日约为 2026-08-19，早于今日）  
- 删除操作：`DELETE m2`

**2. 衰减扫帚**  
- 扫描条目：2 条（排除已 TTL 删除的 m2）  
- m1：hit_count=42 > 0，confidence=0.95 > 0.7 → 不触发  
- m3：hit_count=17 > 0，confidence=0.9 > 0.7 → 不触发  
- 结果：无条目被衰减或二次删除

**3. 压缩扫帚**  
- 当前库仅 1 个主题类别（各条目 type/user_id/tags 均未提供，默认视为独立主题）  
- 单主题条目数 ≤ 10 → 不触发压缩  
- 结果：无条目被合并

---

### 最终库状态

```json
[
  {
    "id": "m1",
    "content": "用户数据库选型用 Postgres，拒绝 Mongo",
    "confidence": 0.95,
    "updated_at": "2026-09-20",
    "hit_count": 42,
    "ttl": null
  },
  {
    "id": "m3",
    "content": "用户偏好暗色主题",
    "confidence": 0.9,
    "updated_at": "2026-09-18",
    "hit_count": 17,
    "ttl": null
  }
]
```

---

### operations.json（审计日志）

```json
{
  "date": "2026-09-20",
  "mode": "sweep",
  "operations": [
    {
      "op": "DELETE",
      "target_id": "m2",
      "before": "{\"id\":\"m2\",\"content\":\"某次构建失败因为断网\",\"confidence\":0.4,\"updated_at\":\"2026-07-20\",\"hit_count\":0,\"ttl\":\"30d\"}",
      "after": null,
      "reason": "TTL expired (30d from 2026-07-20) and confidence 0.4 below threshold 0.4"
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

---

### 清理策略说明

- **TTL 优先**：m2 的 `ttl="30d"` 明确设定了生命周期，到期即删，无需看其他字段。这是最硬性的删除依据。
- **置信度兜底**：即使 m2 没有 TTL，其 confidence=0.4 也已触及删除阈值，双重保障。
- **衰减未触发**：剩余两条 hit_count 均不为零且 confidence 高于 0.7，无需衰减。
- **压缩未触发**：条目数太少，单主题未超限，压缩不经济。

审计日志已随库一并归档，m2 的删除原因可追溯。