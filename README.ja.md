<p align="center"><img src="docs/logo.svg" alt="awesome-skillkit" width="220" /></p>

<h1 align="center">awesome-skillkit</h1>

<p align="center">
  <b>2 つのプロダクトライン、1 つのリポジトリ：<br>AI ツール向け 57 シーンパック · 403 スキル&nbsp;＋&nbsp; マルチエージェント協働向け 18 チーム · 219 エージェント——<br>解凍してドロップイン、AI ツールが即座に仕事を覚えます。</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square" alt="License" /></a>
  <img src="https://img.shields.io/badge/skills-403-brightgreen?style=flat-square" alt="Skills" />
  <img src="https://img.shields.io/badge/packs-57-blue?style=flat-square" alt="Packs" />
  <img src="https://img.shields.io/badge/expert%20teams-18%20%C2%B7%20219%20agents-blueviolet?style=flat-square" alt="Expert Teams" />
  <img src="https://img.shields.io/badge/version-0.23.0-success?style=flat-square" alt="Version" />
</p>

<p align="center">
  <a href="https://x33834.github.io/awesome-skillkit/"><img src="https://img.shields.io/badge/%F0%9F%8C%90_Official_Site-Browse-brightgreen?style=flat-square" alt="Official Site" /></a>
  <a href="https://github.com/x33834/awesome-skillkit/releases/latest/download/_all.zip"><img src="https://img.shields.io/badge/%E2%AC%87%EF%B8%8F_Download-_all.zip-blue?style=flat-square" alt="Download all packs" /></a>
  <a href="https://gitcode.com/badhope/awesome-skillkit"><img src="https://img.shields.io/badge/GitCode-Mirror-3A72BE?style=flat-square" alt="GitCode" /></a>
  <a href="https://gitee.com/badhope/awesome-skillkit"><img src="https://img.shields.io/badge/Gitee-Mirror-C71D23?style=flat-square" alt="Gitee" /></a>
</p>

<p align="center"><a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <strong>日本語</strong></p>

---

## 🌐 このページを他の言語で読む（ワンクリック）

リポジトリ内の SKILL.md ファイルは英語へ翻訳中ですが、ドキュメント・事例・プラットフォーム注記の多くはまだ中国語で書かれています。この README と公式サイトを他の言語で即座に読むには:

- **[🌐 Google 翻訳 — 公式サイトを中文（簡体字）で読む](https://translate.google.com/translate?sl=ja&tl=zh-CN&u=https://x33834.github.io/awesome-skillkit/)**（推奨 — ワンクリック、インストール不要）
- **[🌐 Google 翻訳 — 公式サイトを English で読む](https://translate.google.com/translate?sl=ja&tl=en&u=https://x33834.github.io/awesome-skillkit/)**（推奨 — ワンクリック）
- **[Bing Translator で翻訳](https://cn.bing.com/translator?from=ja&to=zh-Hans)**（任意のページ URL を貼り付けて翻訳）
- **[Immersive Translate ブラウザ拡張](https://github.com/immersive-translate/immersive-translate)**（日常使いに推奨 — サイト全体のバイリンガル横並び表示）
- 📄 他言語 README: [**English (README.md)**](README.md) ・ [**中文简体 (README.zh-CN.md)**](README.zh-CN.md)

---

## 2 つのプロダクトライン — 互いに干渉しない

| | **A · シーンパック（スキル）** | **B · Expert Teams（专家团）** |
|---|---|---|
| **ポジション** | AI コーディング / エージェントツール向けのスキル。1 パック = 1 つの実務シナリオ、skills ディレクトリに入れれば使える | AI コーディングツールや各種 AI ツールにおける**マルチエージェント協働**。役割分担した専門チームが計画・ディスパッチ・品質ゲートを担う |
| **アセット** | 57 パック · 403 スキル · 27 ドメイン · 108 チェーン | 18 チーム · 219 エキスパートエージェント · 100 スキル · オーケストレーション規約（純 Markdown） |
| **場所** | [`packs/`](packs/) + [`skills/`](skills/) | [`expert-teams/`](expert-teams/) |
| **入手** | [公式サイト](https://x33834.github.io/awesome-skillkit/) · [`_all.zip`](https://github.com/x33834/awesome-skillkit/releases/latest/download/_all.zip) | [オンライン閲覧](https://x33834.github.io/awesome-skillkit/expert-teams.html) · [4 プラットフォーム用パッケージ](https://x33834.github.io/awesome-skillkit/expert-teams.html#download) |

---

## これは何？

**awesome-skillkit** は 2 つのプロダクトラインを 1 リポジトリで維持しています（上の表）。このセクションは**ライン A — シーンパック**の説明です：AI コーディング / エージェントツール（Claude Code や `SKILL.md` を読み込めるあらゆるツール）向けに精選した**シナリオパック集**です。各パックは、**1 つの具体的な実世界シナリオ**のために連携するスキルをまとめてバンドルしています——「PR をレビューする」「CI/CD パイプラインをリリースする」「記事を 16 の中国語プラットフォームにクロスポストする」「ショート動画をエンドツーエンドで制作する」といった単位です。

設計思想は徹底してシンプルです。

```mermaid
flowchart LR
    A[Real-world scenario] --> B[Scene pack<br/>1 pack = 1 scenario]
    B --> C[Group of collaborating skills<br/>1–19 of them]
    C --> D[Drop into AI tool<br/>skills directory]
    D --> E[Works in a new session<br/>no config]
    style A fill:#eaf2ff,stroke:#5b8def
    style E fill:#eafaea,stroke:#4caf72
```

- 各パックは**具体的なシナリオ**に対応しており、「エンジニアリング」のような曖昧なドメインではありません。
- 各パックは、そのシナリオで**実際に連携するスキルだけ**をまとめています——絞り込んだ 2 スキル構成（`API Development & Testing`）から、18 スキルのスイート（`AI Research & Writing`）、18 プラットフォームの自動出版マシン（`Content Publishing Automation`）まで。
- 各スキルの**出典はスキルごとに** [`manifest.json`](manifest.json) と各 `packs/*/pack.json` に明記されています——自作、上流からの精選（MIT）、公開ドキュメントからの蒸留のいずれかです。

## Expert Teams — ライン B（マルチエージェント協働）

**ポジション**：AI コーディングツールや各種 AI ツールにおける**マルチエージェント協働**。**18 チーム**はいずれも自己完結した専門班（リード + スペシャリスト + 読み取り専用 QA）で、ワークフロー・フェーズゲート・引き継ぎ規約を内蔵——純 Markdown・プラットフォーム非依存・ランタイム依存なし。

- **アセット**：[`expert-teams/teams/<team>/agents/*.md`](expert-teams/teams/)（219 のエキスパート定義）、チームスキル `expert-teams/teams/<team>/skills/` ＋ 共通スキル `expert-teams/skills/`（計 100）、共通 [`orchestration-protocol.md`](expert-teams/orchestration-protocol.md)、横断ルーター [`project-director.md`](expert-teams/project-director.md)。
- **18 チーム**：学術論文 · フルスタック Web · 数理モデリング · ソフトウェア開発 · ビジュアルデザイン · コンテンツ執筆 · 動画制作 · データ分析 · マーケティング · EC 運営 · プロダクト · 財務会計 · HR · 法務コンプライアンス · 翻訳ローカライズ · 教育研修 · 音声ポッドキャスト · ゲームデザイン。
- **使い方**：横断タスクは `expert-teams/project-director.md` からルーティング。チームリードを直接ディスパッチする場合は `expert-teams/teams/fullstack-web-team/agents/fullstack-team-lead.md` のように指定（リポジトリルートからは全て `expert-teams/` を前置）。
- **オンライン閲覧**：[Expert Teams ページ](https://x33834.github.io/awesome-skillkit/expert-teams.html)——チームマトリクス・データスナップショット・インストールガイド。

### 4 プラットフォーム用パッケージをダウンロード（解凍してインストール）

| パッケージ | 内容 | インストール |
|---|---|---|
| [expert-teams-opencode.zip](https://x33834.github.io/awesome-skillkit/downloads/expert-teams-opencode.zip) | `.opencode/agents/*.md` + `.opencode/skills/*` | プロジェクトルートで解凍 |
| [expert-teams-claude.zip](https://x33834.github.io/awesome-skillkit/downloads/expert-teams-claude.zip) | `.claude/agents/*.md` + `.claude/skills/*`（読み取り専用ロールは `disallowedTools` にマップ済み） | プロジェクトルートで解凍 |
| [expert-teams-cursor.zip](https://x33834.github.io/awesome-skillkit/downloads/expert-teams-cursor.zip) | Cursor プラグインフォルダ（`expert-teams/`、`.cursor-plugin/plugin.json` + agents + skills） | プラグインとしてインストール |
| [expert-teams-gemini.zip](https://x33834.github.io/awesome-skillkit/downloads/expert-teams-gemini.zip) | Gemini CLI 拡張（`gemini-extension.json` + `GEMINI.md` + 18 個の `/<team>` コマンド） | 拡張としてインストール |
| [expert-teams-all.zip](https://x33834.github.io/awesome-skillkit/downloads/expert-teams-all.zip) | プラットフォーム非依存のソースバンドル（`expert-teams/`：teams + skills + 主要ドキュメント） | ファイルを読める任意のエージェントに渡す |

パッケージは**再現可能ビルド**（CI でダイジェスト固定）。`python3 expert-teams/export-platforms.py` でいつでも再生成できます（PyYAML のみ）。GitCode / Gitee サイト用の同一ファイルは [`site/downloads/`](site/downloads/) にミラーされています。

> **由来**：2026-09-27 に旧 `ai-expert-teams` リポジトリ（MIT）から移設。旧リポジトリは GitHub ×2 / GitCode / Gitee の 4 プラットフォームで公開終了。サブツリー独自のゲート（`verify.py` / `unittest` / `build-site.py --check`）と [`README`](expert-teams/README.md) / [`AGENTS.md`](expert-teams/AGENTS.md) を持ちます。

## 使い込む理由 — 5 つの要点

- **場面優先、テーマの寄せ集めではない**：403 スキル / 57 パック / 27 ドメイン / 108 チェーン——1 パック = AI にそのまま渡せる具体的な仕事（「PR レビュー」「記事を 16 つの中国語プラットフォームへ同時配信」）。
- **粒度は選べる**：単一 `SKILL.md`、パック単体 zip、[`_all.zip`](https://github.com/x33834/awesome-skillkit/releases/latest/download/_all.zip) の全量——解凍して skills ディレクトリへ入れ、新しいセッションで設定なしで動作。
- **まず見てから**：[公式サイト](https://x33834.github.io/awesome-skillkit/) でスキル / ドメイン / パックを検索してカードから直接ダウンロード（日英中 README + 双語サイト）。または AI に `find_skill.py search <キーワード>` を実行させる。
- **品質は検証可能**：`tools/validate_skills.py` が **0 errors / 0 warnings** を通過（manifest と配布 zip のダイジェスト相互固定）、CI が全 PR でユニットテスト実行。
- **Agent 対応**：[`AGENTS.md`](AGENTS.md) がタスク開始時・作業途中のスキル先行確認を規定、[`skills/skill_chains.json`](skills/skill_chains.json) がワークフロー内のスキル連携を記録。

## ダウンロードガイド — 2 つの経路

### パス A · 公式サイトを見る（一番簡単）

1. **<https://x33834.github.io/awesome-skillkit/>** を開きます。
2. スキル名、ドメインチップ、パック名で検索します。
3. 任意のスキルカードで **↓ SKILL.md** をクリックすると単一ファイルをダウンロードできます。パックカードからパック全体を zip でダウンロードすることもできます。
4. 全部まとめて取得するには、ヒーローセクションの **↓ `_all.zip`** をクリックします。

### パス B · リポジトリを直接見る

| 欲しいもの | 入手先 |
|---|---|
| 単一の `SKILL.md` | [`skills/`](skills/) をブラウズしてファイルをそのまま開く |
| 1 パックを zip で | [`dist/<pack-id>.zip`](dist/)（ローカルビルド）または [Releases](https://github.com/x33834/awesome-skillkit/releases/latest) のパック別アセット |
| 全パックをまとめて | `dist/_all.zip`、または [`_all.zip` リリースアセット](https://github.com/x33834/awesome-skillkit/releases/latest/download/_all.zip) |
| Expert Teams 資産（18 チーム / 219 エージェント） | [`expert-teams/`](expert-teams/) — すべて Markdown；または[4 プラットフォーム用パッケージ](https://x33834.github.io/awesome-skillkit/expert-teams.html#download)（OpenCode / Claude Code / Cursor / Gemini CLI）を取得 |
| 中国語ミラー | [GitCode](https://gitcode.com/badhope/awesome-skillkit) · [Gitee](https://gitee.com/badhope/awesome-skillkit)（同一タグ、リリース zip 添付） |

> パック別 zip は `python3 build.py` で再ビルドされ、すべての GitHub Release に添付されます。GitCode / Gitee ミラーは同一タグをプッシュし、同一アセットをアップロードしています。

## シナリオパック一覧（全 57 パック）

以下が完全なカタログです。**8 つのシーンライブラリ**ごとにグループ化しています（公式サイトと同じ 2 段階ナビゲーション：シーンライブラリ → ケイパビリティドメイン）。各行はパックフォルダへのリンクになっており、スキル列には同梱されるすべての `SKILL.md` を列挙しています。

### 🛠 ソフトウェア開発 · 21 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`api-development`](packs/api-development) | API Development & Testing | API開発とテスト | 2 | `api-design-reviewer`, `api-test-suite-builder` |
| [`architecture`](packs/architecture) | System Architecture | システムアーキテクチャ設計 | 3 | `senior-architect`, `migration-architect`, `monorepo-navigator` |
| [`ci-cd`](packs/ci-cd) | CI/CD Pipeline | CI/CDパイプライン | 3 | `ci-cd-pipeline-builder`, `ship-gate`, `spec-driven-workflow` |
| [`cloud-platforms`](packs/cloud-platforms) | Cloud Platforms | クラウドプラットフォームツールボックス | 12 | `azure-compute`, `azure-ai`, `azure-deploy`, `azure-messaging`, `azure-storage`, `workers-best-practices`, `cloudflare`, `wrangler`, `supabase`, `supabase-postgres-best-practices`, `firebase-basics`, `firebase-security-rules-auditor` |
| [`code-planning`](packs/code-planning) | Code Planning & Generation | コード計画と生成 | 3 | `code-intent-planner`, `code-generator`, `debug-diagnoser` |
| [`code-quality-pro`](packs/code-quality-pro) | Code Quality Pro | コード品質プロ | 13 | `code-review-excellence`, `debugging-strategies`, `e2e-testing-patterns`, `error-handling-patterns`, `api-design-principles`, `architecture-patterns`, `sql-optimization-patterns`, `postgresql-table-design`, `auth-implementation-patterns`, `monorepo-management`, `deployment-pipeline-design`, `git-advanced-workflows`, `open-code-review` |
| [`code-review`](packs/code-review) | Code Review | コードレビュー | 4 | `code-reviewer`, `api-design-reviewer`, `tech-debt-tracker`, `dependency-auditor` |
| [`containers`](packs/containers) | Containers & Orchestration | コンテナとオーケストレーション | 3 | `docker-development`, `helm-chart-builder`, `kubernetes-operator` |
| [`cybersecurity-pro`](packs/cybersecurity-pro) | Cybersecurity Pro | サイバーセキュリティ実践精選 | 14 | `analyzing-memory-dumps-with-volatility`, `analyzing-linux-audit-logs-for-intrusion`, `analyzing-security-logs-with-splunk`, `analyzing-network-traffic-with-wireshark`, `analyzing-cobalt-strike-beacon-configuration`, `analyzing-malware-behavior-with-cuckoo-sandbox`, `analyzing-ransomware-encryption-mechanisms`, `analyzing-email-headers-for-phishing-investigation`, `analyzing-kubernetes-audit-logs`, `analyzing-azure-activity-logs-for-threats`, `analyzing-sbom-for-supply-chain-vulnerabilities`, `analyzing-threat-actor-ttps-with-mitre-attack`, `detecting-dcsync-attack-in-active-directory`, `hunting-for-lateral-movement-via-wmi` |
| [`database`](packs/database) | Database Design & Management | データベース設計と管理 | 2 | `database-designer`, `sql-database-assistant` |
| [`engineering-playbook`](packs/engineering-playbook) | Engineering Playbook | エンジニアリング方法論ハンドブック | 21 | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `verification-before-completion`, `writing-plans`, `spec-driven-development`, `planning-and-task-breakdown`, `code-review-and-quality`, `debugging-and-error-recovery`, `shipping-and-launch`, `incremental-implementation`, `tdd`, `handoff`, `grill-me` |
| [`github-workflow`](packs/github-workflow) | GitHub Collaboration | GitHubコラボレーション | 3 | `git-worktree-manager`, `changelog-generator`, `code-reviewer` |
| [`hf-ml-hub`](packs/hf-ml-hub) | Hugging Face ML Hub | Hugging Face機械学習 | 11 | `hf-cli`, `huggingface-datasets`, `huggingface-papers`, `huggingface-community-evals`, `trl-training`, `train-sentence-transformers`, `huggingface-spaces`, `huggingface-gradio`, `huggingface-local-models`, `huggingface-llm-trainer`, `huggingface-best` |
| [`incident-response`](packs/incident-response) | Incident Response & SRE | 障害対応とSRE | 3 | `incident-commander`, `runbook-generator`, `slo-architect` |
| [`infrastructure`](packs/infrastructure) | Infrastructure as Code | インフラ as Code | 3 | `terraform-patterns`, `observability-designer`, `kubernetes-operator` |
| [`language-standards`](packs/language-standards) | Language Standards | 言語エンジニアリング規格 | 14 | `go`, `rust`, `python`, `typescript`, `cpp`, `c-sharp`, `java`, `ruby`, `php-development`, `swift`, `elixir`, `kotlin-development`, `sql-best-practices`, `bash-scripting` |
| [`performance`](packs/performance) | Performance Profiling | パフォーマンス最適化 | 1 | `performance-profiler` |
| [`scientific-agent-skills`](packs/scientific-agent-skills) | Scientific Computing | 科学研究計算（厳選） | 12 | `exploratory-data-analysis`, `experimental-design`, `hypothesis-generation`, `literature-review`, `citation-management`, `peer-review`, `polars`, `networkx`, `matplotlib`, `statistical-analysis`, `optimize-for-gpu`, `get-available-resources` |
| [`security`](packs/security) | Security & Secrets | セキュリティとシークレット管理 | 4 | `secrets-vault-manager`, `env-secrets-manager`, `pii-redactor`, `prompt-injection-guard` |
| [`tdd`](packs/tdd) | Test-Driven Development | テスト駆動開発 | 4 | `tdd-guide`, `webapp-flow-tester`, `webapp-e2e-harness`, `agent-eval-harness` |
| [`web-ops`](packs/web-ops) | Web Operations | ウェブ操作 | 1 | `web-data-extractor` |

### 🤖 AI とエージェント · 5 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`ai-agent-development`](packs/ai-agent-development) | AI Agent Development | AI Agent開発 | 5 | `agent-designer`, `mcp-server-builder`, `feature-flags-architect`, `self-eval`, `skill-tester` |
| [`caveman-toolkit`](packs/caveman-toolkit) | Caveman Toolkit | Caveman トークン節約ツールキット | 7 | `caveman`, `caveman-commit`, `caveman-review`, `caveman-help`, `caveman-stats`, `caveman-compress`, `cavecrew` |
| [`chat-prompt-craft`](packs/chat-prompt-craft) | Chat Prompt Craft | チャットプロンプト術 | 1 | `chat-prompt-engineer` |
| [`memory-systems`](packs/memory-systems) | Memory Systems | 長期記憶システム | 4 | `memory-architect`, `memory-extractor`, `memory-manager`, `memory-retriever` |
| [`skill-forge`](packs/skill-forge) | Skill Forge | スキル鍛造所 | 5 | `skill-author`, `skill-linter`, `skill-finder`, `session-handoff`, `weekly-report-generator` |

### 🎨 コンテンツとクリエイティブ · 13 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`ai-media-toolkit`](packs/ai-media-toolkit) | AI Media Toolkit | AIメディア生成ツールボックス | 3 | `video-generation`, `image-generation`, `music-generation` |
| [`ai-research-writing`](packs/ai-research-writing) | AI Research & Writing | AIリサーチ＆ライティング | 18 | `deep-research`, `web-search`, `paper-topic-selector`, `article-outliner`, `article-drafter`, `content-editor`, `seo-optimizer`, `lit-review`, `experiment-runner`, `arch-diagram`, `neural-net-draw`, `latex-formatter`, `self-reviewer`, `journal-adapt`, `anti-defensive`, `ai-humanizer`, `tex-cleaner`, `pub-plotter` |
| [`ai-video-pipeline`](packs/ai-video-pipeline) | AI Video Pipeline | AIショート動画制作パイプライン | 9 | `video-script-writer`, `video-voice-synth`, `video-lip-sync`, `video-editor`, `video-subtitles`, `video-thumbnail`, `transition-designer`, `motion-effects-designer`, `sound-designer` |
| [`audio-studio`](packs/audio-studio) | Audio Studio | オーディオスタジオ | 4 | `podcast-producer`, `tts-voice-director`, `episode-publisher`, `sound-designer` |
| [`content-publishing`](packs/content-publishing) | Content Publishing Automation | コンテンツ多プラットフォーム自動公開 | 18 | `zhihu-content-manager`, `cnblogs-skill`, `wechat-mp-publisher`, `juejin-publisher`, `csdn-publisher`, `jianshu-publisher`, `bilibili-publisher`, `toutiao-publisher`, `baijiahao-publisher`, `xiaohongshu-publisher`, `weibo-publisher`, `douban-publisher`, `v2ex-publisher`, `segmentfault-publisher`, `oschina-publisher`, `static-blog-deploy`, `cross-post-orchestrator`, `image-generation` |
| [`creator-boosters`](packs/creator-boosters) | Creator Boosters | クリエイター強化ツール | 5 | `humanizer`, `diagram-design`, `archify`, `archify-review`, `video-shotcraft` |
| [`de-ai-writing`](packs/de-ai-writing) | De-AI Writing | AIっぽさ除去ライティング | 3 | `ai-trace-auditor`, `humanize-rewriter`, `personal-voice-profile` |
| [`image-studio`](packs/image-studio) | Image Studio | 画像生成ワークベンチ | 4 | `image-prompt-engineer`, `image-generation`, `visual-style-anchor`, `image-batch-processor` |
| [`video-code`](packs/video-code) | Code-Driven Video (HyperFrames) | コード動画（HyperFrames） | 5 | `hyperframes`, `hyperframes-cli`, `hyperframes-animation`, `hyperframes-audio`, `hyperframes-keyframes` |
| [`video-design-studio`](packs/video-design-studio) | Video Design Studio | 動画デザインスタジオ | 5 | `storyboard-designer`, `shot-designer`, `visual-style-anchor`, `transition-designer`, `motion-effects-designer` |
| [`viral-entertainment`](packs/viral-entertainment) | Viral Entertainment | バズるエンタメシナリオ | 2 | `ai-baby-podcast`, `nailong-laugh-shorts` |
| [`visual-design-studio`](packs/visual-design-studio) | Visual Design Studio | ビジュアルデザインスタジオ | 7 | `design-brief-interpreter`, `image-prompt-engineer`, `layout-spec-auditor`, `frontend-design-director`, `frontend-component-lab`, `ui-ux-accessibility`, `design-system-foundations` |
| [`wechat-longform`](packs/wechat-longform) | WeChat Longform Studio | WeChat長文スタジオ | 10 | `baoyu-post-to-wechat`, `baoyu-format-markdown`, `baoyu-markdown-to-html`, `baoyu-cover-image`, `baoyu-article-illustrator`, `baoyu-infographic`, `baoyu-wechat-summary`, `baoyu-translate`, `baoyu-xhs-images`, `baoyu-slide-deck` |

### 📊 データと研究 · 2 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`data-ml-science`](packs/data-ml-science) | Data, ML & Scientific Computing | データ・機械学習・科学計算 | 7 | `etl-builder`, `feature-engineer`, `model-formulator`, `model-solver`, `simulation-runner`, `result-visualizer`, `ml-pipeline` |
| [`dataviz-studio`](packs/dataviz-studio) | Data Viz Studio | データ可視化スタジオ | 2 | `dashboard-designer`, `chart-recommender` |

### 🗂 オフィスと効率化 · 7 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`communication-essentials`](packs/communication-essentials) | Communication Essentials | コミュニケーション必携 | 2 | `tactful-communication`, `decision-debiasing` |
| [`feishu-suite`](packs/feishu-suite) | Feishu Suite (official Lark CLI) | Feishu スイート（公式 CLI） | 28 | `lark-approval`, `lark-apps`, `lark-attendance`, `lark-base`, `lark-calendar`, `lark-contact`, `lark-doc`, `lark-drive`, `lark-event`, `lark-im`, `lark-mail`, `lark-markdown`, `lark-meeting`, `lark-minutes`, `lark-note`, `lark-okr`, `lark-openapi-explorer`, `lark-shared`, `lark-sheets`, `lark-skill-maker`, `lark-slides`, `lark-task`, `lark-vc`, `lark-vc-agent`, `lark-whiteboard`, `lark-wiki`, `lark-workflow-meeting-summary`, `lark-workflow-standup-report` |
| [`google-workspace`](packs/google-workspace) | Google Workspace | Google Workspaceスイート | 12 | `gws-shared`, `gws-gmail`, `gws-gmail-send`, `gws-calendar`, `gws-calendar-agenda`, `gws-drive`, `gws-docs`, `gws-sheets`, `gws-tasks`, `gws-people`, `gws-workflow-standup-report`, `gws-workflow-weekly-digest` |
| [`knowledge-base`](packs/knowledge-base) | Knowledge Base | パーソナル知識ベース | 2 | `personal-wiki`, `knowledge-graph-builder` |
| [`office-productivity`](packs/office-productivity) | Office Productivity | 業務効率ツールボックス | 10 | `ppt-builder`, `excel-assistant`, `resume-tailor`, `meeting-notes`, `internal-comms-writer`, `docx-writer`, `pdf-pipeline`, `epub-builder`, `docx-template-fill`, `career-ops-lite` |
| [`toolsmith`](packs/toolsmith) | Toolsmith | ツールと自動化 | 6 | `file-organizer`, `batch-renamer`, `format-converter`, `task-scheduler`, `invoice-organizer`, `bank-statement-reconcile` |
| [`workspace-integrations`](packs/workspace-integrations) | Workspace Integrations | 外部連携ツールボックス | 4 | `notion-workspace`, `feishu-dingtalk-bridge`, `issue-tracker-sync`, `cloud-drive-manager` |

### 📈 ビジネスと成長 · 6 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`cmo-suite`](packs/cmo-suite) | CMO & C-Suite Suite | CMO・経営層スイート | 12 | `landing`, `linkedin-analytics`, `linkedin-content`, `linkedin-engagement`, `linkedin-profile`, `linkedin-strategy`, `ceo-advisor`, `cfo-advisor`, `cmo-advisor`, `cto-advisor`, `chro-advisor`, `ciso-advisor` |
| [`company-playbooks`](packs/company-playbooks) | Company Playbooks | 企業運営プレイブック | 13 | `scenario-planning`, `market-entry`, `agent-hierarchy`, `operating-cadence`, `process-design`, `business-continuity-and-resilience`, `vendor-management`, `service-level-management`, `program-management`, `dependency-and-risk-management`, `estimating-and-contingency`, `unit-economics`, `pricing-and-packaging` |
| [`growth-marketing`](packs/growth-marketing) | Growth Marketing | グロースマーケティング | 3 | `product-copywriter`, `campaign-designer`, `channel-adapter` |
| [`gtm-growth`](packs/gtm-growth) | GTM Growth Suite | GTM グローススイート | 16 | `meta-ads-analyzer`, `google-search-ads-builder`, `ad-angle-miner`, `competitor-ad-intelligence`, `ad-to-landing-page-auditor`, `paid-channel-prioritizer`, `launch-positioning-builder`, `brand-voice-extractor`, `battlecard-generator`, `competitor-intel`, `competitive-pricing-intel`, `campaign-brief-generator`, `content-repurposing`, `seo-opportunity-finder`, `github-repo-signals`, `community-signals` |
| [`knowledge-work`](packs/knowledge-work) | Knowledge Work Suite | ナレッジワークスイート | 21 | `comp-analysis`, `interview-prep`, `onboarding`, `performance-review`, `policy-lookup`, `recruiting-pipeline`, `review-contract`, `legal-risk-assessment`, `compliance-check`, `triage-nda`, `variance-analysis`, `audit-support`, `process-optimization`, `risk-assessment`, `status-report`, `ticket-triage`, `draft-response`, `kb-article`, `user-research`, `research-synthesis`, `ux-copy` |
| [`product-management`](packs/product-management) | Product Management | プロダクトマネジメント | 14 | `create-prd`, `outcome-roadmap`, `prioritization-frameworks`, `user-stories`, `job-stories`, `stakeholder-map`, `pre-mortem`, `sprint-plan`, `north-star-metric`, `competitive-battlecard`, `market-sizing`, `user-personas`, `to-spec`, `triage` |

### 🎓 学習と教育 · 2 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`edu-craft`](packs/edu-craft) | Edu Craft | 教育クラフト | 3 | `course-designer`, `exercise-generator`, `feynman-explainer` |
| [`homework-autopilot`](packs/homework-autopilot) | Homework Autopilot | 宿題オートパイロット | 3 | `assignment-intake`, `solution-drafter`, `own-voice-rewrite` |

### 🏠 生活と個人 · 1 パック

| Pack ID | パック名 (英語) | パック名 (日本語) | スキル数 | 同梱スキル |
|---|---|---|:---:|---|
| [`life-essentials`](packs/life-essentials) | Life Essentials | 生活必携 | 4 | `home-renovation-avoidance`, `medical-visit-guide`, `car-purchase-maintenance`, `rental-contract-guide` |

> 一部のスキル（例: `api-design-reviewer`、`kubernetes-operator`、`image-generation`）は複数のパックに登場しますが、シナリオをまたいで再利用されるためです——意図的な設計です。

## インストール方法（30 秒）

1. 必要なシナリオの zip を**ダウンロード**します（または `_all.zip` を取得）。
2. **解凍**すると、スキルごとに 1 フォルダ（各 `SKILL.md` を含む）が得られます。
3. スキルフォルダを AI ツールの skills ディレクトリに**ドラッグ**します:
   - Claude Code: `~/.claude/skills/`（グローバル）または `.claude/skills/`（プロジェクト別）
   - その他の skills 対応ツール: 各ツールのドキュメントに記載された skills ディレクトリを使用します。
4. **新しいセッションを開始**します。環境変数も設定も不要——ユーザーのリクエストがスキルの説明に一致すると、自動的に起動します。

## AI と一緒に使う — まずスキルを確認

AI エージェントが本リポジトリで作業するときは、[AGENTS.md](AGENTS.md) のグローバルルールに従います：**各タスクの開始時、および新しい段階に入ったとき・サブ問題に出会ったとき、まず本リポジトリに該当するスキルがあるか確認し、あればそれを使うこと。**

1. 説明を確認：`skills/**/SKILL.md` の frontmatter `description`（トリガー語 / "Use when" / "Do NOT"）が照合基準です。
2. キーワード検索：`python3 skills/meta/skill-finder/scripts/find_skill.py search <キーワード>`。
3. 複数ステップのタスクは [`skills/skill_chains.json`](skills/skill_chains.json) の `domains[].entry`（オーケストレーター）から入って chain の step をたどります。

該当がなければ通常どおり進みます。無理にスキルを当てはめないこと。

## ソースからビルドする

```bash
python3 build.py     # regenerates dist/<pack-id>.zip for every pack + dist/_all.zip
```

`build.py` は [`manifest.json`](manifest.json) と `packs/*/pack.json` を読み込み、`skills/` から参照されたスキルフォルダをステージングして zip を書き出します。`dist/` ディレクトリは gitignore されており、CI / Releases がビルド成果物を添付します。

## コントリビュート

[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。要点: 新しいパックはまず issue を立ててください。新規スキルには `SKILL.md`、`packs/*/pack.json` への出典明記、[`tests/`](tests/) 配下のスモークテストが必須です。

## ライセンス

[Apache License 2.0](LICENSE) © 2026 Morningstar202604
