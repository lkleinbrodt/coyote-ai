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
      <AvatarImage
        src="https://api.iconify.design/mdi:robot.svg"
        alt="AI Assistant"
      />
      <AvatarFallback>AI</AvatarFallback>
    </Avatar>
  );
};

function Message({ sender, message }: MessageProps) {
  return (
    <div className={`message ${sender}`}>
      <div className={`message header ${sender}`}>
        {sender === "user" ? null : <AssistantAvatar />}
      </div>
      <div className={`message content ${sender}`}>{message}</div>
    </div>
  );
}

export default Message;
