import React from 'react'
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const Message = (props) => {
  return (
    <div className={`grid p-5 w-full ${props.is_assistant ? "flex-col justify-items-start" : "flex-col-reverse justify-items-end"}`}>
      {/* Avatar */}
      <Avatar>
        <AvatarFallback>{props.is_assistant ? "A" : "U"}</AvatarFallback>
      </Avatar>
      {/* content */}
      <div className={`rounded-3xl h-fit ${props.is_assistant ? "bg-slate-200": "bg-slate-300"}`}>
        <p className={`p-5 min-w-20 max-w-64 ${props.is_assistant? "text-left" : "text-right"}`}>{props.content}</p>
      </div>
    </div>
  )
}

export default Message