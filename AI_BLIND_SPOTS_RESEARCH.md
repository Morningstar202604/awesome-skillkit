# AI Blind Spots: Human-Only Knowledge Worth Turning Into Skills

**Research date:** 2026-09-25
**Scope:** Domains where LLMs are *structurally* weak (not just "could be better"), where knowledge can be encoded as rules / checklists / decision tables / phrase banks, and where users have recurring real-world need.
**Method:** General web + Chinese-language search across social practice, life-pitfall, cognitive, and sensory domains; cross-referenced with 2025–2026 LLM-limitations literature and benchmarks.

---

## How to read the verdicts

A domain is a **STRONG CANDIDATE** only if all four hold:
- (a) Users repeatedly ask for it; (b) AI *concretely gets it wrong* (not just "generic"); (c) the knowledge decomposes into rules / tables / scripts / checklists; (d) it is safe and ethical.

**MARGINAL** = useful but either AI already does it adequately, knowledge is too vague to encode, or frequency is low.
**REJECT** = unsafe, manipulative, illegal, or already well-covered.

---

## PART 1 — CHINESE SOCIAL & INTERPERSONAL COMMUNICATION

This is the richest blind-spot area: LLM training data is Western-centric (low-context, direct), while Chinese social scripts are high-context, hierarchical, homophone-coded, and locally variant. Independent benchmarks confirm the gap: an arXiv 2026 paper on *Chinese Mock Politeness* found Kimi and peers misclassify pseudo-polite speech as genuine politeness in zero-shot settings, and cross-cultural studies found Chinese refusals come out either blunt ("这个任务无法完成") or stiffly over-polite in ways that feel robotic. The "我会稳稳地接住你" phrase became a Chinese-internet meme precisely because ChatGPT's Chinese emotional register is uncanny.

---

### 1.1 Chinese Banquet & Toast Etiquette (座次 / 敬酒)

**Domain:** Round-table seating hierarchy, toasting order, and glass-courtesy rules for Chinese business/family banquets.

**What AI gets wrong:**
- Ask an LLM "where should I sit at a Chinese dinner?" and it produces a generic paragraph ("the guest of honor faces the door") without the operational rules: *which* side (left > right at equal distance), that the host sits facing the kitchen/door (vulnerable position), that the deputy-host (副陪) sits opposite the host to keep guests drinking.
- It does not know the **toasting iron law**: go in order (先长后幼、先上后下、先客后主), clockwise, never skip a person (跳敬). Skipping someone is read as a deliberate snub.
- It does not know the **glass-height rule**: junior's rim must sit *below* the senior's rim; equals clink rims level. The "one inch" difference is where contracts get signed or lost.
- It flattens business vs. friend contexts — a rule that applies at a client dinner (toast the client's #1 first, then by rank) is wrong at a friend's casual hotpot.

**Actionable knowledge that exists:**
1. **Seating decision table** (round table): facing-door seat = 主位 (host/elder/boss); immediately to its right = 主宾 (guest of honor); left = 二宾; opposite 主位 = 副陪; remaining seats fill by descending seniority. Rectangle tables: center of long side > ends.
2. **Toast-order algorithm**: (1) host opens with a 开场白; (2) guests toast host in reverse-seniority? No — *after* the host, juniors toast seniors, clockwise, one pass; (3) one-on-one toasts may follow, rim-down rule applies; (4) never toast the most junior first.
3. **Red flags checklist** (what to avoid): 跳敬 (skipping), rim above senior's, empty glass before the senior finishes, refilling someone's glass below 1/3 without being asked, splitting a communal dish with your own chopsticks (翻菜).

**Frequency:** High for anyone in corporate China, sales, government-adjacent work, or who hosts/attends family weddings. Mid-frequency for general white-collar users.

**Safety assessment:** Low risk. This is cultural competence, not manipulation. Bound it: "guidelines for respect; does not instruct excessive drinking or peer-pressure drinking." Explicitly discourage 劝酒 (coercive toasting).

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `chinese-banquet-etiquette`* — takes context (business/family/friends, who is host, ranks/ages, city region if known) and outputs seating diagram description + toast order + what to say + what not to do.

---

### 1.2 Chinese Gift Money & Gift Taboos (随份子 / 送礼禁忌)

**Domain:** How much red envelope (红包/随份子) to give by relationship and occasion, plus homophone/number gift taboos.

**What AI gets wrong:**
- LLMs will happily suggest "give an auspicious amount like 666" without the **relationship-tier table** that Chinese users actually need. A generic answer does not tell them 200 vs 500 vs 1000 vs 2000 by relationship.
- It may not flag that **500 is locally awkward in some regions** (associated with white-funerty money / missing 100 from 600?), or that amounts should be *even numbers* for celebrations (双数) — though one veteran insider noted "200块不如180块显得懂规矩" (188/168 carry the 8-wealth homophone; odd-number single-item gifts are wrong).
- Gift-taboo homophones are exactly the kind of culturally-coded fact LLMs under-weight: 送钟=送终 (clock = attending a funeral), 伞=散 (umbrella = breakup), 梨=离 (pear = separation), 鞋=让人走 (shoes = walk away), knives/scissors = 一刀两断 (cutting ties). Western-trained models have no reason to weight these.

**Actionable knowledge that exists:**
1. **Amount table (mainland urban reference, 2025–2026):**

   | Relationship | Wedding 随份子 | Notes |
   |---|---|---|
   | 同事 / casual colleague | ¥200 | face-saving, not heavy |
   | 远亲 / distant relative | ¥200 | ritual amount |
   | 近邻 / neighbor | ¥300 | |
   | 同学 / classmate | ¥500 | |
   | 近亲 / close relative | ¥500–1000 | |
   | 领导 / boss | ¥600 | sensitive — must look like etiquette, not bribery |
   | 好友 / close friend | ¥600–1000 | 666/888/999 lucky variants |
   | 闺蜜 / best friend | ¥1000+ | |
   | 兄弟姐妹 / siblings | ¥2000+ | |

   (Taiwan / banquet-venue tier adjusts upward: casual ¥1200–2000 NTD, hotel ¥2600+.)
2. **Number rules:** even numbers for weddings/celebrations; avoid 4 (sounds like death); prefer 6 (smooth), 8 (wealth), 9 (long-lasting). Funeral money (白事) is the *opposite* — odd numbers, no red envelope, white/blue paper.
3. **Gift taboo lookup table:** clock/watch, umbrella, pear, shoes, white flowers, handkerchiefs, green hat (绿帽子=cuckold), scissors/knives — with safe swaps (tea set instead of clock; scarf instead of umbrella; apple/orange instead of pear).
4. **Bribery boundary:** above a certain amount to a boss/official, "gift" becomes 行贿 — the skill must flag when an amount crosses from etiquette into compliance risk.

**Frequency:** Medium-high. Weddings, Lunar New Year, Mid-Autumn, hospital visits, business gifts — recurring but event-driven (a user might query 5–15 times/year).

**Safety assessment:** Medium-low. Bound it explicitly: (a) never advise gifts to government officials above nominal value; (b) note regional variation and "when in doubt, match the group" (跟着大家); (c) never frame as buying favor.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `chinese-gift-etiquette`* — inputs: occasion (wedding/funeral/New Year/hospital visit/thank-you), relationship tier, city/region, budget range; outputs: amount range, lucky-number variants, taboo gifts to avoid, safe alternatives, red-envelope writing convention (金额大写, signature on back).

---

### 1.3 Chinese High-EQ Phrase Banks (拒绝 / 安慰 / 道歉 / 批评)

**Domain:** Word-for-word Chinese scripts for declining, comforting, apologizing, and criticizing without causing offense.

**What AI gets wrong:**
- Research cited above: when asked to refuse a superior in Chinese, LLMs either output a blunt "这个任务无法完成" (too direct, sounds insubordinate) or stiff, over-padded formal language that reads as translated.
- Comfort-seeking: users complain AI says hollow things ("别难过了，没事的，想开点") — which the actual veteran advice explicitly calls *the worst possible thing to say*. Chinese comfort wisdom says the #1 rule is: **don't reason, don't cheer up, mirror the emotion and stay present.**
- Criticism: AI defaults to either harsh ("你做得不好") or mushy Western sandwich feedback that Chinese recipients find artificial. The working Chinese pattern is: **replace blame with joint problem-solving** ("我们一起看看哪里可以优化"), name the behavior not the person, ask about blockers instead of accusing ("是不是遇到什么卡点了？").

**Actionable knowledge that exists:**
1. **Refusal formula (三明治拒绝法 / sandwich):** 肯定 + 拒绝理由 + 替代方案. Concrete example for a colleague asking you to cover extra work: "谢谢你信任我愿意找我。可惜我今天手头任务已经排满，实在抽不出时间，你可以先找XX看看 / 这个事我建议走XX流程。"
2. **Comfort formula:** 描述你看到的 + 表达你理解的感受 + 陪伴, *no advice*. Example: "我看出来你这次真的挺受伤的，换谁都会难受。我不催你想通，就在这陪你。" Explicitly ban: 别难过/想开点/这有什么大不了的/我早就跟你说过.
3. **Apology formula:** 认行为 (specific behavior, not vague "sorry") + 影响 (impact) + 补救方案 (remedy). "确实是我考虑不周造成的问题，我梳理了两个补救方案，您看优先执行哪一个？"
4. **Criticism translation table:** 你不行 → "这个任务对你可能挑战有点大，我们一起拆解一下"; 你效率太低 → "是不是遇到什么卡点了？看看我能提供什么支持"; 你听不懂吗 → "可能是我没讲清楚，我再换个方式".
5. **Accepting-an-apology swaps:** never say 算了吧 (sounds dismissive), say "没事啦，我知道你不是故意的，别放在心上".

**Frequency:** High. This is a daily need in Chinese work and life.

**Safety assessment:** Low. This is social skill, not manipulation. Bound it: do not produce scripts for lying, gaslighting, or PUA; scripts must be honest and respectful.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `chinese-high-eq-phrases`* — scenario picker (decline boss / decline client / comfort grieving friend / apologize to spouse / give negative feedback to report / decline a favor) → outputs 2–3 register options (formal/casual/close) + what *not* to say.

---

### 1.4 Reading Chinese Subtext (潜台词 / 言外之意)

**Domain:** Decoding high-context Chinese utterances where the literal meaning is the opposite of the intended one.

**What AI gets wrong:**
- The Oreate AI analysis is explicit: models trained on low-context (US/Northern European) data read "我们再考虑考虑" (we'll consider it) as a genuine maybe / sales lead, when in Chinese business context it is almost always a polite **no**. "我尽量" = 这事我办不了. "原则上可以" = 实际不行. "哈哈" from a boss = discomfort, not amusement. "再说吧" = refusal.
- Benchmarks on mock politeness show models literally cannot tell sarcastic/pseudo-politeness from real politeness without explicit definitions.

**Actionable knowledge that exists:**
1. **Subtext lookup table (literal → actual meaning):**

   | Literal phrase | Actual meaning |
   |---|---|
   | 我们再考虑考虑 | Politely declining / no |
   | 原则上可以 | Not actually approved |
   | 我尽量 / 我看看 | Likely will not happen |
   | 再说吧 / 到时候看 | No commitment, drop it |
   | 你人很好 | Friend-zoned / soft rejection |
   | 我不是那个意思 | Don't push further |
   | 哈哈哈哈 (from senior) | Awkward / unhappy |
   | 有空一起吃饭 | Polite sign-off, not a real invitation |

2. **Rule of thumb:** in high-context Chinese, silence ≠ agreement (can mean disagreement), modesty ≠ lack of confidence, indirect wording ≠ maybe.
3. **Context cues:** who speaks (boss vs peer vs subordinate), venue (public banquet vs private WeChat), and whether action follows words.

**Frequency:** Medium-high. Especially painful for young professionals, non-native speakers, and people new to corporate China.

**Safety assessment:** Low. This is literacy, not manipulation. Bound: "decode intent, do not advise manipulating others' perceptions."

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `chinese-subtext-decoder`* — input an utterance + relationship + setting; output literal meaning vs. most likely intent, confidence level, and recommended response.

---

### 1.5 Workplace Upward Management & Meeting Politics (向上管理)

**Domain:** How to report to a boss, when to speak in meetings, how to handle dual managers, how to disagree without sounding defiant.

**What AI gets wrong:**
- AI defaults to generic Western career advice ("be proactive!"). It does not encode the specific Chinese corporate patterns: report *value* not *busyness*; use the **三段式汇报** (one-line conclusion → data/facts → the decision you need); frame pushback as resource prioritization, not refusal ("按目前资源全推进质量和时间都有压力，我建议先聚焦A和B" — you haven't said no, you've helped the org choose).
- It doesn't know the meeting-timing research: speak in the first 3 minutes (you're perceived 50% more confident; your ideas get referenced later), don't raise a big objection right after a decision is made, and "大小领导同时在场一定要学会闭嘴" — when both a senior and junior leader are present, defer to the senior's framing.

**Actionable knowledge that exists:**
1. **Reporting template:** 结论 (one sentence) → 依据 (data/case) → 决策请求 (what you need approved). Not "I was busy all week."
2. **Pushback frame:** never say "做不了" / "时间不够"; say "按现有资源，如果全推进质量和进度都有风险，我建议先聚焦X和Y，请您定优先级."
3. **Meeting rules:** speak early (first 3 min window); use transitions/pauses; don't contradict the boss in public — pull them aside; with two bosses, maintain a shared priority doc so each boss sees what the other decided.
4. **Boundary rules:** bigger boss → relax / be normal (they have enough to be insecure about); smaller boss → inflate their authority (their power is small and will be used on you).

**Frequency:** High for white-collar workers.

**Safety assessment:** Low-medium. Bound: this is constructive communication, not office politics manipulation / backstabbing. Explicitly exclude tactics for undermining colleagues.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `chinese-workplace-reporting`* — scenario (status update / declining extra work / disagreeing with boss / dual-manager conflict / meeting opening) → structured Chinese script.

---

## PART 2 — COGNITIVE BIASES & DECISION QUALITY

### 2.1 Debiasing Checklist / Pre-Mortem / Red-Team

**Domain:** Operational debiasing frameworks applied before a consequential decision — not just a list of biases, but *what to actually do*.

**What AI gets wrong:**
- LLMs are *themselves* vulnerable to the exact biases they would list: anchoring (they anchor on the user's first number), confirmation bias (they agree with the user), and sycophancy (they validate distorted thinking). Asked to "list cognitive biases," they produce a generic 20-bias list with no actionable procedure. They rarely *run* a debiasing protocol on the user's actual decision.
- They do not spontaneously run a pre-mortem ("it's 6 months from now, this failed — write the history of why") because that requires adversarial imagination, and alignment training makes them optimistic.

**Actionable knowledge that exists:**
1. **Pre-mortem protocol (Klein):** "It's [time horizon] from now. This decision failed, plainly. Each person independently writes 10–15 reasons it failed." The framing matters: not "what could go wrong" (invites polite generalities) but "it went wrong, explain why" (licenses doubt).
2. **Bias-buster questions:** What would disconfirm my favorite option? What data would change my mind? Who disagrees, and why? What would I tell a friend in this situation?
3. **Decision table mapping:** Framing → state multiple frames (gain vs. loss); Alternatives → require explicit rejected-option rationale; Evidence → use base rates + seek disconfirming evidence; Probability → confidence ranges, not certainty; Sunk cost → "given where I am today, would I start this?"; Groupthink → independent estimates *before* discussion + assigned red-team role.
4. **Reversibility test:** easy-to-reverse decisions → light scrutiny; hard-to-reverse → escalate, pre-mortem, second opinion.

**Frequency:** Medium. Used at career forks, big purchases, investments, hiring — maybe 5–20 times/year per power user.

**Safety assessment:** Low. This improves judgment; no harm. Bound: not financial/legal advice — frameworks only.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `decision-debiasing-workbench`* — user inputs a pending decision; skill walks them through premortem prompt, bias checklist, reversibility rating, and red-team arguments against their own preferred option.

---

## PART 3 — LIFE PRACTICAL PITFALLS (生活实操避坑)

These are strong because the knowledge is (a) highly specific, (b) changes as scammers adapt (past LLM training may be stale), and (c) structured as checklists with numeric thresholds LLMs otherwise hallucinate.

---

### 3.1 Renovation Anti-Pitfall Checklist (装修避坑)

**Domain:** Avoiding contractor scams, material-substitution fraud, and knowing inspection checkpoints with numeric thresholds.

**What AI gets wrong:**
- Ask an LLM "how do I renovate?" and you get generic advice ("set a budget, get quotes"). It does not know the **42 documented contractor tricks** circulating in 2025–2026: low-ball entry price then 增项 (add-ons), vague contract material specs ("一线品牌瓷砖" → shipped no-name), splitting one task into 5–7 line items (wall paint split into 找平+绷带+底漆+面漆+阴阳角+成品保护) to inflate unit prices.
- It does not reliably emit the numeric acceptance thresholds because these come from local 2025–2026 consumer-protection notices, not timeless fact.

**Actionable knowledge that exists:**
1. **Contract traps:** require "预算即决算，增项不超过5%" in writing; every material must be specified as **brand + model + grade** (not "same grade"); refuse 定金 that locks you into a package.
2. **Inspection checkpoints with numbers:**
   - Water pressure test: ≥0.8 MPa, hold 30 min, no leak.
   - 闭水试验 (waterproofing): ≥48 hours; check downstairs ceiling, not just your floor.
   - Tile hollowing (空鼓): tap all tiles; limit ≤5% and no hollow on wall edges.
   - Board grade: E1 minimum; ENF / E0 for kids' room; demand the test report.
3. **Payment discipline:** tie each payment to a passed milestone; use third-party escrow; never pay >30% up front.
4. **Company red flags:** established <1 year, frequent legal-representative changes, refusal to put changes in writing.

**Frequency:** Low-moderate (once every 5–10 years per household) but **high stakes** (¥100k–1M). Worth a skill because the checklist is reusable and the consequences of failure are severe.

**Safety assessment:** Low. Consumer protection. Bound: not legal advice; cite local 消协 / 市场监管 as authoritative.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `renovation-pitfall-checklist`* — stage picker (signing contract / material delivery / 水电隐蔽验收 / 防水验收 / 瓷砖验收 / final handover) → outputs a printable checklist with numeric thresholds and what to photograph.

---

### 3.2 Medical Visit Preparation (就医沟通)

**Domain:** How to prepare for and communicate in a 5-minute Chinese outpatient visit.

**What AI gets wrong:**
- LLMs happily give medical *content* (symptom explanations, drug info) but do not coach the *patient behavior* that makes or breaks a rushed visit. They don't know: lead with a one-sentence core anchor ("医生，我3天前开始右侧头痛，伴恶心，有高血压史"), never self-diagnose ("我应该是胃炎" → say "我上腹部烧灼感饭后明显"), bring all old films/labs ordered chronologically, list every drug/supplement, and walk out with a written question list.
- Safety boundary: this is not diagnosis — it's visit preparation. AI must not diagnose or prescribe.

**Actionable knowledge that exists:**
1. **Pre-visit pack:** ID + 医保卡; prior records in chronological order; written medication list (including OTC and 保健品); one-line symptom summary.
2. **In-visit script:** (1) core symptom + onset + aggravating factors; (2) describe sensation, don't name disease; (3) answer doctor's questions directly; (4) ask the 5 mandatory questions: What is this? Why this treatment? How long / side effects? How do we know it's working? What if it doesn't help?
3. **Red flags to self-check before the visit:** chest pain, sudden weakness, severe headache, etc. → go to ER, not outpatient.
4. **Triage logic:** choose department by symptom not by disease name; when unsure, ask 导诊台.

**Frequency:** Medium. Every household member visits doctors regularly; poorly prepared visits are a top complaint.

**Safety assessment:** Medium. Must clearly state: "This is communication prep, not medical advice. AI cannot diagnose. For emergencies call 120." Route crisis content to professionals.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `doctor-visit-coach`* — intake form (symptom, duration, history) → generates the one-line opening, the question list to ask, what to bring, and a post-visit note template to record the doctor's instructions.

---

### 3.3 Car Buying & Maintenance Anti-Pitfall (买车/保养)

**Domain:** Dealer tricks at purchase, new-car delivery inspection, and maintenance-interval truths.

**What AI gets wrong:**
- Generic car-advice content. It does not encode the 2025–2026 dealer playbook: talk in **裸车价 (bare-car price) not 综合优惠 (combined discount)**, watch for 库存车 (inventory cars: domestic >3 months, imported >6 months from door-plate date → negotiate 5–10% off), verify **tire date codes** (4-digit DOT code on sidewall — must be *before* the car's production date; if later, tires were swapped), check **glass codes** (any glass later than car build = accident repair), inspect engine-bay screws for torque marks.
- On maintenance: 4S shops push every-visit servicing; the actual truth is full-synthetic oil = 10,000 km / 1 year, air filter = 20k km, brake fluid = 2 years / 40k km, brake pads <3 mm. AI may parrot "change oil every 5000 km" (mineral-oil rule) for synthetic cars.

**Actionable knowledge that exists:**
1. **Delivery inspection (提车) checklist:** door-jamb build date; tire 4-digit date; glass date codes; engine-bay screw uniformity; panel gaps; paint under light; all electronics; spare/triangle/jack.
2. **Price negotiation:** insist on cash discount not "综合优惠"; compare loan vs. cash offers separately; walk away if they won't show 裸车价.
3. **Maintenance interval table:** oil filter + oil (small service), air filter 20k, AC filter 20k, brake fluid 2yr/40k, coolant per manual, brake pads <3mm. "保养手册才是亲妈，4S店建议只是邻居热心推荐."
4. **Used-car minimums:** independent third-party inspection (not a mechanic the dealer recommends); demand 出险记录 + 4S 维保记录; walk away if seller hesitates to show records.

**Frequency:** Low-moderate (purchase once per several years, maintenance every 6–12 months).

**Safety assessment:** Low. Consumer advice. Bound: not mechanical diagnosis; defer to licensed mechanics.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `car-buy-maintenance-checklist`* — stage picker (price negotiation / delivery inspection / service interval / used-car check) → checklist + thresholds.

---

### 3.4 Rental & Real Estate Contract Traps (租房/买房)

**Domain:** Avoiding fake-landlord, rent-loan, and deposit-loss traps; contract terms.

**What AI gets wrong:**
- LLMs can recite contract clauses but do not surface the *active* 2025–2026 traps: the **定金 vs 订金** distinction (定金 is non-refundable and capped at 20% under Civil Code; 订金 is refundable), the **租金贷** trap (agent pushes "monthly payment" that is actually a consumer loan), fake landlords who "forgot the contract" and disappear after deposit, 隔断房 (illegal partitioned rooms in kitchen/balcony/bathroom).

**Actionable knowledge that exists:**
1. **Identity verification:** see 房产证 + 房东 ID; if 二房东, see original lease with sublet permission; ideally all three parties meet.
2. **Before signing:** refuse 租金贷; cap 定金 at 20% of annual rent; lease term ≤20 years (Civil Code Art. 705); write every verbal promise into the contract.
3. **Move-in joint walkthrough:** photograph/video every room, every appliance, every stain; record utility meter readings; sign a 房屋交接清单 together; list known defects with repair responsibility.
4. **Move-out:** normal wear (light wall scuffs, normal floor wear) is not deductible; landlord must provide evidence of damage; get a joint move-out sign-off.

**Frequency:** Medium for urban renters (every 1–3 years); high-stakes deposits.

**Safety assessment:** Low. Bound: legal information, not legal advice; cite Civil Code articles but recommend consulting a lawyer for disputes.

**Verdict: STRONG CANDIDATE.**
*Proposed skill: `rental-contract-checklist`* — intake (renting / buying, city, 二房东?) → contract red-flag scan + move-in/move-out checklists.

---

### 3.5 Government Document Processing (办证)

**Domain:** What documents, timing, and pitfalls for routine PRC administrative tasks (passport, hukou, social security, etc.).

**What AI gets wrong:**
- AI gives vague "bring your ID" answers. It does not encode the 2024–2026 policy updates: e.g., cross-province passport application now only needs ID + in-person appearance (no 居住证 / work permit / bank flow) in many cities; processing time is 7 working days in-hukou vs. 20 days cross-province; minors need birth certificate + guardian; registered state workers need an approval letter.
- Timing and required materials are exactly the kind of fast-changing local facts where LLM training data is stale.

**Actionable knowledge that exists:**
1. **Passport (general 2025–2026):** 身份证原件 + 本人到场 (photo + fingerprints); book via 移民局 mini-program; ~7 days in-hukou, ~20 days cross-province; minors need birth cert + guardian.
2. **General principle:** always book online first; bring originals not copies; call ahead because district-level rules vary; "一次性告知" means the window must list all missing documents at once.
3. **Pitfalls:** showing up without appointment; assuming copy suffices; forgetting fingerprints means in-person; state-worker approval letter often missed.

**Frequency:** Low (once every few years per document) but **frustrating and high-stakes** (people lose half-days).

**Safety assessment:** Low. Bound: "verify on the official 政务服务网 / 移民局 site; rules vary by district and change."

**Verdict: MARGINAL → STRONG CANDIDATE only as a lightweight checklist pack.** The frequency is lower and rules are city-specific and volatile. A skill would need live data / citations to official portals. If built, scope it narrowly (passport, hukou transfer, social-security transfer) and always link to the official portal rather than asserting rules.
*Proposed skill (if pursued): `prc-document-checklists`* — but flag staleness risk.

---

## PART 4 — SENSORY & PHYSICAL CRAFT KNOWLEDGE

### 4.1 Cooking Heat Control & Doneness by Sensory Signals

**Domain:** Judging pan/oil temperature and food doneness by sound, sight, and smell rather than a timer.

**What AI gets wrong:**
- AI recipes say "cook 7 minutes per side" — but cooking science sources are explicit that time is unreliable because heat transfer depends on thickness, starting temp, pan material, burner output, and crowding. AI cannot hear the **sizzle** (sharp crackle = pan hot enough; dull murmur = food steaming in its own water; sizzle fading = moisture gone, time to season), cannot see oil shimmer, cannot smell Maillard aromas. Russian-language analysis of AI cooking notes that a 2°C shift changes emulsion stability, and without real-time surface-tension sensors, the model cannot predict the critical threshold.
- AI will give the *parameters* (temp ranges, ratios) but not the *failure-detection* loop: "if your stir-fry is soggy, it's because the pan wasn't hot enough or you overcrowded the wok; fix by batching."

**Actionable knowledge that exists:**
1. **Heat signal table:**
   - Pan hot test: water bead dances/beads off → ready for searing.
   - Oil: shimmering/ripples = ~160–190°C (medium); faint blue haze = ~200°C+ (high); smoking = too hot.
   - Food hit sound: loud sharp 刺啦 = right; dull/silent = pan too cool (food boils, not fries).
   - Sizzle pattern: aggressive at start, mellow as crust forms — flip when it mellows.
2. **Maillard prerequisites:** high heat + dry surface (pat proteins dry) + contact time without moving. If surface is wet, steam holds food at 100°C and browning cannot start.
3. **Troubleshooting decision tree:** Soggy vegetables → pan too cool / overcrowded. Bitter steak → over-extracted / too hot / burnt fond. Under-done → finish lower heat through-center. Color creeping up egg-white halfway = check release.
4. **Burner reality:** "Medium" on your dial is not a universal temperature — it is a starting point; adjust by result.

**Frequency:** High for people who cook, but the *skill* value is moderate because visual cooking videos already dominate.

**Safety assessment:** Low. Food safety caveats (internal temps for poultry/pork).

**Verdict: MARGINAL.** The knowledge is real and AI genuinely lacks the sensory loop, but (a) cooking content is saturated on video platforms, (b) the skill output is text and cannot transmit feel, (c) users mostly ask for *recipes*, which AI already does well. The actionable gap (troubleshooting + heat-signal table) is worth a small skill, not a flagship.
*Proposed skill (if pursued): `cooking-troubleshooter`* — "why is my X soggy/burnt/raw?" → decision tree fix.

---

### 4.2 Coffee / Tea Brewing Parameters & Tasting

**Domain:** Matching roast level to water temp / grind / ratio, and decoding tasting notes.

**What AI gets wrong:**
- AI can recite the SCA range (90–96°C) but does not reliably apply the **inverse rule**: light roasts need *hotter* water (92–96°C, coarser grind, to extract delicate aromatics), dark roasts need *cooler* water (85–90°C, coarser grind, to suppress bitter over-extraction). It often defaults to one generic temperature. It also cannot distinguish "sour = under-extracted" from "bright acidity = desirable," or "bitter = over-extracted" from "dark-roast chocolate = intentional."

**Actionable knowledge that exists:**
1. **Parameter matrix:**

   | Roast | Water temp | Grind | Ratio |
   |---|---|---|---|
   | Light (filter) | 92–96°C | medium | 1:15–1:17 |
   | Medium | 90–93°C | medium | 1:16 |
   | Dark | 85–90°C | medium-coarse | 1:15 |

2. **Flavor diagnosis:** Sour/empty = under-extracted (grind finer / hotter water / longer contact); Bitter/dry/ashy = over-extracted (coarser grind / cooler water / shorter brew); Hollow/weak = too much water / too coarse.
3. **Tasting vocabulary bridge:** translate user's vague complaint ("tastes bad") into a diagnosis and a one-knob fix.

**Frequency:** Low-moderate; enthusiast hobby.

**Safety assessment:** None.

**Verdict: MARGINAL.** Niche, enthusiasts already use dedicated apps, and the parameter table is small. Not a priority for the skillkit.

---

## PART 5 — EMOTIONAL INTELLIGENCE & DIFFICULT CONVERSATIONS

### 5.1 Difficult Conversation Scripts (Condolence / Breakup / De-escalation)

**Domain:** Word-for-word scripts for high-stakes emotional conversations.

**What AI gets wrong:**
- The literature is consistent (Digital Trends 2025, arXiv 2604.08479, Psychology.com 2026): AI empathy is **templatic and sycophantic**. It loops back to pre-written empathic phrases ("That sounds really hard"), asks therapy-questions ("How did that make you feel?") and then returns to the template; it becomes an echo chamber that validates distorted thinking; it fails to detect crisis signals and cannot de-escalate; it can shift to inappropriate casual/romantic tone; its "empathy" feels uncanny because there is no actual theory of mind.
- In Chinese context, the failure is sharper: AI's comforting phrases ("我会稳稳地接住你") became a meme for being over-affectionate and unnatural.
- For condolence specifically, AI tends toward upbeat / silver-lining language, which is the wrong register.

**Actionable knowledge that exists:**
1. **De-escalation scripts (verbatim):**
   - "Help me understand."
   - "I want to make sure I get your point before I respond — is it [summarize]?"
   - "I'm getting overwhelmed; I need 20 minutes; I do want to come back to this at [time]."
2. **Condolence register:** no silver linings, no "they're in a better place" unless you know the family's belief; show up, say "I'm so sorry," bring practical help (meal, errand), sit in silence.
3. **Breakup structure:** in person (if safe); own your reason ("what I need has changed"), don't falsely blame the other person; don't promise friendship you don't mean; handle logistics (shared lease, belongings) separately from emotion.
4. **Conflict repair loop:** name the rupture, commit to a new pattern ("next time I'll ask for a pause earlier — what will you do?"), build a shared repair signal.

**Frequency:** Medium-high (everyone faces these moments, but they are spaced months apart).

**Safety assessment:** Medium. Bound hard:
- Never provide scripts for manipulation, guilt-tripping, or PUA.
- Crisis / suicidal ideation / domestic violence → route to professional help immediately; do not script around it.
- This is *conversation preparation*, not therapy.

**Verdict: STRONG CANDIDATE (but tightly bounded).** The value is precisely that it supplies *specific, register-correct scripts* AI otherwise templates. The Chinese-context version (安慰/吊唁/分手) is especially valuable because AI's Chinese emotional register is the most uncanny.
*Proposed skill: `difficult-conversation-coach`* — scenario picker → word-for-word opening + likely responses + what not to say + when to pause / when to get professional help.

---

## PART 6 — INDUSTRY BENCHMARK CONTEXT (not a domain itself)

Cross-cutting reasons the above domains are hard for LLMs (from 2025–2026 literature):

1. **Training-data Western / low-context bias** — Chinese high-context pragmatics is systematically under-represented.
2. **No real-world grounding** — models learn from text, not from sizzle sounds, door-jamb metal plates, or contract dispute court cases. They cannot smell caramelization or feel rim height.
3. **Calibration failure** — they produce confident-sounding wrong answers with no reliable "I don't know."
4. **Knowledge cutoff** — scammer playbooks, 4S dealer tricks, and 办证 rules rotate every 6–18 months; training data lags.
5. **Sycophancy / alignment** — they agree with the user, which is the *opposite* of what debiasing and red-teaming require.
6. **Templatic empathy** — research confirms "well-liked but templatic" empathic responses; context-insensitive.
7. **No clock / no state** — dates, days-of-week, and up-to-date local rules are guessed.

This means the highest-value skills are exactly those that **inject structured, up-to-date, culturally-specific rules the model otherwise has to hallucinate**.

---

## SUMMARY TABLE

| # | Domain | Verdict | Why | Suggested skill name |
|---|---|---|---|---|
| 1.1 | Chinese banquet & toast etiquette | **STRONG** | AI flattens hierarchy; seating/toasting rules are concrete tables; high-stakes in Chinese business | `chinese-banquet-etiquette` |
| 1.2 | Gift money amounts & gift taboos | **STRONG** | Relationship-tier amounts + homophone taboos are exactly the culturally-coded data AI under-weights | `chinese-gift-etiquette` |
| 1.3 | High-EQ phrase banks (refuse/comfort/apologize/criticize) | **STRONG** | AI Chinese output is blunt or uncanny; phrase formulas are directly encodable | `chinese-high-eq-phrases` |
| 1.4 | Subtext / 潜台词 decoder | **STRONG** | Benchmarks show models misread Chinese indirectness; literal→intent table is compact | `chinese-subtext-decoder` |
| 1.5 | Upward management & meeting politics | **STRONG** | 三段式汇报, pushback framing, meeting timing are specific scripts AI doesn't encode | `chinese-workplace-reporting` |
| 2.1 | Debiasing / pre-mortem / red-team | **STRONG** | LLMs are themselves biased/sycophantic; a structured protocol forces adversarial thinking | `decision-debiasing-workbench` |
| 3.1 | Renovation anti-pitfall checklist | **STRONG** | Numeric thresholds, rotating scams, high stakes; AI gives only generic advice | `renovation-pitfall-checklist` |
| 3.2 | Medical visit communication coach | **STRONG** | AI won't coach patient behavior; high-frequency; easy boundary (no diagnosis) | `doctor-visit-coach` |
| 3.3 | Car buying / maintenance checklist | **STRONG** | Date-code inspection tricks and maintenance intervals are specific and AI-hallucinated | `car-buy-maintenance-checklist` |
| 3.4 | Rental contract traps | **STRONG** | 定金/订金, rent-loan, move-in walkthrough are active 2025–2026 traps | `rental-contract-checklist` |
| 3.5 | Government document processing (办证) | **MARGINAL** | Useful but low-frequency, city-specific, and volatile; needs live official data | `prc-document-checklists` (optional) |
| 4.1 | Cooking heat-control troubleshooting | **MARGINAL** | Real sensory gap but video-saturated; text can't transmit feel; recipes already work | `cooking-troubleshooter` (small) |
| 4.2 | Coffee/tea brewing parameters | **MARGINAL** | Niche enthusiast; small parameter table; dedicated apps exist | — (deprioritize) |
| 5.1 | Difficult conversation scripts | **STRONG** (bounded) | AI empathy is templatic/sycophantic; register-correct scripts are the gap; crisis boundary required | `difficult-conversation-coach` |

---

## TOP PRIORITY SHORTLIST (build order)

Highest expected user value × AI failure magnitude × encodability × safety:

1. **`chinese-high-eq-phrases`** — daily use, immediately useful, zero safety risk.
2. **`chinese-gift-etiquette`** — event-driven but universally needed; amounts + taboos are pure lookup tables.
3. **`chinese-banquet-etiquette`** — high-stakes for professionals; seating/toast diagrams are compact.
4. **`chinese-subtext-decoder`** — the benchmarked blind spot; compact lookup.
5. **`renovation-pitfall-checklist`** — highest financial stakes; numeric thresholds AI won't reliably emit.
6. **`doctor-visit-coach`** — high frequency; clean safety boundary.
7. **`chinese-workplace-reporting`** — white-collar daily pain point.
8. **`decision-debiasing-workbench`** — meta-skill that compensates for AI's own sycophancy.
9. **`car-buy-maintenance-checklist`** / **`rental-contract-checklist`** — consumer-protection pairs.
10. **`difficult-conversation-coach`** — valuable but requires careful crisis-safety gating.

## EXPLICIT REJECTS (do not pursue)

- Anything that teaches **PUA, manipulation, gaslighting, persuasion exploitation**, or bending social norms to exploit others — overlaps with request-1.x but crosses into harm.
- **Legal/medical/financial professional advice** — provide frameworks and checklists only, always route to licensed professionals; do not position as diagnosis/prescription/legal opinion/investment advice.
- **Direct political sensitivity / sensitive-persona content** — out of scope.
- **Spicy-content / deceptive impersonation** — out of scope.

---

*Sources consulted: 新华网/人民网/央视网 consumer-protection reporting (2025–2026); arXiv 2602.03107 (Chinese Mock Politeness benchmark); arXiv 2604.08479 (templatic AI empathy); industry blogs on LLM limitations (PromptQuorum, CACM, Taim.io, Vanja.io); Chinese social-practice content from 抖音/搜狐/婚礼纪/爱范儿; debiasing literature (Klein premortem, Howard-Abbas decision-quality framework); coffee/SCA parameter references. All numeric thresholds should be re-verified against current local sources before encoding into a shipped skill.*
