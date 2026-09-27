---
name: analyzing-kubernetes-audit-logs
description: >-
  Parses Kubernetes API server audit logs (JSON lines) to detect
  exec-into-pod, secret access, RBAC modifications, privileged pod creation,
  and anonymous API access, and builds SIEM detection rules from the event
  patterns. Use when investigating a suspected cluster compromise,
  reconstructing what an attacker did through the API server, or writing
  Kubernetes-specific detection content. Keywords: audit policy, audit log,
  kube-apiserver, exec into pod, RBAC change, anonymous access, detection
  rules. Do not use for syscall-level detection inside a running container -
  use detecting-container-runtime-threats-with-falco. '
description_zh: "解析 Kubernetes API 审计日志：发现 exec 进容器、密钥读取、RBAC 变更与特权 Pod 等威胁。"
license: Apache-2.0
compatibility: 纯提示型；配套命令面向真实安全工具链（Volatility/Splunk/Wireshark/云 CLI 等），请在获得授权的环境使用。
metadata:
  author: "mukul975/Anthropic-Cybersecurity-Skills 上游（Apache-2.0，社区项目）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mukul975/Anthropic-Cybersecurity-Skills/tree/main/skills/analyzing-kubernetes-audit-logs"
---

# Analyzing Kubernetes Audit Logs


## When to Use

- When investigating security incidents that require analyzing kubernetes audit logs
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Familiarity with container security concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

Parse Kubernetes audit log files (JSON lines format) to detect security-relevant
events including unauthorized access, privilege escalation, and data exfiltration.

```python
import json

with open("/var/log/kubernetes/audit.log") as f:
    for line in f:
        event = json.loads(line)
        verb = event.get("verb")
        resource = event.get("objectRef", {}).get("resource")
        user = event.get("user", {}).get("username")
        if verb == "create" and resource == "pods/exec":
            print(f"Pod exec by {user}")
```

Key events to detect:
1. pods/exec and pods/attach (shell into containers)
2. secrets access (get/list/watch)
3. clusterrolebindings creation (RBAC escalation)
4. Privileged pod creation
5. Anonymous or system:unauthenticated access

## Examples

```python
# Detect secret enumeration
if verb in ("get", "list") and resource == "secrets":
    print(f"Secret access: {user} -> {event['objectRef'].get('name')}")
```

---

## 来源与署名 / Source & Attribution

本技能收录自 [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/tree/main/skills/analyzing-kubernetes-audit-logs)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
