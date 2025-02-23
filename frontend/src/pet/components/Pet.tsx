import React, { useEffect, useState } from "react";

import { ChatBubble } from "./ChatBubble";
import { petApi } from "../services/api";

interface PetProps {
  position: { x: number; y: number };
  targetPosition: { x: number; y: number } | null;
}

export const Pet: React.FC<PetProps> = ({ position, targetPosition }) => {
  const isMoving = targetPosition !== null;
  const [currentMessage, setCurrentMessage] = useState<string | null>(null);
  const [messageQueue, setMessageQueue] = useState<string[]>([]);
  const isFlipped = Boolean(targetPosition && targetPosition.x < position.x);

  // Handle eating animation and message
  useEffect(() => {
    if (isMoving) {
      // Get a message when starting to move towards food
      petApi.getMessage("eat").then((message) => {
        setMessageQueue((prev) => [...prev, message]);
      });
    }
  }, [isMoving]);

  // Process message queue
  useEffect(() => {
    if (messageQueue.length > 0 && !currentMessage) {
      setCurrentMessage(messageQueue[0]);
      setMessageQueue((prev) => prev.slice(1));
    }
  }, [messageQueue, currentMessage]);

  // Occasionally show idle messages
  useEffect(() => {
    if (isMoving) return; // Don't show idle messages while moving

    const idleInterval = setInterval(async () => {
      if (Math.random() < 0.1 && !currentMessage) {
        // 10% chance every 5 seconds
        const message = await petApi.getMessage("idle");
        setMessageQueue((prev) => [...prev, message]);
      }
    }, 5000);

    return () => clearInterval(idleInterval);
  }, [isMoving, currentMessage]);

  return (
    <div
      className="absolute transition-all duration-1000 ease-in-out"
      style={{
        left: position.x - 40,
        top: position.y - 40,
        transform: isFlipped ? "scaleX(-1)" : "scaleX(1)",
      }}
    >
      <ChatBubble
        text={currentMessage || ""}
        onComplete={() => setCurrentMessage(null)}
        isFlipped={isFlipped}
      />
      <div className={`w-20 h-20 relative ${isMoving ? "animate-bounce" : ""}`}>
        {/* Body */}
        <div className="absolute w-20 h-16 bg-white rounded-[50%] bottom-0 shadow-md" />

        {/* Face */}
        <div className="absolute w-[4.5rem] h-[4.5rem] bg-white rounded-full left-[0.375rem] -top-2 shadow-md">
          {/* Eyes */}
          <div className="absolute w-3 h-4 left-4 top-4">
            <div className="absolute w-3 h-4 bg-black rounded-full" />
            <div className="absolute w-1.5 h-1.5 bg-white rounded-full left-[0.1rem] top-[0.1rem]" />
          </div>
          <div className="absolute w-3 h-4 right-4 top-4">
            <div className="absolute w-3 h-4 bg-black rounded-full" />
            <div className="absolute w-1.5 h-1.5 bg-white rounded-full left-[0.1rem] top-[0.1rem]" />
          </div>

          {/* Blush */}
          <div className="absolute w-2.5 h-1.5 bg-pink-300 rounded-full left-2 top-7 opacity-80" />
          <div className="absolute w-2.5 h-1.5 bg-pink-300 rounded-full right-2 top-7 opacity-80" />

          {/* Mouth */}
          <div
            className={`absolute w-2 h-2 bg-pink-400 rounded-full left-[2.15rem] top-8 ${
              isMoving ? "animate-[bounce_1s_infinite]" : ""
            }`}
          />

          {/* Ears */}
          <div className="absolute w-5 h-5 bg-white -left-1 -top-1 rounded-full transform -rotate-45 shadow-sm" />
          <div className="absolute w-5 h-5 bg-white -right-1 -top-1 rounded-full transform rotate-45 shadow-sm" />
          <div className="absolute w-3 h-3 bg-pink-200 left-0 top-0 rounded-full transform -rotate-45" />
          <div className="absolute w-3 h-3 bg-pink-200 right-0 top-0 rounded-full transform rotate-45" />
        </div>

        {/* Tail */}
        <div
          className={`absolute w-8 h-3 bg-white right-[-0.5rem] bottom-6 rounded-full transform origin-left shadow-sm ${
            isMoving
              ? "animate-[wag_1s_infinite]"
              : "animate-[wave_2s_infinite]"
          }`}
        />
      </div>
    </div>
  );
};
