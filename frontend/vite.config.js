import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Requests to /api/... are forwarded to the FastAPI backend, so no CORS setup is needed.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
