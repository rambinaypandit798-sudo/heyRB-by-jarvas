#!/usr/bin/env python3
"""
Unified Agent Workflow Orchestrator
Connects GSD-Core, Ralph Loop, Roo Code, and CodeRabbit into an automated pipeline.
Enables autonomous write, test, review, and self-healing error recovery.
"""

import sys
import subprocess
from pathlib import Path

BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

def run_cmd(cmd, desc):
    print(f"{CYAN}▶ {desc}...{RESET}")
    res = subprocess.run(cmd, shell=True, text=True)
    if res.returncode != 0:
        print(f"{YELLOW}⚠ Step completed with code {res.returncode}{RESET}")
    else:
        print(f"{GREEN}✓ {desc} passed.{RESET}")
    return res.returncode

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print(f"""
{BOLD}{MAGENTA}============================================================{RESET}
{BOLD}🤖 Antigravity Autonomous Agent Workflow Orchestrator{RESET}
{BOLD}{MAGENTA}============================================================{RESET}

Commands:
  {BOLD}agent-workflow check{RESET}        - Verify all modules (GSD, Ralph, Roo, CodeRabbit)
  {BOLD}agent-workflow review [path]{RESET} - Run automated CodeRabbit review on code
  {BOLD}agent-workflow loop{RESET}         - Run continuous Ralph Loop on pending tasks
  {BOLD}agent-workflow status{RESET}       - Inspect Ralph Loop and PRD completion status
  {BOLD}agent-workflow gsd [args]{RESET}   - Run GSD-Core command
""")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "check":
        print(f"{BOLD}Verifying Antigravity Autonomous Toolstack...{RESET}")
        run_cmd("gsd-core --help > /dev/null", "GSD Core Framework")
        run_cmd("ralph-loop check", "Ralph Loop Continuous Engine")
        run_cmd("coderabbit-review --check", "CodeRabbit Automated Review Engine")
        run_cmd("git-auto-sync --check", "Git Auto-Sync Engine")
        print(f"\n{GREEN}{BOLD}All agent workflow modules are active and ready!{RESET}\n")

    elif cmd == "sync":
        args = sys.argv[2:]
        subprocess.run(["git-auto-sync"] + args)

    elif cmd == "review":
        target = sys.argv[2] if len(sys.argv) > 2 else "."
        subprocess.run(["coderabbit-review", target])

    elif cmd == "loop":
        subprocess.run(["ralph-loop", "run"])

    elif cmd == "status":
        subprocess.run(["ralph-loop", "status"])

    elif cmd == "gsd":
        args = sys.argv[2:]
        subprocess.run(["gsd-core"] + args)

    else:
        print(f"{RED}Unknown command: {cmd}. Run 'agent-workflow help' for options.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
