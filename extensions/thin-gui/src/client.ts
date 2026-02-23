import type { LaunchIntent, LaunchResult } from "./contracts";
import { consumeSessionStream, type SessionStreamEvent } from "./sessionStream";

export async function emitLaunchIntent<TState extends Record<string, unknown> = Record<string, unknown>>(
  fetcher: typeof fetch,
  launchPath: string,
  intent: LaunchIntent,
): Promise<LaunchResult<TState>> {
  const response = await fetcher(launchPath, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(intent),
  });

  if (!response.ok) {
    throw new Error(`launch intent failed (${response.status})`);
  }

  return (await response.json()) as LaunchResult<TState>;
}

export async function consumeLaunchSession(
  fetcher: typeof fetch,
  sessionId: string,
  onEvent: (event: SessionStreamEvent) => void,
): Promise<void> {
  await consumeSessionStream(fetcher, `/api/platform/launch/sessions/${sessionId}/stream`, onEvent);
}
