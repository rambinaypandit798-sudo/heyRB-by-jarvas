import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";

/** Saving or editing a memory re-indexes it so vector recall stays accurate. */
export const saveMemory = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data) =>
    z.object({ id: z.string().uuid().optional(), content: z.string().min(2).max(2000), kind: z.string().default("fact") }).parse(data),
  )
  .handler(async ({ data, context }) => {
    const { embed } = await import("./ai.server");
    const vector = await embed(data.content);
    const row = {
      user_id: context.userId,
      content: data.content,
      kind: data.kind,
      embedding: vector as unknown as string,
    };
    if (data.id) {
      const { error } = await context.supabase.from("memories").update(row).eq("id", data.id);
      if (error) throw new Error(error.message);
      return { id: data.id };
    }
    const { data: inserted, error } = await context.supabase
      .from("memories")
      .insert(row)
      .select("id")
      .single();
    if (error) throw new Error(error.message);
    return { id: inserted.id };
  });

/** Reads a GitHub repository through the user's stored token, server side only. */
export const githubTree = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data) => z.object({ repo: z.string().min(3) }).parse(data))
  .handler(async ({ data, context }) => {
    const { data: settings } = await context.supabase
      .from("user_settings")
      .select("github_token")
      .eq("user_id", context.userId)
      .maybeSingle();
    const token = settings?.github_token;
    const headers: Record<string, string> = {
      Accept: "application/vnd.github+json",
      "User-Agent": "RB-Agent",
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const repoRes = await fetch(`https://api.github.com/repos/${data.repo}`, { headers });
    if (!repoRes.ok) {
      return { ok: false as const, error: repoRes.status === 404 ? "Repository not found, or your token cannot see it." : `GitHub returned ${repoRes.status}.` };
    }
    const repo = (await repoRes.json()) as { default_branch: string };
    const treeRes = await fetch(
      `https://api.github.com/repos/${data.repo}/git/trees/${repo.default_branch}?recursive=1`,
      { headers },
    );
    if (!treeRes.ok) return { ok: false as const, error: `GitHub returned ${treeRes.status}.` };
    const tree = (await treeRes.json()) as { tree?: { path: string; type: string; size?: number }[] };
    return {
      ok: true as const,
      branch: repo.default_branch,
      files: (tree.tree ?? []).filter((f) => f.type === "blob").slice(0, 400),
    };
  });

export const githubFile = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data) => z.object({ repo: z.string(), path: z.string(), branch: z.string() }).parse(data))
  .handler(async ({ data, context }) => {
    const { data: settings } = await context.supabase
      .from("user_settings")
      .select("github_token")
      .eq("user_id", context.userId)
      .maybeSingle();
    const headers: Record<string, string> = {
      Accept: "application/vnd.github.raw",
      "User-Agent": "RB-Agent",
    };
    if (settings?.github_token) headers["Authorization"] = `Bearer ${settings.github_token}`;
    const res = await fetch(
      `https://api.github.com/repos/${data.repo}/contents/${data.path}?ref=${data.branch}`,
      { headers },
    );
    if (!res.ok) return { ok: false as const, error: `GitHub returned ${res.status}.` };
    const text = await res.text();
    return { ok: true as const, content: text.slice(0, 120000) };
  });
