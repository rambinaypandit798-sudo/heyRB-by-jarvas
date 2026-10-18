import { recordUsageEvent, markOpenRouterCooldown, markGeminiCooldown } from "./usage.server";

const GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta";

export function openrouterKey(): string | null {
  const key = process.env["OPENROUTER_API_KEY"] || process.env["VITE_OPENROUTER_API_KEY"];
  if (!key) return null;
  return key.trim().replace(/^["']|["']$/g, "");
}

export const OPENROUTER_FREE_MODELS = [
  "openrouter/free",
  "google/gemma-4-31b-it:free",
  "google/gemma-4-26b-a4b-it:free",
  "nvidia/nemotron-3.5-lightning:free",
  "liquid/lfm-2.5-2.6b:free",
];

// Cooldown tracking for rotated API keys
const keyCooldowns = new Map<string, number>();

export function getAllGatewayKeys(): string[] {
  const rawKeys = [
    process.env["GEMINI_API_KEY"],
    process.env["VITE_GEMINI_API_KEY"],
    process.env["LOVABLE_API_KEY"],
    ...(process.env["GEMINI_API_KEYS"] ? process.env["GEMINI_API_KEYS"].split(",") : []),
  ];
  const seen = new Set<string>();
  const valid: string[] = [];
  for (const k of rawKeys) {
    if (!k) continue;
    const clean = k.trim().replace(/^["']|["']$/g, "");
    if (clean && !seen.has(clean)) {
      seen.add(clean);
      valid.push(clean);
    }
  }
  return valid;
}

export function getActiveKey(): string {
  const keys = getAllGatewayKeys();
  if (keys.length === 0) throw new Error("AI is not configured yet.");
  const now = Date.now();
  for (const k of keys) {
    const cd = keyCooldowns.get(k) || 0;
    if (now > cd) return k;
  }
  return keys[0];
}

export function markKeyCooldown(key: string, seconds = 45) {
  keyCooldowns.set(key, Date.now() + seconds * 1000);
}

export function gatewayKey() {
  return getActiveKey();
}

export function normalizeModelName(rawModel: string): string {
  const clean = rawModel.replace(/^google\//i, "").trim();
  if (clean.includes("3.8-flash")) return "gemini-3.8-flash";
  if (clean.includes("3.7-flash")) return "gemini-3.7-flash";
  if (clean.includes("3.6-flash")) return "gemini-3.6-flash";
  if (clean.includes("3.5-flash")) return "gemini-3.5-flash";
  if (clean.includes("3.1-pro")) return "gemini-3.1-pro-preview";
  if (clean.includes("3.1-flash-lite")) return "gemini-3.1-flash-lite";
  if (clean.includes("3-flash")) return "gemini-3-flash-preview";
  if (clean.includes("flash-lite")) return "gemini-flash-lite-latest";
  if (clean.includes("flash")) return "gemini-3.8-flash";
  if (clean.includes("pro")) return "gemini-pro-latest";
  return "gemini-3.8-flash";
}

export function getFallbackModels(primaryModel: string): string[] {
  const normalized = normalizeModelName(primaryModel);
  const fallbacks: string[] = [normalized];

  if (normalized.includes("pro")) {
    if (!fallbacks.includes("gemini-pro-latest")) fallbacks.push("gemini-pro-latest");
    if (!fallbacks.includes("gemini-3.8-flash")) fallbacks.push("gemini-3.8-flash");
    if (!fallbacks.includes("gemini-flash-latest")) fallbacks.push("gemini-flash-latest");
  } else {
    if (!fallbacks.includes("gemini-3.8-flash")) fallbacks.push("gemini-3.8-flash");
    if (!fallbacks.includes("gemini-flash-latest")) fallbacks.push("gemini-flash-latest");
    if (!fallbacks.includes("gemini-3.7-flash")) fallbacks.push("gemini-3.7-flash");
    if (!fallbacks.includes("gemini-flash-lite-latest")) fallbacks.push("gemini-flash-lite-latest");
  }
  return fallbacks;
}

export function calculateBackoffDelay(attempt: number, response?: Response): number {
  const retryAfterHeader = response?.headers?.get("Retry-After");
  if (retryAfterHeader) {
    const seconds = Number(retryAfterHeader);
    if (Number.isFinite(seconds) && seconds > 0) {
      return Math.min(seconds * 1000, 6000);
    }
  }
  const base = 800 * Math.pow(2, attempt);
  const jitter = Math.floor(Math.random() * 300) - 150;
  return Math.min(Math.max(base + jitter, 500), 5000);
}

export function formatGeminiPayload(
  messages: { role: string; content: string }[],
  options?: { enableGoogleSearch?: boolean }
) {
  let systemText = "";
  const contents: { role: "user" | "model"; parts: { text: string }[] }[] = [];

  for (const msg of messages) {
    if (!msg.content?.trim()) continue;

    if (msg.role === "system") {
      systemText = systemText ? `${systemText}\n\n${msg.content}` : msg.content;
      continue;
    }

    const role: "user" | "model" = msg.role === "assistant" ? "model" : "user";
    const last = contents.length > 0 ? contents[contents.length - 1] : undefined;
    if (last && last.role === role && last.parts[0]) {
      last.parts[0].text += `\n\n${msg.content}`;
    } else {
      contents.push({ role, parts: [{ text: msg.content }] });
    }
  }

  // Ensure conversation starts with a user message
  const first = contents[0];
  if (!first || first.role !== "user") {
    contents.unshift({ role: "user", parts: [{ text: "Hello" }] });
  }

  return {
    ...(systemText ? { systemInstruction: { parts: [{ text: systemText }] } } : {}),
    contents,
    ...(options?.enableGoogleSearch ? { tools: [{ googleSearch: {} }] } : {}),
  };
}

export async function embed(text: string): Promise<number[] | null> {
  try {
    const key = gatewayKey();
    const res = await fetch(`${GEMINI_BASE}/models/gemini-embedding-001:embedContent?key=${key}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: { parts: [{ text: text.slice(0, 6000) }] },
        outputDimensionality: 1536,
      }),
    });
    if (!res.ok) {
      return null;
    }
    const json = (await res.json()) as { embedding?: { values?: number[] } };
    return json.embedding?.values ?? null;
  } catch (error) {
    console.error("embedding unavailable", error);
    return null;
  }
}

export async function chatCompletion(
  model: string,
  messages: { role: string; content: string }[],
  options?: { enableGoogleSearch?: boolean }
): Promise<Response> {
  const fallbackModels = getFallbackModels(model);
  const payload = formatGeminiPayload(messages, options);
  const maxAttempts = 3;

  let lastResponse: Response | null = null;
  let lastError: unknown = null;

  for (let modelIdx = 0; modelIdx < fallbackModels.length; modelIdx++) {
    const targetModel = fallbackModels[modelIdx];

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const key = getActiveKey();

      try {
        const response = await fetch(
          `${GEMINI_BASE}/models/${targetModel}:streamGenerateContent?alt=sse&key=${key}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );

        if (response.ok) {
          return response;
        }

        lastResponse = response;

        // If rate limit (429) or transient server error (500, 503)
        if (response.status === 429 || response.status >= 500) {
          if (response.status === 429) {
            markKeyCooldown(key, 30);
          }

          if (attempt < maxAttempts - 1) {
            const delay = calculateBackoffDelay(attempt, response);
            await response.body?.cancel().catch(() => {});
            await new Promise((resolve) => setTimeout(resolve, delay));
            continue;
          }
        } else {
          // Client errors (400, 401, 403, 404) are not retried with this model
          break;
        }
      } catch (err) {
        lastError = err;
        if (attempt < maxAttempts - 1) {
          const delay = calculateBackoffDelay(attempt);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }
  }

  if (lastResponse) {
    return lastResponse;
  }

  throw lastError || new Error("Gemini API request failed after exponential backoff.");
}

export async function completeOnce(model: string, messages: { role: string; content: string }[]) {
  const fallbackModels = getFallbackModels(model);
  const payload = formatGeminiPayload(messages);

  for (const targetModel of fallbackModels) {
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const key = getActiveKey();
        const res = await fetch(`${GEMINI_BASE}/models/${targetModel}:generateContent?key=${key}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          const json = (await res.json()) as {
            candidates?: { content?: { parts?: { text?: string }[] } }[];
          };
          return json.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ?? null;
        }

        if (res.status === 429) {
          markKeyCooldown(key, 30);
          const delay = calculateBackoffDelay(attempt, res);
          await res.body?.cancel().catch(() => {});
          await new Promise((resolve) => setTimeout(resolve, delay));
        } else {
          break;
        }
      } catch (error) {
        console.error("completeOnce retry failure", error);
      }
    }
  }
  return null;
}

export async function openrouterCompletion(
  model: string,
  messages: { role: string; content: string }[],
  options?: { stream?: boolean }
): Promise<Response> {
  const key = openrouterKey();
  if (!key) throw new Error("OpenRouter API key is not configured.");

  const formattedMessages = messages
    .filter((m) => m.content?.trim())
    .map((m) => ({
      role: m.role === "assistant" || m.role === "model" ? "assistant" : m.role === "system" ? "system" : "user",
      content: m.content,
    }));

  const targetModel = model.startsWith("openrouter/") || model.includes("/") ? model : "openrouter/free";

  return fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${key}`,
      "HTTP-Referer": "http://localhost:8080",
      "X-Title": "RB Agent",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: targetModel,
      messages: formattedMessages,
      stream: options?.stream !== false,
    }),
  });
}

export async function chatCompletionWithFailover(
  model: string,
  messages: { role: string; content: string }[],
  options?: { enableGoogleSearch?: boolean }
): Promise<{
  response: Response;
  provider: "openrouter" | "gemini";
  model: string;
  failoverTriggered: boolean;
}> {
  const orKey = openrouterKey();

  // 1. PRIMARY ROUTE: OpenRouter (Top Free Tier / Free Router)
  if (orKey) {
    const candidateModels =
      model.startsWith("openrouter/") || (model.includes("/") && !model.startsWith("google/"))
        ? [model, ...OPENROUTER_FREE_MODELS]
        : OPENROUTER_FREE_MODELS;

    for (const orModel of candidateModels) {
      try {
        const orRes = await openrouterCompletion(orModel, messages, { stream: true });
        if (orRes.ok) {
          recordUsageEvent({ provider: "openrouter", model: orModel, failover: false });
          return {
            response: orRes,
            provider: "openrouter",
            model: orModel,
            failoverTriggered: false,
          };
        }
        if (orRes.status === 429 || orRes.status >= 500) {
          await orRes.body?.cancel().catch(() => {});
          continue;
        }
      } catch (orErr) {
        // network exception, try next free candidate
        continue;
      }
    }
  }

  // 2. REVERSE FAILOVER: Google Gemini
  markOpenRouterCooldown(30);
  console.warn("[Reverse Failover] OpenRouter unavailable or exhausted. Cascading seamlessly to Google Gemini fallback...");

  try {
    const geminiRes = await chatCompletion(model, messages, options);
    if (geminiRes.ok) {
      recordUsageEvent({ provider: "gemini", model: normalizeModelName(model), failover: true });
      return {
        response: geminiRes,
        provider: "gemini",
        model: normalizeModelName(model),
        failoverTriggered: true,
      };
    }

    return {
      response: geminiRes,
      provider: "gemini",
      model: normalizeModelName(model),
      failoverTriggered: true,
    };
  } catch (geminiError) {
    throw geminiError;
  }
}

export const FORMAT_RULES = `Output formatting rules that you must never break:
Never use asterisk characters for bold or italics. Never use hash characters for headings. Never use markdown syntax of any kind, including backticks outside of real code blocks.
When you list features, options, steps or any structured multi point data, start every single item with the bullet dot character followed by one space, like this:
• first point
• second point
Never use numbers, dashes or asterisks as list markers. Keep prose clean, natural and plain.`;

export function systemPrompt(opts: {
  userName: string;
  agentPrompt?: string;
  memories: string[];
}) {
  const parts = [
    `You are RB Agent, an elite personal AI assistant and multi agent automation hub for ${opts.userName}. You speak naturally in the language the user writes in, including Hindi and Hinglish.`,
    opts.agentPrompt ?? "You are the RB Agent core assistant and you can route work to your coding, phone automation, research, memory and social sub agents.",
    FORMAT_RULES,
  ];
  if (opts.memories.length) {
    parts.push(
      `Long term memory vault for this user. Apply these silently and never ask for them again:\n${opts.memories
        .map((m) => `• ${m}`)
        .join("\n")}`,
    );
  }
  return parts.join("\n\n");
}
