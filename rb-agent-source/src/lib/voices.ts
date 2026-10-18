export type VoiceProfile = {
  id: string;
  name: string;
  tone: string;
  lang: string;
  pitch: number;
  rate: number;
  /** Hints used to pick the closest installed system voice. */
  match: string[];
  gender: "male" | "female";
};

export const VOICE_PROFILES: VoiceProfile[] = [
  {
    id: "aarav",
    name: "Aarav",
    tone: "Deep, calm and authoritative",
    lang: "en-IN",
    pitch: 0.82,
    rate: 0.96,
    match: ["ravi", "hemant", "male"],
    gender: "male",
  },
  {
    id: "naina",
    name: "Naina",
    tone: "Warm, friendly and reassuring",
    lang: "hi-IN",
    pitch: 1.06,
    rate: 0.98,
    match: ["lekha", "swara", "female"],
    gender: "female",
  },
  {
    id: "kabir",
    name: "Kabir",
    tone: "Crisp, precise and professional",
    lang: "en-IN",
    pitch: 0.96,
    rate: 1.06,
    match: ["rishi", "daniel", "male"],
    gender: "male",
  },
  {
    id: "rhea",
    name: "Rhea",
    tone: "Energetic, dynamic and bright",
    lang: "en-IN",
    pitch: 1.18,
    rate: 1.12,
    match: ["samantha", "kalpana", "female"],
    gender: "female",
  },
  {
    id: "vivaan",
    name: "Vivaan",
    tone: "Youthful, casual and quick",
    lang: "en-US",
    pitch: 1.04,
    rate: 1.14,
    match: ["alex", "fred", "male"],
    gender: "male",
  },
  {
    id: "meera",
    name: "Meera",
    tone: "Soft, slow and story-like",
    lang: "hi-IN",
    pitch: 1.0,
    rate: 0.88,
    match: ["lekha", "google हिन्दी", "female"],
    gender: "female",
  },
];

export const DEFAULT_VOICE = "aarav";

export function voiceById(id: string) {
  return VOICE_PROFILES.find((v) => v.id === id) ?? VOICE_PROFILES[0];
}
