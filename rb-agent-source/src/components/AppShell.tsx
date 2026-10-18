import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import {
  Code2,
  FileText,
  FolderKanban,
  Globe,
  Home,
  MessageSquare,
  Menu,
  PlusCircle,
  Search,
  Settings as SettingsIcon,
  Sparkles,
  Trash2,
  Waves,
} from "lucide-react";
import { toast } from "sonner";

import { BrandMark } from "@/components/BrandMark";
import { UsageBadge } from "@/components/UsageDashboard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useChats, useDeleteChat } from "@/hooks/useChats";
import { useSettings } from "@/hooks/useAccount";
import { createRecognition, readTranscript } from "@/lib/speech";

const NAV = [
  { to: "/", label: "Home", icon: Home },
  { to: "/web", label: "Web Preview", icon: Globe },
  { to: "/code", label: "Code Preview", icon: Code2 },
  { to: "/files", label: "File Preview", icon: FileText },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/skills", label: "Skill Add", icon: Sparkles },
] as const;

/** Background listener for the "Hey RB" wake phrase. */
function useWakeWord(enabled: boolean) {
  const [awake, setAwake] = useState(false);
  const navigate = useNavigate();
  const recRef = useRef<ReturnType<typeof createRecognition>>(null);

  useEffect(() => {
    if (!enabled) {
      recRef.current?.abort();
      recRef.current = null;
      return;
    }
    const rec = createRecognition("en-IN");
    if (!rec) return;
    recRef.current = rec;
    let stopped = false;
    rec.onresult = (event) => {
      const { text } = readTranscript(event);
      const lower = text.toLowerCase();
      if (lower.includes("hey rb") || lower.includes("hey are be") || text.includes("हे आरबी")) {
        setAwake(true);
        navigate({ to: "/" });
        setTimeout(() => setAwake(false), 6000);
      }
    };
    rec.onerror = () => undefined;
    rec.onend = () => {
      if (!stopped) {
        try {
          rec.start();
        } catch {
          // browser refused restart
        }
      }
    };
    try {
      rec.start();
    } catch {
      // ignore
    }
    return () => {
      stopped = true;
      rec.abort();
    };
  }, [enabled, navigate]);

  return awake;
}

function DrawerBody({ onNavigate }: { onNavigate: () => void }) {
  const { data: chats = [] } = useChats();
  const [query, setQuery] = useState("");
  const deleteChat = useDeleteChat();
  const filtered = chats.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()));
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2.5 px-4 pt-5">
        <BrandMark size={38} />
        <div>
          <p className="font-display text-base font-semibold leading-tight">RB Agent</p>
          <p className="text-[11px] text-muted-foreground">Personal AI Assistant</p>
        </div>
      </div>

      <nav aria-label="Main menu" className="mt-5 space-y-0.5 px-3">
        {NAV.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            aria-current={item.to === "/" ? pathname === "/" ? "page" : undefined : pathname.startsWith(item.to) ? "page" : undefined}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground aria-[current=page]:bg-accent aria-[current=page]:text-accent-foreground"
          >
            <item.icon className="size-4" /> {item.label}
          </Link>
        ))}
        <Link to="/" onClick={onNavigate} className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground">
          <MessageSquare className="size-4" /> Chats
        </Link>
      </nav>

      <div className="mt-5 px-4">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Recents
        </p>
        <div className="relative mt-2">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your history"
            className="glass h-10 rounded-xl border-0 pl-9 text-sm"
          />
        </div>
      </div>

      <div className="mt-2 min-h-0 flex-1 space-y-1 overflow-y-auto px-3 pb-3">
        {filtered.length === 0 ? (
          <p className="px-3 py-6 text-xs text-muted-foreground">
            No saved chats yet.
          </p>
        ) : null}
        {filtered.map((chat) => (
          <div
            key={chat.id}
            className="group flex items-center gap-1 rounded-xl transition-colors hover:bg-accent/70"
          >
            <Link
              to="/c/$chatId"
              params={{ chatId: chat.id }}
              onClick={onNavigate}
              className="min-w-0 flex-1 px-3 py-2.5 text-sm"
            >
              <span className="block truncate">{chat.title}</span>
              <span className="block text-[11px] text-muted-foreground">
                {new Date(chat.updated_at).toLocaleDateString()}
              </span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              type="button"
              aria-label={`Delete ${chat.title}`}
              onClick={() => {
                deleteChat.mutate(chat.id, {
                  onSuccess: () => toast.success("Chat deleted"),
                  onError: (error) => toast.error(error.message),
                });
              }}
              className="mr-2 size-8 shrink-0 text-muted-foreground hover:text-destructive sm:opacity-0 sm:group-hover:opacity-100"
            >
              <Trash2 className="size-4" />
            </Button>
          </div>
        ))}
      </div>

      <div className="border-t border-border/60 px-4 py-2.5 flex items-center justify-between text-xs text-muted-foreground">
        <span className="text-[11px] font-medium">Provider Status:</span>
        <UsageBadge />
      </div>

      <div className="border-t border-border p-3">
        <Button asChild className="h-auto w-full rounded-lg p-0">
        <Link
          to="/"
          onClick={onNavigate}
          className="flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold"
        >
          <PlusCircle className="size-4" /> New chat
        </Link>
        </Button>
      </div>
    </div>
  );
}

export function AppShell({ children, title }: { children: ReactNode; title?: string }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { data: settings } = useSettings();
  const awake = useWakeWord(Boolean(settings?.wake_word_enabled));

  return (
    <div className="flex min-h-screen flex-col">
      <header className="glass sticky top-0 z-40 flex items-center gap-3 px-4 py-3">
        <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
          <SheetTrigger asChild>
            <Button
              variant="secondary"
              size="icon"
              type="button"
              aria-label="Open menu"
              className="size-10 rounded-full"
            >
              <Menu className="size-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="glass-strong w-[86vw] max-w-sm border-0 p-0 sm:w-80">
            <DrawerBody onNavigate={() => setDrawerOpen(false)} />
          </SheetContent>
        </Sheet>

        <BrandMark size={36} />
        <div className="min-w-0 flex-1">
          <p className="font-display truncate text-[17px] font-semibold leading-tight">
            {title ?? "RB Agent"}
          </p>
          <p className="text-[11px] text-muted-foreground">Personal AI Assistant</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <UsageBadge />
          {settings?.wake_word_enabled ? (
            <span className="flex items-center gap-1 rounded-full bg-accent px-2.5 py-1 text-[10px] font-semibold text-accent-foreground">
              <Waves className="size-3" /> Hey RB
            </span>
          ) : null}
        </div>
      </header>

      {awake ? (
        <div className="fixed left-1/2 top-20 z-50 -translate-x-1/2">
          <div className="glass-strong flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold">
            <span className="size-2 animate-core-pulse rounded-full bg-primary" /> RB Agent is
            listening
          </div>
        </div>
      ) : null}

      <main className="min-h-0 flex-1">{children}</main>
    </div>
  );
}
