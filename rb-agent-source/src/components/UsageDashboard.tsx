import React from "react";
import { Activity, ShieldCheck, Zap, RefreshCw, BarChart3, Layers } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { useUsage } from "@/hooks/useUsage";

export function UsageDashboard() {
  const { data: usage, isLoading, refetch } = useUsage();

  if (isLoading || !usage) {
    return (
      <div className="flex items-center justify-center p-6 text-sm text-muted-foreground">
        <RefreshCw className="size-4 animate-spin mr-2" /> Loading usage analytics...
      </div>
    );
  }

  const { today } = usage;
  const isGeminiFailover = usage.activeProvider === "gemini" || usage.openrouterQuotaStatus === "cooldown";
  const openrouterPercentage = today.requests > 0 ? Math.round((today.openrouterCount / today.requests) * 100) : 100;
  const geminiPercentage = today.requests > 0 ? Math.round((today.geminiCount / today.requests) * 100) : 0;

  return (
    <div className="space-y-4">
      {/* Provider & Health Status Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 rounded-2xl border border-border/80 bg-background/50 p-4">
        <div className="flex items-center gap-3">
          <div
            className={`flex size-10 shrink-0 items-center justify-center rounded-xl ${
              isGeminiFailover ? "bg-amber-500/15 text-amber-500" : "bg-blue-500/15 text-blue-500"
            }`}
          >
            {isGeminiFailover ? <Zap className="size-5" /> : <Layers className="size-5" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-foreground">Active Provider:</span>
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                  isGeminiFailover
                    ? "bg-amber-500/15 text-amber-600 dark:text-amber-400"
                    : "bg-blue-500/15 text-blue-600 dark:text-blue-400"
                }`}
              >
                <span
                  className={`size-2 rounded-full ${
                    isGeminiFailover ? "bg-amber-500 animate-pulse" : "bg-blue-500"
                  }`}
                />
                {isGeminiFailover ? "Google Gemini (Active Failover)" : "OpenRouter (Default Primary)"}
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {isGeminiFailover
                ? "OpenRouter cooling down. Requests are currently handled by Google Gemini fallback tier."
                : "OpenRouter free models active as primary AI provider with Google Gemini standby failover."}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          <span
            className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${
              usage.openrouterQuotaStatus === "cooldown"
                ? "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400"
                : "border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400"
            }`}
          >
            {usage.openrouterQuotaStatus === "cooldown" ? "⏱ OpenRouter Cooldown" : "✓ Primary Online"}
          </span>
          <button
            type="button"
            onClick={() => refetch()}
            className="p-1.5 text-muted-foreground hover:text-foreground transition-colors rounded-lg hover:bg-accent"
            title="Refresh Usage Stats"
          >
            <RefreshCw className="size-3.5" />
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="glass rounded-2xl p-3">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] font-medium uppercase tracking-wider">Today's Reqs</span>
            <Activity className="size-3.5 text-primary" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-foreground">
            {today.requests}
          </div>
          <p className="text-[10px] text-muted-foreground mt-0.5">
            {usage.totalRequests} all-time
          </p>
        </div>

        <div className="glass rounded-2xl p-3">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] font-medium uppercase tracking-wider">Tokens Used</span>
            <BarChart3 className="size-3.5 text-primary" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-foreground">
            {today.totalTokens > 1000
              ? `${(today.totalTokens / 1000).toFixed(1)}k`
              : today.totalTokens}
          </div>
          <p className="text-[10px] text-muted-foreground mt-0.5">
            ~{Math.round(today.promptTokens)} in / ~{Math.round(today.completionTokens)} out
          </p>
        </div>

        <div className="glass rounded-2xl p-3">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] font-medium uppercase tracking-wider">OpenRouter</span>
            <Layers className="size-3.5 text-blue-500" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-foreground">
            {today.openrouterCount}
          </div>
          <p className="text-[10px] text-muted-foreground mt-0.5">
            {usage.totalOpenRouterRequests} primary hits
          </p>
        </div>

        <div className="glass rounded-2xl p-3">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[11px] font-medium uppercase tracking-wider">Gemini Failovers</span>
            <ShieldCheck className="size-3.5 text-emerald-500" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-foreground">
            {today.geminiCount}
          </div>
          <p className="text-[10px] text-muted-foreground mt-0.5">
            {today.failoverCount} fallback events
          </p>
        </div>
      </div>

      {/* Provider Distribution Bar */}
      <div className="glass rounded-2xl p-3.5">
        <div className="flex items-center justify-between text-xs font-medium text-muted-foreground mb-2">
          <span>Provider Traffic Distribution</span>
          <span className="text-foreground">
            OpenRouter {openrouterPercentage}% · Gemini {geminiPercentage}%
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted flex">
          <div
            className="bg-blue-500 transition-all duration-500"
            style={{ width: `${openrouterPercentage}%` }}
          />
          <div
            className="bg-emerald-500 transition-all duration-500"
            style={{ width: `${geminiPercentage}%` }}
          />
        </div>
        <div className="flex items-center justify-between text-[11px] text-muted-foreground mt-2">
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-blue-500" /> OpenRouter (Primary Engine)
          </div>
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-emerald-500" /> Google Gemini (Standby Failover)
          </div>
        </div>
      </div>
    </div>
  );
}

export function UsageBadge() {
  const { data: usage } = useUsage();

  if (!usage) return null;

  const isGeminiFailover = usage.activeProvider === "gemini" || usage.openrouterQuotaStatus === "cooldown";

  return (
    <Link
      to="/settings"
      className="flex items-center gap-1.5 rounded-full border border-border/60 bg-background/60 px-2.5 py-1 text-[11px] font-medium text-foreground hover:bg-accent/80 transition-colors shadow-xs"
      title="View AI Usage Analytics & Provider Status"
    >
      <span
        className={`size-1.5 rounded-full ${
          isGeminiFailover ? "bg-amber-500 animate-pulse" : "bg-blue-500"
        }`}
      />
      <span className="hidden sm:inline">
        {isGeminiFailover ? "Gemini (Failover)" : "OpenRouter"}
      </span>
      <span className="tabular-nums text-muted-foreground">
        · {usage.today.requests} reqs
      </span>
    </Link>
  );
}
