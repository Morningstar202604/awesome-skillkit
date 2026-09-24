# Music Style Lexicon: Genre · Emotion · Instrumentation · Vocals · Production (music-style-lexicon)

> Look up this table by slot when writing generative-music prompts (Suno-class). **A bare genre name is the weakest command**—writing only `pop` is asking the model to average all the pop songs it has eaten: mediocre but safe.
> **Iron rule**: fill the five-slot formula in order; 8-15 tags is the sweet spot (<5 leaves default blank for the model, >20 they fight each other); the first tag has the highest weight.

## Table of Contents

- [1. Five-slot formula](#1-five-slot-formula-fill-the-style-box-in-this-order)—fill the Style box in this order
- [2. Genre family tree](#2-genre-family-treebroad-category--subgenre--era--signature-instrument)—broad category → subgenre × era → signature instrument
- [3. Emotion tag × BPM mapping](#3-emotion-tag--bpm-mappingemotion-and-tempo-fighting-always-crashes)—emotion and tempo fighting always crashes
- [4. Structure tags](#4-structure-tagsused-in-the-lyrics-box-non-bracket-text-will-be-sung)—used in the Lyrics box
- [5. Vocals tag set](#5-vocals-tag-set)
- [6. Instrument call-sheet](#6-instrument-call-sheetname-specifics-not-categories)—name specifics, not categories
- [7. Production aesthetic words](#7-production-aesthetic-wordsmix-slot)—mix slot
- [8. BPM zone quick reference](#8-bpm-zone-quick-reference)
- [9. Negative list](#9-negative-listwriting-these-always-crashes)—writing these always crashes
- [10. Ready-made seeds](#10-ready-made-seedsswap-words-and-go)—swap words and go

## 1. Five-slot formula (fill the Style box in this order)

```
[genre two-level] + [emotion energy] + [vocals three layers] + [instruments named] + [production aesthetic + BPM number]
```

| Slot | Key point | Bad | Good |
|------|------|---|----|
| 1. Genre | **Two-level depth**: broad category is the "continent," sub-genre+era is the "street address"; when blending timbres, lead genre first | `rock` | `garage rock revival, 1990s` |
| 2. Emotion | **One direction, not three**; emotion words beat technical words (the model has heard more emotion descriptions) | `emotional` | `quietly devastated` |
| 3. Vocals | **Three layers**: timbre trait (raspy female) + delivery (breathy, close-mic'd) + processing (doubled, tape-slapped) | `female vocal` | `raspy female vocal, breathy delivery, doubled` |
| 4. Instruments | **Name what you'll actually hear**; 2-3 lead instruments enough; write concrete model texture | `guitar and drums` | `clean jangly Telecaster, brushed drums` |
| 5. Production | Mix aesthetic + **explicit BPM number** (without a number the model drifts to the genre average) | `produced well` | `lo-fi tape warmth, 92 BPM` |

- Weak: `sad piano song about losing someone` (four words, four hundred outcomes)
- Strong: `chamber folk, quietly devastated, fragile male vocal barely above a whisper, felt piano, bowed cello, brushed snare, dry intimate mix with room tone, 68 BPM`

## 2. Genre family tree (broad category → subgenre × era → signature instrument)

| Broad category | Subgenre seeds (copy directly) | Signature instrument/texture |
|------|---------------------|--------------|
| Pop | `Synth-pop, 1980s` / `indie pop` / `K-pop, 2020s` / `future bass` | analog synths, gated snare, sequenced bass |
| Hip-hop | `Boom-bap, 1990s` / `trap` / `drill` / `phonk, 145 BPM` | dusty vinyl, punchy snare, 808 bass, cowbell melody |
| Rock | `garage rock revival` / `Thrash metal, 1980s` / `post-rock` | palm-muted riffs, double kick, wall of distortion |
| Electronic | `Classic house, 1990s` / `melodic techno` / `liquid drum and bass` / `synthwave` | 909 kick, piano stabs, arpeggiated pad |
| R&B/Soul | `Southern soul, 1970s` / `neo soul` / `boom bap hip hop` | Hammond organ, horn section, gritty guitar |
| Folk/Country | `indie folk` / `Americana` / `bossa nova` | fingerpicked acoustic, glockenspiel, kick drum stomp |
| Film score | `cinematic trailer, epic, tense` / `space ambient` | staccato strings, taiko hits, brass swells, granular synth |
| Blues | `Delta blues` | resonator guitar, slide guitar, stomping foot |
| Chinese style | `Chinese traditional, pentatonic` | guzheng, erhu, pipa, dizi |

> Empty slots get filled with "the average of this genre"—every slot is your choice.

## 3. Emotion tag × BPM mapping (emotion and tempo fighting always crashes)

| Emotion | tag | BPM range | Forbidden pairing |
|------|-----|---------|------|
| Cheerful | `joyful` `cheerful` `uplifting` | 120-140 | ✗ slower than 100 |
| Sad | `melancholic` `sad` `mournful` | 60-80 | ✗ faster than 110 |
| Romantic | `romantic` `intimate` `loving` | 70-90 | — |
| Tense | `tense` `suspenseful` `urgent` | 130-160 | ✗ slower than 100 |
| Calm | `calm` `peaceful` `relaxing` | 60-80 | ✗ heavy distortion |
| Epic | `epic` `grandiose` | 60-90 (slow and grand) | — |
| Dreamy | `dreamy` `ethereal` `floating` | 70-100 | — |
| Dark | `dark` `ominous` `brooding` | 70-120 | — |

**Counter-example**: `[lofi][bpm-150]`—lo-fi semantics carry 70-90 BPM; forcing 150 loses both.

## 4. Structure tags (used in the Lyrics box; non-bracket text will be sung)

- Skeleton: `[Intro]` → `[Verse 1]` → `[Pre-Chorus]` → `[Chorus]` → `[Verse 2]` → `[Chorus]` → `[Bridge]` → `[Chorus]` → `[Outro]`
- With parameters: `[Intro: Acoustic guitar]`, `[Outro: Fade out]`, `[Chorus x2]`, `[Verse: Rap]`, `[Solo: electric guitar]`
- Advanced (v5-level): `[Callback: Chorus melody]` (recall the verse hook at the end), `[Drop]`, `[Build-up]`, `[Drum Break]`

## 5. Vocals tag set

`solo vocal` · `duet` · `choir` · `harmony` (layered backing) · `falsetto` · `rap` · `growl` (metal scream) · `whisper` (breathy/ASMR) · `spoken-word` · `auto-tune` · `no-vocals` / `instrumental`

Vocals three-layer stacked example: `husky female vocal sitting behind the beat, close-mic'd, stacked doubles in chorus`

## 6. Instrument call-sheet (name specifics, not categories)

| Category | Copy directly |
|------|---------|
| Keys | `felt piano` `rhodes` `Hammond organ` `analog synth` `arpeggiated pad` |
| Guitar | `fingerpicked acoustic` `clean jangly Telecaster` `distorted-guitar` `palm-muted riffs` |
| Strings | `bowed cello` `staccato strings` `brass swells` `harp` |
| Winds | `saxophone` `muted trumpet` `horn section` `flute` |
| Percussion | `brushed drums` `808 bass` `taiko hits` `shaker loops` `congas` |
| Texture | `vinyl crackle` `tape saturation` `room tone` `granular synth` `sine drones` |

## 7. Production aesthetic words (mix slot)

`lo-fi tape warmth` · `glossy radio mix` · `raw one-room recording` · `dry intimate mix with room tone` · `wide 1985 mix with gated reverb` · `warm analog console saturation` · `cavernous modern mix` · `mono 1968 mix, no reverb`

## 8. BPM zone quick reference

| BPM | Semantics | Fits |
|-----|------|------|
| 40-60 | Very slow | Ambient, meditation, sleep |
| 60-80 | Slow | Ballad, folk, slow R&B |
| 80-100 | Mid-tempo | Pop, Soul |
| 100-120 | Brisk | Dance-pop, Funk |
| 120-140 | Fast | Rock, EDM, House |
| 140+ | Very fast | Punk, DnB, Hardcore |

## 9. Negative list (writing these always crashes)

- **Vague adjectives**: `a nice song` / `very sad`—AI doesn't understand nice; write `melancholic, slow tempo, minor key, felt piano`
- **Four-genre mishmash**: `pop, rock, jazz, classical mix`—at most two families, lead first (`indie pop with jazz influences`)
- **Emotion×tempo contradiction**: see section 3 mapping
- **Lyrics in the Style box**: lyrics go only in the Lyrics box; the Style box holds only style tags
- **Bare text in the Lyrics box**: non-`[tag]` content gets sung—always use brackets for section directions
- **No BPM number**: without a number it drifts to the default average; always give it explicitly

## 10. Ready-made seeds (swap words and go)

```
Late-night jazz: jazz, smooth, intimate, upright-bass, brushed drums, piano, male-vocals, 70 BPM
Retro electronic: synthwave, 1980s, nostalgic, driving-beat, analog synths, gated snare, no-vocals, 128 BPM
Summer pop: future-bass, uplifting, summer-vibes, female-vocals, synth-plucks, 110 BPM
Epic trailer: cinematic trailer, epic, tense, staccato strings, taiko drums, brass swells, choir stabs, instrumental, 60 BPM
Chinese-style ambient: Chinese traditional, pentatonic, peaceful, guzheng, erhu, flute, no-vocals, 65 BPM
```
