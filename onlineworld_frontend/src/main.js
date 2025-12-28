import { createApp } from 'vue'
// import './style.css'
import App from './App.vue'
import router from './router'
import './index.css'  // Tailwind样式入口

const app = createApp(App)

app.use(router)
app.mount('#app')

document.title = '复古论坛-首页'