# TTS 网关接入（video-voice-synth）

本技能采用「**用户自备网关**」模式：**仓库不提供、也不内嵌任何 TTS 厂商端点**。
你需要自己部署或指定一个 TTS 服务，并把它告诉脚本。

> **端点以你的实际部署为准，执行前必须确认。** 本文出现的 `127.0.0.1:30081`、
> 路径 `/v1/tts`、字段名 `speed` / `pitch` / `format` 均为**仓库示例默认值**
> （来自本技能脚本的初始常量），不是任何厂商的公开 API 承诺。**VERIFY BEFORE USE**：
> 执行前用你的服务文档或 `curl` 探测结果覆盖，见第 3 节。

## 目录

0. 前置自检 / 1. 环境变量约定 / 2. 请求与响应约定 / 3. 三步连通性探测
4. 失败处置表 / 5. 批量合成与并发 / 6. Mock 模式边界 / 7. 安全红线

## 0. 前置自检

```bash
command -v ffprobe >/dev/null && echo "ffprobe=OK" || echo "ffprobe=缺失(时长校验不可用)"
echo "BASE=${GATEWAY_BASE_URL:-<未设置>}  TIMEOUT=${GATEWAY_TIMEOUT:-30}"
[ -n "$GATEWAY_API_KEY" ] && echo "KEY=已设置(长度 ${#GATEWAY_API_KEY})" || echo "KEY=未设置"
```

预期：BASE 为你的网关根地址，ffprobe 可用（用于校验音频时长）。
BASE 为 `<未设置>` → 先按第 1 节设置，不要用脚本内置默认值蒙混过关。

## 1. 环境变量约定

以下名称是**本仓库的约定示例**，不是行业标准；若你的网关要求别的名字，
以你的部署为准，只改脚本读取变量的那一行。

| 变量 | 示例值 | 必需 | 说明 |
|---|---|---|---|
| `GATEWAY_BASE_URL` | `http://127.0.0.1:30081` | 是 | 网关根地址，**不带尾斜杠、不带路径** |
| `GATEWAY_API_KEY` | （你的密钥） | 视网关而定 | 以 `Authorization` 头发送，不落盘 |
| `GATEWAY_TIMEOUT` | `30` | 否 | 单次请求超时秒数；长文本按字数上调（见第 5 节） |
| `TTS_OUTPUT_FORMAT` | `wav` | 否 | 目标音频容器；下游 lip-sync 一般吃 `wav` |

```bash
export GATEWAY_BASE_URL="http://127.0.0.1:30081"   # ← 改成你的实际地址
export GATEWAY_API_KEY="..."
export GATEWAY_TIMEOUT=30
```

## 2. 请求与响应约定

**VERIFY BEFORE USE**：以下是本技能脚本当前发出的请求体。字段名、取值域、音色 ID
（如 `baby_f01`）**必须与你部署的服务一致**——音色 ID 尤其如此，它们来自本技能的
Voice Catalog 表，仅在你的网关登记了同名音色时才有效。

```
POST {GATEWAY_BASE_URL}/v1/tts
Content-Type: application/json
Authorization: Bearer ${GATEWAY_API_KEY}

{
  "text": "你们猜我花了多少钱买了这个？",
  "voice": "baby_f01",
  "speed": 1.2,
  "pitch": 3,
  "format": "wav"
}
```

成功判据（三条同时满足）：

1. HTTP `2xx`；
2. 响应体是音频二进制（不是 JSON 错误对象）——用 `file out.wav` 看是否识别为音频；
3. `ffprobe -v error -show_entries format=duration -of default=nw=1 out.wav` 得到
   **合理时长**（经验区间：中文约 4–6 字/秒，属经验值，需按你的音色实测校准）。

**音色清单核实**（在批量合成前做一次）：

```bash
curl -sS -m 10 -H "Authorization: Bearer ${GATEWAY_API_KEY}" "$GATEWAY_BASE_URL/v1/voices"
# 有该端点则返回可用音色；404 表示此网关没有列目录接口 → 逐个试合成 1 句短文本验证
```

若返回列表里没有 `baby_f01` 这类 ID，就不能在脚本里填它，否则一定失败。

## 3. 三步连通性探测

```bash
# 步骤 1：服务是否在跑
curl -sS -m 5 -o /dev/null -w "HTTP=%{http_code} connect=%{time_connect}s\n" "$GATEWAY_BASE_URL/"
# 预期：200/401/403/404 任一。
# (7) Failed to connect = 没起或地址错；(28) timed out = 防火墙/安全组

# 步骤 2：健康检查（路径以你的服务为准）
for p in /health /healthz /v1/health /docs; do
  printf "%-12s " "$p"; curl -sS -m 5 -o /dev/null -w "%{http_code}\n" "$GATEWAY_BASE_URL$p"
done

# 步骤 3：真实探活（一句短文本即可，确认鉴权+合成链路）
curl -sS -m "$GATEWAY_TIMEOUT" -o probe.wav -w "HTTP=%{http_code} total=%{time_total}s\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GATEWAY_API_KEY}" \
  -d '{"text":"测试","voice":"baby_f01","speed":1.0,"pitch":0,"format":"wav"}' \
  "$GATEWAY_BASE_URL/v1/tts"
ls -l probe.wav && file probe.wav
```

预期：步骤 3 的 HTTP=200，且 `file probe.wav` 输出含 `WAV` / `RIFF` / `Audio`。
若 `file` 显示 `ASCII text` 或 `JSON` → 服务端返回了错误信息，把内容 `cat probe.wav` 看具体原因。

## 4. 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| `curl: (7) Failed to connect` | 服务未启动 / 端口错 | 确认进程与端口：`ss -ltnp \| grep 30081` |
| `curl: (28) timed out` | 网络被拦，或文本过长渲染超时 | 调大 `GATEWAY_TIMEOUT`；长句拆成短句分次合成 |
| HTTP `401` | 密钥缺失或错误 | 重新 export；密钥含 `$`、空格时用单引号 |
| HTTP `403` | 无该接口权限 / IP 白名单 | 查服务端权限配置 |
| HTTP `404` | 路径不对 | 步骤 2 循环探路径 |
| HTTP `422` / `400` | 字段不匹配（常见于 `voice` 值不在音色表） | 用第 2 节的音色清单端点核实 ID |
| HTTP `429` | 限流 | 串行 + 每次请求间 `sleep 0.5`；批量模式降低并发 |
| HTTP `5xx` | 服务端错误（模型未加载、显存不足） | 查服务端日志；重试一次仍失败则 `--mock` 占位 |
| 200 但文件是 JSON 文本 | 服务端返回错误对象 | `cat` 文件看 message 字段 |
| 200 但时长异常短（<0.3s） | 文本为空或编码问题 | 检查 JSON 是否 UTF-8；中文不要做 `\uXXXX` 转义以外的事 |
| 音频无声（全零采样） | 合成失败但返回了静音 | 判据：`ffprobe -af volumedetect` 看 `mean_volume`；接近 -91 dB 即为空 |

## 5. 批量合成与并发

批量模式按脚本 `scenes` 逐条合成，输出 `scene_<id>.wav`。要点：

1. **串行优先**。自建网关多为单卡，并发很容易触发 5xx 或 429；先串行跑通再加并发。
2. **超时按字数放大**。经验做法：`GATEWAY_TIMEOUT = 15 + 字数 × 0.2` 秒；长句先拆句。
3. **逐条落盘并校验**。每条合成完立刻 `ffprobe` 取时长，与脚本里 `duration_sec`
   对比，偏差 > 0.5s 记录下来——下游 lip-sync 与画面时长会跟着偏。
4. **失败不中断全流程**：记录失败的 scene id，全部跑完后再补跑失败项。

补跑示例（对失败场景单独重试）：

```bash
python3 - <<'PY'
import json, pathlib
for p in sorted(pathlib.Path(".").glob("scene_*.wav")):
    print(p.name, p.stat().st_size)
PY
# 预期：每个 scene 都有文件且大小 > 0；为 0 的即需补跑
```

## 6. Mock 模式边界

`--mock` 或 `SKILLKIT_MOCK=1` 时脚本生成**静音 WAV**（时长按字数估算）并输出
`"mock": true`。合法用途：联调下游 lip-sync / 拼接流程、CI 无网关自测。

**禁止**把 mock 音频当作交付物：它是全零采样的静音文件。交付前确认：
`ffprobe -v error -af volumedetect -f null -` 的 `mean_volume` 明显高于 -91 dB，
且结果里 `mock` 不为 `true`。

## 7. 安全红线

- 密钥只走环境变量；不进脚本、不进 Git、不用明文打日志（打印长度即可）。
- 文本输入视为不可信：不要把用户文本直接拼进 shell 命令，走 JSON 序列化。
- 覆盖已有音频、删除文件属不可逆操作，执行前先向用户确认。
