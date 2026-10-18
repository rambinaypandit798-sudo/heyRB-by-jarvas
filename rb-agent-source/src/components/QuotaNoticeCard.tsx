import React, { useState, useEffect } from "react";
import { Clock, RefreshCw, AlertCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface QuotaErrorInfo {
  message: string;
  isQuota: boolean;
  retryAfter: number;
}

interface QuotaNoticeCardProps {
  error: QuotaErrorInfo | null;
  onRetry: () => void;
  disabled?: boolean;
}

export function QuotaNoticeCard({ error, onRetry, disabled = false }: QuotaNoticeCardProps) {
  if (!error) return null;

  const [countdown, setCountdown] = useState<number>(error.retryAfter || 15);

  useEffect(() => {
    if (!error.isQuota) return;
    setCountdown(error.retryAfter || 15);

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [error.isQuota, error.retryAfter]);

  if (!error.isQuota) {
    return (
      <div
        role="alert"
        className="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 rounded-2xl border border-destructive/30 bg-destructive/5 p-4 text-foreground transition-all duration-300 animate-rise"
      >
        <div className="flex items-center gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-destructive/10 text-destructive">
            <AlertCircle className="size-4" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-foreground">Service Connection Notice</h4>
            <p className="text-xs text-muted-foreground mt-0.5">{error.message}</p>
          </div>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={disabled}
          onClick={onRetry}
          className="shrink-0 rounded-xl text-xs gap-1.5 self-end sm:self-auto"
        >
          <RefreshCw className={`size-3.5 ${disabled ? "animate-spin" : ""}`} />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className="mt-4 overflow-hidden rounded-2xl border border-amber-500/30 bg-amber-500/[0.04] dark:bg-amber-500/[0.07] p-4 sm:p-5 backdrop-blur-xl shadow-sm transition-all duration-300 animate-rise"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="relative flex size-9 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400">
            <Sparkles className="size-4 animate-pulse" />
            <span className="absolute -top-0.5 -right-0.5 flex size-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-amber-500" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-[14px] font-semibold tracking-tight text-foreground">
                AI Capacity Cooldown
              </h4>
              <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-medium text-amber-600 dark:text-amber-400">
                Rate-Limit Protected
              </span>
            </div>
            <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">
              Google Gemini API capacity is momentarily resting. Your conversation and memory vault are safely preserved.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2.5 border-t border-amber-500/20 pt-3">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="size-3.5 text-amber-500/80" />
          <span>
            {countdown > 0 ? (
              <>
                Ready for full speed in{" "}
                <span className="font-semibold tabular-nums text-foreground">{countdown}s</span>
              </>
            ) : (
              <span className="font-medium text-emerald-600 dark:text-emerald-400">
                ✓ Ready to retry now
              </span>
            )}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="default"
            size="sm"
            disabled={disabled}
            onClick={onRetry}
            className="rounded-xl text-xs font-medium gap-1.5 shadow-sm"
          >
            <RefreshCw className={`size-3.5 ${disabled ? "animate-spin" : ""}`} />
            {disabled ? "Retrying..." : "Retry Now"}
          </Button>
        </div>
      </div>
    </div>
  );
}
