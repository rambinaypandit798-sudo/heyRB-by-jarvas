/**
 * Robust Multilingual Command Recognition Engine for Media & Speech Control.
 * Recognizes play, pause, resume, seek, and intent triggers across English & Hindi.
 */

import { speechEngine } from "./speech";
import { mediaPlayerEngine } from "./media";

export type MediaCommandType =
  | "pause_all"
  | "resume_all"
  | "pause_speech"
  | "resume_speech"
  | "stop_speech"
  | "pause_media"
  | "resume_media"
  | "seek_media"
  | "none";

export interface RecognizedCommand {
  type: MediaCommandType;
  seekDelta?: number;
  seekTarget?: number;
  description: string;
}

export function recognizeMediaCommand(rawText: string): RecognizedCommand {
  const text = rawText.toLowerCase().trim().replace(/[.,!?;:]+$/, "");

  // 1. Pause speech / reading
  if (
    /^(pause\s+(?:speech|reading|voice|talk)|रुक\s*जाओ|बोलना\s+बंद\s+करो|रुको)$/i.test(text)
  ) {
    return { type: "pause_speech", description: "Paused speech synthesis" };
  }

  // 2. Resume speech / reading
  if (
    /^(resume\s+(?:speech|reading|voice)|continue\s+(?:reading|speaking)|आगे\s+बोलो|फिर\s+से\s+बोलो|चालू\s+करो)$/i.test(text)
  ) {
    return { type: "resume_speech", description: "Resumed speech synthesis from saved bookmark" };
  }

  // 3. Stop speech
  if (
    /^(stop\s+(?:speech|reading|voice|talking)|शांत\s+रहो|बंद\s+करो)$/i.test(text)
  ) {
    return { type: "stop_speech", description: "Stopped speech synthesis" };
  }

  // 4. Seek forward / rewind
  const forwardMatch = text.match(/^(?:skip|forward|seek\s+forward)\s+(\d+)\s*(?:s|sec|seconds?)?$/i);
  if (forwardMatch) {
    const delta = parseInt(forwardMatch[1], 10);
    return {
      type: "seek_media",
      seekDelta: delta,
      description: `Seeked forward ${delta} seconds`,
    };
  }

  const rewindMatch = text.match(/^(?:rewind|back|seek\s+back)\s+(\d+)\s*(?:s|sec|seconds?)?$/i);
  if (rewindMatch) {
    const delta = -parseInt(rewindMatch[1], 10);
    return {
      type: "seek_media",
      seekDelta: delta,
      description: `Rewound ${Math.abs(delta)} seconds`,
    };
  }

  // 5. General Pause (both speech and media)
  if (/^(pause|pause\s+(?:music|song|player|audio|media)|hold\s+on|wait)$/i.test(text)) {
    return { type: "pause_all", description: "Paused playback and speech" };
  }

  // 6. General Resume
  if (/^(resume|resume\s+(?:music|song|player|audio|media)|continue|play)$/i.test(text)) {
    return { type: "resume_all", description: "Resumed playback and speech" };
  }

  return { type: "none", description: "" };
}

/**
 * Execute recognized client command immediately without waiting for network round-trip.
 * Returns true if command was handled.
 */
export function executeClientMediaCommand(rawText: string): boolean {
  const cmd = recognizeMediaCommand(rawText);
  if (cmd.type === "none") return false;

  switch (cmd.type) {
    case "pause_all":
      speechEngine.pause();
      mediaPlayerEngine.pause();
      return true;

    case "resume_all":
      if (speechEngine.getState().paused) {
        speechEngine.resume();
      }
      mediaPlayerEngine.resume();
      return true;

    case "pause_speech":
      speechEngine.pause();
      return true;

    case "resume_speech":
      speechEngine.resume();
      return true;

    case "stop_speech":
      speechEngine.stop();
      return true;

    case "pause_media":
      mediaPlayerEngine.pause();
      return true;

    case "resume_media":
      mediaPlayerEngine.resume();
      return true;

    case "seek_media":
      if (cmd.seekDelta !== undefined) {
        mediaPlayerEngine.skip(cmd.seekDelta);
        return true;
      }
      return false;

    default:
      return false;
  }
}
