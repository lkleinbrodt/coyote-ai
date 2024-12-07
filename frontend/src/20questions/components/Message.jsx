import "./Message.css";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

import React from "react";

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

function Message(props, index) {
  let sender = props.sender;
  let content = props.message;

  //TODO: it would be cool to use the first letter of the current USERNAME, instead of just "you"

  return (
    <div key={`message-${index}`} className={`message ${sender}`}>
      <div className={`message header ${sender}`}>
        {sender === "user" ? null : <AssistantAvatar />}
      </div>
      <div className={`message content ${sender}`}>{content}</div>
    </div>
  );

  // return (
  //   <div data-role={dataRoll} className="bubble-container">
  //     <div className={thisClass}>
  //       <div className="text_message">
  //         {props.message.replace(/<\/?[^>]+(>|$)/g, "")}
  //       </div>
  //     </div>
  //     <div className="clear"></div>
  //   </div>
  // );
}
export default Message;
