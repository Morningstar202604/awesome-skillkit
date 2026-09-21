# Memory Extraction Results

**Input check:** Dialogue text ✓ | user_id = `alice` ✓ | Memory export: NO_DEDUP mode
**Segments:** 1 segment (short dialogue, single topic cluster)

---

## candidates.json

```json
[
  {
    "content": "用户数据库最终选择了 Postgres，后续不要再推荐 Mongo",
    "type": "decision",
    "confidence": 0.9,
    "evidence_quote": "我们数据库最终选了 Postgres，别再推荐 Mongo 了。",
    "granularity_note": "复合决策拆为一条（选型结果 + 偏好约束绑定于同一决策）",
    "user_id": "alice",
    "duplicate_of": null
  },
  {
    "content": "用户部署方式固定为 docker compose，后续不要再推荐 k8s",
    "type": "decision",
    "confidence": 0.9,
    "evidence_quote": "部署一律走 docker compose，别整 k8s。",
    "granularity_note": "单一决策，无需拆分",
    "user_id": "alice",
    "duplicate_of": null
  }
]
```

---

## 统计摘要

| 指标 | 值 |
|---|---|
| 候选条目总数 | 2 |
| type=decision | 2 |
| type=fact | 0 |
| type=preference | 0 |
| type=project_status | 0 |
| 平均 confidence | 0.90 |
| 去重模式 | **NO_DEDUP**（无现有记忆库导出，confidence 上限压至 0.8 不适用，因用户原话显式，维持 0.9） |
| 推断条目 | 0 |
| 敏感类别条目 | 0 |

---

## 抽取说明

- 两条均为**决策（decision）**：用户用"最终选了""一律"等词明确落定选择，且附带否定约束（别再推荐 X），符合决策类信号。
- 未抽取为 preference 的原因："别再推荐 Mongo/k8s"是对已有技术决策的约束强化，而非泛化好恶；"最终选了/一律走"是拍板动作，非持续性偏好表达。
- 无敏感类别，无推断条目，无代词残留，无需拆分。