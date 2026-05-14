import type { Message } from '../type'
import { ChatMessage, ChatSender } from '@tdesign-react/chat'
import { useState, useRef, useEffect } from 'react'
interface Props {
    messages: Message[]
}

const MessageList: React.FC<Props> = ({ messages }) => {
    const messageListRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
      if(messageListRef.current) {
          messageListRef.current.scrollTop = messageListRef.current.scrollHeight
      }
  }, [messages])
  return(
    <div
        className="flex-1 overflow-y-auto p-6 flex flex-col gap-6"
        ref={messageListRef}
    >
        {
            messages.map(msg => (
                <div
                    key={msg.id}
                    className="flex gap-3 max-w-[780px] w-full mx-auto"
                >
                    <ChatMessage 
                        role={msg.role} 
                        content={[{type: msg.role === 'user' ? 'text' : 'markdown', data: msg.content}]}
                        variant={msg.role === 'user' ? 'outline' : 'text'}
                        placement={msg.role === 'user' ? 'right' : 'left'}
                        status={msg.status || 'complete'}
                    />
                </div>
            ))
        }
    </div>
    
  )
}

export default MessageList