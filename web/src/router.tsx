import { createBrowserRouter } from 'react-router-dom'
import Layout from '@/components/Layout'
import Home from '@/pages/Home'
import Counter from '@/pages/Counter'
import About from '@/pages/About'
import NotFound from '@/pages/NotFound'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'counter', element: <Counter /> },
      { path: 'about', element: <About /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])
