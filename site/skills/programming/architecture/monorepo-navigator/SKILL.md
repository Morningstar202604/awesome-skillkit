---
name: monorepo-navigator
description: "Navigate, manage, and optimize monorepos. Covers Turborepo, Nx, pnpm workspaces, and Lerna. Cross-package impact analysis, selective builds/tests on affected packages, remote caching, dependency graph visualization, and structured multi-repo to monorepo migrations. Use when setting up a new monorepo, sorting out a monorepo, navigating a large repo, understanding package dependencies, optimizing CI for a large workspace, debugging cross-package dependency issues, or planning a multi-repo consolidation. Do NOT use for building or publishing packages (navigation and impact analysis only)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: architecture
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Monorepo Navigator

Navigate, manage, and optimize monorepos (Turborepo, Nx, pnpm workspaces, Lerna): cross-package impact analysis, building/testing only affected packages, dependency-graph visualization, and multi-repo → monorepo migration planning.

## Input Checklist

| Input | Required | Description |
|---|---|---|
| Monorepo root | Yes | The workspace path to analyze, e.g. `.` or `/path/to/monorepo` |
| Task intent | Yes | One of: map structure / impact analysis / CI optimization / migration planning / release orchestration |
| Change scope | Required for impact analysis | Which baseline to compare against, e.g. `origin/main` |
| Output format | No | Analysis report is text by default; `--json` for machine consumption |

When inputs are missing, ask for all at once: "Please provide: (1) monorepo root; (2) what to do this time (mapping / impact analysis / CI optimization / migration / release); (3) for impact analysis, which branch or commit to compare against."

## Pre-flight Checks

Run line by line; on any failure → fix per the remediation and STOP:

```bash
# 1. The target directory exists
ls <monorepo root> > /dev/null && echo OK
# Expected: OK. On failure: confirm the path with the user, STOP.

# 2. Identify the workspace type (at least one signal should hit)
ls <monorepo root>/turbo.json <monorepo root>/nx.json <monorepo root>/pnpm-workspace.yaml <monorepo root>/lerna.json <monorepo root>/package.json 2>/dev/null
# Expected: at least one file listed. All empty → not a standard monorepo; confirm intent with the user, STOP.

# 3. The analysis script is available
ls scripts/monorepo_analyzer.py
# Expected: the filename (run inside the skill directory). On failure: cd to the skill directory; still missing → STOP and report.
```

## Workflow

### Step 1: Analyze the workspace

```bash
python3 scripts/monorepo_analyzer.py examples/sample-monorepo   # bundled sample monorepo (npm workspaces, three packages); swap in your repo root for a real project
python3 scripts/monorepo_analyzer.py examples/sample-monorepo --json
```

- **Action**: determine the monorepo type (Turborepo/Nx/pnpm/Lerna), workspace members, and internal dependency graph.
- **Expected**: output a package list and dependency relationships; with `--json`, include a structured package list.
- **On failure**: empty output / error → the directory has no recognizable workspace; confirm the root with the user, then STOP.

### Step 2: Answer the task intent (dispatch by intent)

- **Impact analysis**: based on the Step 1 dependency graph, answer "which apps break if shared package P changes?" — traverse reverse dependencies; on the command line, use `pnpm -r --filter ...[origin/main] exec test` or `npx turbo run build --filter=...[origin/main]` to run only affected packages.
- **CI optimization**: check whether CI scopes with `--filter`, whether remote cache is configured (`TURBO_TOKEN`/`TURBO_TEAM`), and whether turbo.json `inputs` excludes unrelated files from the cache key.
- **Dependency-graph visualization**: turn the Step 1 dependencies into a Mermaid `graph TD` diagram.
- **Migration planning**: produce a phased plan (using `git filter-repo --to-subdirectory-filter` to preserve history; hand-moving files is forbidden).
- **Expected**: each intent yields a conclusion with concrete commands, matching the detected tool (turbo commands for turbo projects, pnpm commands for pnpm projects).
- **On failure**: the detected tool doesn't match the user's expectation → trust the detection and explain the basis.

### Step 3: Give an action list

- **Action**: check the current state against the failure table, and turn the hit pitfalls into action items with fix commands; for release orchestration use Changesets (`pnpm changeset` + `pnpm changeset publish`, which auto-replaces `workspace:*`).
- **Expected**: each action-list item includes: which file to change, which command to run, and how to verify.
- **On failure**: a fix falls outside "navigation and analysis" (actually building/publishing) → declare it out of this skill's scope and hand it back to the user or another skill.

## Tooling Quick Reference

| Tool | Best for | Key features |
|---|---|---|
| **Turborepo** | JS/TS monorepos, simple pipeline config | First-class remote caching, minimal config |
| **Nx** | Large enterprises, plugin ecosystem | Project graph, code generation, affected commands |
| **pnpm workspaces** | workspace protocol, disk efficiency | `workspace:*` references local packages |
| **Lerna** | npm publishing, version management | Batch publishing, conventional commits |
| **Changesets** | Modern version management (better than Lerna) | Changelog generation, pre-release channels |

Most modern combo: **pnpm workspaces + Turborepo + Changesets**

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|---|---|---|
| Every PR does a full build | `turbo run build` without `--filter` | Always use `--filter=...[origin/main]` in CI |
| Publish fails: `workspace:*` left behind | Direct `npm publish` | Use `pnpm changeset publish`, which auto-replaces with real versions |
| Unrelated changes trigger a full rebuild | turbo.json `inputs` cache key is too broad | Exclude docs and config files from `inputs` |
| One package's change drags down all type-checking | Shared tsconfig isn't layered | Each package `extends` the root config and overrides `rootDir`/`outDir` |
| git history lost after migration | Hand-moving files during merge | Use `git filter-repo --to-subdirectory-filter` before merging |
| Remote cache doesn't work in CI | `TURBO_TOKEN`/`TURBO_TEAM` not configured | Set the env vars, then verify with `turbo run build --summarize` |
| The AI assistant edits files in the wrong package | CLAUDE.md is too generic | Each package's CLAUDE.md states "When working on X, only touch files in apps/X" |

## Best Practices

1. **The root CLAUDE.md defines the map** — record every package, its purpose, and dependency rules
2. **Each package's CLAUDE.md defines its rules** — what's allowed, what's forbidden, the test command
3. **Always scope commands with --filter** — running everything on every change defeats the purpose
4. **Remote cache isn't optional** — without it, monorepo CI is slower than multi-repo
5. **Use Changesets, not hand-managed versions** — never hand-edit package.json versions in a monorepo
6. **Shared config at the root, extended inside packages** — tsconfig.base.json, .eslintrc.base.js, jest.base.config.js
7. **Run impact analysis before merging a shared-package change** — run affected checks and report the blast radius
8. **Keep packages/types pure TypeScript** — no runtime code, no dependencies; builds and type-checks stay fast

## Delivery Criteria

- Definition of success: the Step 1 analysis report covers all workspace packages and internal dependencies; the Step 2/3 conclusions cite concrete package names and commands from the report.
- Artifact naming: archived analysis `monorepo-analysis.{txt,json}` (when using `--json`); migration plan `monorepo-migration-plan.md`; the Mermaid diagram is embedded in the report.
- Save location: delivered in-conversation by default; archived files go to a user-specified directory (don't write into the target monorepo unless the user asks).
- Completeness verification: every command in the report runs verbatim in the target repo's context; the impact list matches the dependency graph.

## References

- `references/monorepo-patterns.md` — common architectures and CI patterns; read when planning a migration or a CI-optimization proposal.
- `references/monorepo-tooling-reference.md` — detailed usage of Turborepo and other tools; read when you need tool detail beyond the quick reference.
