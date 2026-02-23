import path from "node:path";

export type TaskCliDefaults = {
  vaultRoot: string;
  dbPath: string;
  missionId?: string;
  runsRoot: string;
};

export type RendererCliDefaults = {
  theme: string;
  vaultRoot: string;
  themesRoot: string;
  outputRoot: string;
  missionId?: string;
  runsRoot: string;
};

export function resolveTaskCliDefaults(cwd: string = process.cwd()): TaskCliDefaults {
  const vaultRoot =
    process.env.VAULT_ROOT ??
    path.resolve(cwd, "..", "..", "memory", "vault");
  return {
    vaultRoot,
    dbPath:
      process.env.DB_PATH ??
      path.resolve(cwd, "..", "..", "memory", "vault", ".udos", "state.db"),
    missionId: process.env.MISSION_ID,
    runsRoot:
      process.env.RUNS_ROOT ??
      path.resolve(cwd, "..", "..", "memory", "vault", "06_RUNS"),
  };
}

export function resolveRendererCliDefaults(
  cwd: string = process.cwd(),
): RendererCliDefaults {
  const vaultRoot =
    process.env.VAULT_ROOT ?? path.resolve(cwd, "..", "memory", "vault");
  return {
    theme: process.env.THEME ?? "prose",
    vaultRoot,
    themesRoot: process.env.THEMES_ROOT ?? path.resolve(cwd, "..", "themes"),
    outputRoot:
      process.env.OUTPUT_ROOT ??
      path.resolve(cwd, "..", "memory", "vault", "_site"),
    missionId: process.env.MISSION_ID,
    runsRoot: process.env.RUNS_ROOT ?? path.join(vaultRoot, "06_RUNS"),
  };
}

