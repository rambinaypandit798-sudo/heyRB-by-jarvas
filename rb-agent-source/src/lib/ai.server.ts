const GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta";

export function gatewayKey() {
  const key = process.env["GEMINI_API_KEY"] || process.env["LOVABLE_API_KEY"];
  if (!key) throw new Error("AI is not configured yet.");
  return key;
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
      console.error("embedding failed", res.status, await res.text());
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
) {
  const targetModel = normalizeModelName(model);
  const key = gatewayKey();
  const payload = formatGeminiPayload(messages, options);

  const request = () =>
    fetch(`${GEMINI_BASE}/models/${targetModel}:streamGenerateContent?alt=sse&key=${key}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

  const waitBeforeRetry = async (response?: Response) => {
    const retryAfter = Number(response?.headers.get("Retry-After"));
    const delay = Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter * 1000 : 700;
    await new Promise((resolve) => setTimeout(resolve, Math.min(delay, 3000)));
  };

  let response: Response;
  try {
    response = await request();
  } catch {
    await waitBeforeRetry();
    response = await request();
  }
  if (response.status === 429 || response.status >= 500) {
    await waitBeforeRetry(response);
    await response.body?.cancel();
    response = await request();
  }
  return response;
}

export async function completeOnce(model: string, messages: { role: string; content: string }[]) {
  try {
    const targetModel = normalizeModelName(model);
    const key = gatewayKey();
    const payload = formatGeminiPayload(messages);

    const res = await fetch(`${GEMINI_BASE}/models/${targetModel}:generateContent?key=${key}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) return null;
    const json = (await res.json()) as {
      candidates?: { content?: { parts?: { text?: string }[] } }[];
    };
    return json.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ?? null;
  } catch (error) {
    console.error("completeOnce failed", error);
    return null;
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
