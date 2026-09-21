# 设计计划

## Token 系统

| 字段 | 值 |
|------|-----|
| subject | 开发者工具官网落地页——受众是重度终端用户（开发者/工程师），品牌性格"快、稳、不花哨"，视觉语言需匹配技术产品的冷峻质感 |
| palette | **黑板灰** #0D0F12 · **电路铜** #C49A6C · **终端绿** #4ADE80 · **冷光白** #E5E7EB · **深空蓝** #1E293B |
| type | 标题用等宽字体族（JetBrains Mono / Fira Code）——呼应代码气质；正文用无衬线族（Inter）——保证长文可读性 |
| layout | 左侧大标题+CTA的硬边布局，右侧代码预览区；所有分区明确边界（1px 分割线），无卡片式软容器；移动端单列堆叠 |
| principle | 页面本身就是个终端界面——用代码编辑器式的排版与节奏，把"速度感"通过字符间距、行高、等宽字体传递出来，而不是靠动画或渐变 |

```text
+--------------------------------------------------------------+
|  [logo]              nav links (等宽小字)    [cta btn]       |
+--------------------------------------------------------------+
|                                                              |
|   快、稳、不花哨          ████████████████████               |
|                                                              |
|   新一代开发者工具          [Install Now >]                  |
|   0.8s 启动 · 零依赖        性能测试数据（等宽数字阵列）      |
|                                                              |
|   ┌──────────────────────────────┐  ┌─────────────────────┐  |
|   │  $ npm install @fasttool/core │  │  功能矩阵（表格）   │  |
|   │  ✅ installed in 0.3s        │  │  ├ 编译速度 ────────┤  |
|   └──────────────────────────────┘  │  ├ 内存占用 ────────┤  |
|                                     │  └ 错误率 ─────────┘  │  |
|                                     └─────────────────────┘  |
+--------------------------------------------------------------+
|  © 2025 FastTool · Documentation · GitHub · License          |
+--------------------------------------------------------------+
```

---

## AI 味自查

| 清单命中 | 判定 | 处置 |
|----------|------|------|
| 万物皆圆角卡片 | 默认值 | **改为硬边**：所有分区用1px细线分隔，背景色块对比，无任何border-radius |
| 渐变色+玻璃态 | 默认值 | **完全移除**：只用纯色块，电路铜仅用于关键数据和高亮行 |
| 全大写小字眉标 | 默认值 | **删除**：眉标信息直接以等宽字体写入正文首句 |
| 对齐永远居中 | 默认值 | **保留部分居中**：仅开场口号居中（"扉页"感），其余全部左对齐——模仿代码编辑器的左对齐阅读流 |
| 每个元素都淡入上浮 | 默认值 | **限制动效**：页面加载时仅 CTA 按钮有0.2s 的"打字机"式逐字出现效果，其余全部静态 |
| 图标一律线性风格 | 默认值 | **保留混合**：功能矩阵用等宽字符绘制（▸ ○ —），不用图标库 |
| 背景全是纯白/纯黑 | 默认值 | **替换**：背景用黑板灰 #0D0F12，正文区用深空蓝 #1E293B 做层次区分 |

---

## 实现代码

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FastTool — 新一代开发者工具</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg-primary: #0D0F12;
    --bg-secondary: #1E293B;
    --text-primary: #E5E7EB;
    --text-muted: #94A3B8;
    --accent-copper: #C49A6C;
    --accent-green: #4ADE80;
    --border: #2A3341;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    --font-sans: 'Inter', -apple-system, sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-sans);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }

  /* ── Nav ── */
  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 48px;
    border-bottom: 1px solid var(--border);
    font-family: var(--font-mono);
    font-size: 13px;
    letter-spacing: 0.02em;
  }

  .logo {
    font-weight: 700;
    font-size: 16px;
    color: var(--accent-green);
    letter-spacing: 0.05em;
  }

  .nav-links {
    display: flex;
    gap: 32px;
    list-style: none;
  }

  .nav-links a {
    color: var(--text-muted);
    text-decoration: none;
    transition: color 0.15s;
  }

  .nav-links a:hover { color: var(--text-primary); }

  .btn-install {
    background: var(--accent-copper);
    color: var(--bg-primary);
    border: none;
    padding: 10px 24px;
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.02em;
  }

  .btn-install:hover { background: #d4aa7c; }

  /* ── Hero ── */
  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: calc(100vh - 73px);
    border-bottom: 1px solid var(--border);
  }

  .hero