---
name: campaign-designer
description: "Design an e-commerce/growth campaign around finished product copy: marketing-calendar placement (festival nodes vs everyday), channel matrix with roles per channel, and single-variable A/B variant pairs (one change per pair, hypothesis stated). Reads copy from product-copywriter, hands variant matrix to channel-adapter. Use when the user asks to 排活动 / 营销日历 / 投放计划 / A/B 测试 / campaign / 渠道矩阵. Do NOT use for writing the base copy itself (product-copywriter), nor for per-platform reformatting (channel-adapter)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: marketing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# 活动设计师

把文案升级成**有节奏的战役**。核心纪律是**单变量 A/B**——一次改两个变量，赢了也不知道为什么赢，数据就白跑了。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 基础文案 | ✓ | product-copywriter 的产出 |
| 战役目标 | ✓（缺就问） | 冲销量 / 打认知 / 清库存——目标决定节奏与渠道权重 |
| 预算档位 | ✗ | 影响渠道矩阵宽度，不猜 |

缺输入时一次性问齐："请提供：① 基础文案（或说明由 product-copywriter 先产出）② 战役目标（冲销量/打认知/清库存）③ 档期与预算档位（可选）。"

## 前置自检

本技能纯 prompt 驱动：无运行时依赖、无端点、无环境变量。自检点：

```bash
test -f ../product-copywriter/references/sources-and-methodology.md && echo OK
```

预期输出 `OK`（共享方法论文献在位）；失败不阻塞——框架纪律在本文件内自足，交付时注明文献缺失。

## 工作流

### 步骤 1：定节奏（节点 vs 日常）

- **节点型**（618/双 11/开学季）：预热（种草）→ 爆发（转化）→ 返场（长尾）三段，每段渠道配比不同
- **日常型**：周更节奏，1 主推渠道 + 2 辅助渠道轮换，避免全平台同时开火分散弹药
- 输出营销日历表：日期 | 节点 | 主渠道 | 动作 | 素材需求

### 步骤 2：排渠道矩阵（一渠道一角色）

| 渠道类型 | 角色 | 内容形态 |
|----------|------|----------|
| 种草（小红书/抖音） | 拉新认知 | 场景化内容，弱销售感 |
| 搜索（电商站内/搜索引擎） | 承接意图 | 强卖点+比价信息 |
| 私域（社群/朋友圈/邮件） | 复购与转介绍 | 人格化沟通 + 专属权益 |

纪律：**渠道各司其职**，同一素材全渠道直发 = 三个渠道一起平庸（适配交给 channel-adapter）。

### 步骤 3：设计 A/B 变体对（单变量纪律）

每对变体只允许一个差异维度，并写明假设：

```markdown
- 对 1【标题钩子】假设：数字钩 > 悬念钩
  A: "3 天卖了 2000 件的真相" / B: "为什么大家都在抢这个"
- 对 2【CTA 措辞】假设：损失厌恶 > 行动指令
  A: "别错过今晚 8 点的价" / B: "点击锁定优惠"
```

- 一次测试 ≤2 对变体——对数越多，单对流量越薄，结论越不可信
- 测完的赢家写回基础文案，下一轮基于新基线迭代

### 步骤 4：链条移交

交付营销日历 + 渠道矩阵 + 变体对清单。**接着说："战役排好了，调用 channel-adapter 把基础文案出成各渠道变体"**——链条自动展开。
- 预期：channel-adapter 拿到的矩阵每渠道有角色、变体对每对只有一个差异维度。
- 若失败：数据回流显示某渠道表现差 → 带数据回步骤 2 调整矩阵角色与权重，不推翻整体节奏。

## 交付标准

- 产物：营销日历表（日期|节点|主渠道|动作|素材需求）+ 渠道矩阵（每渠道一角色）+ A/B 变体对清单（每对带假设）。
- 保存位置：直接输出在对话中（本技能不写文件），供 channel-adapter 引用。
- 完整性验证：每对变体可逐字指出唯一差异维度；≤2 对同时测试；节点型战役预热段排期 ≥7 天。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| A/B 测了个寂寞 | 一对变体改了多处 | 对照单变量纪律重切变体 |
| 全渠道同素材 | 缺渠道角色分工 | 回步骤 2 给每渠道定角色 |
| 预热没量就开卖 | 节奏压缩 | 节点型预热至少提前 7 天 |
| 数据结论互相矛盾 | 多对变体同时跑且互污染 | 隔离测试期或按渠道分桶 |

## 参考

框架与变体纪律出处记录在 product-copywriter 的
[sources-and-methodology.md](../product-copywriter/references/sources-and-methodology.md)（同包共享）。
