---
name: performance-profiler
description: "Systematic performance profiling for Node.js, Python, and Go apps: locate CPU/memory/I/O bottlenecks, generate flame graphs, analyze bundle size, optimize database queries, and run load tests with k6 and Artillery. Always measure before changing. Use when troubleshooting a slow endpoint, planning a performance budget, tracking a memory leak, profiling performance, finding a bottleneck, or optimizing slow code. Do NOT use when the ask is to patch business logic or refactor the hot path directly (this skill only diagnoses and recommends)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: performance
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Performance Profiler

Systematic performance profiling: locate bottlenecks, quantify before/after differences, and give optimization direction.

## Core Capabilities

- **CPU profiling** — Node.js flame graphs, Python py-spy, Go pprof
- **Memory profiling** — heap snapshots, leak detection, GC pressure
- **Bundle-size analysis** — webpack-bundle-analyzer, Next.js bundle analyzer
- **Database optimization** — EXPLAIN ANALYZE, slow-query logs, N+1 detection
- **Load testing** — k6 scripts, Artillery scenarios, ramped load
- **Before/after comparison** — establish a baseline first, then profile, optimize, and re-measure to verify

## Input Checklist

| Input | Required | Description | Default |
|------|------|------|------|
| project_path | Yes | Path to the root of the project to profile | — |
| format | No | `text` / `json` (use `--json`) | text |
| large_file_threshold_kb | No | Threshold (KB) for large-file warnings | script default |

When missing, ask for all at once: "Please provide: (1) project_path (the project root). I'll run the output format and threshold on defaults."

## Pre-flight Checks

```bash
python3 --version
test -f scripts/performance_profiler.py && echo "OK script present"
```

- Expected: a version number; if the script exists it prints `OK script present`.
- On failure: the script is missing → STOP and report; for non-Python projects also install the corresponding runtime (node/py-spy/go) and k6/artillery as needed.

## Workflow

### Step 1: Scan risk metrics (baseline)

```bash
python3 scripts/performance_profiler.py examples/sample-codebase   # bundled sample codebase; swap in the project root for your real project
python3 scripts/performance_profiler.py examples/sample-codebase --json
python3 scripts/performance_profiler.py examples/sample-codebase --large-file-threshold-kb 256
```

- Action: Scan the project and output performance risk metrics (large files, suspicious patterns, etc.).
- Expected: the terminal prints a risk list; with `--json` it outputs structured JSON; `--large-file-threshold-kb` overrides the threshold.
- On failure: `No such file or directory` → wrong project_path; an unexpected exit → drop `--json` to see the text error.

### Step 2: Establish a before/after measurement baseline

- Action: Before any optimization, record P50/P95/P99 latency, RPS, error rate, and memory footprint.
- Expected: A comparable numeric baseline.
- On failure: No monitoring data → first use step 1's scan plus a runtime profiler to get numbers; optimizing by gut feel is forbidden.

### Step 3: Profile and optimize by language

- Action: Pull the corresponding command from references/profiling-recipes.md to generate flame graphs/heap snapshots; optimize per the checklist in references/optimization-playbook.md.
- Expected: Pinpoint specific hotspots (function/query/dependency).
- On failure: No hotspot → go back to the baseline to confirm whether the bottleneck hypothesis holds.

### Step 4: Re-measure to verify

- Action: After optimizing, repeat steps 1–2 and compare against the baseline to confirm improvement.
- Expected: Key metrics improve versus the baseline (lower latency) or reduced resource usage.
- On failure: No improvement, or even a regression → roll back the change, reread the recipes, and pick another path.

## Quick Optimization Checklist

- Database: index high-frequency query columns; connection pools (pgBouncer/HikariCP); result caching (Redis); merge N+1 into batch queries.
- Application: make sync I/O async; paginate large result sets; stream large files; cache expensive computations (LRU/Redis).
- Frontend: code-split large bundles (dynamic import); lazy-load below-the-fold images; gzip/brotli compression; serve static assets from a CDN.

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `No such file or directory` | Wrong project_path | Check the path and rerun |
| Unexpected non-zero exit | The project contains an unsupported structure | Drop `--json` to see the text error |
| Metrics don't improve after optimization | Wrong hotspot judgment | Roll back; reread profiling-recipes.md |
| Missing runtime tools | node/py-spy/go not installed | Install the corresponding profiling tool and re-measure |

## Delivery Criteria

- Definition of success: produce baseline numbers + hotspot location + an after-optimization re-measure comparison (at least latency or resources improved).
- Artifact naming: `profile-<date>.json` (with --json) or terminal report text.
- Save location: project root or the directory the user specifies.
- Completeness verification: both before/after `--json` outputs parse, and the key metric fields exist and are comparable.

## References

- references/profiling-recipes.md — read for Node/Python/Go profiling commands, flame graphs, heap snapshots
- references/optimization-playbook.md — read for before/after measurement templates, DB/Node/bundle/API optimization checklists, and common pitfalls
