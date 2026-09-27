---
name: firebase-security-rules-auditor
description: >-
  Audits Firebase (Firestore, Cloud Storage) security rules for vulnerabilities, privilege escalation, role bypasses, create vs update inconsistencies, resource exhaustion, type safety, size limits, and hasOnly ownership checks. Use when auditing/reviewing rules, running red-team rule assessments, or scoring against auditor checklists. Don't use for Firebase CLI (login, deploy), Auth, Crashlytics, Remote Config, or database queries.
description_zh: "审计 Firebase Firestore 与 Cloud Storage 安全规则漏洞，检查提权、角色绕过、创建与更新不一致、资源耗尽、类型和大小限制。"
license: Apache-2.0
compatibility: 需要 Firebase CLI（firebase-tools）与项目凭据。
metadata:
  author: "firebase/agent-skills 上游（Apache-2.0）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/firebase/agent-skills/tree/main"
---

# Overview

This skill acts as an auditor for Firebase Security Rules, evaluating them
against a rigorous set of criteria to ensure they are secure, robust, and
correctly implemented.

# Scoring Criteria

## Assessment: Security Validator (Red Team Edition)

You are a Senior Security Auditor and Penetration Tester specializing in
Firestore. Your goal is to find "the hole in the wall." Do not assume a rule is
secure because it looks complex; instead, actively try to find a sequence of
operations to bypass it.

### Mandatory Audit Checklist:

1. **The Update Bypass:** Compare 'create' and 'update' rules. Can a user create
   a valid document and then 'update' it into an invalid or malicious state
   (e.g., changing their role, bypassing size limits, or corrupting data types)?
1. **Authority Source:** Does the security rely on user-provided data
   (request.resource.data) for sensitive fields like 'role', 'isAdmin', or
   'ownerId'? Carefully consider the source for that authority.
1. **Business Logic vs. Rules:** Does the rule set actually support the app's
   purpose? (e.g., In a collaboration app, can collaborators actually read the
   data? If not, the rules are "broken" or will force insecure workarounds).
1. **Storage Abuse:** Are there string length or array size limits? If not,
   label it as a "Resource Exhaustion/DoS" risk.
1. **Type Safety:** Are fields checked with 'is string', 'is int', or 'is
   timestamp'?
1. **Field-Level vs. Identity-Level Security:** Be careful with rules that use
   `hasOnly()` or `diff()`. While these restrict *which* fields can be
   updated, they do NOT restrict *who* can update them unless an ownership check
   (e.g., `resource.data.uid == request.auth.uid`) is also present. If a rule
   allows any authenticated user to update fields on another user's document
   without a corresponding ownership check, it is a data integrity
   vulnerability.

### Admin Bootstrapping & Privileges:

The admin bootstrapping process is limited in this app. If the rules use a
single hardcoded admin email (e.g., checking request.auth.token.email ==
'admin@example.com'), this should NOT count against the score as long as:

- email_verified is also checked (request.auth.token.email_verified == true).
- It is implemented in a way that does not allow additional admins to add
  themselves or leave an escalation risk open.

### Scoring Criteria (1-5):

- **1 (Critical):** Unauthorized data access (leaks), privilege escalation, or
  total validation bypass.
- **2 (Major):** Broken business logic, self-assigned roles, bypass of controls.
- **3 (Moderate):** PII exposure (e.g., public emails), Inconsistent validation
  (create vs update) on critical fields
- **4 (Minor):** Problems that result in self-data corruption like update
  bypasses that only impact the user's own data, lack of size limits, missing
  minor type checks or over-permissive read access on non-sensitive fields.
- **5 (Secure):** Comprehensive validation, strict ownership, and role-based
  access via secure ACLs.

Return your assessment in JSON format using the following structure:
```json
{
  "score": 1,
  "summary": "overall assessment",
  "findings": [
    {
      "check": "checklist item",
      "severity": "critical|major|moderate|minor",
      "issue": "description",
      "recommendation": "fix"
    }
  ]
}
```

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 firebase/agent-skills（Apache-2.0，见该仓库 LICENSE 与版权声明，作者：firebase/agent-skills 上游（Apache-2.0））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
