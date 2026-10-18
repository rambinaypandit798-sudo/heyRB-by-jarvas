import fs from "fs";
import path from "path";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export interface MediaPlaybackState {
  id: string;
  title: string;
  url: string;
  type: "audio" | "video";
  currentTime: number;
  duration: number;
  status: "playing" | "paused" | "stopped";
  lastUpdated: string;
}

const MEDIA_STATE_FILE = path.resolve(process.cwd(), ".media-state.json");

interface MediaStateStore {
  items: Record<string, MediaPlaybackState>;
  lastActiveId: string | null;
}

let store: MediaStateStore = {
  items: {},
  lastActiveId: null,
};

// Load persistent state from disk
try {
  if (fs.existsSync(MEDIA_STATE_FILE)) {
    const raw = fs.readFileSync(MEDIA_STATE_FILE, "utf-8");
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed.items === "object") {
      store = {
        items: parsed.items,
        lastActiveId: parsed.lastActiveId ?? null,
      };
    }
  }
} catch {
  // Use in-memory fallback
}

function persistStore() {
  try {
    fs.writeFileSync(MEDIA_STATE_FILE, JSON.stringify(store, null, 2), "utf-8");
  } catch {
    // Non-fatal
  }
}

export function saveMediaPlaybackState(patch: {
  id: string;
  title?: string;
  url?: string;
  type?: "audio" | "video";
  currentTime: number;
  duration?: number;
  status?: "playing" | "paused" | "stopped";
}): MediaPlaybackState {
  const existing = store.items[patch.id] ?? {
    id: patch.id,
    title: patch.title || "Media Track",
    url: patch.url || "",
    type: patch.type || "audio",
    currentTime: 0,
    duration: 0,
    status: "paused",
    lastUpdated: new Date().toISOString(),
  };

  const updated: MediaPlaybackState = {
    ...existing,
    ...patch,
    currentTime: Math.max(0, patch.currentTime),
    duration: patch.duration !== undefined ? Math.max(0, patch.duration) : existing.duration,
    status: patch.status ?? existing.status,
    lastUpdated: new Date().toISOString(),
  };

  store.items[patch.id] = updated;
  store.lastActiveId = patch.id;
  persistStore();
  return updated;
}

export function getMediaPlaybackState(id?: string): MediaPlaybackState | null {
  if (id) {
    return store.items[id] ?? null;
  }
  if (store.lastActiveId && store.items[store.lastActiveId]) {
    return store.items[store.lastActiveId];
  }
  const all = Object.values(store.items);
  return all.length > 0 ? all[all.length - 1] : null;
}

export function getAllMediaStates(): Record<string, MediaPlaybackState> {
  return store.items;
}

/** Check Termux media player status if available on Android device */
export async function getTermuxMediaPlayerStatus(): Promise<{
  available: boolean;
  status?: string;
  currentPosition?: number;
  duration?: number;
}> {
  try {
    const { stdout } = await execAsync("termux-media-player info 2>/dev/null", { timeout: 1500 });
    const parsed = JSON.parse(stdout);
    return {
      available: true,
      status: parsed.status,
      currentPosition: parsed.current_position,
      duration: parsed.duration,
    };
  } catch {
    return { available: false };
  }
}

/** Control Termux media player command */
export async function controlTermuxMediaPlayer(
  cmd: "play" | "pause" | "stop" | "resume",
  file?: string
): Promise<{ success: boolean; output?: string }> {
  try {
    const termuxCmd =
      cmd === "resume"
        ? "termux-media-player play"
        : cmd === "play" && file
        ? `termux-media-player play ${JSON.stringify(file)}`
        : `termux-media-player ${cmd}`;

    const { stdout } = await execAsync(termuxCmd, { timeout: 2500 });
    return { success: true, output: stdout.trim() };
  } catch (err: any) {
    return { success: false, output: err?.message };
  }
}
