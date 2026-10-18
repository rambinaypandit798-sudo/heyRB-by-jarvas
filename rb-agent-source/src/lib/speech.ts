import { voiceById, VOICE_PROFILES, type VoiceProfile } from "./voices";

/**
 * Speech playback engine with a character accurate bookmark.
 * Pausing stores the exact character index reached so resuming continues
 * from that word instead of restarting the whole block.
 */
type Listener = (state: SpeechState) => void;

export type SpeechState = {
  activeId: string | null;
  speaking: boolean;
  paused: boolean;
  /** Text already spoken plus the current sentence — used for live subtitles. */
  spoken: string;
};

class SpeechEngine {
  private listeners = new Set<Listener>();
  private state: SpeechState = { activeId: null, speaking: false, paused: false, spoken: "" };
  private fullText = "";
  private offset = 0;
  private voiceId = "aarav";
  private utterance: SpeechSynthesisUtterance | null = null;
  private onEndCb: (() => void) | null = null;

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
    const profile = voiceById(this.voiceId) ?? VOICE_PROFILES[0];
    if (!profile) return;
    const slice = this.fullText.slice(from);
    if (!slice.trim()) {
      this.stop();
      return;
    }
    const utter = new SpeechSynthesisUtterance(slice);
    utter.lang = profile.lang;
    utter.pitch = profile.pitch;
    utter.rate = profile.rate;
    const voice = this.pickVoice(profile);
    if (voice) utter.voice = voice;

    utter.onboundary = (event) => {
      this.offset = from + (event.charIndex ?? 0);
      this.emit({ spoken: this.fullText.slice(0, this.offset + 40) });
    };
    utter.onend = () => {
      if (this.state.paused) return;
      this.offset = 0;
      this.utterance = null;
      this.emit({ activeId: null, speaking: false, paused: false, spoken: "" });
      this.onEndCb?.();
      this.onEndCb = null;
    };
    this.utterance = utter;
    window.speechSynthesis.speak(utter);
    this.emit({ speaking: true, paused: false });
  }

  speak(id: string, text: string, voiceId: string, onEnd?: () => void) {
    if (!this.supported) return;
    window.speechSynthesis.cancel();
    this.voiceId = voiceId;
    this.fullText = text;
    this.offset = 0;
    this.onEndCb = onEnd ?? null;
    this.emit({ activeId: id, spoken: "" });
    this.run(0);
  }

  pause() {
    if (!this.supported || !this.state.speaking) return;
    // Cancel instead of pause: Chrome mobile drops paused utterances, so the
    // stored character offset is what makes resume exact.
    window.speechSynthesis.cancel();
    this.emit({ paused: true, speaking: false });
  }

  resume() {
    if (!this.supported || !this.state.paused) return;
    this.emit({ paused: false });
    this.run(this.offset);
  }

  toggle(id: string, text: string, voiceId: string) {
    if (this.state.activeId !== id) {
      this.speak(id, text, voiceId);
      return;
    }
    if (this.state.paused) this.resume();
    else this.pause();
  }

  stop() {
    if (!this.supported) return;
    window.speechSynthesis.cancel();
    this.offset = 0;
    this.fullText = "";
    this.utterance = null;
    this.onEndCb = null;
    this.emit({ activeId: null, speaking: false, paused: false, spoken: "" });
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
  const win = window as unknown as { SpeechRecognition?: new () => RecognitionLike; webkitSpeechRecognition?: new () => RecognitionLike };
  const Ctor = win.SpeechRecognition ?? win.webkitSpeechRecognition;
  if (!Ctor) return null;
  const rec = new Ctor();
  rec.lang = lang;
  rec.continuous = true;
  rec.interimResults = true;
  return rec;
}

export function readTranscript(event: unknown): { text: string; final: boolean } {
  const e = event as { results?: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }>; resultIndex?: number };
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
