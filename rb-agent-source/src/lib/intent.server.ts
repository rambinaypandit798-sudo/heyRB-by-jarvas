import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export interface IntentAction {
  type: "youtube" | "spotify" | "url" | "custom";
  query?: string;
  url: string;
  fallbackUrl: string;
  actionText: string;
}

export function parseIntentFromQuery(text: string): IntentAction | null {
  const clean = text.trim();

  // YouTube match: "open youtube and play [song]", "play [song] on youtube", "search youtube for [song]"
  const ytMatch =
    clean.match(/^(?:please\s+)?(?:open\s+(?:youtube|yt)\s+(?:and\s+)?(?:play|search for|find)\s+|play\s+(.+?)\s+on\s+(?:youtube|yt)|open\s+(?:youtube|yt)\s+for\s+)(.+)$/i) ||
    clean.match(/^(?:play|listen to)\s+(.+?)\s+(?:on\s+youtube|via\s+youtube)$/i) ||
    clean.match(/^(?:youtube|yt)\s+(?:pe\s+)?(?:play\s+|chalao\s+|bajao\s+)(.+)$/i);

  if (ytMatch) {
    const rawSong = ytMatch[1] || ytMatch[2] || "";
    const song = rawSong.replace(/^(song|music|video|track)\s+/i, "").trim();
    const encoded = encodeURIComponent(song);
    return {
      type: "youtube",
      query: song,
      url: `vnd.youtube://results?search_query=${encoded}`,
      fallbackUrl: `https://www.youtube.com/results?search_query=${encoded}`,
      actionText: `Open YouTube & play "${song}"`,
    };
  }

  // Spotify match: "open spotify and play [song]", "play [song] on spotify"
  const spotifyMatch =
    clean.match(/^(?:please\s+)?(?:open\s+spotify\s+(?:and\s+)?(?:play|search for)\s+|play\s+(.+?)\s+on\s+spotify)(.+)?$/i);

  if (spotifyMatch) {
    const song = (spotifyMatch[1] || spotifyMatch[2] || "").trim();
    const encoded = encodeURIComponent(song);
    return {
      type: "spotify",
      query: song,
      url: `spotify:search:${encoded}`,
      fallbackUrl: `https://open.spotify.com/search/${encoded}`,
      actionText: `Open Spotify & play "${song}"`,
    };
  }

  // Generic direct URL
  const urlMatch = clean.match(/^(?:open\s+url|browse\s+to|navigate\s+to)\s+(https?:\/\/[^\s]+)$/i);
  if (urlMatch) {
    const targetUrl = urlMatch[1];
    return {
      type: "url",
      url: targetUrl,
      fallbackUrl: targetUrl,
      actionText: `Open ${targetUrl}`,
    };
  }

  return null;
}

export async function launchAndroidIntent(
  intent: IntentAction
): Promise<{ success: boolean; method: string; detail?: string }> {
  const candidateCommands = [
    // 1. Direct Termux open URL helper
    `termux-open-url "${intent.fallbackUrl}" 2>/dev/null`,
    // 2. Android am start intent with custom scheme or URL
    `am start -a android.intent.action.VIEW -d "${intent.fallbackUrl}" 2>/dev/null`,
    `am start -a android.intent.action.VIEW -d "${intent.url}" 2>/dev/null`,
    // 3. xdg-open fallback
    `xdg-open "${intent.fallbackUrl}" 2>/dev/null`,
  ];

  for (const cmd of candidateCommands) {
    try {
      await execAsync(cmd, { timeout: 3000 });
      return { success: true, method: cmd.split(" ")[0] };
    } catch {
      // Try next candidate
    }
  }

  return { success: false, method: "fallback-browser", detail: intent.fallbackUrl };
}
