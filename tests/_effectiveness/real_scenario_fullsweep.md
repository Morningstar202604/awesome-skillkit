# 全库严格场景化实测报告（第三代证明）

> 生成：2026-09-22 01:19 UTC　|　LLM 模式：开（agnes-2.5-flash）
> 总数 169 = **pass 63** / fail 78 / error 3 / no-example 25 / spec-error 0

> 场景来源：每个技能 SKILL.md 的用法示例 + 旗舰技能苛刻覆盖表；
> 断言：退出码、JSON 契约字段、产物文件存在且非空、无 traceback、诚实标注。

## FAIL / ERROR 明细（技能 bug 候选）

### `audio/podcast-producer` — FAIL
- scenario: --file script.md --dialogue
- argv: `['--file', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_script.md', '--dialogue']`
- reason: rc=1
- stdout 尾: `     "rule": "overlong_line",
      "detail": "266 chars > 90: split into shorter lines"
    }
  ],
  "count": 12,
  "rules": [
    "overlong_line",
    "speaker_label"
  ],
  "status": "violation"
}
`

### `chat/chat-prompt-engineer` — FAIL
- scenario: --prompt <system prompt> --mode agent
- argv: `['--prompt', '<system prompt>', '--mode', 'agent']`
- reason: rc=1
- stdout 尾: `lse,
    "constraints": false,
    "output-format": false,
    "boundary": false
  },
  "missing": [
    "persona",
    "capability-flow",
    "constraints",
    "output-format",
    "boundary"
  ]
}
`

### `dataviz/dashboard-designer` — FAIL
- scenario: build <data.csv> --out dashboard.html --title 季度销售看板
- argv: `['build', '<data.csv>', '--out', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_out.json', '--title', '季度销售看板']`
- reason: rc=1
- stderr 尾: `ERROR: CSV 不存在：<data.csv>
`

### `design/layout-spec-auditor` — FAIL
- scenario: --width 896 --height 384 --expect 900x383
- argv: `['--width', '896', '--height', '384', '--expect', '900x383', '--file-mb', '0.4']`
- reason: rc=1
- stdout 尾: `8,
    "bottom_float_zone": 0.15,
    "advice": "keep text away from bottom 15% (platform overlay zone); margin >= 8% of the short edge"
  },
  "missing": [
    "resolution"
  ],
  "status": "fail"
}
`

### `education/exercise-generator` — FAIL
- scenario: --text ; echo exit=$?
- argv: `['--text', ';', 'echo', 'exit=$?']`
- reason: rc=2
- stderr 尾: `usage: exercise_lint.py [-h] [--file FILE] [--text TEXT] [--allow-mcq]
exercise_lint.py: error: unrecognized arguments: echo exit=$?
`

### `integrations/feishu-dingtalk-bridge` — FAIL
- scenario: --help >/dev/null && echo CLI_OK
- argv: `['>/dev/null', '&&', 'echo', 'CLI_OK']`
- reason: rc=2
- stderr 尾: `usage: im_bridge.py [-h] {build-message,parse-webhook} ...
im_bridge.py: error: argument cmd: invalid choice: '>/dev/null' (choose from 'build-message', 'parse-webhook')
`

### `integrations/issue-tracker-sync` — FAIL
- scenario: field-map >/dev/null && echo FIELD_MAP_OK
- argv: `['field-map', '>/dev/null', '&&', 'echo', 'FIELD_MAP_OK']`
- reason: rc=2
- stderr 尾: `usage: issue_sync.py [-h] {build,field-map,weekly-report} ...
issue_sync.py: error: unrecognized arguments: >/dev/null && echo FIELD_MAP_OK
`

### `integrations/notion-workspace` — FAIL
- scenario: --help >/dev/null && echo CLI_OK
- argv: `['>/dev/null', '&&', 'echo', 'CLI_OK']`
- reason: rc=2
- stderr 尾: `tabase-query,parse-page,blocks-to-markdown} ...
notion_ops.py: error: argument cmd: invalid choice: '>/dev/null' (choose from 'build-page', 'build-database-query', 'parse-page', 'blocks-to-markdown')
`

### `knowledge/knowledge-graph-builder` — FAIL
- scenario: export <notes-dir> --format dot --out graph.dot
- argv: `['export', '<notes-dir>', '--format', 'dot', '--out', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_out.json']`
- reason: rc=1
- stderr 尾: `ERROR: 目录不存在：C:\Users\X1882\WorkBuddy\2026-09-19-21-05-15\awesome-skillkit\skills\knowledge\knowledge-graph-builder\<notes-dir>
`

### `knowledge/personal-wiki` — FAIL
- scenario: --help >/dev/null && echo script ok
- argv: `['>/dev/null', '&&', 'echo', 'script ok']`
- reason: rc=2
- stderr 尾: `usage: wiki_build.py [-h] {init,index,search,lint,stats} ...
wiki_build.py: error: argument cmd: invalid choice: '>/dev/null' (choose from 'init', 'index', 'search', 'lint', 'stats')
`

### `marketing/channel-adapter` — FAIL
- scenario: --file variant.md --channel xhs
- argv: `['--file', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_variant.md', '--channel', 'xhs']`
- reason: rc=1
- stdout 尾: `,
    {
      "check": "hook_first_line",
      "pass": true,
      "detail": "first line: '# FastAPI 性能优化实战'",
      "fix": null
    }
  ],
  "missing": [
    "word_budget"
  ],
  "status": "fail"
}
`

### `meta/agent-eval-harness` — ERROR
- scenario: --input cases.jsonl --index 0 --mode judge
- argv: `['--input', 'cases.jsonl', '--index', '0', '--mode', 'judge', '--out', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_out.json']`
- reason: 
- stderr 尾: `AppData\Roaming\Python\Python313\site-packages\sitecustomize.py", line 28, in utf8_open
    return original_open(*args, **kwargs)
FileNotFoundError: [Errno 2] No such file or directory: 'cases.jsonl'
`

### `meta/skill-linter` — FAIL
- scenario: $d --json > /dev/null || exit
- argv: `['$d', '--json', '>', '/dev/null', '||', 'exit', '1']`
- reason: rc=2
- stderr 尾: `usage: lint_skill.py [-h] [--json] [--verbose] target
lint_skill.py: error: unrecognized arguments: > /dev/null || exit 1
`

### `meta/weekly-report-generator` — FAIL
- scenario: --days 7 --input report.json --write -o
- argv: `['--days', '7', '--input', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_report.json', '--write', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=2
- stderr 尾: `[ERROR] . is not a git repo
`

### `office/docx-template-fill` — FAIL
- scenario: --template ./tpl.docx --data ./data.json --list-only
- argv: `['--template', './tpl.docx', '--data', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_data.json', '--list-only']`
- reason: rc=2
- stderr 尾: `[ERROR] template not found: ./tpl.docx
`

### `office/epub-builder` — FAIL
- scenario: --help >/dev/null && echo script ok
- argv: `['>/dev/null', '&&', 'echo', 'script ok']`
- reason: rc=2
- stderr 尾: `usage: epub_build.py [-h] {build,inspect} ...
epub_build.py: error: argument cmd: invalid choice: '>/dev/null' (choose from 'build', 'inspect')
`

### `office/pdf-pipeline` — FAIL
- scenario: rotate merged.pdf --degrees 90 --pages 1-2
- argv: `['rotate', 'merged.pdf', '--degrees', '90', '--pages', '1-2', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stderr 尾: `ERROR: 文件不存在：merged.pdf
`

### `programming/ai-engineering/mcp-server-builder` — FAIL
- scenario: --input out/tool_manifest.json --strict --format text
- argv: `['--input', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_tool_manifest.json', '--strict', '--format', 'text']`
- reason: rc=2
- stderr 尾: `ERROR: Manifest must include a 'tools' array.
`

### `programming/ai-engineering/mcp-server-builder` — FAIL
- scenario: --server-name billing-mcp --language typescript
- argv: `['--server-name', 'billing-mcp', '--language', 'typescript']`
- reason: rc=2
- stderr 尾: `ERROR: No input provided. Use --input <spec-file> or pipe OpenAPI via stdin.
`

### `programming/ai-engineering/skill-tester/assets/sample-skill` — FAIL
- scenario: batch text_files/ --format json --output batch_results.json
- argv: `['batch', 'text_files/', '--format', 'json', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=2
- stderr 尾: `                 {analyze,transform,batch} ...
text_processor.py: error: unrecognized arguments: --format json --output C:\Users\X1882\AppData\Local\Temp\skillkit_scenario_ezbzeej1\in_out_output.json
`

### `programming/ai-engineering/skill-tester` — FAIL
- scenario: <技能路径> --json --detailed --minimum-score 75
- argv: `['<技能路径>', '--json', '--detailed', '--minimum-score', '75']`
- reason: rc=1
- stderr 尾: `{"error": "error: path not found: <\u6280\u80fd\u8def\u5f84>"}
`

### `programming/ai-engineering/skill-tester` — FAIL
- scenario: $skill
- argv: `['$skill']`
- reason: rc=1
- stderr 尾: `error: skill path is not a directory: $skill
`

### `programming/ai-engineering/skill-tester` — FAIL
- scenario: <技能路径
- argv: `['<技能路径']`
- reason: rc=1
- stderr 尾: `error: target not found: <技能路径
`

### `programming/ai-engineering/skill-tester` — FAIL
- scenario: $skill --json
- argv: `['$skill', '--json']`
- reason: rc=1
- stderr 尾: `{"error": "error: skill path is not a directory: $skill"}
`

### `programming/api/api-design-reviewer` — FAIL
- scenario: openapi.json --format json --output lint.json
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_openapi.json', '--format', 'json', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stdout 尾: `Report written to C:\Users\X1882\AppData\Local\Temp\skillkit_scenario_ezbzeej1\in_out_output.json
`

### `programming/api/api-design-reviewer` — FAIL
- scenario: openapi.json --format json --min-grade B --output
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_openapi.json', '--format', 'json', '--min-grade', 'B', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stdout 尾: `Scorecard written to C:\Users\X1882\AppData\Local\Temp\skillkit_scenario_ezbzeej1\in_out_output.json
`
- stderr 尾: `Grade F is below minimum required grade B
`

### `programming/architecture/migration-architect` — FAIL
- scenario: --before assets/database_schema_before.json --after assets/database_schema_after.json --type database
- argv: `['--before', 'C:\\Users\\X1882\\WorkBuddy\\2026-09-19-21-05-15\\awesome-skillkit\\skills\\programming\\architecture\\migration-architect\\assets\\database_schema_before.json', '--after', 'C:\\Users\\X1882\\WorkBuddy\\2026-09-19-21-05-15\\awesome-skillkit\\skills\\programming\\architecture\\migration-architect\\assets\\database_schema_after.json', '--type', 'database', '--format', 'json', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stdout 尾: `Compatibility report saved to C:\Users\X1882\AppData\Local\Temp\skillkit_scenario_ezbzeej1\in_out_o.json
`

### `programming/architecture/migration-architect` — FAIL
- scenario: --input migration_spec.json --format json -o migration_plan.json
- argv: `['--input', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_migration_spec.json', '--format', 'json', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stderr 尾: `Error: Missing required field 'type' in specification
`

### `programming/architecture/migration-architect` — FAIL
- scenario: --input migration_plan.json --format both -o rollback_runbook
- argv: `['--input', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_migration_plan.json', '--format', 'both', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stderr 尾: `Error: Migration plan must contain migration_id or source field
`

### `programming/architecture/monorepo-navigator` — FAIL
- scenario: /path/to/monorepo --json
- argv: `['/path/to/monorepo', '--json']`
- reason: rc=1
- stderr 尾: `Path is not a directory: C:\path\to\monorepo
`

### `programming/architecture/senior-architect` — FAIL
- scenario: ./my-project --format mermaid --type component
- argv: `['./my-project', '--format', 'mermaid', '--type', 'component']`
- reason: rc=1
- stderr 尾: `Error: Project path does not exist: C:\Users\X1882\WorkBuddy\2026-09-19-21-05-15\awesome-skillkit\skills\programming\architecture\senior-architect\my-project
`

### `programming/architecture/senior-architect` — FAIL
- scenario: ./my-project --output json
- argv: `['./my-project', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=2
- stderr 尾: `roject_path
dependency_analyzer.py: error: argument --output/-o: invalid choice: 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json' (choose from 'human', 'json')
`

### `programming/architecture/senior-architect` — FAIL
- scenario: ./my-project --verbose
- argv: `['./my-project', '--verbose']`
- reason: rc=1
- stderr 尾: `Error: Project path does not exist: C:\Users\X1882\WorkBuddy\2026-09-19-21-05-15\awesome-skillkit\skills\programming\architecture\senior-architect\my-project
`

### `programming/cicd/ship-gate` — FAIL
- scenario: <项目根目录> --json --no-interactive
- argv: `['<项目根目录>', '--json', '--no-interactive']`
- reason: rc=1
- stderr 尾: `Error: 'C:\Users\X1882\WorkBuddy\2026-09-19-21-05-15\awesome-skillkit\skills\programming\cicd\ship-gate\<项目根目录>' is not a directory
`

### `programming/code-quality/code-reviewer` — FAIL
- scenario: . --base main --head feature-branch
- argv: `['.', '--base', 'main', '--head', 'feature-branch']`
- reason: rc=1
- stderr 尾: `Error: C:\Users\X1882\WorkBuddy\2026-09-19-21-05-15\awesome-skillkit\skills\programming\code-quality\code-reviewer is not a git repository
`

### `programming/code-quality/dependency-auditor` — FAIL
- scenario: /path/to/project --format json --fail-on-high -o scan.json
- argv: `['/path/to/project', '--format', 'json', '--fail-on-high', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stderr 尾: `Error: Project path does not exist: \path\to\project
`

### `programming/code-quality/dependency-auditor` — FAIL
- scenario: scan.json --risk-threshold medium --timeline 90 --format
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_scan.json', '--risk-threshold', 'medium', '--timeline', '90', '--format', 'json', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stdout 尾: `Warning: Unexpected inventory format
`
- stderr 尾: `Error: 'by_risk'
`

### `programming/code-quality/tdd-guide` — FAIL
- scenario: coverage --report coverage.xml --threshold 80
- argv: `['coverage', '--report', 'coverage.xml', '--threshold', '80']`
- reason: rc=2
- stderr 尾: `error: 文件不存在: coverage.xml
`

### `programming/code-quality/tech-debt-tracker` — FAIL
- scenario: --input-dir snapshots/ --period monthly --format both
- argv: `['--input-dir', 'snapshots/', '--period', 'monthly', '--format', 'both', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stdout 尾: `Directory does not exist: snapshots/
`

### `programming/code-quality/tech-debt-tracker` — FAIL
- scenario: debt_inventory.json --framework wsjf --team-size 6 --sprint-capacity
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_debt_inventory.json', '--framework', 'wsjf', '--team-size', '6', '--sprint-capacity', '20', '--format', 'json', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stdout 尾: `Error loading debt inventory: Invalid debt inventory format
`

### `programming/code-quality/tech-debt-tracker` — FAIL
- scenario: /path/to/codebase --format json --output debt_inventory.json
- argv: `['/path/to/codebase', '--format', 'json', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stdout 尾: `Scan failed: Directory does not exist: /path/to/codebase
`

### `programming/containers/docker-development` — FAIL
- scenario: docker-compose.yml --output json
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_docker-compose.yml', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=2
- stderr 尾: ` [composefile]
compose_validator.py: error: argument --output/-o: invalid choice: 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json' (choose from 'text', 'json')
`

### `programming/containers/docker-development` — FAIL
- scenario: --help >/dev/null 2>&1
- argv: `['>/dev/null', '2>&1']`
- reason: rc=2
- stderr 尾: `usage: dockerfile_analyzer.py [-h] [--output {text,json}] [--security]
                              [dockerfile]
dockerfile_analyzer.py: error: unrecognized arguments: 2>&1
`

### `programming/containers/helm-chart-builder` — FAIL
- scenario: --help >/dev/null 2>&1
- argv: `['>/dev/null', '2>&1']`
- reason: rc=2
- stderr 尾: `usage: chart_analyzer.py [-h] [--output {text,json}] [--security] [chartdir]
chart_analyzer.py: error: unrecognized arguments: 2>&1
`

### `programming/containers/helm-chart-builder` — FAIL
- scenario: mychart/values.yaml --output json
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_values.yaml', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=2
- stderr 尾: `t] [valuesfile]
values_validator.py: error: argument --output/-o: invalid choice: 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json' (choose from 'text', 'json')
`

### `programming/database/database-designer` — FAIL
- scenario: --input schema.sql --generate-erd --output-format json -o
- argv: `['--input', 'schema.sql', '--generate-erd', '--output-format', 'json', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stderr 尾: `Error: [Errno 2] No such file or directory: 'schema.sql'
`

### `programming/database/sql-database-assistant` — FAIL
- scenario: --sqlite app.db --table users --json
- argv: `['--sqlite', 'app.db', '--table', 'users', '--json']`
- reason: rc=2
- stderr 尾: `错误：SQLite 文件不存在: app.db
`

### `programming/github/changelog-generator` — FAIL
- scenario: --input commits.txt --next-version v1.4.0 --format json
- argv: `['--input', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_commits.txt', '--next-version', 'v1.4.0', '--format', 'json']`
- reason: rc=2
- stderr 尾: `ERROR: No valid conventional commit messages found in input.
`

### `programming/github/changelog-generator` — FAIL
- scenario: --current-version 1.3.0 --output-format json
- argv: `['--current-version', '1.3.0', '--output-format', 'json']`
- reason: rc=1
- stderr 尾: `No input data provided
`

### `programming/github/git-worktree-manager` — FAIL
- scenario: --input config.json --format json
- argv: `['--input', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_config.json', '--format', 'json']`
- reason: rc=2
- stderr 尾: `ERROR: Missing required values: --branch and --name (or provide via JSON input).
`

### `programming/incident/incident-commander` — FAIL
- scenario: --help >/dev/null 2>&1
- argv: `['>/dev/null', '2>&1']`
- reason: rc=2
- stderr 尾: `cident_classifier.py [-h] [--input INPUT] [--format {json,text}]
                              [--interactive] [--output OUTPUT]
incident_classifier.py: error: unrecognized arguments: >/dev/null 2>&1
`

### `programming/incident/incident-commander` — FAIL
- scenario: --incident assets/sample_incident_data.json --timeline timeline.md --output pir.md
- argv: `['--incident', 'C:\\Users\\X1882\\WorkBuddy\\2026-09-19-21-05-15\\awesome-skillkit\\skills\\programming\\incident\\incident-commander\\assets\\sample_incident_data.json', '--timeline', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_timeline.md', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=1
- stderr 尾: `Error: Invalid JSON - Expecting value: line 1 column 1 (char 0)
`

### `programming/incident/slo-architect` — FAIL
- scenario: --slo-doc docs/slos/
- argv: `['--slo-doc', 'docs/slos/']`
- reason: rc=2
- stderr 尾: `ERROR: not found: docs/slos/
`

### `programming/infrastructure/kubernetes-operator` — FAIL
- scenario: --crd config/crd/ --format json
- argv: `['--crd', 'config/crd/', '--format', 'json']`
- reason: rc=2
- stderr 尾: `ERROR: not found: config/crd/
`

### `programming/infrastructure/kubernetes-operator` — FAIL
- scenario: --controller controllers/myapp_controller.go
- argv: `['--controller', 'controllers/myapp_controller.go']`
- reason: rc=2
- stderr 尾: `ERROR: not found: controllers/myapp_controller.go
`

### `programming/infrastructure/terraform-patterns` — FAIL
- scenario: ./terraform --output json
- argv: `['./terraform', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=2
- stderr 尾: `] [directory]
tf_module_analyzer.py: error: argument --output/-o: invalid choice: 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json' (choose from 'text', 'json')
`

### `programming/infrastructure/terraform-patterns` — FAIL
- scenario: ./terraform --output json
- argv: `['./terraform', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json']`
- reason: rc=2
- stderr 尾: `ct] [target]
tf_security_scanner.py: error: argument --output/-o: invalid choice: 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json' (choose from 'text', 'json')
`

### `programming/performance/performance-profiler` — FAIL
- scenario: /path/to/project --large-file-threshold-kb 256
- argv: `['/path/to/project', '--large-file-threshold-kb', '256']`
- reason: rc=1
- stderr 尾: `Error: C:\path\to\project is not a directory
`

### `programming/planning/code-generator` — FAIL
- scenario: --plan plan.json --format json --output report.json
- argv: `['--plan', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_plan.json', '--format', 'json', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json', '--output-dir', '.']`
- reason: rc=2
- stderr 尾: `roject PROJECT]
                         [--output OUTPUT] [--format {markdown,json}]
                         [--dry-run] [--no-mock]
code_generator.py: error: unrecognized arguments: --output-dir .
`

### `programming/security/env-secrets-manager` — FAIL
- scenario: /path/to/repo --json
- argv: `['/path/to/repo', '--json']`
- reason: rc=2
- stderr 尾: `{"error": "error: repo path is not a directory: \\path\\to\\repo"}
`

### `programming/testing/webapp-e2e-harness` — ERROR
- scenario: --url http://127.0.0.1:8000 --out e2e --write
- argv: `['--url', 'http://127.0.0.1:8000', '--out', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_out.json', '--write']`
- reason: 
- stderr 尾: `^^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 228, in makedirs
FileExistsError: [WinError 183] 当文件已存在时，无法创建该文件。: 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_out.json'
`

### `programming/workflow/agent-designer` — FAIL
- scenario: execution_logs.json --detailed -o eval
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_execution_logs.json', '--detailed', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stderr 尾: `No valid execution logs found in input file
`

### `programming/workflow/agent-designer` — FAIL
- scenario: requirements.json --format json -o arch
- argv: `['C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_requirements.json', '--format', 'json', '-o', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_o.json']`
- reason: rc=1
- stderr 尾: `ng 9 required positional arguments: 'goal', 'description', 'tasks', 'constraints', 'team_size', 'performance_requirements', 'safety_requirements', 'integration_requirements', and 'scale_requirements'
`

### `tools/bank-statement-reconcile` — FAIL
- scenario: --statement ./bank.csv --billing ./my_expenses.csv
- argv: `['--statement', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_bank.csv', '--billing', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_my_expenses.csv']`
- reason: rc=3
- stderr 尾: `[ERROR] cannot locate amount/date columns (amt_s=None, amt_b=None, date_s=None, date_b=None)
`

### `tools/batch-renamer` — FAIL
- scenario: apply $TARGET_DIR --pattern IMG_{n:03d}.{ext} --yes
- argv: `['apply', '$TARGET_DIR', '--pattern', 'IMG_{n:03d}.{ext}', '--yes']`
- reason: rc=1
- stderr 尾: `ERROR: 不是目录: $TARGET_DIR
`

### `tools/file-organizer` — FAIL
- scenario: apply $TARGET_DIR --by type --dry-run
- argv: `['apply', '$TARGET_DIR', '--by', 'type', '--dry-run']`
- reason: rc=1
- stderr 尾: `ERROR: 不是目录: $TARGET_DIR
`

### `tools/format-converter` — FAIL
- scenario: image photo.png photo.jpg --width 800 --quality
- argv: `['image', 'photo.png', 'photo.jpg', '--width', '800', '--quality', '85']`
- reason: rc=1
- stderr 尾: `ERROR: 输入文件不存在: photo.png
`

### `tools/invoice-organizer` — FAIL
- scenario: --src ./loose_invoices --dst ./organized
- argv: `['--src', './loose_invoices', '--dst', './organized']`
- reason: rc=2
- stderr 尾: `[ERROR] src not found: ./loose_invoices
`

### `video/storyboard-designer` — FAIL
- scenario: <storyboard 目录>
- argv: `['<storyboard', '目录>']`
- reason: rc=2
- stderr 尾: `usage: scene_lint.py [-h] directory
scene_lint.py: error: unrecognized arguments: 目录>
`

### `video/video-editor` — FAIL
- scenario: --clips clip1.mp4 clip2.mp4 --audio bgm.mp3 --output
- argv: `['--clips', 'clip1.mp4', 'clip2.mp4', '--audio', 'bgm.mp3', '--output', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_out_output.json', '--transitions', 'fade', 'cut']`
- reason: rc=2
- stderr 尾: `工具 ffmpeg，但 PATH 中未找到。
安装指引:
  Debian/Ubuntu : sudo apt update && sudo apt install -y ffmpeg
  macOS         : brew install ffmpeg
  校验          : ffmpeg -version
若只需联调下游流程，可加 --mock（产物为占位，不会真实生成文件）。
`

### `video/video-thumbnail` — FAIL
- scenario: --title 宝宝测评iPhone 16 --style funny
- argv: `['--title', '宝宝测评iPhone 16', '--style', 'funny']`
- reason: rc=4
- stderr 尾: `服务已启动: curl -sS -m 5 -o /dev/null -w '%{http_code}\n' http://127.0.0.1:30080/
  2) 确认地址正确  : export GATEWAY_BASE_URL=http://<host>:<port>  (不带尾斜杠)
  3) 若只需联调下游: 加 --mock 或 SKILLKIT_MOCK=1（产物为占位，不可交付）
`

### `writing/ai-trace-auditor` — FAIL
- scenario: 文本文件路径
- argv: `['文本文件路径']`
- reason: rc=1
- stderr 尾: `error: cannot read 文本文件路径: [Errno 2] No such file or directory: '文本文件路径'
`

### `writing/blog/cnblogs-skill` — FAIL
- scenario: <markdown_file> --title 文章标题
- argv: `['<markdown_file>', '--title', '文章标题']`
- reason: rc=1
- stdout 尾: `错误: 文件不存在 - <markdown_file>
`

### `writing/blog/csdn-publisher` — FAIL
- scenario: --version && test -f scripts/csdn_publisher.py &&
- argv: `['--version', '&&', 'test', '-f', 'scripts/csdn_publisher.py', '&&', 'echo', 'OK']`
- reason: rc=2
- stderr 尾: `        {categories,draft-save,publish,edit,delete,list} ...
csdn_publisher.py: error: argument cmd: invalid choice: '&&' (choose from 'categories', 'draft-save', 'publish', 'edit', 'delete', 'list')
`

### `writing/blog/jianshu-publisher` — FAIL
- scenario: --version && test -f scripts/jianshu_publisher.py &&
- argv: `['--version', '&&', 'test', '-f', 'scripts/jianshu_publisher.py', '&&', 'echo', 'OK']`
- reason: rc=2
- stderr 尾: `e COOKIE_FILE]
                            {draft-save,publish,edit,delete} ...
jianshu_publisher.py: error: argument cmd: invalid choice: '&&' (choose from 'draft-save', 'publish', 'edit', 'delete')
`

### `writing/blog/static-blog-deploy` — FAIL
- scenario: --version && test -f scripts/static_blog_deploy.py &&
- argv: `['--version', '&&', 'test', '-f', 'scripts/static_blog_deploy.py', '&&', 'echo', 'OK']`
- reason: rc=2
- stderr 尾: `ploy,netlify-deploy} ...
static_blog_deploy.py: error: argument cmd: invalid choice: '&&' (choose from 'hexo-deploy', 'hugo-deploy', 'github-pages', 'gitlab-pages', 'vercel-deploy', 'netlify-deploy')
`

### `writing/juejin/juejin-publisher` — FAIL
- scenario: --execute categories | head -5
- argv: `['--execute', 'categories', '|', 'head', '-5']`
- reason: rc=2
- stderr 尾: `n_publish.py [-h] [--cookie COOKIE] [--cookie-file COOKIE_FILE]
                         {categories,tags,draft-save,publish} ...
juejin_publish.py: error: unrecognized arguments: --execute | head -5
`

### `writing/orchestrator/cross-post-orchestrator` — ERROR
- scenario: --manifest post.manifest.json run --only juejin
- argv: `['--manifest', 'C:\\Users\\X1882\\AppData\\Local\\Temp\\skillkit_scenario_ezbzeej1\\in_post.manifest.json', 'run', '--only', 'juejin']`
- reason: 
- stderr 尾: `ome-skillkit\skills\writing\orchestrator\cross-post-orchestrator\scripts\cross_post.py", line 66, in load_manifest
    raise ValueError("manifest 缺少必填字段: %s" % key)
ValueError: manifest 缺少必填字段: title
`

### `writing/video/bilibili-publisher` — FAIL
- scenario: article-save --execute --title ... --content ...
- argv: `['article-save', '--execute', '--title', '...', '--content', '...']`
- reason: rc=1
- stderr 尾: `缺少认证：设置环境变量 BILI_COOKIE 或提供凭据文件
`

### `writing/wechat/wechat-mp-publisher` — FAIL
- scenario: --execute add-thumb cover.jpg
- argv: `['--execute', 'add-thumb', 'cover.jpg']`
- reason: rc=2
- stderr 尾: `chat_mp_publish.py [-h] [--appid APPID] [--secret SECRET]
                            {token,upload-img,add-thumb,add-draft,publish} ...
wechat_mp_publish.py: error: unrecognized arguments: --execute
`

### `writing/zhihu/zhihu-content-manager` — FAIL
- scenario: --help > /dev/null && echo lint-ok
- argv: `['>', '/dev/null', '&&', 'echo', 'lint-ok']`
- reason: rc=2
- stderr 尾: `usage: zhihu_html_lint.py [-h] [--json] [--strict] html_file
zhihu_html_lint.py: error: unrecognized arguments: /dev/null && echo lint-ok
`

## no-example（文档债：SKILL.md 无可解析用法示例）

- `meta/skill-finder` skills\meta\skill-finder\scripts\find_skill.py
- `programming/ai-engineering/skill-tester` skills\programming\ai-engineering\skill-tester\scripts\audit_skills.py
- `programming/incident/slo-architect` skills\programming\incident\slo-architect\scripts\slo_designer.py
- `programming/math/model-formulator` skills\programming\math\model-formulator\scripts\model_formulator.py
- `programming/planning/code-generator` skills\programming\planning\code-generator\scripts\project_analyzer.py
- `programming/planning/code-intent-planner` skills\programming\planning\code-intent-planner\scripts\l1_matcher.py
- `programming/planning/code-intent-planner` skills\programming\planning\code-intent-planner\scripts\llm_client.py
- `programming/planning/code-intent-planner` skills\programming\planning\code-intent-planner\scripts\normalizer.py
- `programming/planning/code-intent-planner` skills\programming\planning\code-intent-planner\scripts\plan_renderer.py
- `programming/planning/code-intent-planner` skills\programming\planning\code-intent-planner\scripts\session_manager.py
- `programming/security/pii-redactor` skills\programming\security\pii-redactor\scripts\pii_scan.py
- `programming/security/prompt-injection-guard` skills\programming\security\prompt-injection-guard\scripts\injection_scan.py
- `programming/security/secrets-vault-manager` skills\programming\security\secrets-vault-manager\scripts\audit_log_analyzer.py
- `programming/security/secrets-vault-manager` skills\programming\security\secrets-vault-manager\scripts\rotation_planner.py
- `programming/security/secrets-vault-manager` skills\programming\security\secrets-vault-manager\scripts\vault_config_generator.py
- `programming/testing/webapp-flow-tester` skills\programming\testing\webapp-flow-tester\scripts\with_server.py
- `video/video-prompt-engineer` skills\video\video-prompt-engineer\scripts\prompt_audit.py
- `writing/community/douban-publisher` skills\writing\community\douban-publisher\scripts\douban_publisher.py
- `writing/community/oschina-publisher` skills\writing\community\oschina-publisher\scripts\oschina_publisher.py
- `writing/community/segmentfault-publisher` skills\writing\community\segmentfault-publisher\scripts\segmentfault_publisher.py
- `writing/community/v2ex-publisher` skills\writing\community\v2ex-publisher\scripts\v2ex_publisher.py
- `writing/news/baijiahao-publisher` skills\writing\news\baijiahao-publisher\scripts\baijiahao_publisher.py
- `writing/news/toutiao-publisher` skills\writing\news\toutiao-publisher\scripts\toutiao_publisher.py
- `writing/social/weibo-publisher` skills\writing\social\weibo-publisher\scripts\weibo_publisher.py
- `writing/social/xiaohongshu-publisher` skills\writing\social\xiaohongshu-publisher\scripts\xiaohongshu_publisher.py

## 逐技能结果

| 技能 | 判定 | 秒 | 产物/原因 |
|---|---|---|---|
| `audio/podcast-producer` | fail | 0.11 | rc=1 |
| `chat/chat-prompt-engineer` | fail | 0.11 | rc=1 |
| `dataviz/dashboard-designer` | fail | 0.13 | rc=1 |
| `design/frontend-component-lab` | pass | 0.11 |  |
| `design/layout-spec-auditor` | fail | 0.11 | rc=1 |
| `education/exercise-generator` | fail | 0.1 | rc=2 |
| `integrations/cloud-drive-manager` | pass | 0.11 |  |
| `integrations/feishu-dingtalk-bridge` | fail | 0.12 | rc=2 |
| `integrations/issue-tracker-sync` | fail | 0.11 | rc=2 |
| `integrations/notion-workspace` | fail | 0.1 | rc=2 |
| `knowledge/knowledge-graph-builder` | fail | 0.11 | rc=1 |
| `knowledge/personal-wiki` | fail | 0.12 | rc=2 |
| `marketing/channel-adapter` | fail | 0.11 | rc=1 |
| `meta/agent-eval-harness` | error | 0.13 |  |
| `meta/session-handoff` | pass | 0.1 |  |
| `meta/skill-finder` | no-example |  | SKILL.md 无可解析用法示例 |
| `meta/skill-linter` | fail | 0.11 | rc=2 |
| `meta/weekly-report-generator` | fail | 0.11 | rc=2 |
| `office/career-ops-lite` | pass | 0.1 |  |
| `office/docx-template-fill` | fail | 0.11 | rc=2 |
| `office/docx-writer` | pass | 0.23 |  |
| `office/epub-builder` | fail | 0.13 | rc=2 |
| `office/pdf-pipeline` | fail | 0.29 | rc=1 |
| `paper/ai-humanizer` | pass | 0.12 |  |
| `paper/anti-defensive` | pass | 0.1 |  |
| `paper/arch-diagram` | pass | 0.1 |  |
| `paper/experiment-runner` | pass | 1.95 |  |
| `paper/figure-maker` | pass | 0.86 | ov_fm.pdf:10427B |
| `paper/journal-adapt` | pass | 0.11 |  |
| `paper/latex-formatter` | pass | 0.14 |  |
| `paper/lit-review` | pass | 0.14 |  |
| `paper/neural-net-draw` | pass | 0.11 |  |
| `paper/paper-topic-selector` | pass | 0.11 |  |
| `paper/pub-plotter` | pass | 0.89 | ov_pub.pdf:11679B |
| `paper/self-reviewer` | pass | 0.11 |  |
| `paper/tex-cleaner` | pass | 0.12 |  |
| `ppt/ppt-builder` | pass | 0.3 |  |
| `programming/ai-engineering/feature-flags-architect` | pass | 0.11 |  |
| `programming/ai-engineering/feature-flags-architect` | pass | 0.1 |  |
| `programming/ai-engineering/feature-flags-architect` | pass | 0.12 |  |
| `programming/ai-engineering/mcp-server-builder` | fail | 0.12 | rc=2 |
| `programming/ai-engineering/mcp-server-builder` | fail | 0.12 | rc=2 |
| `programming/ai-engineering/skill-tester/assets/sample-skill` | fail | 0.11 | rc=2 |
| `programming/ai-engineering/skill-tester` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/ai-engineering/skill-tester` | fail | 0.12 | rc=1 |
| `programming/ai-engineering/skill-tester` | fail | 0.11 | rc=1 |
| `programming/ai-engineering/skill-tester` | fail | 0.11 | rc=1 |
| `programming/ai-engineering/skill-tester` | fail | 0.11 | rc=1 |
| `programming/api/api-design-reviewer` | fail | 0.13 | rc=1 |
| `programming/api/api-design-reviewer` | fail | 0.13 | rc=1 |
| `programming/api/api-design-reviewer` | pass | 0.13 |  |
| `programming/architecture/migration-architect` | fail | 0.13 | rc=1 |
| `programming/architecture/migration-architect` | fail | 0.12 | rc=1 |
| `programming/architecture/migration-architect` | fail | 0.14 | rc=1 |
| `programming/architecture/monorepo-navigator` | fail | 0.1 | rc=1 |
| `programming/architecture/senior-architect` | fail | 0.11 | rc=1 |
| `programming/architecture/senior-architect` | fail | 0.11 | rc=2 |
| `programming/architecture/senior-architect` | fail | 0.12 | rc=1 |
| `programming/cicd/ci-cd-pipeline-builder` | pass | 0.13 |  |
| `programming/cicd/ci-cd-pipeline-builder` | pass | 0.12 |  |
| `programming/cicd/ship-gate` | fail | 0.13 | rc=1 |
| `programming/cicd/spec-driven-workflow` | pass | 0.11 |  |
| `programming/code-quality/code-reviewer` | pass | 0.12 |  |
| `programming/code-quality/code-reviewer` | fail | 0.11 | rc=1 |
| `programming/code-quality/code-reviewer` | pass | 0.39 |  |
| `programming/code-quality/dependency-auditor` | fail | 0.13 | rc=1 |
| `programming/code-quality/dependency-auditor` | pass | 0.12 |  |
| `programming/code-quality/dependency-auditor` | fail | 0.14 | rc=1 |
| `programming/code-quality/tdd-guide` | fail | 0.14 | rc=2 |
| `programming/code-quality/tech-debt-tracker` | fail | 0.14 | rc=1 |
| `programming/code-quality/tech-debt-tracker` | fail | 0.12 | rc=1 |
| `programming/code-quality/tech-debt-tracker` | fail | 0.12 | rc=1 |
| `programming/containers/docker-development` | fail | 0.11 | rc=2 |
| `programming/containers/docker-development` | fail | 0.1 | rc=2 |
| `programming/containers/helm-chart-builder` | fail | 0.1 | rc=2 |
| `programming/containers/helm-chart-builder` | fail | 0.11 | rc=2 |
| `programming/data/etl-builder` | pass | 0.11 |  |
| `programming/data/feature-engineer` | pass | 0.11 |  |
| `programming/database/database-designer` | pass | 0.13 |  |
| `programming/database/database-designer` | pass | 0.13 |  |
| `programming/database/database-designer` | fail | 0.12 | rc=1 |
| `programming/database/sql-database-assistant` | pass | 0.12 |  |
| `programming/database/sql-database-assistant` | pass | 0.12 |  |
| `programming/database/sql-database-assistant` | fail | 0.12 | rc=2 |
| `programming/debug/debug-diagnoser` | pass | 0.11 |  |
| `programming/github/changelog-generator` | pass | 0.14 |  |
| `programming/github/changelog-generator` | fail | 0.13 | rc=2 |
| `programming/github/changelog-generator` | fail | 0.12 | rc=1 |
| `programming/github/git-worktree-manager` | pass | 0.27 |  |
| `programming/github/git-worktree-manager` | fail | 0.12 | rc=2 |
| `programming/incident/incident-commander` | fail | 0.12 | rc=2 |
| `programming/incident/incident-commander` | fail | 0.12 | rc=1 |
| `programming/incident/incident-commander` | pass | 0.12 |  |
| `programming/incident/runbook-generator` | pass | 0.1 |  |
| `programming/incident/slo-architect` | pass | 0.11 |  |
| `programming/incident/slo-architect` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/incident/slo-architect` | fail | 0.1 | rc=2 |
| `programming/infrastructure/kubernetes-operator` | fail | 0.11 | rc=2 |
| `programming/infrastructure/kubernetes-operator` | pass | 0.11 |  |
| `programming/infrastructure/kubernetes-operator` | fail | 0.11 | rc=2 |
| `programming/infrastructure/observability-designer` | pass | 0.12 |  |
| `programming/infrastructure/observability-designer` | pass | 0.12 |  |
| `programming/infrastructure/terraform-patterns` | fail | 0.11 | rc=2 |
| `programming/infrastructure/terraform-patterns` | fail | 0.11 | rc=2 |
| `programming/math/model-formulator` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/math/model-solver` | pass | 0.75 |  |
| `programming/math/result-visualizer` | pass | 0.67 |  |
| `programming/math/simulation-runner` | pass | 0.12 | ov_sim.json:203B |
| `programming/ml/ml-pipeline` | pass | 2.88 |  |
| `programming/performance/performance-profiler` | fail | 0.11 | rc=1 |
| `programming/planning/code-generator` | fail | 0.12 | rc=2 |
| `programming/planning/code-generator` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/planning/code-intent-planner` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/planning/code-intent-planner` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/planning/code-intent-planner` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/planning/code-intent-planner` | pass | 0.13 |  |
| `programming/planning/code-intent-planner` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/planning/code-intent-planner` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/planning/deep-research` | pass | 0.12 |  |
| `programming/planning/web-search` | pass | 15.35 |  |
| `programming/security/env-secrets-manager` | fail | 0.12 | rc=2 |
| `programming/security/pii-redactor` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/security/prompt-injection-guard` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/security/secrets-vault-manager` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/security/secrets-vault-manager` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/security/secrets-vault-manager` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/testing/webapp-e2e-harness` | error | 0.11 |  |
| `programming/testing/webapp-flow-tester` | no-example |  | SKILL.md 无可解析用法示例 |
| `programming/workflow/agent-designer` | fail | 0.14 | rc=1 |
| `programming/workflow/agent-designer` | fail | 0.12 | rc=1 |
| `programming/workflow/agent-designer` | pass | 0.12 |  |
| `programming/workflow/agent-designer` | pass | 0.11 |  |
| `tools/bank-statement-reconcile` | fail | 0.11 | rc=3 |
| `tools/batch-renamer` | fail | 0.12 | rc=1 |
| `tools/file-organizer` | fail | 0.12 | rc=1 |
| `tools/format-converter` | fail | 0.13 | rc=1 |
| `tools/invoice-organizer` | fail | 0.1 | rc=2 |
| `tools/task-scheduler` | pass | 0.11 |  |
| `video/storyboard-designer` | fail | 0.11 | rc=2 |
| `video/video-editor` | fail | 0.12 | rc=2 |
| `video/video-lip-sync` | pass | 0.14 |  |
| `video/video-prompt-engineer` | no-example |  | SKILL.md 无可解析用法示例 |
| `video/video-script-writer` | pass | 3.22 | ov_script.json:1735B |
| `video/video-subtitles` | pass | 0.11 |  |
| `video/video-thumbnail` | fail | 2.2 | rc=4 |
| `video/video-voice-synth` | pass | 0.14 |  |
| `writing/ai-trace-auditor` | fail | 0.09 | rc=1 |
| `writing/article-drafter` | pass | 0.11 |  |
| `writing/article-outliner` | pass | 0.11 |  |
| `writing/assets/ai-cover-generator` | pass | 0.14 |  |
| `writing/blog/cnblogs-skill` | fail | 0.11 | rc=1 |
| `writing/blog/csdn-publisher` | fail | 0.14 | rc=2 |
| `writing/blog/jianshu-publisher` | fail | 0.13 | rc=2 |
| `writing/blog/static-blog-deploy` | fail | 0.14 | rc=2 |
| `writing/community/douban-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/community/oschina-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/community/segmentfault-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/community/v2ex-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/content-editor` | pass | 0.11 |  |
| `writing/juejin/juejin-publisher` | fail | 0.14 | rc=2 |
| `writing/news/baijiahao-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/news/toutiao-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/orchestrator/cross-post-orchestrator` | error | 0.15 |  |
| `writing/seo-optimizer` | pass | 0.12 | ov_seo.json:778B |
| `writing/social/weibo-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/social/xiaohongshu-publisher` | no-example |  | SKILL.md 无可解析用法示例 |
| `writing/video/bilibili-publisher` | fail | 0.14 | rc=1 |
| `writing/wechat/wechat-mp-publisher` | fail | 0.13 | rc=2 |
| `writing/zhihu/zhihu-content-manager` | fail | 0.1 | rc=2 |