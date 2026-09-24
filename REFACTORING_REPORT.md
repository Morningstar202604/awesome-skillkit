# Skillkit Refactoring Report

**Date:** 2026-09-24
**Scope:** Full repository refactor — 156 SKILL.md, 36 scene packs, ~336 Python scripts
**Branch/State:** Working tree at `/home/user/Doubao/chats/38443767625831170/skillkit`

---

## 1. Executive Summary

| Metric | Before | After | Change |
|---|---|---|---|
| SKILL.md files | 156 | 156 | Unchanged (all now English) |
| Chinese chars in SKILL.md | ~45,000+ | **0** | Fully anglicized |
| YAML parse errors | 8 | **0** | All fixed |
| Python scripts (.py) | ~336 | **178** | -158 deleted |
| `__pycache__` dirs | ~110 | **0** | All removed |
| tools/ scripts | 16 + 21 tasks | **3** | -34 deleted |
| Scene pack zips | 36 | **36** | Rebuilt |
| Total bundle (_all.zip) | — | **2.3 MB** | 154 skills |
| Publisher automation scripts | 17 skill dirs | **0** (1 kept) | Removed per new direction |

---

## 2. Problem Fixes (13 Groups)

All 13 groups were independently verified before fixing.

| # | Severity | Issue | Verification | Fix | Validation |
|---|---|---|---|---|---|
| 1 | Critical | 16 publisher scripts use 3-layer `..` to find `_common/`, break after flat zip | Confirmed: `os.path.normpath(os.path.join(__file__, "..","..","..","_common"))` in all 16 | **Eliminated by removal** — all publisher automation scripts deleted (new direction: content adaptation, not posting). `_common/` deleted. | No scripts remain to import `_common`; `grep -r "publish_common" skills/` returns 0 hits |
| 2 | Critical | `simulation.py` `sensitivity()` defined but never called; `--sensitivity` always errors | Confirmed: line 116 unconditionally printed error JSON | Wired up `--sensitivity` to call `sensitivity()` with param normalization (space- or comma-separated), `--spec` loading, perturbation support | `--help` shows both flags; test run outputs valid `sensitivity_ready` JSON |
| 3 | Critical | 8 SKILL.md YAML frontmatter unparseable (6 unescaped inner quotes, 2 unquoted colon-space) | Confirmed: all 8 fail `yaml.safe_load()` | 6 converted `description` to `>-` block scalar; 2 wrapped `compatibility` in double quotes | All 8 pass `yaml.safe_load()`; full-repo scan = 0 YAML errors |
| 4 | High | `bilibili/toutiao/oschina` publisher `http_web()` missing `headers` param but callers pass it | Confirmed: signature `def http_web(url, method, data)` vs calls with `headers=` | **Eliminated by removal** — publisher scripts deleted | No HTTP client code remains |
| 5 | High | `compatibility_checker.py` duplicate `"boolean"` dict key (line 130 & 150), second overwrites first → boolean→tinyint misreported as breaking | Confirmed: two `"boolean"` keys in `TYPE_COMPATIBILITY_MATRIX` | Merged into single dict with all 8 mappings (3 SQL + 5 JSON), comments separating namespaces | AST walk = 0 duplicate keys; runtime: `boolean→tinyint=compatible`, `boolean→string=breaking` |
| 6 | High | `lint_skill.py count_trigger_words()` uses 3 hints but `USE_WHEN_HINTS` has 6 → false FAILs | Confirmed: line 170 hardcoded `("use when", "当用户", "触发")` vs line 56's 6 | Changed loop to iterate `USE_WHEN_HINTS` constant directly | `--help` works; runtime confirms all 6 hints checked |
| 7 | High | `paper_pipeline.py` line 81: two `\begin{document}`, one `\end{document}` | Confirmed: template string `\documentclass{article}\begin{document}\title{Draft}\begin{document}\end{document}` | Removed duplicate `\begin{document}` | grep confirms exactly 1 begin + 1 end |
| 8 | Medium | `tdd-guide`: `coverage_analyzer.py` docs say `--report` but it's positional; 3 other scripts have no `__main__`/argparse but docs treat as CLI | Confirmed: `coverage_analyzer` positional only; `test_generator`, `tdd_workflow`, `fixture_generator` have no argparse | Added `--report` repeatable flag to `coverage_analyzer`; added `main()` + argparse + `if __name__` to all 3 scripts | All 4 run `--help` successfully; documented commands execute |
| 9 | Medium | `simulation-runner` SKILL.md documents `--perturbation` but argparse doesn't register it | Confirmed: SKILL.md line 65 uses `--perturbation 0.1`, argparse had no such flag | Added `--perturbation` (float, default 0.1) to argparse | `--help` shows flag; test run with `--perturbation 0.2` produces ±20% values |
| 10 | Medium | `article-outliner` docs say `--json-input` is file path but code does `json.loads()` on the string | Confirmed: line 96 `json.loads(args.json_input)` directly | Added file-path detection: if `Path(arg).is_file()`, read and parse file; otherwise parse as inline JSON string | Both `--json-input /tmp/x.json` and `--json-input '{"k":"v"}'` work |
| 11 | Low | `latex_formatter.py` line 107 `ext={}` always empty → `method` always `stdlib-fallback` | Confirmed: `format_latex()` hardcodes `ext = {}`; `main()` computes `ext` but never passes it | Added `ext: dict = None` param; `ext = ext or {}`; `main()` passes `ext=ext` | `method="external-lint"` when chktex present; `stdlib-fallback` otherwise |
| 12 | Low | `script_lint.py` docstring says 240-char limit but `MAX_LINE_CHARS=90` | Confirmed: docstring line 11 "> 240 chars" vs line 29 `MAX_LINE_CHARS = 90` | Changed docstring to "> 90 chars" | grep confirms no remaining "240" reference |
| 13 | Low | `convert.py` `_run()` returns 0/1 → `rc==47` branch dead code | Confirmed: `_run()` collapses all non-zero to 1; pandoc exit 47 (needs LaTeX engine) unreachable | `_run()` now returns actual subprocess returncode (0–255), clamping negative signal codes to 1 | `_run(['python3','-c','sys.exit(47)'])` returns 47 |

---

## 3. Content Publishing Refactor (18 Skills)

**Direction change:** From "posting automation" to "platform-adapted article generation." Users generate content with the AI, then manually format and publish — no automation scripts needed.

### Per-skill changes

| Skill | Scripts Deleted | SKILL.md | Key Adaptation Info |
|---|---|---|---|
| zhihu-content-manager | ✅ | Rewritten EN | Long-form columns; Draft.js HTML, no tables, `<figure>` images, LaTeX, 3k–10k chars |
| cnblogs-skill | ✅ | Rewritten EN | GFM Markdown; no h1, short paragraphs, emoji headings, 2 images, category+tags |
| wechat-mp-publisher | ✅ | Rewritten EN | Rich-text; title ≤64, cover 900×383, no external links, mobile pacing |
| juejin-publisher | ✅ | Rewritten EN | GFM; strong code blocks, Mermaid, TL;DR, 1 category + 3–5 tags |
| csdn-publisher | ✅ | Rewritten EN | Baidu-search-optimized; title ≤80, error→cause→fix structure, screenshots |
| jianshu-publisher | ✅ | Rewritten EN | Literary essays; title ≤30, collections (专题), 5–10 tags, personal voice |
| bilibili-publisher | ✅ | Rewritten EN | Video metadata (title ≤80, 12 tags, timestamps), dynamic posts ≤230 chars, 16:9 cover |
| toutiao-publisher | ✅ | Rewritten EN | Algorithmic feed; title ≤30, 1–3 sentence paragraphs, 3–9 images, no code |
| baijiahao-publisher | ✅ | Rewritten EN | Baidu-search explainer; title ≤30, direct answer up front, keyword-rich summary |
| xiaohongshu-publisher | ✅ | Rewritten EN | Image-first; title ≤20, body ≤1,000 chars, 3:4 cover (1080×1440), 5–15 hashtags |
| weibo-publisher | ✅ | Rewritten EN | Microblog; hook first ~140 chars, `#话题#` hashtags, 1–9 images, hot-search topics |
| douban-publisher | ✅ | Rewritten EN | Cultural reviews/notes/diary; literary voice, groups, 3–10 tags |
| v2ex-publisher | ✅ | Rewritten EN | Hacker forum; title ≤120, no inline images, plain text/code, node selection |
| segmentfault-publisher | ✅ | Rewritten EN | Stack-Overflow-style Q&A + blog; code blocks, Mermaid, 1–5 tags |
| oschina-publisher | ✅ | Rewritten EN | Open-source tooling; GitHub links, "use cases/pros & cons", 1–5 tags |
| static-blog-deploy | ✅ | Rewritten EN | **Reframed** → Static Blog Content Adaptation; Hugo/Jekyll/Hexo front matter, image shortcodes |
| cross-post-orchestrator | ✅ | Rewritten EN | **Reframed** → Cross-Platform Content Adaptation Guide; platform matrix, per-platform workflow |
| ai-cover-generator | ❌ Kept | Rewritten EN | Cover image generation (content creation, not posting); scripts retained |

**Also deleted:** `skills/writing/_common/` (publish_common.py + tests), all automation-only reference files (API docs, account examples, cookie samples).

**Verification:** 18/18 YAML valid; 0 Chinese chars; 0 broken script references; `content-publishing.zip` contains only `ai-cover-generator/scripts/`.

---

## 4. Script & Tool Cleanup

### Deletion Summary (~160 files)

| Category | Count | Reason |
|---|---|---|
| Smoke test runners (`test_smoke_*.py`) | 103 | Dev/test infrastructure; auto-generated by deleted `gen_smoke.py`; not part of any skill workflow |
| Pytest unit-test files | 8 | Test harnesses; not user-facing; not referenced by SKILL.md |
| Dead/orphaned modules | 2 | `normalizer.py`, `session_manager.py` — never imported, not referenced |
| Domain-level pipeline orchestrators | 11 | `*_pipeline.py` files at domain root; not in any skill dir, not documented; pure planners or stubs |
| tools/ dev infrastructure | 35 + 1 JSON | CI/test/reporting tools; only `build_site.py`, `validate_skills.py`, `release.py` are used by CI/docs |
| `tools/tasks/` directory | 21 | Supporting modules for deleted `run_all.py`/`scenario_harness.py` |
| `__pycache__` directories | ~110 | Build artifacts; removed everywhere |
| `.pyc` files | all | Build artifacts |

### Kept (178 .py files)

- **build.py** — root build system
- **tools/build_site.py** — static site generator (CI + docs)
- **tools/validate_skills.py** — CI quality gate
- **tools/release.py** — release helper (referenced by 6 docs)
- **~160 skill scripts** — all referenced in their SKILL.md as workflow tools and parse/run correctly
- **Example/sample fixtures** — sample codebases referenced by SKILL.md (tdd-guide, senior-architect, tech-debt-tracker, etc.)

### Reference Cleanup
- 2 SKILL.md references to deleted smoke tests removed (`layout-spec-auditor`, `code-generator`)
- `skill_chains.json` updated: dangling `entry` paths set to `null` for 9 domains
- 2 additional missed smoke tests in writing/ removed by orchestrator

---

## 5. English Unification & Keyword Optimization

**All 156 SKILL.md files translated from Chinese (or mixed) to pure English.**

| Domain Batch | Skills | Agent | Status |
|---|---|---|---|
| programming | 51 | Translation A | ✅ 0 CJK, 0 YAML err |
| video + paper + writing(non-pub) | 34 | Translation B | ✅ 0 CJK, 0 YAML err |
| office + tools + meta + education + design | 32 | Translation C | ✅ 0 CJK, 0 YAML err |
| memory + integrations + marketing + audio + knowledge + dataviz + ppt + music + chat | 21 | Translation D | ✅ 0 CJK, 0 YAML err |
| writing (18 publishers) | 18 | Publisher Refactor | ✅ 0 CJK, 0 YAML err |

**Keyword optimization:** Each skill's `description` and "When to Use" sections now contain natural AI-trigger keywords specific to its domain (e.g., database skills include "database design / SQL / schema / query optimization"; video skills include "video script / storyboard / subtitle"; writing skills include "article outline / SEO / content adaptation"). No keyword stuffing — keywords flow naturally in professional English.

**Additional YAML repairs during translation:**
- `skill-tester/assets/sample-skill/SKILL.md` — malformed frontmatter consolidated
- `performance-profiler`, `ml-pipeline` — duplicated description + leaking table columns fixed

---

## 6. README & Official Site

### README.md (English, primary)
- Full rewrite with: header/badges, quick nav, **one-click translation block** (Google Translate URL + Bing + Immersive Translate + Chinese README link), positioning, **dual-path download guide** (official site + repository), **36-pack scenario directory table** (pack ID, EN name, ZH name, skill count, full skill list), install instructions, build from source, contributing, license.

### README.zh-CN.md (信达雅 Chinese)
- Mirrors English structure 1:1; Chinese names bolded in pack table; professional native Chinese tone (e.g., "把整套工作能力，一次交给你的 AI 工具"); translation block points en→zh direction.

### site/index.html
- `<html lang="en">`, English hero H1 + tagline with Chinese subtitle
- Translate UI: "🌐 中文 / Translate" pill (Google Translate one-click), "沉浸式翻译" pill, dedicated "🌐 一键译成中文" button
- `app.js` patched: stats/footer/title render in English; tagline uses English description
- `app.css`: new styles for pills/subtitle/button
- Stale "143" references → 154

### site/data/site.json
- Verified: 154 skills, 36 packs, 18 domains, 62 chains, v0.22.0
- All pack `local_url` → `packs/<id>.zip` ✅
- All skill `file` paths resolve to existing files ✅

### README.ja.md
- Version badge 0.19.0 → 0.22.0; translation links section added; note that EN/ZH are authoritative

---

## 7. Build & Packaging

### build.py output
```
36 scene pack zips + 1 _all.zip = 37 archives
_all.zip: 154 skills, ~2286 KB (2.3 MB)
manifest.json: 36 packs synced (size_kb/sha256/updated)
```

### Site deployment
- 37 zips copied to `site/packs/`
- 154 SKILL.md copies to `site/skills/` (single-skill download supported)
- `build_site.py` regenerated `site/data/site.json`

### Download options (all verified)
1. **Single SKILL.md** → `site/skills/<domain>/<subdir>/<skill>/SKILL.md` (download button in site UI)
2. **Scene pack zip** → `site/packs/<pack-id>.zip` (download button in site UI)
3. **Total bundle** → `site/packs/_all.zip` (hero button in site UI)
4. **Repository path** → `skills/` directory browse + `dist/` zips + Releases

---

## 8. Translation Solution

Implemented the zero-dependency Google Translate URL technique:
```
https://translate.google.com/translate?sl=en&tl=zh-CN&u=<target-url>
```
- Placed in README.md top section and site header
- Bing Translator alternative for users in China: `https://cn.bing.com/translator?from=en&to=zh-Hans`
- Immersive Translate browser extension recommended: `github.com/immersive-translate/immersive-translate`
- Official精校 Chinese README: `README.zh-CN.md` (信达雅 quality)
- Each scene pack has Chinese name + description in pack.json and README table

---

## 9. Coverage & Unfinished Items

### Completed
- ✅ All 13 issue groups verified + fixed
- ✅ All 156 SKILL.md in English, 0 CJK, 0 YAML errors
- ✅ 18 publisher skills refactored to content-adaptation model
- ✅ ~160 useless scripts/tools deleted
- ✅ 36 pack zips + _all.zip built
- ✅ Site updated with translation links + English hero
- ✅ README with 36-pack directory + dual download guide + translation links
- ✅ README.zh-CN.md 信达雅 translation
- ✅ build.py + build_site.py run successfully

### Not in scope / deferred
- `references/*.md` files inside skill directories still contain Chinese (only SKILL.md was translated; references are supplementary reading)
- `scripts/*.py` docstrings/comments may still contain Chinese (code functionality unchanged; only SKILL.md required English)
- Site secondary UI text (tab labels, card tags, empty-state) remains Chinese — Google Translate one-click handles this
- README.ja.md body not fully rewritten (only translation links + version badge updated)
- No git commit created (changes are in working tree)

---

## 10. File Change Summary

| Area | Files Changed | Nature |
|---|---|---|
| SKILL.md (translation) | 156 | Chinese→English rewrite in place |
| Publisher SKILL.md (refactor) | 18 | Complete rewrite + structure change |
| Python scripts (bug fixes) | ~15 | Targeted bug fixes |
| Python scripts (deleted) | ~160 | Removed (smoke tests, dead code, dev tools) |
| _common/ (deleted) | 1 dir | publish_common.py + tests removed |
| __pycache__ (deleted) | ~110 dirs | All build artifacts |
| README.md | 1 | Full rewrite |
| README.zh-CN.md | 1 | Full rewrite (信达雅) |
| README.ja.md | 1 | Partial update |
| site/index.html | 1 | English hero + translate UI |
| site/assets/app.js | 1 | English rendering patch |
| site/assets/app.css | 1 | New element styles |
| site/data/site.json | 1 | Regenerated |
| site/packs/*.zip | 37 | Rebuilt |
| site/skills/**/SKILL.md | 154 | Recopied |
| manifest.json | 1 | Synced (size/sha256/updated) |
| skill_chains.json | 1 | Dangling entries nulled |
| dist/*.zip | 37 | Built |
