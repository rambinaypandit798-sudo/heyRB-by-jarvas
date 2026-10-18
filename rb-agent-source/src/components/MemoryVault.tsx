import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { Check, Pencil, Plus, Search, Trash2, X } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
import { saveMemory } from "@/lib/vault.functions";

type Memory = { id: string; content: string; kind: string; created_at: string };

export function MemoryVault() {
  const queryClient = useQueryClient();
  const save = useServerFn(saveMemory);
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  const { data: memories = [] } = useQuery({
    queryKey: ["memories"],
    queryFn: async (): Promise<Memory[]> => {
      const { data, error } = await supabase
        .from("memories")
        .select("id, content, kind, created_at")
        .order("created_at", { ascending: false });
      if (error) throw new Error(error.message);
      return (data ?? []) as Memory[];
    },
  });

  const persist = useMutation({
    mutationFn: async (input: { id?: string; content: string }) =>
      save({ data: { id: input.id, content: input.content, kind: "fact" } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memories"] });
      setDraft("");
      setEditingId(null);
      toast.success("Memory vault updated");
    },
    onError: (error) => toast.error(error.message),
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("memories").delete().eq("id", id);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memories"] });
      toast.success("Memory deleted");
    },
    onError: (error) => toast.error(error.message),
  });

  const filtered = memories.filter((m) => m.content.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search saved facts"
          className="glass h-11 rounded-xl border-0 pl-9"
        />
      </div>

      <div className="glass rounded-2xl p-3">
        <Textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Add a fact RB Agent should always remember"
          className="min-h-20 resize-none border-0 bg-transparent p-0 text-sm shadow-none focus-visible:ring-0"
        />
        <div className="mt-2 flex justify-end">
          <Button
            size="sm"
            className="rounded-full"
            disabled={draft.trim().length < 2 || persist.isPending}
            onClick={() => persist.mutate({ content: draft.trim() })}
          >
            <Plus className="size-4" /> Save memory
          </Button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="px-1 py-4 text-sm text-muted-foreground">
          Nothing saved yet. Say "याद रखो" in a chat and RB Agent stores it here automatically.
        </p>
      ) : null}

      {filtered.map((memory) => (
        <div key={memory.id} className="glass rounded-2xl p-3">
          {editingId === memory.id ? (
            <div>
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="min-h-20 resize-none border-0 bg-transparent p-0 text-sm shadow-none focus-visible:ring-0"
              />
              <div className="mt-2 flex justify-end gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  className="rounded-full"
                  onClick={() => setEditingId(null)}
                >
                  <X className="size-4" /> Cancel
                </Button>
                <Button
                  size="sm"
                  className="rounded-full"
                  disabled={persist.isPending}
                  onClick={() => persist.mutate({ id: memory.id, content: editText.trim() })}
                >
                  <Check className="size-4" /> Update
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex items-start gap-2">
              <p className="min-w-0 flex-1 text-sm leading-6">• {memory.content}</p>
              <button
                type="button"
                aria-label="Edit memory"
                onClick={() => {
                  setEditingId(memory.id);
                  setEditText(memory.content);
                }}
                className="grid size-8 shrink-0 place-items-center rounded-full text-muted-foreground hover:text-primary"
              >
                <Pencil className="size-4" />
              </button>
              <button
                type="button"
                aria-label="Delete memory"
                onClick={() => remove.mutate(memory.id)}
                className="grid size-8 shrink-0 place-items-center rounded-full text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="size-4" />
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
