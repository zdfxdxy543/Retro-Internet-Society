/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 复古论坛配色（灰色、深蓝色为主）
        retro: {
          bg: '#f0f0f0',
          header: '#003366',
          text: '#333333',
          link: '#0066cc',
          border: '#cccccc',
          postBg: '#ffffff',
          replyBg: '#f9f9f9'
        }
      },
      fontFamily: {
        // 复古宋体
        song: ['SimSun', 'STSong', 'serif']
      }
    },
  },
  plugins: [],
  corePlugins: {
    // 禁用现代圆角（复古论坛多为直角）
    borderRadius: false,
    // 禁用阴影（复古论坛无阴影）
    boxShadow: false
  }
}

