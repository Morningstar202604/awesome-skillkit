# 社区互动操作

## 目录

1. [行为规范](#1-行为规范)
2. [评论获取（API）](#2-评论获取api)
3. [评论提交（浏览器）](#3-评论提交浏览器)
4. [回复评论](#4-回复评论)
5. [推荐博文（点赞）](#5-推荐博文点赞)
6. [查看消息](#6-查看消息)
7. [博问互动](#7-博问互动)
8. [闪存/发动态](#8-闪存发动态)
9. [每日活跃检查清单](#9-每日活跃检查清单)

---

## 1. 行为规范

### 核心原则

| 规则 | 说明 |
|------|------|
| 一问一答 | 别人回复了才回，不主动重复评论同一个人 |
| 内容筛选 | 纯客套/情绪化/无实质内容的评论跳过不回 |
| 回复质量 | 回复要有实质内容，补充观点或表示感谢并展开讨论 |
| 不敷衍 | 不发"感谢支持"、"说得好"等无意义回复 |
| 克制互动 | 宁可不回也不要乱回，质量优先于数量 |

### 应该回复的情况

- 评论者提出了具体技术问题
- 评论者分享了有价值的不同观点
- 评论者指出了文章中的错误
- 评论者提出了有建设性的补充

### 应该跳过的情况

- 纯客套："感谢分享"、"学到了"、"写的很好"
- 情绪化表达："太悲观了"、"小编危言耸听"
- 无实质内容：只有一个表情、只说"顶"、"沙发"
- 已经回复过的人再次发无关内容

---

## 2. 评论获取（API）

通过 AJAX 接口获取文章评论（返回 HTML 片段）：

```python
import urllib.request

cookie = open('/tmp/ck.txt').read()

req = urllib.request.Request(
    f'https://www.cnblogs.com/badhope/ajax/GetComments.aspx?postId={postId}&pageIndex=0',
    headers={
        'Cookie': cookie,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'text/html'
    }
)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode()
```

返回的是 HTML 片段，用 `.feedbackItem` 选择器解析。在浏览器中：

```javascript
const items = document.querySelectorAll('.feedbackItem');
const result = [];
for (const item of items) {
  const body = item.querySelector('.blog_comment_body');
  const links = item.querySelectorAll('a');
  let name = 'unknown';
  let floor = '';
  for (const l of links) {
    if (l.href && l.href.includes('home.cnblogs.com')) {
      name = l.textContent.trim();
    }
    if (l.textContent.includes('楼')) {
      floor = l.textContent.trim();
    }
  }
  result.push({
    floor: floor,
    name: name,
    body: body ? body.textContent.trim() : 'none'
  });
}
return result;
```

---

## 3. 评论提交（浏览器）

评论提交需要浏览器操作（无 API）。需要先通过 `dumate-browser-use` 打开文章页面：

```bash
# 导航到文章页面
scripts/playwright-cli goto "https://www.cnblogs.com/badhope/p/{postId}/{slug}"
```

填写评论：

```javascript
const txt = document.querySelector('#tbCommentBody');
txt.value = '评论内容...';
txt.dispatchEvent(new Event('input', {bubbles:true}));
txt.dispatchEvent(new Event('change', {bubbles:true}));
```

提交评论：

```javascript
const btn = document.querySelector('#btn_comment_submit');
btn.click();
```

验证成功（textarea 被清空 = 成功）：

```javascript
const txt = document.querySelector('#tbCommentBody');
return txt ? txt.value === '' : 'no textarea';
```

---

## 4. 回复评论

### 点击"回复"链接

```javascript
// 找到指定评论的"回复"链接
const items = document.querySelectorAll('.feedbackItem');
const targetItem = items[index]; // index从0开始
const replyLink = Array.from(targetItem.querySelectorAll('a'))
  .find(a => a.textContent.trim() === '回复');
if (replyLink) replyLink.click();
```

### 填写回复

点击"回复"后，textarea 会自动填充 `@用户名`：

```javascript
const txt = document.querySelector('#tbCommentBody');
txt.value = '@用户名\n回复内容...';
txt.dispatchEvent(new Event('input', {bubbles:true}));
txt.dispatchEvent(new Event('change', {bubbles:true}));
```

### 提交回复

同评论提交，点击 `#btn_comment_submit`。

### 删除评论

如果需要删除自己的评论（如重复评论）：

```python
import urllib.request

cookie = open('/tmp/ck.txt').read()
xsrf = open('/tmp/xsrf.txt').read().strip()

req = urllib.request.Request(
    f'https://www.cnblogs.com/badhope/comment/DeleteComment.aspx?commentId={commentId}',
    headers={
        'Cookie': cookie,
        'X-XSRF-TOKEN': xsrf
    },
    method='POST'
)
urllib.request.urlopen(req, timeout=15)
```

---

## 5. 推荐博文（点赞）

### 打开博文页面

```bash
scripts/playwright-cli goto "https://www.cnblogs.com/{用户}/{postId}"
```

### 点击推荐

```javascript
const btn = document.querySelector('.diggit');
if (btn) btn.click();
```

### 验证

```javascript
// 等待2秒后检查
const tip = document.querySelector('#digg_tips');
return tip ? tip.textContent.trim() : 'no tip';
// "支持成功 撤回" = 推荐成功
```

### 批量推荐

先从首页获取博文列表：

```javascript
const links = document.querySelectorAll('a');
const result = [];
for (const l of links) {
  if (l.href && l.href.match(/cnblogs\.com\/[^/]+\/p\/\d+/) && l.textContent.trim().length > 5) {
    result.push({ title: l.textContent.trim().substring(0, 80), href: l.href });
  }
}
return result.slice(0, 12);
```

然后逐个打开并推荐。注意避开敏感话题文章。

---

## 6. 查看消息

### 打开消息中心

```bash
scripts/playwright-cli goto "https://msg.cnblogs.com/"
```

### 获取消息列表

```javascript
const links = document.querySelectorAll('a[href*=item]');
const result = [];
for (const l of links) {
  result.push({
    text: l.textContent.trim().substring(0, 100),
    href: l.href
  });
}
return result.slice(0, 10);
```

### 消息类型

- `[博客评论通知]` — 有人评论了你的文章
- `[博问回复通知]` — 博问帖有新回复
- `JS权限申请已批准` — 系统通知
- `博客申请已批准` — 系统通知

---

## 7. 博问互动

### 查看博问帖

```bash
scripts/playwright-cli goto "https://q.cnblogs.com/q/{topicId}"
```

### 获取博问帖内容

博问页面 DOM 与博客不同，用文本搜索：

```javascript
const pageText = document.body.innerText;
const lines = pageText.split('\n').filter(l => l.trim().length > 5);
return lines.slice(0, 30);
```

### 回复博问帖

```javascript
const textarea = document.querySelector('#post-comment-body, .comment-textarea, textarea');
if (textarea) {
  textarea.value = '回复内容';
  textarea.dispatchEvent(new Event('input', {bubbles:true}));
}
// 查找提交按钮
const btn = document.querySelector('button[class*=submit], .comment-submit');
if (btn) btn.click();
```

---

## 8. 闪存/发动态

### 打开闪存页面

```bash
scripts/playwright-cli goto "https://ing.cnblogs.com/"
```

### 发布闪存

```javascript
const txt = document.querySelector('#ing_TextContent, .ing-textarea, textarea');
if (txt) {
  txt.value = '动态内容 #标签#';
  txt.dispatchEvent(new Event('input', {bubbles:true}));
}
const btn = document.querySelector('#btn_ing_post, .ing-submit, button[class*=submit]');
if (btn) btn.click();
```

闪存支持标签语法：用 `#标签名#` 包裹标签。

---

## 9. 每日活跃检查清单

| 任务 | 数量 | 方式 |
|------|:---:|------|
| 推荐别人博文 | 3篇 | 浏览器打开+点击推荐 |
| 在别人博文下评论 | 3条 | 浏览器打开+填写评论 |
| 查看消息中心 | 1次 | 浏览器打开消息页 |
| 检查自己文章评论 | 全部 | API获取评论列表 |
| 回复新评论 | 按需 | 只回该回的 |
| 检查博问帖回复 | 按需 | 浏览器打开博问 |

### 检查自己文章评论的流程

```python
# 已发布文章列表
post_ids = [22467774, 22436525, 22435358, 22435341, 22435239, 22435235, 22435231, 22435149, 22435111, 22430972, 22404761, 22359592, 22357737, 22345012, 22290394]

# 逐篇检查评论
for pid in post_ids:
    req = urllib.request.Request(
        f'https://www.cnblogs.com/badhope/ajax/GetComments.aspx?postId={pid}&pageIndex=0',
        headers={
            'Cookie': cookie,
            'X-Requested-With': 'XMLHttpRequest'
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode()
    # 检查是否有 .feedbackItem
    if 'feedbackItem' in html:
        print(f"Post {pid}: 有评论")
    # 无评论的跳过
```

### 回复决策流程

1. 获取评论列表
2. 对每条评论判断：是否需要回复？
3. 检查是否已经回复过（避免重复）
4. 需要回复的 → 打开文章页面 → 点击回复 → 填写内容 → 提交
5. 不需要回复的 → 跳过
