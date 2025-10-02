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
      const response = await fetch("/api/poeltl/get-person", {
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex flex-col relative overflow-hidden">
      {/* Subtle background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 dark:bg-blue-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 dark:opacity-10 animate-pulse"></div>
        <div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-slate-300 dark:bg-slate-700/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 dark:opacity-10 animate-pulse"
          style={{ animationDelay: "2s" }}
        ></div>
        <div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gray-200 dark:bg-gray-700/20 rounded-full mix-blend-multiply filter blur-xl opacity-20 dark:opacity-5 animate-pulse"
          style={{ animationDelay: "4s" }}
        ></div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-4xl flex-1 flex flex-col relative z-10">
        {/* Header Section */}
        <div className="flex flex-col items-center space-y-6 mb-6">
          <div className="text-center space-y-3">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-slate-600 to-gray-600 dark:from-blue-400 dark:via-slate-300 dark:to-gray-300 bg-clip-text text-transparent">
              Poeltl Chat
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-300 font-medium">
              Guess the person in 20 questions or less!
            </p>
          </div>

          <div className="flex flex-col items-center space-y-4 w-full max-w-md">
            <PersonPicker onClick={handlePersonSelected} loading={isLoading} />

            <div className="w-full space-y-3 bg-white/80 dark:bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-slate-200 dark:border-white/20 shadow-sm">
              <div className="flex justify-between text-sm font-medium text-slate-600 dark:text-slate-300">
                <span>Progress</span>
                <span className="text-slate-800 dark:text-white font-semibold">
                  {nGuesses} / 20
                </span>
              </div>
              <Progress
                value={(nGuesses / 20) * 100}
                className="h-3 bg-slate-200 dark:bg-white/20 border-0"
              />
            </div>
          </div>
        </div>

        {/* Chat Section */}
        <div className="flex-1 flex flex-col bg-white/80 dark:bg-white/10 backdrop-blur-lg rounded-2xl border border-slate-200 dark:border-white/20 shadow-xl min-h-0 overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-white/20 scrollbar-track-transparent">
            {chatMessages.length === 0 && !currentResponse && (
              <div className="text-center text-slate-600 dark:text-slate-300 py-12">
                <div className="text-6xl mb-4">🎯</div>
                <p className="text-xl font-medium">
                  Start asking questions to guess who I am!
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                  Think strategically - every question counts!
                </p>
              </div>
            )}

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
                message={`🎉 20 questions are up! I am: ${person}`}
              />
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-slate-200 dark:border-white/20 bg-white/60 dark:bg-white/5 backdrop-blur-sm p-4">
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  id="chat-input"
                  className="w-full px-4 py-3 pr-20 rounded-xl border-2 border-slate-200 dark:border-white/20 bg-white dark:bg-white/10 backdrop-blur-sm text-slate-900 dark:text-white placeholder:text-slate-500 dark:placeholder:text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-all duration-200"
                  placeholder="Ask a question..."
                  onKeyUp={handleUserInput}
                  onChange={handleInputChange}
                  autoComplete="off"
                  disabled={nGuesses >= 20}
                  maxLength={200}
                />
                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-500 dark:text-slate-300 font-medium">
                  {inputLength}/200
                </div>
              </div>

              <button
                className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-r from-blue-500 to-slate-600 text-white hover:from-blue-600 hover:to-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-blue-500/25 transform hover:scale-105 active:scale-95"
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
                  width="18"
                  height="18"
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
            </div>

            <div className="text-center text-xs text-slate-500 dark:text-slate-300 mt-3 font-medium">
              🤖 I'm just an AI, I may answer incorrectly.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
