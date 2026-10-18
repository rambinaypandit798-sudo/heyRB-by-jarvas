/**
 * Environment & Platform Detection Engine.
 * Automatically identifies whether RB Agent is running inside:
 * 1. Native Android / Capacitor / APK wrapper / WebView
 * 2. Standard Web Browser (localhost / desktop / Chrome tab)
 */

export type AppEnvironment = "native" | "web";

export function detectAppEnvironment(): AppEnvironment {
  // 1. If running on server side (Node.js/Nitro)
  if (typeof window === "undefined") {
    const isAndroidHost = Boolean(
      process.env.TERMUX_VERSION ||
      process.env.ANDROID_ROOT ||
      process.env.ANDROID_DATA
    );
    return isAndroidHost ? "native" : "web";
  }

  const win = window as any;

  // 2. Capacitor / Cordova native wrapper
  if (
    win.Capacitor?.isNativePlatform?.() ||
    win.Capacitor?.getPlatform?.() === "android" ||
    win.cordova !== undefined
  ) {
    return "native";
  }

  // 3. Android JavaScriptInterface native bridge
  if (win.Android || win.AndroidBridge || win._nativeAndroid) {
    return "native";
  }

  // 4. Android WebView detection
  const ua = (navigator.userAgent || "").toLowerCase();
  const isAndroidUA = ua.includes("android");
  const isWebView =
    ua.includes("; wv") ||
    ua.includes("version/") && ua.includes("chrome/") && isAndroidUA && !ua.includes("safari");

  // 5. Standalone installed PWA / TWA wrapper
  const isStandalone =
    window.matchMedia?.("(display-mode: standalone)").matches ||
    (navigator as any).standalone === true;

  if (isWebView || (isStandalone && isAndroidUA)) {
    return "native";
  }

  // 6. Default to standard web browser (localhost / desktop / tab)
  return "web";
}

export function isNativeApp(): boolean {
  return detectAppEnvironment() === "native";
}

export function isWebBrowser(): boolean {
  return detectAppEnvironment() === "web";
}
