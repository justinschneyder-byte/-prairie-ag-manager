import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND_PATHS = [
  '/auth', '/fields', '/machines', '/crops', '/inputs', '/sprays',
  '/maintenance', '/weather', '/chat', '/export', '/import', '/health', '/blue-book',
]

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: Object.fromEntries(
      BACKEND_PATHS.map((p) => [p, { target: 'http://127.0.0.1:8000', changeOrigin: true }])
    ),
  },
})
