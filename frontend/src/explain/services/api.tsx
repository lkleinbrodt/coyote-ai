// src/explain/services/api.ts

// Define the base URL directly, using environment variables
const API_BASE_URL = `${import.meta.env.VITE_BASE_URL || ""}api/explain`;

export type ExplanationLevel = "child" | "student" | "professional" | "expert";

interface StreamResponsePayload {
  content?: string;
  done?: boolean;
  error?: string; // Match backend error field name
}

export const streamExplanation = async (
  topic: string,
  level: ExplanationLevel,
  onContent: (content: string) => void,
  onComplete: () => void,
  onError: (error: string) => void
): Promise<void> => {
  let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
  const controller = new AbortController();
  const signal = controller.signal;

  try {
    const response = await fetch(`${API_BASE_URL}/stream/${level}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ topic }),
      signal,
    });

    if (!response.ok) {
      let errorJson;
      try {
        errorJson = await response.json();
      } catch {
        // Ignore parsing error
      }
      const errorMessage =
        errorJson?.error?.message ||
        `HTTP error! Status: ${response.status} ${response.statusText}`;
      throw new Error(errorMessage);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      let boundary = buffer.indexOf("\n\n");
      while (boundary >= 0) {
        const message = buffer.substring(0, boundary);
        buffer = buffer.substring(boundary + 2);

        if (message.startsWith("data:")) {
          const dataString = message.substring(5).trim();
          if (dataString) {
            try {
              const data: StreamResponsePayload = JSON.parse(dataString);
              if (data.content) {
                onContent(data.content);
              }
              if (data.error) {
                onError(data.error);
              }
              if (data.done) {
                onComplete();
              }
            } catch (e) {
              console.error(`Error parsing stream JSON:`, e);
            }
          }
        }

        boundary = buffer.indexOf("\n\n");
      }
    }

    if (buffer.trim() && buffer.startsWith("data:")) {
      console.warn(`Processing final buffer content: ${buffer}`);
    }
  } catch (error: unknown) {
    if (error instanceof Error && error.name === "AbortError") {
      console.log(`Fetch aborted for ${level}`);
    } else {
      onError(
        error instanceof Error
          ? error.message
          : "An unexpected stream error occurred"
      );
    }
  } finally {
    if (reader) {
      try {
        await reader.cancel();
      } catch (e) {
        console.error(`Error cancelling stream reader:`, e);
      }
    }
  }
};
