import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* BrowserRouter: 주소(URL)에 따라 다른 페이지를 보여주기 위한 라우터 */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
