/**
 * PWA Service Worker Registration and Network Status Handler for RB Agent OS.
 */

class PwaManager {
  constructor() {
    this.statusDot = document.getElementById("connection-status-dot");
    this.statusText = document.getElementById("connection-status-text");
    this.deferredPrompt = null;
    this.init();
  }

  init() {
    // Register Service Worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
          .then((reg) => console.log('[PWA] Service worker registered:', reg.scope))
          .catch((err) => console.warn('[PWA] Service worker registration failed:', err));
      });
    }

    // Monitor Online / Offline network state
    window.addEventListener('online', () => this.updateOnlineStatus(true));
    window.addEventListener('offline', () => this.updateOnlineStatus(false));
    this.updateOnlineStatus(navigator.onLine);

    // Install prompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      console.log('[PWA] Install prompt captured.');
    });
  }

  updateOnlineStatus(isOnline) {
    if (this.statusDot) {
      if (isOnline) {
        this.statusDot.classList.remove("offline");
        if (this.statusText) this.statusText.textContent = "Online";
      } else {
        this.statusDot.classList.add("offline");
        if (this.statusText) this.statusText.textContent = "Offline";
      }
    }
  }
}

window.pwaManager = new PwaManager();
