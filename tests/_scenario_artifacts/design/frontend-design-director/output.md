收到 brief，输入已齐全，开工。

---

## 步骤 1：设计计划

**主题提炼**

重度终端用户 = 开发者/工程师。他们不看"营销话术"，看数字、看参数、看 benchmark。品牌想传达的「快、稳、不花哨」不是口号，是工程信仰——这个页面本身就应该像他们用的工具：执行、静默、结果导向。

- **材料与触感**：冷金属 + 代码终端 + 性能仪表。不是温暖的手作感，而是精密仪器。
- **使用状态**：用户在评估是否接入自己的生产环境，心里有戒备心（"又一个吹牛的 SaaS"）。页面要像一份技术文档——证据先行，废话归零。
- **现成素材**：benchmark 数字、延迟毫秒数、吞吐量曲线——这些就是视觉资产。

```markdown
## Design Plan
- subject:   开发者工具落地页；受众=重度终端用户；核心信息=快、稳、不花哨；决策场景=生产环境接入评估
- palette:   深渊黑 #0A0E17 · 终端绿 #2ECC71 · 铝银 #C4CBD6 · 警告琥珀 #E8A838 · 极白 #F4F6F9
- type:      标题族：JetBrains Mono（等宽，代码体感，大字号做视觉骨架）；正文族：Inter（系统级清晰，无装饰）
- layout:    单栏纵向，全宽 hero + 参数区块，无容器卡片；左对齐为主，关键数字跨全宽居中放大；移动端保持等宽字可识别
- principle: 页面本身是"证据展示"：数字和 benchmark 是主角，UI 元素隐退；任何装饰性元素必须有工程意义
```

```text
+--------------------------------------------------------------+
|  [品牌]  终端绿 |  参数  |  文档  |  [接入]                    |
+--------------------------------------------------------------+
|                                                              |
|   启动到就绪                                            0.8ms  |
|   [ JetBrain Mono 超大字号跨全宽 ]                           |
|                                                              |
|   不是宣传语，是第一条 benchmark。                            |
|   第二行参数在下一屏继续展开。                                |
|                                                              |
+--------------------------------------------------------------+
|   ────────────────────────────────────────────────────────    |
|   LATENCY    THROUGHPUT    UPTIME    ERROR RATE               |
|   0.8ms      120k/s       99.99%     0.001%                   |
|   [等宽数字，铝银色，无容器包围]                              |
+--------------------------------------------------------------+
|   代码片段 / 集成示例（终端风格背景，终端绿光标的闪烁点）      |
|   $ install tool@latest                                    |
|   $ run benchmark                                        |
+--------------------------------------------------------------+
|   极简 footer：文档链接 | GitHub | Changelog                  |
+--------------------------------------------------------------+
```

---

## 步骤 2：默认味自查

对照 AI 设计特征清单逐条过：

| 清单命中 | 判定 | 处置 |
|----------|------|------|
| 万物皆圆角卡片容器 | 默认值 | 全部砍掉，区块之间用细分隔线或留白呼吸，无 container padding 包裹 |
| 渐变背景装饰（hero 区蓝紫渐变） | 默认值 | 换为深渊黑纯色背景，hero 唯一的"光"来自终端绿高亮的数字 |
| 全大写小字眉标（"TRUSTED BY 10K+ DEVS"） | 默认值 | 删除；把数字直接变成主视觉（"120k/s throughput"本身就是证据，不需要标语包装） |
| 英雄区人物/插画插图 | 默认值 | 删除；重度终端用户不需要情感化插图，需要的是参数 |
| 每个功能区块同款淡入上浮动画 | 默认值 | 取消全页滚动动画；唯一动效 = 终端光标闪烁 + benchmark 数字从 0 计数到目标值（一次编排，执行后立即停） |
| 两栏图文交替布局 | 保留 | 单栏纵向更适合"读文档"的心智模型；不强行拆两栏 |
| 导航悬停下划线动效 | 保留 | 简单即可，但颜色用铝银而非品牌绿（品牌绿留给数据，不浪费在导航上） |
| 按钮大面积渐变色 | 默认值 | "接入"按钮改为终端绿实心矩形，无渐变无阴影，hover 仅变深一级色度 |

**自查结论**：替换了 6 处默认值，保留了 2 处合理选择（单栏布局、导航下划线）。计划已足够反模板，进入实现。

---

## 步骤 3：实现

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>工具名称 — 快、稳、不花哨</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --black: #0A0E17;
      --green: #2ECC71;
      --silver: #C4CBD6;
      --amber: #E8A838;
      --white: #F4F6F9;
      --green-dim: #1A9D5C;
      --border: #1E2638;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--black);
      color: var(--silver);
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }

    /* 导航：极简，铝银，无多余动效 */
    nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 40px;
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      background: rgba(10, 14, 23, 0.95);
      backdrop-filter: blur(4px);
      z-index: 100;
    }

    .brand {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      font-size: 18px;
      color: var(--white