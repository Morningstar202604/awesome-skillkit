---
name: performance-profiler
description: "Systematic performance profiling for Node.js, Python, and Go applications. Identifies CPU, memory, and I/O bottlenecks, generates flamegraphs, analyzes bundle sizes, optimizes database queries, runs load tests with k6 and Artillery. Always measures before and after. Use when investigating a slow endpoint, planning a performance budget, or hunting a memory leak in production. 当用户要求 性能分析 / 找瓶颈 / 优化慢代码 时使用。 Do NOT use for changing application code to fix hotspots (profiling only)."
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

**Tier:** POWERFUL  
**Category:** Engineering  
**Domain:** Performance Engineering  

---

## Overview

Systematic performance profiling for Node.js, Python, and Go applications. Identifies CPU, memory, and I/O bottlenecks; generates flamegraphs; analyzes bundle sizes; optimizes database queries; detects memory leaks; and runs load tests with k6 and Artillery. Always measures before and after.

## Core Capabilities

- **CPU profiling** — flamegraphs for Node.js, py-spy for Python, pprof for Go
- **Memory profiling** — heap snapshots, leak detection, GC pressure
- **Bundle analysis** — webpack-bundle-analyzer, Next.js bundle analyzer
- **Database optimization** — EXPLAIN ANALYZE, slow query log, N+1 detection
- **Load testing** — k6 scripts, Artillery scenarios, ramp-up patterns
- **Before/after measurement** — establish baseline, profile, optimize, verify

---

## When to Use

- App is slow and you don't know where the bottleneck is
- P99 latency exceeds SLA before a release
- Memory usage grows over time (suspected leak)
- Bundle size increased after adding dependencies
- Preparing for a traffic spike (load test before launch)
- Database queries taking >100ms

---

## Quick Start

```bash
# Analyze a project for performance risk indicators
python3 scripts/performance_profiler.py /path/to/project

# JSON output for CI integration
python3 scripts/performance_profiler.py /path/to/project --json

# Custom large-file threshold
python3 scripts/performance_profiler.py /path/to/project --large-file-threshold-kb 256
```

---

## Golden Rule: Measure First

```bash
# Establish baseline BEFORE any optimization
# Record: P50, P95, P99 latency | RPS | error rate | memory usage

# Wrong: "I think the N+1 query is slow, let me fix it"
# Right: Profile → confirm bottleneck → fix → measure again → verify improvement
```

---

## Node.js Profiling
→ See references/profiling-recipes.md for details

## Quick Optimization Checklist

### Database
- [ ] Add indexes for frequently queried columns
- [ ] Use connection pooling (pgBouncer, HikariCP)
- [ ] Enable query result caching (Redis, application-level)
- [ ] Batch N+1 queries into single bulk query

### Application
- [ ] Replace synchronous I/O with async equivalents
- [ ] Add pagination for large result sets
- [ ] Use streaming for large file processing
- [ ] Cache expensive computations (LRU, Redis)

### Frontend
- [ ] Code-split large bundles (dynamic import)
- [ ] Lazy-load images below the fold
- [ ] Compress assets (gzip, brotli)
- [ ] Use CDN for static assets

---

## References

- [references/profiling-recipes.md](references/profiling-recipes.md) — Node.js/Python/Go profiling commands, flamegraph generation, heap snapshots
- [references/optimization-playbook.md](references/optimization-playbook.md) — before/after measurement template, quick-win optimization checklist (DB/Node/bundle/API), common pitfalls, best practices
