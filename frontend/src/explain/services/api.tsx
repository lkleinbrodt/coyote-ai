// src/explain/services/api.ts

import axiosInstance from "@/utils/axiosInstance";

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
    const response = await axiosInstance.post(
      `/explain/stream/${level}`,
      { topic },
      {
        headers: {
          Accept: "text/event-stream",
        },
        responseType: "stream",
        signal,
      }
    );

    if (!response.data) {
      throw new Error("Response body is null");
    }

    reader = response.data.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      if (!reader) {
        throw new Error("Stream reader is null");
      }

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
