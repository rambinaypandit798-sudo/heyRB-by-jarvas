import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, ArrowRight, ExternalLink, RotateCw, Search } from "lucide-react";

import { AppShell } from "@/components/AppShell";
import { Input } from "@/components/ui/input";

export const Route = createFileRoute("/_authenticated/web")({
  head: () => ({
    meta: [
      { title: "Web Preview — RB Agent" },
      { name: "description", content: "Search Google and browse pages inside RB Agent." },
      { property: "og:title", content: "Web Preview — RB Agent" },
      { property: "og:description", content: "In-app Google search and web page viewer." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: WebPreview,
});

function toUrl(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return "";
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (/^[\w-]+(\.[\w-]+)+(\/.*)?$/.test(trimmed)) return `https://${trimmed}`;
  return `https://www.google.com/search?igu=1&q=${encodeURIComponent(trimmed)}`;
}

function WebPreview() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [index, setIndex] = useState(-1);
  const [nonce, setNonce] = useState(0);
  const current = index >= 0 ? history[index] : "";

  const go = (value: string) => {
    const url = toUrl(value);
    if (!url) return;
    const next = [...history.slice(0, index + 1), url];
    setHistory(next);
    setIndex(next.length - 1);
  };

  return (
    <AppShell title="Web Preview">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-3 px-4 pt-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            go(query);
          }}
          className="glass flex items-center gap-1.5 rounded-2xl p-1.5"
        >
          <button
            type="button"
            aria-label="Back"
            disabled={index <= 0}
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
            className="grid size-9 place-items-center rounded-full text-muted-foreground disabled:opacity-40"
          >
            <ArrowLeft className="size-4" />
          </button>
          <button
            type="button"
            aria-label="Forward"
            disabled={index >= history.length - 1}
            onClick={() => setIndex((i) => Math.min(history.length - 1, i + 1))}
            className="grid size-9 place-items-center rounded-full text-muted-foreground disabled:opacity-40"
          >
            <ArrowRight className="size-4" />
          </button>
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Google or enter a URL"
            className="h-10 flex-1 border-0 bg-transparent text-sm shadow-none focus-visible:ring-0"
          />
          <button
            type="button"
            aria-label="Reload"
            disabled={!current}
            onClick={() => setNonce((n) => n + 1)}
            className="grid size-9 place-items-center rounded-full text-muted-foreground disabled:opacity-40"
          >
            <RotateCw className="size-4" />
          </button>
          <button
            type="submit"
            className="grid size-9 place-items-center rounded-full bg-primary text-primary-foreground"
            aria-label="Go"
          >
            <Search className="size-4" />
          </button>
        </form>

        {current ? (
          <div className="flex items-center justify-between gap-2 px-1">
            <p className="truncate text-[11px] text-muted-foreground">{current}</p>
            <a
              href={current}
              target="_blank"
              rel="noreferrer"
              className="flex shrink-0 items-center gap-1 text-[11px] font-semibold text-primary"
            >
              Open in new tab <ExternalLink className="size-3" />
            </a>
          </div>
        ) : null}

        <div className="glass h-[calc(100vh-15rem)] overflow-hidden rounded-3xl">
          {current ? (
            <iframe
              key={`${current}-${nonce}`}
              src={current}
              title="Web preview"
              className="size-full bg-background"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          ) : (
            <div className="grid h-full place-items-center px-8 text-center">
              <div>
                <p className="font-display text-lg font-semibold">Browse without leaving RB Agent</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Type a question to search Google, or paste any web address.
                </p>
              </div>
            </div>
          )}
        </div>
        <p className="px-1 pb-2 text-[11px] text-muted-foreground">
          Some websites block being shown inside other apps. Use Open in new tab for those.
        </p>
      </div>
    </AppShell>
  );
}
