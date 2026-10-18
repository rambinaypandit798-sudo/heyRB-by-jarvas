/**
 * Live Internet Search & Real-Time Grounding Service
 * Provides real-time factual web searches, query classification,
 * and citation formatting for RB Agent.
 */

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
}

const REALTIME_KEYWORDS = [
  "latest", "current", "news", "today", "tonight", "yesterday", "tomorrow",
  "price", "pricing", "live", "update", "updates", "release", "version",
  "score", "match", "weather", "stock", "crypto", "bitcoin", "rate",
  "now", "recently", "newest", "who is the current", "who is", "what happened",
  "who won", "2026", "2025", "search", "google", "browse", "find online"
];

const HINDI_REALTIME_KEYWORDS = [
  "सर्च", "खोजो", "ढूंढो", "पता करो", "आज", "ताज़ा", "लेटेस्ट", "अपडेट", "दाम", "भाव", "मौसम"
];

/**
 * Detects whether a user prompt requires real-time live internet grounding.
 */
export function isLiveInformationQuery(query: string): boolean {
  if (!query) return false;
  const lower = query.toLowerCase();

  for (const kw of REALTIME_KEYWORDS) {
    // Word boundary or exact match
    const regex = new RegExp(`\\b${kw}\\b`, "i");
    if (regex.test(lower)) return true;
  }

  for (const kw of HINDI_REALTIME_KEYWORDS) {
    if (lower.includes(kw)) return true;
  }

  return false;
}

/**
 * Performs live real-time web search via DuckDuckGo HTML engine.
 */
export async function searchLiveWeb(query: string, maxResults: number = 5): Promise<SearchResult[]> {
  const cleanQuery = query.replace(/[^\w\s\u0900-\u097F\-]/g, " ").trim();
  if (!cleanQuery) return [];

  try {
    const res = await fetch(`https://html.duckduckgo.com/html/?q=${encodeURIComponent(cleanQuery)}`, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
      },
      signal: AbortSignal.timeout(8000)
    });

    if (!res.ok) {
      console.warn("Live web search returned HTTP", res.status);
      return [];
    }

    const html = await res.text();
    const results: SearchResult[] = [];
    const seenUrls = new Set<string>();

    const blocks = html.split('<div class="result results_links');
    for (const block of blocks.slice(1)) {
      const titleMatch = block.match(/class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/);
      const snippetMatch = block.match(/class="result__snippet"[^>]*>([\s\S]*?)<\/a>/);

      if (titleMatch && titleMatch[1] && titleMatch[2]) {
        const rawUrl = titleMatch[1];
        const uddg = rawUrl.match(/uddg=([^&]+)/);
        const url = uddg && uddg[1] ? decodeURIComponent(uddg[1]) : rawUrl;
        
        if (!url || !url.startsWith("http") || seenUrls.has(url)) continue;
        seenUrls.add(url);

        const title = titleMatch[2]
          .replace(/<[^>]+>/g, "")
          .replace(/&#x27;/g, "'")
          .replace(/&amp;/g, "&")
          .replace(/&quot;/g, '"')
          .trim();

        const snippet = (snippetMatch && snippetMatch[1])
          ? snippetMatch[1]
              .replace(/<[^>]+>/g, "")
              .replace(/&#x27;/g, "'")
              .replace(/&amp;/g, "&")
              .replace(/&quot;/g, '"')
              .trim()
          : "";

        results.push({ title, url, snippet });
      }

      if (results.length >= maxResults) break;
    }

    return results;
  } catch (error) {
    console.error("Live web search failed:", error);
    return [];
  }
}

/**
 * Formats live search results into a clean factual grounding block for system prompt.
 */
export function formatSearchGroundingContext(results: SearchResult[]): string {
  if (!results.length) return "";

  const facts = results
    .map((r, i) => `[Source ${i + 1}] Title: ${r.title}\nURL: ${r.url}\nSummary: ${r.snippet}`)
    .join("\n\n");

  return `[REAL-TIME LIVE SEARCH GROUNDING DATA - OCTOBER 2026]
The following up-to-date factual information was retrieved LIVE from web search:

${facts}

GROUNDING DIRECTIVE:
• You MUST use the live data above to answer the user's inquiry accurately.
• Do not claim knowledge cutoffs or rely on outdated pre-trained assumptions when answering this query.
• You MUST append a clean markdown "Sources & References" list at the very end of your response with the source titles and markdown links to the verified URLs.`;
}

/**
 * Formats a clean list of citations.
 */
export function formatSourceCitations(results: SearchResult[]): string {
  if (!results.length) return "";
  const list = results
    .map((r) => `• [${r.title}](${r.url})`)
    .join("\n");
  return `\n\n### 🌐 Sources & References\n${list}`;
}
