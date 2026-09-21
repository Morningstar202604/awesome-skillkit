# POST /orders 测试套件设计

## 路由信息

- **Endpoint**: `POST /orders`
- **Content-Type**: `application/json`
- **请求体**: `{ sku: string, qty: number, coupon?: string }`
- **业务假设**（需确认）:
  - SKU 必须存在于商品库
  - qty > 0 且不超过库存上限
  - coupon 可选，若提供则校验优惠码有效性
  - 响应: 201 Created + `{ orderId, total, items: [{ sku, qty, unitPrice }] }`
  - 幂等键（Idempotency-Key）通过请求头 `Idempotency-Key: uuid` 传递

---

## 一、正常场景用例

| # | 测试用例 | 前置条件 | 输入 | 预期结果 | 分类 |
|---|---------|---------|------|---------|------|
| 1 | 下单成功（无优惠） | SKU-A 存在，库存充足 | `{ sku: "SKU-A", qty: 1 }` | 201，orderId 非空，total = unitPrice × 1 | 正常 |
| 2 | 下单成功（含有效优惠码） | SKU-A 存在，coupon-10 有效 | `{ sku: "SKU-A", qty: 2, coupon: "coupon-10" }` | 201，total = unitPrice × 2 × 0.9，优惠券已消耗 | 正常 |
| 3 | 批量下单（qty > 1） | SKU-B 库存 ≥ 5 | `{ sku: "SKU-B", qty: 5 }` | 201，items.qty = 5，库存扣减正确 | 正常 |
| 4 | 多次下单同一 SKU | 无并发 | `{ sku: "SKU-A", qty: 1 }`（重复 3 次）| 3 次均 201，分别返回不同 orderId | 正常 |

---

## 二、边界用例

| # | 测试用例 | 前置条件 | 输入 | 预期结果 | 分类 |
|---|---------|---------|------|---------|------|
| 5 | qty 最小值（1） | SKU-A 库存 ≥ 1 | `{ sku: "SKU-A", qty: 1 }` | 201，成功 | 边界 |
| 6 | qty = 0 | 任意 SKU | `{ sku: "SKU-A", qty: 0 }` | 400/422，提示 qty 必须 > 0 | 边界 |
| 7 | qty = -1 | 任意 SKU | `{ sku: "SKU-A", qty: -1 }` | 400/422，提示 qty 必须 > 0 | 边界 |
| 8 | qty 达到库存上限 | SKU-C 库存 = 10 | `{ sku: "SKU-C", qty: 10 }` | 201，库存归零 | 边界 |
| 9 | qty 超出库存上限 | SKU-C 库存 = 10 | `{ sku: "SKU-C", qty: 11 }` | 400/422，提示库存不足 | 边界 |
| 10 | coupon 为空字符串 | SKU-A 存在 | `{ sku: "SKU-A", qty: 1, coupon: "" }` | 400/422，coupon 格式无效或忽略 | 边界 |
| 11 | 超长 SKU（边界长度） | 假设 SKU 最大长度 64 | `{ sku: "<64字符>", qty: 1 }` | 201 或 400（取决于是否超限） | 边界 |
| 12 | sku 超出最大长度 | 假设 SKU 最大长度 64 | `{ sku: "<65字符>", qty: 1 }` | 400/422，提示 SKU 格式错误 | 边界 |

---

## 三、异常用例

| # | 测试用例 | 前置条件 | 输入 | 预期结果 | 分类 |
|---|---------|---------|------|---------|------|
| 13 | SKU 不存在 | 无 | `{ sku: "INVALID-SKU", qty: 1 }` | 404，提示 SKU 不存在 | 异常 |
| 14 | 请求体为空 | 无 | `{}` | 400/422，提示缺少 sku/qty | 异常 |
| 15 | sku 缺失 | 无 | `{ qty: 1 }` | 400/422，提示缺少 sku | 异常 |
| 16 | qty 缺失 | 无 | `{ sku: "SKU-A" }` | 400/422，提示缺少 qty | 异常 |
| 17 | sku 为 null | 无 | `{ sku: null, qty: 1 }` | 400/422，提示 sku 类型错误 | 异常 |
| 18 | qty 为 string | 无 | `{ sku: "SKU-A", qty: "two" }` | 400/422，提示 qty 类型错误 | 异常 |
| 19 | qty 为浮点数 | 无 | `{ sku: "SKU-A", qty: 1.5 }` | 400/422，提示 qty 必须为整数 | 异常 |
| 20 | coupon 无效 | SKU-A 存在 | `{ sku: "SKU-A", qty: 1, coupon: "BAD-COUPON" }` | 400/422，提示优惠券无效 | 异常 |
| 21 | coupon 已过期 | SKU-A 存在 | `{ sku: "SKU-A", qty: 1, coupon: "EXPIRED-COUPON" }` | 400/422，提示优惠券已过期 | 异常 |
| 22 | 并发扣减超库存（见并发用例） | 库存 = 1 | 两请求同时 `{ sku: "SKU-X", qty: 1 }` | 一个 201，另一个 400/409 库存不足 | 并发 |
| 23 | SQL 注入 payload | 无 | `{ sku: "'; DROP TABLE orders; --", qty: 1 }` | 400/200（已净化），不崩溃 | 安全 |
| 24 | XSS payload | 无 | `{ sku: "<script>alert(1)</script>", qty: 1 }` | 201 或 400（已净化），响应中不含未转义 HTML | 安全 |

---

## 四、幂等用例

| # | 测试用例 | 前置条件 | 输入 | 预期结果 | 分类 |
|---|---------|---------|------|---------|------|
| 25 | 相同 Idempotency-Key 重复提交 | 无 | 请求头 `Idempotency-Key: idem-001`，body