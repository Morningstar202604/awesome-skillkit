---
name: "ai-cover-generator"
description: "技术文章封面图/配图生成。对接本地图片生成服务（127.0.0.1:30080，GPT Image 2 模型）：提交文生图任务、轮询状态、下载结果、可选 PIL 压缩为 <1MB JPG 供平台上传。内置平台尺寸约束校验（16倍数、宽高比、总像素）。当用户提到生成封面图、文章配图、给文章加图时使用。默认 dry-run，服务不可达时报错而非伪造结果。 何时使用：发文流程里需要封面图或正文配图时。触发场景（中/英）：生成封面图 / 文章配图 / 给文章加图 / 生成题图 / generate a cover image / create a blog illustration。排除项：不生成视频封面与动图，不做图片裁剪、修图与 OCR（交给本地图像工具）。 Use when the user asks 生成封面图 / 文章配图 / 给文章加图 / 生成题图 / generate a cover image / create a blog illustration. Do NOT use when the task is cropping or editing existing images, OCR, or video cover generation."
license: Apache-2.0
compatibility: Python 3.8+（标准库即可运行；`--jpg` 压缩功能需 Pillow）
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: writing/assets
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# AI 封面图生成技能

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| prompt | 是 | `--prompt`，英文更稳：主体 + 风格 + 光影 + 构图 + 配色 |
| 尺寸 | 否 | `--size WxH`，须满足 16 倍数、宽高比 1:3~3:1、总像素 655360~8294400 |
| 画质 | 否 | `--quality auto/high/medium/low`，缺省 `auto` |
| 输出路径 | 否 | `--out cover.png`；不传则由脚本决定落盘位置 |
| 是否压 JPG | 否 | `--jpg`，额外用 PIL 压缩出 <1MB 的 JPG 供平台上传 |
| 轮询超时 | 否 | `--timeout`，缺省 180 秒 |

缺输入时一次性问齐：「请提供：① 图片描述（或直接说要什么风格）② 目标平台与尺寸 ③ 是否需要 <1MB 的 JPG。默认：`--size 1536x1024`、`--quality auto`、dry-run。」

## 前置自检

```bash
python3 --version                                    # 预期 >= 3.8
test -f scripts/generate_cover.py && echo SCRIPT-OK  # 预期打印 SCRIPT-OK
python3 -c "import PIL; print('PIL-OK')" 2>/dev/null || echo "PIL 缺失：仅影响 --jpg 压缩"
curl -s -o /dev/null -w '%{http_code}\n' "${IMAGE_API_BASE:-http://127.0.0.1:30080}/api/image/status"
```

- 预期：出现 `SCRIPT-OK`；否则技能包不完整，STOP 并提示重装技能包。
- `PIL` 缺失不影响出图，只是加 `--jpg` 时会失败。
- 服务探测返回 4xx 属正常（说明网关在跑、只是参数为空）；返回 `000` 说明服务不可达 → 提示用户启动服务，STOP，**不要伪造结果**。

## 工作流

### 步骤 1：先看请求计划（默认 dry-run）

```bash
python3 scripts/generate_cover.py --prompt "..." --size 1536x1024
```

预期：打印提交计划（端点、prompt、size、params）与尺寸校验结论，**不联网**。

### 步骤 2：提交并等待完成

```bash
python3 scripts/generate_cover.py --execute \
  --prompt "Dark tech blog cover, isometric illustration of publish pipelines across platforms, flat design, #0d1117 background, green #238636 and blue #58a6ff accents" \
  --size 1536x1024 --out cover.png --jpg --timeout 180
```

预期：提交任务 → 轮询至 `is_final=true && state=="success"` → 下载到 `--out`；产出非空 PNG，加 `--jpg` 时同目录另有 <1MB JPG。

- `--jpg`：额外用 PIL 压缩出 <1MB 的 JPG（知乎/公众号上传要求小体积）
- 服务不可达 → 明确报错 exit 1，不会假装成功

### 步骤 3：按平台规范选 Prompt 与尺寸

| 平台 | 建议 prompt 要素 | 尺寸 |
|------|------------------|------|
| 博客园 | 暗色 #0d1117 背景 + #238636/#58a6ff 点缀，flat-design 无渐变 | 1536x1024 (3:2) |
| 知乎 | 主题场景风格插画，避免纯渐变 PPT 风 | 1536x1024 |
| 公众号 | 900x383 头图比例附近取整到16倍数（如 896x384） | 896x384 |

英文 prompt 更稳：主体 + 风格 + 光影 + 构图 + 配色。

## 服务契约

与本地 ai-image-gen 服务完全一致：

- **提交**：`POST /api/image/generate`
  `{"model":"gpt-image-2","prompt":"...","params":{"size":"1792x1024","quality":"auto","n":1}}`
- **轮询**：`GET /api/image/status?task_id=...`
  `is_final=true && state=="success"` 时 `result_url` 为下载地址
- **尺寸规则**：宽高均为 16 的倍数；宽高比 1:3~3:1；总像素 655360~8294400（脚本提交前会校验）

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--prompt` | 字符串 | 图片描述，英文更稳 |
| `--size` | `WxH` | 须过 16 倍数/比例/总像素三道校验 |
| `--quality` | `auto`/`high`/`medium`/`low` | 画质档位，缺省 `auto` |
| `--out` | 路径 | 图片落盘位置 |
| `--jpg` | 标志 | 额外压缩出 <1MB JPG（需 Pillow） |
| `--execute` | 标志 | 不加则只打印计划，不联网 |
| `--timeout` | 秒 | 轮询超时，缺省 180 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 服务不可达，exit 1 | 本地图片服务未启动 | 提示用户启动 127.0.0.1:30080 的服务后重跑，**不要伪造占位图** |
| 尺寸校验不通过 | 宽高非 16 倍数 / 比例或像素越界 | 取整到 16 的倍数并落在像素区间内，再重跑 |
| 轮询超时仍未终态 | 队列卡住或 `--timeout` 设得过短 | 调大超时重跑；仍无结果则把 task_id 报给服务维护方 |
| `--jpg` 压缩失败 | 未安装 Pillow | `pip install pillow` 后重跑，或去掉 `--jpg` 只交 PNG |
| 下载文件为 0 字节 | `result_url` 已过期 | 重新轮询取新的 `result_url` 再下载 |
| 图上出现乱码文字 | prompt 里要求模型生成中文文字 | prompt 只描述画面，文字留给后期加，勿让模型出中文字符 |

## 交付标准

- **成功定义**：`--out` 指向的文件存在且非空；加 `--jpg` 时同目录另有 <1MB 的 JPG 可直接上传。
- **产物命名**：`cover.png` / `cover.jpg`（或 `--out` 指定名称）。
- **保存位置**：`--out` 指定路径，缺省为调用方当前目录。
- **完整性验证**：`ls -lh <out>` 确认非 0 字节，并肉眼确认画面主体与 prompt 相符。
- **服务不可达时报错退出，绝不用占位图冒充成功。**

## 与其他技能的联动

- `cnblogs-skill` / `zhihu-content-manager` 的发文流程中「生成配图」一步即调用本技能
- 生成的 JPG 路径直接传给对应平台的图片上传步骤

## 参考

- [scripts/generate_cover.py](scripts/generate_cover.py) —— 生成主脚本：尺寸校验、提交、轮询、下载与 JPG 压缩
