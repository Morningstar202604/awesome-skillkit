---
name: "ai-cover-generator"
description: "技术文章封面图/配图生成。对接本地图片生成服务（127.0.0.1:30080，GPT Image 2 模型）：提交文生图任务、轮询状态、下载结果、可选 PIL 压缩为 <1MB JPG 供平台上传。内置平台尺寸约束校验（16倍数、宽高比、总像素）。当用户提到生成封面图、文章配图、给文章加图时使用。默认 dry-run，服务不可达时报错而非伪造结果。"
---

# AI 封面图生成 Skill

## compatibility
- Python 3.8+（标准库即可运行；`--jpg` 压缩功能需 Pillow）
- 本地图片服务运行于 `http://127.0.0.1:30080`（可用环境变量 `IMAGE_API_BASE` 覆盖）

## 服务契约

与本地 ai-image-gen 服务完全一致：

- **提交**：`POST /api/image/generate`
  `{"model":"gpt-image-2","prompt":"...","params":{"size":"1792x1024","quality":"auto","n":1}}`
- **轮询**：`GET /api/image/status?task_id=...`
  `is_final=true && state=="success"` 时 `result_url` 为下载地址
- **尺寸规则**：宽高均为 16 的倍数；宽高比 1:3~3:1；总像素 655360~8294400（脚本提交前会校验）

## 使用

### 1. 先看请求计划（默认 dry-run）

```bash
python3 scripts/generate_cover.py --prompt "..." --size 1536x1024
```

### 2. 提交并等待完成

```bash
python3 scripts/generate_cover.py --execute \
  --prompt "Dark tech blog cover, isometric illustration of publish pipelines across platforms, flat design, #0d1117 background, green #238636 and blue #58a6ff accents" \
  --size 1536x1024 --out cover.png --jpg --timeout 180
```

- `--jpg`：额外用 PIL 压缩出 <1MB 的 JPG（知乎/公众号上传要求小体积）
- 服务不可达 → 明确报错 exit 1，不会假装成功

### 3. Prompt 风格模板（配合各平台规范）

| 平台 | 建议 prompt 要素 | 尺寸 |
|------|------------------|------|
| 博客园 | 暗色 #0d1117 背景 + #238636/#58a6ff 点缀，flat-design 无渐变 | 1536x1024 (3:2) |
| 知乎 | 主题场景风格插画，避免纯渐变 PPT 风 | 1536x1024 |
| 公众号 | 900x383 头图比例附近取整到16倍数（如 896x384） | 896x384 |

英文 prompt 更稳：主体 + 风格 + 光影 + 构图 + 配色。

## 与其他技能的联动

- `cnblogs-skill` / `zhihu-content-manager` 的发文流程中「生成配图」一步即调用本技能
- 生成的 JPG 路径直接传给对应平台的图片上传步骤
