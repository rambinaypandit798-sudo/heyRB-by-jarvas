"""
RB.AI - WhatsApp Integration Bridge
Enables WhatsApp message automation, direct URL scheme dispatching (wa.me),
and Android intent opening for hands-free messaging.
"""

import urllib.parse
from typing import Dict, Any
from core.automation import automation
from core.database import db

class WhatsAppBridge:
    def __init__(self):
        pass

    def create_whatsapp_link(self, phone_number: str, message: str) -> str:
        """
        Formats phone number and encodes message for https://wa.me/ URL scheme.
        """
        # Strip spaces, hyphens, plus signs
        clean_phone = "".join(filter(str.isdigit, phone_number))
        encoded_msg = urllib.parse.quote(message)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"

    def send_whatsapp_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Launches WhatsApp with pre-filled message via Termux open-url or returns payload.
        """
        if not phone_number:
            return {"success": False, "error": "Phone number is required"}

        link = self.create_whatsapp_link(phone_number, message)
        res = automation.open_url(link)
        
        return {
            "success": res.get("success", True),
            "phone": phone_number,
            "url": link,
            "message": message,
            "termux_action": res
        }

    def send_status_report(self, phone_number: str) -> Dict[str, Any]:
        """
        Generates and sends device status summary to WhatsApp contact.
        """
        user_name = db.get_setting("user_name", "Ram Binay")
        batt = automation.get_battery_status()
        report = (
            f"⚡ *RB Agent Status Report*\n"
            f"User: {user_name}\n"
            f"Battery: {batt.get('percentage', 'N/A')}% ({batt.get('status', 'N/A')})\n"
            f"Temperature: {batt.get('temperature', 'N/A')}°C\n"
            f"Health: {batt.get('health', 'N/A')}\n"
            f"Status: Device is active and operating normally."
        )
        return self.send_whatsapp_message(phone_number, report)

# Global singleton
whatsapp_bridge = WhatsAppBridge()
