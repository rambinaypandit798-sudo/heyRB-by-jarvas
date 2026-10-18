import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { FileText, Image as ImageIcon, Trash2, Upload } from "lucide-react";

import { AppShell } from "@/components/AppShell";

export const Route = createFileRoute("/_authenticated/files")({
  head: () => ({
    meta: [
      { title: "File Preview — RB Agent" },
      { name: "description", content: "Upload and inspect PDFs, images and text files inside RB Agent." },
      { property: "og:title", content: "File Preview — RB Agent" },
      { property: "og:description", content: "Document handling panel for PDFs, images and text files." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: FilePreview,
});

type Item = { id: string; name: string; type: string; size: number; url: string; text?: string };

function human(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function FilePreview() {
  const [items, setItems] = useState<Item[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const active = items.find((i) => i.id === activeId) ?? null;

  useEffect(() => {
    return () => items.forEach((item) => URL.revokeObjectURL(item.url));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const add = async (list: FileList | null) => {
    if (!list?.length) return;
    const next: Item[] = [];
    for (const file of Array.from(list)) {
      const item: Item = {
        id: `${file.name}-${file.size}-${Date.now()}`,
        name: file.name,
        type: file.type || "application/octet-stream",
        size: file.size,
        url: URL.createObjectURL(file),
      };
      if (file.type.startsWith("text/") || /\.(txt|md|csv|json)$/i.test(file.name)) {
        item.text = (await file.text()).slice(0, 40000);
      }
      next.push(item);
    }
    setItems((prev) => [...next, ...prev]);
    setActiveId(next[0]?.id ?? null);
  };

  return (
    <AppShell title="File Preview">
      <div className="mx-auto w-full max-w-3xl space-y-4 px-4 pt-4">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="glass flex w-full flex-col items-center gap-2 rounded-3xl p-8 text-center"
        >
          <span className="grid size-12 place-items-center rounded-2xl bg-accent text-accent-foreground">
            <Upload className="size-5" />
          </span>
          <span className="font-display text-base font-semibold">Upload a document</span>
          <span className="text-xs text-muted-foreground">PDF, images, text, markdown, CSV and JSON</span>
        </button>
        <input
          ref={inputRef}
          type="file"
          multiple
          hidden
          accept=".pdf,.txt,.md,.csv,.json,image/*"
          onChange={(e) => add(e.target.files)}
        />

        {items.length ? (
          <div className="space-y-2">
            {items.map((item) => (
              <div
                key={item.id}
                className={`glass flex items-center gap-3 rounded-2xl p-3 ${
                  activeId === item.id ? "ring-2 ring-ring" : ""
                }`}
              >
                <button
                  type="button"
                  onClick={() => setActiveId(item.id)}
                  className="flex min-w-0 flex-1 items-center gap-3 text-left"
                >
                  <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent text-accent-foreground">
                    {item.type.startsWith("image/") ? (
                      <ImageIcon className="size-4" />
                    ) : (
                      <FileText className="size-4" />
                    )}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold">{item.name}</span>
                    <span className="block text-[11px] text-muted-foreground">
                      {human(item.size)} · {item.type}
                    </span>
                  </span>
                </button>
                <button
                  type="button"
                  aria-label={`Remove ${item.name}`}
                  onClick={() => {
                    URL.revokeObjectURL(item.url);
                    setItems((prev) => prev.filter((i) => i.id !== item.id));
                    if (activeId === item.id) setActiveId(null);
                  }}
                  className="grid size-9 place-items-center rounded-full text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            ))}
          </div>
        ) : null}

        {active ? (
          <div className="glass overflow-hidden rounded-3xl">
            <p className="border-b border-border px-4 py-3 text-sm font-semibold">{active.name}</p>
            {active.type.startsWith("image/") ? (
              <img src={active.url} alt={active.name} className="max-h-[60vh] w-full object-contain" />
            ) : active.type === "application/pdf" ? (
              <iframe src={active.url} title={active.name} className="h-[70vh] w-full" />
            ) : active.text !== undefined ? (
              <pre className="max-h-[60vh] overflow-auto px-4 py-3 text-xs leading-5 whitespace-pre-wrap">
                {active.text}
              </pre>
            ) : (
              <p className="px-4 py-6 text-sm text-muted-foreground">
                This file type cannot be previewed here.
              </p>
            )}
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}
