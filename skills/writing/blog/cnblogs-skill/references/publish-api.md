# API 发文完整流程

## 目录

1. [Cookie 提取](#1-cookie-提取)
2. [XSRF Token 获取](#2-xsrf-token-获取)
3. [登录态验证](#3-登录态验证)
4. [读取文章（GET）](#4-读取文章get)
5. [创建文章（POST）](#5-创建文章post)
6. [更新文章（POST）](#6-更新文章post)
7. [POST 请求字段详解](#7-post-请求字段详解)
8. [发布后验证](#8-发布后验证)
9. [签名管理 API](#9-签名管理-api)
10. [完整 Python 示例](#10-完整-python-示例)

---

## 1. Cookie 提取

Cookie 存储在会话工作目录的 `auth-state.json` 文件中。提取 cnblogs 域的所有 cookie：

```python
import json

with open('auth-state.json') as f:
    data = json.load(f)

cookies = data.get('cookies', [])
parts = []
for c in cookies:
    domain = c.get('domain', '')
    if 'cnblogs' in domain:
        parts.append(f"{c['name']}={c['value']}")

cookie_str = '; '.join(parts)
# 保存到文件供后续使用
with open('/tmp/ck.txt', 'w') as f:
    f.write(cookie_str)
```

关键 cookie 包括：
- `.Cnblogs.AspNetCore.Cookies` — 主认证 cookie
- `.CNBlogsCookie` — 辅助认证 cookie
- `XSRF-TOKEN` — 防 CSRF token（需单独提取，见下文）

---

## 2. XSRF Token 获取

POST 请求需要 `X-XSRF-TOKEN` header。**不能从 auth-state.json 中直接取**（可能已过期），需通过 HTTP 请求重新获取：

```python
import urllib.request, urllib.parse

cookie_str = open('/tmp/ck.txt').read()

req = urllib.request.Request(
    'https://i.cnblogs.com/posts',
    headers={
        'Cookie': cookie_str,
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
)
with urllib.request.urlopen(req, timeout=15) as resp:
    set_cookies = resp.headers.get_all('Set-Cookie') or []
    for sc in set_cookies:
        if 'XSRF' in sc:
            token_part = sc.split(';')[0]  # XSRF-TOKEN=xxx
            token_val = urllib.parse.unquote(token_part.split('=', 1)[1])
            with open('/tmp/xsrf.txt', 'w') as f:
                f.write(token_val)
            break
```

关键点：
- GET 的目标是 **HTML 页面** `https://i.cnblogs.com/posts`，不是 API 端点
- API 端点（如 `/api/posts/{id}`）的响应不包含 Set-Cookie 头
- token 值需要 `urllib.parse.unquote` 解码

---

## 3. 登录态验证

在执行任何操作前，先验证 cookie 是否有效：

```python
import json, urllib.request

cookie = open('/tmp/ck.txt').read()

req = urllib.request.Request(
    'https://i.cnblogs.com/api/posts/22435239',  # 用任意已有文章ID
    headers={'Cookie': cookie, 'Accept': 'application/json'}
)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        if 'blogPost' in data:
            print("Cookie 有效")
        else:
            print("Cookie 可能过期")
except Exception as e:
    print(f"Cookie 过期: {e}")
```

判断标准：
- 返回 JSON 且包含 `blogPost` 字段 → 有效
- 返回 HTML（`<!doctype html>`）→ 过期，需重新登录

---

## 4. 读取文章（GET）

```python
import json, urllib.request

cookie = open('/tmp/ck.txt').read()

req = urllib.request.Request(
    f'https://i.cnblogs.com/api/posts/{postId}',
    headers={'Cookie': cookie, 'Accept': 'application/json'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    bp = data['blogPost']
```

返回的 `blogPost` 对象包含完整文章数据，字段见下方第7节。

---

## 5. 创建文章（POST）

```python
import json, urllib.request

cookie = open('/tmp/ck.txt').read()
xsrf = open('/tmp/xsrf.txt').read().strip()

post_data = {
    "postType": 1,
    "accessPermission": 0,
    "title": "文章标题",
    "postBody": "Markdown 正文",
    "categoryIds": [2526541],
    "siteCategoryId": 108762,
    "blogTeamIds": [],
    "isPublished": True,
    "displayOnHomePage": True,
    "isAllowComments": True,
    "includeInMainSyndication": True,
    "isPinned": False,
    "showBodyWhenPinned": False,
    "isOnlyForRegisterUser": False,
    "isUpdateDateAdded": False,
    "entryName": "your-slug-here",
    "description": "摘要内容",
    "featuredImage": None,
    "tags": ["标签1", "标签2"],
    "isMarkdown": True,
    "isDraft": False,
    "isAigc": False,
    "changePostType": False,
    "blogId": 861831,
    "author": "your_username",
    "removeScript": False,
    "inSiteCandidate": True,
    "inSiteHome": False,
    "autoDesc": None,
    "password": None,
    "publishAt": None,
    "changeCreatedTime": False,
    "canChangeCreatedTime": False,
    "isContributeToImpressiveBugActivity": False,
    "usingEditorId": None,
    "sourceUrl": None,
    "clientInfo": None
}

json_data = json.dumps(post_data, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://i.cnblogs.com/api/posts',
    data=json_data,
    headers={
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-XSRF-TOKEN': xsrf
    },
    method='POST'
)

with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read().decode())
    print(f"文章ID: {result['id']}")
    print(f"文章URL: {result['url']}")
```

成功响应（200）：
```json
{
    "id": 22467774,
    "title": "文章标题",
    "url": "https://www.cnblogs.com/your_username/p/22467774/slug",
    "blogUrl": "https://www.cnblogs.com/your_username",
    "postType": 1,
    "dateAdded": "2026-08-14T12:14:00",
    "entryName": "slug",
    "tags": ["标签1", "标签2"],
    "isVip": null
}
```

---

## 6. 更新文章（POST）

更新文章与创建文章使用同一个 API 端点（`POST /api/posts`），区别在于请求体中包含 `id` 字段：

```python
# 1. 先 GET 获取现有文章完整数据
req = urllib.request.Request(
    f'https://i.cnblogs.com/api/posts/{postId}',
    headers={'Cookie': cookie, 'Accept': 'application/json'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    bp = data['blogPost']

# 2. 修改需要变更的字段
bp['postBody'] = "修改后的正文"
bp['title'] = "修改后的标题"

# 3. POST 更新（与创建相同的端点，body 包含 id）
json_data = json.dumps(bp, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://i.cnblogs.com/api/posts',
    data=json_data,
    headers={
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-XSRF-TOKEN': xsrf
    },
    method='POST'
)
with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read().decode())
    print(f"更新成功: {result['id']}")
```

---

## 7. POST 请求字段详解

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | int | 更新时必填 | 文章ID，创建时不传 |
| `postType` | int | 是 | 固定 1（博客文章） |
| `accessPermission` | int | 是 | 固定 0（公开） |
| `title` | string | 是 | 文章标题 |
| `postBody` | string | 是 | Markdown 正文 |
| `categoryIds` | array | 否 | 个人分类ID数组 |
| `siteCategoryId` | int\|null | 否 | 网站分类ID |
| `blogTeamIds` | array | 是 | 固定 []（无团队博客） |
| `isPublished` | bool | 是 | True=发布，False=保存草稿 |
| `displayOnHomePage` | bool | 是 | 是否显示在博客首页 |
| `isAllowComments` | bool | 是 | 是否允许评论 |
| `includeInMainSyndication` | bool | 是 | 是否包含在RSS中 |
| `isPinned` | bool | 是 | 是否置顶 |
| `showBodyWhenPinned` | bool | 是 | 置顶时是否显示全文 |
| `isOnlyForRegisterUser` | bool | 是 | 是否仅登录用户可见 |
| `isUpdateDateAdded` | bool | 是 | 是否更新发布时间 |
| `entryName` | string | 是 | URL slug（英文+数字+连字符） |
| `description` | string | 是 | 摘要（显示在列表页） |
| `featuredImage` | string\|null | 否 | 封面图URL |
| `tags` | array | 是 | 标签数组（最多8个） |
| `isMarkdown` | bool | 是 | True=Markdown模式 |
| `isDraft` | bool | 是 | 是否草稿 |
| `isAigc` | bool | 是 | 是否AI生成内容 |
| `changePostType` | bool | 是 | 固定 False |
| `blogId` | int | 是 | 博客ID（861831） |
| `author` | string | 是 | 用户名（your_username） |
| `removeScript` | bool | 是 | 固定 False |
| `inSiteCandidate` | bool | 是 | 是否投稿首页候选区 |
| `inSiteHome` | bool | 是 | 是否投稿首页原创精品 |
| `autoDesc` | string\|null | 否 | 自动摘要（留null让系统生成） |
| `password` | string\|null | 否 | 密码保护（null=无密码） |
| `publishAt` | null | 是 | **必须为 null**，传 "" 会报错 |
| `changeCreatedTime` | bool | 是 | 固定 False |
| `canChangeCreatedTime` | bool | 是 | 固定 False |
| `isContributeToImpressiveBugActivity` | bool | 是 | 固定 False |
| `usingEditorId` | null | 否 | 固定 null |
| `sourceUrl` | string\|null | 否 | 原文链接（转载时用） |
| `clientInfo` | null | 否 | 固定 null |

### 关键避坑

- `publishAt` **必须为 `null`**，传空字符串 `""` 会报 `DateTime 转换错误`
- `autoDesc` 和 `password` 也用 `null`，不用 `""`
- `featuredImage` 用 `null`，不传空字符串
- 更新文章时，先 GET 获取完整 `blogPost` 对象，修改后整体 POST 回去

---

## 8. 发布后验证

```python
import json, urllib.request, re

cookie = open('/tmp/ck.txt').read()

req = urllib.request.Request(
    f'https://i.cnblogs.com/api/posts/{postId}',
    headers={'Cookie': cookie, 'Accept': 'application/json'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    bp = data['blogPost']
    body = bp.get('postBody', '')

# 验证项
print(f"IsPublished: {bp.get('isPublished')}")
print(f"InSiteCandidate: {bp.get('inSiteCandidate')}")
print(f"Tags: {bp.get('tags')}")
print(f"PostBody length: {len(body)}")

# 格式检查
h1 = [l for l in body.split('\n') if l.strip().startswith('# ') and not l.strip().startswith('## ')]
print(f"H1 titles: {len(h1)} {'PASS' if len(h1)==0 else 'FAIL'}")

imgs = re.findall(r'!\[.*?\]\((https?://.*?)\)', body)
print(f"Images: {len(imgs)} {'PASS' if len(imgs)>=2 else 'WARN'}")

entities = re.findall(r'&\w+;', bp.get('title', ''))
print(f"Title entities: {len(entities)} {'PASS' if len(entities)==0 else 'FAIL'}")

br = body.count('<br>')
print(f"BR tags: {br} {'PASS' if br==0 else 'FAIL'}")
```

---

## 9. 签名管理 API

签名通过系统 API 管理，不要在文章正文中放签名。

### 获取签名列表

```python
req = urllib.request.Request(
    'https://i.cnblogs.com/api/signature',
    headers={'Cookie': cookie, 'Accept': 'application/json'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
```

### 创建/更新签名（HTML格式）

```python
sig_data = {
    "id": None,  # None=新建，已有ID=更新
    "content": '<hr>\n<p><strong>作者：Morningstar202604</strong></p>\n<p>原文链接：<a href="{post_url}">{post_url}</a></p>\n<p>本文为博主原创文章，转载请注明出处。</p>',
    "isDefault": True
}

json_data = json.dumps(sig_data, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://i.cnblogs.com/api/signature',
    data=json_data,
    headers={
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-XSRF-TOKEN': xsrf
    },
    method='POST'
)
with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read().decode())
    print(f"签名ID: {result.get('id')}")
```

签名内容使用 HTML 标签（`<hr>`, `<p>`, `<strong>`, `<a>`），不用 Markdown。系统变量 `{author}` 和 `{post_url}` 会在文章显示时自动替换。

### 删除签名

```python
req = urllib.request.Request(
    f'https://i.cnblogs.com/api/signature/{sigId}',
    headers={
        'Cookie': cookie,
        'X-XSRF-TOKEN': xsrf
    },
    method='DELETE'
)
urllib.request.urlopen(req, timeout=15)
```

---

## 10. 完整 Python 示例

以下是一个完整的发文脚本，从提取 cookie 到验证发布：

```python
#!/usr/bin/env python3
"""博客园 API 发文完整示例"""

import json
import urllib.request
import urllib.parse

# === 1. 提取 Cookie ===
with open('auth-state.json') as f:
    auth_data = json.load(f)

cookie_parts = []
for c in auth_data['cookies']:
    if 'cnblogs' in c.get('domain', ''):
        cookie_parts.append(f"{c['name']}={c['value']}")
cookie = '; '.join(cookie_parts)

# === 2. 获取 XSRF Token ===
req = urllib.request.Request(
    'https://i.cnblogs.com/posts',
    headers={
        'Cookie': cookie,
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0'
    }
)
with urllib.request.urlopen(req, timeout=15) as resp:
    for sc in (resp.headers.get_all('Set-Cookie') or []):
        if 'XSRF' in sc:
            xsrf = urllib.parse.unquote(sc.split(';')[0].split('=', 1)[1])
            break

# === 3. 构造文章数据 ===
with open('article.md', 'r') as f:
    body = f.read()

post_data = {
    "postType": 1,
    "accessPermission": 0,
    "title": "文章标题",
    "postBody": body,
    "categoryIds": [2526541],
    "siteCategoryId": 108762,
    "blogTeamIds": [],
    "isPublished": True,
    "displayOnHomePage": True,
    "isAllowComments": True,
    "includeInMainSyndication": True,
    "isPinned": False,
    "showBodyWhenPinned": False,
    "isOnlyForRegisterUser": False,
    "isUpdateDateAdded": False,
    "entryName": "article-slug",
    "description": "摘要",
    "featuredImage": None,
    "tags": ["标签1", "标签2"],
    "isMarkdown": True,
    "isDraft": False,
    "isAigc": False,
    "changePostType": False,
    "blogId": 861831,
    "author": "your_username",
    "removeScript": False,
    "inSiteCandidate": True,
    "inSiteHome": False,
    "autoDesc": None,
    "password": None,
    "publishAt": None,
    "changeCreatedTime": False,
    "canChangeCreatedTime": False,
    "isContributeToImpressiveBugActivity": False,
    "usingEditorId": None,
    "sourceUrl": None,
    "clientInfo": None
}

# === 4. POST 创建文章 ===
json_data = json.dumps(post_data, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://i.cnblogs.com/api/posts',
    data=json_data,
    headers={
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-XSRF-TOKEN': xsrf
    },
    method='POST'
)

with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read().decode())
    print(f"发布成功！ID={result['id']}, URL={result['url']}")
```
