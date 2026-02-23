export type LaunchIntent = {
  target: string;
  mode: string;
  launcher?: string | null;
  workspace?: string | null;
  profile_id?: string | null;
  auth?: Record<string, unknown>;
};

export type LaunchSession = {
  session_id: string;
  target: string;
  mode: string;
  launcher: string | null;
  workspace: string | null;
  profile_id: string | null;
  auth: Record<string, unknown>;
  state: "planned" | "starting" | "ready" | "stopping" | "stopped" | "error";
  created_at: string;
  updated_at: string;
  error?: string;
};

export type LaunchResult<TState extends Record<string, unknown> = Record<string, unknown>> = {
  success: boolean;
  state: TState & {
    session_id: string;
    state: LaunchSession["state"];
    thin_gui?: {
      component: string;
      contract: string;
      intent: Omit<LaunchIntent, "auth">;
      session: { id: string; get: string; stream: string };
    };
  };
};
