import { createFileRoute } from "@tanstack/react-router";
import {
  saveMediaPlaybackState,
  getMediaPlaybackState,
  getAllMediaStates,
  controlTermuxMediaPlayer,
  getTermuxMediaPlayerStatus,
} from "@/lib/media.server";

export const Route = createFileRoute("/api/media-state")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const url = new URL(request.url);
        const id = url.searchParams.get("id");
        const checkTermux = url.searchParams.get("termux") === "1";

        if (checkTermux) {
          const termuxStatus = await getTermuxMediaPlayerStatus();
          return new Response(JSON.stringify(termuxStatus), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }

        if (id) {
          const item = getMediaPlaybackState(id);
          return new Response(JSON.stringify(item || null), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }

        const all = getAllMediaStates();
        return new Response(JSON.stringify(all), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      },

      POST: async ({ request }) => {
        try {
          const body = (await request.json()) as {
            id?: string;
            title?: string;
            url?: string;
            type?: "audio" | "video";
            currentTime?: number;
            duration?: number;
            status?: "playing" | "paused" | "stopped";
            termuxCmd?: "play" | "pause" | "stop" | "resume";
            file?: string;
          };

          if (body.termuxCmd) {
            const result = await controlTermuxMediaPlayer(body.termuxCmd, body.file);
            return new Response(JSON.stringify(result), {
              status: 200,
              headers: { "Content-Type": "application/json" },
            });
          }

          if (!body.id) {
            return new Response(JSON.stringify({ error: "Missing media id" }), {
              status: 400,
              headers: { "Content-Type": "application/json" },
            });
          }

          const saved = saveMediaPlaybackState({
            id: body.id,
            title: body.title,
            url: body.url,
            type: body.type,
            currentTime: body.currentTime ?? 0,
            duration: body.duration,
            status: body.status,
          });

          return new Response(JSON.stringify(saved), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        } catch (err: any) {
          return new Response(JSON.stringify({ error: err?.message || "Failed to save media state" }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
          });
        }
      },
    },
  },
});
