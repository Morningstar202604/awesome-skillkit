---
name: ruby
description: >-
  Ruby development guidelines covering idiomatic code style, Ruby 3.x features, testing with
  RSpec, and best practices for building maintainable Ruby applications. Do NOT use for Rails-
  specific conventions, gem packaging, or Ruby version upgrades.
description_zh: "Ruby 规范：地道写法、Ruby 3.x 特性与 RSpec 测试。"
license: Apache-2.0
compatibility: 纯提示型；随语言与框架版本演进，以上游为准。
metadata:
  author: "mindrally/skills 上游（Apache-2.0；由 Cursor Rules 转换）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mindrally/skills/tree/main/ruby"
---

# Ruby Development

You are an expert in Ruby development, including Ruby 3.x features, testing frameworks, and modern Ruby best practices.

## Code Style and Structure

- Write concise, idiomatic Ruby code with accurate examples
- Adhere to Ruby community conventions and style guides
- Use snake_case for files, methods, and variables
- Use CamelCase for classes and modules
- Favor descriptive names like `user_signed_in?` and `calculate_total`

## Ruby Language Features

- Leverage Ruby 3.x capabilities including:
  - Pattern matching with `case/in`
  - Endless methods for simple one-liners
  - Keyword arguments for clarity
  - Safe navigation operator (`&.`)
- Use blocks, procs, and lambdas effectively
- Apply metaprogramming judiciously

## Syntax and Formatting

- Follow the Ruby Style Guide
- Employ expressive syntax features
- Prefer single quotes except when string interpolation is needed
- Use meaningful method and variable names
- Keep methods small and focused (Single Responsibility Principle)

## Error Handling

- Apply exceptions for genuine edge cases only
- Implement proper logging with user-friendly messages
- Use custom exception classes for domain-specific errors
- Handle errors gracefully with appropriate rescue blocks

## Object-Oriented Design

- Follow SOLID principles
- Favor composition over inheritance
- Use modules for shared behavior (mixins)
- Keep classes focused and cohesive

## Testing Best Practices

### RSpec Guidelines

- Write comprehensive coverage of typical cases, edge cases, and error conditions
- Use clear, descriptive naming conventions for test blocks
- Organize logically with `describe` for classes/methods and `context` for scenarios
- Use `let` and factories (FactoryBot) instead of fixtures
- Ensure test independence with minimal shared state
- Mock external services strategically while testing real behavior when possible

### Test Structure

```ruby
describe ClassName do
  describe '#method_name' do
    context 'when condition exists' do
      it 'does expected behavior' do
        expect(result).to eq(expected)
      end
    end
  end
end
```

## Performance Optimization

- Profile code before optimizing
- Use appropriate data structures
- Leverage lazy enumerators for large collections
- Cache expensive computations

## Security

- Sanitize user input
- Use parameterized queries
- Keep dependencies updated
- Follow security best practices for handling sensitive data

## Verification Commands

- `rubocop` — expect `no offenses detected` (or only accepted todos from .rubocop_todo.yml).
- `rubocop --format json | jq '.summary.offense_count'` — expect 0 on touched files.

---

## 来源与署名 / Source & Attribution

本技能收录自 [mindrally/skills](https://github.com/mindrally/skills/tree/main/ruby)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
