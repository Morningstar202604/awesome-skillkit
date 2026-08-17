# 已知坑与解决方案

## 目录

1. [publishAt 字段报 DateTime 转换错误](#1-publishat-字段报-datetime-转换错误)
2. [XSRF Token "会话校验失败"](#2-xsrf-token-会话校验失败)
3. [浏览器 Session 过期无法操作编辑器](#3-浏览器-session-过期无法操作编辑器)
4. [图片插入 replace 匹配失败](#4-图片插入-replace-匹配失败)
5. [Cookie 从 auth-state.json 提取后无效](#5-cookie-从-auth-statejson-提取后无效)
6. [图片上传返回"未登录"](#6-图片上传返回未登录)
7. [Playwright click/fill 超时](#7-playwright-clickfill-超时)
8. [标签输入框无法用 fill](#8-标签输入框无法用-fill)
9. [评论提交后看似无反应](#9-评论提交后看似无反应)
10. [投稿 checkbox 被 disabled](#10-投稿-checkbox-被-disabled)
11. [登录态过期](#11-登录态过期)
12. [编辑器找不到 #md-editor](#12-编辑器找不到-md-editor)
13. [CSS 选择器语法错误](#13-css-选择器语法错误)

---

## 1. publishAt 字段报 DateTime 转换错误

**现象**：

```
HTTP Error 400: {"errors":["The JSON value could not be converted to System.Nullable`1[System.DateTime]. Path: $.publishAt | LineNumber: 0 | BytePositionInLine: 13931."],"type":0}
```

**原因**：`publishAt` 字段传了空字符串 `""`，博客园后端尝试将其解析为 DateTime 但失败。

**解决方案**：`publishAt` 必须为 `null`（Python 的 `None`），不能是空字符串：

```python
# 错误
"publishAt": ""

# 正确
"publishAt": None
```

同样，`autoDesc`、`password`、`featuredImage` 也应该用 `null` 而非空字符串。

---

## 2. XSRF Token "会话校验失败"

**现象**：

```
HTTP Error 400: {"errors":["会话校验失败，请刷新页面重试"],"type":4}
```

**原因**：XSRF token 无效或已过期。从 `auth-state.json` 中直接提取的 XSRF token 可能已经过期。

**解决方案**：通过 HTTP 请求重新获取 XSRF token：

```python
# GET 请求 HTML 页面（不是 API 端点）
req = urllib.request.Request(
    'https://i.cnblogs.com/posts',
    headers={'Cookie': cookie, 'Accept': 'text/html'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    for sc in (resp.headers.get_all('Set-Cookie') or []):
        if 'XSRF' in sc:
            xsrf = urllib.parse.unquote(sc.split(';')[0].split('=', 1)[1])
```

关键：GET 的目标是 **HTML 页面** `https://i.cnblogs.com/posts`，不是 API 端点。API 端点的响应不包含 Set-Cookie 头。

---

## 3. 浏览器 Session 过期无法操作编辑器

**现象**：`playwright-cli goto "https://i.cnblogs.com/posts/edit"` 后页面跳转到登录页，或 `eval` 返回 `SecurityError: Failed to read the 'cookie' property`。

**原因**：浏览器 Playwright session 已过期，或浏览器会话已关闭。

**解决方案**：改用 API 方式操作（推荐），或重新初始化浏览器：

1. **API 方式**（首选）：从 `auth-state.json` 提取 cookie，用 Python urllib 直接调用 API。API cookie 的有效期通常比浏览器 session 长。
2. **重新初始化浏览器**：设置 cookie 后导航到后台页面（见 `references/publish-api.md`）。
3. **提示用户登录**：如果 API cookie 也过期，提示用户通过浏览器手动登录。

---

## 4. 图片插入 replace 匹配失败

**现象**：用 `body.replace(old_text, new_text)` 插入图片 URL 后，图片未出现在正文中。

**原因**：replace 的目标文本与实际正文不完全匹配（标点、换行、空格差异）。

**解决方案**：

1. **先调试定位**：用 `body.find("部分文本")` 确认文本位置
2. **检查实际内容**：打印目标位置附近 200 字符
3. **使用精确匹配**：确保标点符号（中文/英文）、换行符（`\n`）、空格完全一致

```python
# 调试
idx = body.find("本文不站队")
if idx >= 0:
    print(f"Found at {idx}: {repr(body[idx:idx+120])}")
else:
    print("Not found, searching alternatives...")
```

4. **插入后验证**：检查图片 URL 是否已在 body 中

```python
if img_url in body:
    print("Image inserted successfully")
else:
    print("Image insertion FAILED")
```

---

## 5. Cookie 从 auth-state.json 提取后无效

**现象**：从 `auth-state.json` 提取的 cookie 用于 API 调用时返回 HTML 页面（而非 JSON）。

**原因**：
1. Cookie 已过期（auth-state.json 是登录时的快照）
2. 提取时遗漏了关键 cookie
3. cookie 字符串格式错误

**解决方案**：

1. **验证 cookie 有效性**：

```python
req = urllib.request.Request(
    'https://i.cnblogs.com/api/posts/22435239',
    headers={'Cookie': cookie, 'Accept': 'application/json'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    raw = resp.read().decode()
    if raw.startswith('{'):
        print("Cookie 有效")
    else:
        print("Cookie 过期")
```

2. **确保提取所有 cnblogs 域 cookie**：

```python
for c in auth_data['cookies']:
    if 'cnblogs' in c.get('domain', ''):
        parts.append(f"{c['name']}={c['value']}")
```

3. **如果过期**：提示用户通过浏览器重新登录

---

## 6. 图片上传返回"未登录"

**现象**：上传图片到 `upload.cnblogs.com` 返回 `{"success":false,"message":"未登录，请先登录"}`。

**原因**：上传端点 `upload.cnblogs.com` 需要有效的登录 cookie，且 `Referer` 头需要正确设置。

**解决方案**：

1. **确保 cookie 包含所有 cnblogs 域**：从 auth-state.json 提取所有 `cnblogs` 域 cookie
2. **设置 Referer 头**：`Referer: https://i.cnblogs.com/`
3. **设置 User-Agent**：`Mozilla/5.0`
4. **使用 multipart/form-data**：不是 base64，是标准的文件上传格式

```python
headers = {
    'Cookie': cookie,
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://i.cnblogs.com/'
}
```

---

## 7. Playwright click/fill 超时

**现象**：使用 `playwright-cli click eXX` 或 `fill eXX "text"` 时超时，尤其对 Ant Design 组件。

**原因**：博客园新版后台使用 Angular + Ant Design，组件有动画延迟和自定义事件。

**解决方案**：统一用 `eval` 执行 JS 操作：

```javascript
// 不推荐：容易超时
scripts/playwright-cli click eXX

// 推荐：用JS直接操作DOM
scripts/playwright-cli eval "() => { document.querySelector('#elementId').click(); }"
```

需要触发 Angular 变更检测时 dispatch input/change 事件：

```javascript
const el = document.querySelector('#elementId');
el.value = 'value';
el.dispatchEvent(new Event('input', {bubbles:true}));
el.dispatchEvent(new Event('change', {bubbles:true}));
```

---

## 8. 标签输入框无法用 fill

**现象**：标签输入是 Ant Design Select 组件，普通 fill 无效。

**解决方案**：用 keyboard type + Enter：

```bash
scripts/playwright-cli eval "() => { document.querySelector('.ant-select-selection-search-input').focus(); }"
scripts/playwright-cli type "标签名"
scripts/playwright-cli press Enter
```

---

## 9. 评论提交后看似无反应

**现象**：点击提交评论后，评论列表数量没变。

**原因**：评论实际已提交成功，但列表异步加载有延迟。成功的标志是 **textarea 被清空**。

**解决方案**：

```javascript
const txt = document.querySelector('#tbCommentBody');
if (txt && txt.value === '') {
  // 成功！刷新页面确认
}
```

---

## 10. 投稿 checkbox 被 disabled

**现象**：`#site-publish-site-home`（原创精品投稿）checkbox 无法点击。

**原因**：3小时内同分类只能投1篇候选区文章。

**解决方案**：改投首页候选区（`inSiteCandidate: True`），或换一个网站分类直接发布。

---

## 11. 登录态过期

**现象**：
- API 返回 HTML 而非 JSON
- 浏览器页面跳转到登录页
- 图片上传返回"未登录"

**解决方案**：提示用户通过浏览器重新登录：

```
您的博客园登录态已过期，请手动登录后告诉我继续。
登录地址：https://account.cnblogs.com/signin
```

用户登录后，`auth-state.json` 会更新，重新提取 cookie 即可。

---

## 12. 编辑器找不到 #md-editor

**现象**：浏览器中找不到 `#md-editor` textarea。

**原因**：编辑器可能不在 Markdown 模式，或页面未完全加载。

**解决方案**：

```javascript
// 检查编辑器模式
const modeToggle = document.querySelector('[class*=editor-mode], .mode-toggle');
if (modeToggle && modeToggle.textContent.includes('Markdown')) {
  modeToggle.click(); // 切换到 Markdown 模式
}
// 等待2秒后再查找
const ta = document.querySelector('#md-editor');
```

注意：API 方式不依赖编辑器，推荐优先使用 API。

---

## 13. CSS 选择器语法错误

**现象**：`querySelector` 报 "is not a valid selector"。

**原因**：属性选择器中包含特殊字符或缺少引号。

**错误**：
```javascript
document.querySelector('a[href*=home.cnblogs.com]')  // 缺少引号
```

**正确**：
```javascript
document.querySelector('a[href*="home.cnblogs.com"]')  // 属性值加引号
```

或用 JS 遍历替代复杂选择器：

```javascript
const links = document.querySelectorAll('a');
for (const l of links) {
  if (l.href && l.href.includes('home.cnblogs.com')) break;
}
```
