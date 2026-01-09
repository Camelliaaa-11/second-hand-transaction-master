import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    // 允许局域网访问
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        // 指向你的电脑 IP (后端地址)
        target: 'http://192.168.92.1:5011',
        changeOrigin: true
      }
      // ❌ 注意：这里把 /uploads 删掉了，千万别加！
    }
  }
})