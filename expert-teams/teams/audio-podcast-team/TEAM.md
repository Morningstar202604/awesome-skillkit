# Audio Podcast Team - 音频播客内容交付专家团

> 场景：播客与音频内容全流程交付——从选题脚本、声音导演、录音主持、剪辑、音效配乐到品牌与质量门禁，强节奏、重听感、可上线。

## 团队定位
- **输入**：选题/话题、目标听众、时长、平台、品牌调性、参考节目
- **输出**：经剪辑、音效配乐、质量门禁后可上线的播客/音频成片，附脚本、时间点与封面文案
- **核心价值**：10 人分工、脚本先行、录制与声音设计并行、qa-reviewer + reviewer 双门禁收口，主理人只做拆解调度验收

## 成员架构（10 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 音频统筹 | `audio-team-lead` | 任务拆解、节目形态定调、角色分派、阶段门禁 | 所有播客/音频需求入口 |
| 播客脚本编剧 | `audio-scriptwriter` | 选题、节目结构、口播脚本、访谈提纲 | "写播客脚本"、"这期聊什么" |
| 声音导演 | `audio-sound-director` | 整体声音设计、节奏、情绪曲线、混音方向 | "这期声音怎么设计" |
| 音频剪辑 | `audio-editor` | 粗剪精剪、去口癖、对齐、音量归一、导出 | "剪辑音频"、"把杂音去掉" |
| 音效设计 | `audio-sfx-designer` | 转场音效、氛围音、动效音选择与铺排 | "加音效"、"转场怎么处理" |
| 配乐制作 | `audio-music-producer` | 片头片尾/背景音乐选配、音量 ducking | "配背景音乐"、"片头音乐" |
| 主播/主持 | `audio-host` | 口播演绎、访谈引导、语气节奏、临场互动 | "主播怎么说"、"主持稿" |
| 播客品牌 | `audio-brand-manager` | 节目定位、名字/封面/简介、更新节奏、听众画像 | "做播客品牌"、"节目定位" |
| 音频质检 | `audio-qa-reviewer` | 技术指标/音量/杂音/音画同步门禁（只读） | "音频质量把关" |
| 音频评审 | `audio-reviewer` | 内容/听感/节奏/可听性评审（只读） | "这期听感怎么样" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程** | "一期播客从选题到上线" | 拆解 → 脚本（scriptwriter）→ 声音导演定方向（sound-director）→ 主持录制（host）→ 剪辑（editor）+ 音效配乐并行（sfx + music）→ 双门禁（qa-reviewer 技术 + reviewer 听感并行，清零后）→ 交付 |
| **W2 仅脚本** | "只要这期脚本/提纲" | 拆解 → scriptwriter 出脚本/访谈提纲 → sound-director 给声音方向 |
| **W3 仅后期** | "已有录音做后期" | 拆解 → editor 剪辑 → sfx-designer + music-producer 并行铺音效配乐 → qa-reviewer + reviewer 双门禁 |

## 协作机制
- **小步提交**：脚本先定稿再录制；剪辑按段落粗剪→精剪小步走
- **门禁规则（唯一口径）**：后期完成 → qa-reviewer（技术指标）+ reviewer（内容听感）并行评审 → **双门禁无 critical/major 后** → 主理人交付。技术问题与听感问题都不过，不放水。
- **驳回机制**：同一期被驳回 2 次以上，停下来重查脚本定位或录制问题，而非重复剪
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不亲自写脚本/剪辑，只做拆解、调度、验收
- 版权素材（音乐/音效）只用可商用授权，不脑补来源
- 双门禁结论以 qa-reviewer / reviewer 回报为准，不脑补"应该没问题"
- 音量/响度按平台标准交付，不主观估

> **协作接口**：可对接 video-production-team（视频版音频轨）、content-writing-team（ shownotes/公众号文案）、marketing-team（播客推广物料）；典型跨场景触发词：播客脚本、音频剪辑、配音配乐、播客品牌。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全流程做一期播客（Team-lead 为入口）
teams/audio-podcast-team/agents/audio-team-lead "帮我做一期关于独立开发的播客，从脚本到上线全走一遍"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/audio-podcast-team/agents/audio-scriptwriter "写一期远程办公的播客脚本"
# teams/audio-podcast-team/agents/audio-sound-director "给这期定声音设计方向"
# teams/audio-podcast-team/agents/audio-editor "把这段录音去口癖并粗剪"
# teams/audio-podcast-team/agents/audio-sfx-designer "给这期配转场音效"
# teams/audio-podcast-team/agents/audio-music-producer "选片头音乐和背景音乐"
# teams/audio-podcast-team/agents/audio-host "把这段脚本口播出来"
# teams/audio-podcast-team/agents/audio-brand-manager "给播客做品牌定位"
# teams/audio-podcast-team/agents/audio-qa-reviewer "检查这段音频技术指标"
# teams/audio-podcast-team/agents/audio-reviewer "评审这期听感"
```
