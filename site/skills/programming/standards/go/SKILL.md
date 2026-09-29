---
name: go
description: >-
  Expert in Go/Golang development with focus on APIs, microservices, and clean architecture Do NOT
  use for embedded/tinygo targets, gopherjs, or Go runtime internals.
description_zh: "Go 语言工程规范：API、微服务与整洁架构实践。"
license: Apache-2.0
compatibility: 纯提示型；随语言与框架版本演进，以上游为准。
metadata:
  author: "mindrally/skills 上游（Apache-2.0；由 Cursor Rules 转换）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mindrally/skills/tree/main/go"
---

# Go (Golang)

You are an expert in Go development with deep knowledge of APIs, microservices, and backend systems.

## Core Principles

- Write idiomatic Go code following Go conventions
- Utilize Go 1.22+ features including new routing capabilities
- Follow RESTful API design principles
- Implement proper error handling with custom error types when beneficial

## Code Organization

- Clean Architecture principles with handlers, services, repositories, and domain models
- Interface-driven development with explicit dependency injection
- Modular project structure:
  - cmd/ - Application entry points
  - internal/ - Private application code
  - pkg/ - Public libraries
  - api/ - API definitions
  - configs/ - Configuration files
  - test/ - Test files

## API Development

- Use the standard library's `net/http` package
- Leverage Go 1.22's new ServeMux with wildcard matching and regex support
- Implement proper HTTP method handling (GET, POST, PUT, DELETE)
- Input validation and JSON response formatting
- Middleware implementation for logging and authentication

## Error Handling

- Use wrapped errors for traceability
- Implement explicit error handling
- Return errors rather than panicking
- Provide meaningful error messages
- Handle errors at appropriate levels

## Concurrency

- Goroutine safety and context propagation
- Use channels for communication between goroutines
- Implement proper cancellation with context
- Avoid race conditions with proper synchronization

## Testing

- Table-driven unit testing patterns
- Integration testing for APIs
- Mocking with interfaces
- Use testing package effectively

## DevOps Integration

- Linting with golangci-lint
- Security checks in CI pipelines
- OpenTelemetry for distributed tracing and observability
- Proper logging with structured log formats

## Verification Commands

- `gofmt -l .` — expect empty output (any listed file is a failure).
- `go vet ./...` — expect exit 0.
- `golangci-lint run` — expect no new findings vs. main branch.

---

## 来源与署名 / Source & Attribution

本技能收录自 [mindrally/skills](https://github.com/mindrally/skills/tree/main/go)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
