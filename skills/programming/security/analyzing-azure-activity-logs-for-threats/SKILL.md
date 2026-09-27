---
name: analyzing-azure-activity-logs-for-threats
description: >-
  'Queries Azure Monitor activity logs and sign-in logs via
  azure-monitor-query
description_zh: "查询 Azure Monitor 活动与登录日志，发现可疑管理操作、异地登录与提权行为。"
license: Apache-2.0
compatibility: 纯提示型；配套命令面向真实安全工具链（Volatility/Splunk/Wireshark/云 CLI 等），请在获得授权的环境使用。
metadata:
  author: "mukul975/Anthropic-Cybersecurity-Skills 上游（Apache-2.0，社区项目）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mukul975/Anthropic-Cybersecurity-Skills/tree/main/skills/analyzing-azure-activity-logs-for-threats"
---

# Analyzing Azure Activity Logs for Threats


## When to Use

- When investigating security incidents that require analyzing azure activity logs for threats
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Familiarity with security operations concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

Use azure-monitor-query to execute KQL queries against Azure Log Analytics workspaces,
detecting suspicious admin operations and sign-in anomalies.

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

response = client.query_workspace(
    workspace_id="WORKSPACE_ID",
    query="AzureActivity | where OperationNameValue has 'MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE' | take 10",
    timespan=timedelta(hours=24),
)
```

Key detection queries:
1. Role assignment changes (privilege escalation)
2. Resource group and subscription modifications
3. Key vault secret access from new IPs
4. Network security group rule changes
5. Conditional access policy modifications

## Examples

```python
# Detect new Global Admin role assignments
query = '''
AuditLogs
| where OperationName == "Add member to role"
| where TargetResources[0].modifiedProperties[0].newValue has "Global Administrator"
'''
```

---

## 来源与署名 / Source & Attribution

本技能收录自 [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/tree/main/skills/analyzing-azure-activity-logs-for-threats)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
