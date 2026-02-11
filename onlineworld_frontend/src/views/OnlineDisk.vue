<template>
  <div class="disk-container">
    <header class="disk-header">
      <h1>在线网盘</h1>
      <p>输入分享号和密码下载文件</p>
    </header>
    
    <main class="disk-main">
      <form class="disk-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="share_id">分享号</label>
          <input 
            id="share_id"
            v-model="form.share_id" 
            type="text" 
            placeholder="请输入分享号"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password"
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            required
          />
        </div>
        
        <button type="submit" class="download-btn" :disabled="loading">
          <span v-if="loading">正在验证...</span>
          <span v-else>下载文件</span>
        </button>
        
        <div v-if="message" class="message" :class="messageType">
          {{ message }}
        </div>
      </form>
    </main>
    
    <footer class="disk-footer">
      <p>© 2024 在线网盘系统</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { downloadDiskFile } from '../api/disk'

const form = ref({
  share_id: '',
  password: ''
})

const loading = ref(false)
const message = ref('')
const messageType = ref('success')

const handleSubmit = async () => {
  loading.value = true
  message.value = ''
  
  try {
    const result = await downloadDiskFile(form.value.share_id, form.value.password)
    
    if (result.success) {
      messageType.value = 'success'
      message.value = '验证成功，开始下载...'
      
      // 创建一个隐藏的a标签来触发文件下载
      const link = document.createElement('a')
      link.href = result.downloadUrl
      link.download = result.fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else {
      messageType.value = 'error'
      message.value = result.message || '下载失败'
    }
  } catch (error) {
    messageType.value = 'error'
    message.value = error.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.disk-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.disk-header {
  text-align: center;
  margin-bottom: 30px;
}

.disk-header h1 {
  color: #333;
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.disk-header p {
  color: #666;
  font-size: 1.1rem;
}

.disk-form {
  background-color: #f9f9f9;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.download-btn {
  width: 100%;
  padding: 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #45a049;
}

.download-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.message {
  margin-top: 20px;
  padding: 12px;
  border-radius: 4px;
  text-align: center;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.disk-footer {
  text-align: center;
  margin-top: 40px;
  color: #666;
  font-size: 0.9rem;
}
</style>