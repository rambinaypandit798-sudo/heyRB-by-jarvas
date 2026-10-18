import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";

import { supabase } from "@/integrations/supabase/client";
import { DEFAULT_MODEL } from "@/lib/models";
import { DEFAULT_VOICE } from "@/lib/voices";

export type Settings = {
  user_id: string;
  model: string;
  voice_profile: string;
  wake_word_enabled: boolean;
  live_subtitles: boolean;
  telegram_bot_token: string | null;
  telegram_enabled: boolean;
  whatsapp_api_key: string | null;
  whatsapp_enabled: boolean;
  github_token: string | null;
  github_repo: string | null;
  automation_enabled: boolean;
};

const DEFAULT_USER = {
  id: "00000000-0000-0000-0000-000000000000",
  email: "user@local",
  user_metadata: { display_name: "Ram" },
  app_metadata: {},
  aud: "authenticated",
  created_at: new Date().toISOString(),
};

export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setReady(true);
    }).catch(() => {
      setReady(true);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => sub.subscription.unsubscribe();
  }, []);

  const effectiveUser = session?.user ?? (DEFAULT_USER as unknown as Session["user"]);
  return { session, ready, user: effectiveUser };
}

export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      try {
        const { data: auth } = await supabase.auth.getUser();
        if (auth.user) {
          const { data } = await supabase
            .from("profiles")
            .select("id, display_name")
            .eq("id", auth.user.id)
            .maybeSingle();
          const accountName = auth.user.user_metadata?.["display_name"] || auth.user.user_metadata?.["full_name"] || auth.user.user_metadata?.["name"];
          if (data && data.display_name && data.display_name !== "Friend") return data;
          const fallback = {
            id: auth.user.id,
            display_name: typeof accountName === "string" && accountName.trim() ? accountName.trim() : auth.user.email?.split("@")[0] ?? "Ram",
          };
          await supabase.from("profiles").upsert(fallback);
          return fallback;
        }
      } catch {}

      const localName = typeof window !== "undefined" ? localStorage.getItem("rb_profile_name") || "Ram" : "Ram";
      return {
        id: DEFAULT_USER.id,
        display_name: localName,
      };
    },
  });
}

const FALLBACK_SETTINGS: Omit<Settings, "user_id"> = {
  model: DEFAULT_MODEL,
  voice_profile: DEFAULT_VOICE,
  wake_word_enabled: false,
  live_subtitles: true,
  telegram_bot_token: null,
  telegram_enabled: false,
  whatsapp_api_key: null,
  whatsapp_enabled: false,
  github_token: null,
  github_repo: null,
  automation_enabled: false,
};

export function useSettings() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: async (): Promise<Settings | null> => {
      try {
        const { data: auth } = await supabase.auth.getUser();
        if (auth.user) {
          const { data } = await supabase
            .from("user_settings")
            .select("*")
            .eq("user_id", auth.user.id)
            .maybeSingle();
          if (data) return data as Settings;
          const row = { user_id: auth.user.id, ...FALLBACK_SETTINGS };
          await supabase.from("user_settings").upsert(row);
          return row;
        }
      } catch {}

      if (typeof window !== "undefined") {
        const local = localStorage.getItem("rb_user_settings");
        if (local) {
          try {
            return JSON.parse(local) as Settings;
          } catch {}
        }
      }
      return { user_id: DEFAULT_USER.id, ...FALLBACK_SETTINGS };
    },
  });
}

export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (patch: Partial<Settings>) => {
      try {
        const { data: auth } = await supabase.auth.getUser();
        if (auth.user) {
          const { error } = await supabase
            .from("user_settings")
            .upsert({ user_id: auth.user.id, ...FALLBACK_SETTINGS, ...patch }, { onConflict: "user_id" });
          if (error) throw new Error(error.message);
          return;
        }
      } catch {}

      const current = (qc.getQueryData(["settings"]) as Settings) || { user_id: DEFAULT_USER.id, ...FALLBACK_SETTINGS };
      const updated = { ...current, ...patch };
      if (typeof window !== "undefined") {
        localStorage.setItem("rb_user_settings", JSON.stringify(updated));
      }
      qc.setQueryData(["settings"], updated);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings"] }),
  });
}
