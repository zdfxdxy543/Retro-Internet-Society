<template>
  <div class="container retro-container">
    <!-- 公司网站头部 -->
    <div class="bg-retro-header text-white py-6 px-4 mb-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">未来科技有限公司</h1>
        <p class="text-lg italic">科技创造未来，创新引领时代</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <div class="bg-retro-postBg border border-retro-border py-2 px-4 mb-6">
      <div class="max-w-5xl mx-auto flex space-x-8 text-center">
        <router-link to="/company" class="nav-link">首页</router-link>
        <router-link to="/company/products" class="nav-link">产品中心</router-link>
        <router-link to="/company/about" class="nav-link">关于我们</router-link>
        <router-link to="/company/contact" class="nav-link active">联系我们</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 左侧：联系表单 -->
      <div class="bg-retro-postBg border border-retro-border p-6">
        <h2 class="text-2xl font-bold mb-6 retro-title">联系我们</h2>
        <div class="retro-content">
          <form @submit.prevent="handleSubmit">
            <div class="mb-4">
              <label for="name" class="block mb-1 font-bold">姓名</label>
              <input 
                type="text" 
                id="name" 
                v-model="formData.name"
                class="w-full p-2 border border-retro-border bg-white"
                required
              >
            </div>
            
            <div class="mb-4">
              <label for="email" class="block mb-1 font-bold">邮箱</label>
              <input 
                type="email" 
                id="email" 
                v-model="formData.email"
                class="w-full p-2 border border-retro-border bg-white"
                required
              >
            </div>
            
            <div class="mb-4">
              <label for="phone" class="block mb-1 font-bold">电话</label>
              <input 
                type="tel" 
                id="phone" 
                v-model="formData.phone"
                class="w-full p-2 border border-retro-border bg-white"
                required
              >
            </div>
            
            <div class="mb-4">
              <label for="subject" class="block mb-1 font-bold">主题</label>
              <input 
                type="text" 
                id="subject" 
                v-model="formData.subject"
                class="w-full p-2 border border-retro-border bg-white"
                required
              >
            </div>
            
            <div class="mb-6">
              <label for="message" class="block mb-1 font-bold">留言内容</label>
              <textarea 
                id="message" 
                v-model="formData.message"
                rows="5"
                class="w-full p-2 border border-retro-border bg-white"
                required
              ></textarea>
            </div>
            
            <button 
              type="submit" 
              class="bg-blue-700 hover:bg-blue-800 text-white py-2 px-6 rounded transition-colors"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '发送中...' : '发送留言' }}
            </button>
          </form>
          
          <div v-if="submitSuccess" class="mt-6 p-4 bg-green-100 border border-green-500 text-green-800 rounded">
            <p>留言发送成功！我们将尽快与您联系。</p>
          </div>
        </div>
      </div>
      
      <!-- 右侧：联系方式 -->
      <div class="bg-retro-postBg border border-retro-border p-6">
        <h2 class="text-2xl font-bold mb-6 retro-title">联系方式</h2>
        
        <div class="mb-8 retro-content">
          <div class="contact-item mb-4">
            <div class="font-bold">公司名称</div>
            <div>{{ companyInfo.name }}</div>
          </div>
          
          <div class="contact-item mb-4">
            <div class="font-bold">地址</div>
            <div>{{ companyInfo.address }}</div>
          </div>
          
          <div class="contact-item mb-4">
            <div class="font-bold">电话</div>
            <div>{{ companyInfo.phone }}</div>
          </div>
          
          <div class="contact-item mb-4">
            <div class="font-bold">邮箱</div>
            <div>{{ companyInfo.email }}</div>
          </div>
          
          <div class="contact-item mb-4">
            <div class="font-bold">网站</div>
            <div>{{ companyInfo.website }}</div>
          </div>
        </div>
        
        <div class="retro-content">
          <h3 class="font-bold mb-3 text-lg">营业时间</h3>
          <div class="mb-2">周一至周五：9:00 - 18:00</div>
          <div class="mb-2">周六：10:00 - 16:00</div>
          <div>周日：休息</div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import companyApi from '../api/company.js'
import Footer from '../components/Footer.vue'

// 表单数据
const formData = ref({
  name: '',
  email: '',
  phone: '',
  subject: '',
  message: ''
})

// 状态
const isSubmitting = ref(false)
const submitSuccess = ref(false)

// 公司信息
const companyInfo = ref({
  name: '未来科技有限公司',
  address: '北京市海淀区中关村科技园区',
  phone: '010-12345678',
  email: 'contact@futuretech.com',
  website: 'www.futuretech.com'
})

// 加载公司信息
onMounted(() => {
  loadCompanyInfo()
})

const loadCompanyInfo = async () => {
  try {
    const response = await companyApi.getContact()
    if (response.status === 'success' && response.data) {
      companyInfo.value = response.data.company
    }
  } catch (error) {
    console.error('加载联系信息失败:', error)
  }
}

// 处理表单提交
const handleSubmit = async () => {
  isSubmitting.value = true
  
  // 模拟表单提交
  setTimeout(() => {
    isSubmitting.value = false
    submitSuccess.value = true
    
    // 重置表单
    formData.value = {
      name: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    }
    
    // 5秒后隐藏成功消息
    setTimeout(() => {
      submitSuccess.value = false
    }, 5000)
  }, 1000)
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.retro-container {
  background-color: #f0f0f0;
  color: #333333;
  font-family: SimSun, STSong, serif;
}

.retro-title {
  color: #333333;
  border-bottom: 2px solid #666666;
  padding-bottom: 4px;
  margin-bottom: 12px;
}

.retro-content {
  line-height: 1.8;
  font-size: 14px;
}

.nav-link {
  color: #333333;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #e0e0e0;
}

.nav-link.active {
  background-color: #cccccc;
  font-weight: bold;
}

.contact-item {
  padding: 8px 0;
  border-bottom: 1px dashed #666666;
}

input, textarea {
  font-family: SimSun, STSong, serif;
  font-size: 14px;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #666666;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}
</style>