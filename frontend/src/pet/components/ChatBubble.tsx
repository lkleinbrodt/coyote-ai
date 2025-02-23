import React, { useEffect, useState } from "react";

interface ChatBubbleProps {
  text: string;
  onComplete?: () => void;
  isFlipped?: boolean;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  text,
  onComplete,
  isFlipped = false,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!text) {
      setIsVisible(false);
      return;
    }

    // Show the bubble immediately
    setIsVisible(true);

    // Calculate display duration based on text length (minimum 2 seconds, 100ms per character)
    const displayDuration = Math.max(2000, text.length);

    // Start fade out
    const fadeOutTimer = setTimeout(() => {
      setIsVisible(false);
    }, displayDuration);

    // Call onComplete after fade out animation
    const cleanupTimer = setTimeout(() => {
      onComplete?.();
    }, displayDuration + 500); // 500ms matches the CSS transition duration

    return () => {
      clearTimeout(fadeOutTimer);
      clearTimeout(cleanupTimer);
    };
  }, [text, onComplete]);

  if (!text) return null;

  return (
    <div
      className={`absolute -top-16 ${
        isFlipped ? "right-4" : "-left-4"
      } transform transition-opacity duration-500 ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
      style={{
        // Ensure text is always readable by counteracting parent's transform
        transform: isFlipped
          ? "scaleX(-1) translateX(50%)"
          : "translateX(-50%)",
      }}
    >
      {/* Chat bubble container */}
      <div className="relative bg-white rounded-xl p-3 shadow-md">
        {/* Bubble text - counter flip when parent is flipped */}
        <p
          className="text-gray-800 text-sm whitespace-pre-wrap max-w-[200px]"
          style={{ transform: isFlipped ? "scaleX(-1)" : "none" }}
        >
          {text}
        </p>
        {/* Bubble tail */}
        <div className="absolute bottom-0 left-1/2 transform translate-x-1/2 translate-y-1/2 rotate-45 w-4 h-4 bg-white" />
      </div>
    </div>
  );
};
