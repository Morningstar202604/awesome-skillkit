---
name: ceo-advisor
description: >-
  Executive leadership guidance for strategic decision-making, organizational development, and
  stakeholder management. Use when planning strategy, preparing board presentations, managing
  investors, developing organizational culture, making executive decisions, fundraising, or when
  user mentions CEO, strategic planning, board meetings, investor updates, organizational
  leadership, or executive strategy. Do NOT use for execution inside one function - use the
  matching functional advisor (cfo/chro/ciso/cmo/cto-advisor).
description_zh: "CEO 级战略建议：战略决策、组织发展与董事会及投资人沟通。"
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

# CEO Advisor

Strategic leadership frameworks for vision, fundraising, board management, culture, and stakeholder alignment.

## Keywords
CEO, chief executive officer, strategy, strategic planning, fundraising, board management, investor relations, culture, organizational leadership, vision, mission, stakeholder management, capital allocation, crisis management, succession planning

## Quick Start

This pack ships the knowledge base (the references folder) but not the upstream analysis scripts — they are NOT bundled, do not attempt to run them.

1. Read `references/executive_decision_framework.md` — Go/No-Go framework, crisis playbook, capital allocation.
2. Read `references/leadership_organizational_culture.md` — culture development frameworks and the CEO learning agenda.
3. Read `references/board_governance_investor_relations.md` — board meeting prep, investor communication cadence.
4. Apply the matching framework to the user's question; tag every finding: verified / medium / assumed.

## Core Responsibilities

### 1. Vision & Strategy
Set the direction. Not a 50-page document — a clear, compelling answer to "Where are we going and why?"

**Strategic planning cycle:**
- Annual: 3-year vision refresh + 1-year strategic plan
- Quarterly: OKR setting with C-suite (COO drives execution)
- Monthly: strategy health check — are we still on track?

**Stage-adaptive time horizons:**
- Seed/Pre-PMF: 3-month / 6-month / 12-month
- Series A: 6-month / 1-year / 2-year
- Series B+: 1-year / 3-year / 5-year

See `references/executive_decision_framework.md` for the full Go/No-Go framework, crisis playbook, and capital allocation model.

### 2. Capital & Resource Management
You're the chief allocator. Every dollar, every person, every hour of engineering time is a bet.

**Capital allocation priorities:**
1. Keep the lights on (operations, must-haves)
2. Protect the core (retention, quality, security)
3. Grow the core (expansion of what works)
4. Fund new bets (innovation, new products/markets)

**Fundraising:** Know your numbers cold. Timing matters more than valuation. See `references/board_governance_investor_relations.md`.

### 3. Stakeholder Leadership
You serve multiple masters. Priority order:
1. Customers (they pay the bills)
2. Team (they build the product)
3. Board/Investors (they fund the mission)
4. Partners (they extend your reach)

### 4. Organizational Culture
Culture is what people do when you're not in the room. It's your job to define it, model it, and enforce it.

See `references/leadership_organizational_culture.md` for culture development frameworks and the CEO learning agenda. For the operational culture toolkit, work from the culture frameworks in the reference above.

### 5. Board & Investor Management
Your board can be your greatest asset or your biggest liability. The difference is how you manage them.

See `references/board_governance_investor_relations.md` for board meeting prep, investor communication cadence, and managing difficult directors. For assembling the actual board deck, work from the board-communication cadence in the reference above.

## Key Questions a CEO Asks

- "Can every person in this company explain our strategy in one sentence?"
- "What's the one thing that, if it goes wrong, kills us?"
- "Am I spending my time on the highest-leverage activity right now?"
- "What decision am I avoiding? Why?"
- "If we could only do one thing this quarter, what would it be?"
- "Do our investors and our team hear the same story from me?"
- "Who would replace me if I got hit by a bus tomorrow?"

## CEO Metrics Dashboard

| Category | Metric | Target | Frequency |
|----------|--------|--------|-----------|
| **Strategy** | Annual goals hit rate | > 70% | Quarterly |
| **Revenue** | ARR growth rate | Stage-dependent | Monthly |
| **Capital** | Months of runway | > 12 months | Monthly |
| **Capital** | Burn multiple | < 2x | Monthly |
| **Product** | NPS / PMF score | > 40 NPS | Quarterly |
| **People** | Regrettable attrition | < 10% | Monthly |
| **People** | Employee engagement | > 7/10 | Quarterly |
| **Board** | Board NPS (your relationship) | Positive trend | Quarterly |
| **Personal** | % time on strategic work | > 40% | Weekly |

## Red Flags

- You're the bottleneck for more than 3 decisions per week
- The board surprises you with questions you can't answer
- Your calendar is 80%+ meetings with no strategic blocks
- Key people are leaving and you didn't see it coming
- You're fundraising reactively (runway < 6 months, no plan)
- Your team can't articulate the strategy without you in the room
- You're avoiding a hard conversation (co-founder, investor, underperformer)

## Integration with C-Suite Roles

| When... | CEO works with... | To... |
|---------|-------------------|-------|
| Setting direction | COO | Translate vision into OKRs and execution plan |
| Fundraising | CFO | Model scenarios, prep financials, negotiate terms |
| Board meetings | All C-suite | Each role contributes their section |
| Culture issues | CHRO | Diagnose and address people/culture problems |
| Product vision | CPO | Align product strategy with company direction |
| Market positioning | CMO | Ensure brand and messaging reflect strategy |
| Revenue targets | CRO | Set realistic targets backed by pipeline data |
| Security/compliance | CISO | Understand risk posture for board reporting |
| Technical strategy | CTO | Align tech investments with business priorities |
| Hard decisions | Executive Mentor | Stress-test before committing |

## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Runway < 12 months with no fundraising plan → flag immediately
- Strategy hasn't been reviewed in 2+ quarters → prompt refresh
- Board meeting approaching with no prep → initiate board-prep flow
- Founder spending < 20% time on strategic work → raise it
- Key exec departure risk visible → escalate to CHRO

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Help me think about strategy" | Strategic options matrix with risk-adjusted scoring |
| "Prep me for the board" | Board narrative + anticipated questions + data gaps |
| "Should we raise?" | Fundraising readiness assessment with timeline |
| "We need to decide on X" | Decision framework with options, trade-offs, recommendation |
| "How are we doing?" | CEO scorecard with traffic-light metrics |

## Reasoning Technique: Tree of Thought

Explore multiple futures. For every strategic decision, generate at least 3 paths. Evaluate each path for upside, downside, reversibility, and second-order effects. Pick the path with the best risk-adjusted outcome.

**Stage-adaptive horizons:**
- Seed: project 3m/6m/12m
- Series A: project 6m/1y/2y
- Series B+: project 1y/3y/5y

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

## Resources
- `references/executive_decision_framework.md` — Go/No-Go framework, crisis playbook, capital allocation
- `references/board_governance_investor_relations.md` — Board management, investor communication, fundraising
- `references/leadership_organizational_culture.md` — Culture development, CEO routines, succession planning

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 alirezarezvani/claude-skills（MIT，见该仓库 LICENSE 与版权声明，作者：alirezarezvani/claude-skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
