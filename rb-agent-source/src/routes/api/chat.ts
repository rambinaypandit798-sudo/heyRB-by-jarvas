import { createFileRoute } from "@tanstack/react-router";
import { createClient } from "@supabase/supabase-js";

import { agentById } from "@/lib/agents";
import { hasMemoryTrigger } from "@/lib/memory-triggers";
import { chatCompletion, completeOnce, embed, systemPrompt } from "@/lib/ai.server";
import { usableModel } from "@/lib/models";

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
                : ""),
          },
          ...history.map((m) => ({ role: m.role, content: m.content })),
        ];

        let upstream: Response;
        try {
          upstream = await chatCompletion(model, messages);
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
          if (upstream.status === 429)
            return json({ error: upstreamMessage || "Too many requests right now. Try again in a moment." }, 429);
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
                if (done) break;
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
                      candidates?: { content?: { parts?: { text?: string }[] } }[];
                      choices?: { delta?: { content?: string } }[];
                    };
                    const delta =
                      parsed.candidates?.[0]?.content?.parts?.[0]?.text ??
                      parsed.choices?.[0]?.delta?.content;
                    if (delta) controller.enqueue(encoder.encode(delta));
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
          },
        });
      },
    },
  },
});
