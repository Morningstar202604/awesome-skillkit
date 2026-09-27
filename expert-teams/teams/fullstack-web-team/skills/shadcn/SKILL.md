---
name: shadcn
description: shadcn/ui 组件管理与主题定制指南。当需要用 CLI 添加/更新组件、配置 components.json、定制主题 token 与 CSS 变量、用 CVA 写 variants、覆盖默认样式、组织私有 registry 时，由 fullstack-frontend-engineer 加载执行。
license: MIT
compatibility: universal
---

# shadcn/ui 组件管理

本 skill 面向 fullstack-frontend-engineer，规范 shadcn/ui 的安装、定制与升级。

## 何时使用
- 项目初始化 shadcn/ui 配置（components.json、主题）；
- 用 CLI 加新组件、改主题色、写自定义 variant；
- 升级已安装组件、解决样式冲突。

## 核心认知
- shadcn/ui **不是 npm 组件库**：CLI 把组件源码拷进你仓库，你拥有并可改。
- 基于 Radix UI（无样式原语）+ Tailwind + CVA（变体）+ cn() 工具函数。
- 主题靠 CSS 变量（HSL/OKLCH）切换亮色/暗色，不依赖 JS 运行时。

## 初始化与配置
```bash
# 初始化（已配置 tailwind + path alias 后）
npx shadcn@latest init
# 添加组件
npx shadcn@latest add button dialog input table
```
`components.json` 关键项：
- `style`：默认风格（new-york / default）。
- `tailwind.config` / `tailwind.css`：指向你的配置与全局 CSS。
- `aliases.components` / `aliases.ui`：组件放哪（一般 `@/components/ui`）。
- `rsc: true`：App Router 项目必须开。

## 主题定制
- 改 `app/globals.css` 里的 `:root` 与 `.dark` CSS 变量（`--primary`、`--background`、`--radius` 等）。
- 圆角通过 `--radius` 全局控制，组件内用 `rounded-md` 等 token 引用。
- 新增品牌色：在 `@theme inline` 里映射 CSS 变量，Tailwind 里直接 `bg-brand`。

## 写自定义 variant（CVA）
```tsx
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        danger: "bg-red-600 text-white hover:bg-red-700",
        ghost: "hover:bg-accent",
      },
      size: {
        default: "h-10 px-4",
        sm: "h-8 px-3 text-sm",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
)
```

## 清单（交付前逐项过）
- [ ] `components.json` 路径 alias 正确，`@/components/ui` 可解析。
- [ ] App Router 项目 `rsc: true`，客户端组件加了 `"use client"`。
- [ ] 主题只改 CSS 变量，不在组件里硬编码品牌色 hex。
- [ ] 复用 `cn()`（clsx + tailwind-merge）合并 className，避免覆盖顺序问题。
- [ ] 自定义组件放到 `@/components/ui` 或业务组件目录，不直接改 shadcn 拷来的文件（要改也清楚改动点，便于后续 upgrade 合并）。
- [ ] 暗色模式两种变量都配齐，无视觉断层。
- [ ] 新增组件用 `add` CLI 拉取，不手抄源码避免版本漂移。
- [ ] 升级用 `npx shadcn@latest update`，冲突时人工合并。

## 易错点
- **把组件当 npm 库 `import { Button } from "shadcn-ui"`**：根本没有这个包，组件就在你本地 `@/components/ui/button`。
- **直接改拷来的文件又不记录**：下次 `update` 会被覆盖或冲突；定制尽量用 variant + className 覆盖，少改源码。
- **硬编码颜色**：组件里写 `bg-[#ff0000]`，暗色模式与主题切换全部失效。
- **Tailwind 内容扫描没包含 ui 目录**：`tailwind.config` 的 `content` 漏了 `./components/ui/**/*.{ts,tsx}`，样式全丢。
- **忘记 `"use client"`**：Dialog/Dropdown 等用了 Radix 事件的组件在 Server Component 里直接报错。
- **乱用 `cn()` 反向覆盖**：tailwind-merge 会智能去重，但后写的 `!important` 前缀仍需谨慎。
