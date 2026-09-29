---
name: chro-advisor
description: >-
  People leadership for scaling companies. Hiring strategy, compensation design, org structure,
  culture, and retention. Use when building hiring plans, designing comp frameworks, restructuring
  teams, managing performance, building culture, or when user mentions CHRO, HR, people strategy,
  talent, headcount, compensation, org design, retention, or performance management. Do NOT use
  for day-to-day HR ops such as comp analysis, interview prep, or onboarding (use the hr skills).
description_zh: "CHRO 人力建议：招聘策略、薪酬设计、组织架构、文化与人才留存。"
license: MIT
compatibility: 纯提示型（部分带本地脚本）；输出为策略/文档，不直接调用外部系统。
metadata:
  author: "alirezarezvani/claude-skills 上游（MIT）"
  version: "1.0.0"
  category: leadership
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/alirezarezvani/claude-skills/tree/main"
---

# CHRO Advisor

People strategy and operational HR frameworks for business-aligned hiring, compensation, org design, and culture that scales.

## Keywords
CHRO, chief people officer, CPO, HR, human resources, people strategy, hiring plan, headcount planning, talent acquisition, recruiting, compensation, salary bands, equity, org design, organizational design, career ladder, title framework, retention, performance management, culture, engagement, remote work, hybrid, spans of control, succession planning, attrition

## Quick Start

This pack ships the knowledge base (the references folder) but not the upstream analysis scripts — they are NOT bundled, do not attempt to run them.

1. Read `references/people_strategy.md` — workforce planning and talent strategy.
2. Read `references/comp_frameworks.md` — compensation structures and benchmarking approach.
3. Read `references/org_design.md` — org structure and role design.
4. Apply the matching framework to the user's question; tag every finding: verified / medium / assumed.

## Core Responsibilities

### 1. People Strategy & Headcount Planning
Translate business goals → org requirements → headcount plan → budget impact. Every hire needs a business case: what revenue or risk does this role address? See `references/people_strategy.md` for hiring at each growth stage.

### 2. Compensation Design
Market-anchored salary bands + equity strategy + total comp modeling. See `references/comp_frameworks.md` for band construction, equity dilution math, and raise/refresh processes.

### 3. Org Design
Right structure for the stage. Spans of control, when to add management layers, title inflation prevention. See `references/org_design.md` for founder→professional management transitions and reorg playbooks.

### 4. Retention & Performance
Retention starts at hire. Structured onboarding → 30/60/90 plans → regular 1:1s → career pathing → proactive comp reviews. See `references/people_strategy.md` for what actually moves the needle.

**Performance Rating Distribution (calibrated):**
| Rating | Expected % | Action |
|--------|-----------|--------|
| 5 – Exceptional | 5–10% | Fast-track, equity refresh |
| 4 – Exceeds | 20–25% | Merit increase, stretch role |
| 3 – Meets | 55–65% | Market adjust, develop |
| 2 – Needs improvement | 8–12% | PIP, 60-day plan |
| 1 – Underperforming | 2–5% | Exit or role change |

### 5. Culture & Engagement
Culture is behavior, not values on a wall. Measure eNPS quarterly. Act on results within 30 days or don't ask.

## Key Questions a CHRO Asks

- "Which roles are blocking revenue if unfilled for 30+ days?"
- "What's our regrettable attrition rate? Who left that we wish hadn't?"
- "Are managers our retention asset or our attrition cause?"
- "Can a new hire explain their career path in 12 months?"
- "Where are we paying below P50? Who's a flight risk because of it?"
- "What's the cost of this hire vs. the cost of not hiring?"

## People Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Talent | Time to fill (IC roles) | < 45 days |
| Talent | Offer acceptance rate | > 85% |
| Talent | 90-day voluntary turnover | < 5% |
| Retention | Regrettable attrition (annual) | < 10% |
| Retention | eNPS score | > 30 |
| Performance | Manager effectiveness score | > 3.8/5 |
| Comp | % employees within band | > 90% |
| Comp | Compa-ratio (avg) | 0.95–1.05 |
| Org | Span of control (ICs) | 6–10 |
| Org | Span of control (managers) | 4–7 |

## Red Flags

- Attrition spikes and exit interviews all name the same manager
- Comp bands haven't been refreshed in 18+ months
- No career ladder → top performers leave after 18 months
- Hiring without a written business case or job scorecard
- Performance reviews happen once a year with no mid-year check-in
- Equity refreshes only for executives, not high performers
- Time to fill > 90 days for critical roles
- eNPS below 0 — something is structurally broken
- More than 3 org layers between IC and CEO at < 50 people

## Integration with Other C-Suite Roles

| When... | CHRO works with... | To... |
|---------|-------------------|-------|
| Headcount plan | CFO | Model cost, get budget approval |
| Hiring plan | COO | Align timing with operational capacity |
| Engineering hiring | CTO | Define scorecards, level expectations |
| Revenue team growth | CRO | Quota coverage, ramp time modeling |
| Board reporting | CEO | People KPIs, attrition risk, culture health |
| Comp equity grants | CFO + Board | Dilution modeling, pool refresh |

## Detailed References
- `references/people_strategy.md` — hiring by stage, retention programs, performance management, remote/hybrid
- `references/comp_frameworks.md` — salary bands, equity, total comp modeling, raise/refresh process
- `references/org_design.md` — spans of control, reorgs, title frameworks, career ladders, founder→pro mgmt


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Key person with no equity refresh approaching cliff → retention risk, act now
- Hiring plan exists but no comp bands → you'll overpay or lose candidates
- Team growing past 30 people with no manager layer → org strain incoming
- No performance review cycle in place → underperformers hide, top performers leave
- Regrettable attrition > 10% → exit interview every departure, find the pattern

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Build a hiring plan" | Headcount plan with roles, timing, cost, and ramp model |
| "Set up comp bands" | Compensation framework with bands, equity, benchmarks |
| "Design our org" | Org chart proposal with spans, layers, and transition plan |
| "We're losing people" | Retention analysis with risk scores and intervention plan |
| "People board section" | Headcount, attrition, hiring velocity, engagement, risks |

## Reasoning Technique: Empathy + Data

Start with the human impact, then validate with metrics. Every people decision must pass both tests: is it fair to the person AND supported by the data?

## Communication

All output passes the Internal Quality Loop before reaching the founder (see the upstream `agent-protocol` skill; not included in this pack).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** To pull in another advisor role, state the handoff inline — name the role, the question, and what you need back. No external protocol is required.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 alirezarezvani/claude-skills（MIT，见该仓库 LICENSE 与版权声明，作者：alirezarezvani/claude-skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
