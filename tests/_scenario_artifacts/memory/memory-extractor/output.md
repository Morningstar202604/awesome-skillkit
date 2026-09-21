```json
[
  {
    "content": "用户已将数据库落定为 PostgreSQL",
    "type": "decision",
    "confidence": 0.9,
    "evidence_quote": "我们数据库最终选了 Postgres",
    "granularity_note": "复合句中的决策事实；与后文偏好分开，此为已落定的技术选型",
    "user_id": "alice",
    "duplicate_of": null
  },
  {
    "content": "用户不希望再被推荐 MongoDB",
    "type": "preference",
    "confidence": 0.9,
    "evidence_quote": "别再推荐 Mongo 了",
    "granularity_note": "由同一句中'别再推荐'推导出的明确偏好信号，与决策条目同源但语义不同（前者落定选型，后者约束后续行为）",
    "user_id": "alice",
    "duplicate_of": null
  },
  {
    "content": "用户部署方式偏好 docker compose，明确排斥 k8s",
    "type": "preference",
    "confidence": 0.9,
    "evidence_quote": "部署一律走 docker compose，别整 k8s",
    "granularity_note": "一句话包含正偏好（docker compose）与负偏好（排斥 k8s）两个信号，合并为一条偏好条目；'一律''别整'表明态度强硬，置信度高",
    "user_id": "alice",
    "duplicate_of": null
  }
]
```

**统计行**
- fact: 0 / preference: 2 / decision: 1 / project_status: 0
- 平均 confidence: 0.9
- 去重模式：NO_DEDUP（无现有记忆库导出）