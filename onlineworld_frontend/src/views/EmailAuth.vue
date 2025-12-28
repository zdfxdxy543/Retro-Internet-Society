<template>
  <div class="email-auth-container">
    <div class="auth-form-wrapper">
      <h1 class="auth-title">{{ isLogin ? '登录邮箱系统' : '注册新账号' }}</h1>
      
      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" v-show="isLogin">
        <div class="form-group">
          <label for="login-username">用户名</label>
          <input 
            type="text" 
            id="login-username" 
            v-model="loginForm.username" 
            placeholder="请输入用户名" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="login-password">密码</label>
          <input 
            type="password" 
            id="login-password" 
            v-model="loginForm.password" 
            placeholder="请输入密码" 
            required
          />
        </div>
        
        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <p class="switch-form">
            还没有账号？<a href="#" @click.prevent="toggleForm">点击注册</a>
          </p>
        </div>
      </form>
      
      <!-- 注册表单 -->
      <form @submit.prevent="handleRegister" v-show="!isLogin">
        <div class="form-group">
          <label for="reg-username">用户名</label>
          <input 
            type="text" 
            id="reg-username" 
            v-model="registerForm.username" 
            placeholder="请输入用户名（3-20位字母数字下划线）" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="reg-email">邮箱</label>
          <input 
            type="email" 
            id="reg-email" 
            v-model="registerForm.email" 
            placeholder="请输入邮箱地址" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="reg-password">密码</label>
          <input 
            type="password" 
            id="reg-password" 
            v-model="registerForm.password" 
            placeholder="请输入密码（至少6位）" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="reg-confirm-password">确认密码</label>
          <input 
            type="password" 
            id="reg-confirm-password" 
            v-model="registerForm.confirmPassword" 
            placeholder="请再次输入密码" 
            required
          />
        </div>
        
        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
          <p class="switch-form">
            已有账号？<a href="#" @click.prevent="toggleForm">点击登录</a>
          </p>
        </div>
      </form>
      
      <!-- 错误提示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <!-- 成功提示 -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script>
// import axios from 'axios'
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import emailService from '../api/email.js'

export default {
  name: 'EmailAuth',
  setup() {
    // 状态管理
    const isLogin = ref(true)  // 默认显示登录表单
    const loading = ref(false) // 加载状态
    const errorMessage = ref('') // 错误消息
    const successMessage = ref('') // 成功消息
    const router = useRouter() // 路由实例
    
    // 登录表单数据
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    // 注册表单数据
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    // 清除消息
    const clearMessages = () => {
      errorMessage.value = ''
      successMessage.value = ''
    }
    
    // 切换表单（登录/注册）
    const toggleForm = () => {
      isLogin.value = !isLogin.value
      clearMessages() // 切换时清除消息
    }
    
    // 处理登录
    const handleLogin = async () => {
      clearMessages()
      loading.value = true
      
      try {
        // 调用登录API
        // const response = await axios.post('/email/login', {
        const response = await emailService.login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        if (response.data.success) {
          // 登录成功，存储用户信息并跳转到邮箱首页
          const userInfo = response.data.user
          localStorage.setItem('userInfo', JSON.stringify(userInfo))
          localStorage.setItem('isLoggedIn', 'true')
          
          successMessage.value = '登录成功，正在跳转...'
          
          // 延迟跳转 - 修复：直接跳转到dashboard而不是inbox，避免重定向问题
          setTimeout(() => {
            router.push('/email/dashboard')
          }, 1000)
        } else {
          // 登录失败
          errorMessage.value = response.data.message || '登录失败，请稍后重试'
        }
      } catch (error) {
        // 处理异常
        console.error('Login error:', error)
        if (error.response) {
          errorMessage.value = error.response.data.message || '登录失败，请检查用户名和密码'
        } else {
          errorMessage.value = '网络错误，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    // 处理注册
    const handleRegister = async () => {
      clearMessages()
      loading.value = true
      
      // 表单验证
      if (registerForm.password !== registerForm.confirmPassword) {
        errorMessage.value = '两次输入的密码不一致'
        loading.value = false
        return
      }
      
      if (registerForm.password.length < 6) {
        errorMessage.value = '密码长度至少为6位'
        loading.value = false
        return
      }
      
      // 用户名格式验证（只允许字母、数字、下划线，长度3-20）
      const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
      if (!usernameRegex.test(registerForm.username)) {
        errorMessage.value = '用户名格式不正确，只允许字母、数字、下划线，长度3-20'
        loading.value = false
        return
      }
      
      // 邮箱格式验证
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      if (!emailRegex.test(registerForm.email)) {
        errorMessage.value = '邮箱格式不正确'
        loading.value = false
        return
      }
      
      try {
        // 调用注册API
        // const response = await axios.post('/email/register', {
        const response = await emailService.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        })
        
        if (response.data.success) {
          // 注册成功
          successMessage.value = '注册成功，请登录'
          
          // 重置注册表单
          registerForm.username = ''
          registerForm.email = ''
          registerForm.password = ''
          registerForm.confirmPassword = ''
          
          // 自动切换到登录表单
          setTimeout(() => {
            toggleForm()
            clearMessages()
          }, 2000)
        } else {
          // 注册失败
          errorMessage.value = response.data.message || '注册失败，请稍后重试'
        }
      } catch (error) {
        // 处理异常
        console.error('Register error:', error)
        if (error.response) {
          errorMessage.value = error.response.data.message || '注册失败'
        } else {
          errorMessage.value = '网络错误，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    return {
      isLogin,
      loading,
      errorMessage,
      successMessage,
      loginForm,
      registerForm,
      toggleForm,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.email-auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px); /* 减去导航栏高度 */
  padding: 20px;
  background-color: #f5f7fa;
  background-image: 
    linear-gradient(30deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8),
    linear-gradient(150deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8),
    linear-gradient(30deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8),
    linear-gradient(150deg, #f0f4f8 12%, transparent 12.5%, transparent 87%, #f0f4f8 87.5%, #f0f4f8),
    linear-gradient(60deg, #f8fafc 25%, transparent 25.5%, transparent 75%, #f8fafc 75%, #f8fafc);
  background-size: 80px 140px;
  background-position: 0 0, 0 0, 40px 70px, 40px 70px, 0 0;
}

.auth-form-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.auth-title {
  text-align: center;
  color: #333;
  margin-bottom: 25px;
  font-size: 1.8rem;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #4a6bff;
  box-shadow: 0 0 0 2px rgba(74, 107, 255, 0.2);
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #4a6bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #3a5aef;
}

.submit-btn:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.form-actions {
  margin-top: 30px;
}

.switch-form {
  text-align: center;
  margin-top: 15px;
  color: #666;
}

.switch-form a {
  color: #4a6bff;
  text-decoration: none;
  cursor: pointer;
}

.switch-form a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #fff0f0;
  border: 1px solid #ffd6d6;
  border-radius: 4px;
  color: #d32f2f;
  font-size: 14px;
}

.success-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #f0fff0;
  border: 1px solid #d6ffd6;
  border-radius: 4px;
  color: #388e3c;
  font-size: 14px;
}

/* 响应式样式 */
@media (max-width: 500px) {
  .auth-form-wrapper {
    padding: 20px;
  }
  
  .auth-title {
    font-size: 1.5rem;
  }
}
</style>