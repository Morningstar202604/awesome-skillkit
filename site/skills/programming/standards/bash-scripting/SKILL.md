---
name: bash-scripting
description: >-
  Bash scripting guidelines covering security, portability, error handling, and automation best
  practices for DevOps. Do NOT use for executing or debugging a failing script, POSIX sh
  portability audits, or PowerShell/zsh/fish specifics.
description_zh: "Bash 脚本规范：安全、可移植、错误处理与自动化。"
license: Apache-2.0
compatibility: 纯提示型；随语言与框架版本演进，以上游为准。
metadata:
  author: "mindrally/skills 上游（Apache-2.0；由 Cursor Rules 转换）"
  version: "1.0.0"
  category: programming
  pattern: single-task
  tier: standard
  verified-date: "2026-09-27"
  source: "https://github.com/mindrally/skills/tree/main/bash-scripting"
---

# Bash Scripting

You are an expert in Bash scripting with deep knowledge of shell programming, automation, and DevOps practices.

## Core Principles

- Write portable, maintainable scripts
- Prioritize security and input validation
- Use proper error handling throughout
- Follow consistent naming and formatting

## Naming & Structure

- Use descriptive names for scripts and variables (e.g., `backup_files.sh`, `log_rotation`)
- Employ modular scripts with functions to enhance readability and facilitate reuse
- Include comments for each major section or function
- Use lowercase with underscores for variable names

## Input Validation & Security

- Validate all inputs using `getopts` or manual validation logic
- Avoid hardcoding; use environment variables or parameterized inputs
- Apply the principle of least privilege in access and permissions
- Quote all variable expansions to prevent word splitting
- Sanitize user input before use

## Code Quality

- Ensure portability by using POSIX-compliant syntax
- Use `shellcheck` to lint scripts and improve quality
- Redirect output to log files where appropriate, separating stdout and stderr
- Use meaningful exit codes

## Error Handling & Cleanup

- Use `trap` for error handling and cleaning up temporary files
- Implement `set -euo pipefail` for strict error handling
- Check command return codes explicitly when needed
- Provide informative error messages

## Best Practices

```bash
#!/usr/bin/env bash
set -euo pipefail

# Trap for cleanup
trap cleanup EXIT

cleanup() {
    # Clean up temporary files
    rm -f "${TEMP_FILE:-}"
}

# Use functions for modularity
main() {
    validate_input "$@"
    process_data
}

validate_input() {
    [[ $# -lt 1 ]] && { echo "Usage: $0 <arg>"; exit 1; }
}

main "$@"
```

## Automation Best Practices

- Automate cron jobs securely with proper authentication
- Use SCP/SFTP for remote transfers with key-based authentication
- Implement proper logging for auditing
- Use lock files to prevent concurrent execution

## Specific Use Cases

- Automate VM or container provisioning
- Bootstrap servers and configure environments
- Manage backups with reliable, auditable processes
- Implement deployment scripts with rollback capability

## Verification Commands

- `shellcheck script.sh` — expect exit 0, no output (add to CI on every script change).
- `bash -n script.sh` — syntax-only parse; expect silent exit 0.
- `shellcheck --severity=style script.sh` — stricter pass; treat new style findings as review comments, not blockers.

---

## 来源与署名 / Source & Attribution

本技能收录自 [mindrally/skills](https://github.com/mindrally/skills/tree/main/bash-scripting)（Apache-2.0）；awesome-skillkit 仅做规范化（frontmatter 归一、补中文描述、路径与链接清理）与署名，内容与更新以上游为准。
