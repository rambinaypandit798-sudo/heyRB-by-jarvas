---
name: roo-code
description: Roo Code rules, custom modes (architect, code, debug, review), and autonomous think-then-do workflows for structured coding and prompt guidelines.
---

# Roo Code Autonomous Guidelines & Modes

This skill exposes Roo Code instructions, mode configurations, and architecture constraints.

## Configured Rules in Workspace

The workspace loads rules from `.roo/rules/` and `.roorules`:
- `01-general.md`: Think-then-do pattern, zero filler, zero-mock policy.
- `02-architecture-context.md`: Strict context memory, read project layout first, keep Lovable UI designs & sticky input bar 100% intact.
- `03-autonomous-self-healing.md`: Autonomous error self-healing loop for build failures and API mismatches.
- `04-clean-api-integration.md`: Clean API integration bypassing rigid `sk_` prefixes.
- `05-coderabbit-quality.md`: CodeRabbit pre-commit automated review.

## Available Modes (`.roo/modes.json`)

1. `autonomous-loop`: Full task breakdown and continuous loop execution.
2. `coderabbit-auditor`: Deep security and code review mode.
3. `self-healer`: Automated error triage and hotfixing without user prompts.
