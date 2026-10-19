import { toast } from "sonner";
import { speechEngine } from "./speech";

export interface DeviceActionPayload {
  type: "youtube" | "spotify" | "whatsapp" | "settings" | "camera" | "dialer" | "clock" | "calculator" | "gallery" | "url" | "custom";
  appName: string;
  actionText: string;
  package?: string;
  action?: string;
  query?: string;
  url?: string;
  fallbackUrl?: string;
  settingType?: "wifi" | "bluetooth" | "display" | "sound" | "main";
}

export interface ActionExecutionResult {
  success: boolean;
  method: "android-bridge" | "capacitor" | "cordova" | "termux-server" | "web-fallback";
  spokenConfirmation: string;
  action: DeviceActionPayload;
}

type ActionEventListener = (action: DeviceActionPayload) => void;
const overlayListeners = new Set<ActionEventListener>();

/**
 * Event emitter for Gemini-Style Floating Overlay Window
 */
export const overlayWindowEvents = {
  subscribe(listener: ActionEventListener) {
    overlayListeners.add(listener);
    return () => {
      overlayListeners.delete(listener);
    };
  },
  trigger(action: DeviceActionPayload) {
    overlayListeners.forEach((listener) => {
      try {
        listener(action);
      } catch (e) {
        console.error("Overlay listener error:", e);
      }
    });
  },
};

/**
 * Executes deep device actions via available runtime bridge:
 * 1. AndroidBridge (Native APK WebView JavascriptInterface)
 * 2. Capacitor / Cordova native plugins
 * 3. Termux server-side am start execution (/api/intent)
 * 4. Web browser fallback (window.open)
 *
 * Automatically triggers spoken voice confirmation:
 * "हाँ, यह कर दिया है" (Yes, it's done).
 */
export async function executeDeviceAction(action: DeviceActionPayload): Promise<ActionExecutionResult> {
  const confirmationText = "हाँ, यह कर दिया है";
  let method: ActionExecutionResult["method"] = "web-fallback";
  let success = false;

  // Trigger Gemini-Style Floating Overlay Window
  overlayWindowEvents.trigger(action);

  // 1. Priority 1: Native AndroidBridge (In APK WebView)
  if (typeof window !== "undefined" && (window as any).AndroidBridge) {
    const bridge = (window as any).AndroidBridge;
    try {
      if (action.type === "youtube") {
        success = bridge.openYouTube(action.query || "");
      } else if (action.type === "settings") {
        success = bridge.openSettings(action.settingType || "main");
      } else {
        success = bridge.launchApp(action.package || "", action.url || "", action.action || "");
      }
      if (success) {
        method = "android-bridge";
      }
    } catch (err) {
      console.warn("AndroidBridge execution failed, falling back:", err);
    }
  }

  // 2. Priority 2: Capacitor Plugins (if configured)
  if (!success && typeof window !== "undefined" && (window as any).Capacitor) {
    try {
      const cap = (window as any).Capacitor;
      if (cap.isNativePlatform && cap.isNativePlatform()) {
        if (action.package && cap.Plugins?.AppLauncher) {
          await cap.Plugins.AppLauncher.openUrl({ url: action.url || `${action.package}://` });
          success = true;
          method = "capacitor";
        }
      }
    } catch (e) {
      console.warn("Capacitor launch failed:", e);
    }
  }

  // 3. Priority 3: Termux Server Intent Dispatch (/api/intent)
  if (!success) {
    try {
      const res = await fetch("/api/intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: {
            type: action.type,
            appName: action.appName,
            package: action.package,
            action: action.action,
            query: action.query,
            url: action.url,
            fallbackUrl: action.fallbackUrl,
            actionText: action.actionText,
          },
          platform: "native",
        }),
      });
      const data = await res.json();
      if (data?.success && data?.mode === "native") {
        success = true;
        method = "termux-server";
      }
    } catch (e) {
      console.warn("Termux server intent dispatch failed:", e);
    }
  }

  // 4. Priority 4: Web Browser Redirection Fallback
  if (!success && typeof window !== "undefined") {
    const targetUrl = action.fallbackUrl || action.url;
    if (targetUrl) {
      try {
        window.open(targetUrl, "_blank", "noopener,noreferrer");
        success = true;
        method = "web-fallback";
      } catch (e) {
        console.warn("Web fallback open failed:", e);
      }
    }
  }

  // Mandatory Spoken Confirmation Feedback: "हाँ, यह कर दिया है"
  try {
    speechEngine.speakConfirmation(confirmationText);
  } catch (err) {
    console.warn("Spoken confirmation trigger error:", err);
  }

  // Toast feedback
  toast.success(confirmationText, {
    description: action.actionText || `${action.appName} launched successfully.`,
    duration: 3500,
  });

  return {
    success,
    method,
    spokenConfirmation: confirmationText,
    action,
  };
}
