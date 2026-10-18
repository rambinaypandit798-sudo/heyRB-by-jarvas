drop function if exists public.match_memories(uuid, extensions.vector, int);

create or replace function public.match_memories(p_embedding extensions.vector(1536), p_limit int default 6)
returns table (id uuid, content text, kind text, similarity float)
language sql stable security invoker set search_path = public, extensions as $$
  select m.id, m.content, m.kind, 1 - (m.embedding operator(extensions.<=>) p_embedding) as similarity
  from public.memories m
  where m.user_id = auth.uid() and m.embedding is not null
  order by m.embedding operator(extensions.<=>) p_embedding
  limit p_limit;
$$;

revoke all on function public.match_memories(extensions.vector, int) from public, anon;
grant execute on function public.match_memories(extensions.vector, int) to authenticated, service_role;

revoke all on function public.handle_new_user() from public, anon, authenticated;
revoke all on function public.update_updated_at_column() from public, anon, authenticated;