# 视觉细节词库：光照 · 构图 · 焦段 · 材质 · 氛围（visual-detail-lexicon）

> 写图像 prompt 时按槽位查这张表。**光照比其他任何槽位都更能改变一张图**——同一主体，换光照=换情绪。
> 铁律：具体名词替换抽象形容词（`beautiful` → `soft rim light on hair`）；质量词（8K/masterpiece）2-3 个封顶，堆多反而掉权重。
> 模型差异见 [model-dialects.md](model-dialects.md)，本表是跨模型通用的细节层。

## 目录

- [一、光照词库（三层）](#一光照词库三层)——自然光 / 影棚光 / 光效与情绪
- [二、构图词库](#二构图词库)——景别 / 机位 / 构图法则
- [三、焦段与镜头感](#三焦段与镜头感一张词--一种透视性格)——一张词 = 一种透视性格
- [四、材质与微细节](#四材质与微细节beautiful-的替代品)——"beautiful" 的替代品
- [五、色彩方案词](#五色彩方案词)
- [六、氛围情绪词](#六氛围情绪词mood-槽位)——mood 槽位
- [七、静态图里的"动势"词](#七静态图里的动势词图不吵但要有风)——图不吵，但要有风
- [八、负面词与节制](#八负面词与节制)
- [九、场景模板](#九场景模板改四个括号就能用)——改四个括号就能用

## 一、光照词库（三层）

### 自然光

| 英文 | 中文 | 效果与情绪 | 何时用 |
|------|------|-----------|--------|
| `golden hour` | 黄金时刻（日落前后低角度暖光） | 暖、柔、最讨喜的人像光 | 人像、风景、怀旧 |
| `blue hour` | 蓝调时刻（日落后深蓝天光） | 冷、静谧、都市感 | 城市夜景、氛围片 |
| `overcast diffused light` | 阴天漫射光 | 均匀柔光无硬影 | 产品、肤色还原 |
| `dappled light through leaves` | 树叶间洒落的碎光 | 夏日、慵懒、电影感 | 户外、青春题材 |
| `harsh midday sun, strong shadows` | 正午硬光强影 | 力量、纪实、沙漠感 | 硬汉风格、街头 |
| `moonlight, cool blue tones` | 月光冷蓝 | 孤寂、悬疑 | 夜景、恐怖 |

### 戏剧光

| 英文 | 中文 | 效果与情绪 | 何时用 |
|------|------|-----------|--------|
| `chiaroscuro` | 明暗对照法（伦勃朗式强对比） | 油画感、神秘 | 肖像、静物 |
| `Rembrandt lighting` | 伦勃朗光（一侧脸亮，另颊三角光斑） | 经典人像标准 | 男性肖像、稳重感 |
| `rim lighting / backlit` | 轮廓光/逆光 | 主体镶发光边，与背景分离 | 剪发丝、氛围感 |
| `volumetric lighting, god rays` | 体积光/丁达尔光束 | 神圣、史诗 | 教堂、森林、废墟 |
| `silhouette` | 剪影 | 形状叙事、留白想象 | 日落、极简 |
| `lens flare` | 镜头光斑 | 电影感、不完美真实 | 追光镜头 |
| `[color] gel lighting` | 色片打光（如 `teal and orange gel`） | MV 感、赛博 | 时装、音乐 |

### 棚拍与人工光

| 英文 | 中文 | 效果与情绪 | 何时用 |
|------|------|-----------|--------|
| `studio lighting, three-point setup` | 三点布光 | 商业标准、干净 | 产品、证件照 |
| `softbox / octabox` | 柔光箱 | 大面积柔光，皮肤细腻 | 美妆、电商 |
| `neon lighting, colorful reflections` | 霓虹+彩色反射 | 夜生活、赛博朋克 | 街拍、海报 |
| `candlelight, warm flickering` | 烛光暖闪 | 私密、古典 | 餐厅、年代戏 |
| `bioluminescent glow` | 生物荧光 | 奇幻、深海 | 概念艺术 |
| `practical lights (screen glow, lamp)` | 画内光源 | 真实感、科技感 | 深夜办公、黑客 |

## 二、构图词库

| 英文 | 中文 | 效果 | 何时用 |
|------|------|------|--------|
| `rule of thirds` | 三分法 | 百搭不犯错 | 默认选项 |
| `centered composition, symmetrical` | 居中对称 | 庄严、强迫症舒适 | 建筑、Wes Anderson 风格 |
| `negative space on the left` | 左侧负空间 | 给标题/文案留位 | 海报、banner |
| `leading lines` | 引导线 | 视线被拉向主体 | 街道、桥梁、走廊 |
| `framed through the doorway` | 框中框 | 偷窥感、层次 | 叙事场景 |
| `foreground subject, background bokeh` | 前景实、背景虚 | 主体强调 | 人像、美食 |
| `bird's eye view / overhead` | 鸟瞰/俯拍 | 秩序、上帝视角 | 城市平铺、Flat Lay |
| `worm's eye view / low angle` | 虫瞰/仰拍 | 主体高大压迫 | 英雄、建筑 |
| `Dutch angle` | 倾斜构图 | 不安、动荡 | 悬疑、冲突 |
| `over-the-shoulder` | 过肩 | 对话代入 | 双人场景 |
| `clean sky area for headline` | 天空留白放标题 | 排版友好 | 广告合成 |

## 三、焦段与镜头感（一张词 = 一种透视性格）

| 英文 | 中文 | 透视性格 | 何时用 |
|------|------|---------|--------|
| `16mm wide angle` | 16mm 广角 | 边缘拉伸、场景包纳 | 环境叙事、室内 |
| `35mm lens, documentary feel` | 35mm 纪实 | 接近人眼、自然 | 街拍、日常 |
| `50mm lens` | 50mm 标准 | 中性无畸变 | 万能默认 |
| `85mm portrait, creamy bokeh` | 85mm 人像 | 面部无畸变+奶油虚化 | 人像主力 |
| `200mm telephoto, compressed perspective` | 200mm 长焦 | 空间压缩、背景糊成色块 | 街头偷感、动物 |
| `macro lens, extreme detail` | 微距 | 放大到眼可见纹理 | 水珠、昆虫、珠宝 |
| `tilt-shift miniature effect` | 移轴微缩 | 真实城市变模型 | 城市、创意 |
| `fisheye, distorted edges` | 鱼眼 | 边缘夸张弯曲 | 滑板、极限运动 |
| `anamorphic lens, oval bokeh` | 变形宽银幕 | 椭圆虚化+横向蓝线光斑 | 电影感拉满 |
| `shot on [Hasselblad / Sony A7III]` | 相机机身引用 | 暗示色彩科学与质感 | 写实人像、产品 |

## 四、材质与微细节（"beautiful" 的替代品）

材质词让 AI 知道表面"是什么做的"——这是照片感和塑料感的分水岭：

- 皮肤：`porcelain skin texture with visible pores` / `freckles, fine peach fuzz`
- 金属：`brushed aluminum` / `micro scratches on metal` / `oxidized copper patina`
- 木：`weathered oak, visible grain` / `cracked lacquer`
- 布：`linen with natural wrinkles` / `silk sheen` / `frayed denim edges`
- 纸：`paper fibers` / `letterpress debossing` / `watercolor bleed at the edges`
- 玻璃：`condensation droplets` / `refractions and caustics`
- 空气：`dust motes in air` / `volumetric fog` / `steam rising`
- 做旧：`fine film grain` / `subtle chromatic aberration` / `light leaks`
- 装饰：`intricate filigree` / `hand-stitched seams` / `enamel chips`

**堆叠公式**（一次叠四层，AI 越具体越听话）：
`材质（brushed aluminum）+ 年代（Art Deco 1920s）+ 色板（muted teal and copper）+ 环境（industrial loft with tall windows）`

## 五、色彩方案词

| 英文 | 中文 | 情绪 |
|------|------|------|
| `warm palette, amber and terracotta` | 暖色：琥珀+陶土 | 温暖、大地 |
| `cool blue and silver tones` | 冷调：蓝+银 | 科技、疏离 |
| `desaturated, muted tones` | 去饱和低纯度 | 苍凉、文艺 |
| `high saturation, vivid colors` | 高饱和鲜艳 | 活力、电商 |
| `monochromatic, shades of blue` | 单色系 | 极简、观念 |
| `pastel palette, soft pinks and creams` | 粉彩柔和 | 少女、治愈 |
| `neon palette on black` | 黑底霓虹 | 夜店、赛博 |
| `teal and orange grade` | 青橙调色 | 好莱坞大片默认色 |

## 六、氛围情绪词（mood 槽位）

`serene`（宁静）· `dramatic, intense`（戏剧张力）· `melancholic, nostalgic`（忧郁怀旧）· `mysterious, eerie`（神秘不安）· `romantic, warm`（浪漫温暖）· `futuristic, cold`（未来冷感）· `whimsical, dreamlike`（奇想梦境）· `gritty, raw`（粗粝真实）

## 七、静态图里的"动势"词（图不吵，但要有风）

静态图加动词性修饰，画面立刻活：

- `windswept hair`（风扬起发丝）
- `fabric billowing`（布料鼓荡）
- `water splashing, frozen mid-air`（水花凝固半空）
- `birds circling overhead`（鸟群盘旋）
- `steam rising from the cup`（杯口升腾热气）
- `leaves scattered mid-fall`（落叶悬空散落）

## 八、负面词与节制

- 排除用 `--no text, watermark, people, blur`（Midjourney）/ `negative_prompt` 字段（SD/Flux）
- 质量词封顶 2-3 个：`highly detailed` + `professional photography` 够了；`8K masterpiece award-winning ultra` 堆一起权重稀释
- 想要的写正向：`clear sky` 而非 `sky with no clouds`（模型容易漏掉 no）

## 九、场景模板（改四个括号就能用）

```
人像：[年龄特征] [发型], [材质细节皮肤], Rembrandt lighting, 85mm creamy bokeh, rule of thirds --ar 4:5
产品：[产品], [材质词], softbox studio lighting, isolated on [背景], sharp focus, e-commerce ready --ar 1:1
风景：[地点], [时间词 golden/blue hour], [天气], wide 16mm, leading lines, volumetric god rays --ar 16:9
海报：[主题], [风格词], centered composition, negative space top for headline, [色板] --ar 2:3
头像：professional headshot, [表情], plain light gray background, soft studio light --ar 1:1
```
