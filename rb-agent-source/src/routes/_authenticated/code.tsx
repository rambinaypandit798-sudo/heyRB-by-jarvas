import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { FileCode2, FolderGit2, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/AppShell";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSettings, useUpdateSettings } from "@/hooks/useAccount";
import { githubFile, githubTree } from "@/lib/vault.functions";

export const Route = createFileRoute("/_authenticated/code")({
  head: () => ({
    meta: [
      { title: "Code Preview — RB Agent" },
      { name: "description", content: "Browse your connected GitHub repository files inside RB Agent." },
      { property: "og:title", content: "Code Preview — RB Agent" },
      { property: "og:description", content: "GitHub connected code viewer for repository files." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: CodePreview,
});

function CodePreview() {
  const { data: settings } = useSettings();
  const updateSettings = useUpdateSettings();
  const loadTree = useServerFn(githubTree);
  const loadFile = useServerFn(githubFile);

  const [repo, setRepo] = useState("");
  const [branch, setBranch] = useState("");
  const [files, setFiles] = useState<{ path: string; size?: number }[]>([]);
  const [activePath, setActivePath] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");

  useEffect(() => {
    if (settings?.github_repo) setRepo(settings.github_repo);
  }, [settings?.github_repo]);

  const tree = useMutation({
    mutationFn: async (value: string) => loadTree({ data: { repo: value } }),
    onSuccess: (result) => {
      if (!result.ok) {
        toast.error(result.error);
        return;
      }
      setBranch(result.branch);
      setFiles(result.files);
      setActivePath(null);
      setContent("");
    },
    onError: (error) => toast.error(error.message),
  });

  const file = useMutation({
    mutationFn: async (path: string) => loadFile({ data: { repo, path, branch } }),
    onSuccess: (result, path) => {
      if (!result.ok) {
        toast.error(result.error);
        return;
      }
      setActivePath(path);
      setContent(result.content);
    },
    onError: (error) => toast.error(error.message),
  });

  return (
    <AppShell title="Code Preview">
      <div className="mx-auto w-full max-w-3xl space-y-4 px-4 pt-4">
        <div className="glass rounded-3xl p-4">
          <p className="font-display flex items-center gap-2 text-sm font-semibold">
            <FolderGit2 className="size-4 text-primary" /> GitHub repository
          </p>
          <div className="mt-3 flex gap-2">
            <Input
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder="owner/repository"
              className="glass h-11 rounded-xl border-0"
            />
            <Button
              className="h-11 rounded-xl"
              disabled={!repo.includes("/") || tree.isPending}
              onClick={() => {
                tree.mutate(repo);
                updateSettings.mutate({ ...settings, github_repo: repo });
              }}
            >
              {tree.isPending ? <Loader2 className="size-4 animate-spin" /> : "Load"}
            </Button>
          </div>
          <p className="mt-2 text-[11px] text-muted-foreground">
            Private repositories need your GitHub token, saved in Settings.
          </p>
        </div>

        {files.length ? (
          <div className="grid gap-4 md:grid-cols-[minmax(0,15rem)_1fr]">
            <div className="glass max-h-[60vh] overflow-y-auto rounded-3xl p-2">
              {files.map((item) => (
                <button
                  key={item.path}
                  type="button"
                  onClick={() => file.mutate(item.path)}
                  className={`flex w-full items-center gap-2 rounded-xl px-2.5 py-2 text-left text-xs transition-colors hover:bg-accent ${
                    activePath === item.path ? "bg-accent text-accent-foreground" : ""
                  }`}
                >
                  <FileCode2 className="size-3.5 shrink-0 text-muted-foreground" />
                  <span className="truncate">{item.path}</span>
                </button>
              ))}
            </div>
            <div className="glass overflow-hidden rounded-3xl">
              <p className="truncate border-b border-border px-4 py-3 text-xs font-semibold">
                {activePath ?? `${files.length} files on ${branch}`}
              </p>
              {file.isPending ? (
                <div className="grid h-40 place-items-center">
                  <Loader2 className="size-5 animate-spin text-primary" />
                </div>
              ) : (
                <pre className="max-h-[54vh] overflow-auto px-4 py-3 text-[11px] leading-5">
                  {content || "Select a file to read its code."}
                </pre>
              )}
            </div>
          </div>
        ) : (
          <div className="glass grid place-items-center rounded-3xl px-8 py-16 text-center">
            <div>
              <p className="font-display text-lg font-semibold">Connect a repository</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Enter an owner and repository name to browse its files and code.
              </p>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
