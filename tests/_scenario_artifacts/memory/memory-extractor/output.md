```json
[
  {
    "content": "用户决定使用 Postgres 作为数据库，不再考虑 Mongo",
    "type": "decision",
    "confidence": 0.9,
    "evidence_quote": "我们数据库最终选了 Postgres，别再推荐 Mongo 了。",
    "granularity_note": "复合句拆出一条；包含决策结果与排除项",
    "user_id": "alice",
    "duplicate_of": null
  },
  {
    "content": "用户偏好使用 docker compose 进行部署，排斥 k8s",
    "type": "preference",
    "confidence": 0.9,
    "evidence_quote": "部署一律走 docker compose，别整 k8s。",
    "granularity_note": "复合句拆出一条；包含明确偏好与负面约束",
    "user_id": "alice",
    "duplicate_of": null
  }
]
```

**统计摘要：**
- 候选条目总数：2 条
- fact: 0 | preference: 1 | decision: 1 | project_status: 0
- 平均置信度：0.9
- 去重状态：NO_DEDUP（无现有记忆库导出）