import { Button, NotificationPlugin } from 'tdesign-react'
import { AddIcon, DeleteIcon } from 'tdesign-icons-react'
import { useTranslation } from 'react-i18next'

import { useState, useRef, useEffect  } from 'react'
import { getConversationList, getConversationDetail, createConversation } from '@/api/conversation'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { ChatSender } from '@tdesign-react/chat'
import type { Conversation, Message } from './type'
import WelcomePage from './components/WelcomePage'
import MessageList from './components/MessageList'

const ChatPage: React.FC = () => {
    const { t } = useTranslation()
    const { id } = useParams<{ id?: string }>()
    const navigate = useNavigate()
    const location = useLocation()
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [messages, setMessages] = useState<Message[]>([])
    const [newChatFlag, setNewChatFlag] = useState<boolean>(true)
    const [inputValue, setInputValue] = useState('')
    const [loading, setLoading] = useState(false)
    const abortControllerRef = useRef<AbortController | null>(null)

    const isEmpty = messages.length === 0
    const hanldeCreateNewChat = () => {
        navigate('/chat')
    }

    const handleLoadMessage = (id: string) => {
        getConversationDetail(id).then(res => {
            if(res.code === 200) {
                setMessages(res.data?.messageList || [])
            }
        }).catch(err => {
            NotificationPlugin.error({
                title: t('chat.error.fetchDetail'),
                content: err.message
            })
        }).finally(() => {
            setNewChatFlag(false)
        })
    }

    const handleNavToMessage = (id: string) => () => {
        navigate(`/chat/${id}`)
        setNewChatFlag(false)
    }

    const handleSendFirstMessage = async (message: string) => {
        if(!message) return
        // 1. create new conversation 
        const payload = {
            id: crypto.randomUUID(),
            user_id: 1, //TODO: implement user info later
            knowledge_base_id: 8, //TODO: implement knowledge base later
            title: message
        }
        try {
            setLoading(true)
            const res = await createConversation(payload)
            if(res.code === 200) {
                setConversations(prev => [res.data, ...prev])
                // 2. jump to new conversation page
                navigate(`/chat/${res.data.id}`, { state: { firstMessage: message } })
            }
        } catch(err) {
            NotificationPlugin.error({
                title: t('chat.error.create'),
                content: err.message
            })
        } finally {
            setLoading(false)
        }
        
    }

    const handleSendMessage = async (message: string) => {
        const uid = crypto.randomUUID()
        const aid = crypto.randomUUID()
        const userMessage: Message = {
            id: uid,
            role: 'user',
            content: message,
            create_time: new Date().toISOString()
        }
        const assitantMessage: Message = {
            id: aid,
            role: 'assistant',
            content: '',
            status: 'pending',
            create_time: new Date().toISOString()
        }
        setMessages(prev => [...prev, userMessage, assitantMessage])
        setInputValue('')
        setLoading(true)
        const controller = new AbortController()
        abortControllerRef.current = controller

        try {
            const res = await fetch(
                `${import.meta.env.VITE_APP_BASE_API}/chat/ask`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, conversation_id: id }),
                    signal: controller.signal,
                }
            )
            const reader = res.body!.getReader()
            const decoder = new TextDecoder()
            let buffer = ''
            while(true) {
                const { done, value } = await reader.read()
                if(done) break
                buffer += decoder.decode(value, {stream: true})
                const parts = buffer.split('\n\n')
                buffer = parts.pop()!  // 末尾不完整的部分留到下次
                for (const part of parts) {
                    const dataLine = part.trim()
                    if (!dataLine.startsWith('data:')) continue
                    const payload = dataLine.slice(5).trim()
                    if (payload === '[DONE]') {
                        setMessages(prev => prev.map(msg =>
                            msg.id === aid ? { ...msg, status: 'complete' } : msg
                        ))
                        break
                    }
                    let parsed: any
                    parsed = JSON.parse(payload)
                    if (parsed.error) throw new Error(parsed.error)
                    setMessages(prev => prev.map(msg =>
                        msg.id === aid
                            ? { ...msg, status: 'streaming', content: msg.content + parsed.content }
                            : msg
                    ))
                }
            }
        } catch(err: any) {
            if (err.name !== 'AbortError') {
                NotificationPlugin.error({ title: t('chat.error.send'), content: err })
                // removce pending message
                setMessages(prev => prev.filter(m => m.id !== aid))
            }
        } finally {
            setLoading(false)
            abortControllerRef.current = null
        }

    }

    const handleAbortChat = () => {
        abortControllerRef.current?.abort()
    }

    useEffect(() => {
        // ComponentDidMount
        getConversationList().then(res => {
            if(res.code === 200) {
                setConversations(res.data || [])
            }
        }).catch(err => {
            NotificationPlugin.error({
                title: t('chat.error.fetchList'),
                content: err.message
            })
        })
    }, [])

    useEffect(() => {

        if(id) {
            const firstMessage = (location.state as { firstMessage?: string })?.firstMessage
            console.log('firstMessage', firstMessage)
            // create new conversation
            if(firstMessage) {
                setNewChatFlag(false)
                navigate(location.pathname, { replace: true, state: {} })
                handleSendMessage(firstMessage)
            } else {
                // click conversation item
                handleLoadMessage(id)
            }
            
        } else {
            setNewChatFlag(true)
            setMessages([])
        }
    }, [id])

  return (
    <div className="flex h-full overflow-hidden">
      <aside className="w-[260px] flex flex-col shrink-0 border-r border-gray-200 border-r border-[var(--color-border)]">
        <div className="flex items-center justify-between p-4 text-[13px] font-medium text-[var(--color-text-secondary)]">
            <span>{t('chat.sidebar.title')}</span>
            <Button
                variant="text"
                shape="square"
                size="small"
                icon={<AddIcon />}
                title={t('chat.sidebar.newChat')}
                onClick={hanldeCreateNewChat}
            />
        </div>
        <div className="flex-1 overflow-y-auto px-2">
            {
                conversations.length === 0 ? (
                    <p className="text-center text-[13px] text-[var(--color-text-secondary)]">{t('chat.sidebar.empty')}</p>
                ) :(
                    conversations.map(conv => (
                        <div
                            key={conv.id}
                            className="group flex justify-between items-center truncate text-[14px] p-2 hover:bg-[var(--color-bg-2)] cursor-pointer hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-text-primary)]"
                        >
                            <span onClick={handleNavToMessage(conv.id)}>{conv.title}</span>
                            <Button
                                className="shrink-0 opacity-0 transition-opacity duration-150 group-hover:opacity-100"
                                variant="text"
                                shape="square"
                                size="small"
                                icon={<DeleteIcon size="14px" />}
                            >

                            </Button>
                        </div>
                    ))
                )
            }
        </div>
        <div className="h-[64px] border-t border-[var(--color-border)] p-4 text-[13px] font-medium text-[var(--color-text-secondary)]">

        </div>
      </aside>
       <div className="flex-1 flex flex-col overflow-hidden">
            {isEmpty ? 
                (
                    <WelcomePage 
                        onSend={handleSendFirstMessage}
                        onStop={handleAbortChat}
                        loading={loading}
                    />
                ) : (
                    <div className="flex-1 flex flex-col overflow-hidden">
                        <MessageList 
                            messages={messages}
                        />
                       <div className="shrink-0 bg-[var(--color-bg)] py-6">
                            <div className="max-w-[780px] mx-auto">
                                <ChatSender
                                    placeholder={t('chat.input.placeholder')}
                                    value={inputValue}
                                    loading={loading}
                                    autosize={{minRows: 1, maxRows: 1}}
                                    onChange={(e) => setInputValue(e.detail)}
                                    onSend={() => { handleSendMessage(inputValue) }}
                                    onStop={handleAbortChat}
                                />
                            </div>
                        </div> 
                    </div>
                )
            }
       </div>
    </div>
  )
}

export default ChatPage