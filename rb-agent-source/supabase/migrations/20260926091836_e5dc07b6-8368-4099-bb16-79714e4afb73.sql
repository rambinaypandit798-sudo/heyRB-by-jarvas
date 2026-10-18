create extension if not exists vector with schema extensions;

create or replace function public.update_updated_at_column()
returns trigger as $$ begin new.updated_at = now(); return new; end; $$ language plpgsql set search_path = public;

create table public.profiles (
  id uuid primary key references auth.users on delete cascade,
  display_name text not null default 'Friend',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
grant select, insert, update, delete on public.profiles to authenticated;
grant all on public.profiles to service_role;
alter table public.profiles enable row level security;
create policy "own profile" on public.profiles for all to authenticated using (auth.uid() = id) with check (auth.uid() = id);
create trigger profiles_updated_at before update on public.profiles for each row execute function public.update_updated_at_column();

create table public.chats (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  title text not null default 'New chat',
  agent text not null default 'core',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
grant select, insert, update, delete on public.chats to authenticated;
grant all on public.chats to service_role;
alter table public.chats enable row level security;
create policy "own chats" on public.chats for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index chats_user_idx on public.chats (user_id, updated_at desc);
create trigger chats_updated_at before update on public.chats for each row execute function public.update_updated_at_column();

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  chat_id uuid not null references public.chats on delete cascade,
  user_id uuid not null references auth.users on delete cascade,
  role text not null check (role in ('user','assistant','system')),
  content text not null default '',
  created_at timestamptz not null default now()
);
grant select, insert, update, delete on public.messages to authenticated;
grant all on public.messages to service_role;
alter table public.messages enable row level security;
create policy "own messages" on public.messages for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index messages_chat_idx on public.messages (chat_id, created_at);

create table public.memories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  content text not null,
  kind text not null default 'fact',
  embedding extensions.vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
grant select, insert, update, delete on public.memories to authenticated;
grant all on public.memories to service_role;
alter table public.memories enable row level security;
create policy "own memories" on public.memories for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index memories_user_idx on public.memories (user_id, created_at desc);
create trigger memories_updated_at before update on public.memories for each row execute function public.update_updated_at_column();

create table public.user_settings (
  user_id uuid primary key references auth.users on delete cascade,
  model text not null default 'google/gemini-3.8-flash',
  voice_profile text not null default 'aarav',
  wake_word_enabled boolean not null default false,
  live_subtitles boolean not null default true,
  telegram_bot_token text,
  telegram_enabled boolean not null default false,
  whatsapp_api_key text,
  whatsapp_enabled boolean not null default false,
  github_token text,
  github_repo text,
  automation_enabled boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
grant select, insert, update, delete on public.user_settings to authenticated;
grant all on public.user_settings to service_role;
alter table public.user_settings enable row level security;
create policy "own settings" on public.user_settings for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create trigger user_settings_updated_at before update on public.user_settings for each row execute function public.update_updated_at_column();

create or replace function public.match_memories(p_user_id uuid, p_embedding extensions.vector(1536), p_limit int default 6)
returns table (id uuid, content text, kind text, similarity float)
language sql stable security definer set search_path = public, extensions as $$
  select m.id, m.content, m.kind, 1 - (m.embedding operator(extensions.<=>) p_embedding) as similarity
  from public.memories m
  where m.user_id = p_user_id and m.embedding is not null
  order by m.embedding operator(extensions.<=>) p_embedding
  limit p_limit;
$$;

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1), 'Friend'))
  on conflict (id) do nothing;
  insert into public.user_settings (user_id) values (new.id) on conflict (user_id) do nothing;
  return new;
end; $$;

create trigger on_auth_user_created after insert on auth.users for each row execute function public.handle_new_user();