---
name: layout-spec-auditor
description: "Audit a generated image (or its plan) against a design spec and platform layout rules: aspect ratio match, minimum resolution, safe-area margins for text, platform file-size limits, and text-budget compliance. Reads the actual image file with Pillow when available, or audits declared dimensions. Use when the user asks to 检查图片规格 / 尺寸对不对 / 审图 / layout audit / 封面规格 / 图片合规, or automatically after generating an image in the visual-design-studio chain. Do NOT use for judging aesthetics (that is design critique), nor for writing prompts."
license: Apache-2.0
compatibility: Python 3.8+; Pillow optional (needed only when auditing an actual image file).
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Layout Spec Auditor

链条守门员。生成完的图在交付前过三道闸：**比例对不对、分辨率够不够、文字安不安全**。规格阶段说好的画布，交付时偏差 1% 都是返工。

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
- `PIL-OK` 仅在审计真实图片文件时必需；输出 `PIL-MISSING` 时修复二选一：`pip install pillow`，或改走声明尺寸模式（`--width/--height` 纯计算，不读图）。

## 工作流

### 步骤 1：跑规格审计脚本

```bash
python3 scripts/spec_audit.py --image cover.png --platform wechat-header
python3 scripts/spec_audit.py --width 1080 --height 1440 --platform xhs-portrait
python3 scripts/spec_audit.py --image cover.png --platform wechat-header --text-chars 14
```

输出 JSON：每项 `pass/fail` 与修复建议。非零退出码 = 有 fail 项。

### 步骤 2：按平台规格表核对（脚本内置）

内置规格库覆盖主流中文平台与海外平台（公众号头图 900x383 / 小红书 3:4 竖 1080x1440 与 1:1 方图 / B 站封面 1146x717 / 抖音竖版 1080x1920 / YouTube 缩略图 1280x720 ≤2MB 等）。平台不在库内时手动声明目标 W×H 走 `--expect WxH`。

### 步骤 3：文字安全区人工复核

脚本给建议值，人做最后判断：

- 四边留白 ≥ 画布短边 8%（平台 UI 控件会盖住边缘）
- 关键文字避开底部 15%（多数平台信息浮层区）
- 图上文字总量 ≤ 规格单 text 字段预算；超了回 image-prompt-engineer 减字，不是缩小字号硬塞

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
| 文字被 UI 盖住 | 踩了平台浮层区 | 按 8%/15% 安全区规则移动构图重点 |
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
