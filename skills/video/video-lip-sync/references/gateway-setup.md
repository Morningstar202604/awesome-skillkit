# 口型同步网关接入（video-lip-sync）

本技能采用「**用户自备网关**」模式：**仓库不提供、也不内嵌任何厂商端点**。
你需要自己部署或指定一个 lip-sync 服务，并把它告诉脚本。

> **端点以你的实际部署为准，执行前必须确认。** 本文中出现的 `127.0.0.1:30081`、
> 路径 `/v1/lipsync`、字段名 `mouth_width` 均为**仓库示例默认值**（来自本技能脚本的
> 初始常量），不是任何厂商的公开 API 承诺。**VERIFY BEFORE USE**：执行前用你自己的
> 服务文档或 `curl` 探测结果覆盖这些值，见第 3 节。

## 目录

0. 接入模式与前置声明 / 1. 环境变量约定 / 2. 请求与响应约定 / 3. 三步连通性探测
4. 失败处置表 / 5. 异步任务与排队 / 6. Mock 模式边界 / 7. 安全红线

## 0. 接入模式与前置声明

| 项 | 说明 |
|---|---|
| 谁提供端点 | 用户。仓库不内置、不推荐、不保证任何第三方地址 |
| 凭据来源 | 仅环境变量，禁止写进 SKILL.md、脚本或 Git |
| 默认行为 | 脚本默认**真实模式**；网关不可达时报错退出（非 0），不静默造假 |
| 兜底 | `--mock` 或 `SKILLKIT_MOCK=1` 才走假数据，且输出带 `"mock": true` |

自检第一步（任何排查之前先跑）：

```bash
echo "BASE=${GATEWAY_BASE_URL:-<未设置>}  TIMEOUT=${GATEWAY_TIMEOUT:-120}"
[ -n "$GATEWAY_API_KEY" ] && echo "KEY=已设置(长度 ${#GATEWAY_API_KEY})" || echo "KEY=未设置"
```

预期：BASE 为你的网关根地址（如 `http://127.0.0.1:30081`），KEY 至少有值。
若 BASE 为 `<未设置>` → 先按第 1 节设置环境变量，不要用脚本里的默认值蒙混。

## 1. 环境变量约定

以下名称是**本仓库的约定示例**，不是行业标准；若你的网关要求别的名字（如
`LIPSYNC_ENDPOINT`），以你的部署为准，只需要在同一处改掉脚本读取的变量名。

| 变量 | 示例值 | 必需 | 说明 |
|---|---|---|---|
| `GATEWAY_BASE_URL` | `http://127.0.0.1:30081` | 是 | 网关根地址，**不要带尾斜杠**，不要带路径 |
| `GATEWAY_API_KEY` | （你的密钥） | 视网关而定 | 仅经环境变量传入，脚本以 `Authorization` 头发送 |
| `GATEWAY_TIMEOUT` | `120` | 否 | 单次请求超时秒数；口型渲染通常比 TTS 慢，默认给足 |

设置方式（当前 shell 生效，不落盘）：

```bash
export GATEWAY_BASE_URL="http://127.0.0.1:30081"   # ← 改成你的实际地址
export GATEWAY_API_KEY="..."
export GATEWAY_TIMEOUT=120
```

写入 `~/.zshrc` / `~/.bashrc` 前先确认该机器非多人共享。

## 2. 请求与响应约定

**VERIFY BEFORE USE**：下面这段是本技能脚本当前发出的请求体，字段名必须与你部署的
服务一致。核对方法：查看你所用服务的 OpenAPI / README，或对网关根路径做一次
`curl "$GATEWAY_BASE_URL/openapi.json"`（有则返回接口定义）。

```
POST {GATEWAY_BASE_URL}/v1/lipsync
Content-Type: application/json
Authorization: Bearer ${GATEWAY_API_KEY}     # 若网关不需要鉴权可省略

{
  "face_image": "character.png",   # 相对路径；部分实现要求 base64 或上传 URL
  "audio_path": "scene_1.wav",
  "mouth_width": 40,
  "mouth_height": 30
}
```

成功判据（三条同时满足才算成功）：

1. HTTP 状态码 `2xx`；
2. `Content-Type` 为视频类型（如 `video/mp4`）；
3. 落盘后 `ffprobe -v error -show_entries format=duration -of default=nw=1 out.mp4`
   得到的时长**约等于**输入音频时长（误差 ≤ 0.3s）。

第 3 条最容易被忽略：返回了 200 但时长对不上，后面拼接会整体错位，务必校验。

## 3. 三步连通性探测

按顺序执行，**任一步失败就停在那里处理**，不要跳到下一步。

```bash
# 步骤 1：端口是否通（不依赖任何业务路径）
curl -sS -m 5 -o /dev/null -w "HTTP=%{http_code} connect=%{time_connect}s\n" "$GATEWAY_BASE_URL/"
# 预期：HTTP 为 200/401/403/404 任一（说明服务在跑）；
# 失败特征：curl: (7) Failed to connect = 服务没起或地址错 → 检查进程与端口
#          curl: (28) Operation timed out = 被防火墙/安全组拦 → 检查监听地址是 127.0.0.1 还是 0.0.0.0

# 步骤 2：健康检查路径（路径名以你的服务为准，常见的有 /health /healthz /v1/health）
for p in /health /healthz /v1/health; do
  printf "%-12s " "$p"; curl -sS -m 5 -o /dev/null -w "%{http_code}\n" "$GATEWAY_BASE_URL$p"
done
# 预期：至少一个返回 200。全 404 = 路径名不对，查你的服务文档

# 步骤 3：真实探活（用最短音频，确认鉴权与渲染链路都通）
curl -sS -m "$GATEWAY_TIMEOUT" -o probe.mp4 -w "HTTP=%{http_code} total=%{time_total}s\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
  -d '{"face_image":"character.png","audio_path":"scene_1.wav","mouth_width":40,"mouth_height":30}' \
  "$GATEWAY_BASE_URL/v1/lipsync"
# 预期：HTTP=200 且 probe.mp4 非空（ls -l probe.mp4 显示 > 0 字节）
```

`ls -l probe.mp4` 为 0 字节即视为失败，即使 HTTP 是 200。

## 4. 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| `curl: (7) Failed to connect` | 服务未启动 / 地址或端口错 | 确认进程在跑、监听地址、端口；本机用 `ss -ltnp \| grep 30081` |
| `curl: (28) timed out` | 防火墙、安全组，或渲染耗时超过 `-m` | 先放宽 `-m` 重试；再查网络策略 |
| HTTP `401` | 缺或错的 `GATEWAY_API_KEY` | 重新 export；注意密钥里的 `$`、空格需引号包裹 |
| HTTP `403` | 密钥无该接口权限 / IP 白名单 | 查服务端权限配置 |
| HTTP `404` | 路径不对 | 步骤 2 循环探路径，以你的服务文档为准 |
| HTTP `422` / `400` | 请求体字段不匹配 | 对照第 2 节字段与你的服务定义逐字段核对 |
| HTTP `429` | 限流 | 降低并发；串行处理并在每场景间 `sleep 1` |
| HTTP `5xx` | 服务端内部错误（模型未加载、显存不足常见） | 看服务端日志；重试一次仍失败则改用 `--mock` 交付占位 |
| 返回 200 但视频 0 字节 | 服务端出了空响应 | 视为失败，不要用空文件继续下游流程 |
| 返回视频时长与音频不符 | 帧率/时长参数不对 | 用 `ffprobe` 对比两者，检查 `frame_rate` 配置 |

## 5. 异步任务与排队

部分自建网关是**异步**的：先返回任务 ID，再轮询结果。识别特征：响应是 JSON（不是视频二进制），
且含 `task_id` / `job_id` / `status` 之类的字段。

轮询模板（字段名以你的服务为准，**VERIFY BEFORE USE**）：

```bash
# 提交 → 拿到 task_id（假设返回 {"task_id":"abc123"}）
TASK=$(curl -sS -m 30 -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
  -H "Content-Type: application/json" -d @payload.json \
  "$GATEWAY_BASE_URL/v1/lipsync" | python3 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")

# 轮询：最多 60 次 × 5 秒 = 5 分钟
for i in $(seq 1 60); do
  S=$(curl -sS -m 10 -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
        "$GATEWAY_BASE_URL/v1/tasks/$TASK" | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])")
  echo "try=$i status=$S"
  [ "$S" = "succeeded" ] && break
  [ "$S" = "failed" ] && { echo "任务失败"; exit 1; }
  sleep 5
done
```

要点：**必须设最大重试次数**并区分 `queued` / `running` / `succeeded` / `failed`。
无限轮询会让整条流水线挂死。

## 6. Mock 模式边界

`--mock` 或 `SKILLKIT_MOCK=1` 时脚本**只产出元数据 JSON，不生成视频**，输出中带
`"mock": true`。它的唯一合法用途是：联调下游（拼接、字幕）时的占位，以及 CI 里的
无网关自测。

**禁止**把 mock 输出当作交付物——`"output_path"` 指向的文件并不存在。交付前用
`ls -l <output_path>` 确认文件真实存在，且结果里 `mock` 不为 `true`。

## 7. 安全红线

- 密钥只走环境变量；不进脚本、不进 Git、不进日志（排查时用长度代替内容打印）。
- 网关返回的文件视为**不可信输入**：落盘前限制目录（如固定输出到 `output/` 子目录），
  不要按响应里的文件名直接拼接路径。
- 删除、覆盖、对外发布属不可逆操作，执行前必须向用户确认。
