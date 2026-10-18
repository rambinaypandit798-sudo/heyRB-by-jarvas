"""
RB.AI - Custom 5 Sub-Agents Engine
Real, working logic for:
1. Research & Web Agent (Live HTTP web search)
2. Memory & Notes Agent (NLP intent parsing for 'यह चीज़ सेव कर लो', SQLite persistence)
3. Preview / View Agent (Live web URL scraping & Markdown inspection)
4. Automation Agent (Hardware control, Platform channels, Call announcements)
5. Coding & GitHub Agent (Script execution & GitHub REST API repo sync)
"""

import re
import sys
import json
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional
from core.database import db
from core.automation import automation

import ipaddress
import socket

class SubAgentsEngine:
    def __init__(self):
        pass

    def _is_safe_url(self, url: str) -> bool:
        """Validates that a URL does not target loopback or private network addresses (SSRF Protection)."""
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            host = parsed.hostname.lower() if parsed.hostname else ""
            if not host or host in ("localhost", "::1"):
                return False
            try:
                ip = ipaddress.ip_address(host)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                    return False
            except ValueError:
                try:
                    resolved_ip = socket.gethostbyname(host)
                    ip = ipaddress.ip_address(resolved_ip)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                        return False
                except Exception:
                    pass
            return True
        except Exception:
            return False

    # =========================================================================
    # 1. RESEARCH & WEB AGENT
    # =========================================================================
    def run_web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Executes a real-time web search using DuckDuckGo HTML/Instant API
        for live data gathering (e.g. latest Gemini models, news, tech specs).
        """
        if not query:
            return {"success": False, "error": "Query cannot be empty"}

        results = []
        try:
            # First attempt: DuckDuckGo Instant Answer API
            encoded_query = urllib.parse.quote_plus(query)
            api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                abstract = data.get("AbstractText", "")
                abstract_source = data.get("AbstractSource", "")
                abstract_url = data.get("AbstractURL", "")

                if abstract:
                    results.append({
                        "title": f"DuckDuckGo Instant Answer ({abstract_source})",
                        "snippet": abstract,
                        "url": abstract_url
                    })

                for topic in data.get("RelatedTopics", []):
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append({
                            "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                            "snippet": topic.get("Text"),
                            "url": topic.get("FirstURL")
                        })
                    if len(results) >= max_results:
                        break

            # Fallback / Supplemental: DuckDuckGo HTML scrape if instant answer is sparse
            if len(results) < 2:
                html_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                html_req = urllib.request.Request(
                    html_url,
                    headers={"User-Agent": "Mozilla/5.0 (Android; Mobile; rv:109.0) Gecko/119.0 Firefox/119.0"}
                )
                with urllib.request.urlopen(html_req, timeout=12) as html_resp:
                    html_content = html_resp.read().decode("utf-8", errors="ignore")
                    
                    # Regex extraction for search results
                    matches = re.findall(
                        r'<a class="result__url" href="([^"]+)".*?<a class="result__snippet[^"]*"[^>]*>(.*?)</a>',
                        html_content,
                        re.DOTALL
                    )
                    for raw_url, raw_snip in matches[:max_results]:
                        clean_url = urllib.parse.unquote(raw_url.replace("//duckduckgo.com/l/?uddg=", "").split("&")[0])
                        clean_snip = re.sub(r'<[^>]+>', '', raw_snip).strip()
                        if clean_url.startswith("http") and clean_snip:
                            results.append({
                                "title": f"Result for {query[:30]}",
                                "snippet": clean_snip,
                                "url": clean_url
                            })
                            if len(results) >= max_results:
                                break

            return {
                "success": True,
                "agent": "Research & Web Agent",
                "query": query,
                "count": len(results),
                "results": results or [{"title": query, "snippet": f"Searched web for '{query}'. Live connection established.", "url": f"https://www.google.com/search?q={encoded_query}"}]
            }
        except Exception as e:
            # Fallback search link
            return {
                "success": True,
                "agent": "Research & Web Agent",
                "query": query,
                "results": [{
                    "title": f"Live Web Search for '{query}'",
                    "snippet": f"Direct link to live web results for query: {query}",
                    "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
                }],
                "warning": str(e)
            }

    # =========================================================================
    # 2. MEMORY & NOTES AGENT
    # =========================================================================
    def process_memory_intent(self, text: str) -> Dict[str, Any]:
        """
        Parses text for memory/save intents:
        Detects Hindi: "यह चीज़ सेव कर लो", "याद रखना", "नोट कर लो"
        Detects English: "remember this", "save note", "save this", "store note"
        Automatically persists into local SQLite database.
        """
        lower = text.lower().strip()
        
        # Save triggers
        triggers = [
            "यह चीज़ सेव कर लो", "यह चीज सेव कर लो", "इसे सेव कर लो", "सेव कर लो",
            "नोट कर लो", "याद रखना", "याद रखो",
            "remember this", "save note", "save this", "store this", "take a note",
            "note down", "add to notes", "create note"
        ]

        is_save_intent = any(trigger in lower for trigger in triggers)
        
        if is_save_intent:
            cleaned_content = text
            for trigger in triggers:
                # Remove trigger phrase from content
                pattern = re.compile(re.escape(trigger), re.IGNORECASE)
                cleaned_content = pattern.sub("", cleaned_content).strip()

            # Remove leading colons or hyphens
            cleaned_content = re.sub(r"^[:\-—, ]+", "", cleaned_content).strip()
            
            title = cleaned_content.split("\n")[0][:40] if cleaned_content else "Quick Note"
            if not title:
                title = "Note from Voice"
            
            note_id = db.add_note(title=title, content=cleaned_content or text, tags="auto-parsed")
            
            return {
                "is_memory_intent": True,
                "action": "saved",
                "note_id": note_id,
                "title": title,
                "content": cleaned_content or text,
                "message": f"सफलतापूर्वक सेव कर लिया गया (Note #{note_id}): '{title}'"
            }

        # Check retrieval triggers: "मेरे नोट्स दिखाओ", "show my notes", "get notes"
        if any(w in lower for w in ["मेरे नोट्स", "नोट्स दिखाओ", "show notes", "get notes", "list notes"]):
            notes = db.get_notes()
            return {
                "is_memory_intent": True,
                "action": "list",
                "count": len(notes),
                "notes": notes,
                "message": f"आपके पास कुल {len(notes)} नोट्स सुरक्षित हैं।"
            }

        return {"is_memory_intent": False}

    # =========================================================================
    # 3. PREVIEW / VIEW AGENT
    # =========================================================================
    def preview_url_or_markdown(self, target: str) -> Dict[str, Any]:
        """
        Live web content scraper and Markdown renderer engine for code and content previews.
        """
        target = target.strip()
        if target.startswith("http://") or target.startswith("https://"):
            if not self._is_safe_url(target):
                return {
                    "success": False,
                    "type": "web_url",
                    "url": target,
                    "error": "URL blocked: Access to local or private network addresses is restricted (SSRF protection)."
                }
            try:
                req = urllib.request.Request(
                    target,
                    headers={"User-Agent": "Mozilla/5.0 (Android; Mobile; RB-Agent/2.0)"}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = resp.read(65536).decode("utf-8", errors="ignore")
                    
                    # Extract page title
                    title_match = re.search(r"<title>(.*?)</title>", raw, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else target
                    
                    # Strip tags for clean text preview
                    clean_text = re.sub(r"<script.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
                    clean_text = re.sub(r"<style.*?</style>", "", clean_text, flags=re.DOTALL | re.IGNORECASE)
                    clean_text = re.sub(r"<[^>]+>", " ", clean_text)
                    clean_text = " ".join(clean_text.split())[:600]

                    return {
                        "success": True,
                        "type": "web_url",
                        "url": target,
                        "title": title,
                        "preview_snippet": clean_text,
                        "status_code": resp.status
                    }
            except Exception as e:
                return {
                    "success": False,
                    "type": "web_url",
                    "url": target,
                    "error": f"Failed to load preview: {str(e)}"
                }
        else:
            # Markdown / Code text preview
            return {
                "success": True,
                "type": "markdown_code",
                "content": target,
                "length": len(target)
            }

    # =========================================================================
    # 4. AUTOMATION AGENT
    # =========================================================================
    def execute_device_automation(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Real-time device automation handlers using Termux platform API:
        torch, vibrate, battery, clipboard, shell, and call announcements.
        """
        if action == "torch":
            enabled = bool(params.get("enabled", True))
            return automation.set_torch(enabled)
        elif action == "vibrate":
            ms = int(params.get("duration", 300))
            return automation.vibrate(ms)
        elif action == "battery":
            return automation.get_battery_status()
        elif action == "clipboard_get":
            return automation.get_clipboard()
        elif action == "clipboard_set":
            return automation.set_clipboard(params.get("text", ""))
        elif action == "notify":
            return automation.send_notification(params.get("title", "RB Agent"), params.get("content", ""))
        elif action == "call_announcement":
            caller_name = params.get("caller_name", "")
            phone = params.get("phone", "")
            short_name = "Ram Binay"
            
            # Announce via TTS in Hindi/English
            if not caller_name or caller_name.lower() in ("unknown", "unknown caller"):
                speech = f"नमस्ते {short_name}, इनका फोन आया है"
            else:
                speech = f"नमस्ते {short_name}, {caller_name} का फोन आया है"
            automation.speak(speech)
            automation.send_notification(
                title=f"Incoming Call: {caller_name or 'Incoming'}",
                content=f"{speech} (Number: {phone})"
            )
            return {
                "success": True,
                "announced": speech,
                "caller": caller_name or "Unknown",
                "phone": phone
            }
        elif action == "shell":
            return automation.execute_shell(params.get("command", ""))
        return {"success": False, "error": f"Unknown automation action: {action}"}

    # =========================================================================
    # 5. CODING & GITHUB AGENT
    # =========================================================================
    def execute_code_or_github(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coding & GitHub Agent:
        1. Executes python / shell scripts in Termux sandbox.
        2. Connects to GitHub REST API with OAuth / Personal Token to fetch, sync, and display user repos.
        """
        if action == "exec_script":
            code = params.get("code", "")
            lang = params.get("lang", "python")
            if lang == "python":
                try:
                    res = subprocess.run(
                        [sys.executable, "-c", code],
                        shell=False,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    return {
                        "success": res.returncode == 0,
                        "stdout": res.stdout[:50000],
                        "stderr": res.stderr[:50000],
                        "returncode": res.returncode
                    }
                except subprocess.TimeoutExpired:
                    return {"success": False, "error": "Execution timed out (15s limit)"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            else:
                return automation.execute_shell(code)

        elif action == "fetch_github_repos":
            username = params.get("username", "")
            token = params.get("token") or db.get_integration("github").get("token", "")
            
            headers = {
                "User-Agent": "RB-Agent-Assistant",
                "Accept": "application/vnd.github.v3+json"
            }
            if token:
                headers["Authorization"] = f"token {token}"

            if not username and token:
                url = "https://api.github.com/user/repos?sort=updated&per_page=15"
            elif username:
                url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=15"
            else:
                return {"success": False, "error": "GitHub username or Personal Token required"}

            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp:
                    repos = json.loads(resp.read().decode("utf-8"))
                    repo_list = []
                    for r in repos:
                        repo_list.append({
                            "name": r.get("name"),
                            "full_name": r.get("full_name"),
                            "description": r.get("description") or "No description",
                            "stars": r.get("stargazers_count", 0),
                            "forks": r.get("forks_count", 0),
                            "language": r.get("language") or "Code",
                            "html_url": r.get("html_url"),
                            "updated_at": r.get("updated_at")
                        })
                    
                    if token:
                        db.save_integration("github", {"token": token, "username": username or "authenticated_user"})

                    return {
                        "success": True,
                        "count": len(repo_list),
                        "repositories": repo_list
                    }
            except urllib.error.HTTPError as e:
                return {"success": False, "error": f"GitHub API Error: {e.code} - {e.reason}"}
            except Exception as e:
                return {"success": False, "error": f"GitHub request failed: {str(e)}"}

        return {"success": False, "error": f"Unknown Coding & GitHub action: {action}"}

    # =========================================================================
    # AUTONOMOUS INTENT ROUTING (CORE ORCHESTRATOR)
    # =========================================================================
    def route_and_process_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Intelligently parses user input (typed or spoken) and routes to the appropriate sub-agent:
        - Memory & Notes: Save / Remember / Note down
        - Hardware & Automation: Torch, Battery, Vibrate, Call Announce
        - Research & Web: Live web searches & queries
        - Coding & GitHub: Repositories and script execution
        Returns clean, polished user responses hiding raw hardware/debug traces.
        """
        raw = text.strip()
        lower = raw.lower()
        if not lower:
            return None

        user_name = db.get_setting("user_name", "Ram Binay kumar Pandit")

        # 1. Memory & Notes Intent
        mem_triggers = [
            "यह चीज़ सेव कर लो", "यह चीज सेव कर लो", "इसे सेव कर लो", "सेव कर लो",
            "नोट कर लो", "याद रखना", "याद रखो",
            "remember this", "save note", "save this", "store this", "take a note",
            "note down", "add to notes", "create note"
        ]
        if any(trig in lower for trig in mem_triggers):
            res = self.process_memory_intent(raw)
            return {
                "routed": True,
                "agent": "Memory & Notes Agent",
                "tag": "memory",
                "response": res.get("message", "नोट सफलतापूर्वक सुरक्षित कर लिया गया है।")
            }

        # Notes Retrieval
        if any(trig in lower for trig in ["मेरे नोट्स", "नोट्स दिखाओ", "show my notes", "get notes", "list notes"]):
            notes = db.get_notes()
            if not notes:
                reply = f"{user_name}, वर्तमान में कोई सुरक्षित नोट मौजूद नहीं है।"
            else:
                formatted = [f"• #{n['id']} {n['title']}: {n['content']}" for n in notes[:5]]
                reply = f"📝 **आपके सुरक्षित नोट्स ({len(notes)} कुल):**\n" + "\n".join(formatted)
            return {
                "routed": True,
                "agent": "Memory & Notes Agent",
                "tag": "memory",
                "response": reply
            }

        # 2. Hardware & Automation Intent
        # Torch Toggle
        if any(w in lower for w in ["torch on", "turn on torch", "light on", "turn on flashlight", "flashlight on", "लाइट जलाओ", "टॉर्च चालू"]):
            automation.set_torch(True)
            return {
                "routed": True,
                "agent": "Automation Agent",
                "tag": "automation",
                "response": "🔦 टॉर्च चालू कर दी गई है (Flashlight turned ON)."
            }
        if any(w in lower for w in ["torch off", "turn off torch", "light off", "flashlight off", "लाइट बंद", "टॉर्च बंद"]):
            automation.set_torch(False)
            return {
                "routed": True,
                "agent": "Automation Agent",
                "tag": "automation",
                "response": "🔦 टॉर्च बंद कर दी गई है (Flashlight turned OFF)."
            }

        # Battery Status
        if any(w in lower for w in ["battery", "battery status", "बैटरी", "कितना चार्ज है", "charging status"]):
            batt = automation.get_battery_status()
            if batt.get("available"):
                pct = batt.get("percentage", 85)
                status = batt.get("status", "Discharging")
                temp = batt.get("temperature", "Normal")
                reply = f"🔋 **बैटरी स्थिति:** {pct}% ({status}) | तापमान: {temp}°C"
            else:
                reply = f"🔋 **बैटरी स्थिति:** डिवाइस सामान्य रूप से एक्टिव है।"
            return {
                "routed": True,
                "agent": "Automation Agent",
                "tag": "automation",
                "response": reply
            }

        # Device Vibration
        if any(w in lower for w in ["vibrate", "वाइब्रेट", "vibrate phone", "haptic test"]):
            automation.vibrate(300)
            return {
                "routed": True,
                "agent": "Automation Agent",
                "tag": "automation",
                "response": "📳 हेप्टिक वाइब्रेशन सफलतापूर्वक ट्रिगर हुआ।"
            }

        # Call Announcement
        if any(w in lower for w in ["call announce", "call announcement", "कॉल अनाउंस", "फोन आया"]):
            caller = ""
            match = re.search(r"(?:from|of|का फोन|कॉल)\s+([a-zA-Z\u0900-\u097F\s]+)", raw, re.IGNORECASE)
            if match and match.group(1).strip():
                caller = match.group(1).strip()
            call_res = self.execute_device_automation("call_announcement", {"caller_name": caller})
            return {
                "routed": True,
                "agent": "Automation Agent",
                "tag": "automation",
                "response": f"📞 कॉल अनाउंसमेंट: \"{call_res.get('announced')}\""
            }

        # 3. Research & Web Intent
        web_match = re.match(r"^(?:search(?:\s+web)?|google|look up|खोजो|सर्च करो)\s+(.+)", raw, re.IGNORECASE)
        if web_match:
            query = web_match.group(1).strip()
            search_res = self.run_web_search(query, max_results=3)
            items = search_res.get("results", [])
            if items:
                snippets = [f"• **{it['title']}**: {it['snippet'][:180]}..." for it in items[:3]]
                reply = f"🌐 **वेब सर्च परिणाम ({query}):**\n\n" + "\n\n".join(snippets)
            else:
                reply = f"🌐 वेब पर '{query}' के लिए लाइव सर्च पूरा हुआ।"
            return {
                "routed": True,
                "agent": "Research & Web Agent",
                "tag": "research",
                "response": reply
            }

        # 4. Coding & GitHub Intent
        gh_match = re.search(r"(?:github\s+repos?|fetch\s+repos?|repos?\s+of)\s+([a-zA-Z0-9_\-]+)", raw, re.IGNORECASE)
        if gh_match:
            target_user = gh_match.group(1).strip()
            gh_res = self.execute_code_or_github("fetch_github_repos", {"username": target_user})
            repos = gh_res.get("repositories", [])
            if repos:
                lines = [f"• **{r['name']}** ({r['language']}): ⭐ {r['stars']} | [View]({r['html_url']})" for r in repos[:5]]
                reply = f"💻 **GitHub रिपॉजिटरीज़ ({target_user}):**\n" + "\n".join(lines)
            else:
                reply = f"💻 GitHub पर '{target_user}' के लिए कोई सार्वजनिक रिपॉजिटरी नहीं मिली या दर सीमा पार हो गई।"
            return {
                "routed": True,
                "agent": "Coding & GitHub Agent",
                "tag": "coding",
                "response": reply
            }

        return None

# Global singleton
sub_agents = SubAgentsEngine()
