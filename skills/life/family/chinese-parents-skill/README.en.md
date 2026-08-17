<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo.jpg">
    <img src="assets/logo.jpg" alt="Chinese Parents Skill" width="180">
  </picture>
</p>

<h1 align="center">Chinese Parents Skill</h1>

<p align="center">
  <em>A Chinese-parent simulator — so what kind of mom did you get?</em>
</p>

<p align="center">
  <a href="https://github.com/weed33834/chinese-parents-skill/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/weed33834/chinese-parents-skill?style=flat-square&color=red" alt="License">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/releases">
    <img src="https://img.shields.io/github/v/release/weed33834/chinese-parents-skill?style=flat-square&color=orange" alt="Version">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/stargazers">
    <img src="https://img.shields.io/github/stars/weed33834/chinese-parents-skill?style=flat-square" alt="Stars">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/commits/main">
    <img src="https://img.shields.io/github/last-commit/weed33834/chinese-parents-skill?style=flat-square&color=blue" alt="Last Commit">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill/issues">
    <img src="https://img.shields.io/github/issues/weed33834/chinese-parents-skill?style=flat-square&color=green" alt="Issues">
  </a>
  <a href="https://github.com/weed33834/chinese-parents-skill">
    <img src="https://img.shields.io/github/repo-size/weed33834/chinese-parents-skill?style=flat-square" alt="Repo Size">
  </a>
</p>

<p align="center">
  <a href="README.md">中文</a> · <a href="README.en.md">**English**</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#what-this-is">What</a> ·
  <a href="#three-modes">Three Modes</a> ·
  <a href="#10-dimensions">10 Dimensions</a> ·
  <a href="#the-calculator">Calculator</a> ·
  <a href="#18-scenarios">Scenarios</a> ·
  <a href="#want-to-add-something">Contributing</a>
</p>

---

## What this is

Has your mom ever said *look at so-and-so's kid*?

Does she praise you for coming third, and then ask what the top scorer got?

This project isn't research. It does three things:

- **Simulate** — tell it what your mom is like, it plays her
- **Diagnose** — describe what she does, it back-solves a profile you can recompute yourself
- **Counterplay** — there's a conversation you've been putting off; it runs the rehearsal with you

Chinese parenting isn't one thing. Same "came third in the class": one mom scolds first and asks after, one praises first and asks after, one doesn't ask at all. Ten dimensions, 0-100 each, **59,049 possible parents** on paper.

**The whole point of this skill, in one sentence: rebuild a Chinese-parent profile you and someone else can both recompute.** Simulate, diagnose, counterplay — those are the means; the profile is the end. The "mom" it computes has to hold up (there's a formula), match up (ask about the same person twice, get the same report), and fail honestly (when the data's missing it says so, instead of making something up). The foundation v0.5 lays is exactly those three things: the multi-turn engine actually runs, the fake numbers are blocked, and every number in the docs has an assertion guarding it.

**The big change in v0.5**: v0.4 shipped a "calculator" but only computed the first turn — ask "what if I push back, how does she react" and it had no answer. Now the multi-turn state machine is fully implemented and the five-turn dialogue reproduces value-for-value. And missing dimensions are no longer silently filled with 50 (that was the fake-number trap v0.4 itself warned about) — they go through a three-tier confidence of known / inferred / blind plus contamination tracking.

---

## Three modes

### 1. Simulate

Give it a profile, it performs. **Multi-turn** — you can push back and watch her escalate.

```
You:  My mom runs a tight ship but she's soft underneath. I'm telling her
      I want to quit and go full-time on social media.

AI:   [Profile] Control Strict(72) · Warmth Warm(58) · Anxiety Anxious(60)
                · Values Traditional(30)
      [State]   TEMP 24 (braced) · BOND 69 · YIELD 70

      "Social media? What kind of job is that? Who pays your social
       insurance and housing fund?"
      ...
      ── TEMP 42 ↑18 (pressuring) │ BOND 66 ↓3 │ persuasion 12/70

You:  This is my business, stay out of it.

AI:   ── TEMP 75 ↑33 (volatile) │ BOND 58 ↓8
      "Your business? Name one thing in your entire life I haven't
       worried about. Fine. Your business. All of it, yours..."
```

*Social insurance and housing fund* is the benefits package attached to a "proper" job. When a Chinese parent reaches for that phrase, the word they mean is **stability**.

That line — *this is my business* — is `+40` on the landmine table, plus another `+10` against any parent with `CTL≥75`. **It's the worst value-for-money sentence in the whole vocabulary: you win the point and lose the round.**

### 2. Diagnose

Describe the behavior, it back-solves the profile. Or take the 30-question quiz.

```
  Control          █████████████████████░░░   88  Domineering
  Warmth           ██████░░░░░░░░░░░░░░░░░░   25  Rational
  Involvement      █████████████████░░░░░░░   70  Active
  Anxiety          ████████████████████░░░░   85  Panicked
  Communication    ████░░░░░░░░░░░░░░░░░░░░   18  Command
  Values           █████░░░░░░░░░░░░░░░░░░░   20  Traditional
  Finance          ███████░░░░░░░░░░░░░░░░░   30  Stingy
  Expectation      ██████████████████████░░   92  Extremely High
  Social           █████░░░░░░░░░░░░░░░░░░░   22  Restrictive
  Independence     ████░░░░░░░░░░░░░░░░░░░░   15  Do-it-all

  ── coupling rules triggered ──
   ▸ Pressure without warmth: the house runs like an admin office, orders only, no feedback loop
   ▸ Anxiety with nowhere to go: comes back out as steady nagging and displaced anger
   ▸ Love indexed to grades: bomb a test and lose the affection, silence is the punishment

  ── nearest anchors ──
   Tiger Parent   91%    biggest gaps  Anxiety 85 vs 65 · Control 88 vs 70
   Dominant Parent  91%    biggest gaps  Anxiety 85 vs 60 · Finance 30 vs 45

  ── how to read this ──
   You open inside the pressure band. No warm-up room, go straight to the point.
   YIELD 87. You will not accumulate that much persuasion in one sitting.
   The goal isn't to convince her. It's to reach the next round without burning BOND.
```

**These numbers aren't decoration.** v0.3 printed percentages too, and nowhere in the whole document was there an algorithm — ask about the same person twice, get two different reports. v0.4 ships the formulas and the calculator. Go check them.

### 3. Counterplay

New in v0.4, and the part most people actually came for.

Diagnosis tells you your mom is a Tiger Parent. What you want to know is **how do I even open my mouth about this**.

Counterplay gives you: a feasibility grade (some fights are unwinnable, and it will say so), three routes (head-on / flanking / done-deal), 12 tactics, a three-layer reaction tree, and what to do when it goes badly.

> **T4 · Face-Saving**
> A lot of the pressure in a Chinese family was never the parent's own. An aunt asked something at dinner, she had no answer, and the pressure rolls downhill to you.
> Hand her one line she can say at that table and you've taken the source away.
> The follow-up is colder: *"If someone really pushes, put me on the phone. I'll handle it."*
> She isn't asking for a wedding. She's asking not to be cornered at the dinner table.

*Face* (**面子** *miànzi*) is the standing she carries in front of relatives. Losing it in public is a real cost in a Chinese family, not a figure of speech.

---

## 10 dimensions

| Dimension | What it tracks | 0 end → 100 end |
|-----------|----------------|-----------------|
| Control `CTL` | How wide her jurisdiction runs | Hands-off · Moderate · Strict · Domineering |
| Warmth `WRM` | The volume of emotional expression | Cold · Rational · Warm · Indulgent |
| Involvement `INV` | How much energy she actually puts in | Absent · Passive · Active · Overbearing |
| Anxiety `ANX` | How frightened she is of your future | Zen · Moderate · Anxious · Panicked |
| Communication `COM` | Which direction information flows | Command · Lecture · Discuss · Listen |
| Values `VAL` | Traditional or progressive | Traditional · Mixed · Progressive |
| Finance `FIN` | How money moves | Stingy · Moderate · Generous |
| Expectation `EXP` | How high the bar sits | None · Moderate · Extremely High |
| Social `SOC` | How she polices your friendships | Restrictive · Guided · Open |
| Independence `IND` | Train you, or do it for you | Do-it-all · Guide · Let Go |

**Two of these run against instinct:**

`Warmth` is not "how much she loves you." It's **how loud the love gets said**. Cold at 0 is love that never makes it out of her mouth; Indulgent at 100 is love thick enough to suffocate. Both ends are broken — it's the only dimension where the optimum sits in the upper middle, not at an end.

`Communication` is not "how much she talks." It's **which way information flows**. A parent at `COM=88` might say three sentences all evening, and all three are *"and then?"* and *"what do you think?"* Don't confuse a talker for a high score.

### What one dimension can't show you

What actually decides how hard a parent is to deal with is usually a combination:

| Combination | What it is |
|-------------|------------|
| `COM` high + `CTL` high | **Democracy Theater**. She'll sit through all forty minutes of your case, then execute the original plan |
| `INV` low + `COM` low + `CTL` mid | **Zombie Parenting** (*zhàshī-shì*, "the corpse sits up"). Gone for months, then awake overnight and running everything, with zero lead-up |
| `CTL` high + `WRM` high | **Sweet Suffocation**. No shouting, no insults — just sighing and wiping her eyes. You can't even find the door into the argument |
| `ANX` high + `FIN` low | Anxiety with nowhere to spend itself, converted into nagging and displaced blame |
| `EXP` high + `WRM` low | Love indexed to grades. Bomb a test, lose the affection; going quiet is the main punishment |

**Democracy Theater is the hardest one to name**, because the process satisfies every published standard for "healthy communication." You can't even find grounds to be angry, so you start doubting yourself instead.

There's exactly one test: **after she heard you out, did the conclusion move?**

### The eight anchors

Not eight kinds of parent — eight coordinates on the map, used for similarity scoring. Your mom almost certainly sits somewhere between them. Full vectors in [dimensions.md](references/dimensions.md).

| Anchor | `--type` value | In one line |
|--------|----------------|-------------|
| Tiger Parent | `虎妈虎爸` | Highest bar, lowest warmth, no negotiation |
| Hustle Parent | `鸡娃家长` | *jīwá*, "chicken-blood kid" — every waking hour booked with tutoring and enrichment; spends freely, panics constantly |
| Helicopter Parent | `直升机父母` | Involvement pushed well past the point of being useful |
| Zen Parent | `佛系家长` | *fóxì*, "Buddha-style" — genuinely doesn't push |
| Open-minded Parent | `开明家长` | Listens, and the conclusion can actually move |
| Dominant Parent | `强势家长` | Decides for you, doesn't explain, escalates if you resist |
| Zombie Parenting | `诈尸式育儿` | Absent by default, then suddenly awake and in total command |
| Widowed Parenting | `丧偶式育儿` | *sàng'ǒu-shì*, "parenting as if widowed" — one parent lives in the house and is functionally not there |

The gap between the last two is only `CTL` and `ANX`. Widowed genuinely checked out (`CTL=12`); Zombie ignores you for months and then goes all the way in (`CTL=30` paired with `COM=12`, pure command). Zombie does more damage — intervention with no runway.

---

## The calculator

### Profile

```bash
# Some dimensions given, the rest inferred from coupling rules
python3 scripts/profile.py --scores "CTL=88,ANX=85,EXP=92"

# Load an anchor (names are Chinese-only for now; this one is Tiger Parent)
python3 scripts/profile.py --type 虎妈虎爸

# Answer the 30 questions interactively
python3 scripts/profile.py --quiz

# The answer string is archivable — replay it any time
python3 scripts/profile.py --answers cdcbbdcddcaabbcbabcabdddaacbad

# Machine-readable
python3 scripts/profile.py --scores "..." --json
```

Standard library only, zero dependencies, Python 3.8+. Prints the dimension bars, the extreme dimensions, the coupling rules you hit, the anchor ranking, six dynamics values and how to read them.

**Missing dimensions aren't guessed:** give it only `CTL=90` and the rest get inferred from coupling rules (`inferred` — direction trustworthy, magnitude not) or hard-filled to 50 (`blind` — conclusion void). When a hard-filled dimension contaminates a downstream dynamics value, the output marks it `⚠` and **suppresses the similarity score and the readings**; with ≥4 `blind` dimensions it simply says "no similarity reported." Better to say less than to make things up.

**Every number in the docs recomputes to what this script says**, including the table of 8 anchors × 6 dynamics values. A mismatch is a bug — open an issue.

### Multi-turn simulation

```bash
# See every available move in the landmine / de-escalation tables
python3 scripts/profile.py --list-moves

# Run the built-in five-turn example (dynamics.md §7.2)
python3 scripts/profile.py --simulate-demo

# Specify your own move sequence, starting BOND, and channel
python3 scripts/profile.py --type 虎妈虎爸 \
    --simulate T21 T9 T1 C2 C18 --bond 69 --channel wechat --who 我
```

`--simulate` prints each turn as a line-by-line ledger: which line, how many degrees up or down, how BOND moved, where persuasion stands; and at the end, a **verdict** (real concession / fake concession / no concession) and **the most expensive line** — the one where you won the point and bled the most relationship points. Off-face channels (phone / WeChat) discount heating by 0.8, WeChat another 0.8, but multiply BOND damage by 1.2.

**This isn't a demo.** It's the executable spec of `dynamics.md` §§4-7: bonuses take only the single highest match, not a sum; net heating per turn caps at +35; once TEMP≥85 only `[高温]` entries fire, at ×1.5; the second use of a de-escalation line is ×0.5, the third ×0. The five-turn `--simulate-demo` matches §7.2 value-for-value, and any formula change gets caught on the spot by the 68 assertions in `scripts/test_profile.py`.

---

## 18 scenarios

The first 10 are old, the last 8 are new in v0.4. Full matrix in [scenarios.md](references/scenarios.md).

| | Scenario | Key dimensions |
|---|----------|----------------|
| A | School / work performance | Control · Anxiety · Expectation |
| B | Life choices (quitting, startups, gap years) | Values · Control · Anxiety |
| C | Dating and marriage | Values · Social · Control |
| D | Spending and money | Finance · Control |
| E | Living together at home | Warmth · Involvement |
| F | Friends and social life | Social · Control |
| G | Screens and devices | Control · Anxiety |
| H | Health and habits | Warmth · Involvement |
| I | Appearance | Values · Control |
| J | Schooling and cram schools | Anxiety · Finance · Expectation |
| **K** | **Relative gatherings and the comparison circuit** | Anxiety · Social · Expectation |
| **L** | **Marriage pressure, grandchildren, bride price** | Values · Anxiety · Control |
| **M** | **Buying a home and family money** | Finance · Control · Independence |
| **N** | **Elder care and support obligations** | Warmth · Involvement · Finance |
| **O** | **Multiple children and favoritism** | Warmth · Finance · Expectation |
| **P** | **Emotions and mental health** | Values · Warmth · Communication |
| **Q** | **Privacy (she went through your phone)** | Control · Social |
| **R** | **Careers your relatives can't name** | Values · Anxiety · Expectation |

*Bride price* (**彩礼** *cǎilǐ*) is the cash and goods the groom's side transfers to the bride's family before a wedding — still an open negotiation across much of China, and often the thing the two families are actually fighting about.

Among the new ones: **M** was never an argument about money, it's an argument about how much say you keep after you take it. And in **O**, the wound was never the 100,000 yuan that went to your brother — it's hearing her say, about you, *forget it, don't count on that one*.

---

## Repository layout

```
chinese-parents-skill/
├── SKILL.md                    # Entry point: mode routing, load navigation
├── references/
│   ├── dimensions.md           # The 10-dimension numeric core (single source of truth)
│   ├── scenarios.md            # 18 scenarios × dimension impact matrix
│   ├── dynamics.md             # Emotion state machine, landmine/de-escalation tables, yield rules
│   ├── diagnosis.md            # Diagnostic flow, differential diagnosis, report format
│   ├── counterplay.md          # Counterplay: routes, 12 tactics, reaction trees
│   ├── family-system.md        # Multi-role family system, background modifiers
│   ├── quotes.md               # Quote library, translation table for what she really means
│   ├── quirks.md               # Absurd-parent casebook: 17 distorted-thinking templates + scenario cases + anti-logic simulation rules
│   └── quiz.md                 # 30-question quiz bank (auto-exported from the script)
├── scripts/
│   └── profile.py              # Profile calculator, standard library only
├── README.md · README.en.md · README.ja.md · README.ko.md · CHANGELOG.md
├── CONTRIBUTING.md · CODE_OF_CONDUCT.md · LICENSE
└── assets/ · .github/
```

SKILL.md used to be one 627-line file. It's now an entry point plus on-demand references. **Not for tidiness — a 26KB single file went into context in full, every single time.**

---

## Boundaries

This skill doesn't do family counseling, doesn't do family therapy, and doesn't take a side. It also won't:

- Simulate physical violence, abuse, or confinement
- Use regional stereotypes, or pin behavior on someone's hometown, education level, or job
- Stick labels like "personality disorder" or "narcissistic abuse" on anyone — it describes behavior patterns, it doesn't make clinical calls
- Tack *deep down your parents love you* onto the end of a simulation

**If your situation involves physical safety, severe emotional abuse, financial coercion, or thoughts of hurting yourself, don't come here looking for a script.** That isn't a problem better phrasing solves. Find someone who can actually help you, offline.

---

## Want to add something

Does your mom have a line this project hasn't collected? Does some scenario not sound like her? Is a dimension's scoring band off?

Don't sit on it. This project runs on shared material, and whatever your mom does, someone else's mom probably does too.

- Something's broken → [open an Issue](https://github.com/weed33834/chinese-parents-skill/issues/new?template=bug_report.md)
- Got an idea → [feature request](https://github.com/weed33834/chinese-parents-skill/issues/new?template=feature_request.md)
- New scenario → [scenario suggestion](https://github.com/weed33834/chinese-parents-skill/issues/new?template=scenario_suggestion.md)

Read [CONTRIBUTING.md](CONTRIBUTING.md) before you send a PR. If you touched a formula or a dimension vector, run `scripts/profile.py` and confirm the numbers in the docs still line up.

## License

[Apache-2.0](LICENSE) © 2026 badhope
