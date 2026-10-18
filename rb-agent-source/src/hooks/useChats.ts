import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { supabase } from "@/integrations/supabase/client";
import { chatTitleFrom } from "@/lib/format";

export type Chat = {
  id: string;
  title: string;
  agent: string;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  id: string;
  chat_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
};

export function useChats() {
  return useQuery({
    queryKey: ["chats"],
    queryFn: async (): Promise<Chat[]> => {
      try {
        const { data: auth } = await supabase.auth.getUser();
        if (auth?.user) {
          const { data, error } = await supabase
            .from("chats")
            .select("id, title, agent, created_at, updated_at")
            .order("updated_at", { ascending: false });
          if (!error && data) return data as Chat[];
        }
      } catch {}

      if (typeof window !== "undefined") {
        const local = localStorage.getItem("rb_local_chats");
        if (local) {
          try {
            return JSON.parse(local) as Chat[];
          } catch {}
        }
      }
      return [];
    },
  });
}

export function useMessages(chatId: string | undefined) {
  return useQuery({
    queryKey: ["messages", chatId],
    enabled: Boolean(chatId),
    queryFn: async (): Promise<ChatMessage[]> => {
      try {
        const { data: auth } = await supabase.auth.getUser();
        if (auth?.user) {
          const { data, error } = await supabase
            .from("messages")
            .select("id, chat_id, role, content, created_at")
            .eq("chat_id", chatId!)
            .order("created_at", { ascending: true });
          if (!error && data) return data as ChatMessage[];
        }
      } catch {}

      if (typeof window !== "undefined" && chatId) {
        const local = localStorage.getItem(`rb_local_msgs_${chatId}`);
        if (local) {
          try {
            return JSON.parse(local) as ChatMessage[];
          } catch {}
        }
      }
      return [];
    },
  });
}

export async function createChatWithMessage(text: string, agent: string) {
  try {
    const { data: auth } = await supabase.auth.getUser();
    if (auth?.user) {
      const { data: chat, error } = await supabase
        .from("chats")
        .insert({ user_id: auth.user.id, title: chatTitleFrom(text), agent })
        .select("id")
        .single();
      if (!error && chat) {
        const { error: msgError } = await supabase
          .from("messages")
          .insert({ chat_id: chat.id, user_id: auth.user.id, role: "user", content: text });
        if (!msgError) return chat.id as string;
      }
    }
  } catch {}

  const chatId = crypto.randomUUID();
  const now = new Date().toISOString();
  const newChat: Chat = {
    id: chatId,
    title: chatTitleFrom(text),
    agent,
    created_at: now,
    updated_at: now,
  };
  const firstMsg: ChatMessage = {
    id: crypto.randomUUID(),
    chat_id: chatId,
    role: "user",
    content: text,
    created_at: now,
  };

  if (typeof window !== "undefined") {
    const existingChats: Chat[] = JSON.parse(localStorage.getItem("rb_local_chats") || "[]");
    localStorage.setItem("rb_local_chats", JSON.stringify([newChat, ...existingChats]));
    localStorage.setItem(`rb_local_msgs_${chatId}`, JSON.stringify([firstMsg]));
  }
  return chatId;
}

export async function addMessage(chatId: string, role: "user" | "assistant", content: string) {
  try {
    const { data: auth } = await supabase.auth.getUser();
    if (auth?.user) {
      const { data, error } = await supabase
        .from("messages")
        .insert({ chat_id: chatId, user_id: auth.user.id, role, content })
        .select("id, chat_id, role, content, created_at")
        .single();
      if (!error && data) {
        await supabase.from("chats").update({ updated_at: new Date().toISOString() }).eq("id", chatId);
        return data as ChatMessage;
      }
    }
  } catch {}

  const now = new Date().toISOString();
  const msg: ChatMessage = {
    id: crypto.randomUUID(),
    chat_id: chatId,
    role,
    content,
    created_at: now,
  };

  if (typeof window !== "undefined") {
    const existingMsgs: ChatMessage[] = JSON.parse(localStorage.getItem(`rb_local_msgs_${chatId}`) || "[]");
    localStorage.setItem(`rb_local_msgs_${chatId}`, JSON.stringify([...existingMsgs, msg]));

    const existingChats: Chat[] = JSON.parse(localStorage.getItem("rb_local_chats") || "[]");
    const updatedChats = existingChats.map((c) => (c.id === chatId ? { ...c, updated_at: now } : c));
    localStorage.setItem("rb_local_chats", JSON.stringify(updatedChats));
  }
  return msg;
}

export function useDeleteChat() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (chatId: string) => {
      try {
        const { data: auth } = await supabase.auth.getUser();
        if (auth?.user) {
          await supabase.from("chats").delete().eq("id", chatId);
        }
      } catch {}

      if (typeof window !== "undefined") {
        const existingChats: Chat[] = JSON.parse(localStorage.getItem("rb_local_chats") || "[]");
        localStorage.setItem("rb_local_chats", JSON.stringify(existingChats.filter((c) => c.id !== chatId)));
        localStorage.removeItem(`rb_local_msgs_${chatId}`);
      }
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chats"] }),
  });
}

/** Streams an assistant reply from the RB Agent backend. */
export async function streamReply(opts: {
  agent: string;
  model: string;
  history: { role: "user" | "assistant"; content: string }[];
  onDelta: (full: string) => void;
}) {
  let token = "bypass-local-token";
  try {
    const { data } = await supabase.auth.getSession();
    if (data.session?.access_token) {
      token = data.session.access_token;
    }
  } catch {}

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ agent: opts.agent, model: opts.model, messages: opts.history }),
  });

  if (!res.ok || !res.body) {
    let message = "RB Agent could not answer right now.";
    try {
      const payload = (await res.json()) as { error?: string };
      if (payload.error) message = payload.error;
    } catch {
      // keep default
    }
    throw new Error(message);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let full = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    full += decoder.decode(value, { stream: true });
    opts.onDelta(full);
  }
  return { text: full, memorySaved: res.headers.get("X-Memory-Saved") === "1" };
}
