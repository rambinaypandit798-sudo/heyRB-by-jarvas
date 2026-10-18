import { createFileRoute } from "@tanstack/react-router";
import { launchAndroidIntent, parseIntentFromQuery, type IntentAction } from "@/lib/intent.server";

export const Route = createFileRoute("/api/intent")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        try {
          const body = (await request.json()) as {
            text?: string;
            intent?: IntentAction;
          };

          let targetIntent: IntentAction | null = body.intent ?? null;
          if (!targetIntent && body.text) {
            targetIntent = parseIntentFromQuery(body.text);
          }

          if (!targetIntent) {
            return new Response(JSON.stringify({ error: "Could not parse intent from request" }), {
              status: 400,
              headers: { "Content-Type": "application/json" },
            });
          }

          const clientPlatform = (request.headers.get("x-client-platform") ||
            (body as any).clientPlatform) as "native" | "web" | undefined;

          const result = await launchAndroidIntent(targetIntent, { clientPlatform });
          return new Response(
            JSON.stringify({
              intent: targetIntent,
              result,
            }),
            {
              status: 200,
              headers: { "Content-Type": "application/json" },
            }
          );
        } catch (err: any) {
          return new Response(JSON.stringify({ error: err?.message || "Intent execution failed" }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
          });
        }
      },
    },
  },
});
