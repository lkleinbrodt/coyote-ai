import "./Poeltl.css";

import { ChatMessage, useChat } from "../hooks/useChat";
import React, { useEffect, useState } from "react";

import Message from "../components/Message";
import PersonPicker from "../components/PersonPicker";
import { Progress } from "@/components/ui/progress";

export default function Poeltl() {
  const [person, setPerson] = useState<string>("");
  const [nGuesses, setNGuesses] = useState<number>(0);
  const [inputLength, setInputLength] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const {
    chatMessages,
    currentResponse,
    handleStream,
    addMessage,
    resetChat,
    setChatMessages,
  } = useChat(person);

  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, currentResponse]);

  useEffect(() => {
    setNGuesses(chatMessages.filter((msg) => msg.role === "user").length);
  }, [chatMessages]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputLength(event.target.value.length);
  };

  const handleSubmit = (message: string) => {
    if (nGuesses >= 20) {
      return;
    }
    const userMessage = message;

    addMessage(userMessage, "user");

    const messages = [
      ...chatMessages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
      { role: "user", content: userMessage },
    ];

    handleStream(messages as ChatMessage[]);

    const input = document.getElementById("chat-input") as HTMLInputElement;
    input.value = "";

    setInputLength(0);
  };

  const handleUserInput = async (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    const target = event.target as HTMLInputElement;

    if (event.key === "Enter" && target.value.trim()) {
      handleSubmit(target.value);
    }
  };
  const getPerson = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/twenty-questions/get-person", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      //sleep for 1 second
      await new Promise((resolve) => setTimeout(resolve, 500));

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPerson(data.person);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePersonSelected = () => {
    (async () => {
      setChatMessages([]);
      await getPerson();
      resetChat();
    })();
  };

  useEffect(() => {
    handlePersonSelected();
  }, []);

  return (
    <div className="app-container">
      <div className="container d-flex flex-column align-items-center flex-col">
        <div className="header gap-2">
          <PersonPicker onClick={handlePersonSelected} loading={isLoading} />
          <Progress value={(nGuesses / 20) * 100} />
          <h4 className="text-muted-foreground">{nGuesses} / 20</h4>
        </div>
      </div>
      <div className="chat-container">
        <div className="messages-container">
          {chatMessages.map((chatMessage, index) => (
            <Message
              sender={chatMessage.role}
              message={chatMessage.content}
              key={index}
            />
          ))}
          {currentResponse && (
            <Message sender="assistant" message={currentResponse} />
          )}
          {nGuesses >= 20 && (
            <Message
              sender="assistant"
              message={`20 questions are up. I am: ${person}`}
            />
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <input
              type="text"
              id="chat-input"
              className="chat-input"
              placeholder="Ask a question..."
              onKeyUp={handleUserInput}
              onChange={handleInputChange}
              autoComplete="off"
              disabled={nGuesses >= 20}
              maxLength={200}
            />
            <div>
              <button
                className="send-button"
                onClick={() => {
                  const input = document.getElementById(
                    "chat-input"
                  ) as HTMLInputElement;
                  handleSubmit(input.value);
                }}
                disabled={nGuesses >= 20}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  stroke="currentColor"
                >
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
              <div className="character-counter">{inputLength}/200</div>
            </div>
          </div>
        </div>

        <div className="disclaimer">
          I'm just an AI, I may answer incorrectly.
        </div>
      </div>
    </div>
  );
}
