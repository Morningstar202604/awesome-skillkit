---
name: github-actions-advanced
description: GitHub Actions 高级 Workflow 工程化指南。当需要编写/优化 CI/CD、配置 OIDC 云认证、复用 reusable workflow、矩阵构建、依赖缓存、密钥与环境保护、Runner 安全加固时，由 fullstack-ci-cd-engineer 加载执行。
license: MIT
compatibility: universal
---

# GitHub Actions 高级实践

本 skill 面向 fullstack-ci-cd-engineer，产出**安全、快、可复用**的流水线。

## 何时使用
- 新建 CI（lint/test/build）或 CD（部署到 K8s/云）；
- 现有 workflow 慢、密钥硬编码、权限过宽；
- 需要 OIDC 免长期密钥、跨仓库复用 workflow、矩阵多版本测试。

## 核心原则
1. **最小权限**：`permissions` 默认设为 `read-all`，按需提升；不用 `write-all`。
2. **OIDC 替代长期密钥**：用云厂商 OIDC role，不在 repo 存 AK/SK。
3. **Pin action 到 SHA**：第三方 action 固定 commit SHA，不用 `@main`。
4. **缓存依赖**：pnpm/npm/pip/docker layer 都缓存，缩短流水线。
5. **环境保护**：生产部署走 environment + 审批人。

## OIDC 部署到云（示例：AWS）
```yaml
permissions:
  id-token: write   # 换取 OIDC token
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ap-northeast-1
      - run: terraform apply -auto-approve
```

## 缓存与矩阵
```yaml
strategy:
  fail-fast: false
  matrix:
    node: [20, 22]
steps:
  - uses: actions/setup-node@v4
    with: { node-version: "${{ matrix.node }}", cache: 'pnpm' }
  - run: pnpm ci
  - run: pnpm test
```

## Reusable Workflow
- 公共逻辑抽 `.github/workflows/reusable-*.yml`，`workflow_call:` 声明 inputs/secrets。
- 业务 workflow 用 `uses: org/.github/.github/workflows/reusable-test.yml@<sha>` 调用。
- 复用后只在一处改 lint/test 规则，避免每个仓库复制粘贴。

## 清单（交付前逐项过）
- [ ] 每个 job 显式声明 `permissions`，未用到的不授予。
- [ ] 云认证走 OIDC，仓库/环境 secrets 无长期 AK/SK。
- [ ] 第三方 action 全部 pin 到 SHA（`{sha}-#vX.Y.Z`）。
- [ ] 依赖缓存命中（actions/setup-node cache、actions/cache）。
- [ ] 生产部署绑定 environment + 必需审批人。
- [ ] 敏感输出不打日志（`echo::add-mask::` 或 secrets 自动掩码）。
- [ ] 矩阵 `fail-fast: false`，单版本失败不中断全部。
- [ ] workflow_dispatch 手动触发的参数有默认值与校验。
- [ ] 超时 `timeout-minutes` 已设，防挂死 Runner。

## 易错点
- **`permissions: write-all` 全局开**：任意 PR 都能写仓库，被投毒后可直接改代码投供应链；按 job 收紧。
- ** Pull request 事件跑部署**：外部 PR 能触发生产部署，部署 job 必须限定 `main` tag + environment 审批。
- **action 用 `@main`**：上游仓库被劫持即供应链攻击，必须 pin SHA。
- **缓存 key 不锁 lockfile**：`pnpm-lock.yaml` 变了却命中旧缓存，导致测试与本地不一致；key 里拼 lockfile hash。
- **secrets 传到第三方 action**：`secrets: inherit` 会把所有密钥外传，只传必需的。
- **忘记 `timeout-minutes`**：卡死的 job 一直占 Runner、烧配额。
- **`pull_request` vs `push` 分支保护混乱**：tag 构建漏跑，发布流水线和 CI 分开写清楚触发条件。
