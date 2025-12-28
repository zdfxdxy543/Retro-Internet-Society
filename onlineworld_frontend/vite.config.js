import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 8080,
    proxy: {
      // 代理后端API（隐藏真实请求地址）
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        // 不要重写路径，因为后端API蓝图已经有/api前缀
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
      // 代理邮箱系统API调用，但保留前端路由功能
      '/email/register': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/email/login': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/email/logout': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/email/status': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/email/send': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/email/inbox': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/email/outbox': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    // 隐藏Vue标识（拟真）
    rollupOptions: {
      output: {
        manualChunks: undefined,
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
})