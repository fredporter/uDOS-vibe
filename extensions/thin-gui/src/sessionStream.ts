import type { LaunchSession } from "./contracts";

export type SessionStreamEvent =
  | { type: "session"; session: LaunchSession }
  | { type: "end"; reason: string }
  | { type: "error"; message: string };

export async function consumeSessionStream(
  fetcher: typeof fetch,
  streamPath: string,
  onEvent: (event: SessionStreamEvent) => void,
): Promise<void> {
  const response = await fetcher(streamPath, {
    method: "GET",
    headers: { Accept: "text/event-stream" },
  });

  if (!response.ok || !response.body) {
    onEvent({ type: "error", message: `stream unavailable (${response.status})` });
    return;
  }

  const decoder = new TextDecoder();
  const reader = response.body.getReader();
  let buffer = "";

  while (true) {
    const next = await reader.read();
    if (next.done) {
      onEvent({ type: "end", reason: "closed" });
      return;
    }

    buffer += decoder.decode(next.value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const eventName = frame
        .split("\n")
        .find((line) => line.startsWith("event:"))
        ?.slice(6)
        .trim();
      const payload = frame
        .split("\n")
        .find((line) => line.startsWith("data:"))
        ?.slice(5)
        .trim();

      if (!eventName || !payload) {
        continue;
      }

      if (eventName === "session") {
        onEvent({ type: "session", session: JSON.parse(payload) as LaunchSession });
        continue;
      }

      if (eventName === "end") {
        const parsed = JSON.parse(payload) as { reason?: string };
        onEvent({ type: "end", reason: parsed.reason ?? "unknown" });
        return;
      }
    }
  }
}
