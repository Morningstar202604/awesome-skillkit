---
name: video-script-writer
description: "Write video scripts: dialogue, narration, shot descriptions, timing markers, and platform-compliant titles/captions. Supports multiple video types (talking character, meme, tutorial, vlog, short). Includes a golden-3-second hook discipline, single-CTA rule, and speaking-rate word budgeting. Use when the user needs a script for a video before production. 当用户要求 写视频脚本 / 短视频文案 / 分镜脚本 / 口播稿时使用。 Do NOT use for generating video files (script text only), nor for scene-by-scene storyboards and prompt pairs (use storyboard-designer)."
license: Apache-2.0
compatibility: "Prompt-based with an optional helper script. scripts/script_writer.py (Python 3.8+, stdlib only) generates a deterministic scene skeleton and — if SKILLKIT_LLM_URL/KEY env vars are set — calls an OpenAI-compatible gateway to write real dialogue. Without the gateway it emits template placeholder lines and labels them honestly (dialogue_source=template). No API keys required."
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-22"
---

# 视频脚本编写

产出可投产的结构化视频脚本：台词、计时、画面指示、平台合规标题与标签。**脚本文本是唯一产物，不生成视频文件。**

短视频的评判标准不是"文案写得好"，而是**前 3 秒不被划走、看完知道做什么**。本技能的全部纪律围绕这两点。

## 适用决策表

| 你的处境 | 本技能的位置 | 去向 |
|----------|--------------|------|
| 有一个概念，要成片脚本 | ✅ 本技能 | 这里 |
| 已有脚本，要拆成分镜 | ❌ 越界 | storyboard-designer |
| 要有画面的视频 prompt（非脚本） | ❌ 越界 | video-prompt-engineer |
| 要文案但不涉及视频 | ❌ 越界 | product-copywriter |
| 只给了"拍个好看的视频"这类空概念 | ⚠️ 先退回补：主体 + 钩子 | 前置自检 |
| 目标时长超平台上限 | ⚠️ 先决策：拆集 or 下调 | 失败处置表 |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| concept | ✓ | 视频概念一句话（含主体与钩子） |
| video_type | ✗ | `talking_character` / `meme` / `tutorial` / `vlog` / `short`，默认 `talking_character` |
| duration | ✗ | 目标时长（秒），默认 30 |
| platform | ✗ | `douyin` / `bilibili` / `tiktok`，默认 `douyin` |
| language | ✗ | `zh` / `en`，默认 `zh` |
| tone | ✗ | `funny` / `educational` / `dramatic`，默认 `funny` |
| character | ✗ | 角色 JSON（name / persona / voice_style） |

任一必需输入缺失时，一次性问齐：

> 请提供：① 视频概念（一句话，含主体与钩子）。可选：② 类型（默认 talking_character）、③ 时长（默认 30s）、④ 平台（默认 douyin）、⑤ 语言（默认 zh）、⑥ 角色设定、⑦ 基调（默认 funny）。

## 前置自检

- 概念非空：空概念（如"拍个好看的视频"）直接退回，要求补充主体与钩子。
- 时长不超平台上限：douyin 60s / bilibili 900s / tiktok 600s。超限 → 让用户二选一：拆集 或 下调时长（脚本会静默截断，见诚实声明 5，不要默认接受）。
- **选轨确认（仅当你实际要运行脚本时适用）**：环境是否配了 `SKILLKIT_LLM_URL` + `SKILLKIT_LLM_KEY`？
  - 配了 → LLM 轨，脚本会调真模型写台词。
  - 没配 → 模板轨，台词是自描述占位（`[角色] Attention grabber about: 概念`），**必须告诉用户这一点**，并给出两个选择：配网关重跑，或拿骨架人工写台词。
  - **纯提示词模式（不运行脚本、直接手写脚本）跳过本项**：你按下方工作流把台词写完即可。**不得因为"无法检查环境变量"或"缺配置"而把任务退回用户**——交付物是本条视频的完整脚本，不是执行计划或环境检查结论。

## 暗知识（真正决定视频成败的东西）

### 1. 前 3 秒是黄金窗口：钩子不是"介绍"

观众在前 3 秒决定留或走。**钩子的定义是制造信息缺口**，不是自我介绍、不是"大家好"，也不是重复标题。

六种可复用的钩子类型：

| 类型 | 句式骨架 | 适用 |
|------|----------|------|
| 痛点开场 | 「你的 X 是不是总 Y？」 | 教程、干货 |
| 结果前置 | 「我用这招把 X 从 A 降到 B」 | 教程、评测 |
| 反常识 | 「X 其实不是 Y 的原因」 | 观点、科普 |
| 数字 | 「3 个动作，第 2 个最容易做错」 | 清单、教程 |
| 提问 | 「为什么 A 时 B 总发生？」 | 科普、剧情 |
| 利益承诺 | 「看完这条，你能 X」 | 教程、导流 |

> 数字钩子里的数字**必须真实可核**（红线 1）；「90% 的人做错」式无从核实的比例属于编造，不许用。

> 采信说明：钩子的重要性是行业通行共识；但"3 秒流失 X%""完播率提升 Y%"类的具体数字各家口径不一、无可核出处，本技能**不引用百分比**。

### 2. 一条视频只给一个 CTA

「点赞 + 关注 + 转发 + 评论 + 主页领表」= 没有 CTA——注意力被分摊就等于零。导流型视频的正确做法：**全片所有设计服务于结尾那一个动作**。

### 3. 台词字数必须按口播语速核算

中文口播通行语速约 **4–5 字/秒**（新闻联播式播报更快）。据此：

| 时长 | 台词容量（字） |
|------|----------------|
| 15s | 60–75 |
| 30s | 120–150 |
| 60s | 240–300 |

超容量的唯一正解是**砍词**，不是"说快点"——加速会牺牲清晰度与情绪。（语速为通行经验值，非平台规则；不同主播实际差异较大。）

### 4. 口播与画面分工：能演的不说

画面能演出来的信息，口播不要重复（「我打开了冰箱」+ 画面开冰箱 = 双重浪费）。口播只承担画面给不了的四种信息：**心理活动、背景交代、结论、数字**。

### 5. 循环设计：结尾接回开头

meme / 短平快类型，让结尾画面或台词能直接接上开头 → 观众循环播放，完播与互动数据双赢。设计法：把钩子句写成能被"接住"的句子。

### 6. 封面/标题的承诺必须在前 3 秒兑现

承诺（封面/标题说有什么）与兑现（前 3 秒给什么）不一致 = 划走 + 负向反馈，这是流量衰减的常见原因。**写脚本时把封面文案和前 3 秒对照着写**。

### 7. 合规不是可选项

- 带货/推广类：避开广告法极限词（最、第一、国家级、100% 等），避开虚假功效承诺。
- 全类型：避免诱导互动（"点赞过万就发下期"）——主流平台规则明令限制。
- 医疗健康类：不得承诺疗效。
  > 具体类目规则以平台最新公示为准；本技能只做风险扫描，不做合规保证（诚实声明 7）。

## 红线（硬性禁令）

1. **不编数据、不造假承诺**：钩子里的数字（"90% 的人做错"）必须有出处或改为定性表述；"3 天涨粉 10 万"式承诺直接禁止。
2. **不写人设说不出口的台词**：角色是毒舌教练就写毒舌教练的话——人设一致性优先于文采。
3. **模板轨台词不得冒充成品**：脚本产出的 `dialogue_source=template` 时，交付必须显式声明"这是骨架，台词待写"。
4. **不承诺流量结果**：本技能保证结构合规与节奏合理，不对"爆款"作任何承诺。
5. **单 CTA 不堆砌**（暗知识 2）。

## 诚实声明（脚本的实际行为）

`scripts/script_writer.py` 是**骨架生成器 + 可选的 LLM 台词轨**。以下为 2026-09-22 实跑核实：

1. **LLM 双轨**：配置 `SKILLKIT_LLM_URL` + `SKILLKIT_LLM_KEY`（可选 `SKILLKIT_LLM_MODEL`）后，脚本调 OpenAI 兼容网关写台词，每场 `dialogue_source="llm"`；未配置、`--no-llm` 或网关失败 → 模板占位台词，`dialogue_source="template"`，且模板句**自描述为待补写**（如 `[Character] Payoff: 概念 (punchline here)`）。
2. **顶层 `dialogue_source`** 汇总为 `llm` / `mixed` / `template` 三态；网关失败时 `llm_note` 记录原因（不静默冒充）。
3. **`visual` 字段恒为占位**：`[role: describe visual action here]`——脚本不生成画面描述，必须人工或 LLM 补写。
4. **`sfx` 大多数为空**：仅 hook / punchline / outro 三个角色有默认音效，其余为空字符串。
5. **时长行为**：超出平台上限时**静默截断**并写入 `duration_note`；目标时长小于场景数时抬升到场景数（每场至少 1 秒）并写入 `duration_note`。
6. **`caption` 是自动拼装的标签式文案**（含 emoji 前缀），脚本只做长度核对（`caption_check`），**不做内容合规审查**。
7. **`tts_config.speed`**：funny 基调 = 1.2，其余 = 1.0；这是生成参数透传，不是"建议语速"。
8. **`character.voice_style` 原样透传**，脚本不校验取值是否被下游 TTS 支持。
9. **`status` 字段**：成功为 `"success"`；输入错误（缺 concept / JSON 不合法）时脚本**打印错误 JSON 而非静默失败**，退出码 2。
10. **非法 `platform` 静默回退 `douyin`**：传入 `douyin/bilibili/tiktok` 以外的值不会报错，按 douyin 规则处理（平台上限与 caption 上限都按 douyin）。跨平台投递时注意这一条。

## 工作流

### 步骤 1：概念收敛与选轨

按前置自检核对概念与选轨。概念里必须能读出"主体 + 钩子方向"。

**交付物是一份自包含的脚本 JSON**（逐场台词、`visual`/`camera`/`sfx` 指示、时长、标题与标签全部落在 `scenes[]` 与顶层字段里——下游 lip-sync 与剪辑按键值读取，另开的表格它读不到）——不是执行计划、不是"请提供更多信息"、不是环境检查结论。纯提示词模式下台词由你直接写完整；脚本模式才需要选轨。
预期：concept 非空；用户已知晓本次是 LLM 轨还是模板轨。
若失败：概念空泛 → 退回补，不猜着写。

### 步骤 2：生成脚本

```bash
python3 scripts/script_writer.py --concept "宝宝测评手机" --type talking_character --duration 30 --platform douyin --language zh --tone funny
```

预期：stdout 输出 JSON，含 `title` / `hook` / `scenes`（id、role、duration_sec、dialogue、dialogue_source、visual、camera、sfx）/ `caption` / `total_duration` / `dialogue_source` / `caption_check`；`scenes` 总时长 = 目标时长（每场 ≥1s）。
若失败：`status=error` → 读 error 字段定位；网关失败 → 看 `llm_note`，决定重试或转人工。

### 步骤 3：把画面要素写回场景对象（必做）

脚本的 `visual` 全是占位。按「能演的不说」（暗知识 4）逐场补写：**主体 + 动作 + 景别/环境** 写进 `scenes[i].visual`，镜头运动写 `camera`，情绪拐点加 `sfx`——**写回场景对象本身，不要另开表格、不要出现字段缺失**（下游按键值读取）。
**`dialogue` 只放能念出口的台词**；括号里的动作 / 表情 / 音效指示属于画面层（`visual`/`sfx`），不要混进 `dialogue`。
自包含示例（交付照此形状，字段全部内嵌）：

```json
{ "id": 2, "role": "主角", "duration_sec": 4, "dialogue": "我是谁…我在哪…", "dialogue_source": "llm", "visual": "浴室镜前，主角立牌式刷牙、眼神空洞，牙膏沫挂在嘴角", "camera": "中景，镜面反射带出背后疲惫身影", "sfx": "机械刷牙声" }
```

预期：交付 JSON 的每个场景对象都含 `visual`（具体可执行），且 `dialogue` 内无括号动作指示。若失败：写不出画面 → 说明该场没有视觉信息，考虑合并或砍掉这场。

### 步骤 4：按语速核算台词容量

统计各场台词字数，对照暗知识 3 的容量表。超容量 → 砍词（优先砍重复信息与形容词）。
预期：台词总字数 ÷ 时长 ∈ [4, 5] 字/秒。若失败：LLM 轨台词普遍超长 → 在 prompt 里加"每场不超过 N 字"重跑或人工删。

### 步骤 5：合规与承诺一致性核对

- 兑现测试：封面/标题（`title`）承诺的信息，前 3 秒（`hook`）是否给出（暗知识 6）。
- 合规扫描：极限词 / 诱导互动 / 疗效承诺（暗知识 7）。
- CTA 计数：全片是否只有一个行动号召（暗知识 2）。
预期：三项全过。若失败：兑现不一致 → 改 title 或 hook（不要两边都改，无法归因）。

## 脚本类型要点

### 口播角色（talking_character，baby、nailong 等）

- 对话驱动，2–4 场景；每场景一句台词 + 一个动作。
- 金句落在 70–80% 处（经验值）；视觉以角色 + 道具为主，背景极简。

### 梗图/反应类（meme）

- 切镜率全类型最高（[timing-guide.md](references/timing-guide.md) 的 Meme 行：1.5–4s/镜、30s 片 8–15 镜）——**15s 片约 4–8 镜**。不要切成三个 5 秒的大段：均分时长 = 节奏平，是 meme 最常见的失败。
- 节拍按「铺垫 → 重复/升级 → 反差落点」：笑点 / 崩溃点放在末 1–2 镜（期待落差），不是匀速线性吐槽；文字压屏 + 音频金句，每镜至多一句。
- 结尾**必须**做循环衔接（暗知识 5）：末镜最后一帧回环到首帧。

### 教程/讲解类（tutorial）

- 开头 5s 给结果承诺（学完能得到什么）→ 步骤 20–60s（每步 <10s，一步一动作）→ 结尾 5s 收束 + 单 CTA（时间划分为经验值）。
- **B 站与抖音的差异**：B 站观众耐心更高，可接受更长的铺垫与更深的原理；抖音前 3 秒定生死，不要把 B 站式开场搬到抖音。

## 内置验证步骤（交付前逐条打勾）

- [ ] **3 秒钩子测试**：`hook` 是信息缺口/张力，不是自我介绍或泛问
- [ ] **单 CTA 测试**：全片只有一个行动号召
- [ ] **语速测试**：台词总字数 ÷ 时长 ∈ [4, 5] 字/秒
- [ ] **兑现测试**：title/封面承诺 ↔ 前 3 秒一致性
- [ ] **循环测试**（meme）：结尾能接回开头
- [ ] **合规扫描**：无极限词 / 诱导互动 / 疗效承诺
- [ ] **占位清除**：`visual` 占位已全部替换；`dialogue_source=template` 时已向用户声明台词待写
- [ ] **字段内嵌**：`visual`/`camera`/`sfx` 位于 `scenes[]` 对象内（未用表格替代）；`dialogue` 为纯净台词

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| `status=error`，`缺少 concept` | 无输入 | 退回要求补概念 |
| `status=error`，`输入 JSON 不合法` | `--json-input` 语法错 | 修正 JSON 后重跑（rc=2） |
| `llm_note` 提示网关失败 | 网关超时/坏 JSON | 重试；连续失败则转人工写台词，并如实告知 |
| 总时长被截断（`duration_note`） | 超平台上限 | 与用户二选一：拆集 or 下调时长，不要默认接受截断 |
| 某场 duration_sec = 1（疑似挤压） | 目标时长过短 | 确认 `duration_note` 是否记录抬升；必要时缩短概念或加时长 |
| 台词超语速容量 | LLM 不懂"秒" | 按暗知识 3 砍词；或在网关 prompt 里加字数约束重跑 |
| caption 超限（`caption_check.ok=false`） | 标题过长 | 裁剪 title 或合并标签 |
| 用户要"必爆" | 期望管理 | 明确不做流量承诺（红线 4），改为解释结构合规性 |

## 交付标准

- 结构化脚本 JSON：`title` / `hook` / `scenes[]`（含 `dialogue`、`dialogue_source`、`visual`、`camera`、`sfx`、`duration_sec`）/ `caption` / `total_duration`——**一份自包含 JSON**，画面 / 音效指示写在场景对象内，不用表格替代。
- `dialogue` 只含可念出的台词（动作 / 表情 / 音效指示归 `visual`/`sfx`）。
- `scenes` 总时长 = 目标时长；每场 ≥1s。
- 每场 `visual` 可执行（非占位）；`dialogue_source` 如实标注。
- 台词语速 ∈ [4, 5] 字/秒；`caption_check.ok = true`。
- 内置验证 8 项全过。
- 仅脚本文本，不生成视频文件；下游接 video-voice-synth → video-lip-sync → video-editor。

## 参考

- `references/script-templates.md` — 各类型成品模板，写脚本前照抄骨架。
- `references/timing-guide.md` — 节奏 / beat 规则与时长分配。
- `references/sources-and-methodology.md` — 暗知识 1–7 的来源与采信纪律（拒绝百分比效果承诺）、脚本行为实测记录。交付/署名/被质疑时读。
- [cinematography-lexicon.md](../video-prompt-engineer/references/cinematography-lexicon.md) — 镜头语言词库（转场/动作/表演细节）：脚本里的镜头指示词直接从这张选。

## 附录：CLI 契约（参数速查表）

| 参数 | 取值 | 说明 |
|------|------|------|
| `--concept` | str | 必填，视频概念 |
| `--type` | enum | 模板类型（talking_character/meme/tutorial/vlog/short） |
| `--duration` | int | 目标秒数，默认 30 |
| `--platform` | enum | douyin/bilibili/tiktok |
| `--language` | zh/en | 默认 zh |
| `--tone` | enum | 基调，默认 funny |
| `--character` | JSON 串 | 角色设定（name/persona/voice_style） |
| `--json-input` | 文件 | 完整 JSON 输入，覆盖单项参数 |
| `--no-llm` | flag | 强制走模板轨（即使配了网关） |
| `--output` | 文件 | 写文件替代 stdout |
| env | `SKILLKIT_LLM_URL` / `SKILLKIT_LLM_KEY` / `SKILLKIT_LLM_MODEL` | 配置后启用 LLM 台词轨 |
