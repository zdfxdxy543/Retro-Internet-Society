<template>
  <div class="search-result-container">
    <div class="search-header">
      <h1 class="search-title">NexusSearch</h1>
      <div class="search-form-container">
        <form class="search-form" @submit.prevent="handleSearch">
          <input
            v-model="keyword"
            type="text"
            class="search-input"
            placeholder="输入关键词进行搜索..."
          />
          <button type="submit" class="search-button">搜索</button>
        </form>
      </div>
    </div>
    
    <div class="search-result-content">
      <div class="search-stats">
        <p v-if="results.length > 0">找到 {{ results.length }} 条相关结果</p>
        <p v-else>没有找到相关结果</p>
      </div>
      
      <div class="search-results">
        <div
          v-for="result in results"
          :key="result.id"
          class="search-result-item"
        >
          <h3 class="result-title">
            <a :href="result.url" target="_blank">{{ result.title }}</a>
          </h3>
          <div class="result-meta">
            <span class="result-type">{{ getResultTypeLabel(result.type) }}</span>
            <span class="result-url">{{ result.url }}</span>
            <span class="result-time">{{ formatDate(result.update_time) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import request from '../api/request'

const router = useRouter()
const route = useRoute()
const keyword = ref('')
const results = ref([])
const loading = ref(false)

// 从路由参数中获取关键词
onMounted(() => {
  const queryKeyword = route.query.keyword
  if (queryKeyword) {
    keyword.value = queryKeyword
    fetchSearchResults(queryKeyword)
  }
})

// 搜索结果类型标签映射
const resultTypeLabels = {
  forum_board: '论坛板块',
  forum_post: '论坛帖子',
  shop_product: '商城商品',
  dynamic_page: '动态页面'
}

// 获取结果类型标签
const getResultTypeLabel = (type) => {
  return resultTypeLabels[type] || '未知类型'
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 搜索处理函数
const handleSearch = () => {
  if (keyword.value.trim()) {
    router.push({
      path: '/search-engine/search',
      query: { keyword: keyword.value.trim() }
    })
    fetchSearchResults(keyword.value.trim())
  }
}

// 获取搜索结果
const fetchSearchResults = async (searchKeyword) => {
  loading.value = true
  try {
    const response = await request.get(`/api/search-engine?keyword=${encodeURIComponent(searchKeyword)}`)
    results.value = response.data.results || []
  } catch (error) {
    console.error('搜索失败:', error)
    results.value = []
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-result-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.search-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px 0;
}

.search-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: bold;
  letter-spacing: -2px;
}

.search-form-container {
  display: flex;
  justify-content: center;
  max-width: 600px;
  margin: 0 auto;
}

.search-form {
  display: flex;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 15px 20px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-right: none;
  border-radius: 25px 0 0 25px;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #3498db;
}

.search-button {
  padding: 15px 30px;
  font-size: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 0 25px 25px 0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #2980b9;
}

.search-result-content {
  max-width: 800px;
  margin: 0 auto;
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-stats {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-result-item {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-title {
  font-size: 1.2rem;
  margin-bottom: 5px;
}

.result-title a {
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.3s ease;
}

.result-title a:hover {
  color: #3498db;
  text-decoration: underline;
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.result-type {
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
}

.result-url {
  color: #27ae60;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-time {
  color: #95a5a6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-title {
    font-size: 2rem;
  }
  
  .search-form {
    flex-direction: column;
  }
  
  .search-input {
    border-radius: 25px 25px 0 0;
    border-right: 2px solid #ddd;
  }
  
  .search-button {
    border-radius: 0 0 25px 25px;
    margin-top: -2px;
  }
  
  .search-result-content {
    padding: 20px;
  }
}
</style>