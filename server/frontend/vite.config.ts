import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: '0.0.0.0',
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    allowedHosts: ['lprserver.tail605477.ts.net'],
  },
})
