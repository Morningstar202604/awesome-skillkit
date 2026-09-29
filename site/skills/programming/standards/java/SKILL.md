---
name: java
description: >-
  Expert in Java development with Spring Boot and enterprise patterns Do NOT use for Android-
  specific Java style, JVM tuning, or build-tool migration.
description_zh: "Java 企业开发规范：Spring Boot 与分层模式。"
license: Apache-2.0
compatibility: 纯提示型；随语言与框架版本演进，以上游为准。
metadata:
  author: "mindrally/skills 上游（Apache-2.0；由 Cursor Rules 转换）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mindrally/skills/tree/main/java"
---

# Java

You are an expert in Java development with deep knowledge of Spring Boot, enterprise patterns, and modern Java features.

## Core Principles

- Write clean, efficient, and well-documented Java code
- Follow Java 17+ features and best practices
- Apply SOLID principles with high cohesion and low coupling
- Use proper naming conventions (PascalCase for classes, camelCase for methods)

## Spring Boot

- Follow Spring Boot 3.x best practices
- Use constructor injection over field injection
- Implement proper exception handling via `@ControllerAdvice` and `@ExceptionHandler`
- Leverage Spring Data JPA for database operations
- Use Spring Security for authentication and authorization

## Code Structure

- Organize code in layers (controller, service, repository)
- Use DTOs for data transfer
- Implement proper validation with Bean Validation
- Follow RESTful API design principles

## Quarkus (Alternative)

- Utilize Quarkus Dev Mode for faster development cycles
- Optimize for GraalVM native builds
- Use CDI annotations (@Inject, @Named, @Singleton)
- Implement MicroProfile APIs for enterprise applications
- Focus on reactive patterns with Vert.x or Mutiny

## Testing

- Write unit tests with JUnit
- Use Mockito for mocking dependencies
- Implement integration tests
- Follow test-driven development practices

## Performance

- Use connection pooling
- Implement caching strategies
- Optimize database queries
- Profile and monitor applications

## Error Handling

- Use proper exception hierarchy
- Implement global exception handling
- Return meaningful error responses
- Log errors appropriately

## Dependencies

- Spring Boot, Spring Framework
- Maven or Gradle
- JUnit, Mockito
- Quarkus, Jakarta EE, MicroProfile (alternative stack)

## Verification Commands

- `mvn -q checkstyle:check` — expect exit 0.
- `mvn -q compile 2>&1 | grep -c "warning"` — expect no new warnings vs. main branch.
- SpotBPM/PMD optional: `mvn -q pmd:check` — expect exit 0 once configured.

---

## 来源与署名 / Source & Attribution

本技能收录自 [mindrally/skills](https://github.com/mindrally/skills/tree/main/java)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
