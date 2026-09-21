## 全库清扫报告

**模式：** sweep（全库清扫）
**执行时间：** 2026-09-21
**库前条目数：** 3
**库后条目数：** 2
**清理总量：** 1 条

---

### 逐条裁决

| 条目 | 处置 | 理由 |
|---|---|---|
| m1 | **保留** | TTL 为 null（永不过期），confidence=0.95 远超阈值，hit_count=42 命中频繁，属高价值核心记忆。 |
| m2 | **DELETE（TTL 扫帚）** | ttl=30d 且 updated_at=2026-07-20，距今已超 60 天，TTL 已过期。即使 ttl 字段语义模糊，confidence=0.4 也已达删除阈值，双重理由支持删除。 |
| m3 | **保留** | TTL 为 null，confidence=0.9 高，hit_count=17 适中，主题稳定。 |

---

### 三把扫帚执行记录

1. **TTL 扫帚：** m2 因 ttl 过期删除（1 条）。
2. **衰减扫帚：** 无其他条目满足「90 天未命中且 confidence<0.7」条件，跳过。
3. **压缩扫帚：** 同主题（user_id 未指定按全局统计）共 2 条保留条目，不足 10 条触发线，跳过。

---

### 审计日志（operations.json）

```json
{
  "date": "2026-09-21",
  "mode": "sweep",
  "operations": [
    {
      "op": "DELETE",
      "target_id": "m2",
      "before": "某次构建失败因为断网",
      "after": null,
      "reason": "TTL expired (ttl=30d, updated_at=2026-07-20, days elapsed > 60); confidence=0.4 also below deletion threshold"
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

### 清扫后记忆库

```json
[
  {"id": "m1", "content": "用户数据库选型用 Postgres，拒绝 Mongo", "confidence": 0.95, "updated_at": "2026-09-20", "hit_count": 42, "ttl": null},
  {"id": "m3", "content": "用户偏好暗色主题", "confidence": 0.9, "updated_at": "2026-09-18", "hit_count": 17, "ttl": null}
]
```

**说明：** m2 的内容「某次构建失败因为断网」属于偶发事件记录，置信度已跌至 0.4，且带 30 天 TTL，符合「短期上下文不应污染长期记忆」的设计意图，删除合理。若用户后续重新发生类似故障并标记重要性，memory-extractor 会重新抽取为新候选。