# Roo Code Rule 05: CodeRabbit Automated Quality Gates

1. **Pre-Commit Automated Code Review**:
   - Before completing tasks, closing loops, or committing to version control, run `coderabbit-review` to inspect modified code.
   - Zero tolerance for syntax errors (Python AST errors, JS/TS parser errors).
   - Zero tolerance for critical security vulnerabilities (hardcoded secrets, unescaped shell commands, SQL injections).

2. **Automated Remediations**:
   - If `coderabbit-review` surfaces issues, auto-fix them immediately within the active loop before pushing or concluding.
