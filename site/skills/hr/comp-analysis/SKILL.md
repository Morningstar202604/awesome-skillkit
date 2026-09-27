---
name: comp-analysis
description: >-
  Analyze compensation — benchmarking, band placement, and equity modeling. Trigger with "what should we pay a [role]", "is this offer competitive", "model this equity grant", or when uploading comp data to find outliers and retention risks.
description_zh: "薪酬分析：市场对标、职级带宽定位与股权建模，识别异常与留人风险。"
license: Apache-2.0
compatibility: 任意兼容 Agent Skills 的工具可用；部分技能假设已连接企业系统（CRM/HRIS/文档库），未连接时按文内提示降级。
metadata:
  author: "anthropics/knowledge-work-plugins 上游（Apache-2.0）"
  version: "1.0.0"
  category: hr
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/anthropics/knowledge-work-plugins/tree/main"
---

# /comp-analysis

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Analyze compensation data for benchmarking, band placement, and planning. Helps benchmark compensation against market data for hiring, retention, and equity planning.

## Usage

```
/comp-analysis $ARGUMENTS
```

## What I Need From You

**Option A: Single role analysis**
"What should we pay a Senior Software Engineer in SF?"

**Option B: Upload comp data**
Upload a CSV or paste your comp bands. I'll analyze placement, identify outliers, and compare to market.

**Option C: Equity modeling**
"Model a refresh grant of 10K shares over 4 years at a $50 stock price."

## Compensation Framework

### Components of Total Compensation
- **Base salary**: Cash compensation
- **Equity**: RSUs, stock options, or other equity
- **Bonus**: Annual target bonus, signing bonus
- **Benefits**: Health, retirement, perks (harder to quantify)

### Key Variables
- **Role**: Function and specialization
- **Level**: IC levels, management levels
- **Location**: Geographic pay adjustments
- **Company stage**: Startup vs. growth vs. public
- **Industry**: Tech vs. finance vs. healthcare

### Data Sources
- **With ~~compensation data**: Pull verified benchmarks
- **Without**: Use web research, public salary data, and user-provided context
- Always note data freshness and source limitations

## Output

Provide percentile bands (25th, 50th, 75th, 90th) for base, equity, and total comp. Include location adjustments and company-stage context.

```markdown
## Compensation Analysis: [Role/Scope]

### Market Benchmarks
| Percentile | Base | Equity | Total Comp |
|------------|------|--------|------------|
| 25th | $[X] | $[X] | $[X] |
| 50th | $[X] | $[X] | $[X] |
| 75th | $[X] | $[X] | $[X] |
| 90th | $[X] | $[X] | $[X] |

**Sources:** [Web research, compensation data tools, or user-provided data]

### Band Analysis (if data provided)
| Employee | Current Base | Band Min | Band Mid | Band Max | Position |
|----------|-------------|----------|----------|----------|----------|
| [Name] | $[X] | $[X] | $[X] | $[X] | [Below/At/Above] |

### Recommendations
- [Specific compensation recommendations]
- [Equity considerations]
- [Retention risks if applicable]
```

## If Connectors Available

If **~~compensation data** is connected:
- Pull verified market benchmarks by role, level, and location
- Compare your bands against real-time market data

If **~~HRIS** is connected:
- Pull current employee comp data for band analysis
- Identify outliers and retention risks automatically

## Tips

1. **Location matters** — Always specify location for benchmarking. SF vs. Austin vs. London are very different.
2. **Total comp, not just base** — Include equity, bonus, and benefits for a complete picture.
3. **Keep data confidential** — Comp data is sensitive. Results stay in your conversation.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 anthropics/knowledge-work-plugins（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：anthropics/knowledge-work-plugins 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
