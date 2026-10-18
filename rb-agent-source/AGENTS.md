<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

- Keep the five visible specialist identities in `src/lib/agents.ts` and reuse their IDs for the home workspace and saved chats, because this keeps agent conversations isolated without duplicating routing logic.
- Keep the specialist workspace as a full-screen dialog scoped to `.agent-workspace` tokens, because the rest of the app retains its existing light theme.
