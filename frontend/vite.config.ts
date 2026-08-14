import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  // Plugins teach Vite how to handle React JSX and Tailwind CSS classes.
  plugins: [react(), tailwindcss()],

  // In local development the browser talks to Vite first, then Vite forwards
  // `/api/...` requests to FastAPI. This avoids browser CORS errors without
  // changing backend code.
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
