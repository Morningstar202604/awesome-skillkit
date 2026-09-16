---
name: "zhihu-content-manager"
description: "知乎内容发布与管理自动化工具。支持文章发布、编辑、删除、草稿清理、话题标签管理、封面图上传、乱码检测与修复。当用户提到 知乎发文、知乎发布、知乎文章、知乎回答、知乎草稿、知乎专栏、知乎乱码、修复知乎内容、publish to zhihu、zhihu article、zhihu draft、zhihu column、fix zhihu mojibake 或任何涉及知乎内容管理的操作时触发。 Do NOT use for publishing to platforms other than zhihu.com."
license: Apache-2.0
compatibility: Requires network access to www.zhihu.com and valid session credentials in environment variables. Python 3.8+.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 知乎发文管理技能

基于 Playwright 浏览器自动化 + 站内 API 的知乎内容管理：发布/编辑/删除文章与回答、封面与插图上传、乱码检测修复、批量修复。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `zhihu_state.json` | 是 | 登录态 cookies，由用户本地浏览器登录后导出；路径可用 `ZHIHU_STATE_FILE` 覆盖（默认当前目录 `zhihu_state.json`），不入库 |
| Playwright + Chromium | 是 | `pip install playwright && playwright install chromium` |
| `ZHIHU_CHROME_PATH` | 否 | 指定 Chromium 可执行文件；缺省用 Playwright 自带浏览器 |
| 正文 HTML 文件 | 发布/编辑/修复必需 | 必须满足下文「平台硬性格式规范」，先过 lint |
| 封面图文件 | 发布必需 | jpg/png，建议 2K 分辨率、3:2 宽高比，压缩到 <2MB |
| article_id / answer_id | 编辑/删除/修复必需 | 从文章 URL `/p/{id}` 或创作中心获取 |

缺输入时一次性问齐：
「请一次性提供：① 任务类型（发布/编辑/删除/修乱码/批量修复）；② zhihu_state.json 路径；③ 正文 HTML 文件与封面图路径（发布时）；④ 目标 article_id/answer_id（编辑或删除时）。不逐条追问。」

## 前置自检

```bash
python3 --version                                                        # ≥ 3.8
python3 -c "import playwright; print('playwright-ok')"                    # Playwright 已装
python3 -c "from playwright.sync_api import sync_playwright; print('chromium-check')"  # 能导入
test -f zhihu_state.json && echo state-ok                                 # 登录态文件存在
python3 scripts/zhihu_html_lint.py --help > /dev/null && echo lint-ok     # 检查脚本可用
```

任一失败 → 修复（装依赖 / 导出登录态 / 补文件）→ 重跑，通过前 STOP，不进入发布步骤。

## 浏览器启动配置（所有任务的公共前置）

```python
import os
from playwright.sync_api import sync_playwright

CHROME_PATH = os.environ.get("ZHIHU_CHROME_PATH") or None  # None 时用 Playwright 自带 Chromium
STATE_FILE = os.environ.get("ZHIHU_STATE_FILE", "zhihu_state.json")

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

批量操作（获取→修复→发布→验证）必须在**同一个浏览器 session** 内完成，避免重复登录与状态丢失。

## 平台硬性格式规范

发布到知乎的 HTML 必须遵循（与风格无关，lint 会强制检查）：

| 元素 | 规范 |
|------|------|
| 段落 | `<p data-pid="X">内容</p>`；空行段落用 `<p data-pid="X"><br data-text="true"/></p>`（Draft.js 会剥离 `<p></p>`，导致段落挤在一起） |
| 标题 | `<h2>` / `<h3>`（中文编号如"一、""1.1"） |
| 引用 | `<blockquote data-pid="X">内容</blockquote>` |
| 代码块 | `<code>` 内所有 `<` `>` 转义为 `&lt;` `&gt;`，否则被浏览器当 HTML 标签吃掉 |
| 图片 | 必须 `<figure data-size="normal"><img src="URL"/></figure>` 包裹；**裸 `<img>` 会被过滤** |
| 粗体 | `<b>`，不要 `<strong>` |
| 列表 | `<ul><li>` |
| 公式 | 行内 `<span class="FormulaCSR" data-tex="LaTeX" data-eeimg="1">$LaTeX$</span>`；块级 `<p data-pid="X"><span class="FormulaCSR" data-tex="LaTeX" data-eeimg="2">$$LaTeX$$</span></p>` |

**绝对禁止**：裸 `<img>`、`<table>`（Draft.js 无法清除）、未转义尖括号、`<p></p>` 空段落。

## 工作流

### 步骤 1：发布前 lint 检查（必须全部通过）

```bash
python3 scripts/zhihu_html_lint.py article.html [--json] [--strict]
```

预期：退出码 0，无 error 级问题。
若失败：存在 error 时退出码 1，**禁止发布**；按「失败处置表」的 lint 代码修复后重跑。`--strict` 时 warning 也算失败。

### 步骤 2：发布新文章

```text
导航: https://zhuanlan.zhihu.com/write
  ↓
设置标题（React 兼容方式，直接传字符串，勿用 base64）:
  Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set.call(textarea, "标题")
  textarea.dispatchEvent(new Event('input', { bubbles: true }))
  ↓
上传封面（如需要）:
  找到 input[type="file"][accept*="image"] (通常是第1个或第2个)
  file_input.set_input_files("/path/to/cover.jpg")
  等待3秒
  清除弹窗: document.querySelectorAll('.Modal-backdrop, .Modal').forEach(el => el.remove())
  ↓
注入 HTML 内容（分块 paste，15000 字符/块）:
  for chunk in [html[i:i+15000] for i in range(0, len(html), 15000)]:
      if not first:
          定位编辑器末尾: focus() + selectAllChildren() + collapseToEnd()
      ClipboardEvent paste 注入:
          dt = new DataTransfer()
          dt.setData('text/html', chunk)
          dt.setData('text/plain', chunk)
          editor.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }))
      等待2秒
  ↓
验证预览包含中文字符（出现 Latin-1 乱码 → 停止，见失败处置表）
  ↓
点击"发布"按钮（先移除 Modal 遮罩）:
  document.querySelectorAll('.Modal-backdrop, .Modal').forEach(el => el.remove())
  遍历所有 button 找到 textContent.trim() === '发布' 并 click()
  ↓
添加话题标签（编辑页底部）:
  找到 placeholder 包含"话题"的 input，设置 value（如"编程"）
  从 Popover 建议列表精确匹配点击第一个
  ↓
确认发布: 点击"确认发布"或"确认"按钮
```

预期：跳转到新文章页 `/p/{id}`；记录该 ID 写入台账。
若失败：新文章 404 → 反垃圾系统暂时屏蔽，等待后重查（见失败处置表）。

专栏归属：新建文章时可在 /write 页面选择目标专栏；**已发布文章的专栏归属不可修改**（平台限制），换专栏 = 删旧文 → 新建 → 选新专栏 → 贴内容 → 发布。

### 步骤 3：编辑已发布文章

```text
导航: https://zhuanlan.zhihu.com/p/{id}/edit
  ↓
设置新标题（方式同步骤 2）
  ↓
上传新封面（如需要）
  ↓
替换内容:
  方式1（推荐）: selectAllChildren + paste 覆盖（不要先 clear!）
  方式2: Ctrl+A + Delete + paste
  ↓
验证预览
  ↓
点击"更新"按钮（先移除 Modal 遮罩）
```

预期：更新后等待约 90 秒缓存清除再验证。
若失败：预览正常但未保存 → 确认操作的是**文章**编辑页而非回答编辑页（回答编辑页 UI 更新无效，见步骤 4）。

### 步骤 4：更新回答内容（必须走 API）

回答更新**必须通过 API**，编辑器 UI 操作不会真正保存：

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

预期：返回 `ok: true`；等待约 90 秒缓存清除后验证。
若失败：status 403 → 触发反爬限流，等 2-5 分钟再试。

### 步骤 5：删除内容

文章删除**必须通过 UI**（API DELETE 始终返回 403）：

```text
导航: https://www.zhihu.com/creator/manage/creation/all
  ↓
找到文章卡片 → 点击"更多"按钮
  ↓
点击"删除"
  ↓
确认删除
```

回答删除：同样通过创作中心内容管理页面操作。
预期：列表中该条目消失。
若失败：找不到条目 → 刷新页面重查。

### 步骤 6：图片上传与 URL 构造

```text
在 /write 页面:
  找到 input[type="file"][accept*="image"] (index=1)
  设置文件路径（压缩到 <2MB）
  等待上传完成
  从编辑器 img 元素的 src 提取 hash
  构造公开 URL: https://pic1.zhimg.com/v2-{hash}_r.jpg
```

预期：构造出的 URL 可公开访问。
若失败：上传卡住 → 压缩图片后重试。

封面/插图生成：工具不限（文生图 API、本地工具均可），封面要求 2K 分辨率、3:2 宽高比、英文 prompt 描述场景风格；上传前用 PIL 压缩：

```python
PIL.Image.open('cover.png').convert('RGB').save('cover.jpg', 'JPEG', quality=75)  # 压缩到 <1MB
```

### 步骤 7：乱码检测与修复

检测：遍历内容文本，匹配连续 Latin-1 字符 `[\u00c0-\u00ff]{2,}`（乱码特征：`å` `ç` `è` `æ` 等）。

修复文章：进 `/p/{id}/edit` → 全选内容 + paste 覆盖正确 HTML → 点击更新。
修复回答：API PUT `/api/v4/answers/{id}` 传入正确 HTML → 等待约 90 秒缓存清除 → 验证。

### 步骤 8：批量文章修复工作流

```text
Phase 1: 获取所有文章 HTML（单浏览器 session）
  - 打开每篇文章页面，提取 .Post-RichText 或 .RichText 的 innerHTML
  - 保存到本地文件 old_articles/{id}_{title}.html
  - 分析格式：空行段落数、hr 分割线、table 标签、data-pid 完整性
Phase 2: 离线修复 HTML
  - 插入空行段落：在 </p> 后添加 <p data-pid="X"><br data-text="true"/></p>
  - 在 <h2> 前添加 <hr/>（如没有）；删除 table 标签；确保所有 <p> 有 data-pid
Phase 3: 批量更新到知乎（单浏览器 session）
  - 进入编辑页 /p/{id}/edit
  - 清除编辑器（innerHTML = '' 或 selectAllChildren + deleteFromDocument）
  - 分块 paste 注入 HTML（15000 字符/块）→ 点击"更新" → 等待8秒确认保存
  - 10-30 秒间隔后继续下一篇
Phase 4: 验证
  - 抽样检查 5-10 篇：段落间距（getBoundingClientRect）、乱码（Latin-1 字符）、图片完整性
```

## 反爬虫应对

触发「请求异常」（code:40362）时：
1. 等待 2-5 分钟
2. 使用真实 user_agent 配置
3. 启动参数加 `--disable-blink-features=AutomationControlled`
4. 注入 `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
5. 新建文章可能被反垃圾系统暂时屏蔽（显示 404），等待一段时间

## 平台铁律（经验教训合并，违反必出事故）

1. **不要用 base64 编码中文内容**传给 page.evaluate()——atob() 不支持 UTF-8，中文会变 Latin-1 乱码（如"学"变成 `å­¦`）；直接传字符串，Playwright 自动正确处理 UTF-8。
2. **不要用 API 发布/更新中文文章**——知乎 publish 端点有服务端编码 bug（ensure_ascii 与 HTML 实体编码都会把 UTF-8 中文存为 Latin-1 乱码）；文章走编辑器 paste，回答走 API PUT（回答内容是服务端接受的例外路径）。
3. **不要在回答编辑页通过 UI 更新**——Draft.js 行为不同，预览正常但实际未保存；回答必须 API PUT。
4. **不要在同一浏览器 session 中频繁调用 API**——批量 fetch 会触发反爬 403 限流；改用浏览器 DOM 提取或分时段操作。
5. **不要中途关闭浏览器 session**——批量操作在同一个 session 内完成。
6. 文章删除必须走 UI，API DELETE 返回 403。
7. 发布/更新后需等待约 90 秒缓存清除才能验证。
8. 超长文章（4万~6万字）分块通过 ClipboardEvent paste 注入。

## 发布质量验证（发布后执行）

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

| 评级 | 条件 | 处置 |
|------|------|------|
| A | 大间距占比>70% + BR空行>20个 | 通过 |
| B | 大间距占比>50% + BR空行>10个 | 通过 |
| C | 大间距占比>30% | 基本可用，建议修复 |
| D | 大间距占比<30% | 不合格，回到步骤 8 修复 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| E001 | 裸 `<img>`（会被过滤） | 用 `<figure>` 包裹 |
| E002 | 出现 `<table>`（Draft.js 无法清除） | 删除 table 或改用列表 |
| E003 | 空段落 `<p></p>`（会被剥离） | 换 `<p data-pid="X"><br data-text="true"/></p>` |
| E004 | `<code>` 块内未转义尖括号 | `<`/`>` 改为 `&lt;`/`&gt;` |
| E005 | Latin-1 乱码特征字符 | 内容已损坏，用正确 HTML 重新覆盖（步骤 7） |
| W001 | 使用了 `<strong>` 而非 `<b>` | 替换标签 |
| 正文出现 `å` `ç` `è` `æ` 等 | UTF-8 被错误解码（base64 或 API 发布中文） | 用 paste 注入正确 HTML 覆盖 |
| 正文缺 `#include <iostream>` 之类 | 代码块内尖括号未转义 | 转义后重发 |
| 发布后 404 | 反垃圾系统暂时屏蔽 | 等待后重查 |
| code:40362「请求异常」 | 反爬虫风控 | 按上文「反爬虫应对」处理 |
| 批量 fetch 返回 403 | API 限流 | 改用浏览器 DOM 提取，分时段操作 |

## 交付标准

- 成功定义：lint 退出码 0 → 发布/更新成功 → 质量评级 ≥ B（大间距占比>50%）→ 无乱码、图片完整。
- 产物命名：本地修复文件存 `old_articles/{id}_{title}.html`；封面 `cover.jpg`（<1MB）。
- 保存位置：专栏 ID 与已发布文章台账存 `references/account.local.json`（字段：`columns` 专栏名→专栏 ID；`published_articles` 系列→[{标题, 文章ID}]），发文成功后由流程追加。
- 验证完整性：发布/更新后等待 90 秒，抽样用「发布质量验证」脚本核对评级，并搜索 Latin-1 乱码字符。

## 参考

- `references/content-ops.md` —— 排版要求、视觉要求、内容风格、草稿箱盘点等**可自定义的内容运营策略**。首次使用复制为个人风格基线按账号定位修改；平台硬规则（本文件的 lint 部分）与之无关。
- `references/account.example.json` —— 台账模板。首次使用复制为同目录 `account.local.json` 并填入自己的数据（不入库）。
- `tests/test_zhihu_html_lint.py` —— lint 脚本单元测试，运行 `python -m unittest discover -s tests`。
