"""
Android & Termux Integration Service for RB Agent OS.
Executes permitted device actions via Termux:API and Android Intents.
Transparently distinguishes Termux-local tools from companion integrations.
"""

import json
import shutil
import subprocess
from typing import Any, Dict, Optional

class AndroidTools:
    def __init__(self):
        # Check if termux-api CLI commands exist on the system path
        self.has_termux_api = shutil.which("termux-toast") is not None

    def termux_toast(self, message: str) -> Dict[str, Any]:
        """Displays a toast message on Android screen via Termux:API."""
        if not self.has_termux_api:
            return {
                "status": "unsupported",
                "verified": False,
                "error": "Termux:API binary not found. Install 'pkg install termux-api' and Termux:API app from F-Droid."
            }
        
        try:
            res = subprocess.run(
                ["termux-toast", message],
                capture_output=True,
                text=True,
                timeout=4,
                check=False
            )
            if res.returncode == 0:
                return {
                    "status": "success",
                    "verified": True,
                    "message": f"Toast displayed: '{message}'"
                }
            return {
                "status": "error",
                "verified": False,
                "error": f"termux-toast failed with code {res.returncode}: {res.stderr}"
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "verified": False,
                "error": "termux-toast timed out. Ensure Termux:API app is installed and granted background execution permissions."
            }
        except Exception as e:
            return {"status": "error", "verified": False, "error": str(e)}

    def termux_vibrate(self, duration_ms: int = 250) -> Dict[str, Any]:
        """Vibrates the Android phone for specified milliseconds."""
        if not self.has_termux_api:
            return {
                "status": "unsupported",
                "verified": False,
                "error": "Termux:API package not found."
            }
        
        try:
            res = subprocess.run(
                ["termux-vibrate", "-d", str(int(duration_ms))],
                capture_output=True,
                text=True,
                timeout=4,
                check=False
            )
            if res.returncode == 0:
                return {
                    "status": "success",
                    "verified": True,
                    "message": f"Device vibrated for {duration_ms}ms"
                }
            return {
                "status": "error",
                "verified": False,
                "error": f"termux-vibrate failed with code {res.returncode}: {res.stderr}"
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "verified": False,
                "error": "termux-vibrate timed out. Ensure Termux:API app is installed."
            }
        except Exception as e:
            return {"status": "error", "verified": False, "error": str(e)}

    def termux_battery_status(self) -> Dict[str, Any]:
        """Reads real Android battery status."""
        if not self.has_termux_api:
            return {
                "status": "unsupported",
                "verified": False,
                "error": "Termux:API package not found."
            }

        try:
            res = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                return {
                    "status": "success",
                    "verified": True,
                    "battery": data
                }
            return {
                "status": "error",
                "verified": False,
                "error": f"Failed to read battery status: {res.stderr or 'Empty output'}"
            }
        except subprocess.TimeoutExpired:
            # Actionable diagnostics when companion is not answering
            return {
                "status": "warning",
                "verified": False,
                "error": "termux-battery-status timed out. Please ensure Termux:API APK is installed with battery permissions granted."
            }
        except Exception as e:
            return {"status": "error", "verified": False, "error": str(e)}

    def android_open_intent(self, uri: str) -> Dict[str, Any]:
        """
        Dispatches an Android intent / URL via termux-open-url or am start.
        Requires user confirmation if called autonomously.
        """
        if not uri:
            return {"status": "error", "verified": False, "error": "URI cannot be empty"}

        # Validate URI schemes
        allowed_schemes = ("http://", "https://", "tel:", "sms:", "mailto:", "geo:", "market://")
        if not any(uri.startswith(scheme) for scheme in allowed_schemes):
            return {
                "status": "error",
                "verified": False,
                "error": f"Unsupported or dangerous URI scheme in '{uri}'"
            }

        # Check for termux-open-url
        if shutil.which("termux-open-url"):
            try:
                res = subprocess.run(
                    ["termux-open-url", uri],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if res.returncode == 0:
                    return {
                        "status": "success",
                        "verified": True,
                        "action": "open_url",
                        "uri": uri,
                        "message": f"Successfully launched intent for {uri}"
                    }
            except Exception as e:
                pass

        # Try am start (Android Activity Manager)
        if shutil.which("am"):
            try:
                res = subprocess.run(
                    ["am", "start", "-a", "android.intent.action.VIEW", "-d", uri],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if res.returncode == 0:
                    return {
                        "status": "success",
                        "verified": True,
                        "action": "am_start",
                        "uri": uri,
                        "message": f"Dispatched Android intent {uri}"
                    }
            except Exception:
                pass

        return {
            "status": "browser_intent_fallback",
            "verified": False,
            "action": "client_dispatch_needed",
            "uri": uri,
            "message": f"Command dispatched to client browser for deep link: {uri}"
        }

    def get_permission_status(self) -> Dict[str, Any]:
        """Reports system and Android integration permissions."""
        return {
            "termux_api_installed": self.has_termux_api,
            "termux_battery_available": shutil.which("termux-battery-status") is not None,
            "termux_toast_available": shutil.which("termux-toast") is not None,
            "termux_vibrate_available": shutil.which("termux-vibrate") is not None,
            "android_activity_manager_available": shutil.which("am") is not None,
            "companion_mode": "PWA_with_Termux_Bridge"
        }

android_tools = AndroidTools()
