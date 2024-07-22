import React from 'react'
import Message from '@/components/Message'

const ChatHistory = (props) => {
  return (
    <div className='flex-col grid justify-items-end'>
      {props.messages.map((msg, idx) => (
        <Message key={idx} is_assistant={msg.is_assistant} content={msg.message} />
      ))
      }
    </div>
  )
}

export default ChatHistory