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

> 更小的镜像。更快的构建。更安全的容器。不靠猜。

一套带明确主张的 Docker 工作流，把臃肿的 Dockerfile 变成生产级容器。覆盖优化、多阶段构建、compose 编排与安全加固。

这不是 Docker 教程——这是一组具体决策，关于如何构建不浪费时间、不占空间、不扩大攻击面的容器。

## 斜杠命令

| 命令 | 作用 |
|---------|-------------|
| `/docker:optimize` | 分析并优化 Dockerfile 的体积、速度与层缓存 |
| `/docker:compose` | 按最佳实践生成或改进 docker-compose.yml |
| `/docker:security` | 审计 Dockerfile 或运行中容器的安全问题 |

## 何时激活

识别用户的这些表达：

- "Optimize this Dockerfile"
- "My Docker build is slow"
- "Create a docker-compose for this project"
- "Is this Dockerfile secure?"
- "Reduce my Docker image size"
- "Set up multi-stage builds"
- "Docker best practices for [language/framework]"
- 任何涉及 Dockerfile、docker-compose、容器、镜像体积、构建缓存、Docker 安全的请求

用户有 Dockerfile，或想把某个东西容器化 → 本技能适用。

## 输入清单

| 输入 | 必需 | 说明 |
|-------|----------|-------------|
| Dockerfile 路径 | 视情况 | `/docker:optimize` 与 `/docker:security` 的目标（默认 cwd 下的 `Dockerfile`） |
| 服务拓扑 | 视情况 | 各服务及其角色，用于 `/docker:compose` |
| 基础镜像约束 | 可选 | Registry、glibc/musl 需求、是否偏好带 shell 便于调试 |
| 暴露端口 / 卷 / 环境变量 | 可选 | 应用所需，用于 compose 生成 |
| 开发还是生产意图 | 可选 | 决定 bind mounts vs named volumes、调试端口、重启策略 |

缺输入时一次性收集："请一次性提供：① Dockerfile 或要容器化内容的描述 ② 需要哪些服务（app/database/cache/queue/proxy）③ 端口、卷与必需的环境变量 ④ 这是本地开发还是类生产环境。其余我按下方清单决定。"

## 前置自检

先探测再动手；任一失败，给出修复方法并停止：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
# 自检：python3 scripts/dockerfile_analyzer.py --help 与 compose_validator.py --help 均预期退出码 0
test -f <Dockerfile-path>   # optimize/security 任务预期退出码 0；失败：向用户要文件
docker --version >/dev/null 2>&1   # 预期退出码 0；失败：docker 未安装 → 跳过构建/验证步骤，仅做静态分析
```

## 工作流

### 步骤 1：分析现有 Dockerfile（`/docker:optimize`）

读 Dockerfile；识别基础镜像及其体积；数层（每个 RUN/COPY/ADD = 1 层）；记下反模式。然后套用优化清单：

```text
BASE IMAGE
├── 用具体 tag，生产环境绝不用 :latest
├── 优先 slim/alpine 变体（debian-slim > ubuntu > debian）
├── CI 里用 digest 锁定保证可复现：image@sha256:...
└── 基础镜像匹配运行时需求（编译好的二进制别用 python:3.12）

LAYER OPTIMIZATION
├── 相关 RUN 命令用 && \ 合并
├── 层排序：变化最少的在前（依赖先于源码）
├── 包管理器缓存在同一 RUN 层内清理
├── 用 .dockerignore 排除无关文件
└── 构建依赖与运行时依赖分离

BUILD CACHE
├── 先 COPY 依赖文件再 COPY 源码（package.json、requirements.txt、go.mod）
├── 依赖安装与代码拷贝分属不同层
├── 用 BuildKit cache mount：--mount=type=cache,target=/root/.cache
└── 依赖安装之前避免 COPY . .

MULTI-STAGE BUILDS
├── 阶段 1：build（完整 SDK、构建工具、开发依赖）
├── 阶段 2：runtime（最小基础镜像，只要生产产物）
├── COPY --from=builder 只拿需要的
└── 最终镜像应无构建工具、无源码、无开发依赖
```

预期：重写后的 Dockerfile，每个决策带行内注释，附预估体积降幅。
失败时：用户应用需要特殊构建工具 → 构建阶段保持宽松，只加固 runtime 阶段。

### 步骤 2：用分析器校验

```bash
python3 scripts/dockerfile_analyzer.py examples/Dockerfile              # 随包样例；你的真实项目换成 Dockerfile
python3 scripts/dockerfile_analyzer.py examples/Dockerfile --output json
python3 scripts/dockerfile_analyzer.py examples/Dockerfile --security   # 聚焦安全
```

预期：分析器报告层数、基础镜像备注，且无残留反模式标记。docker 可用时的可选构建验证：`docker build -t <name> .` 成功。
失败时：分析器标记仍在 → 逐项应用修复并重跑，直到干净。

### 步骤 3：生成或修复 docker-compose.yml（`/docker:compose`）

识别服务（app/web/worker、数据库、缓存、队列、反向代理），然后套用：

```text
SERVICES
├── 用 depends_on 配 condition: service_healthy
├── 每个服务都加 healthcheck
├── 设资源限额（mem_limit、cpus）
├── 持久数据用 named volumes
└── 锁定 image 版本

NETWORKING
├── 显式建网络（不依赖默认网络）
├── 前端与后端网络分离
├── 只暴露需要外部访问的端口
└── 纯后端网络用 internal: true

ENVIRONMENT
├── 密钥用 env_file，不写内联 environment
├── 绝不提交 .env 文件（加进 .gitignore）
├── 用变量替换：${VAR:-default}
└── 所有必需环境变量都写文档

DEVELOPMENT vs PRODUCTION
├── 用 compose profiles 或 override 文件区分
├── Dev：bind mount 热重载，暴露调试端口
├── Prod：named volumes、无调试端口、restart: unless-stopped
└── 开发专属配置放 docker-compose.override.yml
```

交付物：`docker-compose.yml`、记录全部必需变量的 `.env.example`、dev/prod 标注。

### 步骤 4：校验 compose 文件

```bash
python3 scripts/compose_validator.py examples/docker-compose.yml             # 随包样例；你的真实项目换成 docker-compose.yml
python3 scripts/compose_validator.py docker-compose.yml --output json
python3 scripts/compose_validator.py docker-compose.yml --strict    # 有 warning 即失败
```

预期：校验器确认 healthcheck、网络、卷无问题，无端口冲突，且（`--strict` 下）零 warning。
失败时：逐项应用修复并重跑，直到 `--strict` 通过。

### 步骤 5：安全审计（`/docker:security`）

Dockerfile 检查：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 以 root 运行 | Critical | 创建用户后加 `USER nonroot` |
| 使用 :latest tag | High | 锁定到具体版本 |
| ENV/ARG 中放密钥 | Critical | 改用 BuildKit secrets：`--mount=type=secret` |
| COPY 用宽泛 glob | Medium | 用具体路径，加 .dockerignore |
| 多余的 EXPOSE | Low | 只暴露应用实际使用的端口 |
| 无 HEALTHCHECK | Medium | 加 HEALTHCHECK，interval 设置合理 |
| 特权指令 | High | 避免 `--privileged`，drop capabilities |
| 包管理器缓存残留 | Low | 同一 RUN 层内清理 |

运行时检查（compose / 运行中的容器）：

| 检查项 | 严重度 | 修复 |
|-------|----------|-----|
| 容器以 root 运行 | Critical | 在 Dockerfile 或 compose 中设 user |
| 根文件系统可写 | Medium | compose 中用 `read_only: true` |
| 保留全部 capabilities | High | drop 全部，只加需要的：`cap_drop: [ALL]` |
| 无资源限额 | Medium | 设 `mem_limit` 与 `cpus` |
| host 网络模式 | High | 用 bridge 或自定义网络 |
| 敏感挂载 | Critical | 生产环境绝不挂载 /etc、/var/run/docker.sock |
| 未配置日志驱动 | Low | 设 `logging:` 带大小上限 |

预期：一份 `SECURITY AUDIT — <Dockerfile/image>` 格式的报告，带 CRITICAL/HIGH/MEDIUM/LOW 计数与逐项修复；交付前零 CRITICAL 项。

### 步骤 6：主动提示项

无人要求也要指出：

- **Dockerfile 用 :latest** → 建议锁定到具体版本 tag。
- **无 .dockerignore** → 建一个。至少包含：`.git`、`node_modules`、`__pycache__`、`.env`。
- **依赖安装之前 COPY . .** → 缓存失效。调整顺序先装依赖。
- **以 root 运行** → 加 USER 指令。生产无例外。
- **ENV 或 ARG 中的密钥** → 改用 BuildKit secret mount。绝不把密钥烧进层。
- **镜像超过 1GB** → 必须多阶段构建。生产镜像没理由这么大。
- **无 healthcheck** → 加一个。编排器（Compose、K8s）需要它做生命周期管理。
- **apt-get 未在同一层清理** → 同一 RUN 里加 `rm -rf /var/lib/apt/lists/*`。

## 多阶段构建模式

### 模式 1：编译型语言（Go、Rust、C++）

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

### 模式 2：Node.js / TypeScript

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

### 模式 3：Python

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

## 基础镜像决策树

```text
是编译产物吗（Go、Rust、C）？
├── 是 → distroless/static 或 scratch
└── 否
    ├── 调试需要 shell？
    │   ├── 是 → alpine 变体（如 node:20-alpine）
    │   └── 否 → distroless 变体
    ├── 需要 glibc（不是 musl）？
    │   ├── 是 → slim 变体（如 python:3.12-slim）
    │   └── 否 → alpine 变体
    └── 需要特定 OS 包？
        ├── 很多 → debian-slim
        └── 很少 → alpine + apk add
```

## 失败处置表

| 症状 / 报错 | 原因 | 修复 |
|-----------------|-------|-----|
| 重写后分析器标记仍在 | 修复方式不对，或引入了新反模式 | 重跑 `dockerfile_analyzer.py --security`；一次只处理一个标记 |
| 优化后 `docker build` 失败 | 构建阶段少了必要构建依赖 | 构建阶段保留 SDK/工具；只让 runtime 阶段保持最小 |
| Compose 校验器：端口冲突 | 两个服务绑了同一个宿主端口 | 后端服务挪进 internal 网络；映射唯一的宿主端口 |
| Healthcheck 永远不过 | 端点或间隔不对 | 手动探测应用端点；调整 `interval`/`retries` |
| 多阶段后镜像仍超 1GB | 重组件被拷进了 runtime | 只拷构建出的二进制/dist；用 `docker history <image>` 核实 |
| `read_only: true` 下应用写不了文件 | 可写路径未提供 | 给 /tmp 和应用可写路径加 `tmpfs` 或 `emptyDir` 型卷 |

## 交付标准

成功定义：优化后的 Dockerfile 通过 `dockerfile_analyzer.py` 校验（无标记），`docker-compose.yml` 通过 `--strict` 校验，安全审计报告零 CRITICAL 发现项。
产物命名：`Dockerfile`、`docker-compose.yml`、`docker-compose.override.yml`（仅开发）、`.env.example`、`.dockerignore`。
保存位置：项目根目录，与源码同处。
完整性验证：分析器与校验器都通过（校验器用 `--strict`）；Dockerfile 中每个环境变量都出现在 `.env.example`；安全报告枚举全部检查项及 pass/fix 状态。

## 安全红线

- 密钥绝不进 Dockerfile、ARG/ENV、镜像层或已提交的 `.env` 文件——用 BuildKit secret mount，并用 `.gitignore` 排除 env 文件。
- 默认姿态：非 root 用户、只读根文件系统、drop capabilities、锁定 tag。
- 生产集群议题（编排、线上排障）超出范围；chart 相关归 helm-chart-builder。

## 参考

- `references/dockerfile-best-practices.md` —— 分析器标记背后的完整规则集与语言专项模式
- `references/compose-patterns.md` —— 组合多服务拓扑（网络、profiles、override 文件）时

## 相关技能

- **senior-devops** —— 更宽的 DevOps 范围（CI/CD、IaC、监控）。互补——容器专项用 docker-development，流水线与基础设施用 senior-devops。
- **senior-security** —— 应用安全。互补——docker-development 覆盖容器安全，senior-security 覆盖应用层威胁。
- **autoresearch-agent** —— 可把 Docker 构建耗时或镜像体积当可度量的实验来优化。
- **ci-cd-pipeline-builder** —— 流水线构建。互补——docker-development 构建容器，ci-cd-pipeline-builder 部署它们。

镜像与 compose 就绪，**接着说："容器化完成，继续调用 helm-chart-builder 生成部署 chart"——链条自动展开**。
