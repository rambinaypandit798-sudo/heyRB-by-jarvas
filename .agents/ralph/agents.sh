#!/usr/bin/env bash
# Default agent command templates (used by loop.sh and CLI).

AGENT_CODEX_CMD="codex exec --yolo --skip-git-repo-check -"
AGENT_CODEX_INTERACTIVE_CMD="codex --yolo {prompt}"
AGENT_CLAUDE_CMD="claude -p --dangerously-skip-permissions \"\$(cat {prompt})\""
AGENT_CLAUDE_INTERACTIVE_CMD="claude --dangerously-skip-permissions {prompt}"
AGENT_DROID_CMD="droid exec --skip-permissions-unsafe -f {prompt}"
AGENT_DROID_INTERACTIVE_CMD="droid --skip-permissions-unsafe {prompt}"
AGENT_OPENCODE_CMD="opencode run \"\$(cat {prompt})\""
AGENT_OPENCODE_INTERACTIVE_CMD="opencode --prompt {prompt}"
AGENT_ANTIGRAVITY_CMD="antigravity-cli exec --yolo {prompt}"
AGENT_ANTIGRAVITY_INTERACTIVE_CMD="antigravity-cli {prompt}"
AGENT_GEMINI_CMD="gemini --yolo {prompt}"
AGENT_GEMINI_INTERACTIVE_CMD="gemini {prompt}"
AGENT_PYTHON_CMD="python /data/data/com.termux/files/home/.agents/ralph/runner.py {prompt}"
DEFAULT_AGENT="antigravity"
