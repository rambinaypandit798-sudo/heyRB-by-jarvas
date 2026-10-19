import { useEffect, useState } from "react";
import {
  Sparkles,
  ExternalLink,
  Volume2,
  X,
  Play,
  Settings as SettingsIcon,
  Camera,
  MessageSquare,
  Music,
  CheckCircle2,
} from "lucide-react";
import { overlayWindowEvents, type DeviceActionPayload } from "@/lib/actions";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function OverlayWindow() {
  const [currentAction, setCurrentAction] = useState<DeviceActionPayload | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const unsubscribe = overlayWindowEvents.subscribe((action) => {
      setCurrentAction(action);
      setVisible(true);
    });
    return unsubscribe;
  }, []);

  // Auto-dismiss after 7.5 seconds
  useEffect(() => {
    if (!visible) return;
    const timer = setTimeout(() => {
      setVisible(false);
    }, 7500);
    return () => clearTimeout(timer);
  }, [visible, currentAction]);

  if (!visible || !currentAction) return null;

  const getActionIcon = () => {
    switch (currentAction.type) {
      case "youtube":
        return <Play className="size-5 fill-red-500 text-red-500" />;
      case "spotify":
        return <Music className="size-5 text-emerald-400" />;
      case "whatsapp":
        return <MessageSquare className="size-5 text-green-400" />;
      case "settings":
        return <SettingsIcon className="size-5 text-sky-400" />;
      case "camera":
        return <Camera className="size-5 text-amber-400" />;
      default:
        return <Sparkles className="size-5 text-primary" />;
    }
  };

  const targetLink = currentAction.fallbackUrl || currentAction.url;

  return (
    <div
      role="dialog"
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-24 z-50 flex justify-center px-4 sm:bottom-20"
    >
      <div
        className={cn(
          "pointer-events-auto relative w-full max-w-md overflow-hidden rounded-2xl border border-primary/30 p-4 shadow-2xl transition-all duration-300",
          "bg-background/90 backdrop-blur-2xl dark:bg-card/90",
          "ring-1 ring-white/10 dark:ring-primary/20",
          visible ? "animate-rise scale-100 opacity-100" : "scale-95 opacity-0 pointer-events-none"
        )}
      >
        {/* Gemini-Style Iridescent Ambient Glow Gradient */}
        <div className="pointer-events-none absolute -inset-0.5 -z-10 rounded-2xl bg-gradient-to-r from-cyan-500/20 via-primary/25 to-purple-500/20 blur-md opacity-80 animate-pulse" />

        <div className="flex items-start gap-3">
          {/* Action Icon / Planetary Badge */}
          <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent text-accent-foreground shadow-sm">
            {getActionIcon()}
          </div>

          {/* Action Info */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <span className="flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-primary">
                <Sparkles className="size-3 animate-spin" style={{ animationDuration: "4s" }} />
                Gemini Action Hub
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-medium text-emerald-500">
                <CheckCircle2 className="size-2.5" /> Executed
              </span>
            </div>

            <h4 className="mt-0.5 truncate text-[15px] font-semibold text-foreground">
              {currentAction.appName}
            </h4>

            <p className="mt-0.5 text-xs text-muted-foreground line-clamp-1">
              {currentAction.actionText || "Action triggered on device"}
            </p>

            {/* Voice Feedback Caption */}
            <div className="mt-2.5 flex items-center gap-2 rounded-lg bg-accent/60 px-2.5 py-1.5 text-xs font-medium text-accent-foreground">
              <Volume2 className="size-3.5 shrink-0 text-primary animate-pulse" />
              <span className="truncate">"हाँ, यह कर दिया है"</span>
              <span className="ml-auto text-[10px] text-muted-foreground">Spoken Feedback</span>
            </div>

            {/* Controls */}
            {targetLink ? (
              <div className="mt-2.5 flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-xs rounded-lg gap-1 border-primary/20 hover:bg-primary hover:text-primary-foreground"
                  onClick={() => {
                    if (targetLink) window.open(targetLink, "_blank", "noopener,noreferrer");
                  }}
                >
                  <ExternalLink className="size-3" />
                  View in Browser
                </Button>
              </div>
            ) : null}
          </div>

          {/* Close Button */}
          <button
            type="button"
            onClick={() => setVisible(false)}
            aria-label="Dismiss overlay"
            className="grid size-7 shrink-0 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
