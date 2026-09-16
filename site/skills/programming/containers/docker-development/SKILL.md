---
name: docker-development
description: "Docker and container development agent skill and plugin for Dockerfile optimization, docker-compose orchestration, multi-stage builds, and container security hardening. Use when: user wants to optimize a Dockerfile, create or improve docker-compose configurations, implement multi-stage builds, audit container security, reduce image size, or follow container best practices. Covers build performance, layer caching, secret management, and production-ready container patterns. 当用户要求 写 Dockerfile / 容器化应用 / 优化镜像体积 时使用。 Do NOT use for running containers in a production cluster."
license: Apache-2.0
compatibility: Requires docker. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: containers
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Docker Development

> Smaller images. Faster builds. Secure containers. No guesswork.

Opinionated Docker workflow that turns bloated Dockerfiles into production-grade containers. Covers optimization, multi-stage builds, compose orchestration, and security hardening.

Not a Docker tutorial — a set of concrete decisions about how to build containers that don't waste time, space, or attack surface.

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/docker:optimize` | Analyze and optimize a Dockerfile for size, speed, and layer caching |
| `/docker:compose` | Generate or improve docker-compose.yml with best practices |
| `/docker:security` | Audit a Dockerfile or running container for security issues |

## When This Skill Activates

Recognize these patterns from the user:

- "Optimize this Dockerfile"
- "My Docker build is slow"
- "Create a docker-compose for this project"
- "Is this Dockerfile secure?"
- "Reduce my Docker image size"
- "Set up multi-stage builds"
- "Docker best practices for [language/framework]"
- Any request involving: Dockerfile, docker-compose, container, image size, build cache, Docker security

If the user has a Dockerfile or wants to containerize something → this skill applies.

## 输入清单

| Input | Required | Description |
|-------|----------|-------------|
| Dockerfile path | Conditional | Target for `/docker:optimize` and `/docker:security` (default `Dockerfile` in cwd) |
| Service topology | Conditional | Services and their roles, for `/docker:compose` |
| Base image constraints | Optional | Registry, glibc/musl needs, shell-for-debugging preference |
| Exposed ports / volumes / env vars | Optional | Required by the app, for compose generation |
| Dev vs prod intent | Optional | Decides bind mounts vs named volumes, debug ports, restart policy |

Collect missing inputs in one shot: "Please provide: ① the Dockerfile or a description of what to containerize ② services needed (app/database/cache/queue/proxy) ③ ports, volumes, and required env vars ④ is this for local dev or production-like setup. Everything else I'll decide by the checklists below."

## 前置自检

Probe before running; on any failure, give the fix and STOP:

```bash
python3 --version   # expect 3.8+; fail: install python3
python3 scripts/dockerfile_analyzer.py --help >/dev/null 2>&1   # expect exit 0; fail: script missing → check skill dir
python3 scripts/compose_validator.py --help >/dev/null 2>&1
test -f <Dockerfile-path>   # expect exit 0 for optimize/security tasks; fail: ask user for the file
docker --version >/dev/null 2>&1   # expect exit 0; fail: docker not installed → skip build/verify steps, static analysis only
```

## 工作流

### 步骤 1: Analyze the current Dockerfile (`/docker:optimize`)

Read the Dockerfile; identify base image and its size; count layers (each RUN/COPY/ADD = 1 layer); note anti-patterns. Then apply the optimization checklist:

```text
BASE IMAGE
├── Use specific tags, never :latest in production
├── Prefer slim/alpine variants (debian-slim > ubuntu > debian)
├── Pin digest for reproducibility in CI: image@sha256:...
└── Match base to runtime needs (don't use python:3.12 for a compiled binary)

LAYER OPTIMIZATION
├── Combine related RUN commands with && \
├── Order layers: least-changing first (deps before source code)
├── Clean package manager cache in the same RUN layer
├── Use .dockerignore to exclude unnecessary files
└── Separate build deps from runtime deps

BUILD CACHE
├── COPY dependency files before source code (package.json, requirements.txt, go.mod)
├── Install deps in a separate layer from code copy
├── Use BuildKit cache mounts: --mount=type=cache,target=/root/.cache
└── Avoid COPY . . before dependency installation

MULTI-STAGE BUILDS
├── Stage 1: build (full SDK, build tools, dev deps)
├── Stage 2: runtime (minimal base, only production artifacts)
├── COPY --from=builder only what's needed
└── Final image should have NO build tools, NO source code, NO dev deps
```

Expected: a rewritten Dockerfile with inline comments per decision and an estimated size reduction.
If it fails: user's app needs exotic build tooling → keep the build stage permissive and harden only the runtime stage.

### 步骤 2: Validate with the analyzer

```bash
python3 scripts/dockerfile_analyzer.py Dockerfile              # text report
python3 scripts/dockerfile_analyzer.py Dockerfile --output json
python3 scripts/dockerfile_analyzer.py Dockerfile --security   # security-focused
```

Expected: analyzer reports layer count, base-image notes, and no remaining anti-pattern flags. Optional build check when docker is available: `docker build -t <name> .` succeeds.
If it fails: analyzer flags persist → apply the flagged fix and re-run until clean.

### 步骤 3: Generate or fix docker-compose.yml (`/docker:compose`)

Identify services (app/web/worker, database, cache, queue, reverse proxy), then apply:

```text
SERVICES
├── Use depends_on with condition: service_healthy
├── Add healthchecks for every service
├── Set resource limits (mem_limit, cpus)
├── Use named volumes for persistent data
└── Pin image versions

NETWORKING
├── Create explicit networks (don't rely on default)
├── Separate frontend and backend networks
├── Only expose ports that need external access
└── Use internal: true for backend-only networks

ENVIRONMENT
├── Use env_file for secrets, not inline environment
├── Never commit .env files (add to .gitignore)
├── Use variable substitution: ${VAR:-default}
└── Document all required env vars

DEVELOPMENT vs PRODUCTION
├── Use compose profiles or override files
├── Dev: bind mounts for hot reload, debug ports exposed
├── Prod: named volumes, no debug ports, restart: unless-stopped
└── docker-compose.override.yml for dev-only config
```

Deliverables: `docker-compose.yml`, `.env.example` with every required variable documented, dev/prod annotations.

### 步骤 4: Validate the compose file

```bash
python3 scripts/compose_validator.py docker-compose.yml             # text report
python3 scripts/compose_validator.py docker-compose.yml --output json
python3 scripts/compose_validator.py docker-compose.yml --strict    # fail on warnings
```

Expected: validator confirms healthchecks, networks, volumes, no port conflicts, and (with `--strict`) zero warnings.
If it fails: apply each flagged fix and re-run until `--strict` passes.

### 步骤 5: Security audit (`/docker:security`)

Dockerfile checks:

| Check | Severity | Fix |
|-------|----------|-----|
| Running as root | Critical | Add `USER nonroot` after creating user |
| Using :latest tag | High | Pin to specific version |
| Secrets in ENV/ARG | Critical | Use BuildKit secrets: `--mount=type=secret` |
| COPY with broad glob | Medium | Use specific paths, add .dockerignore |
| Unnecessary EXPOSE | Low | Only expose ports the app uses |
| No HEALTHCHECK | Medium | Add HEALTHCHECK with appropriate interval |
| Privileged instructions | High | Avoid `--privileged`, drop capabilities |
| Package manager cache retained | Low | Clean in same RUN layer |

Runtime checks (compose / running container):

| Check | Severity | Fix |
|-------|----------|-----|
| Container running as root | Critical | Set user in Dockerfile or compose |
| Writable root filesystem | Medium | Use `read_only: true` in compose |
| All capabilities retained | High | Drop all, add only needed: `cap_drop: [ALL]` |
| No resource limits | Medium | Set `mem_limit` and `cpus` |
| Host network mode | High | Use bridge or custom network |
| Sensitive mounts | Critical | Never mount /etc, /var/run/docker.sock in prod |
| No log driver configured | Low | Set `logging:` with size limits |

Expected: a report in the format `SECURITY AUDIT — <Dockerfile/image>` with CRITICAL/HIGH/MEDIUM/LOW counts and per-finding fixes; zero CRITICAL items before handover.

### 步骤 6: Proactive flags

Flag these without being asked:

- **Dockerfile uses :latest** → Suggest pinning to a specific version tag.
- **No .dockerignore** → Create one. At minimum: `.git`, `node_modules`, `__pycache__`, `.env`.
- **COPY . . before dependency install** → Cache bust. Reorder to install deps first.
- **Running as root** → Add USER instruction. No exceptions for production.
- **Secrets in ENV or ARG** → Use BuildKit secret mounts. Never bake secrets into layers.
- **Image over 1GB** → Multi-stage build required. No reason for a production image this large.
- **No healthcheck** → Add one. Orchestrators (Compose, K8s) need it for proper lifecycle management.
- **apt-get without cleanup in same layer** → `rm -rf /var/lib/apt/lists/*` in the same RUN.

## Multi-Stage Build Patterns

### Pattern 1: Compiled Language (Go, Rust, C++)

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/server

# Runtime stage
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

### Pattern 2: Node.js / TypeScript

```dockerfile
# Dependencies stage
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false

# Build stage
FROM deps AS builder
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-alpine
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Pattern 3: Python

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=builder /install /usr/local
COPY . .
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Base Image Decision Tree

```text
Is it a compiled binary (Go, Rust, C)?
├── Yes → distroless/static or scratch
└── No
    ├── Need a shell for debugging?
    │   ├── Yes → alpine variant (e.g., node:20-alpine)
    │   └── No → distroless variant
    ├── Need glibc (not musl)?
    │   ├── Yes → slim variant (e.g., python:3.12-slim)
    │   └── No → alpine variant
    └── Need specific OS packages?
        ├── Many → debian-slim
        └── Few → alpine + apk add
```

## 失败处置表

| Symptom / Error | Cause | Fix |
|-----------------|-------|-----|
| Analyzer flags persist after rewrite | Fix applied incorrectly or new anti-pattern introduced | Re-run `dockerfile_analyzer.py --security`; address one flag at a time |
| `docker build` fails after optimization | Missing build deps dropped from build stage | Keep SDK/tools in the build stage; only the runtime stage stays minimal |
| Compose validator: port conflict | Two services bind the same host port | Move backend services to internal networks; map unique host ports |
| Healthcheck never passes | Wrong endpoint or interval | Probe the app endpoint manually; adjust `interval`/`retries` |
| Image still over 1GB after multi-stage | Heavy artifacts copied into runtime | Copy only built binaries/dist; verify with `docker history <image>` |
| App can't write files with `read_only: true` | Writable paths not provisioned | Add `tmpfs` or `emptyDir`-style volumes for /tmp and app-writable paths |

## 交付标准

Success definition: optimized Dockerfile validated by `dockerfile_analyzer.py` (no flags), validated `docker-compose.yml` passing `--strict`, and a security audit report with zero CRITICAL findings.
Artifact naming: `Dockerfile`, `docker-compose.yml`, `docker-compose.override.yml` (dev-only), `.env.example`, `.dockerignore`.
Save location: project root next to the application source.
Verify completeness: analyzer and validator both pass (validator at `--strict`); every env var in the Dockerfile appears in `.env.example`; security report enumerates all checks with pass/fix status.

## 安全红线

- Secrets never go into Dockerfiles, ARG/ENV, image layers, or committed `.env` files — use BuildKit secret mounts and env files excluded via `.gitignore`.
- Default posture: non-root user, read-only root filesystem, dropped capabilities, pinned tags.
- Production cluster concerns (orchestration, live troubleshooting) are out of scope; charts live with helm-chart-builder.

## 参考

- `references/dockerfile-best-practices.md` — read for the full rule set behind the analyzer's flags and language-specific patterns
- `references/compose-patterns.md` — read when composing multi-service topologies (networks, profiles, override files)

## Related Skills

- **senior-devops** — Broader DevOps scope (CI/CD, IaC, monitoring). Complementary — use docker-development for container-specific work, senior-devops for pipeline and infrastructure.
- **senior-security** — Application security. Complementary — docker-development covers container security, senior-security covers application-level threats.
- **autoresearch-agent** — Can optimize Docker build times or image sizes as measurable experiments.
- **ci-cd-pipeline-builder** — Pipeline construction. Complementary — docker-development builds the containers, ci-cd-pipeline-builder deploys them.

镜像与 compose 就绪，**接着说："容器化完成，继续调用 helm-chart-builder 生成部署 chart"——链条自动展开**。
