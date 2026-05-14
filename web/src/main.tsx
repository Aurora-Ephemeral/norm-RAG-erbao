import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import 'tdesign-react/es/style/index.css';
import '@tdesign-react/chat/es/style/index.js';
import './style/tdesign-override.css'
import './style/global.css'
import './locales'

import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
