# 前端八宗罪（LLM 写组件最常翻车的 8 类，逐一堵死）

1. **魔法数字** — 颜色/间距/圆角/字号直接写死在样式里。堵：全部取自
   `design-tokens.json`（CSS 变量或内联 token 引用），组件里搜不到 `#` 和 `px` 裸值。
2. **内联样式对象** — `style={{ color: 'red' }}`。堵：一律走 CSS Modules class。
3. **Props 无类型** — `function X(props){}`。堵：先写 `XxxProps` 接口，无 `any`。
4. **可交互无 a11y** — `<div onClick>`。堵：用 `<button>`/`<a>` 或补 `role`/`aria-*`。
5. **状态管理越权** — 组件内塞全局逻辑。堵：只接收 props + 本地 `useState`。
6. **未处理异步/空态** — 列表直接 `.map`。堵：加 loading / empty / error 三态。
7. **命名歧义** — `btn`/`go`/`item`。堵：语义化组件名 + 动词 props。
8. **样式方案假设** — 默认 CSS Modules；工程用 Tailwind/Styled 需手改。

## 自检命令（在用户工程内）
- `tsc --noEmit`（类型）
- `grep -RE "('#[0-9a-f]{3,6}|[0-9]+px)" src/ui/`（魔法数字扫描，理想输出为空）
