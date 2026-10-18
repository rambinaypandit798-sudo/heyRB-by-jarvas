import { voiceById, VOICE_PROFILES, type VoiceProfile } from "./voices";

/**
 * Enhanced Speech playback engine with word-accurate bookmarking & resume support.
 * Pausing stores the exact character index reached so resuming continues
 * seamlessly from that exact word instead of restarting from the beginning.
 */
type Listener = (state: SpeechState) => void;

export type SpeechState = {
  activeId: string | null;
  speaking: boolean;
  paused: boolean;
  /** Text already spoken plus the current sentence — used for live subtitles. */
  spoken: string;
  charOffset: number;
  totalChars: number;
};

const BOOKMARKS_STORAGE_KEY = "rb_speech_bookmarks_v1";

function loadSavedBookmarks(): Record<string, number> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(BOOKMARKS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function persistBookmark(id: string, offset: number) {
  if (typeof window === "undefined" || !id) return;
  try {
    const bookmarks = loadSavedBookmarks();
    if (offset <= 0) {
      delete bookmarks[id];
    } else {
      bookmarks[id] = offset;
    }
    localStorage.setItem(BOOKMARKS_STORAGE_KEY, JSON.stringify(bookmarks));
  } catch {
    // Non-fatal
  }
}

/** Aligns a raw character offset to the start of the current or next word boundary. */
function alignToWordBoundary(text: string, index: number): number {
  if (index <= 0) return 0;
  if (index >= text.length) return text.length;

  let pos = index;
  // If we are in the middle of a word, back up to the first character of this word
  while (pos > 0 && !/\s/.test(text[pos - 1])) {
    pos--;
  }
  return pos;
}

class SpeechEngine {
  private listeners = new Set<Listener>();
  private state: SpeechState = {
    activeId: null,
    speaking: false,
    paused: false,
    spoken: "",
    charOffset: 0,
    totalChars: 0,
  };
  private fullText = "";
  private offset = 0;
  private voiceId = "aarav";
  private utterance: SpeechSynthesisUtterance | null = null;
  private onEndCb: (() => void) | null = null;
  private isIntentionalPause = false;
  private timer: number | null = null;
  private lastBoundaryTime = 0;

  constructor() {
    // Ensure clean state if tab is restored
    if (typeof window !== "undefined") {
      window.addEventListener("beforeunload", () => {
        if (this.state.speaking && this.state.activeId) {
          persistBookmark(this.state.activeId, this.offset);
        }
      });
    }
  }

  subscribe(listener: Listener) {
    this.listeners.add(listener);
    listener(this.state);
    return () => this.listeners.delete(listener);
  }

  private emit(patch: Partial<SpeechState>) {
    this.state = { ...this.state, ...patch };
    this.listeners.forEach((l) => l(this.state));
  }

  get supported() {
    return typeof window !== "undefined" && "speechSynthesis" in window;
  }

  getState(): SpeechState {
    return this.state;
  }

  getBookmark(id: string): number {
    const bookmarks = loadSavedBookmarks();
    return bookmarks[id] ?? 0;
  }

  private clearTimer() {
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  private startFallbackTimer(profile: VoiceProfile, startFrom: number) {
    this.clearTimer();
    this.lastBoundaryTime = Date.now();
    // Typical speech: ~14 characters per second at 1.0 rate
    const charsPerSec = Math.max(8, 14 * (profile.rate || 1));

    this.timer = window.setInterval(() => {
      if (!this.state.speaking || this.state.paused) {
        this.clearTimer();
        return;
      }
      const now = Date.now();
      const elapsedSinceBoundary = (now - this.lastBoundaryTime) / 1000;
      // If onboundary hasn't fired in >350ms, advance estimated offset
      if (elapsedSinceBoundary > 0.35) {
        const estimatedAdvance = Math.floor(elapsedSinceBoundary * charsPerSec);
        const nextOffset = Math.min(this.fullText.length, startFrom + estimatedAdvance);
        if (nextOffset > this.offset) {
          this.offset = nextOffset;
          if (this.state.activeId) {
            persistBookmark(this.state.activeId, this.offset);
          }
          this.emit({
            charOffset: this.offset,
            spoken: this.fullText.slice(0, Math.min(this.fullText.length, this.offset + 40)),
          });
        }
      }
    }, 200);
  }

  private pickVoice(profile: VoiceProfile) {
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) return null;
    const byHint = voices.find((v) =>
      profile.match.some((hint) => v.name.toLowerCase().includes(hint.toLowerCase())),
    );
    if (byHint) return byHint;
    const byLang = voices.find((v) => v.lang.toLowerCase() === profile.lang.toLowerCase());
    if (byLang) return byLang;
    const byPrefix = voices.find((v) => v.lang.toLowerCase().startsWith(profile.lang.slice(0, 2)));
    return byPrefix ?? voices[0];
  }

  /** Speak from a given character offset in the text. */
  private run(from: number) {
    if (!this.supported) return;
    const safeFrom = alignToWordBoundary(this.fullText, Math.max(0, from));
    this.offset = safeFrom;

    const profile = voiceById(this.voiceId) ?? VOICE_PROFILES[0];
    if (!profile) return;

    const slice = this.fullText.slice(safeFrom);
    if (!slice.trim()) {
      this.stop();
      return;
    }

    this.isIntentionalPause = false;
    const utter = new SpeechSynthesisUtterance(slice);
    utter.lang = profile.lang;
    utter.pitch = profile.pitch;
    utter.rate = profile.rate;
    const voice = this.pickVoice(profile);
    if (voice) utter.voice = voice;

    utter.onboundary = (event) => {
      if (this.isIntentionalPause) return;
      this.lastBoundaryTime = Date.now();
      const rawIndex = safeFrom + (event.charIndex ?? 0);
      this.offset = Math.min(this.fullText.length, rawIndex);
      if (this.state.activeId) {
        persistBookmark(this.state.activeId, this.offset);
      }
      this.emit({
        charOffset: this.offset,
        spoken: this.fullText.slice(0, Math.min(this.fullText.length, this.offset + 40)),
      });
    };

    utter.onend = () => {
      this.clearTimer();
      // If this was an intentional pause triggered via cancel(), preserve bookmark and offset!
      if (this.isIntentionalPause || this.state.paused) {
        return;
      }
      this.offset = 0;
      this.utterance = null;
      if (this.state.activeId) {
        persistBookmark(this.state.activeId, 0);
      }
      this.emit({
        activeId: null,
        speaking: false,
        paused: false,
        spoken: "",
        charOffset: 0,
        totalChars: 0,
      });
      this.onEndCb?.();
      this.onEndCb = null;
    };

    utter.onerror = (err) => {
      this.clearTimer();
      // Chrome/Android triggers error 'canceled' or 'interrupted' when paused
      if (this.isIntentionalPause || this.state.paused || err.error === "canceled" || err.error === "interrupted") {
        return;
      }
      console.warn("Speech synthesis error:", err.error);
      this.stop();
    };

    this.utterance = utter;
    this.startFallbackTimer(profile, safeFrom);
    window.speechSynthesis.speak(utter);
    this.emit({
      speaking: true,
      paused: false,
      charOffset: safeFrom,
      totalChars: this.fullText.length,
    });
  }

  speak(id: string, text: string, voiceId: string, onEnd?: () => void, startOffset?: number) {
    if (!this.supported) return;

    this.isIntentionalPause = false;
    this.clearTimer();
    window.speechSynthesis.cancel();

    this.voiceId = voiceId;
    this.fullText = text;

    // Check if a bookmark was requested or previously stored
    const saved = startOffset !== undefined ? startOffset : this.getBookmark(id);
    const from = saved > 0 && saved < text.length ? alignToWordBoundary(text, saved) : 0;

    this.offset = from;
    this.onEndCb = onEnd ?? null;
    this.emit({
      activeId: id,
      spoken: from > 0 ? text.slice(0, from) : "",
      charOffset: from,
      totalChars: text.length,
      paused: false,
    });

    this.run(from);
  }

  pause() {
    if (!this.supported) return;
    this.isIntentionalPause = true;
    this.clearTimer();

    // Store bookmark before cancellation
    if (this.state.activeId) {
      persistBookmark(this.state.activeId, this.offset);
    }

    this.emit({
      paused: true,
      speaking: false,
      charOffset: this.offset,
      totalChars: this.fullText.length,
    });

    try {
      window.speechSynthesis.cancel();
    } catch {
      // safe ignore
    }
  }

  resume() {
    if (!this.supported) return;
    if (!this.fullText && this.state.activeId) {
      return;
    }
    this.isIntentionalPause = false;
    this.emit({ paused: false, speaking: true });
    this.run(this.offset);
  }

  toggle(id: string, text: string, voiceId: string) {
    if (this.state.activeId !== id) {
      this.speak(id, text, voiceId);
      return;
    }
    if (this.state.paused) {
      this.resume();
    } else if (this.state.speaking) {
      this.pause();
    } else {
      this.speak(id, text, voiceId);
    }
  }

  seek(charOffset: number) {
    if (!this.supported || !this.fullText) return;
    const clamped = Math.max(0, Math.min(this.fullText.length, charOffset));
    const aligned = alignToWordBoundary(this.fullText, clamped);
    this.offset = aligned;
    if (this.state.activeId) {
      persistBookmark(this.state.activeId, aligned);
    }
    if (this.state.speaking && !this.state.paused) {
      this.clearTimer();
      this.isIntentionalPause = true;
      window.speechSynthesis.cancel();
      this.run(aligned);
    } else {
      this.emit({
        charOffset: aligned,
        spoken: this.fullText.slice(0, aligned),
      });
    }
  }

  stop(id?: string, clearBookmark = false) {
    if (!this.supported) return;
    this.clearTimer();
    this.isIntentionalPause = false;

    if (id && clearBookmark) {
      persistBookmark(id, 0);
    } else if (this.state.activeId && !clearBookmark) {
      persistBookmark(this.state.activeId, this.offset);
    }

    try {
      window.speechSynthesis.cancel();
    } catch {}

    this.offset = 0;
    this.fullText = "";
    this.utterance = null;
    this.onEndCb = null;
    this.emit({
      activeId: null,
      speaking: false,
      paused: false,
      spoken: "",
      charOffset: 0,
      totalChars: 0,
    });
  }
}

export const speechEngine = new SpeechEngine();

/** Minimal typing for the vendor prefixed browser recogniser. */
type RecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: unknown) => void) | null;
  onerror: ((event: unknown) => void) | null;
  onend: (() => void) | null;
};

export function createRecognition(lang = "hi-IN"): RecognitionLike | null {
  if (typeof window === "undefined") return null;
  const win = window as unknown as {
    SpeechRecognition?: new () => RecognitionLike;
    webkitSpeechRecognition?: new () => RecognitionLike;
  };
  const Ctor = win.SpeechRecognition ?? win.webkitSpeechRecognition;
  if (!Ctor) return null;
  const rec = new Ctor();
  rec.lang = lang;
  rec.continuous = true;
  rec.interimResults = true;
  return rec;
}

export function readTranscript(event: unknown): { text: string; final: boolean } {
  const e = event as {
    results?: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }>;
    resultIndex?: number;
  };
  if (!e.results) return { text: "", final: false };
  let text = "";
  let final = false;
  for (let i = 0; i < e.results.length; i += 1) {
    const result = e.results[i];
    if (!result) continue;
    text += result[0]?.transcript ?? "";
    if (result.isFinal) final = true;
  }
  return { text: text.trim(), final };
}
