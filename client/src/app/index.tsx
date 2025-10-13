import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../shared/styles/global.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <h1 className="text-2xl font-bold text-red-500">Hello World</h1>
  </StrictMode>
)
