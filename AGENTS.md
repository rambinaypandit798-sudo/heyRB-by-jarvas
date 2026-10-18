# AUTONOMOUS AGENT WORKFLOW DIRECTIVES & RULES (ANTIGRAVITY CLI)

## 1. STRICT CONTEXT MEMORY
- Always inspect the project layout, dependencies, and configuration from the repository root before touching or modifying any file.
- Keep all original Lovable UI designs, styling tokens, sticky input bar layouts, Arc Reactor HUD, and component structures **100% intact**. Never modify or dismantle existing UI flows.

## 2. AUTONOMOUS ERROR SELF-HEALING LOOP
- If an npm build failure, TypeScript error, API mismatch, or terminal exception occurs: **DO NOT ASK THE USER**.
- Immediately analyze the stack trace and error logs.
- Apply targeted fixes to the affected file(s).
- Restart servers or re-run build/test commands, and verify connectivity automatically until resolved.

## 3. CLEAN API INTEGRATION
- Bypass rigid prefix restrictions (such as `sk_` or `sk-`) to seamlessly integrate direct Google Gemini API requests (`AIzaSy...`) without crashing.
- Support multimodal payloads, streaming responses (SSE), and handle rate limits with backoff automatically.

## 4. GSD-CORE & RALPH LOOP CONTINUOUS EXECUTION
- Structure all non-trivial tasks using spec-driven development (`PLAN.md`, `prd.json`).
- Execute tasks in a continuous, atomic loop until requirements are 100% satisfied.
- Never terminate an active loop with tasks left in an unverified or pending state.

## 5. CODERABBIT AUTOMATED CODE REVIEW
- Run `coderabbit-review` on modified files before marking tasks as complete or committing changes.
- Ensure 0 syntax errors (Python AST, JS/Node `--check`, JSON validity) and 0 security vulnerabilities.
