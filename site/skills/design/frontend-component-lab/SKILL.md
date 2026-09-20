---
name: frontend-component-lab
description: >
  Scaffold production-grade React/TypeScript UI components wired to a design
  token system: component + CSS Modules + design-tokens.json, plus a review
  checklist that kills the classic LLM frontend sins (magic numbers, inline
  styles, untyped props, missing a11y). Use when the user asks to 做一个组件 /
  建个 React 组件 / 组件脚手架 / UI 组件库 / 设计系统 token / frontend design
  system / 组件规范. Do NOT use for pure image/design-mockup generation
  (use image-prompt-engineer) or for backend work.
license: Apache-2.0
compatibility: 产出 .tsx/.css/.json 源码文件；需用户自接 TS 工程（不联网、不装 npm 也能生成）
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: script
  tier: standard
  verified-date: "2026-09-20"
---

# Frontend Component Lab（组件脚手架 + 设计系统 Token）

把一个组件需求变成**能跑的 React/TS 组件 + CSS Modules + 设计 token 文件**，
并附一份"LLM 写前端最容易翻车"的审查清单。改造自 mattpocock/skills 的
`frontend-design` 思路与 ECC 的 `frontend-patterns`（React/Next 规范），裁剪为
离线、零依赖的脚手架 + 纪律层。

核心判断：**模型写前端的病不在"写不出"，而在"魔法数字 + 内联样式 + Props 无类型"**。
本技能把这三类问题用 token 文件和强类型骨架直接堵死。

> 红线：默认 **dry-run** 只打印将生成什么；`--write` 才落盘；同名已存在需
> `--force`。零网络、不装 npm。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 组件名 | 是 | PascalCase，如 `PricingCard` |
| props | 否 | 逗号分隔的 string 类型 props |
| token 覆盖 | 否 | 传一个 JSON 覆盖默认 color/spacing/radius/font |
| 输出目录 | 否 | 默认当前目录 |

## 前置自检

1. 组件名是否 PascalCase？（脚本会拒绝小写开头）
2. 目标工程是否用 CSS Modules？若不是（用 Tailwind/Styled），`--write` 后需手改
   `.module.css` 为对应方案——本技能不假设构建工具。
3. 设计 token 是否要继承现有品牌？有就先准备一份覆盖 JSON。

## 工作流

```bash
# 1. 干跑：看会生成哪些文件
python3 scripts/scaffold_component.py --name PricingCard --props title,price,cta --out ./src/ui

# 2. 真生成
python3 scripts/scaffold_component.py --name PricingCard --props title,price,cta \
  --out ./src/ui --write

# 3. 带品牌 token 覆盖
python3 scripts/scaffold_component.py --name PricingCard --tokens ./brand.json \
  --out ./src/ui --write --force
```

生成后，按 [references/frontend-sins.md](references/frontend-sins.md) 的清单
过一遍 TSX，把 `// TODO` 补成真实渲染逻辑。

## 交付标准

- `design-tokens.json` 是**唯一**颜色/间距/圆角来源，组件内**零魔法数字**
- `XxxProps` 接口齐全，无 `any`
- 每个可交互元素有 `role` / `aria-*` 或 `data-component` 锚点
- 文件能被 tsc 编译（用户工程内 `tsc --noEmit` 过）

## 失败处置表

| 现象 | 根因 | 处置 |
|---|---|---|
| 组件名被拒 | 非 PascalCase / 含非字母 | `--name` 改合法名 |
| 已存在文件不覆盖 | 默认幂等 | 加 `--force` |
| 颜色还是默认蓝 | 没传 token 覆盖 | 准备覆盖 JSON 传 `--tokens` |
| CSS 不被识别 | 工程没用 CSS Modules | 手改样式方案 |
| a11y 缺 role | TODO 没补 | 按 sins 清单补交互语义 |

## 参考

- 前端"八宗罪"审查清单：[references/frontend-sins.md](references/frontend-sins.md)

## 链路位置

- 上游：`design-brief-interpreter`（把模糊需求翻成设计规格）
- 下游：`layout-spec-auditor`（按平台版面规格审计产出）
