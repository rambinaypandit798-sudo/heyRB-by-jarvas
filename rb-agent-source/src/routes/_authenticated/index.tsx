import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";

import { AgentCore } from "@/components/AgentCore";
import { AgentHub } from "@/components/AgentHub";
import { AppShell } from "@/components/AppShell";
import { BrandMark } from "@/components/BrandMark";
import { InputBar } from "@/components/InputBar";
import { useProfile, useSettings, useUpdateSettings } from "@/hooks/useAccount";
import { createChatWithMessage } from "@/hooks/useChats";
import { agentName, type AgentId } from "@/lib/agents";
import { usableModel } from "@/lib/models";

export const Route = createFileRoute("/_authenticated/")({
  head: () => ({
    meta: [
      { title: "RB Agent — Your AI Agent Hub" },
      {
        name: "description",
        content:
          "Talk to RB Agent and its five specialist sub agents for coding, phone automation, research, memory and social workflows.",
      },
      { property: "og:title", content: "RB Agent — Your AI Agent Hub" },
      {
        property: "og:description",
        content: "Voice powered assistant with five specialist sub agents and a permanent memory vault.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: HomeScreen,
});

function HomeScreen() {
  const navigate = useNavigate();
  const { data: profile } = useProfile();
  const { data: settings } = useSettings();
  const updateSettings = useUpdateSettings();
  const [hubOpen, setHubOpen] = useState(false);
  const [agent, setAgent] = useState<AgentId>("core");
  const [liveMode, setLiveMode] = useState(false);
  const [busy, setBusy] = useState(false);

  const model = usableModel(settings?.model);
  const name = profile?.display_name?.trim() || "friend";

  const send = async (text: string) => {
    setBusy(true);
    try {
      const chatId = await createChatWithMessage(text, agent);
      navigate({ to: "/c/$chatId", params: { chatId }, search: { live: liveMode ? 1 : 0 } });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Could not start the chat.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppShell>
      <div className="mx-auto flex h-[calc(100dvh-64px)] w-full max-w-3xl flex-col px-4 pb-3 sm:px-7">
        <div className="shrink-0 flex flex-col items-center pt-8 text-center sm:pt-14">
          <BrandMark size={50} />
          <h1 className="font-display mt-4 text-[22px] leading-snug font-semibold sm:text-3xl">
            नमस्ते, {name} आज आपका क्या प्लान है
          </h1>
        </div>

        <div className="flex min-h-40 flex-1 items-center justify-center py-4">
          <AgentCore
            onClick={() => setHubOpen(true)}
            label="RB Agent"
          />
        </div>

        <div className="shrink-0 mt-auto pb-1">
          <InputBar
            model={model}
            onModelChange={(id) => updateSettings.mutate({ ...settings, model: id })}
            onSend={send}
            busy={busy}
            liveMode={liveMode}
            onLiveModeChange={setLiveMode}
            agentLabel={agentName(agent)}
          />
        </div>
      </div>

      <AgentHub
        open={hubOpen}
        onOpenChange={(next) => {
          setHubOpen(next);
          if (!next) setAgent("core");
        }}
        active={agent}
        model={model}
        onModelChange={(id) => updateSettings.mutate({ ...settings, model: id })}
        onSend={send}
        busy={busy}
        liveMode={liveMode}
        onLiveModeChange={setLiveMode}
        onSelect={(id) => {
          setAgent(id);
        }}
      />
    </AppShell>
  );
}
