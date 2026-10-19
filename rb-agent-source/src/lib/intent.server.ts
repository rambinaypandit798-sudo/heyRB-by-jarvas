import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export interface IntentAction {
  type:
    | "youtube"
    | "spotify"
    | "whatsapp"
    | "settings"
    | "camera"
    | "dialer"
    | "clock"
    | "calculator"
    | "gallery"
    | "url"
    | "custom";
  package?: string;
  action?: string;
  query?: string;
  url: string;
  fallbackUrl: string;
  actionText: string;
  appName: string;
  settingType?: "wifi" | "bluetooth" | "display" | "sound" | "main";
  spokenConfirmation?: string;
}

/**
 * Strict Multilingual Intent Parser for Android Apps and Device Settings.
 * Correctly matches English & Hindi app launch and media triggers:
 * - "YouTube खोलो", "open YouTube", "open YouTube and play [song]"
 * - "Spotify खोलो", "open Spotify and play [song]"
 * - "WhatsApp खोलो", "Settings खोलो", "Camera खोलो"
 * - "WiFi खोलो", "Bluetooth खोलो", "Sound settings खोलो"
 */
export function parseIntentFromQuery(rawText: string): IntentAction | null {
  const clean = rawText.trim().replace(/[.,!?;:]+$/, "");
  const defaultConfirmation = "हाँ, यह कर दिया है";

  // 1. YouTube: Just Open App ("YouTube खोलो", "open youtube", "launch youtube", "youtube chalu karo")
  if (
    /^(?:please\s+)?(?:open|launch|start)\s+(?:the\s+)?(?:youtube|yt)(?:\s+app)?$/i.test(clean) ||
    /^(?:youtube|yt)\s*(?:खोलो|खोलें|ओपन\s*करो|kholo|chalu\s*karo|start\s*karo)$/i.test(clean) ||
    /^(?:खोलो|खोलें|kholo)\s+(?:youtube|yt)$/i.test(clean)
  ) {
    return {
      type: "youtube",
      appName: "YouTube",
      package: "com.google.android.youtube",
      action: "android.intent.action.MAIN",
      url: "vnd.youtube://",
      fallbackUrl: "https://www.youtube.com",
      actionText: "Opening YouTube app directly",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 2. YouTube: Play or Search Song / Video
  const ytPlayMatch =
    clean.match(/^(?:please\s+)?(?:open\s+(?:youtube|yt)\s+(?:and\s+)?(?:play|search|find)|play\s+(.+?)\s+on\s+(?:youtube|yt)|open\s+(?:youtube|yt)\s+for\s+)(.+)$/i) ||
    clean.match(/^(?:play|listen to)\s+(.+?)\s+(?:on\s+youtube|via\s+youtube)$/i) ||
    clean.match(/^(?:youtube|yt)\s+(?:pe|par|me|mein)\s+(?:play\s+|chalao\s+|bajao\s+|search\s+)(.+)$/i) ||
    clean.match(/^(?:youtube|yt)\s+(?:kholo\s+aur\s+play\s+karo|खोलो\s+और\s+चलाओ|खोलो\s+और\s+बजाओ)\s+(.+)$/i) ||
    clean.match(/^(?:youtube|yt)\s+(?:par|pe)\s+(.+?)\s*(?:chalao|bajao|play\s*karo|चलाओ|बजाओ)$/i);

  if (ytPlayMatch) {
    const rawSong = ytPlayMatch[1] || ytPlayMatch[2] || "";
    const song = rawSong.replace(/^(song|music|video|track|गाना)\s+/i, "").trim();
    if (song.length > 0) {
      const encoded = encodeURIComponent(song);
      return {
        type: "youtube",
        appName: "YouTube",
        package: "com.google.android.youtube",
        query: song,
        url: `vnd.youtube://results?search_query=${encoded}`,
        fallbackUrl: `https://www.youtube.com/results?search_query=${encoded}`,
        actionText: `Opening YouTube app to play "${song}"`,
        spokenConfirmation: defaultConfirmation,
      };
    }
  }

  // 3. Spotify: Just Open App
  if (
    /^(?:please\s+)?(?:open|launch|start)\s+(?:the\s+)?spotify(?:\s+app)?$/i.test(clean) ||
    /^spotify\s*(?:खोलो|खोलें|ओपन\s*करो|kholo|chalu\s*karo)$/i.test(clean) ||
    /^(?:खोलो|kholo)\s+spotify$/i.test(clean)
  ) {
    return {
      type: "spotify",
      appName: "Spotify",
      package: "com.spotify.music",
      action: "android.intent.action.MAIN",
      url: "spotify:",
      fallbackUrl: "https://open.spotify.com",
      actionText: "Opening Spotify app directly",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 4. Spotify: Play Song
  const spotifyMatch =
    clean.match(/^(?:please\s+)?(?:open\s+spotify\s+(?:and\s+)?(?:play|search for)\s+|play\s+(.+?)\s+on\s+spotify)(.+)?$/i) ||
    clean.match(/^spotify\s+(?:pe|par)\s+(?:play\s+|chalao\s+|bajao\s+)(.+)$/i);

  if (spotifyMatch) {
    const song = (spotifyMatch[1] || spotifyMatch[2] || "").trim();
    if (song.length > 0) {
      const encoded = encodeURIComponent(song);
      return {
        type: "spotify",
        appName: "Spotify",
        package: "com.spotify.music",
        query: song,
        url: `spotify:search:${encoded}`,
        fallbackUrl: `https://open.spotify.com/search/${encoded}`,
        actionText: `Opening Spotify app to play "${song}"`,
        spokenConfirmation: defaultConfirmation,
      };
    }
  }

  // 5. WhatsApp: Open App
  if (
    /^(?:please\s+)?(?:open|launch)\s+whatsapp(?:\s+app)?$/i.test(clean) ||
    /^whatsapp\s*(?:खोलो|खोलें|ओपन\s*करो|kholo)$/i.test(clean) ||
    /^(?:खोलो|kholo)\s+whatsapp$/i.test(clean)
  ) {
    return {
      type: "whatsapp",
      appName: "WhatsApp",
      package: "com.whatsapp",
      action: "android.intent.action.MAIN",
      url: "whatsapp://",
      fallbackUrl: "https://web.whatsapp.com",
      actionText: "Opening WhatsApp directly",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 6. Specific Device Settings (Wi-Fi, Bluetooth, Display, Sound)
  if (/(?:open|launch)\s+(?:wifi|wi-fi)(?:\s+settings)?$/i.test(clean) || /(?:wifi|wi-fi)\s*(?:खोलो|kholo)$/i.test(clean)) {
    return {
      type: "settings",
      appName: "Wi-Fi Settings",
      action: "android.settings.WIFI_SETTINGS",
      settingType: "wifi",
      url: "intent:#Intent;action=android.settings.WIFI_SETTINGS;end",
      fallbackUrl: "",
      actionText: "Opening Wi-Fi Settings",
      spokenConfirmation: defaultConfirmation,
    };
  }

  if (/(?:open|launch)\s+bluetooth(?:\s+settings)?$/i.test(clean) || /bluetooth\s*(?:खोलो|kholo)$/i.test(clean)) {
    return {
      type: "settings",
      appName: "Bluetooth Settings",
      action: "android.settings.BLUETOOTH_SETTINGS",
      settingType: "bluetooth",
      url: "intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end",
      fallbackUrl: "",
      actionText: "Opening Bluetooth Settings",
      spokenConfirmation: defaultConfirmation,
    };
  }

  if (/(?:open|launch)\s+sound(?:\s+settings)?$/i.test(clean) || /sound\s*(?:settings\s*)?(?:खोलो|kholo)$/i.test(clean)) {
    return {
      type: "settings",
      appName: "Sound Settings",
      action: "android.settings.SOUND_SETTINGS",
      settingType: "sound",
      url: "intent:#Intent;action=android.settings.SOUND_SETTINGS;end",
      fallbackUrl: "",
      actionText: "Opening Sound Settings",
      spokenConfirmation: defaultConfirmation,
    };
  }

  if (/(?:open|launch)\s+display(?:\s+settings)?$/i.test(clean) || /display\s*(?:settings\s*)?(?:खोलो|kholo)$/i.test(clean)) {
    return {
      type: "settings",
      appName: "Display Settings",
      action: "android.settings.DISPLAY_SETTINGS",
      settingType: "display",
      url: "intent:#Intent;action=android.settings.DISPLAY_SETTINGS;end",
      fallbackUrl: "",
      actionText: "Opening Display Settings",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 7. Android General Settings
  if (
    /^(?:please\s+)?(?:open|launch)\s+(?:phone\s+|android\s+)?settings$/i.test(clean) ||
    /^(?:phone\s+)?settings\s*(?:खोलो|kholo)$/i.test(clean)
  ) {
    return {
      type: "settings",
      appName: "Settings",
      action: "android.settings.SETTINGS",
      settingType: "main",
      url: "intent:#Intent;action=android.settings.SETTINGS;end",
      fallbackUrl: "",
      actionText: "Opening Android System Settings",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 8. Android Camera
  if (
    /^(?:please\s+)?(?:open|launch)\s+camera$/i.test(clean) ||
    /^camera\s*(?:खोलो|kholo)$/i.test(clean)
  ) {
    return {
      type: "camera",
      appName: "Camera",
      action: "android.media.action.IMAGE_CAPTURE",
      url: "intent:#Intent;action=android.media.action.IMAGE_CAPTURE;end",
      fallbackUrl: "",
      actionText: "Opening Camera directly",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 9. Phone Dialer
  if (
    /^(?:please\s+)?(?:open|launch)\s+(?:dialer|phone)$/i.test(clean) ||
    /^(?:dialer|phone)\s*(?:खोलो|kholo)$/i.test(clean)
  ) {
    return {
      type: "dialer",
      appName: "Phone Dialer",
      action: "android.intent.action.DIAL",
      url: "tel:",
      fallbackUrl: "",
      actionText: "Opening Phone Dialer",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 10. Clock / Alarms
  if (
    /^(?:please\s+)?(?:open|launch)\s+(?:clock|alarm)$/i.test(clean) ||
    /^(?:clock|alarm)\s*(?:खोलो|kholo)$/i.test(clean)
  ) {
    return {
      type: "clock",
      appName: "Clock",
      action: "android.intent.action.SHOW_ALARMS",
      url: "intent:#Intent;action=android.intent.action.SHOW_ALARMS;end",
      fallbackUrl: "",
      actionText: "Opening Clock & Alarms",
      spokenConfirmation: defaultConfirmation,
    };
  }

  // 11. Explicit URL Navigation
  const urlMatch = clean.match(/^(?:open\s+url|browse\s+to|navigate\s+to)\s+(https?:\/\/[^\s]+)$/i);
  if (urlMatch) {
    const targetUrl = urlMatch[1];
    return {
      type: "url",
      appName: "Browser",
      url: targetUrl,
      fallbackUrl: targetUrl,
      actionText: `Opening ${targetUrl}`,
      spokenConfirmation: defaultConfirmation,
    };
  }

  return null;
}

/**
 * Execute intent with environment awareness:
 * - If clientPlatform is "native", dispatches direct Android package/URI intent (am start).
 * - If clientPlatform is "web", returns webUrl for immediate client-side redirection without terminal clutter.
 */
export async function launchAndroidIntent(
  intent: IntentAction,
  options?: { clientPlatform?: "native" | "web" }
): Promise<{
  success: boolean;
  method: string;
  mode: "native" | "web";
  webUrl?: string;
  nativeUrl?: string;
  spokenConfirmation: string;
}> {
  const isWebMode = options?.clientPlatform === "web";
  const confirmationText = intent.spokenConfirmation || "हाँ, यह कर दिया है";

  // In Web Mode, do not trigger terminal Android app launch; prepare direct web URL
  if (isWebMode) {
    return {
      success: true,
      method: "web-browser",
      mode: "web",
      webUrl: intent.fallbackUrl || intent.url,
      spokenConfirmation: confirmationText,
    };
  }

  // In Native/APK Mode, execute direct Android Intent via am start
  const candidateCommands: string[] = [];

  // Priority 1: Native package launcher or specific intent action with package constraint
  if (intent.package) {
    if (intent.query && intent.url) {
      candidateCommands.push(
        `am start -a android.intent.action.VIEW -d "${intent.url}" -p ${intent.package} 2>/dev/null`
      );
    } else {
      candidateCommands.push(
        `am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p ${intent.package} 2>/dev/null`
      );
    }
  }

  // Priority 2: Generic Android system action (e.g. Settings, Camera)
  if (intent.action) {
    candidateCommands.push(`am start -a ${intent.action} 2>/dev/null`);
  }

  // Priority 3: Native custom URI scheme (e.g. vnd.youtube://...)
  if (intent.url && !intent.url.startsWith("http")) {
    candidateCommands.push(`am start -a android.intent.action.VIEW -d "${intent.url}" 2>/dev/null`);
  }

  for (const cmd of candidateCommands) {
    try {
      const { stderr } = await execAsync(cmd, { timeout: 3500 });
      if (!stderr || !stderr.includes("Error: Activity not started")) {
        return {
          success: true,
          method: cmd.split(" ")[0],
          mode: "native",
          nativeUrl: intent.url,
          spokenConfirmation: confirmationText,
        };
      }
    } catch {
      // Try next candidate
    }
  }

  // Fallback if native am commands fail
  return {
    success: true,
    method: "web-fallback",
    mode: "web",
    webUrl: intent.fallbackUrl || intent.url,
    spokenConfirmation: confirmationText,
  };
}
