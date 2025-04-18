import "./Message.css";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

// Define types
interface MessageProps {
  sender: "user" | "assistant";
  message: string;
}

const AssistantAvatar = () => {
  return (
    <Avatar>
      <AvatarImage src="icons/AI Basketball.png" alt="AI Assistant" />
      <AvatarFallback>AI</AvatarFallback>
    </Avatar>
  );
};

function Message({ sender, message }: MessageProps) {
  return (
    <div className={`message ${sender}`}>
      {sender === "assistant" && (
        <div className={`message header ${sender}`}>
          <AssistantAvatar />
        </div>
      )}
      <div className={`message content ${sender}`}>{message}</div>
    </div>
  );
}

export default Message;
