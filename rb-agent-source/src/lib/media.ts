/**
 * Client-side Persistent Media State & Audio/Video Engine.
 * Synchronizes playback timestamps with localStorage and /api/media-state
 * so pausing and resuming continues from the exact second without resetting.
 */

export interface MediaItem {
  id: string;
  title: string;
  url: string;
  type: "audio" | "video";
  currentTime: number;
  duration: number;
  status: "playing" | "paused" | "stopped";
}

const LOCAL_STORAGE_KEY = "rb_persistent_media_state_v1";

export function loadLocalMediaBookmarks(): Record<string, { currentTime: number; duration: number }> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function saveLocalMediaBookmark(id: string, currentTime: number, duration: number) {
  if (typeof window === "undefined" || !id) return;
  try {
    const bookmarks = loadLocalMediaBookmarks();
    bookmarks[id] = {
      currentTime: Math.max(0, currentTime),
      duration: Math.max(0, duration),
    };
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(bookmarks));
  } catch {}
}

export function getSavedMediaTimestamp(id: string): number {
  const bookmarks = loadLocalMediaBookmarks();
  return bookmarks[id]?.currentTime ?? 0;
}

// Global active player state & event hub
type MediaListener = (item: MediaItem | null) => void;

class MediaPlayerEngine {
  private activeItem: MediaItem | null = null;
  private listeners = new Set<MediaListener>();
  private activeElement: HTMLAudioElement | HTMLVideoElement | null = null;
  private syncDebounceTimer: number | null = null;

  subscribe(listener: MediaListener) {
    this.listeners.add(listener);
    listener(this.activeItem);
    return () => this.listeners.delete(listener);
  }

  private emit() {
    this.listeners.forEach((l) => l(this.activeItem));
  }

  getActiveItem(): MediaItem | null {
    return this.activeItem;
  }

  attachElement(
    item: { id: string; title: string; url: string; type: "audio" | "video" },
    element: HTMLAudioElement | HTMLVideoElement
  ) {
    this.activeElement = element;
    const savedTime = getSavedMediaTimestamp(item.id);

    this.activeItem = {
      id: item.id,
      title: item.title,
      url: item.url,
      type: item.type,
      currentTime: savedTime,
      duration: element.duration || 0,
      status: element.paused ? "paused" : "playing",
    };

    if (savedTime > 0 && Math.abs(element.currentTime - savedTime) > 0.5) {
      try {
        element.currentTime = savedTime;
      } catch {}
    }

    this.emit();
  }

  updateProgress(currentTime: number, duration: number, isPlaying: boolean) {
    if (!this.activeItem) return;
    this.activeItem.currentTime = currentTime;
    if (duration > 0) this.activeItem.duration = duration;
    this.activeItem.status = isPlaying ? "playing" : "paused";

    // Save to localStorage immediately
    saveLocalMediaBookmark(this.activeItem.id, currentTime, duration);
    this.emit();

    // Debounced sync to backend
    if (this.syncDebounceTimer !== null) {
      clearTimeout(this.syncDebounceTimer);
    }
    this.syncDebounceTimer = window.setTimeout(() => {
      if (this.activeItem) {
        fetch("/api/media-state", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: this.activeItem.id,
            title: this.activeItem.title,
            url: this.activeItem.url,
            type: this.activeItem.type,
            currentTime: this.activeItem.currentTime,
            duration: this.activeItem.duration,
            status: this.activeItem.status,
          }),
        }).catch(() => {});
      }
    }, 2000);
  }

  pause() {
    if (this.activeElement && !this.activeElement.paused) {
      this.activeElement.pause();
      if (this.activeItem) {
        this.activeItem.status = "paused";
        saveLocalMediaBookmark(this.activeItem.id, this.activeElement.currentTime, this.activeElement.duration);
        this.emit();
      }
    }
  }

  resume() {
    if (this.activeElement && this.activeElement.paused) {
      if (this.activeItem) {
        const savedTime = getSavedMediaTimestamp(this.activeItem.id);
        if (savedTime > 0 && Math.abs(this.activeElement.currentTime - savedTime) > 0.5) {
          this.activeElement.currentTime = savedTime;
        }
      }
      this.activeElement.play().catch(() => {});
      if (this.activeItem) {
        this.activeItem.status = "playing";
        this.emit();
      }
    }
  }

  toggle() {
    if (this.activeElement) {
      if (this.activeElement.paused) {
        this.resume();
      } else {
        this.pause();
      }
    }
  }

  seek(seconds: number) {
    if (this.activeElement) {
      const target = Math.max(0, Math.min(this.activeElement.duration || 999999, seconds));
      this.activeElement.currentTime = target;
      if (this.activeItem) {
        this.activeItem.currentTime = target;
        saveLocalMediaBookmark(this.activeItem.id, target, this.activeElement.duration || 0);
        this.emit();
      }
    }
  }

  skip(deltaSeconds: number) {
    if (this.activeElement) {
      const target = Math.max(0, this.activeElement.currentTime + deltaSeconds);
      this.seek(target);
    }
  }
}

export const mediaPlayerEngine = new MediaPlayerEngine();
