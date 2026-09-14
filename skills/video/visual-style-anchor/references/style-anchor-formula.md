# 风格锚五槽位展开公式 / Style Anchor Formula

> 风格锚是全片视觉 DNA：一页纸，五槽位，每次生成时 style 槽位整段引用。
> 本文给每个槽位更细的填法与示例。

## 槽位 1：色彩板 palette

三层结构：

```text
主色 ×1（占画面 ~60%）：环境基调
强调色 ×1（~10%）：只给焦点对象（主角、产品、按钮）
辅助色 ×1-2（~30%）：过渡与层次
```

- 每色必须给 HEX 值（`#0E1A2B`），「深蓝」不是规格是感觉
- 从参考图取色的方法：截图 → 取色器 → 记 3 个关键区域（天空/主体/阴影）的值
- 一致性规则：强调色出现次数越少越高级；全片 ≤3 主色，多平台分发时同锚不改色

## 槽位 2：光线 lighting

三个变量：

| 变量 | 选项 | 示例 |
|------|------|------|
| 光源类型 | natural / practical / studio | practical = 画内可见光源（霓虹、台灯、屏幕） |
| 时段 | dawn / noon / golden hour / blue hour / night | 时段决定色温基调 |
| 对比度 | high-contrast / soft / flat | 高对比=戏剧，软=温和，平=文档感 |

一句合成示例：`night exterior, practical neon signage as key light, high contrast with cyan-orange split`

## 槽位 3：材质 materials

- 列 3-5 个全片会反复出现的表面：`湿面反光沥青 / 磨砂塑料 / 玻璃橱窗`
- 禁止清单同样重要：写明「禁止出现的质感」（如纯平色块、低饱和哑光）——
  生成模型的默认质感往往不是你想要的，负向约束比正向描述更能锁住画面

## 槽位 4：时代 era

- 明确年代与「年代标记物」：出现的物件的年代必须 ≤ 故事年代
- 正向写法：`现代都市 2020s`；负向写法：`全片禁: CRT 电视、胶片颗粒、翻盖手机`
- 年代标记物是跑片高发区——观众对年代穿帮零容忍

## 槽位 5：媒介质感 medium

按项目类型三选一并整段复用：

| 类型 | 媒介短语 |
|------|----------|
| 剧情/电影感 | `cinematic live-action, 35mm depth-of-field feel, subtle handheld breathing` |
| 产品/商业 | `product-commercial gloss, clean studio backdrop, crisp reflections` |
| 动画/风格化 | `anime cel style, flat shading with rim light` |

## 完整示例（雨夜便利店短片）

```markdown
# Style Anchor: 雨夜便利店
## 色彩板
主色 #0E1A2B / 强调 #FF6B35 / 辅助 #7FD1C9（青）
规则：强调色只给剧情道具与主角高光。
## 光线
夜外景，practical neon 主光，青橙对比，高光允许溢出。
## 材质
湿面反光沥青、磨砂塑料、玻璃橱窗。禁止: 纯平色块、低饱和哑光。
## 时代
2020s 都市。全片禁: CRT 电视、胶片颗粒。
## 媒介
cinematic live-action, 35mm depth-of-field feel, 轻微手持呼吸感。
```

## 验收

- 五槽位齐 + 色彩有 HEX + 材质有禁止清单 + 媒介三选一
- ≤60 行：超过说明在写 prompt 而不是锚——细内容归 prompt 层
