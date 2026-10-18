import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Plus, Sparkles, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useSettings, useUpdateSettings } from "@/hooks/useAccount";
import { MemoryVault } from "@/components/MemoryVault";

export const Route = createFileRoute("/_authenticated/skills")({
  head: () => ({
    meta: [
      { title: "Skill Add — RB Agent" },
      { name: "description", content: "Add custom skills and standing instructions to RB Agent." },
      { property: "og:title", content: "Skill Add — RB Agent" },
      { property: "og:description", content: "Add custom skills and standing instructions." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Skills,
});

const BUILTIN = [
  { id: "automation", label: "Phone task execution", detail: "Runs device tasks end to end and speaks the result" },
  { id: "research", label: "Deep web research", detail: "Multi step browsing and synthesis" },
  { id: "github", label: "GitHub commits", detail: "Reads repositories and drafts commits" },
  { id: "telegram", label: "Telegram workflows", detail: "Bot replies and channel rules" },
];

function Skills() {
  const { data: settings } = useSettings();
  const updateSettings = useUpdateSettings();
  const [custom, setCustom] = useState<string[]>([]);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("rb-skills");
    if (saved) setCustom(JSON.parse(saved) as string[]);
  }, []);

  const persist = (next: string[]) => {
    setCustom(next);
    localStorage.setItem("rb-skills", JSON.stringify(next));
  };

  return (
    <AppShell title="Skill Add">
      <div className="mx-auto w-full max-w-2xl space-y-4 px-4 pt-4">
        <div className="glass rounded-3xl p-4">
          <p className="font-display flex items-center gap-2 text-sm font-semibold">
            <Sparkles className="size-4 text-primary" /> Built in skills
          </p>
          <div className="mt-3 space-y-3">
            {BUILTIN.map((skill) => (
              <div key={skill.id} className="flex items-start gap-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{skill.label}</p>
                  <p className="text-[11px] text-muted-foreground">{skill.detail}</p>
                </div>
                <Switch
                  checked={
                    skill.id === "automation" ? Boolean(settings?.automation_enabled) : true
                  }
                  onCheckedChange={(value) => {
                    if (skill.id === "automation")
                      updateSettings.mutate({ ...settings, automation_enabled: value });
                  }}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-3xl p-4">
          <p className="font-display text-sm font-semibold">Your custom skills</p>
          <p className="text-[11px] text-muted-foreground">
            Each skill is a standing instruction saved to your memory vault.
          </p>
          <div className="mt-3 flex gap-2">
            <Input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Always summarise long replies in five bullet points"
              className="glass h-11 rounded-xl border-0"
            />
            <Button
              className="h-11 rounded-xl"
              disabled={draft.trim().length < 4}
              onClick={() => {
                persist([draft.trim(), ...custom]);
                setDraft("");
                toast.success("Skill added");
              }}
            >
              <Plus className="size-4" />
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {custom.map((skill) => (
              <div key={skill} className="flex items-start gap-2">
                <p className="min-w-0 flex-1 text-sm leading-6">• {skill}</p>
                <button
                  type="button"
                  aria-label="Remove skill"
                  onClick={() => persist(custom.filter((s) => s !== skill))}
                  className="grid size-8 place-items-center rounded-full text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-3xl p-4">
          <p className="font-display text-sm font-semibold">Memory vault</p>
          <p className="mb-3 text-[11px] text-muted-foreground">
            Everything RB Agent remembers about you, editable at any time.
          </p>
          <MemoryVault />
        </div>
      </div>
    </AppShell>
  );
}
