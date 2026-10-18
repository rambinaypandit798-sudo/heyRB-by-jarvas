import { createFileRoute } from "@tanstack/react-router";
import { createClient } from "@supabase/supabase-js";

import { agentById } from "@/lib/agents";
import { hasMemoryTrigger } from "@/lib/memory-triggers";
import { chatCompletion, completeOnce, embed, systemPrompt } from "@/lib/ai.server";
import { usableModel } from "@/lib/models";
import {
  isLiveInformationQuery,
  searchLiveWeb,
  formatSearchGroundingContext,
  formatSourceCitations,
  SearchResult,
} from "@/lib/search.server";

type Incoming = {
  agent?: string;
  model?: string;
  messages?: { role: "user" | "assistant"; content: string }[];
};

function json(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export const Route = createFileRoute("/api/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const token = request.headers.get("authorization")?.replace(/^Bearer\s+/i, "");
        let user: { id: string } = { id: "00000000-0000-0000-0000-000000000000" };
        let profileName: string | null = "Ram";

        const headers: Record<string, string> = {};
        if (token && token !== "bypass-local-token") {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const supabase = createClient(
          process.env["SUPABASE_URL"]!,
          process.env["SUPABASE_PUBLISHABLE_KEY"]!,
          {
            auth: { persistSession: false, autoRefreshToken: false },
            global: { headers },
          },
        );

        if (token && token !== "bypass-local-token") {
          const { data: userData } = await supabase.auth.getUser(token);
          if (userData?.user) {
            user = userData.user;
          }
        }

        const body = (await request.json()) as Incoming;
        const history = (body.messages ?? []).filter((m) => m.content?.trim()).slice(-24);
        const lastUser = [...history].reverse().find((m) => m.role === "user")?.content ?? "";
        if (!lastUser) return json({ error: "Nothing to send." }, 400);

        const model = usableModel(body.model);
        const agent = agentById(body.agent ?? "");

        try {
          const { data: profile } = await supabase
            .from("profiles")
            .select("display_name")
            .eq("id", user.id)
            .maybeSingle();
          if (profile?.display_name) profileName = profile.display_name;
        } catch {}

        // Long term memory retrieval through the vector index.
        let memories: string[] = [];
        const vector = await embed(lastUser);
        if (vector) {
          const { data: matches } = await supabase.rpc("match_memories", {
            p_embedding: vector as unknown as string,
            p_limit: 6,
          });
          memories = ((matches ?? []) as { content: string; similarity: number }[])
            .filter((m) => m.similarity > 0.15)
            .map((m) => m.content);
        }

        // Memory capture: the user explicitly asked RB Agent to remember something.
        let savedMemory: string | null = null;
        if (hasMemoryTrigger(lastUser)) {
          const extracted = await completeOnce(model, [
            {
              role: "system",
              content:
                "Extract the single durable fact or preference the user wants stored, as one short plain sentence in the user's own language. No markdown, no quotes, no preamble. If there is nothing durable, reply exactly NONE.",
            },
            { role: "user", content: lastUser },
          ]);
          if (extracted && extracted.toUpperCase() !== "NONE") {
            savedMemory = extracted;
            const memVector = await embed(extracted);
            if (user.id !== "00000000-0000-0000-0000-000000000000") {
              try {
                await supabase.from("memories").insert({
                  user_id: user.id,
                  content: extracted,
                  kind: "preference",
                  embedding: memVector as unknown as string,
                });
              } catch {}
            }
            if (!memories.includes(extracted)) memories.unshift(extracted);
          }
        }

        // Live Internet Search & Real-Time Grounding
        let searchGroundingPrompt = "";
        let searchResults: SearchResult[] = [];
        const isSearchIntent = isLiveInformationQuery(lastUser) || body.agent === "research" || body.agent === "view";

        if (isSearchIntent) {
          try {
            searchResults = await searchLiveWeb(lastUser, 4);
            if (searchResults.length > 0) {
              searchGroundingPrompt = formatSearchGroundingContext(searchResults);
            }
          } catch (searchErr) {
            console.error("Live web search fetch failed:", searchErr);
          }
        }

        const messages = [
          {
            role: "system",
            content:
              systemPrompt({
                userName: profileName ?? "friend",
                agentPrompt: agent?.prompt ?? "You are RB Agent, the general personal assistant.",
                memories,
              }) +
              (savedMemory
                ? `\n\nYou just stored this in the memory vault, confirm it briefly in one line: ${savedMemory}`
                : "") +
              (searchGroundingPrompt ? `\n\n${searchGroundingPrompt}` : ""),
          },
          ...history.map((m) => ({ role: m.role, content: m.content })),
        ];

        let upstream: Response;
        try {
          upstream = await chatCompletion(model, messages, { enableGoogleSearch: true });
        } catch (error) {
          console.error("Gemini API service connection failed", error);
          return json({ error: "The AI service is temporarily unavailable. Please retry your message." }, 503);
        }

        if (!upstream.ok || !upstream.body) {
          let upstreamMessage = "";
          try {
            const payload = (await upstream.json()) as {
              message?: string;
              error?: { message?: string; code?: number; status?: string } | string;
            };
            upstreamMessage =
              (typeof payload.error === "object" ? payload.error?.message : payload.error) ??
              payload.message ??
              "";
          } catch {
            await upstream.body?.cancel();
          }
          console.error("Gemini API upstream error", upstream.status, upstreamMessage);

          // Autonomous Self-Healing Fallback: If upstream hits 429 quota or 503, provide verified live search results
          if (searchResults.length > 0 && (upstream.status === 429 || upstream.status === 503)) {
            const answer = `Here are the latest live facts retrieved for "${lastUser}":\n\n` +
              searchResults.map((r) => `• ${r.title}: ${r.snippet}`).join("\n\n") +
              formatSourceCitations(searchResults);

            return new Response(answer, {
              headers: {
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "no-cache",
                "X-Search-Grounding": "1",
                "X-Live-Search-Fallback": "1",
              },
            });
          }

          if (upstream.status === 429) {
            const greetingMatch = /^(hi|hello|hey|namaste|नमस्ते|who are you|what is your mission|what can you do|help)/i.test(lastUser.trim());
            if (greetingMatch) {
              const fallbackText = `नमस्ते, Ram Binay Pandit! I am RB (Robotic Brain / Rapid Butler), your autonomous personal operating system agent.

• Direct Hardware Control: Battery, torch, clipboard, notifications, and Termux terminal integration.
• Autonomous Code & Automation: Continuous task execution, Ralph Loop, GSD-Core, and CodeRabbit code audits.
• Dynamic Memory & Notes: Local SQLite storage synchronized with Supabase cloud.
• Live Internet Research: Real-time search grounding and source citation verification.

(Note: Google Gemini cloud API is currently cooling down from a rate-limit quota. Cloud reasoning will resume automatically.)`;
              return new Response(fallbackText, {
                headers: {
                  "Content-Type": "text/plain; charset=utf-8",
                  "Cache-Control": "no-cache",
                  "X-Autonomous-Fallback": "1",
                },
              });
            }
            return json({ error: upstreamMessage || "Google Gemini API rate limit reached. Please retry in a few moments." }, 429);
          }
          if (upstream.status === 402)
            return json({ error: upstreamMessage || "AI credits are exhausted. Add credits to keep chatting." }, 402);
          if (upstream.status === 401)
            return json({ error: upstreamMessage || "Invalid Gemini API key. Please check your GEMINI_API_KEY." }, 401);
          if (upstream.status === 403)
            return json({ error: upstreamMessage || "This AI request is not permitted." }, 403);
          if (upstream.status === 400 || upstream.status === 404)
            return json({ error: upstreamMessage || "The selected AI model could not process this request." }, upstream.status);
          return json({ error: upstreamMessage || "The AI service is temporarily unavailable. Please retry your message." }, 503);
        }

        const decoder = new TextDecoder();
        const encoder = new TextEncoder();
        let buffer = "";
        let fullOutputText = "";

        const stream = new ReadableStream<Uint8Array>({
          async start(controller) {
            const body = upstream.body;
            if (!body) {
              controller.close();
              return;
            }
            const reader = body.getReader();
            try {
              for (;;) {
                const { done, value } = await reader.read();
                if (done) {
                  if (
                    searchResults.length > 0 &&
                    !fullOutputText.includes("Sources & References") &&
                    !fullOutputText.includes("http://") &&
                    !fullOutputText.includes("https://")
                  ) {
                    const citations = formatSourceCitations(searchResults);
                    controller.enqueue(encoder.encode(citations));
                  }
                  break;
                }
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() ?? "";
                for (const line of lines) {
                  const trimmed = line.trim();
                  if (!trimmed.startsWith("data:")) continue;
                  const payload = trimmed.slice(5).trim();
                  if (!payload || payload === "[DONE]") continue;
                  try {
                    const parsed = JSON.parse(payload) as {
                      candidates?: {
                        content?: { parts?: { text?: string }[] };
                        groundingMetadata?: {
                          groundingChunks?: { web?: { uri?: string; title?: string } }[];
                        };
                      }[];
                      choices?: { delta?: { content?: string } }[];
                    };
                    const delta =
                      parsed.candidates?.[0]?.content?.parts?.[0]?.text ??
                      parsed.choices?.[0]?.delta?.content;
                    if (delta) {
                      fullOutputText += delta;
                      controller.enqueue(encoder.encode(delta));
                    }

                    // Extract native grounding chunks if provided by Gemini
                    const nativeChunks = parsed.candidates?.[0]?.groundingMetadata?.groundingChunks;
                    if (Array.isArray(nativeChunks)) {
                      for (const c of nativeChunks) {
                        if (c.web?.uri && c.web?.title && !searchResults.some((r) => r.url === c.web?.uri)) {
                          searchResults.push({
                            title: c.web.title,
                            url: c.web.uri,
                            snippet: "",
                          });
                        }
                      }
                    }
                  } catch {
                    // partial frame, ignore
                  }
                }
              }
            } catch (error) {
              console.error("stream error", error);
            } finally {
              controller.close();
              reader.releaseLock();
            }
          },
        });

        return new Response(stream, {
          headers: {
            "Content-Type": "text/plain; charset=utf-8",
            "Cache-Control": "no-cache",
            "X-Memory-Saved": savedMemory ? "1" : "0",
            "X-Search-Grounding": searchResults.length > 0 ? "1" : "0",
          },
        });
      },
    },
  },
});
