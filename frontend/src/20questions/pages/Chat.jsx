import "./Chat.css";

import React, { useEffect, useState } from "react";

import Message from "../components/Message";

const Chat = () => {
  const [chatMessages, setChatMessages] = useState([]);
  const [currentResponse, setCurrentResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = React.useRef(null);

  // Add scroll to bottom effect
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll when messages change or when currentResponse changes
  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, currentResponse]);

  const handleStream = async (messages) => {
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

  const handleUserInput = async (event) => {
    if (event.key === "Enter" && event.target.value.trim()) {
      const userMessage = event.target.value;
      event.target.value = ""; // Clear input

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
};

export default Chat;
