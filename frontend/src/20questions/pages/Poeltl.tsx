import "./Poeltl.css";

import { ChatMessage, useChat } from "../hooks/useChat";
import React, { useEffect, useState } from "react";

import Message from "../components/Message";
import PersonPicker from "../components/PersonPicker";

export default function Poeltl() {
  const [person, setPerson] = useState<string>("");
  const [nGuesses, setNGuesses] = useState<number>(0);
  const [inputLength, setInputLength] = useState<number>(0);

  const { chatMessages, currentResponse, handleStream, addMessage, resetChat } =
    useChat(person);

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

  const handleUserInput = async (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    const target = event.target as HTMLInputElement;

    if (nGuesses >= 20) {
      return;
    }

    if (event.key === "Enter" && target.value.trim()) {
      const userMessage = target.value;
      target.value = "";

      addMessage(userMessage, "user");

      const messages = [
        ...chatMessages.map((msg) => ({
          role: msg.role,
          content: msg.content,
        })),
        { role: "user", content: userMessage },
      ];

      handleStream(messages as ChatMessage[]);
    }
  };

  const handlePersonSelected = (person: string) => {
    setPerson(person);
    resetChat();
  };

  console.log("currentResponse: ", currentResponse);
  return (
    <div className="app-container">
      <div className="container d-flex flex-column align-items-center flex-col">
        <div className="person-picker-container">
          <PersonPicker
            onPersonSelected={handlePersonSelected}
            disabled={false}
          />
        </div>
        <div className="guess-counter">
          Guesses: {chatMessages.filter((msg) => msg.role === "user").length}
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
        </div>
        <div className="character-counter">{inputLength}/200</div>
        <div className="disclaimer">
          I'm just an AI, I may answer incorrectly.
        </div>
      </div>
    </div>
  );
}
