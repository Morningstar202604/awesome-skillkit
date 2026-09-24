# The Eight Frontend Sins (the 8 categories where LLMs most often mess up components, each plugged shut)

1. **Magic numbers** — colors/spacing/corner radius/font sizes hardcoded directly in styles. Plug: all values pulled from
   `design-tokens.json` (CSS variables or inline token references); no bare `#` or `px` values should be found in components.
2. **Inline style objects** — `style={{ color: 'red' }}`. Plug: always use CSS Modules class.
3. **Untyped props** — `function X(props){}`. Plug: write the `XxxProps` interface first; no `any`.
4. **Interactive without a11y** — `<div onClick>`. Plug: use `<button>`/`<a>` or add `role`/`aria-*`.
5. **Overreaching state management** — stuffing global logic inside a component. Plug: only accept props + local `useState`.
6. **Unhandled async/empty states** — calling `.map` directly on a list. Plug: add loading / empty / error three states.
7. **Ambiguous naming** — `btn`/`go`/`item`. Plug: semantic component names + verb props.
8. **Styling assumption** — default CSS Modules; if the project uses Tailwind/Styled, needs manual adjustment.

## Self-check commands (run in the user's project)
- `tsc --noEmit` (types)
- `grep -RE "('#[0-9a-f]{3,6}|[0-9]+px)" src/ui/` (magic number scan; ideal output is empty)
