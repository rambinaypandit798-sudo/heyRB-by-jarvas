import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { z } from "zod";

import { AppShell } from "@/components/AppShell";
import { InputBar } from "@/components/InputBar";
import { LiveSubtitles, MessageList } from "@/components/MessageList";
import { useProfile, useSettings, useUpdateSettings } from "@/hooks/useAccount";
import { addMessage, streamReply, useMessages } from "@/hooks/useChats";
import { supabase } from "@/integrations/supabase/client";
import { agentName } from "@/lib/agents";
import { cleanText } from "@/lib/format";
import { usableModel } from "@/lib/models";
import { speechEngine } from "@/lib/speech";
import { DEFAULT_VOICE } from "@/lib/voices";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_authenticated/c/$chatId")({
  validateSearch: z.object({ live: z.number().optional() }),
  head: () => ({ meta: [
    { title: "Conversation — RB Agent" },
    { name: "description", content: "Continue your conversation with RB Agent and its specialist workspaces." },
    { property: "og:title", content: "Conversation — RB Agent" },
    { property: "og:description", content: "Continue your conversation with RB Agent and its specialist workspaces." },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary" },
  ] }),
  component: ChatScreen,
});

function ChatScreen() {
  const { chatId } = Route.useParams();
  const { live } = Route.useSearch();
  const queryClient = useQueryClient();
  const { data: messages = [], isLoading } = useMessages(chatId);
  const { data: settings } = useSettings();
  const { data: profile } = useProfile();
  const updateSettings = useUpdateSettings();

  const [streaming, setStreaming] = useState<string | null>(null);
  const [thinking, setThinking] = useState(false);
  const [replyError, setReplyError] = useState<string | null>(null);
  const [liveMode, setLiveMode] = useState(live === 1);
  const [agent, setAgent] = useState("core");
  const [title, setTitle] = useState("RB Agent");
  const handled = useRef<Set<string>>(new Set());

  const model = usableModel(settings?.model);
  const voiceId = settings?.voice_profile ?? DEFAULT_VOICE;

  useEffect(() => {
    supabase
      .from("chats")
      .select("title, agent")
      .eq("id", chatId)
      .maybeSingle()
      .then(({ data }) => {
        if (data) {
          setAgent(data.agent);
          setTitle(data.title);
        }
      });
  }, [chatId]);

  useEffect(() => () => speechEngine.stop(), [chatId]);

  const respond = useCallback(
    async (history: { role: "user" | "assistant"; content: string }[]) => {
      setThinking(true);
      setReplyError(null);
      try {
        const { text, memorySaved } = await streamReply({
          agent,
          model,
          history,
          onDelta: setStreaming,
        });
        const finalText = cleanText(text);
        if (finalText) {
          const saved = await addMessage(chatId, "assistant", finalText);
          if (memorySaved) {
            toast.success("Saved to your memory vault");
            queryClient.invalidateQueries({ queryKey: ["memories"] });
          }
          if (liveMode) speechEngine.speak(saved.id, finalText, voiceId);
        }
      } catch (error) {
        setReplyError(error instanceof Error ? error.message : "RB Agent could not reply.");
      } finally {
        setStreaming(null);
        setThinking(false);
        queryClient.invalidateQueries({ queryKey: ["messages", chatId] });
        queryClient.invalidateQueries({ queryKey: ["chats"] });
      }
    },
    [agent, chatId, liveMode, model, queryClient, voiceId],
  );

  // A trailing user message means the reply has not been generated yet.
  useEffect(() => {
    if (isLoading || thinking || streaming !== null) return;
    const last = messages[messages.length - 1];
    if (!last || last.role !== "user" || handled.current.has(last.id)) return;
    handled.current.add(last.id);
    respond(messages.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })));
  }, [isLoading, messages, respond, streaming, thinking]);

  const send = async (text: string) => {
    try {
      setReplyError(null);
      const saved = await addMessage(chatId, "user", text);
      handled.current.add(saved.id);
      queryClient.invalidateQueries({ queryKey: ["messages", chatId] });
      await respond([
        ...messages.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })),
        { role: "user" as const, content: text },
      ]);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Message could not be sent.");
    }
  };

  return (
    <AppShell title={title}>
      <div className="relative flex h-[calc(100dvh-64px)] w-full flex-col overflow-hidden">
        {/* Agent Sub-Header */}
        <div className="shrink-0 px-4 pt-1">
          <p className="py-2 text-center text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {agentName(agent)} · {profile?.display_name ?? "you"}
          </p>
        </div>

        {/* Scrollable Message List Container */}
        <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4">
          <div className="mx-auto w-full max-w-2xl">
            <MessageList
              messages={messages}
              streaming={streaming}
              thinking={thinking}
              voiceId={voiceId}
            />
            {replyError ? (
              <div role="alert" className="mt-4 flex items-center justify-between gap-3 border border-border bg-muted px-4 py-3 text-sm text-foreground">
                <span>{replyError}</span>
                <Button type="button" variant="outline" size="sm" disabled={thinking} onClick={() => respond(messages.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })))}>
                  Retry
                </Button>
              </div>
            ) : null}
          </div>
        </div>

        {/* Permanently Locked Input Bar at Bottom */}
        <div className="shrink-0 border-t border-border/20 bg-background/90 px-4 pb-3 pt-2 backdrop-blur-xl z-30">
          <div className="mx-auto w-full max-w-2xl">
            <InputBar
              model={model}
              onModelChange={(id) => updateSettings.mutate({ ...settings, model: id })}
              onSend={send}
              busy={thinking || streaming !== null}
              liveMode={liveMode}
              onLiveModeChange={setLiveMode}
              agentLabel={agentName(agent)}
            />
          </div>
        </div>
      </div>
      {settings?.live_subtitles !== false ? <LiveSubtitles /> : null}
    </AppShell>
  );
}
