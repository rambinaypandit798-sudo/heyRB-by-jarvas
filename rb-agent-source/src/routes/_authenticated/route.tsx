import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";

import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/_authenticated")({
  ssr: false,
  beforeLoad: async () => {
    // Auth bypass: skip login check and load app directly
    const { data } = await supabase.auth.getUser().catch(() => ({ data: { user: null } }));
    const defaultUser = {
      id: "00000000-0000-0000-0000-000000000000",
      email: "user@local",
      user_metadata: { display_name: "Ram" },
      app_metadata: {},
      aud: "authenticated",
      created_at: new Date().toISOString(),
    };
    return { user: data?.user || defaultUser };
  },
  component: () => <Outlet />,
});
