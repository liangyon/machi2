/**
 * Utility for consuming Server-Sent Events from a POST endpoint.
 * Used for combat narration streaming.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function streamSSE(
  path: string,
  body: unknown,
  onToken: (token: string) => void,
  onDone?: () => void,
  onError?: (err: Error) => void,
  onData?: (data: Record<string, unknown>) => void
): Promise<void> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    });

    if (!res.ok || !res.body) {
      throw new Error(`SSE request failed: ${res.statusText}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          if (data === "[DONE]") {
            onDone?.();
            return;
          }
          try {
            const parsed = JSON.parse(data) as Record<string, unknown>;
            if (parsed.token) onToken(parsed.token as string);
            // Pass full parsed object to onData for result payloads
            if (onData && (parsed.result !== undefined || parsed.fled !== undefined)) {
              onData(parsed);
            }
          } catch {
            // ignore malformed lines
          }
        }
      }
    }
    onDone?.();
  } catch (err) {
    onError?.(err instanceof Error ? err : new Error(String(err)));
  }
}
