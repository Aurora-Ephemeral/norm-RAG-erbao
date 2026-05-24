import { createBrowserRouter, Navigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import Chat from '@/pages/chat/index'
import NotFound from '@/pages/NotFound'
import KnowledgeBase from '@/pages/knowledge_base/index'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/chat" replace /> },
      { path: 'chat/:id?', element: <Chat /> },
      { path: 'knowledgeBase', element: <KnowledgeBase /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])
