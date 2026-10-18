---
name: coderabbit-review
description: Automated CodeRabbit-style code review to scan for bugs, syntax errors, and security issues across Python, JavaScript, TypeScript, and JSON files before committing or shipping.
---

# CodeRabbit Automated Code Review

This skill allows the agent to run high-precision, CodeRabbit-style automated code reviews on local files, git working trees, or entire repositories.

## When to Run

- Immediately after generating or modifying code.
- Before committing changes with Git.
- As part of the Ralph Loop or GSD-Core verification step (`gsd-verify-work` or `gsd-ship`).

## How to Execute

Run the CodeRabbit reviewer from the command line:

```bash
# Review current directory changes
coderabbit-review

# Review a specific directory or file
coderabbit-review path/to/file_or_dir

# Review with JSON output for programmatic evaluation
coderabbit-review --json

# Run a quick check
coderabbit-review --check
```

## Review Standards Enforced

1. **Syntax Integrity**: Python `ast.parse`, JavaScript/Node `--check`, JSON/YAML validity.
2. **Security Vulnerabilities**: Hardcoded tokens, SQL injections, shell command injection (`shell=True`), dynamic `eval()`.
3. **API Standards**: Bypasses rigid `sk_` prefixes to support direct Google Gemini API keys cleanly.
4. **Preservation**: Verifies that Lovable UI tokens, sticky input bar layouts, and component structures remain 100% intact.
