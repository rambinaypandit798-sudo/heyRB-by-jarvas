import { Brain, Code2, Eye, Globe2, Smartphone, ArrowUpRight, type LucideIcon } from "lucide-react";

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { InputBar } from "@/components/InputBar";
import { AGENTS, type AgentId } from "@/lib/agents";
import { BrandMark } from "@/components/BrandMark";
import { Link } from "@tanstack/react-router";

const ICONS: Record<string, LucideIcon> = {
  code: Code2,
  smartphone: Smartphone,
  globe: Globe2,
  brain: Brain,
  eye: Eye,
};

export function AgentHub({
  open,
  onOpenChange,
  onSelect,
  active,
  model,
  onModelChange,
  onSend,
  busy,
  liveMode,
  onLiveModeChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelect: (agent: AgentId) => void;
  active: AgentId;
  model: string;
  onModelChange: (id: string) => void;
  onSend: (text: string) => void;
  busy: boolean;
  liveMode: boolean;
  onLiveModeChange: (on: boolean) => void;
}) {
  const selected = AGENTS.find((agent) => agent.id === active && agent.id !== "social");
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="agent-workspace fixed inset-0 left-0 top-0 z-50 flex h-[100dvh] w-screen max-w-none translate-x-0 translate-y-0 flex-col overflow-y-auto rounded-none border-0 px-5 py-8 shadow-none data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 sm:px-10">
        <DialogHeader className="mx-auto w-full max-w-4xl items-start pt-8 text-left sm:pt-14">
          <div className="mb-8 flex items-center gap-3"><BrandMark size={40} /><span className="text-sm font-semibold text-primary">RB AGENT / WORKSPACE</span></div>
          <DialogTitle className="font-display text-3xl font-semibold sm:text-5xl">{selected?.name ?? "Choose your specialist"}</DialogTitle>
          <DialogDescription className="mt-3 max-w-xl text-base text-muted-foreground">
            {selected?.domain ?? "Five focused workspaces. One connected mind."}
          </DialogDescription>
        </DialogHeader>

        {selected ? <div className="mx-auto mt-10 flex w-full max-w-4xl flex-1 flex-col">
          <Button variant="ghost" className="w-fit text-primary" onClick={() => onSelect("core")}>← All agents</Button>
          <div className="flex flex-1 flex-col items-center justify-center gap-6 py-12 text-center">
            <div className="agent-workspace-emblem grid size-24 place-items-center rounded-full border border-primary/50 bg-primary/10 text-primary">
              {(() => { const Icon = ICONS[selected.icon] ?? Brain; return <Icon className="size-10" />; })()}
            </div>
            <p className="max-w-md text-sm text-muted-foreground">{selected.domain}</p>
            {selected.id === "research" ? <Link className="text-sm font-medium text-primary underline" to="/web" onClick={() => onOpenChange(false)}>Open Web Preview ↗</Link> : null}
            {selected.id === "preview" ? <Link className="text-sm font-medium text-primary underline" to="/files" onClick={() => onOpenChange(false)}>Open File Preview ↗</Link> : null}
            {selected.id === "coding" ? <Link className="text-sm font-medium text-primary underline" to="/code" onClick={() => onOpenChange(false)}>Open Code Preview ↗</Link> : null}
            {selected.id === "memory" ? <Link className="text-sm font-medium text-primary underline" to="/settings" onClick={() => onOpenChange(false)}>Open Memory Vault ↗</Link> : null}
            {selected.id === "automation" ? <Link className="text-sm font-medium text-primary underline" to="/skills" onClick={() => onOpenChange(false)}>Open Skills ↗</Link> : null}
          </div>
          <div className="w-full pb-5"><InputBar model={model} onModelChange={onModelChange} onSend={onSend} busy={busy} liveMode={liveMode} onLiveModeChange={onLiveModeChange} agentLabel={selected.name} /></div>
        </div> : <div className="mx-auto mt-10 grid w-full max-w-4xl gap-3 pb-10 md:grid-cols-2">
          {AGENTS.filter((agent) => agent.id !== "social").map((agent, index) => {
            const Icon = ICONS[agent.icon] ?? Brain;
            return (
              <Button
                key={agent.id}
                type="button"
                variant="ghost"
                onClick={() => onSelect(agent.id)}
                style={{ animationDelay: `${index * 45}ms` }}
                className={`agent-workspace-item animate-rise group flex h-auto min-h-32 w-full items-center justify-start gap-4 rounded-lg border border-border p-5 text-left whitespace-normal transition-all hover:-translate-y-1 hover:bg-accent/60 ${
                  active === agent.id ? "ring-2 ring-ring" : ""
                }`}
              >
                <span className="grid size-12 shrink-0 place-items-center rounded-full bg-primary/15 text-primary">
                  <Icon className="size-6" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-base font-semibold text-foreground">{agent.name}</span>
                  <span className="mt-1 block text-xs font-normal text-muted-foreground">{agent.domain}</span>
                </span>
                <ArrowUpRight className="size-5 shrink-0 text-primary" />
              </Button>
            );
          })}
        </div>}
      </DialogContent>
    </Dialog>
  );
}
