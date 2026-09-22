---
name: layout-spec-auditor
description: "Audit a generated image (or its plan) against a design spec and platform layout rules: aspect ratio match, minimum resolution, safe-area margins for text, platform file-size limits, and text-budget compliance. Reads the actual image file with Pillow when available, or audits declared dimensions. Use when the user asks to 检查图片规格 / 尺寸对不对 / 审图 / layout audit / 封面规格 / 图片合规, or automatically after generating an image in the visual-design-studio chain. Do NOT use for judging aesthetics (that is design critique), nor for writing prompts."
license: Apache-2.0
compatibility: Python 3.8+; Pillow optional (needed only when auditing an actual image file).
metadata:
  author: "awesome-skillkit"
  version: "1.1"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Layout Spec Auditor

链条守门员。生成完的图在交付前过三道闸：**比例对不对、分辨率够不够、文字安不安全**。规格阶段说好的画布，交付时偏差 1% 都是返工。

## 领域暗知识（审计前必须懂的四件事）

**1. 安全区数字来自平台 UI 的实测位置，不是经验玄学。** 本技能的"四边 8% / 底部 15%"对应的实测事实：抖音与 B 站封面**左下角叠时长标签**，竖版平台底部有进度条与交互按钮，小红书/抖音信息流卡片有圆角裁切——文字或主体落进这些区域就是被 UI 盖住，而不是"被裁掉一点"。不同平台的浮层位置不同，所以按平台查表，不套通用值。

**2. 对比度不是审美问题，是合规问题。** WCAG 2.x 的量化底线：正文文字与背景 **4.5:1**（AA），大字与 UI 组件 **3:1**，AAA 级 7:1。这不是编辑部的偏好——WebAIM 对百万级首页的年度扫描连续多年显示，**对比度不足稳居网页第一大可达性违规（近年扫描中约八成首页中招）**。烧在图上的文字同理：图上标题与背景的对比度低于 4.5:1，在强光屏幕/缩略尺寸下就是不可读，审计时按"合规失败"记，不按"风格建议"记。

**3. 色觉冗余：约 8% 的男性有色觉缺陷。** 色盲不罕见（美国国家眼科研究所等流行病学统计口径：男性约 8%、女性约 0.5%），红绿对比是最常见的失效组合。图上若有仅靠颜色区分的信息（状态、分类、前后对比），审计加一条：灰度化后信息是否仍可分辨（把截图去色看一眼，成本 10 秒）。只靠红/绿编码的"通过/失败"标记记为 fail。

**4. 眯眼测试是结构检查，不是美学评判。** 本技能不评判美学（那是 design critique 的职责），但"第一眼落点是否是主体"是**结构性**问题：把图缩到拇指大小（或眯眼模糊看），视线第一落点如果不是规格单 subject 指定的主体，说明层级失败——这直接对应 Gestalt 对比原则与设计界通用的 squint test，是可判定的，因此属于规格审计范围。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 图片文件 | 二选一 | 实际产出图（有 Pillow 时读真实尺寸） |
| 声明尺寸 | 二选一 | 只有计划时的 W×H（纯审计计算） |
| 设计规格单 | ✓ | design-brief-interpreter 的产出，platform 字段为准 |

缺输入时一次性问齐："请提供：① 实际图片文件路径（有图时）或声明 W×H（仅计划阶段）② 目标平台名（决定验收规格）。"

## 前置自检

```bash
test -f scripts/spec_audit.py && echo SCRIPT-OK
python3 -c "import PIL" 2>/dev/null && echo PIL-OK || echo PIL-MISSING
```

- 预期：`SCRIPT-OK` 必须出现；失败说明技能包不完整，STOP 并提示重装技能包。
- `PIL-OK` 仅在审计真实图片文件（`--image`）时必需；输出 `PIL-MISSING` 时修复二选一：`pip install pillow`，或改走声明尺寸模式（`--width/--height` 纯计算，不读图）。本机实测 `spec_audit.py` 无 `--image` 时不 import PIL，声明尺寸模式确实不依赖 Pillow。

## 工作流

### 步骤 1：跑规格审计脚本

```bash
python3 scripts/spec_audit.py --image cover.png --platform wechat-header
python3 scripts/spec_audit.py --width 1080 --height 1440 --platform xhs-portrait
python3 scripts/spec_audit.py --image cover.png --platform wechat-header --text-chars 14
python3 scripts/spec_audit.py --width 900 --height 383 --expect 900x383 --file-mb 0.4   # 数值自洽 → 全项通过（演示 fail 时改任一值）
```

输出 JSON：每项 `pass/fail` 与修复建议；exit 2 = 用法错误（如缺 `--image` 或 `--width/--height`），其余非零退出码 = 有 fail 项。

**参数纪律（实测）**：`--width/--height` 与 `--image` **必须给其一**——只传 `--expect 900x383` 会返回 `{"error": "need --image or --width/--height"}` 并 exit 2。`--expect` 是「平台不在库内时的自定义目标」，必须与 `--width/--height`（或 `--image`）搭配使用，不能单独替代待审尺寸。

### 步骤 2：按平台规格表核对（脚本内置）

内置规格库覆盖主流中文平台与海外平台（公众号头图 900x383 / 小红书 3:4 竖 1080x1440 与 1:1 方图 / B 站封面 1146x717 / 抖音竖版 1080x1920 / YouTube 缩略图 1280x720 ≤2MB 等）。平台不在库内时，用 `--expect WxH` **配合** `--width/--height` 声明目标 W×H（见步骤 1 第 4 条示例）。

### 步骤 3：文字安全区人工复核

脚本给建议值，人做最后判断：

- 四边留白 ≥ 画布短边 8%（平台 UI 控件会盖住边缘——实测依据见暗知识 1）
- 关键文字避开底部 15%（多数平台信息浮层区）；抖音/B 站封面额外避开左下角时长标签区
- 图上文字总量 ≤ 规格单 text 字段预算；超了回 image-prompt-engineer 减字，不是缩小字号硬塞
- 文字与背景对比度 ≥ 4.5:1（WCAG AA，暗知识 2）；仅靠颜色编码的信息做灰度冗余检查（暗知识 3）
- 缩略检查：图缩到拇指大小第一眼落点 = 规格单主体（眯眼测试，暗知识 4）

### 步骤 4：fail 项回流

尺寸错 → 回 design-brief-interpreter 改规格单 platform 字段再重走链；
文字超预算 → 回 image-prompt-engineer 改 text 段；**audit 不过，不许交付**。

## 交付标准

- 产物：审计结果 JSON（含每项 pass/fail 与建议）+ 结论一句话（全 pass 可交付 / 列出 fail 项与回流去向）。
- 保存位置：直接输出在对话中；被审计的图片文件位置不变。
- 完整性验证：脚本退出码 0 = 全部通过；退出码非 0 时必须逐项给出处置，不允许"带病交付"。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 比例差一点 | 模型不精确出目标尺寸 | 裁切到目标比例（保主体居中），再审计一次 |
| 分辨率不足 | 小图放大交付 | 回 prompt 提尺寸参数重生成，禁拉伸放大 |
| 文字被 UI 盖住 | 踩了平台浮层区 | 按 8%/15% 安全区规则移动构图重点；抖音/B 站另避左下角（暗知识 1） |
| 图上文字缩略后不可读 | 对比度不足或字号过小 | 按 WCAG 4.5:1 提高文字/背景对比（暗知识 2），或回规格单减字放大 |
| 红绿状态标记灰度后不可辨 | 仅靠颜色编码（暗知识 3） | 记 fail；加图标/形状/文字冗余编码后重审 |
| 第一眼落点不是主体 | 层级失败（暗知识 4） | 记 fail 并回流规格单：拉开三档尺寸/明度差距，强调色只给主体 |
| 文件超平台限额 | 无损 PNG 太大 | 转换压缩格式重导出，平台限额见规格表 |

## 平台规格速查（常用 6 条）

| 平台 | 尺寸 | 比例 | 限额 |
|------|------|------|------|
| 公众号头图 | 900x383 | 2.35:1 | ≤5MB |
| 小红书竖图 | 1080x1440 | 3:4 | ≤32MB |
| B 站封面 | 1146x717 | 1.6:1 | ≤5MB |
| 抖音竖版 | 1080x1920 | 9:16 | — |
| YouTube 缩略图 | 1280x720 | 16:9 | ≤2MB |
| 知乎文章头图 | 横图 16:9 | 16:9 | — |

完整表与更新方法见脚本内 `PLATFORM_SPECS`（PR 直接改表 + 跑测试）。

## 参考

- [scripts/spec_audit.py](scripts/spec_audit.py) —— 跑平台规格审计：比例/分辨率/安全区/文件大小，输出逐项 pass/fail JSON
- [scripts/test_smoke_layout_spec_auditor.py](scripts/test_smoke_layout_spec_auditor.py) —— 冒烟测试，改规格表或审计逻辑后先跑它
