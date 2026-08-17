# 配图生成与上传

## 目录

1. [概述](#概述)
2. [配图风格规范](#1-配图风格规范)
3. [生成配图](#2-生成配图)
4. [上传到博客园图床](#3-上传到博客园图床)
5. [在文章中插入图片](#4-在文章中插入图片)
6. [完整流程示例](#5-完整流程示例)

---

## 概述

博客园文章配图分两步：
1. 用 `baidu-image-gen` 技能生成图片到本地
2. 用 Python urllib 直接 POST 上传到博客园图床获取 URL

上传方式有两种：
- **Python urllib 直接上传**（推荐）：无需浏览器，速度快，可靠
- **浏览器 base64 分块注入**（备用）：浏览器 session 有效时可用，较慢

---

## 1. 配图风格规范

| 规则 | 要求 |
|------|------|
| 数量 | 每篇 2 张 |
| 风格 | 暗色技术风（dark theme） |
| 背景色 | #0d1117（GitHub Dark） |
| 主色 | 绿色 #238636 + 蓝色 #58a6ff |
| 辅色 | 橙色 #f78166、紫色 #bc8cff（少量点缀） |
| 设计风格 | flat-design，无渐变，无3D效果 |
| 比例 | 3:2（1536x1024） |
| 文字 | 英文为主，关键中文可加 |
| 内容 | 第一张概念图/对比图，第二张数据图/趋势图 |

### 提示词模板

```
Dark theme technology illustration, background color #0d1117, 
flat design style, no gradient, no 3D effect.
Main colors: green #238636 and blue #58a6ff.
[具体内容描述]
Clean lines, minimal style, professional infographic look.
Aspect ratio 3:2.
```

---

## 2. 生成配图

使用 `baidu-image-gen` 技能：

```bash
# 步骤1：安全检查
cd /path/to/baidu-image-gen
python3 scripts/prompt_filter.py --prompt "你的图片描述"

# 步骤2：提交生成任务
python3 scripts/submit.py \
  --prompt "图片描述" \
  --model "dumate-image2.1" \
  --resolution "high" \
  --aspect_ratio "1536x1024" \
  --output "/path/to/output.png"

# 步骤3：轮询结果
python3 scripts/poll.py \
  --task_id "{task_id}" \
  --model "dumate-image2.1" \
  --output "/path/to/output.png"
```

### 注意事项

- 分辨率选 `high`，宽高比 `1536x1024`（3:2）
- 提示词用英文，描述要具体
- 如果提交时遇到 502，等几秒重试
- 生成后检查图片是否正常（文件大小 > 100KB）

---

## 3. 上传到博客园图床

### 方案A：Python urllib 直接上传（推荐）

无需浏览器，直接用 Python 上传：

```python
import urllib.request
import uuid
import os

cookie = open('/tmp/ck.txt').read()

def upload_image(image_path, cookie):
    """上传图片到博客园图床，返回URL"""
    filename = os.path.basename(image_path)
    
    # 构造 multipart/form-data
    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex[:16]
    
    with open(image_path, 'rb') as f:
        file_data = f.read()
    
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: image/png\r\n\r\n'
    ).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()
    
    req = urllib.request.Request(
        'https://upload.cnblogs.com/imageuploader/processupload',
        data=body,
        headers={
            'Cookie': cookie,
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://i.cnblogs.com/'
        },
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = resp.read().decode()
        return result

# 上传两张图片
for img_path in ['img1.png', 'img2.png']:
    result = upload_image(img_path, cookie)
    print(f"{img_path}: {result}")
```

成功响应：
```json
{"success":true,"message":"https://img2024.cnblogs.com/other/3237984/202608/XXXXXXXXX.png"}
```

失败响应：
```json
{"success":false,"message":"未登录，请先登录"}
```

### 方案B：浏览器 base64 分块注入（备用）

浏览器 session 有效时可用，详见旧版 `references/image-upload.md` 中的 base64 方案。此方案较慢，仅在 Python urllib 上传失败时作为 fallback。

### 上传失败处理

1. 返回"未登录" → Cookie 过期，需重新提取或提示用户登录
2. 返回"只能上传图片文件" → 检查 Content-Type 和文件名后缀
3. 超时 → 图片可能过大，尝试压缩后重传

---

## 4. 在文章中插入图片

### Markdown 语法

```markdown
![图片描述](https://img2024.cnblogs.com/other/...png)
```

### 插入位置

- **第一张**：开头引言后，第一个 `---` 分割线前
- **第二张**：正文中间，关键数据或对比内容后

### 插入方法

用 Python 的 `replace` 方法将图片 URL 插入 Markdown 正文：

```python
img1_url = "https://img2024.cnblogs.com/other/3237984/202608/...png"
img2_url = "https://img2024.cnblogs.com/other/3237984/202608/...png"

# 插入第一张图（开头引言后）
body = body.replace(
    "引言段落的最后一句话。\n\n---",
    "引言段落的最后一句话。\n\n![图片描述1](" + img1_url + ")\n\n---"
)

# 插入第二张图（正文中间）
body = body.replace(
    "关键数据段落的最后一句话。\n\n---",
    "关键数据段落的最后一句话。\n\n![图片描述2](" + img2_url + ")\n\n---"
)
```

### 关键避坑

- **replace 目标文本必须完全匹配**：包括标点符号、换行符、空格
- **匹配失败时先调试**：用 `body.find("目标文本")` 定位，检查实际内容
- **避免重复插入**：插入前检查图片 URL 是否已在 body 中
- **图片描述要有意义**：不用"image1"，用描述性文字

---

## 5. 完整流程示例

```python
#!/usr/bin/env python3
"""配图生成+上传+插入完整流程"""

import json
import urllib.request
import uuid
import os

# 1. 提取 Cookie
with open('auth-state.json') as f:
    auth_data = json.load(f)
cookie_parts = []
for c in auth_data['cookies']:
    if 'cnblogs' in c.get('domain', ''):
        cookie_parts.append(f"{c['name']}={c['value']}")
cookie = '; '.join(cookie_parts)

# 2. 上传图片函数
def upload_image(image_path, cookie):
    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex[:16]
    with open(image_path, 'rb') as f:
        file_data = f.read()
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{os.path.basename(image_path)}"\r\n'
        f'Content-Type: image/png\r\n\r\n'
    ).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()
    
    req = urllib.request.Request(
        'https://upload.cnblogs.com/imageuploader/processupload',
        data=body,
        headers={
            'Cookie': cookie,
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://i.cnblogs.com/'
        },
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode())
        if result.get('success'):
            return result['message']  # 图片URL
        else:
            raise Exception(f"Upload failed: {result.get('message')}")

# 3. 上传两张图片
img1_url = upload_image('img1-vs-battle.png', cookie)
img2_url = upload_image('img2-salary-compare.png', cookie)
print(f"Image 1: {img1_url}")
print(f"Image 2: {img2_url}")

# 4. 读取文章并插入图片
with open('article.md', 'r') as f:
    body = f.read()

body = body.replace(
    "引言结尾。\n\n---",
    "引言结尾。\n\n![描述1](" + img1_url + ")\n\n---"
)
body = body.replace(
    "数据段结尾。\n\n---",
    "数据段结尾。\n\n![描述2](" + img2_url + ")\n\n---"
)

# 5. 验证图片已插入
import re
imgs = re.findall(r'!\[.*?\]\((https?://.*?)\)', body)
print(f"Images in body: {len(imgs)}")
for img in imgs:
    print(f"  -> {img}")

# 6. 保存修改后的文章
with open('article-with-images.md', 'w') as f:
    f.write(body)
```
