import { useQuery } from "@tanstack/react-query";

export interface UsageData {
  today: {
    date: string;
    requests: number;
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    geminiCount: number;
    openrouterCount: number;
    failoverCount: number;
  };
  totalRequests: number;
  totalTokens: number;
  totalGeminiRequests: number;
  totalOpenRouterRequests: number;
  activeProvider: "openrouter" | "gemini";
  primaryProvider: "openrouter";
  openrouterQuotaStatus?: "healthy" | "cooldown" | "exhausted";
  openrouterCooldownUntil?: number;
  geminiQuotaStatus?: "healthy" | "cooldown" | "exhausted";
  geminiStatus?: "standby" | "active" | "healthy";
  lastUpdated: string;
}

export function useUsage() {
  return useQuery<UsageData>({
    queryKey: ["usage-metrics"],
    queryFn: async () => {
      const res = await fetch("/api/usage");
      if (!res.ok) {
        throw new Error("Failed to fetch usage metrics");
      }
      return res.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
    staleTime: 5000,
  });
}
