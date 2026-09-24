# Sources and Methodology

- Skill: webapp-flow-tester (originally written for awesome-skillkit, Apache-2.0).
- Methodology distilled from Anthropic public skills docs (no content copied): only borrowing the publicly known methodological idea that "when testing a local web app, first reconnoiter the page before writing selectors, and let a wrapper script uniformly manage the service process lifecycle". The SKILL.md, dump scripts, test templates, and with_server.py under this directory are all original, written from scratch; no paragraph, example, or code from any upstream doc was copied, translated, or paraphrased.
- The "start → poll for readiness → execute → always clean up" wrapper pattern is independently implemented in this repo (socket polling + process-group signal cleanup).
- License: this skill and its reference files are distributed under Apache-2.0, which is independent of the upstream docs' licensing terms.
