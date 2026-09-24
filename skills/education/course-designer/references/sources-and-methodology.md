# Sources and Methodology

This skill is self-authored; its methodology skeleton is distilled from the following public materials (structural borrowing only, no text copied):

| Source | Type | What was borrowed | License/attribution |
|------|------|----------|-----------|
| [AI-Learning-Agent](https://github.com/Chittesh-ST/AI-Learning-Agent) (LangGraph mastery tutor) | open-source project | Checkpoint decomposition + pass-rate threshold + failure-triggered Feynman remediation loop; strict quiz design that **bans multiple-choice to prevent guessing**; quantified scoring rubric (0-20 bands) | Structural borrowing with attribution |
| [Feynman Learning Coach](https://lobehub.com/skills/jasonxzwen-skill-hub-feynman-learning-coach) (LobeHub skill) | open-source skill | **Learning contract** (scope/level/target/constraints ≤3 questions); Foundations→Mechanism→Example→Transfer→Teach-back path; depth-control table by beginner/intermediate/advanced/exam | Structural borrowing with attribution |
| [Shouwu FeynMind](https://forum.trae.cn/t/topic/70981/3) (TRAE competition entry, frontline high-school teacher) | 🟡 practice case | Reverse teaching design of "AI plays a not-very-smart student"; knowledge-coverage status visualization (active/passive/uncovered); four-dimensional assessment (coverage/accuracy/coherence/engagement) | Design idea borrowed with attribution |
| [THU-MAIC/OpenMAIC feynman-learning](https://github.com/THU-MAIC/OpenMAIC) | open-source skill | Teach-back and follow-up questions at the core; strip jargon; stress-test analogies; transfer to new contexts | Structural borrowing with attribution |
| Mastery Learning (Bloom) | educational public domain | The pass-threshold philosophy of mastery rather than time | Classic theory |

## Design decisions

1. **Learning contract upfront and ≤3 questions**: from the Feynman Learning Coach best practice—
   more than three questions is stalling the teaching.
2. **Checkpoints made decidable**: rewrite "understands" as "can explain / can do / can pass,"
   same source as this repo's "audit culture"—an undecidable goal cannot be accepted.
3. **Feynman loop as a standalone skill** (feynman-explainer): remedial teaching is a separate action,
   decoupled from the course skeleton (this skill) and exercises (exercise-generator), for a clearer chain.
