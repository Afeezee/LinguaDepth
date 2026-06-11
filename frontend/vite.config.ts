import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Read .env from the project root so backend and frontend share one file
  envDir: '..',
  server: {
    port: 5173,
  },
})
