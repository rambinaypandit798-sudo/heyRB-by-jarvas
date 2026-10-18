export type ModelTier = "Fast" | "Balanced" | "Max";

export type ModelOption = {
  id: string;
  label: string;
  tier: ModelTier;
  blurb: string;
  available?: boolean;
};

/** Gemini line-up available to RB Agent. Ordered fast to most intelligent. */
export const MODELS: ModelOption[] = [
  { id: "google/gemini-2.0-flash", label: "Gemini 2.0 Flash", tier: "Fast", blurb: "Legacy model · no longer available", available: false },
  { id: "google/gemini-2.5-flash", label: "Gemini 2.5 Flash", tier: "Fast", blurb: "Fast everyday reasoning" },
  { id: "google/gemini-2.5-flash-lite", label: "Gemini 2.5 Flash Lite", tier: "Fast", blurb: "Lightweight, quick replies" },
  {
    id: "google/gemini-3.1-flash-lite",
    label: "Gemini Flash Lite",
    tier: "Fast",
    blurb: "Lowest latency, great for quick answers",
  },
  {
    id: "google/gemini-3.8-flash",
    label: "Gemini 3.8 Flash",
    tier: "Fast",
    blurb: "Default everyday speed with strong reasoning",
  },
  {
    id: "google/gemini-3.7-flash",
    label: "Gemini 3.7 Flash",
    tier: "Balanced",
    blurb: "Balanced quality for longer tasks",
  },
  {
    id: "google/gemini-3-flash-preview",
    label: "Gemini Flash Preview",
    tier: "Balanced",
    blurb: "Newer conversational tuning",
  },
  {
    id: "google/gemini-3.1-pro-preview",
    label: "Gemini Pro Ultra",
    tier: "Max",
    blurb: "Deepest reasoning for complex work",
  },
  { id: "google/gemini-1.5-pro", label: "Gemini 1.5 Pro", tier: "Max", blurb: "Legacy model · no longer available", available: false },
  { id: "google/gemini-2.0-pro", label: "Gemini 2.0 Pro", tier: "Max", blurb: "Legacy model · no longer available", available: false },
  { id: "google/gemini-ultra", label: "Gemini Ultra", tier: "Max", blurb: "Not available for selection", available: false },
];

export const DEFAULT_MODEL = "google/gemini-3.8-flash";

export function usableModel(id?: string | null) {
  return MODELS.some((model) => model.id === id && model.available !== false) ? (id ?? DEFAULT_MODEL) : DEFAULT_MODEL;
}

export function modelLabel(id: string) {
  return MODELS.find((m) => m.id === id)?.label ?? "Gemini 3.8 Flash";
}
