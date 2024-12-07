import "./Chat.css";

import React, { useEffect, useState } from "react";

import Message from "../components/Message";

// Add interface for chat message structure
interface ChatMessage {
  sender: "user" | "assistant";
  message: string;
}

export default function Chat() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentResponse, setCurrentResponse] = useState<string>("");
  const [, setIsLoading] = useState<boolean>(false);

  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Add scroll to bottom effect
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll when messages change or when currentResponse changes
  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, currentResponse]);

  const handleStream = async (
    messages: { role: string; content: string }[]
  ) => {
    try {
      const response = await fetch("/api/twenty-questions/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      setCurrentResponse("");
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Convert the Uint8Array to text
        const text = new TextDecoder().decode(value);
        fullResponse += text;
        setCurrentResponse(fullResponse);
      }

      // After streaming is complete, add the full response to chat history
      setChatMessages((prev) => [
        ...prev,
        { sender: "assistant", message: fullResponse },
      ]);
      setCurrentResponse("");
    } catch (error) {
      console.error("Error:", error);
    }
    setIsLoading(false);
  };

  const handleUserInput = async (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    const target = event.target as HTMLInputElement;
    if (event.key === "Enter" && target.value.trim()) {
      const userMessage = target.value;
      target.value = ""; // Clear input

      // Add user message to chat
      setChatMessages((prev) => [
        ...prev,
        { sender: "user", message: userMessage },
      ]);

      // Prepare messages for API
      const messages = [
        ...chatMessages.map((msg) => ({
          role: msg.sender === "user" ? "user" : "assistant",
          content: msg.message,
        })),
        { role: "user", content: userMessage },
      ];

      setIsLoading(true);
      handleStream(messages);
    }
  };
  console.log(currentResponse);
  return (
    <div className="app-container">
      <div className="chat-container">
        <div className="messages-container">
          {chatMessages.map((chatMessage, index) => (
            <Message {...chatMessage} key={index} />
          ))}
          {currentResponse && (
            <Message sender="assistant" message={currentResponse} />
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            id="chat-input"
            className="chat-input"
            placeholder="Ask a question..."
            onKeyUp={handleUserInput}
            autoComplete="off"
          />
        </div>
      </div>
    </div>
  );
}
