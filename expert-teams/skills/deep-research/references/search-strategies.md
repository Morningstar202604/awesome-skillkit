# 搜索策略详解

## 查询拆解策略

### 模式匹配规则

| 模式 | 触发条件 | 生成查询 |
|------|---------|---------|
| A 和 B | 含"和"/"vs"/"对比" | 添加"A vs B"查询 |
| 最佳X | 含"最佳"/"最优" | 添加"X 最佳实践"、"X 优缺点" |
| 如何X | 含"如何"/"怎么" | 添加"X 教程"、"X 示例" |
| X框架 | 含"框架" | 添加"X 介绍"、"X 教程" |

### 时间维度扩展

```python
# 自动添加年份查询
if "2024" not in topic and "2025" not in topic:
    queries.append(f"{topic} 2024")
    queries.append(f"{topic} 2025")
```

### 语言维度扩展

```python
# 自动添加英文查询
if any('\u4e00' <= c <= '\u9fff' for c in topic):
    queries.append(to_english(topic))
```

---

## 搜索引擎选择策略

| 场景 | 首选引擎 | 备选引擎 | 原因 |
|------|---------|---------|------|
| 技术文档 | SearXNG | DDG | 聚合 GitHub/官方文档 |
| 新闻事件 | SearXNG + DDG | - | 多源验证 |
| 中文内容 | DDG | SearXNG | DDG 中文结果更好 |
| 英文内容 | SearXNG | DDG | SearXNG 英文结果更准 |

---

## 可信度评估模型

### 域名可信度权重

| 类型 | 权重 | 示例 |
|------|------|------|
| 官方文档 | 1.0 | docs.python.org, fastapi.tiangolo.com |
| 知名博客 | 0.85 | realpython.com |
| 问答社区 | 0.85 | stackoverflow.com |
| 技术博客 | 0.65 | medium.com, dev.to |
| 中文博客 | 0.6 | csdn.net, jianshu.com |
| 新闻网站 | 0.7 | techcrunch.com |

### 引擎权威性权重

| 引擎 | 权重 | 说明 |
|------|------|------|
| Google | 0.9 | 搜索质量最高 |
| Bing | 0.85 | 微软引擎，质量可靠 |
| DuckDuckGo | 0.7 | 隐私优先，结果稍弱 |

---

## 深度控制策略

| 深度级别 | 轮次 | 每轮查询数 | 适用场景 |
|---------|------|-----------|---------|
| Basic | 1 | 3 | 简单查询 |
| Standard | 2-3 | 5 | 一般调研 |
| Deep | 3-5 | 8 | 复杂课题 |
