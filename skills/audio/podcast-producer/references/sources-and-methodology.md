# Sources and Methodology

This skill is self-authored; its methodology skeleton is distilled from the following public materials (structural borrowing only, no text copied):

| Source | Type | What was borrowed | License/attribution |
|------|------|----------|-----------|
| [Podify in practice (sammii.dev)](https://sammii.dev/blog/podify-podcast-generator-003-per-episode) | 🟡 practical blog | The "pure voiceover script" iron rule (TTS reads every marker verbatim); segmented JSON structure (title/segments/showNotes); segmented synthesis + ffmpeg concat joining; no BGM fade needed for a clean finish | Practical methodology cited with attribution |
| [inference-sh/skills ai-podcast-creation](https://github.com/inference-sh/skills) | open-source skill | Multi-voice dialogue split mode (host/guest synthesized separately then crossfaded together); document-to-podcast (NotebookLM-style) two-step: first extract key points then expand into dialogue | MIT ecosystem, structural borrowing with attribution |
| [Open-source podcast pipeline overview (ainomam.com)](https://www.ainomam.com/post/ai-podcast-generator-open-source-20260807) | 🟡 third-party | The boundary judgment that "explanatory/news shows are easy, improvisational banter is not"; long content is more natural when segmented; AI voice disclosure obligation | Experience cited with attribution |
| Kokoro-82M / Qwen3-TTS / Whisper V3 Turbo / PODTILE ecosystem | 🟢🟡 model ecosystem | TTS selection and capability boundaries (see tts-voice-director's voice-catalog.md) | Model capability facts, verification method noted |

## Design decisions

1. **script_lint.py as a standalone script**: Podify's "pure voiceover script" lesson is worth machine enforcement—
   a human checking a 5000-word script will always miss something, while regex checking markers costs nothing.
2. **Segmented script rather than whole-script**: three sources (Podify/inference.sh/overview) all point to the same
   practical lesson—generate in segments then join; high naturalness and repairability.
3. **Duration back-calculated from word count**: Chinese voiceover at 150-180 words/minute is the community-accepted conversion, written into the rules to avoid the systematic overrun of "a 5-minute show written as 3000 words."
