import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  Check,
  Github,
  LogOut,
  MessageCircle,
  Mic2,
  Play,
  Send,
  Smartphone,
  Sparkles,
  User,
  Waves,
} from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/AppShell";
import { MemoryVault } from "@/components/MemoryVault";
import { UsageDashboard } from "@/components/UsageDashboard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useProfile, useSettings, useUpdateSettings } from "@/hooks/useAccount";
import { supabase } from "@/integrations/supabase/client";
import { MODELS } from "@/lib/models";
import { speechEngine } from "@/lib/speech";
import { VOICE_PROFILES } from "@/lib/voices";

export const Route = createFileRoute("/_authenticated/settings")({
  head: () => ({
    meta: [
      { title: "Settings — RB Agent" },
      {
        name: "description",
        content: "Configure voices, memory vault, wake word, automation and integrations for RB Agent.",
      },
      { property: "og:title", content: "Settings — RB Agent" },
      { property: "og:description", content: "Voices, memory vault, wake word, automation and integrations." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: SettingsScreen,
});

function Section({
  icon: Icon,
  title,
  hint,
  children,
}: {
  icon: typeof User;
  title: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="glass rounded-3xl p-4">
      <p className="font-display flex items-center gap-2 text-sm font-semibold">
        <Icon className="size-4 text-primary" /> {title}
      </p>
      {hint ? <p className="mt-0.5 text-[11px] text-muted-foreground">{hint}</p> : null}
      <div className="mt-3">{children}</div>
    </section>
  );
}

function SettingsScreen() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: profile } = useProfile();
  const { data: settings } = useSettings();
  const update = useUpdateSettings();

  const [name, setName] = useState("");
  const [telegram, setTelegram] = useState("");
  const [whatsapp, setWhatsapp] = useState("");
  const [github, setGithub] = useState("");
  const [repo, setRepo] = useState("");

  useEffect(() => setName(profile?.display_name ?? ""), [profile?.display_name]);
  useEffect(() => {
    setTelegram(settings?.telegram_bot_token ?? "");
    setWhatsapp(settings?.whatsapp_api_key ?? "");
    setGithub(settings?.github_token ?? "");
    setRepo(settings?.github_repo ?? "");
  }, [settings]);

  const patch = (values: Record<string, unknown>) => update.mutate({ ...settings, ...values });

  const saveName = async () => {
    try {
      const { data: auth } = await supabase.auth.getUser();
      if (auth?.user) {
        const { error } = await supabase
          .from("profiles")
          .upsert({ id: auth.user.id, display_name: name.trim() || "Ram" });
        if (!error) {
          queryClient.invalidateQueries({ queryKey: ["profile"] });
          toast.success("Name updated");
          return;
        }
      }
    } catch {}

    if (typeof window !== "undefined") {
      localStorage.setItem("rb_profile_name", name.trim() || "Ram");
    }
    queryClient.setQueryData(["profile"], {
      id: "00000000-0000-0000-0000-000000000000",
      display_name: name.trim() || "Ram",
    });
    toast.success("Name updated");
  };

  return (
    <AppShell title="Settings">
      <div className="mx-auto w-full max-w-2xl space-y-4 px-4 pt-4">
        <Section icon={User} title="Your profile" hint="Used in the greeting and by every agent.">
          <div className="flex gap-2">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              className="glass h-11 rounded-xl border-0"
            />
            <Button className="h-11 rounded-xl" onClick={saveName}>
              Save
            </Button>
          </div>
        </Section>

        <Section
          icon={Activity}
          title="AI Usage & Smart Failover"
          hint="Real-time request metrics, token analytics, and failover status between Google Gemini and OpenRouter."
        >
          <UsageDashboard />
        </Section>

        <Section
          icon={Mic2}
          title="Voice profiles"
          hint="Preview a voice, then set it as your permanent reading voice."
        >
          <div className="space-y-2">
            {VOICE_PROFILES.map((voice) => {
              const active = settings?.voice_profile === voice.id;
              return (
                <div
                  key={voice.id}
                  className={`flex items-center gap-2 rounded-2xl p-3 transition-colors ${
                    active ? "bg-accent text-accent-foreground" : "bg-card"
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold">{voice.name}</p>
                    <p className="text-[11px] text-muted-foreground">{voice.tone}</p>
                  </div>
                  <button
                    type="button"
                    aria-label={`Preview ${voice.name}`}
                    onClick={() =>
                      speechEngine.speak(
                        `preview-${voice.id}`,
                        `नमस्ते, मैं ${voice.name} हूँ। I am your RB Agent voice, ready whenever you need me.`,
                        voice.id,
                      )
                    }
                    className="grid size-9 place-items-center rounded-full bg-primary text-primary-foreground"
                  >
                    <Play className="size-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => patch({ voice_profile: voice.id })}
                    className="rounded-full px-3 py-1.5 text-xs font-semibold text-primary"
                  >
                    {active ? <Check className="size-4" /> : "Set default"}
                  </button>
                </div>
              );
            })}
          </div>
        </Section>

        <Section icon={Sparkles} title="Default Gemini model">
          <div className="space-y-2">
            {MODELS.map((model) => (
              <Button
                key={model.id}
                type="button"
                variant="ghost"
                disabled={model.available === false}
                onClick={() => patch({ model: model.id })}
                className={`flex h-auto w-full items-center justify-start gap-2 rounded-lg p-3 text-left whitespace-normal ${
                  settings?.model === model.id ? "bg-accent text-accent-foreground" : "bg-card"
                }`}
              >
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-semibold">{model.label}</span>
                  <span className="block truncate text-[11px] text-muted-foreground">
                    {model.tier} · {model.blurb}
                  </span>
                </span>
                {settings?.model === model.id ? <Check className="size-4 text-primary" /> : null}
              </Button>
            ))}
          </div>
        </Section>

        <Section
          icon={Waves}
          title="System controls and automation"
          hint="Wake word listening runs in this app while it stays open."
        >
          <div className="space-y-3.5">
            <div className="flex items-center gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">Hey RB wake word</p>
                <p className="text-[11px] text-muted-foreground">
                  Listens in the background and opens a listening overlay.
                </p>
              </div>
              <Switch
                checked={Boolean(settings?.wake_word_enabled)}
                onCheckedChange={(value) => patch({ wake_word_enabled: value })}
              />
            </div>
            <div className="flex items-center gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">Live subtitles</p>
                <p className="text-[11px] text-muted-foreground">
                  Shows spoken text in real time during voice replies.
                </p>
              </div>
              <Switch
                checked={settings?.live_subtitles !== false}
                onCheckedChange={(value) => patch({ live_subtitles: value })}
              />
            </div>
            <div className="flex items-center gap-3">
              <div className="min-w-0 flex-1">
                <p className="flex items-center gap-1.5 text-sm font-medium">
                  <Smartphone className="size-3.5" /> Phone task execution
                </p>
                <p className="text-[11px] text-muted-foreground">
                  Lets the automation agent plan and run device tasks, then speak the result.
                </p>
              </div>
              <Switch
                checked={Boolean(settings?.automation_enabled)}
                onCheckedChange={(value) => patch({ automation_enabled: value })}
              />
            </div>
          </div>
        </Section>

        <Section
          icon={Send}
          title="Telegram bot"
          hint="Connect @RBAgentBot or your own bot token."
        >
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <p className="min-w-0 flex-1 text-sm font-medium">Enable Telegram</p>
              <Switch
                checked={Boolean(settings?.telegram_enabled)}
                onCheckedChange={(value) => patch({ telegram_enabled: value })}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="telegram">Bot token</Label>
              <Input
                id="telegram"
                type="password"
                value={telegram}
                onChange={(e) => setTelegram(e.target.value)}
                onBlur={() => patch({ telegram_bot_token: telegram || null })}
                placeholder="123456:ABC-DEF…"
                className="glass h-11 rounded-xl border-0"
              />
            </div>
          </div>
        </Section>

        <Section icon={MessageCircle} title="WhatsApp API">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <p className="min-w-0 flex-1 text-sm font-medium">Enable WhatsApp</p>
              <Switch
                checked={Boolean(settings?.whatsapp_enabled)}
                onCheckedChange={(value) => patch({ whatsapp_enabled: value })}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="whatsapp">API key</Label>
              <Input
                id="whatsapp"
                type="password"
                value={whatsapp}
                onChange={(e) => setWhatsapp(e.target.value)}
                onBlur={() => patch({ whatsapp_api_key: whatsapp || null })}
                className="glass h-11 rounded-xl border-0"
              />
            </div>
          </div>
        </Section>

        <Section
          icon={Github}
          title="GitHub"
          hint="Your token stays on the server and is only used for your repository reads."
        >
          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="ghtoken">Personal access token</Label>
              <Input
                id="ghtoken"
                type="password"
                value={github}
                onChange={(e) => setGithub(e.target.value)}
                onBlur={() => patch({ github_token: github || null })}
                placeholder="ghp_…"
                className="glass h-11 rounded-xl border-0"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="ghrepo">Default repository</Label>
              <Input
                id="ghrepo"
                value={repo}
                onChange={(e) => setRepo(e.target.value)}
                onBlur={() => patch({ github_repo: repo || null })}
                placeholder="owner/repository"
                className="glass h-11 rounded-xl border-0"
              />
            </div>
          </div>
        </Section>

        <Section icon={Sparkles} title="Memory vault" hint="View, edit or delete anything RB Agent remembers.">
          <MemoryVault />
        </Section>

        <Button
          variant="ghost"
          className="mb-4 w-full rounded-2xl text-muted-foreground hover:text-destructive"
          onClick={async () => {
            try {
              await supabase.auth.signOut();
            } catch {}
            queryClient.clear();
            if (typeof window !== "undefined") {
              localStorage.clear();
            }
            toast.success("Session reset & cache cleared");
            navigate({ to: "/" });
          }}
        >
          <LogOut className="size-4" /> Reset session & clear cache
        </Button>
      </div>
    </AppShell>
  );
}
