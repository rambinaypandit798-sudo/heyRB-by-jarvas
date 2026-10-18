#!/usr/bin/env python3
"""
CodeRabbit-Style Automated Code Review Engine
High-fidelity local code reviewer for bugs, syntax errors, and security issues.
Tailored for Termux, Android Userland, Python, TypeScript, JavaScript, and Web stacks.
"""

import os
import sys
import re
import ast
import json
import py_compile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

VERSION = "1.3.0"

# ANSI Color codes
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

SECURITY_PATTERNS = [
    {
        "id": "SEC-001",
        "name": "Hardcoded Secret / Token",
        "severity": "CRITICAL",
        "pattern": r'(?i)(?:api_key|secret|token|password|auth_token|access_token|private_key)\s*[:=]\s*["\'](?!bypass-|test-|fake-|YOUR_|ENV|process\.env|os\.environ|\${)[A-Za-z0-9_\-\.]{24,}["\']',
        "description": "Potential hardcoded credential or secret found in code.",
        "remediation": "Move credential to environment variable or secure vault."
    },
    {
        "id": "SEC-002",
        "name": "Command Injection Vulnerability",
        "severity": "HIGH",
        "pattern": r'(?i)(?:os\.system\s*\(\s*f["\']|subprocess\.(?:call|Popen|run)\s*\([^)]*shell\s*=\s*True[^)]*f["\']|exec\s*\([^)]*\bf["\'])',
        "description": "Formatted string passed into shell execution without shell-escaping.",
        "remediation": "Use arguments array without shell=True, or sanitize via shlex.quote()."
    },
    {
        "id": "SEC-003",
        "name": "SQL Injection Risk",
        "severity": "HIGH",
        "pattern": r'(?i)(?:execute|raw)\s*\(\s*f["\'](?:SELECT|INSERT|UPDATE|DELETE)[^"\']*\{',
        "description": "Unescaped string interpolation in SQL query execution.",
        "remediation": "Use parameterized queries with ? or :param placeholders."
    },
    {
        "id": "SEC-004",
        "name": "Insecure Eval / Function Constructor",
        "severity": "HIGH",
        "pattern": r'(?i)(?:eval\s*\([^)]+\)|new\s+Function\s*\([^)]+\))',
        "description": "Dynamic code evaluation via eval() or new Function().",
        "remediation": "Avoid dynamic evaluation of untrusted strings."
    },
    {
        "id": "SEC-005",
        "name": "Strict Prefix Restriction on API Key",
        "severity": "MEDIUM",
        "pattern": r'(?i)(?:key|token)\.(?:startswith|starts_with)\s*\(\s*["\']sk[-_]',
        "description": "Strict sk- or sk_ prefix enforcement will reject direct Google Gemini keys (AIzaSy...).",
        "remediation": "Remove rigid prefix checks to support direct Google Gemini API keys."
    }
]

CODE_QUALITY_PATTERNS = [
    {
        "id": "QLT-001",
        "name": "Empty Catch Block",
        "severity": "LOW",
        "pattern": r'(?i)catch\s*(?:\([^)]*\))?\s*\{\s*\}',
        "description": "Silent catch block suppresses errors without logging or handling.",
        "remediation": "Log exception or add explicit handling comment."
    },
    {
        "id": "QLT-002",
        "name": "Debug Console Log",
        "severity": "LOW",
        "pattern": r'\bconsole\.(?:log|debug)\s*\(',
        "description": "Console debug logging statement found.",
        "remediation": "Remove debug logging before shipping or use structured logger."
    },
    {
        "id": "QLT-003",
        "name": "Python Bare Except",
        "severity": "MEDIUM",
        "pattern": r'^\s*except\s*:',
        "description": "Bare except catches KeyboardInterrupt and SystemExit unintentionally.",
        "remediation": "Catch Exception instead: except Exception:"
    }
]

IGNORE_DIRS = {
    ".git", "node_modules", ".cache", "__pycache__", ".npm", "dist", "build",
    ".gemini", ".termux", ".agents/ralph/runs", "coverage", ".next",
    ".planning", ".output", ".venv", "venv", ".cargo", ".rustup", "site-packages"
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg",
    ".db", ".sqlite", ".db-wal", ".db-shm", ".tar", ".gz", ".zip",
    ".woff", ".woff2", ".ttf", ".eot", ".lock", ".pb", ".pbtxt",
    ".jsonl", ".log"
}

class CodeRabbitReviewer:
    def __init__(self, target_paths: Optional[List[str]] = None, verbose: bool = False):
        self.target_paths = [Path(p).resolve() for p in (target_paths or ["."])]
        self.verbose = verbose
        self.findings: List[Dict[str, Any]] = []
        self.files_scanned = 0
        self.syntax_errors = 0

    def should_ignore(self, path: Path) -> bool:
        if path.name.startswith(".env") or path.name.endswith(".lock") or path.name.endswith(".jsonl"):
            return True
        for part in path.parts:
            if part in IGNORE_DIRS or part.startswith(".git"):
                return True
        if path.suffix.lower() in IGNORE_EXTENSIONS:
            return True
        return False

    def check_python_syntax(self, file_path: Path) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            ast.parse(content, filename=str(file_path))
            return None
        except SyntaxError as e:
            return f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
        except Exception as e:
            return f"Parse failure: {str(e)}"

    def check_js_syntax(self, file_path: Path) -> Optional[str]:
        if file_path.suffix in [".js", ".mjs", ".cjs"]:
            res = subprocess.run(
                ["node", "--check", str(file_path)],
                capture_output=True,
                text=True
            )
            if res.returncode != 0:
                err = res.stderr.strip() or res.stdout.strip()
                return err.split("\n")[0]
        return None

    def check_json_syntax(self, file_path: Path) -> Optional[str]:
        if file_path.suffix == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                return f"Invalid JSON: {str(e)}"
        return None

    def scan_file(self, file_path: Path):
        self.files_scanned += 1
        try:
            rel_path = file_path.relative_to(Path.cwd())
        except ValueError:
            rel_path = file_path

        # 1. Syntax Check
        syntax_err = None
        if file_path.suffix == ".py":
            syntax_err = self.check_python_syntax(file_path)
        elif file_path.suffix in [".js", ".mjs", ".cjs"]:
            syntax_err = self.check_js_syntax(file_path)
        elif file_path.suffix == ".json":
            syntax_err = self.check_json_syntax(file_path)

        if syntax_err:
            self.syntax_errors += 1
            self.findings.append({
                "file": str(rel_path),
                "line": 1,
                "id": "SYN-001",
                "severity": "CRITICAL",
                "category": "Syntax Error",
                "name": "Parse / Syntax Error",
                "description": syntax_err,
                "remediation": "Correct the syntax error before compiling or executing."
            })

        # 2. Source inspection for patterns
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            if self.verbose:
                print(f"Skipping unreadable file: {file_path} ({e})")
            return

        for idx, line in enumerate(lines, start=1):
            # Check Security Patterns
            for p in SECURITY_PATTERNS:
                if re.search(p["pattern"], line):
                    # Check for false positives
                    if "# coderabbit:ignore" in line or "// coderabbit:ignore" in line:
                        continue
                    self.findings.append({
                        "file": str(rel_path),
                        "line": idx,
                        "id": p["id"],
                        "severity": p["severity"],
                        "category": "Security",
                        "name": p["name"],
                        "description": p["description"],
                        "snippet": line.strip(),
                        "remediation": p["remediation"]
                    })

            # Check Code Quality Patterns
            for q in CODE_QUALITY_PATTERNS:
                if re.search(q["pattern"], line):
                    if "# coderabbit:ignore" in line or "// coderabbit:ignore" in line:
                        continue
                    self.findings.append({
                        "file": str(rel_path),
                        "line": idx,
                        "id": q["id"],
                        "severity": q["severity"],
                        "category": "Quality",
                        "name": q["name"],
                        "description": q["description"],
                        "snippet": line.strip(),
                        "remediation": q["remediation"]
                    })

    def run_review(self) -> Dict[str, Any]:
        for target in self.target_paths:
            if target.is_file():
                if not self.should_ignore(target):
                    self.scan_file(target)
            elif target.is_dir():
                for root, dirs, files in os.walk(target):
                    # Filter dirs in place
                    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".git") and not d.startswith(".gemini")]
                    for file in files:
                        fp = Path(root) / file
                        if not self.should_ignore(fp):
                            self.scan_file(fp)

        critical_count = sum(1 for f in self.findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in self.findings if f["severity"] == "HIGH")
        medium_count = sum(1 for f in self.findings if f["severity"] == "MEDIUM")
        low_count = sum(1 for f in self.findings if f["severity"] == "LOW")

        status = "PASSED"
        if critical_count > 0 or self.syntax_errors > 0:
            status = "FAILED"
        elif high_count > 0:
            status = "WARNING"

        return {
            "status": status,
            "version": VERSION,
            "files_scanned": self.files_scanned,
            "syntax_errors": self.syntax_errors,
            "counts": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "total": len(self.findings)
            },
            "findings": self.findings
        }

    def print_report(self, result: Dict[str, Any], json_output: bool = False):
        if json_output:
            print(json.dumps(result, indent=2))
            return

        print(f"\n{BOLD}{CYAN}------------------------------------------------------------{RESET}")
        print(f"{BOLD}🐰 CodeRabbit Automated Review Engine v{result['version']}{RESET}")
        print(f"{BOLD}{CYAN}------------------------------------------------------------{RESET}")

        status = result["status"]
        if status == "PASSED":
            status_badge = f"{GREEN}[STATUS: PASSED]{RESET}"
        elif status == "WARNING":
            status_badge = f"{YELLOW}[STATUS: WARNING]{RESET}"
        else:
            status_badge = f"{RED}[STATUS: FAILED]{RESET}"

        print(f"Overall Status: {status_badge}")
        print(f"Files Scanned:  {result['files_scanned']}")
        print(f"Syntax Errors:  {result['syntax_errors']}")
        counts = result["counts"]
        print(f"Findings:       {RED}{counts['critical']} Critical{RESET} | {RED}{counts['high']} High{RESET} | {YELLOW}{counts['medium']} Medium{RESET} | {CYAN}{counts['low']} Low{RESET}")
        print(f"{BOLD}{CYAN}------------------------------------------------------------{RESET}\n")

        if not result["findings"]:
            print(f"{GREEN}✓ No syntax errors, security vulnerabilities, or critical flaws detected.{RESET}\n")
            return

        # Group findings by file
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for f in result["findings"]:
            grouped.setdefault(f["file"], []).append(f)

        for file, file_findings in grouped.items():
            print(f"{BOLD}📁 {file}{RESET}")
            for item in file_findings:
                sev = item["severity"]
                if sev == "CRITICAL":
                    sev_str = f"{RED}[CRITICAL]{RESET}"
                elif sev == "HIGH":
                    sev_str = f"{RED}[HIGH]{RESET}"
                elif sev == "MEDIUM":
                    sev_str = f"{YELLOW}[MEDIUM]{RESET}"
                else:
                    sev_str = f"{CYAN}[LOW]{RESET}"

                print(f"  Line {item['line']} {sev_str} {BOLD}{item['name']}{RESET} ({item['id']})")
                print(f"    {item['description']}")
                if "snippet" in item:
                    print(f"    {YELLOW}> {item['snippet']}{RESET}")
                print(f"    {GREEN}↳ Fix: {item['remediation']}{RESET}")
            print()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CodeRabbit Automated Code Review Tool")
    parser.add_argument("paths", nargs="*", default=[], help="Paths to files or directories to review")
    parser.add_argument("--git", action="store_true", help="Only review modified / staged git files")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON")
    parser.add_argument("--check", action="store_true", help="Quick sanity check")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--strict", action="store_true", help="Fail on any medium/high issue")

    args = parser.parse_args()

    if args.check:
        print(f"🐰 CodeRabbit Review Engine v{VERSION} is active and ready in Termux.")
        sys.exit(0)

    target_paths = args.paths
    if args.git:
        try:
            res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
            git_files = []
            for line in res.stdout.splitlines():
                if len(line) >= 4:
                    raw_file = line[3:].strip()
                    if " -> " in raw_file:
                        raw_file = raw_file.split(" -> ")[1].strip()
                    p = Path(raw_file)
                    if p.exists() and p.is_file():
                        git_files.append(str(p))
            target_paths = git_files
            if not target_paths:
                print(f"🐰 CodeRabbit Review: No modified git files to scan.")
                sys.exit(0)
        except Exception as e:
            if args.verbose:
                print(f"Git inspection failed: {e}")
            target_paths = ["."]

    if not target_paths:
        target_paths = ["."]

    reviewer = CodeRabbitReviewer(target_paths=target_paths, verbose=args.verbose)
    result = reviewer.run_review()
    reviewer.print_report(result, json_output=args.json)

    if result["status"] == "FAILED":
        sys.exit(1)
    elif args.strict and (result["counts"]["high"] > 0 or result["counts"]["medium"] > 0):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
