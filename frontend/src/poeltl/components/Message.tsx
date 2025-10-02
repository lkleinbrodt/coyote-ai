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
    <div
      className={`flex items-start space-x-3 ${
        sender === "user" ? "flex-row-reverse space-x-reverse" : ""
      }`}
    >
      {sender === "assistant" && (
        <div className="flex-shrink-0">
          <AssistantAvatar />
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 backdrop-blur-sm ${
          sender === "user"
            ? "bg-gradient-to-r from-blue-500 to-slate-600 text-white ml-auto shadow-lg"
            : "bg-slate-100 dark:bg-white/20 text-slate-900 dark:text-white border border-slate-200 dark:border-white/30"
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">
          {message}
        </p>
      </div>
      {sender === "user" && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-slate-500 flex items-center justify-center shadow-lg">
            <span className="text-xs font-bold text-white">You</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Message;
