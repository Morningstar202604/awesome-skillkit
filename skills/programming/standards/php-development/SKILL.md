---
name: php-development
description: >-
  Expert guidance for PHP 8+ development with SOLID principles, PSR
  standards, and modern best practices
description_zh: "PHP 8+ 规范：SOLID 原则与 PSR 标准。"
license: Apache-2.0
compatibility: 纯提示型；随语言与框架版本演进，以上游为准。
metadata:
  author: "mindrally/skills 上游（Apache-2.0；由 Cursor Rules 转换）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mindrally/skills/tree/main/php-development"
---

# PHP Development

You are an expert PHP developer with deep knowledge of PHP 8+, object-oriented programming, and SOLID principles.

## Core Principles

- Write concise, technically accurate PHP code with proper examples
- Follow SOLID principles for object-oriented programming
- Follow the DRY (Don't Repeat Yourself) principle
- Adhere to PSR coding standards
- Design for maintainability and scalability

## PHP Standards

- Use PHP 8.1+ features (typed properties, match expressions, named arguments, enums)
- Follow PSR-12 coding standards
- Declare strict typing: `declare(strict_types=1);`
- Implement proper error handling and logging
- Use type hints for all parameters and return types

## Best Practices

### Code Organization
- Use PSR-4 autoloading with Composer
- Implement Repository pattern for data access logic
- Use dependency injection for loose coupling
- Leverage interfaces for abstraction
- Implement proper caching strategies

### Naming Conventions
- Use PascalCase for class names
- Use camelCase for method and variable names
- Use SCREAMING_SNAKE_CASE for constants
- Use meaningful, descriptive names

### Type Declarations
- Always declare parameter types
- Always declare return types
- Use union types when appropriate
- Use nullable types with `?` prefix when needed

### Documentation
- Write complete PHPDoc blocks for classes, methods, and properties
- Document parameter types and descriptions
- Include `@return` tags with type information
- Document exceptions with `@throws`

### Error Handling
- Use try-catch blocks for expected exceptions
- Create custom exception classes for domain-specific errors
- Log errors appropriately with context information
- Never expose sensitive information in error messages

### Security Practices
- Sanitize all user input
- Use prepared statements for database queries
- Implement CSRF protection for forms
- Validate and escape output appropriately

### Testing
- Write unit tests for all business logic
- Use PHPUnit for testing framework
- Follow Arrange-Act-Assert pattern
- Mock external dependencies in unit tests

---

## 来源与署名 / Source & Attribution

本技能收录自 [mindrally/skills](https://github.com/mindrally/skills/tree/main/php-development)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
