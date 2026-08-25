# awesome-skillkit

[English](README.md) | [中文](README.zh-CN.md) | **日本語**

AI ツール向けに厳選された**シーンパック**のコレクションです。**各パック = 一つの実務シナリオに対応し、厳選した複数のスキルを同梱しています。** zip をダウンロード → 解凍 → スキルフォルダを AI ツールの skills ディレクトリにドラッグするだけで、すぐに使えます。

## コンセプト

**答えは「シナリオ」——プラットフォームとツールに根ざす。**

- 各パックは、漠然としたドメインではなく、一つの**具体的なシナリオ**（「PR をレビューする」「CI/CD パイプラインを組む」「ブログに投稿する」）に対応します。
- 各パックには、そのシナリオで協調動作するスキル群を同梱 —— 狭いシナリオ向けの 2 個構成から、16 の中国プラットフォームをエンドツーエンドでカバーする 18 スキルのフルセット（`content-publishing`）まで。数百のバラバラなスキルから探し回る必要はもうありません。
- すべてのスキルの**ソースを明記**（「Source」列参照）。どこから来たのかが常に分かります。

## シーンパック一覧

| パック | シナリオ | スキル数 | サイズ |
|--------|----------|----------|--------|
| ai-agent-development | AI エージェント開発 | 5 | 145 KB |
| api-development | API 開発とテスト | 2 | 49 KB |
| architecture | システムアーキテクチャ | 3 | 108 KB |
| ci-cd | CI/CD パイプライン | 3 | 60 KB |
| code-review | コードレビュー | 5 | 242 KB |
| containers | コンテナとオーケストレーション | 3 | 66 KB |
| content-publishing | 中国語プラットフォームへの記事・動画公開自動化 | 18 | 127 KB |
| database | データベース設計と管理 | 2 | 99 KB |
| github-workflow | GitHub 協作ワークフロー | 3 | 43 KB |
| incident-response | インシデント対応と SRE | 3 | 122 KB |
| infrastructure | Infrastructure as Code | 3 | 96 KB |
| performance | パフォーマンスプロファイリング | 1 | 12 KB |
| security | セキュリティとシークレット管理 | 2 | 49 KB |
| tdd | テスト駆動開発 | 1 | 55 KB |

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
bash build.sh        # macOS / Linux / Git Bash
python3 build.py     # クロスプラットフォーム（bash/zip 不要）；全スキル入りの dist/_all.zip も生成

# リリースフロー
git tag v1.6.2
git push origin v1.6.2
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

[Apache License 2.0](LICENSE) © 2026 weed33834