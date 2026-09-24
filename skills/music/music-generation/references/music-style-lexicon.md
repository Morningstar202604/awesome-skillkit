# 音乐风格词库：曲风 · 情绪 · 编制 · 人声 · 制作（music-style-lexicon）

> 写生成音乐 prompt（Suno 类）时按槽位查这张表。**裸曲风名是最弱的指令**——只写 `pop` 等于让模型取它吃过的所有流行歌的平均值：平庸但不出错。
> **铁律**：五槽位公式按顺序填；8-15 个 tag 是甜点区（<5 留白给模型默认，>20 互相打架）；第一个 tag 权重最高。

## Table of Contents

- [一、五槽位公式](#一五槽位公式style-框按此顺序填)——Style 框按此顺序填
- [二、曲风族谱](#二曲风族谱大类--子流派--年代--签名乐器)——大类 → 子流派 × 年代 → 签名乐器
- [三、情绪 tag × BPM 对照](#三情绪-tag--bpm-对照情绪和速度打架必翻车)——情绪和速度打架必翻车
- [四、结构 tag](#四结构-taglyrics-框用非-bracket-文字会被唱出来)——Lyrics 框用
- [五、人声 tag 全集](#五人声-tag-全集)
- [六、乐器点名表](#六乐器点名表写具体别写类目)——写具体，别写类目
- [七、制作美学词](#七制作美学词mix-槽位)——mix 槽位
- [八、BPM 分区速查](#八bpm-分区速查)
- [九、负面清单](#九负面清单写了必翻车)——写了必翻车
- [十、现成种子](#十现成种子改词即用)——改词即用

## 一、五槽位公式（Style 框按此顺序填）

```
[曲风两级] + [情绪能量] + [人声三层] + [乐器点名] + [制作美学 + BPM 数字]
```

| 槽位 | 要点 | 差 | 好 |
|------|------|---|----|
| 1. 曲风 | **两级深度**：大类是"大陆"，sub-genre+年代是"街道定位"；混音色时主导曲风放最前 | `rock` | `garage rock revival, 1990s` |
| 2. 情绪 | **一个方向，不是三个**；情绪词比技术词管用（模型听过的情绪描述更多） | `emotional` | `quietly devastated` |
| 3. 人声 | **三层**：音色特征（raspy female）+ 唱法（breathy, close-mic'd）+ 处理（doubled, tape-slapped） | `female vocal` | `raspy female vocal, breathy delivery, doubled` |
| 4. 乐器 | **点名你会真正听到的东西**；2-3 个主奏足够，写具体型号质感 | `guitar and drums` | `clean jangly Telecaster, brushed drums` |
| 5. 制作 | 混音美学 + **显式 BPM 数字**（没数字模型漂向曲风平均值） | `produced well` | `lo-fi tape warmth, 92 BPM` |

- 弱：`sad piano song about losing someone`（四个词，四百种结果）
- 强：`chamber folk, quietly devastated, fragile male vocal barely above a whisper, felt piano, bowed cello, brushed snare, dry intimate mix with room tone, 68 BPM`

## 二、曲风族谱（大类 → 子流派 × 年代 → 签名乐器）

| 大类 | 子流派种子（直接抄） | 签名乐器/质感 |
|------|---------------------|--------------|
| 流行 | `Synth-pop, 1980s` / `indie pop` / `K-pop, 2020s` / `future bass` | analog synths、gated snare、sequenced bass |
| 嘻哈 | `Boom-bap, 1990s` / `trap` / `drill` / `phonk, 145 BPM` | dusty vinyl、punchy snare、808 bass、cowbell melody |
| 摇滚 | `garage rock revival` / `Thrash metal, 1980s` / `post-rock` | palm-muted riffs、double kick、失真墙 |
| 电子 | `Classic house, 1990s` / `melodic techno` / `liquid drum and bass` / `synthwave` | 909 kick、piano stabs、arpeggiated pad |
| R&B/灵魂 | `Southern soul, 1970s` / `neo soul` / `boom bap hip hop` | Hammond organ、horn section、gritty guitar |
| 民谣/乡村 | `indie folk` / `Americana` / `bossa nova` | fingerpicked acoustic、glockenspiel、kick drum stomp |
| 影视配乐 | `cinematic trailer, epic, tense` / `space ambient` | staccato strings、taiko hits、brass swells、granular synth |
| 布鲁斯 | `Delta blues` | resonator guitar、slide guitar、stomping foot |
| 中国风 | `Chinese traditional, pentatonic` | guzheng、erhu、pipa、dizi |

> 空槽位会被填上"这个曲风的平均值"——每一个槽都是你的选择权。

## 三、情绪 tag × BPM 对照（情绪和速度打架必翻车）

| 情绪 | tag | BPM 区间 | 禁配 |
|------|-----|---------|------|
| 欢快 | `joyful` `cheerful` `uplifting` | 120-140 | ✗ 慢于 100 |
| 哀伤 | `melancholic` `sad` `mournful` | 60-80 | ✗ 快于 110 |
| 浪漫 | `romantic` `intimate` `loving` | 70-90 | — |
| 紧张 | `tense` `suspenseful` `urgent` | 130-160 | ✗ 慢于 100 |
| 平静 | `calm` `peaceful` `relaxing` | 60-80 | ✗ 重失真 |
| 史诗 | `epic` `grandiose` | 60-90（慢而宏大） | — |
| 梦幻 | `dreamy` `ethereal` `floating` | 70-100 | — |
| 黑暗 | `dark` `ominous` `brooding` | 70-120 | — |

**反例**：`[lofi][bpm-150]`——lo-fi 语义自带 70-90 BPM，强行 150 两败俱伤。

## 四、结构 tag（Lyrics 框用；非 bracket 文字会被唱出来）

- 骨架：`[Intro]` → `[Verse 1]` → `[Pre-Chorus]` → `[Chorus]` → `[Verse 2]` → `[Chorus]` → `[Bridge]` → `[Chorus]` → `[Outro]`
- 带参数：`[Intro: Acoustic guitar]`、`[Outro: Fade out]`、`[Chorus x2]`、`[Verse: Rap]`、`[Solo: electric guitar]`
- 进阶（v5 级）：`[Callback: Chorus melody]`（结尾重现主歌钩子）、`[Drop]`、`[Build-up]`、`[Drum Break]`

## 五、人声 tag 全集

`solo vocal`（独唱）· `duet`（对唱）· `choir`（合唱）· `harmony`（和声层叠）· `falsetto`（假声）· `rap` · `growl`（金属嘶吼）· `whisper`（气声/ASMR）· `spoken-word`（念白）· `auto-tune`（电音处理）· `no-vocals` / `instrumental`（纯音乐）

人声三层写法叠加示例：`husky female vocal sitting behind the beat, close-mic'd, stacked doubles in chorus`

## 六、乐器点名表（写具体，别写类目）

| 类目 | 直接可抄 |
|------|---------|
| 键盘 | `felt piano`（毛毡钢琴）`rhodes` `Hammond organ` `analog synth` `arpeggiated pad` |
| 吉他 | `fingerpicked acoustic` `clean jangly Telecaster` `distorted-guitar` `palm-muted riffs` |
| 弦乐 | `bowed cello` `staccato strings` `brass swells` `harp` |
| 管乐 | `saxophone` `muted trumpet` `horn section` `flute` |
| 打击 | `brushed drums` `808 bass` `taiko hits` `shaker loops` `congas` |
| 质感 | `vinyl crackle` `tape saturation` `room tone` `granular synth` `sine drones` |

## 七、制作美学词（mix 槽位）

`lo-fi tape warmth`（磁带暖噪）· `glossy radio mix`（电台亮混）· `raw one-room recording`（一室 Raw）· `dry intimate mix with room tone`（干声近场）· `wide 1985 mix with gated reverb`（80 年代宽混）· `warm analog console saturation`（模拟台饱和）· `cavernous modern mix`（大空间现代混）· `mono 1968 mix, no reverb`（单声道复古）

## 八、BPM 分区速查

| BPM | 语义 | 适用 |
|-----|------|------|
| 40-60 | 极慢 | Ambient、冥想、睡眠 |
| 60-80 | 慢 | Ballad、民谣、R&B 慢歌 |
| 80-100 | 中速 | Pop、Soul |
| 100-120 | 轻快 | Dance-pop、Funk |
| 120-140 | 快 | Rock、EDM、House |
| 140+ | 极快 | Punk、DnB、Hardcore |

## 九、负面清单（写了必翻车）

- **模糊形容词**：`a nice song` / `very sad`——AI 不懂 nice，写 `melancholic, slow tempo, minor key, felt piano`
- **四曲风大杂烩**：`pop, rock, jazz, classical mix`——最多两族，主导在前（`indie pop with jazz influences`）
- **情绪×速度矛盾**：见第三节对照表
- **Style 框写歌词**：歌词只进 Lyrics 框；Style 框只放风格 tag
- **Lyrics 框裸文字**：非 `[tag]` 内容会被唱出来——段落说明一律用 bracket
- **无 BPM 数字**：不写数字就默认平均值漂移，永远显式给

## 十、现成种子（改词即用）

```
深夜爵士：jazz, smooth, intimate, upright-bass, brushed drums, piano, male-vocals, 70 BPM
复古电子：synthwave, 1980s, nostalgic, driving-beat, analog synths, gated snare, no-vocals, 128 BPM
夏日流行：future-bass, uplifting, summer-vibes, female-vocals, synth-plucks, 110 BPM
史诗预告：cinematic trailer, epic, tense, staccato strings, taiko drums, brass swells, choir stabs, instrumental, 60 BPM
国风氛围：Chinese traditional, pentatonic, peaceful, guzheng, erhu, flute, no-vocals, 65 BPM
```
