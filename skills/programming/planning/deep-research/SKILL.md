---
name: deep-research
description: "Multi-round search with information synthesis and structured report generation. Query decomposition, quality scoring, trustworthiness assessment, deduplication. Use when the user asks to research a topic in depth and needs a comprehensive report with sources. 当用户要求 深度调研 / 多轮检索出报告 / 帮我研究这个主题 时使用。"
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: web-search
  tier: powerful
  verified-date: "2026-09-09"
---

# Deep Research — 深度调研Agent

多轮搜索 + 信息综合 + 结构化报告生成。

## 核心能力

| 能力 | 说明 |
|------|------|
| **多轮搜索** | 自动拆分查询，并行搜索，迭代深化 |
| **信息去重** | URL 去重 + 内容相似度过滤 |
| **来源验证** | 标注可信度（官方/博客/论坛） |
| **引用追踪** | 每个结论都有来源链接 |
| **报告生成** | Markdown + JSON 双格式输出 |

---

## 工作流程

```
用户查询
    │
    ▼
┌─────────────────────────────────────────┐
│ Step 1: 查询分析                         │
│  - 拆分子问题                            │
│  - 确定搜索策略                          │
│  - 设定可信度阈值                         │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Step 2: 并行搜索                         │
│  - 多引擎并发                            │
│  - 多子查询并行                          │
│  - 结果缓存                              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Step 3: 信息综合                         │
│  - 去重 + 去噪                           │
│  - 可信度评分                            │
│  - 冲突检测                              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Step 4: 深度分析（可选）                  │
│  - 对比不同观点                          │
│  - 识别共识与分歧                        │
│  - 找出信息缺口                          │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Step 5: 报告生成                         │
│  - 结构化输出                            │
│  - 引用标注                              │
│  - 可信度评估                            │
└─────────────────────────────────────────┘
```

---

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| topic | 是 | 研究主题 |
| depth | 否 | 搜索深度：`basic` / `standard` / `deep` | standard |
| max_rounds | 否 | 最大搜索轮次 | 3 |
| min_sources | 否 | 最小信源数量 | 5 |
| output_format | 否 | 输出格式：`markdown` / `json` / `both` | markdown |
| focus_areas | 否 | 重点关注领域 | 全部 |

缺失时询问模板：「请提供：① 研究主题。其余我将使用默认值。」

---

## Step 1: 查询分析

### 子问题拆解

```python
def decompose_query(topic: str, focus_areas: List[str] = None) -> List[str]:
    """将复杂查询拆分为子问题"""
    # 规则拆解
    patterns = [
        (r"(\w+)和(\w+)", ["对比 {0} 和 {1}", "{0} vs {1}"]),
        (r"最佳(\w+)", ["{0} 最佳实践", "{0} 优缺点"]),
        (r"如何(\w+)", ["{0} 方法", "{0} 教程", "{0} 示例"]),
    ]
    
    sub_queries = [topic]
    for pattern, templates in patterns:
        match = re.search(pattern, topic)
        if match:
            for tpl in templates:
                sub_queries.append(tpl.format(*match.groups()))
    
    # 添加时间维度
    if "2024" in topic or "2025" in topic or "最新" in topic:
        sub_queries.append(f"{topic} 2024 2025")
    
    # 添加英文查询
    sub_queries.append(to_english_query(topic))
    
    return list(set(sub_queries))[:10]  # 最多10个子查询
```

### 搜索策略选择

| 主题类型 | 策略 | 引擎 | 深度 |
|---------|------|------|------|
| 技术文档 | 精准搜索 | SearXNG | standard |
| 新闻事件 | 多源验证 | SearXNG + DDG | deep |
| 比较分析 | 对比搜索 | 多引擎 | deep |
| 入门教程 | 基础搜索 | DDG | basic |

---

## Step 2: 并行搜索

### 多引擎并发

```python
async def parallel_search(queries: List[str]) -> Dict[str, List[Dict]]:
    """并发执行多个搜索"""
    import asyncio
    from search_client import search
    
    async def search_one(q: str) -> tuple:
        try:
            result = await asyncio.to_thread(search, q, use_cache=True)
            return (q, result)
        except Exception as e:
            return (q, {"error": str(e), "results": []})
    
    # 并发执行
    tasks = [search_one(q) for q in queries]
    results = await asyncio.gather(*tasks)
    
    return {q: r for q, r in results}
```

### 搜索结果质量评估

```python
def evaluate_result_quality(result: Dict) -> float:
    """评估单个搜索结果的质量"""
    score = 0.0
    
    # 1. 域名权威度
    domain = result.get("parsed_url", {}).get("domain", "")
    domain_score = DOMAIN_AUTHORITY.get(domain, 0.3)
    score += domain_score * 0.3
    
    # 2. 内容完整性
    content = result.get("content", "")
    if len(content) > 100:
        score += 0.2
    elif len(content) > 50:
        score += 0.1
    
    # 3. 标题相关性
    title = result.get("title", "")
    if title and len(title) > 10:
        score += 0.2
    
    # 4. 来源多样性
    engine = result.get("engine", "")
    if engine in ["google", "bing"]:
        score += 0.15
    elif engine == "duckduckgo":
        score += 0.1
    
    # 5. 新鲜度（从URL推断）
    if "2024" in result.get("url", "") or "2025" in result.get("url", ""):
        score += 0.15
    
    return min(score, 1.0)
```

---

## Step 3: 信息综合

### 去重策略

| 去重级别 | 方法 | 阈值 |
|---------|------|------|
| URL 去重 | 完全匹配 | 100% |
| 域名去重 | 同一域名最多取3条 | 3条 |
| 内容去重 | 相似度 > 0.8 合并 | 0.8 |
| 观点去重 | 相同结论合并引用 | - |

### 可信度评估

```python
def assess_trustworthiness(results: List[Dict]) -> Dict:
    """评估信息来源可信度"""
    trust_scores = {}
    
    for r in results:
        domain = r.get("parsed_url", {}).get("domain", "")
        engine = r.get("engine", "")
        
        # 域名可信度
        domain_trust = DOMAIN_TRUSTWORTHINESS.get(domain, 0.5)
        
        # 引擎可信度
        engine_trust = {"google": 0.9, "bing": 0.85, "duckduckgo": 0.7}.get(engine, 0.6)
        
        # 综合可信度
        trust = domain_trust * 0.6 + engine_trust * 0.4
        trust_scores[r["url"]] = trust
    
    return trust_scores
```

### 冲突检测

```python
def detect_conflicts(results: List[Dict]) -> List[Dict]:
    """检测相互矛盾的信息"""
    conflicts = []
    
    # 按主题聚类
    clusters = cluster_by_topic(results)
    
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        
        # 检查内容差异
        for i, r1 in enumerate(cluster):
            for r2 in cluster[i+1:]:
                if is_contradictory(r1, r2):
                    conflicts.append({
                        "topic": cluster[0].get("topic", "unknown"),
                        "sources": [r1["url"], r2["url"]],
                        "conflict": "观点不一致",
                        "resolution": "需要进一步查证"
                    })
    
    return conflicts
```

---

## Step 4: 深度分析（可选）

### 多视角分析

```python
def multi_perspective_analysis(topic: str, results: List[Dict]) -> Dict:
    """从多个视角分析同一话题"""
    perspectives = {
        "技术实现": filter_by_topic(results, "implementation|code|example"),
        "性能对比": filter_by_topic(results, "performance|benchmark|compare"),
        "最佳实践": filter_by_topic(results, "best practice|tutorial|guide"),
        "社区反馈": filter_by_topic(results, "reddit|forum|review|opinion"),
    }
    
    return {
        "topic": topic,
        "perspectives": {
            name: {
                "result_count": len(res),
                "key_findings": extract_key_findings(res),
                "trust_score": calculate_avg_trust(res),
            }
            for name, res in perspectives.items()
        }
    }
```

### 信息缺口识别

```python
def identify_gaps(topic: str, results: List[Dict]) -> List[str]:
    """识别未覆盖的信息点"""
    covered = extract_topics(results)
    
    # 预定义的关注点
    expected_topics = get_expected_topics(topic)
    
    gaps = []
    for expected in expected_topics:
        if not any(similar(expected, covered_i) for covered_i in covered):
            gaps.append(f"缺少关于 '{expected}' 的信息")
    
    return gaps
```

---

## Step 5: 报告生成

### Markdown 报告结构

```markdown
# 研究报告：{topic}

**生成时间：** {timestamp}  
**搜索轮次：** {rounds}  
**信源数量：** {source_count}  
**整体可信度：** {trust_score}/1.0

---

## 摘要

{2-3句话的核心发现}

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

### JSON 报告结构

```json
{
  "topic": "研究主题",
  "generated_at": "2026-09-09T10:00:00Z",
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
    "technical": {...},
    "performance": {...},
    "community": {...}
  },
  "conflicts": [...],
  "gaps": [...],
  "sources": [...]
}
```

---

## 与 code-intent-planner 的协作

当研究主题涉及技术方案时，自动衔接：

```
deep-research 输出:
{
  "topic": "FastAPI vs Flask",
  "findings": [...],
  "recommendation": "推荐 FastAPI"
}
    │
    ▼
code-intent-planner 输入:
{
  "raw_input": "使用 FastAPI 实现用户认证模块",
  "context": "根据调研，FastAPI 更适合此场景"
}
    │
    ▼
code-intent-planner 输出:
{
  "intent_type": "implement",
  "sub_tasks": [...],
  "solution": "FastAPI CRUD 方案"
}
```

---

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 所有搜索引擎超时 | 网络问题 | 提示用户检查网络 |
| 结果不足 | 查询过于具体 | 扩展查询词，增加轮次 |
| 可信度低 | 来源多为博客/论坛 | 标注低可信度，建议人工验证 |
| 冲突严重 | 观点分歧大 | 如实呈现，不强行统一 |

---

## 参考

- references/search-strategies.md —— 搜索策略详解
- references/report-templates.md —— 报告模板
- references/examples.md —— 真实调研案例