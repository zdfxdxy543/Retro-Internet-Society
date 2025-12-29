<template>
  <div class="search-engine-container">
    <div class="search-engine-header">
      <h1 class="search-engine-title">NexusSearch</h1>
      <p class="search-engine-subtitle">连接互联网上的一切页面</p>
    </div>
    <div class="search-engine-body">
      <form class="search-form" @submit.prevent="handleSearch">
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="输入关键词进行搜索..."
          autofocus
        />
        <button type="submit" class="search-button">搜索</button>
      </form>
      <div class="search-stats">
        <p>NexusSearch 已索引超过 1000+ 个页面</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')

const handleSearch = () => {
  if (keyword.value.trim()) {
    router.push({
      path: '/search-engine/search',
      query: { keyword: keyword.value.trim() }
    })
  }
}
</script>

<style scoped>
.search-engine-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.search-engine-header {
  text-align: center;
  margin-bottom: 40px;
}

.search-engine-title {
  font-size: 3.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: bold;
  letter-spacing: -2px;
}

.search-engine-subtitle {
  color: #7f8c8d;
  font-size: 1.2rem;
}

.search-engine-body {
  width: 100%;
  max-width: 600px;
}

.search-form {
  display: flex;
  width: 100%;
  margin-bottom: 20px;
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

.search-stats {
  text-align: center;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-engine-title {
    font-size: 2.5rem;
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
}
</style>