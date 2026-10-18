#!/usr/bin/env python3
"""
Comprehensive Test Verification Suite for Antigravity Advanced Coding Tools & Workflows
Validates GSD-Core, Ralph Loop, Roo Code, CodeRabbit, and Workflow Directives.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

class ToolVerifier:
    def __init__(self):
        self.home = Path(os.path.expanduser("~")).resolve()
        self.results = []

    def log_result(self, category: str, name: str, passed: bool, details: str = ""):
        self.results.append({
            "category": category,
            "name": name,
            "passed": passed,
            "details": details
        })
        badge = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
        print(f"  {badge} {BOLD}{name}{RESET}: {details}")

    def verify_gsd_core(self):
        print(f"\n{BOLD}{CYAN}1. Verifying GSD-Core & Meta-Prompting Framework{RESET}")
        
        # Check binaries
        binaries = ["gsd-core", "gsd_run", "gsd-tools", "gsd-mcp-server"]
        for b in binaries:
            path = shutil.which(b)
            self.log_result("GSD-Core", f"Binary: {b}", path is not None, path or "Not found in PATH")

        # Check global skills directory
        skills_dir = self.home / ".gemini" / "config" / "skills"
        has_skills = skills_dir.exists() and len(list(skills_dir.glob("gsd-*"))) >= 50
        count = len(list(skills_dir.glob("gsd-*"))) if skills_dir.exists() else 0
        self.log_result("GSD-Core", "Global Skills Installed", has_skills, f"{count} GSD skills active in ~/.gemini/config/skills")

        # Check MCP Server config
        mcp_path = self.home / ".gemini" / "antigravity-cli" / "mcp_config.json"
        has_mcp = mcp_path.exists()
        self.log_result("GSD-Core", "MCP Companion Server Config", has_mcp, str(mcp_path))

    def verify_ralph_loop(self):
        print(f"\n{BOLD}{CYAN}2. Verifying Ralph Loop Continuous Task Execution{RESET}")
        
        # Check ralph CLI
        ralph_bin = shutil.which("ralph")
        self.log_result("Ralph Loop", "Binary: ralph", ralph_bin is not None, ralph_bin or "Not found")

        # Check ralph-loop runner
        runner_bin = shutil.which("ralph-loop")
        self.log_result("Ralph Loop", "Binary: ralph-loop", runner_bin is not None, runner_bin or "Not found")

        # Check .agents/ralph assets
        loop_sh = self.home / ".agents" / "ralph" / "loop.sh"
        self.log_result("Ralph Loop", "Scaffolded loop.sh", loop_sh.exists(), str(loop_sh))

        # Check PRD database
        prd_file = self.home / ".agents" / "tasks" / "prd.json"
        self.log_result("Ralph Loop", "PRD Database (prd.json)", prd_file.exists(), str(prd_file))

    def verify_roo_code(self):
        print(f"\n{BOLD}{CYAN}3. Verifying Roo Code Extension & Architectural Rules{RESET}")
        
        rules_dir = self.home / ".roo" / "rules"
        rule_files = ["01-general.md", "02-architecture-context.md", "03-autonomous-self-healing.md", "04-clean-api-integration.md", "05-coderabbit-quality.md"]
        all_rules_exist = all((rules_dir / f).exists() for f in rule_files)
        self.log_result("Roo Code", "Modular Rules (.roo/rules)", all_rules_exist, f"{len(rule_files)} rules verified")

        roorules = self.home / ".roorules"
        self.log_result("Roo Code", "Project Rule (.roorules)", roorules.exists(), str(roorules))

        modes_file = self.home / ".roo" / "modes.json"
        self.log_result("Roo Code", "Custom Modes (.roo/modes.json)", modes_file.exists(), str(modes_file))

    def verify_coderabbit(self):
        print(f"\n{BOLD}{CYAN}4. Verifying CodeRabbit Automated Review Integration{RESET}")
        
        cr_bin = shutil.which("coderabbit-review")
        self.log_result("CodeRabbit", "Binary: coderabbit-review", cr_bin is not None, cr_bin or "Not found")

        cr_yaml = self.home / ".coderabbit.yaml"
        self.log_result("CodeRabbit", "Configuration (.coderabbit.yaml)", cr_yaml.exists(), str(cr_yaml))

        # Run quick dry run test on a python snippet
        test_py = self.home / "scripts" / "coderabbit_review.py"
        test_run = subprocess.run(["coderabbit-review", str(test_py)], capture_output=True, text=True)
        self.log_result("CodeRabbit", "Live Execution Test", test_run.returncode == 0, f"Exit code {test_run.returncode}")

    def verify_workflow_directives(self):
        print(f"\n{BOLD}{CYAN}5. Verifying Antigravity CLI Workflow Integration & Directives{RESET}")
        
        agents_md = self.home / "AGENTS.md"
        gemini_md = self.home / "GEMINI.md"
        self.log_result("Workflow", "Workspace AGENTS.md", agents_md.exists(), str(agents_md))
        self.log_result("Workflow", "Workspace GEMINI.md", gemini_md.exists(), str(gemini_md))

        # Check for all 5 required directives
        if agents_md.exists():
            content = agents_md.read_text(encoding="utf-8")
            has_context = "STRICT CONTEXT MEMORY" in content
            has_self_healing = "AUTONOMOUS ERROR SELF-HEALING" in content
            has_clean_api = "CLEAN API INTEGRATION" in content
            has_loops = "RALPH LOOP" in content
            has_coderabbit = "CODERABBIT" in content

            self.log_result("Directives", "Strict Context Memory Directive", has_context, "Preserves Lovable UI & tokens")
            self.log_result("Directives", "Self-Healing Loop Directive", has_self_healing, "Zero user interruption on errors")
            self.log_result("Directives", "Clean API Integration Directive", has_clean_api, "Bypasses rigid sk_ prefixes")
            self.log_result("Directives", "Continuous Execution Directive", has_loops, "Continuous loop until 100% complete")
            self.log_result("Directives", "CodeRabbit Gate Directive", has_coderabbit, "Zero syntax errors / 0 vulnerabilities")

    def verify_mcp_servers(self):
        print(f"\n{BOLD}{CYAN}6. Verifying Model Context Protocol (MCP) Servers{RESET}")
        
        fs_bin = shutil.which("mcp-server-filesystem")
        self.log_result("MCP Servers", "Binary: mcp-server-filesystem", fs_bin is not None, fs_bin or "Not found")

        supa_bin = shutil.which("mcp-server-supabase")
        self.log_result("MCP Servers", "Binary: mcp-server-supabase", supa_bin is not None, supa_bin or "Not found")

        wrapper = self.home / "scripts" / "supabase_mcp_wrapper.js"
        self.log_result("MCP Servers", "Supabase MCP Wrapper", wrapper.exists() and os.access(wrapper, os.X_OK), str(wrapper))

        mcp_cfg = self.home / "mcp-config.json"
        has_servers = False
        if mcp_cfg.exists():
            try:
                data = json.loads(mcp_cfg.read_text())
                servers = data.get("mcpServers", {})
                has_servers = "filesystem" in servers and "supabase" in servers
            except Exception:
                pass
        self.log_result("MCP Servers", "Configuration (mcp-config.json)", has_servers, "Filesystem & Supabase entries configured")

    def verify_git_auto_sync(self):
        print(f"\n{BOLD}{CYAN}7. Verifying Autonomous Git Auto-Sync Engine{RESET}")
        
        gas_bin = shutil.which("git-auto-sync")
        self.log_result("Git Auto-Sync", "Binary: git-auto-sync", gas_bin is not None, gas_bin or "Not found")

        script = self.home / "scripts" / "git-auto-sync.sh"
        self.log_result("Git Auto-Sync", "Executable (git-auto-sync.sh)", script.exists() and os.access(script, os.X_OK), str(script))

        # Check git-auto-sync --check
        res = subprocess.run(["git-auto-sync", "--check"], capture_output=True, text=True)
        self.log_result("Git Auto-Sync", "Execution Health Check", res.returncode == 0, res.stdout.strip())

    def run_all(self):
        print(f"{BOLD}{MAGENTA}============================================================{RESET}")
        print(f"{BOLD}🔍 ANTIGRAVITY ADVANCED CODING TOOLS & WORKFLOW VERIFICATION{RESET}")
        print(f"{BOLD}{MAGENTA}============================================================{RESET}")
        
        self.verify_gsd_core()
        self.verify_ralph_loop()
        self.verify_roo_code()
        self.verify_coderabbit()
        self.verify_workflow_directives()
        self.verify_mcp_servers()
        self.verify_git_auto_sync()

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print(f"\n{BOLD}{MAGENTA}============================================================{RESET}")
        print(f"{BOLD}SUMMARY: {total} Checks Performed | {GREEN}{passed} Passed{RESET} | {RED}{failed} Failed{RESET}")
        print(f"{BOLD}{MAGENTA}============================================================{RESET}\n")

        if failed == 0:
            print(f"{GREEN}{BOLD}🎉 ALL SYSTEMS NOMINAL: Autonomous Coding Stack is 100% operational!{RESET}\n")
            return 0
        else:
            print(f"{RED}{BOLD}⚠ SOME CHECKS FAILED: Review the details above.{RESET}\n")
            return 1

if __name__ == "__main__":
    verifier = ToolVerifier()
    sys.exit(verifier.run_all())
