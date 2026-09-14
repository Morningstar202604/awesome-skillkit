# 报告模板

## 目录

- [Markdown 报告模板](#markdown-报告模板)
- [JSON 报告模板](#json-报告模板)

## Markdown 报告模板

```markdown
# 深度研究报告：{topic}

**生成时间：** {timestamp}  
**搜索轮次：** {rounds}  
**信源数量：** {source_count}  
**整体可信度：** {trust_score}/1.0

---

## 摘要

{2-3句话核心发现}

---

## 核心发现

### 1. {发现标题}
{详细描述}

**来源：**
- [来源1](url) (可信度: ⭐⭐⭐⭐⭐)
- [来源2](url) (可信度: ⭐⭐⭐⭐)

### 2. {发现标题}
{详细描述}

...

---

## 多方观点

| 视角 | 主要观点 | 支持度 |
|------|---------|--------|
| 技术实现 | {观点} | ⭐⭐⭐⭐ |
| 性能对比 | {观点} | ⭐⭐⭐ |
| 社区反馈 | {观点} | ⭐⭐⭐⭐⭐ |

---

## 争议与分歧

{如有冲突信息，在此列出}

---

## 信息缺口

{如有未覆盖点，在此列出}

---

## 完整来源

| # | 标题 | URL | 可信度 |
|---|------|-----|--------|
| 1 | {title} | [link](url) | ⭐⭐⭐⭐⭐ |

---

*由 deep-research v1.0 生成*
```

## JSON 报告模板

```json
{
  "topic": "研究主题",
  "generated_at": "ISO timestamp",
  "search_stats": {
    "rounds": 3,
    "queries": 12,
    "sources": 25,
    "deduped_sources": 18
  },
  "summary": "核心发现摘要",
  "findings": [
    {
      "title": "发现标题",
      "content": "详细描述",
      "evidence": [
        {"source": "url", "title": "标题", "trust": 0.95}
      ],
      "confidence": 0.88
    }
  ],
  "perspectives": {
    "technical": {"result_count": 10, "key_findings": [...], "trust_score": 0.85},
    "performance": {"result_count": 5, "key_findings": [...], "trust_score": 0.78}
  },
  "conflicts": [
    {
      "topic": "争议点",
      "sources": ["url1", "url2"],
      "conflict": "观点不一致",
      "resolution": "需要进一步查证"
    }
  ],
  "gaps": ["缺少关于X的信息"],
  "sources": [...]
}
```
