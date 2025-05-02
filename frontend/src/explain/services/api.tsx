// src/explain/services/api.ts

import { streamResponse } from "@/utils/axiosInstance";

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
  await streamResponse(
    `/explain/stream/${level}`,
    { topic },
    (data: StreamResponsePayload) => {
      if (data.content) {
        onContent(data.content);
      }
      if (data.error) {
        onError(data.error);
      }
      if (data.done) {
        onComplete();
      }
    },
    (error: unknown) => {
      if (error instanceof Error && error.name === "AbortError") {
        console.log(`Fetch aborted for ${level}`);
      } else {
        onError(
          error instanceof Error
            ? error.message
            : "An unexpected stream error occurred"
        );
      }
    },
    () => {
      // Stream completed
    }
  );
};
