import { twentyQuestionsApi } from "../services/api";
import { useState } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export const useChat = (person: string) => {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Ok, I'm ready. Ask me questions to guess who I'm thinking of!",
    },
  ]);
  const [currentResponse, setCurrentResponse] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleStream = async (messages: ChatMessage[]) => {
    try {
      const responseBody = await twentyQuestionsApi.askQuestion(
        messages,
        person
      );
      if (!responseBody) throw new Error("No response body");

      const reader = responseBody.getReader();
      setCurrentResponse("");
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = new TextDecoder().decode(value);
        fullResponse += text;
        setCurrentResponse(fullResponse);
      }

      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: fullResponse },
      ]);
      setCurrentResponse("");
    } catch (error) {
      console.error("Error:", error);
    }
    setIsLoading(false);
  };

  const addMessage = (message: string, role: "user" | "assistant") => {
    setChatMessages((prev) => [...prev, { role, content: message }]);
  };

  const resetChat = () => {
    setChatMessages([
      {
        role: "assistant",
        content:
          "Ok, I'm ready. Ask me questions to guess who I'm thinking of!",
      },
    ]);
  };

  return {
    chatMessages,
    currentResponse,
    isLoading,
    handleStream,
    addMessage,
    resetChat,
    setChatMessages,
  };
};
