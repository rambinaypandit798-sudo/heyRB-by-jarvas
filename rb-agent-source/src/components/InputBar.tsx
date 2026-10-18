import { useEffect, useRef, useState } from "react";
import { Camera, FileText, Image as ImageIcon, Mic, Plus, Radio, SendHorizonal, X } from "lucide-react";
import { toast } from "sonner";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ModelSheet } from "@/components/ModelSheet";
import { modelLabel } from "@/lib/models";
import { createRecognition, readTranscript } from "@/lib/speech";
import { cn } from "@/lib/utils";

export function InputBar({
  model,
  onModelChange,
  onSend,
  busy,
  liveMode,
  onLiveModeChange,
  agentLabel,
}: {
  model: string;
  onModelChange: (id: string) => void;
  onSend: (text: string) => void;
  busy: boolean;
  liveMode: boolean;
  onLiveModeChange: (on: boolean) => void;
  agentLabel: string;
}) {
  const [text, setText] = useState("");
  const [sheetOpen, setSheetOpen] = useState(false);
  const [listening, setListening] = useState(false);
  const [attachments, setAttachments] = useState<string[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLInputElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<ReturnType<typeof createRecognition>>(null);

  useEffect(() => {
    textRef.current?.focus();
  }, []);

  useEffect(() => {
    return () => recognitionRef.current?.abort();
  }, []);

  const submit = (value: string) => {
    const payload = attachments.length
      ? `${value}\n\nAttached files: ${attachments.join(", ")}`
      : value;
    if (!payload.trim() || busy) return;
    onSend(payload.trim());
    setText("");
    setAttachments([]);
    textRef.current?.focus();
  };

  const toggleMic = () => {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = createRecognition("hi-IN");
    if (!rec) {
      toast.error("Voice input is not supported in this browser.");
      return;
    }
    recognitionRef.current = rec;
    rec.onresult = (event) => {
      const { text: heard, final } = readTranscript(event);
      setText(heard);
      if (final) {
        rec.stop();
        setListening(false);
        submit(heard);
      }
    };
    rec.onerror = () => {
      setListening(false);
      toast.error("Microphone is unavailable. Check browser permission.");
    };
    rec.onend = () => setListening(false);
    rec.start();
    setListening(true);
  };

  const pick = (list: FileList | null) => {
    if (!list?.length) return;
    setAttachments((prev) => [...prev, ...Array.from(list).map((f) => f.name)].slice(0, 5));
  };

  return (
    <div className="glass-strong rounded-3xl p-2.5">
      {attachments.length ? (
        <div className="mb-2 flex flex-wrap gap-1.5 px-1">
          {attachments.map((name) => (
            <span
              key={name}
              className="flex items-center gap-1 rounded-full bg-accent px-2.5 py-1 text-[11px] font-medium text-accent-foreground"
            >
              {name}
              <button type="button" onClick={() => setAttachments((p) => p.filter((n) => n !== name))}>
                <X className="size-3" />
              </button>
            </span>
          ))}
        </div>
      ) : null}

      <div className="flex items-end gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              aria-label="Add an attachment"
              className="grid size-10 shrink-0 place-items-center rounded-full bg-accent text-accent-foreground transition-transform active:scale-95"
            >
              <Plus className="size-5" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="glass-strong rounded-2xl border-0">
            <DropdownMenuItem onClick={() => cameraRef.current?.click()}>
              <Camera className="size-4" /> Camera
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => imageRef.current?.click()}>
              <ImageIcon className="size-4" /> Photos
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => fileRef.current?.click()}>
              <FileText className="size-4" /> Document
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <div className="min-w-0 flex-1">
          <textarea
            ref={textRef}
            value={text}
            rows={1}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit(text);
              }
            }}
            placeholder={listening ? "Listening…" : `ASK ${agentLabel}`}
            className="max-h-32 w-full resize-none bg-transparent px-1 py-2.5 text-[15px] leading-6 outline-none placeholder:text-muted-foreground"
          />
          <div className="flex items-center gap-1.5 px-1 pb-0.5">
            <button
              type="button"
              onClick={() => setSheetOpen(true)}
              className="rounded-full bg-accent px-3 py-1 text-[11px] font-semibold text-accent-foreground"
            >
              {modelLabel(model)}
            </button>
            <button
              type="button"
              onClick={() => onLiveModeChange(!liveMode)}
              className={cn(
                "flex items-center gap-1 rounded-full px-3 py-1 text-[11px] font-semibold transition-colors",
                liveMode
                  ? "bg-primary text-primary-foreground"
                  : "bg-accent text-accent-foreground",
              )}
            >
              <Radio className="size-3" /> Live chat
            </button>
          </div>
        </div>

        <button
          type="button"
          onClick={toggleMic}
          aria-label="Speak your command"
          className={cn(
            "grid size-10 shrink-0 place-items-center rounded-full transition-transform active:scale-95",
            listening ? "bg-primary text-primary-foreground animate-core-pulse" : "bg-accent text-accent-foreground",
          )}
        >
          <Mic className="size-5" />
        </button>
        <button
          type="button"
          onClick={() => submit(text)}
          disabled={busy || !text.trim()}
          aria-label="Send message"
          className="grid size-10 shrink-0 place-items-center rounded-full bg-primary text-primary-foreground transition-transform active:scale-95 disabled:opacity-40"
        >
          <SendHorizonal className="size-5" />
        </button>
      </div>

      <input ref={cameraRef} type="file" accept="image/*" capture="environment" hidden onChange={(e) => pick(e.target.files)} />
      <input ref={imageRef} type="file" accept="image/*" multiple hidden onChange={(e) => pick(e.target.files)} />
      <input ref={fileRef} type="file" accept=".pdf,.txt,.md,.csv,.json,image/*" multiple hidden onChange={(e) => pick(e.target.files)} />

      <ModelSheet open={sheetOpen} onOpenChange={setSheetOpen} value={model} onChange={onModelChange} />
    </div>
  );
}
