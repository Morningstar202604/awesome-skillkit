---
name: "zhihu-content-manager"
description: "知乎内容发布与管理自动化工具。支持文章发布、编辑、删除、草稿清理、话题标签管理、封面图上传、乱码检测与修复。当用户提到知乎发文、知乎发布、知乎文章、知乎回答、知乎草稿、知乎专栏、知乎乱码、修复知乎内容或任何涉及知乎内容管理的操作时触发。"
---

# 知乎发文管理 Skill

> 原 `## name` / `## description` 小节已上移为 YAML frontmatter（skills 规范要求）。

## compatibility
- Python 3.8+ with playwright
- Chromium browser (路径: /app/chromium-1224/chrome-linux64/chrome)
- zhihu_state.json (知乎登录态cookies文件)

---

## 核心工作流

### 1. 环境准备

```python
import sys
sys.path.insert(0, '/tmp/.pip-global/lib/python3.12/site-packages')
from playwright.sync_api import sync_playwright

CHROME_PATH = '/app/chromium-1224/chrome-linux64/chrome'
STATE_FILE = 'zhihu_state.json'
```

启动浏览器配置：
```python
browser = p.chromium.launch(
    executable_path=CHROME_PATH,
    headless=True,
    args=[
        '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled'
    ]
)
context = browser.new_context(
    storage_state=STATE_FILE,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport={'width': 1920, 'height': 1080},
    locale='zh-CN'
)
context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
page = context.new_page()
```

### 2. HTML内容规范

发布到知乎的HTML必须遵循以下格式：

**段落**：`<p data-pid="X">内容</p>`
**标题**：`<h2>` / `<h3>`（中文编号如"一、""1.1"）
**引用**：`<blockquote data-pid="X">内容</blockquote>`
**代码块**：`<code>` 标签内所有 `<` `>` 必须转义为 `&lt;` `&gt;`
**图片**：必须用 `<figure data-size="normal"><img src="URL"/></figure>` 包裹
**粗体**：`<b>`，不要用 `<strong>`
**列表**：`<ul><li>` 用于结构化知识
**公式**：行内 `<span class="FormulaCSR" data-tex="LaTeX" data-eeimg="1">$LaTeX$</span>`，块级 `<p data-pid="X"><span class="FormulaCSR" data-tex="LaTeX" data-eeimg="2">$$LaTeX$$</span></p>`

**绝对禁止**：裸 `<img>` 标签（会被过滤）、`<table>`（Draft.js无法清除）、未转义的尖括号

### 3. 发布新文章

```
导航: https://zhuanlan.zhihu.com/write
  ↓
设置标题（React兼容方式）:
  Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set.call(textarea, "标题")
  textarea.dispatchEvent(new Event('input', { bubbles: true }))
  ↓
上传封面:
  找到 input[type="file"][accept*="image"] (通常是第1个或第2个)
  file_input.set_input_files("/path/to/cover.jpg")
  等待3秒
  清除弹窗: document.querySelectorAll('.Modal-backdrop, .Modal').forEach(el => el.remove())
  ↓
注入HTML内容（分块paste）:
  chunk_size = 15000
  for chunk in [html[i:i+chunk_size] for i in range(0, len(html), chunk_size)]:
      if not first:
          定位到编辑器末尾: focus() + selectAllChildren() + collapseToEnd()
      ClipboardEvent paste注入:
          dt = new DataTransfer()
          dt.setData('text/html', chunk)
          dt.setData('text/plain', chunk)
          editor.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }))
      等待2秒
  ↓
验证预览包含中文字符
  ↓
点击"发布"按钮（绕过Modal）:
  document.querySelectorAll('.Modal-backdrop, .Modal').forEach(el => el.remove())
  遍历所有button找到textContent.trim() === '发布' 的并click()
  ↓
添加话题标签（编辑页底部）:
  找到placeholder包含"话题"的input
  设置value为"编程"或相关话题
  从Popover建议列表精确匹配点击第一个
  ↓
确认发布: 点击"确认发布"或"确认"按钮
```

**关键注意**：
- **绝对不要用base64编码中文内容**传给page.evaluate()——JavaScript的atob()不支持UTF-8解码，会导致中文变成Latin-1乱码（如"学"变成`å­¦`）
- **直接传字符串参数即可**，Playwright会自动正确处理UTF-8

### 4. 编辑已发布文章

```
导航: https://zhuanlan.zhihu.com/p/{id}/edit
  ↓
设置新标题
  ↓
上传新封面（如需要）
  ↓
替换内容:
  方式1（推荐）: selectAllChildren + paste覆盖（不要先clear!）
  方式2: Ctrl+A + Delete + paste
  ↓
验证预览
  ↓
点击"更新"按钮（绕过Modal）
```

### 5. 更新回答内容（API方式）

回答更新**必须通过API**，编辑器UI操作不会真正保存：

```python
page.evaluate(f"""async () => {{
    const resp = await fetch('/api/v4/answers/{answer_id}', {{
        method: 'PUT',
        headers: {{
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }},
        body: JSON.stringify({{
            content: "HTML内容",
            content_type: 'text/html'
        }})
    }});
    return {{ status: resp.status, ok: resp.ok }};
}}""")
```

### 6. 删除内容

**文章删除**（必须通过UI，API DELETE返回403）：
```
导航: https://www.zhihu.com/creator/manage/creation/all
  ↓
找到文章卡片 → 点击"更多"按钮
  ↓
点击"删除"
  ↓
确认删除
```

**回答删除**：同样通过创作中心内容管理页面操作。

### 7. 乱码检测与修复

**检测方式**：遍历所有内容，检查文本中是否包含连续的Latin-1字符（`[\u00c0-\u00ff]{2,}`）

**修复文章**：
1. 进入编辑页 `/p/{id}/edit`
2. 全选内容 + paste覆盖正确HTML
3. 点击更新

**修复回答**：
1. API PUT `/api/v4/answers/{id}` 传入正确HTML
2. 等待约90秒缓存清除
3. 验证

### 8. 图片上传

```
在/write页面:
  找到 input[type="file"][accept*="image"] (index=1)
  设置文件路径 (压缩到<2MB)
  等待上传完成
  从编辑器img元素的src提取hash
  构造公开URL: https://pic1.zhimg.com/v2-{hash}_r.jpg
```

### 9. 专栏归属

- 新建文章时可在/write页面选择目标专栏
- **已发布文章的专栏归属不可修改**（知乎平台限制）
- 如需更改，只能：删除旧文章 → 新建文章 → 选择新专栏 → 粘贴内容 → 发布

### 10. 反爬虫应对

触发"请求异常"（code:40362）时的处理：
1. 等待2-5分钟
2. 使用真实user_agent配置
3. 添加 `--disable-blink-features=AutomationControlled`
4. 注入 `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
5. 新创建的文章可能被反垃圾系统暂时屏蔽（显示404），需等待一段时间

---

---

## 发布风格与质量标准

### 排版要求
- **万字长文**：每篇文章7000-10000字，内容丰富深入
- **多级标题**：h2大章节带中文编号（如"一、""二、"），h3小节带数字编号（如"1.1""1.2"）
- **章节分割线**：大章节之间用 `<hr/>` 分隔，视觉上清晰分层
- **段落间距**：自然段落之间有空行，引用块与正文之间有空行，层次丰富
- **列表结构**：用 `<ul><li>` 列出结构化知识点、步骤、对比项
- **引用块**：用 `<blockquote>` 包裹名言、重要结论、历史背景
- **代码块**：代码示例用 `<code>` 包裹，必须转义尖括号；长代码块用 `<pre>`
- **粗体强调**：关键术语、核心概念、重要数字用 `<b>` 加粗

### 视觉要求
- **封面图**：主题场景风格（如"复古机械人偶变现代AI"、"机器人侦探监控墙"），非纯渐变PPT风
- **正文插图**：每篇3-5张，均匀穿插在章节之间，内容与章节主题匹配
- **图片格式**：`<figure data-size="normal"><img src="URL" data-caption="说明"/></figure>`
- **公式**：行内用 `<span class="FormulaCSR" data-eeimg="1">$...$</span>`，块级用 `<p>` + `data-eeimg="2"`

### 内容风格
- **故事性开头**：每篇文章以历史故事、场景描写或引人思考的问题开头
- **生动比喻**：用日常类比解释技术概念（如"AI Agent像能帮你干活的助理"）
- **历史背景**：技术演进要有时间线、人物、关键事件
- **实战导向**：每篇都要有代码示例、应用场景、常见误区
- **层次递进**：从基础概念 → 核心原理 → 实战应用 → 进阶技巧
- **结尾升华**：总结核心价值，给出行动建议或学习路径

### 质量标准
- 0乱码、0未转义尖括号、0裸img标签
- 标题层次清晰，无空章节
- 代码可运行，注释完整
- 图片版权安全（用文生图生成）

---

## 草稿管理流程

### 草稿箱盘点
```
1. 访问 https://www.zhihu.com/creator/manage/creation/all
2. 点击"草稿箱"标签
3. 滚动加载所有草稿
4. 对每个草稿判断：
   - 纯图片无文字 → 删除
   - 内容<100字 → 删除
   - 已有已发布版本 → 删除
   - 有实质内容但重复 → 只留最新，其余删除
   - 有实质内容且未发布 → 评估润色发布
```

### 内容润色流程
对于有价值但质量不达标的草稿：
1. 获取完整HTML内容
2. 检查结构：标题层次、段落间距、代码完整性
3. 扩充内容：补充历史背景、增加代码示例、添加应用场景
4. 统一风格：按排版要求和内容风格规范化
5. 生成封面图和正文插图
6. 发布到目标专栏

---

## 完整经验教训

### 核心发现：空行段落方案（最重要！）

**知乎Draft.js编辑器会剥离空段落`<p></p>`**，导致发布后所有段落挤在一起。解决方案：

```html
<!-- 错误：被Draft.js删除，发布后间距消失 -->
<p data-pid="X"></p>

<!-- 正确：保留为26px高度的空白块，产生段落间距 -->
<p data-pid="X"><br data-text="true"/></p>
```

**验证方法**：发布后检查文章页面，用浏览器dev tools查看段落间距，应出现大量`height: 26px`的空白段落。

### 绝对禁止
1. **不要用base64编码中文内容**——atob()不支持UTF-8，中文会变成乱码
2. **不要用API发布/更新中文文章**——知乎publish端点有服务端编码bug，无论ensure_ascii=True还是HTML实体编码都会把UTF-8中文存为Latin-1乱码
3. **不要在回答编辑页通过UI更新**——Draft.js在回答编辑页与文章编辑页行为不同，selectAll+paste+click"更新"预览正常但实际未保存到服务器
4. **不要在同一个浏览器session中频繁调用API**——fetch('/api/articles/{id}')批量获取会触发知乎反爬虫，返回403限流。应通过浏览器页面DOM提取HTML，或分时段操作
5. **不要中途关闭浏览器session**——批量操作（获取→修复→发布→验证）应在同一个浏览器session中完成，避免重复登录和状态丢失

### 必须遵守
6. 代码块中的 `<` `>` 必须转义为 `&lt;` `&gt;`，否则被浏览器当HTML标签吃掉
7. 图片必须用 `<figure>` 包裹，不能用裸 `<img>`
8. 不要用 `<table>` 标签，Draft.js编辑器无法清除table
9. 文章删除必须通过UI（创作中心→内容管理），API DELETE始终返回403
10. 回答更新必须通过API PUT，UI操作不保存
11. 发布/更新后需等待约90秒缓存清除才能验证
12. 超长文章（4万~6万字）分块通过ClipboardEvent paste注入
13. **段落间距方案**：使用`<p data-pid="X"><br data-text="true"/></p>`作为段落分隔，每1-2句话后插入空行段落

### 批量文章修复工作流

```
Phase 1: 获取所有文章HTML（单浏览器session）
  - 打开每篇文章页面
  - 提取 .Post-RichText 或 .RichText 的 innerHTML
  - 保存到本地文件 old_articles/{id}_{title}.html
  - 分析格式：空行段落数、hr分割线、table标签、data-pid完整性

Phase 2: 离线修复HTML
  - 插入空行段落：在</p>后添加<p data-pid="X"><br data-text="true"/></p>
  - 添加hr分割线：在<h2>前添加<hr/>（如没有的话）
  - 删除table标签
  - 确保所有<p>有data-pid

Phase 3: 批量更新到知乎（单浏览器session）
  - 进入编辑页 /p/{id}/edit
  - 清除编辑器（innerHTML = '' 或 selectAllChildren + deleteFromDocument）
  - 分块paste注入HTML（15000字符/块）
  - 点击"更新"按钮
  - 等待8秒确认保存
  - 10-30秒间隔后继续下一篇

Phase 4: 验证
  - 抽样检查5-10篇文章
  - 检查段落间距（浏览器getBoundingClientRect）
  - 检查乱码（搜索Latin-1字符）
  - 检查图片完整性
```

### 封面图和插图生成方案

使用 baidu-image-gen skill：
```bash
python3 scripts/submit.py \
  --prompt "高质量的英文文生图prompt，包含主题、风格、光影、构图" \
  --model dumate-image2.1 \
  --resolution 2K \
  --aspect_ratio 3:2 \
  --output cover.png
```

- 2K分辨率，3:2宽高比
- 英文prompt，详细描述场景和风格
- PIL压缩到<1MB后上传知乎
- 压缩脚本：PIL.Image.open().convert('RGB').save('cover.jpg', 'JPEG', quality=75)

### 文章质量评级标准

发布后通过浏览器验证段落间距质量：

```javascript
// 在文章页面执行
const blocks = document.querySelectorAll('.Post-RichText p, .Post-RichText h2, .Post-RichText h3');
let largeGaps = 0;
let prevBottom = 0;
for (const block of blocks) {
    const rect = block.getBoundingClientRect();
    const gap = prevBottom > 0 ? rect.top - prevBottom : 0;
    if (gap > 30) largeGaps++;
    prevBottom = rect.bottom;
}
// largeGaps / totalBlocks > 0.5 表示间距良好
```

| 评级 | 条件 | 说明 |
|------|------|------|
| A | 大间距占比>70% + BR空行>20个 | 优秀，非常疏朗 |
| B | 大间距占比>50% + BR空行>10个 | 良好，符合要求 |
| C | 大间距占比>30% | 合格，基本可用 |
| D | 大间距占比<30% | 不合格，需修复 |

### 专栏与文章台账（本地）

专栏 ID 和已发布文章 ID 属于账号数据，**不随本技能分发**，存于 `references/account.local.json`：

| 字段 | 说明 |
|------|------|
| `columns` | 专栏名 → 专栏 ID |
| `published_articles` | 系列 → [{标题, 文章ID}] 运营台账 |

首次使用：复制 `references/account.example.json` 为 `account.local.json` 并填入你自己的数据；发文成功后由流程负责追加台账。

**注意**：已发布文章的专栏归属不可修改（知乎平台限制），换专栏 = 删旧文 → 新建 → 选新专栏 → 贴内容 → 发布。

### 常见错误模式
- 乱码特征：`å` `ç` `è` `æ` `¼` `½` `¾` 等Latin-1字符——表示UTF-8被错误解码
- 尖括号被吃：`#include `（缺少`<iostream>`）——表示代码块内未转义
- 发布后显示404——反垃圾系统暂时屏蔽，等待即可
- 空行段落被删除——使用了`<p></p>`而不是`<p><br data-text="true"/></p>`
- API限流——短时间内大量API请求（fetch），改用浏览器DOM操作
