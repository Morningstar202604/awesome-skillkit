# awesome-skillkit

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE) ![Skills](https://img.shields.io/badge/skills-113-brightgreen) ![Packs](https://img.shields.io/badge/scenes-27-blue)

[English](README.md) | [中文](README.zh-CN.md) | **日本語**

> 🌐 **オンライン閲覧** — 113 個のスキルを検索し、任意の `SKILL.md` 単体またはパック zip をダウンロードできます：
> [GitHub Pages](https://ms33834.github.io/awesome-skillkit/) · [GitCode Pages](https://gitcode.host/badhope/awesome-skillkit)
> （手順は [docs/DEPLOY-SITE.md](docs/DEPLOY-SITE.md)）

AI ツール向けに厳選された**シーンパック**のコレクションです。**各パック = 一つの実務シナリオに対応し、厳選した複数のスキルを同梱しています。** zip をダウンロード → 解凍 → スキルフォルダを AI ツールの skills ディレクトリにドラッグするだけで、すぐに使えます。

## コンセプト

**答えは「シナリオ」——プラットフォームとツールに根ざす。**

- 各パックは、漠然としたドメインではなく、一つの**具体的なシナリオ**（「PR をレビューする」「CI/CD パイプラインを組む」「ブログに投稿する」）に対応します。
- 各パックには、そのシナリオで協調動作するスキル群を同梱 —— 狭いシナリオ向けの 2 個構成から、16 の中国プラットフォームをエンドツーエンドでカバーする 18 スキルのフルセット（`content-publishing`）まで。数百のバラバラなスキルから探し回る必要はもうありません。
- すべてのスキルの**ソースを明記**（「Source」列参照）。どこから来たのかが常に分かります。

## シーンパック一覧

| パック | シナリオ | スキル数 | サイズ |
|--------|----------|----------|--------|
| ai-agent-development | AI エージェント開発 | 5 | 151 KB |
| ai-media-toolkit | AI メディア生成 | 4 | 19 KB |
| ai-research-writing | AI リサーチとライティング | 19 | 129 KB |
| ai-video-pipeline | AI ショート動画パイプライン | 6 | 61 KB |
| video-design-studio | 映像デザインスタジオ | 4 | 32 KB |
| visual-design-studio | ビジュアルデザインスタジオ | 3 | 14 KB |
| audio-studio | オーディオスタジオ（ポッドキャスト連鎖） | 3 | 14 KB |
| growth-marketing | グロースマーケティング | 3 | 15 KB |
| edu-craft | 教育クラフト（習得型教学） | 3 | 15 KB |
| chat-prompt-craft | チャットプロンプトクラフト | 1 | 8 KB |
| api-development | API 開発とテスト | 2 | 50 KB |
| architecture | システムアーキテクチャ | 3 | 109 KB |
| ci-cd | CI/CD パイプライン | 3 | 64 KB |
| code-planning | コード計画と生成 | 3 | 74 KB |
| code-review | コードレビュー | 5 | 246 KB |
| containers | コンテナとオーケストレーション | 3 | 67 KB |
| content-publishing | 中国語プラットフォームへの記事・動画公開自動化 | 18 | 132 KB |
| data-ml-science | データ・ML・科学計算 | 7 | 63 KB |
| database | データベース設計と管理 | 2 | 102 KB |
| github-workflow | GitHub 協作ワークフロー | 3 | 39 KB |
| incident-response | インシデント対応と SRE | 3 | 123 KB |
| infrastructure | Infrastructure as Code | 3 | 95 KB |
| office-productivity | オフィス業務 | 4 | 11 KB |
| performance | パフォーマンスプロファイリング | 1 | 11 KB |
| security | セキュリティとシークレット管理 | 2 | 46 KB |
| tdd | テスト駆動開発 | 1 | 50 KB |
| viral-entertainment | バイラルエンタメ（ミーム動画） | 2 | 9 KB |


**27 パック・113 スキル。** ドキュメント：[Direction v2](docs/DIRECTION-V2.md) · [Skill Standard](docs/SKILL-STANDARD-v2.md) · [Versioning](docs/VERSIONING.md) · [Video landscape 調査](docs/VIDEO-LANDSCAPE.md)

## パック詳細

### AI Agent Development（`ai-agent-development`）— 145 KB

**本番級 AI エージェントの構築、マルチエージェントワークフロー、MCP サーバー、フィーチャーフラグ、自己評価。**

| Skill | Source |
|-------|--------|
| agent-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| mcp-server-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| feature-flags-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| self-eval | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| skill-tester | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### API Development & Testing（`api-development`）— 49 KB

**REST API 設計のレビューと、統合/契約テストスイートの生成。**

| Skill | Source |
|-------|--------|
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-test-suite-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### System Architecture（`architecture`）— 108 KB

**システムアーキテクチャの設計、ダウンタイムゼロ移行の計画、モノレポの活用。**

| Skill | Source |
|-------|--------|
| senior-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| migration-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| monorepo-navigator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### CI/CD Pipeline（`ci-cd`）— 60 KB

**実務的な CI/CD パイプライン、リリースゲート、スペック駆動開発ワークフローの生成。**

| Skill | Source |
|-------|--------|
| ci-cd-pipeline-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| ship-gate | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| spec-driven-workflow | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Content Publishing Automation（`content-publishing`）— 127 KB

**知乎・博客园・WeChat 公式アカウント・掘金・CSDN・簡書・ビリビリ・今日頭条・百家号・小紅書・Weibo・豆瓣・V2EX・SegmentFault・OSChina・静的ブログなど、中国の主要プラットフォームへの記事/動画の公開・編集・管理 —— 実戦で検証されたプラットフォームノウハウに加え、クロスポスト編集子と AI カバー画像生成を同梱。**

| Skill | Source |
|-------|--------|
| zhihu-content-manager | skillkit authors (self-authored) |
| cnblogs-skill | skillkit authors (self-authored) |
| wechat-mp-publisher | skillkit authors (self-authored) |
| juejin-publisher | skillkit authors (self-authored) |
| csdn-publisher | skillkit authors (self-authored) |
| jianshu-publisher | skillkit authors (self-authored) |
| bilibili-publisher | skillkit authors (self-authored) |
| toutiao-publisher | skillkit authors (self-authored) |
| baijiahao-publisher | skillkit authors (self-authored) |
| xiaohongshu-publisher | skillkit authors (self-authored) |
| weibo-publisher | skillkit authors (self-authored) |
| douban-publisher | skillkit authors (self-authored) |
| v2ex-publisher | skillkit authors (self-authored) |
| segmentfault-publisher | skillkit authors (self-authored) |
| oschina-publisher | skillkit authors (self-authored) |
| static-blog-deploy | skillkit authors (self-authored) |
| cross-post-orchestrator | skillkit authors (self-authored) |
| ai-cover-generator | skillkit authors (self-authored) |

### Code Review（`code-review`）— 242 KB

**PR レビュー、コード品質分析、依存関係・技術的負債の監査（多言語対応）。**

| Skill | Source |
|-------|--------|
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| code-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| api-design-reviewer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| tech-debt-tracker | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| dependency-auditor | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Containers & Orchestration（`containers`）— 66 KB

**Dockerfile 最適化、docker-compose、Helm チャート、Kubernetes オペレーター。**

| Skill | Source |
|-------|--------|
| docker-development | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| helm-chart-builder | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Database Design & Management（`database`）— 99 KB

**スキーマ設計、ERD 図、マイグレーション、SQL クエリ最適化。**

| Skill | Source |
|-------|--------|
| database-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| sql-database-assistant | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### GitHub Collaboration（`github-workflow`）— 43 KB

**並列 worktree、Conventional Commits ベースの変更履歴、GitHub PR レビュー。**

| Skill | Source |
|-------|--------|
| git-worktree-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| changelog-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| pr-review-expert | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Incident Response & SRE（`incident-response`）— 122 KB

**インシデント指揮、ランブック生成、SLO/エラー予算の定義。**

| Skill | Source |
|-------|--------|
| incident-commander | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| runbook-generator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| slo-architect | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Infrastructure as Code（`infrastructure`）— 96 KB

**Terraform パターン、オブザーバビリティ設計、Kubernetes オペレーター。**

| Skill | Source |
|-------|--------|
| terraform-patterns | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| observability-designer | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| kubernetes-operator | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Performance Profiling（`performance`）— 12 KB

**Node.js・Python・Go の CPU/メモリ/IO ボトルネックをプロファイリング。**

| Skill | Source |
|-------|--------|
| performance-profiler | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Security & Secrets（`security`）— 49 KB

**シークレットボールトの構築と環境変数の衛生管理。**

| Skill | Source |
|-------|--------|
| secrets-vault-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |
| env-secrets-manager | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |

### Test-Driven Development（`tdd`）— 55 KB

**単体テスト・フィクスチャ・モックの作成と、レッド/グリーン/リファクタリングサイクルの支援。**

| Skill | Source |
|-------|--------|
| tdd-guide | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT) |


### AI Media Generation（`ai-media-toolkit`）— 19 KB

**ローカル生成ゲートウェイ経由でテキスト/画像→動画・画像の生成、音楽生成、カバー画像作成。送信/ポーリング/ダウンロードのフルワークフローと失敗時の対処表を内蔵。**

| Skill | Source |
|-------|--------|
| video-generation | self-authored |
| image-generation | self-authored |
| music-generation | self-authored |
| ai-cover-generator | self-authored |

### Office Productivity（`office-productivity`）— 11 KB

**日常オフィス業務の四点セット：実際の .pptx を生成するスライド作成、ビフォー/アフター証拠付きの Excel クリーニング分析、JD 駆動の履歴書カスタマイズ（捏造禁止ルール付き）、構造化議事録。**

| Skill | Source |
|-------|--------|
| ppt-builder | self-authored |
| excel-assistant | self-authored |
| resume-tailor | self-authored |
| meeting-notes | self-authored |

### 映像デザインスタジオ（`video-design-studio`）— 32 KB

**AI映像のプリプロダクション設計層：絵コンテ設計（ビートシート＋シーン別プロンプト対＋連続性制約＋機械検証）、12レシピカードによるショットリスト設計、クロスモデル text-to-video プロンプトエンジニアリング（6スロット構造＋構造監査）、ビジュアルスタイルアンカー＋キャラクター一貫性カード。手法はオープンソース（video-storyboard / video-shotcraft / visual-skills）に由来し、各スキルの sources-and-methodology.md でクレジット。**

| Skill | Source |
|-------|--------|
| storyboard-designer | self-authored |
| shot-recipe-designer | self-authored |
| video-prompt-engineer | self-authored |
| visual-style-anchor | self-authored |

### ビジュアルデザインスタジオ（`visual-design-studio`）— 14 KB

**AI ビジュアルデザイン連鎖：要件 → 仕様書 → プロンプト → レイアウト監査。design-brief-interpreter が曖昧な要求を機械検証可能な 7 項目仕様書に変換し、image-prompt-engineer が 5 セグメント構造の文生画像プロンプト（モデル方言・文字描画ルール込み）を書き、layout-spec-auditor が内蔵プラットフォーム仕様表で比率/解像度/セーフエリア/文字予算を監査する。**

| Skill | ソース |
|-------|--------|
| design-brief-interpreter | self-authored |
| image-prompt-engineer | self-authored |
| layout-spec-auditor | self-authored |

### オーディオスタジオ（`audio-studio`）— 14 KB

**AI ポッドキャスト連鎖：話題/文書 → 台本 → 音声 → 発売可能なエピソード。podcast-producer が TTS セーフな分段台本（lint 付き）を書き、tts-voice-director が音声カタログからキャスティングと ffmpeg 接続計画を立て、episode-publisher が shownotes・タイムスタンプ章・プラットフォームメタデータ（AI 開示行込み）を出力する。**

| Skill | ソース |
|-------|--------|
| podcast-producer | self-authored |
| tts-voice-director | self-authored |
| episode-publisher | self-authored |

### グロースマーケティング（`growth-marketing`）— 15 KB

**EC マーケティング連鎖：product-copywriter が転換フレームワーク（FAB/PAS/AIDA）と異議処理を選び、campaign-designer がカレンダー・チャネルマトリクス・単変量 A/B を計画し、channel-adapter が内蔵制約表に基づき channel_fit_check.py で検証しながら各チャネル版を書き出す。**

| Skill | ソース |
|-------|--------|
| product-copywriter | self-authored |
| campaign-designer | self-authored |
| channel-adapter | self-authored |

### 教育クラフト（`edu-craft`）— 15 KB

**習得型教学連鎖：course-designer が学習契約 + 依存順 checkpoint を設計し、exercise-generator が選択肢問題禁止の厳格な記述式問題（ルーブリック付き）を exercise_lint.py で検証しながら生成し、feynman-explainer が未通過 checkpoint に対し 6 拍フェイマンループで再テスト合格まで補習する。**

| Skill | ソース |
|-------|--------|
| course-designer | self-authored |
| exercise-generator | self-authored |
| feynman-explainer | self-authored |



### Viral Entertainment（`viral-entertainment`）— 11 KB

**特別エンタメシナリオ：AI 赤ちゃんポッドキャストの制作パイプラインと「大笑いナーゴン」風マスコットミーム動画——キャラクター一貫性の規律とプラットフォーム準拠を内蔵。**

| Skill | Source |
|-------|--------|
| ai-baby-podcast | self-authored |
| nailong-laugh-shorts | self-authored |

### チャットプロンプトクラフト（`chat-prompt-craft`）— 8 KB

**会話型 AI アシスタント（豆包、ChatGPT、Kimi、DeepSeek など）向けプロンプトエンジニアリング：（役割 + 背景 + タスク + 要件 + 形式）の五要素式で一次性タスクプロンプト、五段スケルトンでエージェント人設 system prompt、冗長を削る逆方向制約、ヒューリスティック構造監査付き。**

| Skill | Source |
|-------|--------|
| chat-prompt-engineer | self-authored |

## ディレクトリ構成

```
packs/                          # シーンパック定義（シナリオごとに 1 ディレクトリ）
├── code-review/                #   pack.json：シナリオのメタデータ + スキル一覧 + ソース
├── ci-cd/
├── containers/
├── database/
├── api-development/
├── github-workflow/
├── architecture/
├── incident-response/
├── infrastructure/
├── ai-agent-development/
├── security/
├── performance/
└── tdd/
skills/                         # 全スキルコードの唯一の真実の源（Single Source of Truth）
├── programming/                # 上流から厳選（多階層タクソノミー）
└── writing/                    # 自作シナリオスキル
    ├── blog/                   #   cnblogs / CSDN / 簡書 / 静的ブログデプロイ
    ├── zhihu/  wechat/  juejin/#   プラットフォーム別パブリッシャー
    ├── social/                 #   小紅書 / Weibo
    ├── video/  news/           #   ビリビリ / 今日頭条 / 百家号
    ├── community/              #   V2EX / SegmentFault / OSChina / 豆瓣
    ├── assets/  orchestrator/  #   AI カバー画像 / クロスポスト編集子
    └── _common/                #   共有 HTTP/dry-run/認証情報ヘルパー（スキルではない）
dist/                           # ビルド成果物：シーンパックごとに 1 zip（gitignore 済み）
```

## 使い方（30 秒）

1. **Releases** から必要な**シーン**の zip をダウンロード（または `python3 build.py` で `dist/*.zip` をローカル生成）。
2. 解凍すると**複数のスキルフォルダ**（各フォルダに `SKILL.md`）が得られます。
3. スキルフォルダを AI ツールの skills ディレクトリに**ドラッグ**：
   - Claude Code：`~/.claude/skills/`（グローバル）またはプロジェクト内 `.claude/skills/`（プロジェクト限定）
   - 他の skills 対応ツール：各ツールの skills ディレクトリを使用
4. 新しいセッションを開始すればすぐ使えます。設定は不要です。

## ビルドとリリース

ソースは `skills/`、シーンパック定義は `packs/*/pack.json`、zip は Gitee / GitCode / GitHub の Releases で公開します（`dist/` は gitignore 済み）。

```bash
# dist/*.zip の生成（シーンパックごとに 1 zip）
python3 build.py     # 唯一のビルド入口；クロスプラットフォーム；全スキル入りの dist/_all.zip も生成

# リリースフロー（正式リリースは tools/release.py を使用、docs/VERSIONING.md 参照）
python3 tools/release.py 0.13.1 --commit   # CHANGELOG 検証 → bump → commit → tag
git push origin main --follow-tags
# 各プラットフォームの Releases ページで release を作成し dist/*.zip をアップロード
```

## ソースと更新方法

このリポジトリは 2 本のラインで管理しています：

**1. 上流キュレーション** —— 更新はこちらから：

- **上流**：[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（MIT ライセンス）—— 33 個のプログラミングスキルすべて。
- 上流のほぼ重複 2 件（`database-schema-designer`、`agent-workflow-designer`）は兄弟スキルへ統合済み。固有の内容は参考ドキュメントとして存続スキル内に保持されています。

上流の更新を取り込むには：上流リポジトリをクローンし、該当するスキルフォルダを `skills/programming/...` へ再コピーして、`python3 build.py` を再実行してください。

**2. 自作シナリオスキル**（`skills/writing/`、パック `content-publishing`）：

- `zhihu-content-manager` / `cnblogs-skill` / `wechat-mp-publisher` / `juejin-publisher` / `csdn-publisher` / `jianshu-publisher` / `bilibili-publisher` / `toutiao-publisher` / `baijiahao-publisher` / `xiaohongshu-publisher` / `weibo-publisher` / `douban-publisher` / `v2ex-publisher` / `segmentfault-publisher` / `oschina-publisher` / `static-blog-deploy` / `cross-post-orchestrator` / `ai-cover-generator` —— 上流がカバーしない中国プラットフォーム特有の自動化ノウハウをまとめたものです。本リポジトリで保守し、実行可能なチェックスクリプトとユニットテストを同梱。書き込み操作はデフォルトで dry-run です。

スキルごとの詳細な帰属情報は [manifest.json](manifest.json)、各 `packs/*/pack.json`、[SOURCES.md](SOURCES.md) を参照してください。

## 注意事項

- 非コアファイル（`.github`、`.gitignore`、`docker-compose.yml` など）は zip に含めません。実行に必要な内容（`SKILL.md`、`references/`、`scripts/`、`templates/`）は保持されます。
- スキルごとの依存関係（Playwright、ログイン状態など）は各スキルの `SKILL.md` に記載されています。

## ライセンス

[Apache License 2.0](LICENSE) © 2026 Morningstar202604

---
