# e2e 处置手册

## 选择器优先级（从高到低）
1. `get_by_role("button", name="Submit")` — 语义，重构最稳
2. `get_by_label("Email")` / `get_by_placeholder("...")` — 表单首选
3. `[data-testid="pay-btn"]` — 文案会变时的锚点（需在业务代码里预埋）
4. 最后才用 css `text=...`；**禁用**纯 class、纯 xpath

## 登录态复用
```python
# 首登（codegen 产出 auth.json）
ctx = browser.new_context(storage_state="auth.json")
# 后续所有用例都传这个 ctx，避免每条重登
```
- 凭证走 env：`os.environ["E2E_USER"]`，绝不进测试文件。

## 反爬 / 429 / 验证码
- 降并发、加 `page.wait_for_timeout(backoff)` 退避。
- 仿真 user_agent / 视口。
- **验证码不自动化**（绕过有合规风险）：人工登录一次 → storage_state 复用。

## 跑法
```bash
E2E_BASE_URL=http://127.0.0.1:8000 E2E_HEADFUL=1 bash run_e2e.sh
```
- `E2E_HEADFUL=1` 看浏览器调试；`E2E_INSTALL_BROWSER=1` 强制重装浏览器。
