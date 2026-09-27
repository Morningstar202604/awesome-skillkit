---
name: onboarding
description: >-
  Generate an onboarding checklist and first-week plan for a new hire. Use when someone has a start date coming up, building the pre-start task list (accounts, equipment, buddy), scheduling Day 1 and Week 1, or setting 30/60/90-day goals for a new team member.
description_zh: "为新员工生成入职清单与首周计划：入职前账号设备与伙伴安排、Day 1 与第一周日程，以及 30/60/90 天目标。"
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

# /onboarding

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

Generate a comprehensive onboarding plan for a new team member.

## Usage

```
/onboarding $ARGUMENTS
```

## What I Need From You

- **New hire name**: Who's starting?
- **Role**: What position?
- **Team**: Which team are they joining?
- **Start date**: When do they start?
- **Manager**: Who's their manager?

## Output

```markdown
## Onboarding Plan: [Name] — [Role]
**Start Date:** [Date] | **Team:** [Team] | **Manager:** [Manager]

### Pre-Start (Before Day 1)
- [ ] Send welcome email with start date, time, and logistics
- [ ] Set up accounts: email, Slack, [tools for role]
- [ ] Order equipment (laptop, monitor, peripherals)
- [ ] Add to team calendar and recurring meetings
- [ ] Assign onboarding buddy: [Suggested person]
- [ ] Prepare desk / remote setup instructions

### Day 1
| Time | Activity | With |
|------|----------|------|
| 9:00 | Welcome and orientation | Manager |
| 10:00 | IT setup and tool walkthrough | IT / Buddy |
| 11:00 | Team introductions | Team |
| 12:00 | Welcome lunch | Manager + Team |
| 1:30 | Company overview and values | Manager |
| 3:00 | Role expectations and 30/60/90 plan | Manager |
| 4:00 | Free time to explore tools and docs | Self |

### Week 1
- [ ] Complete required compliance training
- [ ] Read key documentation: [list for role]
- [ ] 1:1 with each team member
- [ ] Shadow key meetings
- [ ] First small task or project assigned
- [ ] End-of-week check-in with manager

### 30-Day Goals
1. [Goal aligned to role]
2. [Goal aligned to role]
3. [Goal aligned to role]

### 60-Day Goals
1. [Goal]
2. [Goal]

### 90-Day Goals
1. [Goal]
2. [Goal]

### Key Contacts
| Person | Role | For What |
|--------|------|----------|
| [Manager] | Manager | Day-to-day guidance |
| [Buddy] | Onboarding Buddy | Questions, culture, navigation |
| [IT Contact] | IT | Tool access, equipment |
| [HR Contact] | HR | Benefits, policies |

### Tools Access Needed
| Tool | Access Level | Requested |
|------|-------------|-----------|
| [Tool] | [Level] | [ ] |
```

## If Connectors Available

If **~~HRIS** is connected:
- Pull new hire details and team org chart
- Auto-populate tools access list based on role

If **~~knowledge base** is connected:
- Link to relevant onboarding docs, team wikis, and runbooks
- Pull the team's existing onboarding checklist to customize

If **~~calendar** is connected:
- Create Day 1 calendar events and Week 1 meeting invites automatically

## Tips

1. **Customize for the role** — An engineer's onboarding looks different from a designer's.
2. **Don't overload Day 1** — Focus on setup and relationships. Deep work starts Week 2.
3. **Assign a buddy** — Having a go-to person who isn't their manager makes a huge difference.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 anthropics/knowledge-work-plugins（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：anthropics/knowledge-work-plugins 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
