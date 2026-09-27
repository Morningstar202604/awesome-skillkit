---
name: auth-implementation-patterns
description: >-
  Master authentication and authorization patterns including JWT, OAuth2, session management, and RBAC to build secure, scalable access control systems. Use when implementing auth systems, securing APIs, or debugging security issues.
description_zh: "掌握鉴权与授权模式：JWT、OAuth2、会话管理与 RBAC 权限控制。"
license: MIT
compatibility: 纯提示型，任意支持 SKILL.md 的工具可用；无外部依赖。
metadata:
  author: "wshobson/agents 上游（MIT）"
  version: "1.0.0"
  category: programming
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-27"
  source: "https://github.com/wshobson/agents/tree/main"
---

# Authentication & Authorization Implementation Patterns

Build secure, scalable authentication and authorization systems using industry-standard patterns and modern best practices.

## When to Use This Skill

- Implementing user authentication systems
- Securing REST or GraphQL APIs
- Adding OAuth2/social login
- Implementing role-based access control (RBAC)
- Designing session management
- Migrating authentication systems
- Debugging auth issues
- Implementing SSO or multi-tenancy

## Core Concepts

### 1. Authentication vs Authorization

**Authentication (AuthN)**: Who are you?

- Verifying identity (username/password, OAuth, biometrics)
- Issuing credentials (sessions, tokens)
- Managing login/logout

**Authorization (AuthZ)**: What can you do?

- Permission checking
- Role-based access control (RBAC)
- Resource ownership validation
- Policy enforcement

### 2. Authentication Strategies

**Session-Based:**

- Server stores session state
- Session ID in cookie
- Traditional, simple, stateful

**Token-Based (JWT):**

- Stateless, self-contained
- Scales horizontally
- Can store claims

**OAuth2/OpenID Connect:**

- Delegate authentication
- Social login (Google, GitHub)
- Enterprise SSO

## Detailed patterns and worked examples

Detailed pattern documentation lives in `references/details.md`. Read that file when the navigation tier above is insufficient.

## Best Practices

1. **Never Store Plain Passwords**: Always hash with bcrypt/argon2
2. **Use HTTPS**: Encrypt data in transit
3. **Short-Lived Access Tokens**: 15-30 minutes max
4. **Secure Cookies**: httpOnly, secure, sameSite flags
5. **Validate All Input**: Email format, password strength
6. **Rate Limit Auth Endpoints**: Prevent brute force attacks
7. **Implement CSRF Protection**: For session-based auth
8. **Rotate Secrets Regularly**: JWT secrets, session secrets
9. **Log Security Events**: Login attempts, failed auth
10. **Use MFA When Possible**: Extra security layer

## Common Pitfalls

- **Weak Passwords**: Enforce strong password policies
- **JWT in localStorage**: Vulnerable to XSS, use httpOnly cookies
- **No Token Expiration**: Tokens should expire
- **Client-Side Auth Checks Only**: Always validate server-side
- **Insecure Password Reset**: Use secure tokens with expiration
- **No Rate Limiting**: Vulnerable to brute force
- **Trusting Client Data**: Always validate on server

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 wshobson/agents（MIT，见该仓库 LICENSE 与版权声明，作者：wshobson/agents 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
