---

name: baoyu-wechat-summary
description: >-
  Summarizes WeChat group chat highlights into a structured digest using the local wx-cli binary (https://github.com/jackwener/wx-cli). Generates a normal digest by default; a roast (毒舌) version is opt-in. Maintains per-group history (history.json + history-digests.jsonl), per-user profiles, and per-group fact memory (memory.md) across runs, with privacy guardrails baked in. Use when the user asks to "总结群聊", "群聊精华", "群聊摘要", "summarize group chat", "group chat digest", mentions a WeChat group name with a time range, says "帮我看看 XX 群最近聊了什么", "XX 群有什么值得看的", or asks to "回溯画像" / "初始化画像" / "backfill profiles". Adds the roast version when the user says "毒舌版", "roast 版", "再来个毒舌的", or similar.
description_zh: "用本地 wx-cli 把微信群聊亮点总结成结构化纪要（可选毒舌版，按群维护历史）。"
license: MIT
compatibility: 需要网络与对应平台凭据（微信公众号 API / Chrome CDP 等）；发布类操作先预览再确认。
metadata:
  author: "JimLiu/baoyu-skills 上游（MIT）"
  version: "1.0.0"
  category: writing
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-27"
  source: "https://github.com/JimLiu/baoyu-skills/tree/main"
---

# WeChat Group Summary

群聊精华提取专家。把零散的微信群聊记录提炼成结构化、可读性强的简报，并维护跨次运行的群聊历史与群友画像。底层依赖外部 [wx-cli](https://github.com/jackwener/wx-cli) 二进制（`wx` 命令），不打包脚本。

> **⚠️ Sandbox restriction**
>
> wx-cli reads from `~/.wx-cli/` (config, cache, daemon socket) and from WeChat's data directory (`~/Library/Containers/com.tencent.xinWeChat/` on macOS). Both paths are outside Claude Code's default sandbox. Every `wx` command in this skill needs to run with `dangerouslyDisableSandbox: true` from the start — don't waste a sandbox attempt first. The user can use `/sandbox` to view/edit restrictions.

## References（按需加载）

本文件只保留工作流骨架；细节拆在 `references/` 下，**执行到对应步骤时再读，不要一开始全部读入**：

| 参考文件 | 内容 | 何时读 |
|---------|------|-------|
| [references/setup.md](references/setup.md) | 环境检查（wx-cli 安装/权限/初始化）、wx-cli 命令速查、排障手册 | 新环境首次运行，或任何 `wx` 命令失败时 |
| [references/output-formats.md](references/output-formats.md) | 两版摘要的 Section 顺序、格式与内容规范、输出骨架、自检清单 | Round 2 动笔前 |
| [references/profiles.md](references/profiles.md) | 画像文件格式、更新规则、隐私红线、回溯流程 | Step 3.7 / 8.5 / Step 9 |
| [references/group-memory.md](references/group-memory.md) | 群级事实记忆的写入门槛、防注入、格式 | Step 8.6 |

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** exposed by the current agent runtime — e.g., `AskUserQuestion`, `request_user_input`, `clarify`, `ask_user`, or any equivalent.
2. **Fallback**: if no such tool exists, emit a numbered plain-text message and ask the user to reply with the chosen number/answer for each question.
3. **Batching**: if the tool supports multiple questions per call, combine all applicable questions into a single call; if only single-question, ask them one at a time in priority order.

Concrete `AskUserQuestion` references below are examples — substitute the local equivalent in other runtimes.

## Prerequisites

快速验证环境：`wx --version` 有输出且 `wx sessions` 返回数据即可继续。任何一步失败，或是首次在新环境运行 → 读 [references/setup.md](references/setup.md)（完整环境检查、wx-cli 命令速查、排障手册），停在第一个失败项并给用户确切的修复命令。**绝不自动安装、绝不替用户跑 `sudo`。**

## Preferences (EXTEND.md)

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `EXTEND.md` (relative to project root) | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-wechat-summary/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-wechat-summary/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Read, parse, apply. On first use in session, briefly remind: "Using preferences from [path]. Edit it to change defaults." |
| Not found | **MUST** run first-time setup (BLOCKING) before generating any digest — do NOT silently use defaults. |

### Supported keys

EXTEND.md is plain text with `key: value` or `key=value` lines, `#` for comments, case-insensitive keys.

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `self_wxid` | string | (required) | The owning account's wxid. Messages whose `from_wxid` matches this are attributed to the user. |
| `self_display` | string | (required) | Display name to substitute for the user's own messages in digest text. |
| `default_version` | `normal` / `roast` / `both` | `normal` | Which version(s) to generate when the user doesn't say otherwise. |
| `default_time_range` | string (e.g. `7d`, `24h`, `1d`) | (none) | Default range when the user omits time and there's no incremental anchor. |
| `data_root` | path | `{project_root}/wechat` | Override where digest folders live. |
| `bot_aliases` | comma-separated strings | `bot, 精华bot` | Names that trigger the 「@bot 答疑」 section. A message containing `@<alias>` (case-insensitive) is treated as a question/request aimed at the digest bot. Pick names that do NOT match any real group member or existing bot, to avoid ambiguity. |

A starter template lives at [EXTEND.md.example](EXTEND.md.example).

### First-Time Setup (BLOCKING)

If no EXTEND.md is found, do NOT silently proceed.

**Step A — Try to auto-discover `self_wxid` and `self_display` first.** Run (in order, stop at the first that succeeds):

```bash
# 1. If wx-cli exposes a whoami, use it
wx whoami --json 2>/dev/null

# 2. Otherwise, find self-sent messages in recent sessions
wx sessions --json --limit 20 2>/dev/null
```

For option 2, scan the sessions for any private/group thread the user has sent into and read one of their own `from_wxid` / `from_nickname` pairs. If you can confidently pre-fill both values, use them as defaults in the question below; otherwise leave the fields blank for the user to fill in.

**Step B — Confirm with one `AskUserQuestion` call (batched), pre-filling whatever auto-discovery found:**

- `self_wxid` (e.g., `wxid_abc123`) — fall-back hint: the user can find it with `wx contacts --query "<own nickname>"`, or by inspecting any of their own sent messages in `wx sessions --json`
- `self_display` (e.g., `宝玉`) — how they want their messages attributed
- `default_version` — pick one of `normal` / `roast` / `both`
- `data_root` — where digest folders live. Default: `{project_root}/wechat`. Enter a custom absolute path (e.g. `~/Documents/wechat-digests`) or leave blank for default.
- Save location — pick one of project / XDG / home

Write EXTEND.md to the chosen path. If the user provided a non-default `data_root`, include it as an uncommented line; otherwise omit it (the default applies automatically). Confirm "Preferences saved to [path]. Edit it any time to change defaults.", then continue with the digest workflow.

- 本主题的完整细节见 [references/workflow.md](references/workflow.md)。

## Storage layout

```
{data_root}/                                        # default: {project_root}/wechat/
└── {group_id}-{group_name}/                        # e.g. 12345678901@chatroom-相亲相爱一家人/
    ├── history.json                                # last digest pointer (fast)
    ├── history-digests.jsonl                       # append-only archive
    ├── memory.md                                   # 群级事实记忆（被指正/确认的事实）
    ├── 2026-03-12.md                               # normal digest, single date
    ├── 2026-03-12-roast.md                         # roast digest (only if generated)
    ├── 2026-03-10_2026-03-12.md                    # normal digest, date range
    ├── profiles/                                   # normal user profiles
    │   ├── onlytiancai-胡浩🐸.md
    │   └── ...
    ├── profiles-roast/                             # roast user profiles (only if any roast generated)
    │   ├── onlytiancai-胡浩🐸.md
    │   └── ...
    └── imgs/                                       # optional image-description files
        ├── 49661.txt                               # one-line plain text description
        └── ...
```

## Notes and limitations

- **Image content is opaque**. wx-cli does not decode chat images. The skill respects an `imgs/{message_id}.txt` extension point but does not auto-populate it. When a topic depends heavily on an image with no description file, the digest should say so honestly rather than invent visual content.
- **Reply attribution is best-effort**. If wx-cli's output exposes a quote/reply field, use it. Otherwise fall back to context and flag uncertain inferences in working notes.
- **Local time only**. Date parsing uses the agent's local time zone. Cross-time-zone group members may show timestamps that don't match their wall clock. Per the format rules, never use timestamps to infer sleep or location.
- **wx-cli reinit**. If `wx history` suddenly returns nothing after a WeChat restart, the keys may be stale. Tell the user to run `sudo wx init --force` (while WeChat is running) and retry.

---

## 来源与署名 / Source & Attribution

本技能收录自上游开源仓库 JimLiu/baoyu-skills（MIT，见该仓库 LICENSE 与版权声明，作者：JimLiu/baoyu-skills 上游（MIT））。
awesome-skillkit 保留上游正文与参考文件，仅补齐本仓库 frontmatter 元数据、为长参考文档增补目录、按本仓库链接口径归一化相对路径；同步上游时以官方仓库为准。
