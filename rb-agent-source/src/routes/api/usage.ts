import { createFileRoute } from "@tanstack/react-router";
import { getUsageMetrics } from "@/lib/usage.server";

export const Route = createFileRoute("/api/usage")({
  server: {
    handlers: {
      GET: async () => {
        const stats = getUsageMetrics();
        return new Response(JSON.stringify(stats), {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
          },
        });
      },
    },
  },
});
