-- Supabase schema for mentorship + profiles with RLS and RPC

create type if not exists connection_status as enum ('pending','active','completed','cancelled');
create type if not exists message_type as enum ('text','file','image','audio','video','system');

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text unique,
  username text unique,
  full_name text,
  role text check (role in ('admin','mentor','tutor','student')) not null default 'student',
  bio text,
  teaching_experience text,
  specializations jsonb,
  certifications jsonb,
  timezone text,
  available_days jsonb,
  available_hours jsonb,
  is_available_for_mentorship boolean default false,
  max_mentees int default 3,
  created_at timestamptz default now()
);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, email, username, full_name, role)
  values (new.id, new.email, split_part(new.email,'@',1), coalesce(new.raw_user_meta_data->>'full_name',''), coalesce(new.raw_user_meta_data->>'role','student'))
  on conflict (id) do nothing;
  return new;
end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_user();

create table if not exists public.mentorship_connections (
  id bigserial primary key,
  mentor_id uuid not null references auth.users(id),
  mentee_id uuid not null references auth.users(id),
  status connection_status not null default 'pending',
  connection_message text,
  goals jsonb,
  target_band_score numeric(3,1),
  focus_areas jsonb,
  created_at timestamptz default now()
);
create unique index if not exists uniq_pair_active on public.mentorship_connections(mentor_id, mentee_id) where status in ('pending','active');

create table if not exists public.mentorship_messages (
  id bigserial primary key,
  connection_id bigint not null references public.mentorship_connections(id) on delete cascade,
  sender_id uuid not null references auth.users(id),
  message_type message_type not null default 'text',
  content text,
  file_url text,
  is_read boolean default false,
  created_at timestamptz default now()
);
create index if not exists idx_messages_conn_time on public.mentorship_messages(connection_id, created_at);

alter table public.profiles enable row level security;
alter table public.mentorship_connections enable row level security;
alter table public.mentorship_messages enable row level security;

create policy profiles_read_all on public.profiles for select to authenticated using (true);
create policy profiles_update_self on public.profiles for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);

create policy conns_select_participant on public.mentorship_connections for select to authenticated
  using (auth.uid() = mentor_id or auth.uid() = mentee_id);
create policy conns_insert_as_mentee on public.mentorship_connections for insert to authenticated
  with check (mentee_id = auth.uid());
create policy conns_update_participant on public.mentorship_connections for update to authenticated
  using (auth.uid() = mentor_id or auth.uid() = mentee_id) with check (true);
create policy conns_delete_participant on public.mentorship_connections for delete to authenticated
  using (auth.uid() = mentor_id or auth.uid() = mentee_id);

create policy msgs_select_participant on public.mentorship_messages for select to authenticated
  using (exists(select 1 from public.mentorship_connections c where c.id = connection_id and auth.uid() in (c.mentor_id, c.mentee_id)));
create policy msgs_insert_participant on public.mentorship_messages for insert to authenticated
  with check (
    sender_id = auth.uid()
    and exists(select 1 from public.mentorship_connections c where c.id = connection_id and auth.uid() in (c.mentor_id, c.mentee_id))
  );

create or replace function public.request_connection(
  p_mentor_id uuid,
  p_message text default null,
  p_goals jsonb default null,
  p_target_band_score numeric(3,1) default null,
  p_focus_areas jsonb default null
) returns bigint
language plpgsql security definer as $$
declare new_id bigint;
begin
  insert into public.mentorship_connections (mentor_id, mentee_id, connection_message, goals, target_band_score, focus_areas)
  values (p_mentor_id, auth.uid(), p_message, p_goals, p_target_band_score, p_focus_areas)
  returning id into new_id;
  return new_id;
end; $$;

grant execute on function public.request_connection(uuid, text, jsonb, numeric, jsonb) to authenticated;
