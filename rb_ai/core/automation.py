"""
RB.AI - System Automation Engine
Integrates with Termux API and Android system capabilities.
Hardened with input validation, command sanitization, and path boundary checks.
"""

import os
import json
import shutil
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class TermuxAutomation:
    """Provides hardware and OS automation for RB.AI via Termux API."""

    def __init__(self):
        self.has_termux_api = self._check_command("termux-battery-status")
        self.base_dir = Path(__file__).resolve().parent.parent

    def _check_command(self, cmd: str) -> bool:
        return shutil.which(cmd) is not None

    def _run_cmd(self, cmd_args: list, timeout: int = 10) -> subprocess.CompletedProcess:
        try:
            res = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return res
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(cmd_args, 124, "", "Command timed out")
        except Exception as e:
            return subprocess.CompletedProcess(cmd_args, 1, "", str(e))

    def get_battery_status(self) -> Dict[str, Any]:
        """Returns battery percentage, health, temperature, and charging status."""
        if not self._check_command("termux-battery-status"):
            return {
                "available": False,
                "message": "termux-battery-status not found. Install 'termux-api' package and app."
            }

        res = self._run_cmd(["termux-battery-status"], timeout=2)
        if res.returncode == 0 and res.stdout.strip():
            try:
                data = json.loads(res.stdout)
                return {
                    "available": True,
                    "percentage": data.get("percentage"),
                    "status": data.get("status"),
                    "health": data.get("health"),
                    "temperature": data.get("temperature"),
                    "plugged": data.get("plugged")
                }
            except Exception as e:
                return {"available": False, "error": f"Failed to parse battery JSON: {e}"}
        return {"available": False, "error": res.stderr.strip() or "Failed to read battery"}

    def speak(self, text: str, pitch: float = 1.0, rate: float = 1.0) -> Dict[str, Any]:
        """Speaks text using Android TTS via Termux."""
        if not text:
            return {"success": False, "error": "Empty text"}

        if self._check_command("termux-tts-speak"):
            res = self._run_cmd(["termux-tts-speak", "-p", str(pitch), "-r", str(rate), text], timeout=10)
            return {"success": res.returncode == 0, "engine": "termux-tts"}
        
        # Fallback console speech log
        print(f"[RB.AI Voice]: {text}")
        return {"success": True, "engine": "console_fallback"}

    def send_notification(self, title: str, content: str, priority: str = "high") -> Dict[str, Any]:
        """Shows a system notification on Android."""
        if self._check_command("termux-notification"):
            res = self._run_cmd([
                "termux-notification",
                "--title", str(title)[:100],
                "--content", str(content)[:500],
                "--priority", priority,
                "--id", "rb_ai_notification"
            ], timeout=5)
            return {"success": res.returncode == 0}
        return {"success": False, "message": "termux-notification not available"}

    def vibrate(self, duration_ms: int = 300) -> Dict[str, Any]:
        """Vibrates the device."""
        if self._check_command("termux-vibrate"):
            dur = max(50, min(duration_ms, 5000))
            res = self._run_cmd(["termux-vibrate", "-d", str(dur)], timeout=6)
            return {"success": res.returncode == 0}
        return {"success": False, "message": "termux-vibrate not available"}

    def set_torch(self, enabled: bool) -> Dict[str, Any]:
        """Toggles the device flashlight/torch."""
        if self._check_command("termux-torch"):
            state = "on" if enabled else "off"
            res = self._run_cmd(["termux-torch", state], timeout=5)
            return {"success": res.returncode == 0, "torch": state}
        return {"success": False, "message": "termux-torch not available"}

    def get_clipboard(self) -> Dict[str, Any]:
        """Reads text from system clipboard."""
        if self._check_command("termux-clipboard-get"):
            res = self._run_cmd(["termux-clipboard-get"], timeout=5)
            return {"success": res.returncode == 0, "text": res.stdout}
        return {"success": False, "message": "termux-clipboard-get not available"}

    def set_clipboard(self, text: str) -> Dict[str, Any]:
        """Copies text to system clipboard."""
        if self._check_command("termux-clipboard-set"):
            res = self._run_cmd(["termux-clipboard-set", text], timeout=5)
            return {"success": res.returncode == 0}
        return {"success": False, "message": "termux-clipboard-set not available"}

    def open_url(self, url: str) -> Dict[str, Any]:
        """Opens a validated URL or app intent in the browser or default app."""
        if not url or not isinstance(url, str):
            return {"success": False, "error": "Invalid URL"}
        
        url_clean = url.strip()
        allowed_schemes = ("http://", "https://", "tel:", "sms:", "mailto:", "geo:", "market://")
        if not any(url_clean.startswith(s) for s in allowed_schemes):
            return {"success": False, "error": f"Disallowed URL scheme in: {url_clean[:30]}"}

        cmd = "termux-open-url" if self._check_command("termux-open-url") else "termux-open"
        if self._check_command(cmd):
            res = self._run_cmd([cmd, url_clean], timeout=8)
            return {"success": res.returncode == 0, "url": url_clean}
        return {"success": False, "message": f"{cmd} not available"}

    def get_wifi_info(self) -> Dict[str, Any]:
        """Returns current Wi-Fi connection info."""
        if self._check_command("termux-wifi-connectioninfo"):
            res = self._run_cmd(["termux-wifi-connectioninfo"], timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                try:
                    return {"success": True, "info": json.loads(res.stdout)}
                except Exception:
                    return {"success": True, "raw": res.stdout.strip()}
        return {"success": False, "message": "termux-wifi-connectioninfo not available"}

    def take_photo(self, output_path: str = "", camera_id: int = 0) -> Dict[str, Any]:
        """Captures a photo using the device camera within approved directory."""
        if not self._check_command("termux-camera-photo"):
            return {"success": False, "message": "termux-camera-photo not available"}

        if not output_path:
            output_path = str(self.base_dir / "latest_camera.jpg")
        else:
            # Validate path traversal
            target = Path(output_path).resolve()
            if not (str(target).startswith(str(self.base_dir)) or str(target).startswith(str(Path.home()))):
                return {"success": False, "error": "Access denied: output path outside allowed directories."}
            output_path = str(target)

        res = self._run_cmd(["termux-camera-photo", "-c", str(camera_id), output_path], timeout=15)
        if res.returncode == 0 and os.path.exists(output_path):
            return {"success": True, "path": output_path}
        return {"success": False, "error": res.stderr.strip() or "Camera capture failed"}

    def get_system_summary(self) -> Dict[str, Any]:
        """Provides a complete system health overview (storage, load, battery, memory)."""
        summary = {
            "battery": self.get_battery_status(),
            "cwd": os.getcwd(),
            "user": os.getenv("USER", "termux_user"),
        }
        
        # Disk usage
        try:
            total, used, free = shutil.disk_usage("/")
            summary["storage"] = {
                "total_gb": round(total / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2)
            }
        except Exception:
            pass

        return summary

    def execute_shell(self, command: str, timeout: int = 15) -> Dict[str, Any]:
        """
        Executes a validated shell command inside Termux and returns output.
        Protects against command injection, dangerous metacharacters, and runaway processes.
        """
        if not command or not command.strip():
            return {"success": False, "error": "Command cannot be empty"}

        allow_unsafe = os.getenv("ALLOW_UNSAFE_SHELL", "false").lower() in ("true", "1")

        # Prohibit destructive command tokens
        dangerous_patterns = [
            "rm -rf /", "rm -rf ~", ":(){ :|:& };:", "mkfs", "dd if=/dev/zero",
            "> /dev/sd", "> /dev/block"
        ]
        for pattern in dangerous_patterns:
            if pattern in command:
                return {"success": False, "error": f"Command execution blocked: Prohibited dangerous command pattern detected: {pattern}"}

        # Check for command chaining and injection metacharacters
        forbidden_tokens = [";", "&&", "||", "|", "`", "$(", "<", ">"]
        if not allow_unsafe:
            for token in forbidden_tokens:
                if token in command:
                    return {
                        "success": False,
                        "error": f"Command execution blocked: metacharacter '{token}' disallowed for security. Set ALLOW_UNSAFE_SHELL=true to override."
                    }

        try:
            # Parse into arguments array safely without shell=True
            args = shlex.split(command)
            if not args:
                return {"success": False, "error": "Empty parsed command"}
            args = [os.path.expanduser(a) for a in args]

            # Resolve executable
            executable = shutil.which(args[0])
            if not executable and not allow_unsafe:
                return {"success": False, "error": f"Executable '{args[0]}' not found in system PATH"}

            res = subprocess.run(
                args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            # Limit output to 200KB to prevent memory exhaustion
            max_out = 200000
            stdout_clean = res.stdout[:max_out] if res.stdout else ""
            stderr_clean = res.stderr[:max_out] if res.stderr else ""

            return {
                "success": res.returncode == 0,
                "stdout": stdout_clean,
                "stderr": stderr_clean,
                "exit_code": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"success": False, "error": f"Execution error: {str(e)}"}

    def announce_incoming_call(self, caller_name: str, phone: str = "", user_name: str = "Ram Binay") -> Dict[str, Any]:
        """Announces an incoming phone call via TTS and posts notification."""
        speech = f"{user_name}, {caller_name} का फोन आया है"
        self.speak(speech)
        self.send_notification(
            title=f"Incoming Call: {caller_name}",
            content=f"Number: {phone} - Voice Call Announcement"
        )
        return {
            "success": True,
            "announced": speech,
            "caller": caller_name,
            "phone": phone
        }

# Global singleton
automation = TermuxAutomation()
