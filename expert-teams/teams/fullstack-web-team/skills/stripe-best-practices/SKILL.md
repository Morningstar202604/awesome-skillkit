---
name: stripe-best-practices
description: Stripe 支付、订阅与 Connect 集成最佳实践。当需要接入 Checkout、客户门户、订阅生命周期、Webhook 签名与幂等、Connect 分账、处理退款/争议、落实 PCI 合规时，由 fullstack-backend-engineer 与 fullstack-api-designer 加载执行。
license: MIT
compatibility: universal
---

# Stripe 集成最佳实践

本 skill 面向 fullstack-backend-engineer / fullstack-api-designer，覆盖收款、订阅、Connect 的服务端正确接法。

## 何时使用
- 新建付费/订阅/分账业务；
- 已有 Stripe 集成漏签 webhook、幂等缺失、订阅状态机不完整；
- 处理退款、争议、对账、PCI 合规审查。

## 核心原则
1. **服务端为唯一事实源**：价格、订阅状态、 entitlement 全部以 Stripe webhook 回写的数据库为准，前端不可信。
2. **Webhook 必验签**：用 Stripe 库验 `Stripe-Signature`，拒绝任何未验签请求。
3. **幂等处理**：webhook 与退款/创建付款都用幂等键，重复事件不重复入账。
4. **不在前端算钱**：价格在 Stripe Price/Product 上配置，前端只传 priceId。
5. **PCI 最小化**：用 Stripe Checkout / Elements，不自己碰卡号。

## Checkout 流程
1. 服务端 `stripe.checkout.sessions.create({ mode: 'subscription'|'payment', line_items:[{price: priceId, quantity:1}], success_url, cancel_url, customer: existingCustomerId })`。
2. 前端跳转到 `session.url`，不自己收集卡号。
3. 支付完成后 Stripe 触发 `checkout.session.completed` webhook，服务端据此开通 entitlement。

## Webhook 验签与幂等
```ts
const sig = req.headers['stripe-signature']
const event = stripe.webhooks.constructEvent(
  req.body, sig, process.env.STRIPE_WEBHOOK_SECRET
)
// 按 event.id 去重，已处理过直接 200
switch (event.type) {
  case 'checkout.session.completed': /* 开通 */ break
  case 'customer.subscription.updated': /* 更新状态 */ break
  case 'customer.subscription.deleted': /* 回收权限 */ break
  case 'invoice.paid': /* 记录续费 */ break
  case 'invoice.payment_failed': /* 通知重试 */ break
}
```

## 订阅生命周期必须处理的事件
- `checkout.session.completed`：首次开通。
- `customer.subscription.updated`：升降级、宽限期、取消日期变更。
- `customer.subscription.deleted`：正式取消，回收权限。
- `invoice.paid`：每次续费成功。
- `invoice.payment_failed`：重试/宽限，提醒用户更新支付方式。
- 客户自助管理走 **Billing Portal**（`stripe.billingPortal.sessions.create`），不自己造取消/改套餐 UI。

## Connect 分账
- 平台向卖家收款后用 `Transfer` / `Destination charge` 打款给 Connect 账户。
- 平台抽成在应用层记录，资金留存与结算周期（Payout）按 Connect 类型（Standard/Express/Custom）配置。
- 卖家尽调、KYC、退款责任按 Connect 文档落表。

## 清单（交付前逐项过）
- [ ] 价格配置在 Stripe Product/Price，前端只传 priceId，不前端算金额。
- [ ] webhook 端点已验签，原始 body 传入（不是 json 解析后的对象）。
- [ ] webhook 按 `event.id` 幂等去重，重放安全。
- [ ] 订阅关键事件全部处理，取消/欠费能正确回收 entitlement。
- [ ] 客户改套餐/取消走 Billing Portal，不自建敏感操作 UI。
- [ ] 密钥分环境（test/live），`sk_live_*` 不进前端、不进 Git。
- [ ] 退款/争议（dispute）有监控与申诉入口。
- [ ] 对账：本地订单与 Stripe 发票可核对。
- [ ] 不直接处理卡号，符合 PCI SAQ A。

## 易错点
- **webhook 没验签**：任何人 POST 一个假的 `checkout.session.completed` 就白嫖会员，必须验签。
- **用 `req.body`（已解析 JSON）验签**：签名基于原始字节，必须用 raw body。
- **把 entitlement 建立在前端回调**：用户直接调"开通"接口就能绕过付款，必须以 webhook 为准。
- **漏处理 `invoice.payment_failed`**：续费失败却继续给权益，持续坏账；要通知+宽限后回收。
- **在前端存/传 secret key**：`sk_*` 泄露等于把商户钱包公开，前端只能用 publishable key。
- **幂等键没设**：网络重试导致重复扣款/重复发券，写操作一律带 Idempotency-Key。
- **测试用 live 模式或反之**：环境串了，真实扣款或测单进生产，严格分环境配 key 与 webhook。
