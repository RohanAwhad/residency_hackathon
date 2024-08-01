import React, { useEffect, useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { getChatResponse, getDummyChatHistory, getDummySuggestions } from "@/api";
import ChatHistory from "@/components/ChatHistory";
import Suggestions from "@/components/Suggestions";




/*
It needs to have:
- an Icon / separator to determine who the sent the message
- a history of messages
- 3 suggestions for the user to send
  - on click, it should set the text input to the suggestion
- a text input to send messages
- send button to send the message
- streaming output of assistant reply
- a way to access prev sessions
  - sidebar
- a way to edit the previous messages (skip for now)
- a way to generate title for the conversation

Msg Attributs:
- is_assitant
- content

Will have:
- list of messages
- list of suggestions (len: 3)
- user curr msg
- generatingMsg (bool: True when assistant is generating the msg)
*/



const ChatTab = (props) => {
  //vars
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [userCurrMsg, setUserCurrMsg] = useState("");
  const [generatingMsg, setGeneratingMsg] = useState(false);
  const scrollRef = useRef(null);

  // functions
  // useEffect(() => {
  //   setMessages(getDummyChatHistory());
  //   // setSuggestions(getDummySuggestions());
  //   // console.log(getDummySuggestions())
  // }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e) => {
    setUserCurrMsg(e.target.value);
  }
  const handleSendMessage = () => {
    console.log("Sending message: ", userCurrMsg);
    const history = messages
    setMessages(messages => {
      const newMessages = [...messages, { is_assistant: false, message: userCurrMsg }]
      return newMessages
    });
    setUserCurrMsg("");
    setGeneratingMsg(true);

    getChatResponse(props.url, history, userCurrMsg).then((response) => {
      setMessages(messages => {
        const newMessages = [...messages, { is_assistant: true, message: response.new_response }]
        return newMessages;
      });
      setSuggestions(response.suggestions);
    });
  }

  //render
  return (
    // scroll area
    <div className="h-screen grid justify-items-end">
      <ScrollArea className="w-full h-full flex-col" ref={scrollRef}>
        {messages && <ChatHistory messages={messages} />}
        {suggestions && <Suggestions suggestions={suggestions} setUserCurrMsg={setUserCurrMsg} />}
      </ScrollArea>
      <div className="flex rounded-full border-2 items-center w-full px-3 my-3 h-fit">
        <Input className='text-base border-none py-2' type="text" placeholder="Message your Paper" onChange={handleInputChange} value={userCurrMsg} />
        <Button className="text-base my-1 rounded-full w-fit" onClick={handleSendMessage}>
          Send
        </Button>
      </div>
    </div>
  )
}

export default ChatTab;
