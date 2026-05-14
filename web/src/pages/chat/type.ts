export interface Conversation {
  id: string
  title: string
}

export interface Message {
  id: string
  create_time: string
  content: string
  role: string,
  status?: string
}