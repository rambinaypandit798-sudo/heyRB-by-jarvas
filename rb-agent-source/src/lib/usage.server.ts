import fs from "fs";
import path from "path";

export interface DailyUsage {
  date: string;
  requests: number;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  geminiCount: number;
  openrouterCount: number;
  failoverCount: number;
}

export interface UsageStore {
  today: DailyUsage;
  totalRequests: number;
  totalTokens: number;
  totalGeminiRequests: number;
  totalOpenRouterRequests: number;
  activeProvider: "openrouter" | "gemini";
  primaryProvider: "openrouter";
  openrouterQuotaStatus: "healthy" | "cooldown" | "exhausted";
  openrouterCooldownUntil: number;
  geminiStatus: "standby" | "active" | "healthy";
  lastUpdated: string;
}

const STATS_FILE = path.resolve(process.cwd(), ".usage-stats.json");

function todayDateString(): string {
  return new Date().toISOString().slice(0, 10);
}

function initDailyUsage(): DailyUsage {
  return {
    date: todayDateString(),
    requests: 0,
    promptTokens: 0,
    completionTokens: 0,
    totalTokens: 0,
    geminiCount: 0,
    openrouterCount: 0,
    failoverCount: 0,
  };
}

let inMemoryStore: UsageStore = {
  today: initDailyUsage(),
  totalRequests: 0,
  totalTokens: 0,
  totalGeminiRequests: 0,
  totalOpenRouterRequests: 0,
  activeProvider: "openrouter",
  primaryProvider: "openrouter",
  openrouterQuotaStatus: "healthy",
  openrouterCooldownUntil: 0,
  geminiStatus: "standby",
  lastUpdated: new Date().toISOString(),
};

// Load initial store from disk if present
try {
  if (fs.existsSync(STATS_FILE)) {
    const raw = fs.readFileSync(STATS_FILE, "utf-8");
    const parsed = JSON.parse(raw) as Partial<UsageStore>;
    if (parsed.today && parsed.today.date === todayDateString()) {
      inMemoryStore = {
        ...inMemoryStore,
        ...parsed,
        today: parsed.today,
        activeProvider: parsed.activeProvider || "openrouter",
        primaryProvider: "openrouter",
      };
    } else if (parsed.today) {
      inMemoryStore = {
        ...inMemoryStore,
        totalRequests: parsed.totalRequests || 0,
        totalTokens: parsed.totalTokens || 0,
        totalGeminiRequests: parsed.totalGeminiRequests || 0,
        totalOpenRouterRequests: parsed.totalOpenRouterRequests || 0,
        today: initDailyUsage(),
        activeProvider: "openrouter",
        primaryProvider: "openrouter",
      };
    }
  }
} catch {
  // Use in-memory default
}

function persistStore() {
  try {
    fs.writeFileSync(STATS_FILE, JSON.stringify(inMemoryStore, null, 2), "utf-8");
  } catch {
    // Non-fatal if storage write fails
  }
}

export function recordUsageEvent(event: {
  provider: "openrouter" | "gemini";
  model: string;
  promptTokens?: number;
  completionTokens?: number;
  failover?: boolean;
}) {
  const today = todayDateString();
  if (inMemoryStore.today.date !== today) {
    inMemoryStore.today = initDailyUsage();
  }

  const pTokens = Math.max(0, event.promptTokens || 15);
  const cTokens = Math.max(0, event.completionTokens || 35);
  const total = pTokens + cTokens;

  inMemoryStore.today.requests += 1;
  inMemoryStore.today.promptTokens += pTokens;
  inMemoryStore.today.completionTokens += cTokens;
  inMemoryStore.today.totalTokens += total;

  inMemoryStore.totalRequests += 1;
  inMemoryStore.totalTokens += total;

  if (event.provider === "openrouter") {
    inMemoryStore.today.openrouterCount += 1;
    inMemoryStore.totalOpenRouterRequests += 1;
    inMemoryStore.activeProvider = "openrouter";
    inMemoryStore.geminiStatus = "standby";
  } else {
    inMemoryStore.today.geminiCount += 1;
    inMemoryStore.totalGeminiRequests += 1;
  }

  if (event.failover) {
    inMemoryStore.today.failoverCount += 1;
    inMemoryStore.activeProvider = "gemini";
    inMemoryStore.openrouterQuotaStatus = "cooldown";
    inMemoryStore.geminiStatus = "active";
  }

  inMemoryStore.lastUpdated = new Date().toISOString();
  persistStore();
}

export function markOpenRouterCooldown(seconds = 30) {
  inMemoryStore.openrouterQuotaStatus = "cooldown";
  inMemoryStore.openrouterCooldownUntil = Date.now() + seconds * 1000;
  inMemoryStore.activeProvider = "gemini";
  inMemoryStore.geminiStatus = "active";
  inMemoryStore.lastUpdated = new Date().toISOString();
  persistStore();
}

export function markGeminiCooldown(seconds = 30) {
  inMemoryStore.geminiStatus = "standby";
  inMemoryStore.activeProvider = "openrouter";
  inMemoryStore.lastUpdated = new Date().toISOString();
  persistStore();
}

export function getUsageMetrics(): UsageStore {
  const today = todayDateString();
  if (inMemoryStore.today.date !== today) {
    inMemoryStore.today = initDailyUsage();
  }

  // Check if OpenRouter cooldown has elapsed, restore as primary
  if (inMemoryStore.openrouterCooldownUntil > 0 && Date.now() > inMemoryStore.openrouterCooldownUntil) {
    inMemoryStore.openrouterQuotaStatus = "healthy";
    inMemoryStore.openrouterCooldownUntil = 0;
    inMemoryStore.activeProvider = "openrouter";
    inMemoryStore.geminiStatus = "standby";
  }

  return inMemoryStore;
}
