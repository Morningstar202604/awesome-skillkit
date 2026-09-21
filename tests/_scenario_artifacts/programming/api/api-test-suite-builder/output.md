# POST /orders 测试套件设计

## 用例总表

### A. 正常路径（Happy Path）

| ID | 场景 | 前置条件 | 输入 | 预期结果 |
|----|------|----------|------|----------|
| ORD-N01 | 创建订单：SKU 存在、qty 正数、无优惠券 | 库存充足 | `sku: "SKU001", qty: 2` | 201，返回 order 对象；inventory 减 2 |
| ORD-N02 | 创建订单：SKU 存在、qty=1、有有效优惠券 | 优惠券未过期、满足门槛 | `sku: "SKU002", qty: 1, coupon: "SAVE10"` | 201，price 已应用折扣，inventory 减 1 |
| ORD-N03 | 创建订单：多 SKU 分别下单（串行） | 库存充足 | 多次 `sku: "SKU001", qty: 1` | 每次 201，inventory 逐次递减 |
| ORD-N04 | 幂等创建：相同 idempotency-key 重试 | 订单已创建 | `idempotency-key: "idem-abc", sku: "SKU001", qty: 2` | 201，返回原订单，inventory 不重复扣减 |
| ORD-N05 | 幂等创建：不同 key → 不同订单 | 库存充足 | 两次不同 key，相同 payload | 201 × 2，inventory 减 4 |

---

### B. 边界值（Boundary）

| ID | 场景 | 输入 | 预期结果 |
|----|------|------|----------|
| ORD-B01 | qty = 最小允许值（min=1） | `qty: 1` | 201 |
| ORD-B02 | qty = max_allowed（假设 9999） | `qty: 9999` | 201 或 400（若超库存） |
| ORD-B03 | qty = min - 1 = 0 | `qty: 0` | 400，提示 qty ≥ 1 |
| ORD-B04 | qty = max + 1 = 10000 | `qty: 10000` | 400 或 422，超出允许范围 |
| ORD-B05 | sku 为空字符串 | `sku: ""` | 400/422，字段校验失败 |
| ORD-B06 | sku 超长（超过 DB 限制，假设 64 字符） | `sku: "a".repeat(65)` | 400/422 |
| ORD-B07 | coupon 为空字符串 | `coupon: ""` | 400/422 或忽略（按契约） |
| ORD-B08 | coupon 为 null | `coupon: null` | 等同无优惠券，201 |
| ORD-B09 | coupon 字段缺失 | `{sku: "SKU001", qty: 1}` | 等同无优惠券，201 |
| ORD-B10 | qty 为浮点数 1.5 | `qty: 1.5` | 400/422（qty 应为整数） |
| ORD-B11 | 库存恰好等于 qty | `qty: <current_stock>` | 201，库存归零 |
| ORD-B12 | 库存不足（qty = stock + 1） | `qty: <stock+1>` | 409 或 422，库存不足 |

---

### C. 异常路径（Error Cases）

| ID | 场景 | 输入 | 预期结果 |
|----|------|------|----------|
| ORD-E01 | SKU 不存在 | `sku: "NONEXIST"` | 404 或 422 |
| ORD-E02 | 缺少 sku 字段 | `{qty: 1}` | 400/422，缺失必填字段 |
| ORD-E03 | 缺少 qty 字段 | `{sku: "SKU001"}` | 400/422 |
| ORD-E04 | SKU 格式非法（含特殊字符） | `sku: "SKU/001"` | 400/422 |
| ORD-E05 | 优惠券无效（错误 code） | `coupon: "BADCODE"` | 400/422，优惠券不存在 |
| ORD-E06 | 优惠券已过期 | `coupon: "<expired>"` | 400/422 |
| ORD-E07 | 优惠券门槛未满足（min_spend 未达） | `coupon: "MINSPEND50", qty: 1, sku: "cheap_item"` | 400/422 |
| ORD-E08 | 用户无权限购买该 SKU（如受限品类） | `sku: "RESTRICTED"` | 403 |
| ORD-E09 | 请求体非 JSON（Content-Type 错误） | Body: `sku=SKU001&qty=2` | 415 |
| ORD-E10 | 请求体为空 | Body: `` | 400 |
| ORD-E11 | 缺少 Authorization 头 | 无 token | 401 |
| ORD-E12 | Token 已过期 | Expired JWT | 401 |
| ORD-E13 | Token 有效但角色不足 | 普通用户 token，需 admin | 403 |

---

### D. 幂等性（Idempotency）

| ID | 场景 | 步骤 | 预期结果 |
|----|------|------|----------|
| ORD-I01 | 相同 key 首次创建 | 发送 idem-key=K，payload P | 201，创建订单 O1 |
| ORD-I02 | 相同 key 二次创建（重复提交） | 再次发送 idem-key=K，payload P | 201，返回 O1（同一对象），inventory 不变 |
| ORD-I03 | 相同 key，payload 不同 | 先 K+P1 → 再 K+P2 | 409 或 422，拒绝不一致请求 |
| ORD-I04 | 不同 key，相同 payload | K1+P, K2+P | 201 × 2，两笔订单，inventory 扣两次 |
| ORD-I05 | key 有效期过后重试 | 等待 key 过期（如 24h），再发 K+P | 201，新建订单（key 已清理） |

---

### E. 并发（Concurrency）

| ID | 场景 | 步骤 | 预期结果 |
|----|------|------|----------|
| ORD-C01 | 同一 SKU，两请求同时下单（库存充足） | 并发 2 次 `qty: 1`，