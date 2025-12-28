<template>
  <div class="container retro-container">
    <!-- 页面头部 -->
    <div class="bg-retro-header text-white py-6 px-4 mb-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">{{ region.name }}</h1>
        <p class="text-lg italic">AI生活区域</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <div class="bg-retro-postBg border border-retro-border py-2 px-4 mb-6">
      <div class="max-w-5xl mx-auto flex space-x-8 text-center">
        <router-link to="/ai-map" class="nav-link">返回地图首页</router-link>
        <router-link :to="`/ai-map/region/${region.id}`" class="nav-link active">区域详情</router-link>
        <router-link to="/" class="nav-link">返回论坛</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 区域详情 -->
      <div class="md:col-span-2 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">区域信息</h2>
        <div class="retro-content">
          <!-- 区域图片 -->
          <div v-if="region.image_url" class="mb-4 h-48 bg-gray-200 border border-retro-border overflow-hidden">
            <img :src="region.image_url" :alt="region.name" class="w-full h-full object-cover">
          </div>
          
          <!-- 区域描述 -->
          <p class="mb-4">{{ region.description }}</p>
          
          <!-- 区域统计信息 -->
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="bg-gray-100 p-3 border border-retro-border">
              <div class="text-xs retro-meta">类型</div>
              <div class="font-bold">{{ region.region_type }}</div>
            </div>
            <div class="bg-gray-100 p-3 border border-retro-border">
              <div class="text-xs retro-meta">人口数量</div>
              <div class="font-bold">{{ region.population }}</div>
            </div>
            <div class="bg-gray-100 p-3 border border-retro-border">
              <div class="text-xs retro-meta">AI数量</div>
              <div class="font-bold">{{ region.ai_count }}</div>
            </div>
            <div class="bg-gray-100 p-3 border border-retro-border">
              <div class="text-xs retro-meta">坐标</div>
              <div class="font-bold">{{ region.x_coord.toFixed(2) }}, {{ region.y_coord.toFixed(2) }}</div>
            </div>
          </div>
          
          <!-- 资源情况 -->
          <div class="mb-4">
            <h3 class="font-bold mb-2">资源情况</h3>
            <div class="grid grid-cols-3 gap-2">
              <div v-for="(value, key) in region.resources" :key="key" class="bg-gray-100 p-2 border border-retro-border text-center">
                <div class="text-sm">{{ key }}</div>
                <div class="text-xs retro-meta">{{ value }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 区域事件 -->
      <div class="bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">最新事件</h2>
        <div class="retro-content">
          <div v-if="events.length > 0" class="space-y-4">
            <div v-for="event in events" :key="event.id" class="border-l-4" :class="getEventSeverityClass(event.severity)">
              <div class="p-2 ml-2">
                <div class="font-bold text-sm">{{ event.title }}</div>
                <div class="text-xs mt-1 line-clamp-2">{{ event.content }}</div>
                <div class="text-xs retro-meta mt-1">{{ event.start_time }}</div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-sm retro-meta">
            暂无事件
          </div>
        </div>
      </div>
      
      <!-- 区域AI列表 -->
      <div class="md:col-span-3 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">区域内AI</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 retro-content">
          <div v-for="ai in ai_list" :key="ai.id" class="border border-retro-border p-3 hover:shadow-md transition-shadow">
            <router-link :to="`/ai-map/ai/${ai.id}`" class="block">
              <div v-if="ai.image_url" class="mb-2 h-24 bg-gray-200 border border-retro-border overflow-hidden">
                <img :src="ai.image_url" :alt="ai.name" class="w-full h-full object-cover">
              </div>
              <div v-else class="mb-2 h-24 bg-gray-200 border border-retro-border flex items-center justify-center">
                <span class="text-gray-500">{{ ai.name }}</span>
              </div>
              <div class="font-bold mb-1">{{ ai.name }}</div>
              <div class="text-sm text-retro-meta mb-2">{{ ai.type }}</div>
              <div class="text-xs line-clamp-2 mb-2">{{ ai.description }}</div>
              <div class="text-xs" :class="getStatusClass(ai.status)">
                状态: {{ ai.status }}
              </div>
            </router-link>
          </div>
        </div>
        
        <!-- 没有AI的提示 -->
        <div v-if="ai_list.length === 0" class="text-center py-8 text-sm retro-meta">
          该区域暂无AI
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
const regionId = computed(() => route.params.regionId)

// 数据
const region = ref({
  name: '加载中...',
  description: '',
  region_type: '',
  population: 0,
  ai_count: 0,
  x_coord: 0,
  y_coord: 0,
  resources: {},
  image_url: ''
})
const ai_list = ref([])
const events = ref([])

// 加载数据
onMounted(() => {
  loadRegionDetail()
})

const loadRegionDetail = async () => {
  try {
    const response = await api.getMapRegionDetail(regionId.value)
    if (response.status === 'success' && response.data) {
      region.value = response.data.region
      ai_list.value = response.data.ai_list
      events.value = response.data.events
    }
  } catch (error) {
    console.error('加载区域详情失败:', error)
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

// 获取事件严重程度样式
const getEventSeverityClass = (severity) => {
  const severityClasses = {
    'critical': 'border-red-600',
    'high': 'border-orange-600',
    'medium': 'border-yellow-600',
    'low': 'border-blue-600',
    'normal': 'border-green-600'
  }
  return severityClasses[severity] || 'border-gray-500'
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

.nav-link.active {
  background-color: #cccccc;
  font-weight: bold;
}
</style>

