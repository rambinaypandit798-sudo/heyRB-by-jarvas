"""
Web Search and External Research Service for RB Agent OS.
Provides online factual retrieval using lightweight HTTP querying.
"""

import httpx
from typing import Any, Dict, List
import urllib.parse
import re

class WebSearchTool:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        }

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Performs search query via DuckDuckGo lite/instant API with graceful fallback."""
        if not query or not query.strip():
            return {"status": "error", "error": "Query cannot be empty", "results": []}

        try:
            # 1. Try DuckDuckGo Instant Answer API
            encoded = urllib.parse.quote(query)
            api_url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
            
            with httpx.Client(timeout=8.0, headers=self.headers, follow_redirects=True) as client:
                res = client.get(api_url)
                if res.status_code == 200:
                    data = res.json()
                    abstract = data.get("AbstractText", "")
                    heading = data.get("Heading", "")
                    related = data.get("RelatedTopics", [])
                    
                    results = []
                    if abstract:
                        results.append({
                            "title": heading or query,
                            "snippet": abstract,
                            "url": data.get("AbstractURL", "")
                        })

                    for item in related[:max_results]:
                        if isinstance(item, dict) and "Text" in item:
                            results.append({
                                "title": item.get("FirstURL", "").split("/")[-1].replace("_", " "),
                                "snippet": item.get("Text", ""),
                                "url": item.get("FirstURL", "")
                            })

                    if results:
                        return {
                            "status": "success",
                            "query": query,
                            "results": results,
                            "verified": True
                        }

            # 2. Fallback to DuckDuckGo HTML search
            html_url = f"https://html.duckduckgo.com/html/?q={encoded}"
            with httpx.Client(timeout=8.0, headers=self.headers, follow_redirects=True) as client:
                res = client.get(html_url)
                if res.status_code == 200:
                    # Simple extraction of snippets and titles
                    snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', res.text, re.DOTALL)
                    titles = re.findall(r'<a class="result__url"[^>]*>(.*?)</a>', res.text, re.DOTALL)
                    
                    results = []
                    for i in range(min(len(snippets), max_results)):
                        clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                        clean_title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else f"Result {i+1}"
                        results.append({
                            "title": clean_title,
                            "snippet": clean_snippet,
                            "url": ""
                        })

                    return {
                        "status": "success",
                        "query": query,
                        "results": results,
                        "verified": len(results) > 0
                    }

            return {
                "status": "warning",
                "query": query,
                "results": [],
                "message": "No online search results found or network unreachable."
            }

        except Exception as e:
            return {
                "status": "error",
                "query": query,
                "error": f"Search request failed: {str(e)}",
                "verified": False,
                "results": []
            }

web_search_tool = WebSearchTool()
