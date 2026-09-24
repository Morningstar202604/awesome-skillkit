---
name: docker-development
description: "Docker and container development agent skill and plugin for Dockerfile optimization, docker-compose orchestration, multi-stage builds, and container security hardening. Use when: the user wants to write a Dockerfile, containerize an app, optimize image size, optimize a Dockerfile, create or improve docker-compose configurations, implement multi-stage builds, audit container security, reduce image size, or follow container best practices. Covers build performance, layer caching, secret management, and production-ready container patterns. Do NOT use for running containers in a production cluster."
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

> Smaller images. Faster builds. Safer containers. No guesswork.

A Docker workflow with strong opinions, turning bloated Dockerfiles into production-grade containers. It covers optimization, multi-stage builds, compose orchestration, and security hardening.

This isn't a Docker tutorial — it's a set of concrete decisions about how to build containers that don't waste time, don't waste space, and don't enlarge the attack surface.

## Slash Commands

| Command | Effect |
|---------|-------------|
| `/docker:optimize` | Analyze and optimize a Dockerfile for size, speed, and layer caching |
| `/docker:compose` | Generate or improve docker-compose.yml per best practices |
| `/docker:security` | Audit a Dockerfile or running container for security issues |

## When to Activate

Recognize these phrasings from the user:

- "Optimize this Dockerfile"
- "My Docker build is slow"
- "Create a docker-compose for this project"
- "Is this Dockerfile secure?"
- "Reduce my Docker image size"
- "Set up multi-stage builds"
- "Docker best practices for [language/framework]"
- Any request involving Dockerfile, docker-compose, containers, image size, build cache, or Docker security

The user has a Dockerfile, or wants to containerize something → this skill applies.

## Input Checklist

| Input | Required | Description |
|-------|----------|-------------|
| Dockerfile path | Conditional | The target for `/docker:optimize` and `/docker:security` (defaults to `Dockerfile` in the cwd) |
| Service topology | Conditional | Each service and its role, used for `/docker:compose` |
| Base-image constraints | Optional | Registry, glibc/musl requirements, whether a shell for debugging is preferred |
| Exposed ports / volumes / env vars | Optional | What the app needs, used for compose generation |
| Dev or production intent | Optional | Decides bind mounts vs named volumes, debug ports, restart policy |

When inputs are missing, collect them all at once: "Please provide all at once: (1) the Dockerfile or a description of what to containerize, (2) which services you need (app/database/cache/queue/proxy), (3) ports, volumes, and required environment variables, (4) whether this is local development or a production-like environment. Everything else I decide per the checklist below."

## Pre-flight Checks

Probe first, then act; on any failure, give the fix and stop:

```bash
python3 --version   # expected 3.8+; on failure: install python3
# Self-check: python3 scripts/dockerfile_analyzer.py --help and compose_validator.py --help should both exit 0
test -f <Dockerfile-path>   # expected exit code 0 for optimize/security tasks; on failure: ask the user for the file
docker --version >/dev/null 2>&1   # expected exit code 0; on failure: docker not installed → skip build/verify steps and do static analysis only
```

## Workflow

### Step 1: Analyze the existing Dockerfile (`/docker:optimize`)

Read the Dockerfile; identify the base image and its size; count layers (each RUN/COPY/ADD = 1 layer); note anti-patterns. Then apply the optimization checklist:

```text
BASE IMAGE
├── Use specific tags; never use :latest in production
├── Prefer slim/alpine variants (debian-slim > ubuntu > debian)
├── In CI, pin by digest for reproducibility: image@sha256:...
└── The base image matches the runtime needs (don't use python:3.12 for a compiled binary)

LAYER OPTIMIZATION
├── Merge related RUN commands with && \
├── Order layers: least-changed first (deps before source)
├── Clean the package-manager cache in the same RUN layer
├── Use .dockerignore to exclude unrelated files
└── Separate build deps from runtime deps

BUILD CACHE
├── Copy dependency files before copying source (package.json, requirements.txt, go.mod)
├── Dependency install and code copy live in separate layers
├── Use BuildKit cache mounts: --mount=type=cache,target=/root/.cache
└── Avoid COPY . . before dependency install

MULTI-STAGE BUILDS
├── Stage 1: build (full SDK, build tools, dev deps)
├── Stage 2: runtime (minimal base image, only production artifacts)
├── COPY --from=builder takes only what's needed
└── The final image should have no build tools, no source, no dev deps
```

Expected: a rewritten Dockerfile with an inline comment per decision, plus an estimated size reduction.
On failure: the user's app needs special build tools → keep the build stage permissive; harden only the runtime stage.

### Step 2: Validate with the analyzer

```bash
python3 scripts/dockerfile_analyzer.py examples/Dockerfile              # bundled sample; swap in Dockerfile for your real project
python3 scripts/dockerfile_analyzer.py examples/Dockerfile --output json
python3 scripts/dockerfile_analyzer.py examples/Dockerfile --security   # focus on security
```

Expected: the analyzer reports layer count and base-image notes, with no lingering anti-pattern flags. Optional build verification when docker is available: `docker build -t <name> .` succeeds.
On failure: analyzer flags remain → apply fixes one by one and rerun until clean.

### Step 3: Generate or fix docker-compose.yml (`/docker:compose`)

Identify the services (app/web/worker, database, cache, queue, reverse proxy), then apply:

```text
SERVICES
├── Use depends_on with condition: service_healthy
├── Add a healthcheck to every service
├── Set resource limits (mem_limit, cpus)
├── Use named volumes for persistent data
└── Pin image versions

NETWORKING
├── Create networks explicitly (don't rely on the default network)
├── Separate frontend and backend networks
├── Expose only the ports that need external access
└── Use internal: true for pure backend networks

ENVIRONMENT
├── Use env_file for secrets, not inline environment
├── Never commit .env files (add to .gitignore)
├── Use variable substitution: ${VAR:-default}
└── Document every required environment variable

DEVELOPMENT vs PRODUCTION
├── Distinguish with compose profiles or override files
├── Dev: bind-mount hot reload, expose debug ports
├── Prod: named volumes, no debug ports, restart: unless-stopped
└── Dev-only config goes in docker-compose.override.yml
```

Deliverables: `docker-compose.yml`, a `.env.example` documenting all required variables, and dev/prod annotations.

### Step 4: Validate the compose file

```bash
python3 scripts/compose_validator.py examples/docker-compose.yml             # bundled sample; swap in docker-compose.yml for your real project
python3 scripts/compose_validator.py docker-compose.yml --output json
python3 scripts/compose_validator.py docker-compose.yml --strict    # fail on any warning
```

Expected: the validator confirms healthchecks, networks, and volumes are fine, no port conflicts, and (under `--strict`) zero warnings.
On failure: apply fixes one by one and rerun until `--strict` passes.

### Step 5: Security audit (`/docker:security`)

Dockerfile checks:

| Check | Severity | Fix |
|-------|----------|-----|
| Running as root | Critical | Add `USER nonroot` after creating a user |
| Using the :latest tag | High | Pin to a specific version |
| Secrets in ENV/ARG | Critical | Use BuildKit secrets instead: `--mount=type=secret` |
| COPY with a broad glob | Medium | Use specific paths, add .dockerignore |
| Redundant EXPOSE | Low | Expose only the ports the app actually uses |
| No HEALTHCHECK | Medium | Add a HEALTHCHECK with a reasonable interval |
| Privileged instructions | High | Avoid `--privileged`; drop capabilities |
| Residual package-manager cache | Low | Clean it in the same RUN layer |

Runtime checks (compose / running containers):

| Check | Severity | Fix |
|-------|----------|-----|
| Container running as root | Critical | Set a user in the Dockerfile or compose |
| Writable root filesystem | Medium | Use `read_only: true` in compose |
| All capabilities retained | High | Drop all, add only what's needed: `cap_drop: [ALL]` |
| No resource limits | Medium | Set `mem_limit` and `cpus` |
| host network mode | High | Use a bridge or custom network |
| Sensitive mounts | Critical | Never mount /etc or /var/run/docker.sock in production |
| No log driver configured | Low | Set `logging:` with a size cap |

Expected: a report in the format `SECURITY AUDIT — <Dockerfile/image>` with CRITICAL/HIGH/MEDIUM/LOW counts and per-item fixes; zero CRITICAL items before delivery.

### Step 6: Proactive callouts

Point these out even when nobody asks:

- **Dockerfile uses :latest** → recommend pinning to a specific version tag.
- **No .dockerignore** → create one. At minimum include: `.git`, `node_modules`, `__pycache__`, `.env`.
- **COPY . . before dependency install** → cache invalidation. Reorder to install deps first.
- **Running as root** → add a USER instruction. No exceptions in production.
- **Secrets in ENV or ARG** → use a BuildKit secret mount. Never bake secrets into layers.
- **Image over 1GB** → it must be multi-stage. A production image has no reason to be that big.
- **No healthcheck** → add one. Orchestrators (Compose, K8s) need it for lifecycle management.
- **apt-get not cleaned in the same layer** → add `rm -rf /var/lib/apt/lists/*` in the same RUN.

## Multi-Stage Build Patterns

### Pattern 1: Compiled languages (Go, Rust, C++)

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

## Base-Image Decision Tree

```text
Is it a compiled artifact (Go, Rust, C)?
├── Yes → distroless/static or scratch
└── No
    ├── Need a shell for debugging?
    │   ├── Yes → alpine variant (e.g. node:20-alpine)
    │   └── No → distroless variant
    ├── Need glibc (not musl)?
    │   ├── Yes → slim variant (e.g. python:3.12-slim)
    │   └── No → alpine variant
    └── Need specific OS packages?
        ├── Many → debian-slim
        └── Few → alpine + apk add
```

## Failure Handling Table

| Symptom / error | Cause | Fix |
|-----------------|-------|-----|
| Analyzer flags remain after rewrite | The fix is wrong, or a new anti-pattern was introduced | Rerun `dockerfile_analyzer.py --security`; handle one flag at a time |
| `docker build` fails after optimization | The build stage is missing a needed build dependency | Keep the SDK/tools in the build stage; only the runtime stage stays minimal |
| Compose validator: port conflict | Two services bound the same host port | Move backend services into an internal network; map unique host ports |
| Healthcheck never passes | Wrong endpoint or interval | Probe the app endpoint manually; adjust `interval`/`retries` |
| Image still over 1GB after multi-stage | A heavy component was copied into the runtime | Copy only the built binary/dist; verify with `docker history <image>` |
| App can't write files under `read_only: true` | No writable path provided | Add `tmpfs` or an `emptyDir`-style volume for /tmp and app-writable paths |

## Delivery Criteria

Definition of success: the optimized Dockerfile passes `dockerfile_analyzer.py` (no flags), `docker-compose.yml` passes `--strict` validation, and the security-audit report has zero CRITICAL findings.
Artifact naming: `Dockerfile`, `docker-compose.yml`, `docker-compose.override.yml` (dev only), `.env.example`, `.dockerignore`.
Save location: project root, alongside the source.
Completeness verification: both analyzer and validator pass (validator with `--strict`); every environment variable in the Dockerfile appears in `.env.example`; the security report enumerates every check and its pass/fix status.

## Safety Red Lines

- Secrets never go in the Dockerfile, ARG/ENV, image layers, or committed `.env` files — use a BuildKit secret mount, and exclude env files with `.gitignore`.
- Default posture: non-root user, read-only root filesystem, dropped capabilities, pinned tags.
- Production-cluster concerns (orchestration, live troubleshooting) are out of scope; chart concerns belong to helm-chart-builder.

## References

- `references/dockerfile-best-practices.md` — the full rule set behind the analyzer's flags, plus language-specific patterns
- `references/compose-patterns.md` — when composing multi-service topologies (networks, profiles, override files)

## Related Skills

- **senior-devops** — broader DevOps scope (CI/CD, IaC, monitoring). Complementary — use docker-development for container specifics, senior-devops for pipelines and infrastructure.
- **senior-security** — application security. Complementary — docker-development covers container security, senior-security covers app-layer threats.
- **autoresearch-agent** — can optimize Docker build time or image size as a measurable experiment.
- **ci-cd-pipeline-builder** — pipeline building. Complementary — docker-development builds containers, ci-cd-pipeline-builder deploys them.

Once images and compose are ready, **then say: "Containerization is done; next, call helm-chart-builder to generate the deployment chart" — the chain unfolds automatically**.
