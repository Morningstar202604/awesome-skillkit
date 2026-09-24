# Sources and Methodology

This skill is self-authored; its methodology skeleton is distilled from the following public materials (structural borrowing only, no text copied):

| Source | Type | What was borrowed | License/attribution |
|------|------|----------|-----------|
| [Podify 实战（sammii.dev）](https://sammii.dev/blog/podify-podcast-generator-003-per-episode) | 🟡 实战博客 | 「纯口播词」铁律（TTS 原样读出一切标记）；分段 JSON 结构（title/segments/showNotes）；分段合成 + ffmpeg concat 拼接；无 BGM fade 处理即干净成片 | 实践方法论引用并署名 |
| [inference-sh/skills ai-podcast-creation](https://github.com/inference-sh/skills) | 开源技能 | 多声线对话拆分模式（host/guest 分开合成再 crossfade 合并）；文档转播客（NotebookLM 式）两步法：先提炼要点再展开对话 | MIT 生态，结构借鉴并署名 |
| [开源播客流水线综述（ainomam.com）](https://www.ainomam.com/post/ai-podcast-generator-open-source-20260807) | 🟡 第三方 | 「解释型/新闻型好做、即兴插科打诨做不了」的边界判断；长内容分段更自然；AI 声音披露义务 | 经验引用并署名 |
| Kokoro-82M / Qwen3-TTS / Whisper V3 Turbo / PODTILE 生态 | 🟢🟡 模型生态 | TTS 选型与能力边界（见 tts-voice-director 的 voice-catalog.md） | 模型能力事实，标注核实方法 |

## Design decisions

1. **script_lint.py 独立成脚本**：Podify 的「纯口播词」教训值得机器守门——
   人检查 5000 字脚本必漏，正则查标记零成本。
2. **分段脚本而非整篇**：三条来源（Podify/inference.sh/综述）都指向同一条
   实战经验——分段生成再拼接，自然度与可修复性双高。
3. **时长按字数倒推**：中文口播 150-180 字/分钟是社区公认换算，写进规则
   避免"5 分钟节目写 3000 字"的系统性超支。
