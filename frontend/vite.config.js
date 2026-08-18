import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // 프론트(5173)에서 /api 로 부르면 Django(8000)로 전달된다.
    // → 브라우저 입장에선 같은 출처처럼 보여 CORS 문제 없이 개발 가능.
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
