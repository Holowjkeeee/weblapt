import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],

  preview: {
    host: '127.0.0.1',
    port: 4173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/accounts': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/accounts': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})