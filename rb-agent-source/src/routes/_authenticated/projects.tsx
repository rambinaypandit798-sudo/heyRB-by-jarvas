import { createFileRoute, Link } from "@tanstack/react-router";

import { AppShell } from "@/components/AppShell";
import { useChats } from "@/hooks/useChats";
import { AGENTS, agentName } from "@/lib/agents";

export const Route = createFileRoute("/_authenticated/projects")({
  head: () => ({
    meta: [
      { title: "Projects — RB Agent" },
      { name: "description", content: "Your RB Agent conversations grouped by specialist agent." },
      { property: "og:title", content: "Projects — RB Agent" },
      { property: "og:description", content: "Conversations grouped by specialist agent." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Projects,
});

function Projects() {
  const { data: chats = [] } = useChats();
  const groups = [{ id: "core", name: "RB Agent Core" }, ...AGENTS.map((a) => ({ id: a.id, name: a.name }))];

  return (
    <AppShell title="Projects">
      <div className="mx-auto w-full max-w-2xl space-y-4 px-4 pt-4">
        {groups.map((group) => {
          const items = chats.filter((c) => c.agent === group.id);
          return (
            <div key={group.id} className="glass rounded-3xl p-4">
              <p className="font-display text-sm font-semibold">{group.name}</p>
              <p className="text-[11px] text-muted-foreground">
                {items.length} {items.length === 1 ? "conversation" : "conversations"}
              </p>
              <div className="mt-3 space-y-1">
                {items.slice(0, 6).map((chat) => (
                  <Link
                    key={chat.id}
                    to="/c/$chatId"
                    params={{ chatId: chat.id }}
                    className="block truncate rounded-xl px-2.5 py-2 text-sm transition-colors hover:bg-accent"
                  >
                    • {chat.title}
                  </Link>
                ))}
                {items.length === 0 ? (
                  <p className="px-1 text-xs text-muted-foreground">
                    Nothing here yet. Open {agentName(group.id)} from the agent hub to start.
                  </p>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </AppShell>
  );
}
