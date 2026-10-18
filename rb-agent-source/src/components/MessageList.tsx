import { useEffect, useRef, useState } from "react";
import { Check, Copy, Pause, Play } from "lucide-react";
import { toast } from "sonner";

import { BrandMark } from "@/components/BrandMark";
import { cleanText } from "@/lib/format";
import { speechEngine, type SpeechState } from "@/lib/speech";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/hooks/useChats";

function useSpeechState() {
  const [state, setState] = useState<SpeechState>({
    activeId: null,
    speaking: false,
    paused: false,
    spoken: "",
  });
  useEffect(() => {
    const unsubscribe = speechEngine.subscribe(setState);
    return () => {
      unsubscribe();
    };
  }, []);
  return state;
}

function Actions({ id, text, voiceId }: { id: string; text: string; voiceId: string }) {
  const speech = useSpeechState();
  const [copied, setCopied] = useState(false);
  const isActive = speech.activeId === id;
  const isPlaying = isActive && speech.speaking && !speech.paused;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      toast.error("Clipboard is blocked in this browser.");
    }
  };

  return (
    <div className="mt-1.5 flex items-center gap-1">
      <button
        type="button"
        onClick={copy}
        aria-label="Copy this reply"
        className="grid size-8 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
      >
        {copied ? <Check className="size-4 text-primary" /> : <Copy className="size-4" />}
      </button>
      <button
        type="button"
        onClick={() => speechEngine.toggle(id, text, voiceId)}
        aria-label={isPlaying ? "Pause reading" : "Read this reply aloud"}
        className={cn(
          "grid size-8 place-items-center rounded-full transition-colors hover:bg-accent hover:text-accent-foreground",
          isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground",
        )}
      >
        {isPlaying ? <Pause className="size-4" /> : <Play className="size-4" />}
      </button>
      {isActive && speech.paused ? (
        <span className="text-[11px] font-medium text-muted-foreground">bookmarked</span>
      ) : null}
    </div>
  );
}

export function MessageList({
  messages,
  streaming,
  voiceId,
  thinking,
}: {
  messages: ChatMessage[];
  streaming: string | null;
  voiceId: string;
  thinking: boolean;
}) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, streaming, thinking]);

  return (
    <div className="space-y-4">
      {messages.map((message) => {
        const text = cleanText(message.content);
        if (message.role === "user") {
          return (
            <div key={message.id} className="flex justify-end">
              <div className="animate-rise max-w-[85%] rounded-3xl rounded-br-lg bg-primary px-4 py-2.5 text-[15px] leading-6 whitespace-pre-wrap text-primary-foreground">
                {text}
              </div>
            </div>
          );
        }
        return (
          <div key={message.id} className="animate-rise flex gap-2.5">
            <BrandMark size={28} className="mt-1" />
            <div className="min-w-0 flex-1">
              <div className="text-[15px] leading-7 whitespace-pre-wrap text-foreground">{text}</div>
              <Actions id={message.id} text={text} voiceId={voiceId} />
            </div>
          </div>
        );
      })}

      {streaming !== null ? (
        <div className="flex gap-2.5">
          <BrandMark size={28} className="mt-1" />
          <div className="min-w-0 flex-1 text-[15px] leading-7 whitespace-pre-wrap text-foreground">
            {cleanText(streaming)}
            <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse rounded-sm bg-primary align-middle" />
          </div>
        </div>
      ) : null}

      {thinking && streaming === null ? (
        <div className="flex items-center gap-2.5">
          <BrandMark size={28} />
          <div className="glass flex items-center gap-1.5 rounded-full px-3 py-2">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="size-1.5 animate-bounce rounded-full bg-primary"
                style={{ animationDelay: `${i * 120}ms` }}
              />
            ))}
          </div>
        </div>
      ) : null}

      <div ref={endRef} />
    </div>
  );
}

export function LiveSubtitles() {
  const speech = useSpeechState();
  if (!speech.activeId || !speech.spoken.trim()) return null;
  const tail = speech.spoken.slice(-140);
  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-36 z-40 flex justify-center px-6">
      <p className="glass-strong max-w-xl rounded-2xl px-4 py-2 text-center text-sm leading-6 text-foreground">
        {tail}
      </p>
    </div>
  );
}
