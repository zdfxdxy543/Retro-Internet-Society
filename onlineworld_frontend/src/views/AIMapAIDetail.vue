<template>
  <div class="container retro-container">
    <!-- 页面头部 -->
    <div class="bg-retro-header text-white py-6 px-4 mb-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">{{ ai.name }}</h1>
        <p class="text-lg italic">{{ ai.type }}</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <div class="bg-retro-postBg border border-retro-border py-2 px-4 mb-6">
      <div class="max-w-5xl mx-auto flex space-x-8 text-center">
        <router-link to="/ai-map" class="nav-link">返回地图首页</router-link>
        <router-link :to="`/ai-map/region/${ai.region_id}`" class="nav-link">返回区域</router-link>
        <router-link to="/" class="nav-link">返回论坛</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- AI基本信息 -->
      <div class="md:col-span-2 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">AI信息</h2>
        <div class="retro-content">
          <!-- AI图片 -->
          <div v-if="ai.image_url" class="mb-4 h-64 bg-gray-200 border border-retro-border overflow-hidden">
            <img :src="ai.image_url" :alt="ai.name" class="w-full h-full object-cover">
          </div>
          <div v-else class="mb-4 h-64 bg-gray-200 border border-retro-border flex items-center justify-center">
            <span class="text-gray-500 text-2xl">{{ ai.name }}</span>
          </div>
          
          <!-- AI描述 -->
          <div class="mb-6">
            <p>{{ ai.description }}</p>
          </div>
          
          <!-- AI状态 -->
          <div class="mb-4 p-3 bg-gray-100 border border-retro-border">
            <div class="flex justify-between items-center">
              <div class="font-bold">状态:</div>
              <div class="text-sm" :class="getStatusClass(ai.status)">
                {{ ai.status }}
              </div>
            </div>
          </div>
          
          <!-- AI能力 -->
          <div class="mb-4">
            <h3 class="font-bold mb-2">能力:</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div v-for="(value, key) in ai.capabilities" :key="key" class="p-2 bg-gray-100 border border-retro-border">
                <div class="font-bold text-xs">{{ key }}:</div>
                <div class="text-xs">{{ value }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- AI所属区域信息 -->
      <div class="bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">所属区域</h2>
        <div class="retro-content">
          <div class="font-bold mb-2">{{ ai.region.name }}</div>
          <p class="mb-4">{{ ai.region.description }}</p>
          <router-link :to="`/ai-map/region/${ai.region.id}`" class="inline-block px-4 py-2 bg-gray-200 border border-retro-border hover:bg-gray-300 transition-colors">
            查看区域
          </router-link>
        </div>
      </div>
      
      <!-- AI历史活动 -->
      <div class="md:col-span-3 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">AI活动历史</h2>
        <div class="retro-content">
          <div class="text-center py-8 text-sm retro-meta">
            暂无活动历史记录
          </div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <footer class="mt-12 py-6 px-4 bg-retro-footer text-center text-sm retro-meta">
      <div class="max-w-5xl mx-auto">
        <p>AI生活区域地图 © 2024</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/ai_map.js'

const route = useRoute()
const aiId = computed(() => route.params.aiId)

// 数据
const ai = ref({
  name: '',
  type: '',
  status: '',
  description: '',
  capabilities: {},
  image_url: '',
  region: {
    id: '',
    name: '',
    description: ''
  },
  region_id: ''
})

// 加载数据
onMounted(() => {
  loadAIDetail()
})

const loadAIDetail = async () => {
  try {
    const response = await api.getAIDetail(aiId.value)
    if (response.status === 'success' && response.data) {
      ai.value = response.data.ai
    }
  } catch (error) {
    console.error('加载AI详情失败:', error)
  }
}

// 获取AI状态样式
const getStatusClass = (status) => {
  const statusClasses = {
    'active': 'text-green-600',
    'inactive': 'text-gray-500',
    'maintenance': 'text-yellow-600',
    'error': 'text-red-600'
  }
  return statusClasses[status] || 'text-gray-500'
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

.retro-meta {
  color: #666666;
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
</style>

