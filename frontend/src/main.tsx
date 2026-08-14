import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// React starts from this file. It finds the `<div id="root">` in index.html
// and renders our application inside it.
createRoot(document.getElementById('root')!).render(
  // StrictMode helps catch common React mistakes while developing.
  <StrictMode>
    <App />
  </StrictMode>,
)
