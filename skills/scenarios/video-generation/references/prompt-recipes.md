# Video Prompt Recipes

Formulas for composing generation prompts (Step 2 of SKILL.md). The gateway
renders what the prompt describes; vague prompts produce vague footage.

## Contents

- [The formula](#the-formula)
- [Worked examples](#worked-examples)
- [Image-to-video notes](#image-to-video-notes)

## The formula

One paragraph, four slots, in this order:

```
[主体 Subject] 在 [场景 Scene] 中 [动作 Action]，[氛围 Mood]，[镜头 Shot hint]
```

- **Subject**: concrete noun with 1–2 attributes ("一位穿蓝色围裙的咖啡师")
- **Scene**: place + time + light ("清晨的街角小店，暖色灯光")
- **Action**: one continuous motion, not a montage ("缓慢拉花并将杯子推向镜头")
- **Mood**: adjectives the renderer can lean on ("温馨、治愈、电影感")
- **Shot hint** (optional): "特写", "缓慢推进", "环绕" — one camera idea max

Rules of thumb:

1. One scene, one action per video. Six seconds cannot hold a story arc.
2. Physical verbs beat abstract verbs: "拿起、转动、递出" over "展示、体现".
3. Put the most important visual FIRST — early tokens weigh more.
4. No text-in-video requests; rendered text is unreliable across engines.

## Worked examples

Strong prompt (product intro, 16:9):

> 一只白色陶瓷马克杯放在原木桌面上，窗外晨光斜射进来形成柔和光斑，
> 咖啡缓缓注入杯中，热气轻轻升起，镜头从侧面缓慢推近至拉花特写，
> 温馨、专业、令人信赖的电影感氛围。

Weak prompt (same brief) and why it fails:

> 咖啡视频，要好看。

- No subject detail → engine picks a random cup; no scene → random backdrop;
  "好看" is not renderable; no motion → first frame frozen feel.

Strong prompt (vertical short, knowledge clip):

> 一位戴黑框眼镜的年轻讲师站在书架前，面对镜头微笑并抬起手中的笔记本，
> 明亮的日间办公室背景，节奏轻快、清晰明亮的科普氛围，中景固定机位。

## Image-to-video notes

The reference image fixes the SUBJECT and SCENE; your prompt then only needs
to specify MOTION and MOOD. Do not re-describe what the image already shows.

Good image-to-video prompt for a portrait photo:

> 人物保持姿势不变，头发被微风吹起，嘴角慢慢上扬露出微笑，
> 背景光斑轻微闪烁，整体氛围温柔自然。
