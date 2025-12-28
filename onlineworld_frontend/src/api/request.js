import axios from 'axios'

// 创建axios实例（隐藏请求标识）
const service = axios.create({
  baseURL: import.meta.env.DEV ? '' : '',  // 开发环境代理到/api，生产环境直接访问
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    // 模拟真实浏览器请求头，隐藏Vue标识
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
  },
  withCredentials: true  // 允许携带Cookie（玩家匿名状态）
})

// 请求拦截器：无额外操作，保持简洁
service.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器：处理404等错误
service.interceptors.response.use(
  response => response.data,
  error => {
    // 模拟真实404页面
    if (error.response && error.response.status === 404) {
      const errorMsg = error.response.data.html || '<h1>404 页面不存在</h1>'
      document.body.innerHTML = `
        <div style="width: 80%; margin: 50px auto; font-family: SimSun;">
          ${errorMsg}
          <p style="margin-top: 20px;"><a href="/" style="color: #0066cc;">返回论坛首页</a></p>
        </div>
      `
    }
    return Promise.reject(error)
  }
)

export default service