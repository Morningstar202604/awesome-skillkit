# 图像模型方言笔记 / Image Model Dialects (VERIFY BEFORE USE)

> ⚠️ **时效声明**：图像模型以**月度级**速度更新（型号/能力/定价都会变）。
> 本文件为 2026-09-14 网络调研快照，执行前按「核实方法」列重新确认
> （SKILL-STANDARD-v2 诫 7/诫 8）。来源分级：🟢 官方 · 🟡 第三方 · 🔵 社区。

## 跨模型硬规则（先查这条再写 prompt）

1. **文字渲染铁律**：图上需要可读文字（标题/标签/图表轴/OG 文案）→ 选
   GPT Image 系；Gemini 系图像模型基本不渲染可读文字。🟡🟢
2. **透明背景（图标/logo）**：需 RGBA alpha 的选原生透明支持的型号
   （如 GPT Image 1.5），并非所有图像模型都能出透明通道。🟡
3. **自然语言整句**优于关键词堆砌——所有现代图像模型通用。🟡
4. **文字逐字双引号包裹** + 编辑用 "change 'old' to 'new'" 句式 + 字符数
   剧变会破坏版式。🟡
5. **负向约束名词式**：`blurry, watermark` 而非 `no blur`。🟡

## 模型选型速查

| 需求 | 首选 | 理由 |
|------|------|------|
| 真实感场景/氛围图 | Gemini 3.x Flash Image 系 | 深度、环境复杂度好；不渲染文字 |
| 海报/信息图/带字 OG 图 | GPT Image 2 系 | 文字渲染可用（含多语种） |
| 批量风格探索（同构图多色） | GPT Image 2 系 | 单次调用原生多变体 |
| 透明图标/logo | GPT Image 1.5 | 原生 RGBA |
| 快速草稿迭代 | Flash 档 | 免费额度/低延迟 |
| 开源自托管 | SD 系/Flux 系 | 权限自由但文字渲染更弱，配后期排版 |

*核实方法：搜索各家「image model docs」最新版；模型 ID 随版本漂移，执行前
先查官方模型列表接口。*

## 摄影与构图词汇（跨模型通用）🔵

- **胶片/镜头**：Kodak Portra 800（人像肤色）、Fuji Velvia 50（高饱和风光）、
  50mm f/1.4（浅景深）、24mm 广角、tilt-shift（移轴微缩）
- **布光**：Rembrandt lighting（三角光）、soft diffused（软光棚拍）、
  rim/backlight（轮廓光）、volumetric（体积光雾感）
- **构图**：rule of thirds、centered symmetry、generous negative space、
  bird's-eye / low-angle hero shot
- **风格点名**：写不出风格名就描述特征——"visible brushstrokes, thick paint
  texture" 胜过 "painterly style"

## 通用兜底

方言不确定时：**五段结构 + 双引号包文字 + 名词式负向**，跳过模型专属参数。
写错专属标记比不写更糟。

## 审计与方言的关系

五段结构是跨模型不变量；模型选型与专属参数靠人工对照本文件核实。两层检查，
缺一不可。

## 变更维护

发现方言失效：更新对应条目 + 顶部快照日期，PR 走正常门禁。
