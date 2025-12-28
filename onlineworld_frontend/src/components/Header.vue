<template>
  <div class="bg-retro-header text-white py-3 px-4">
    <div class="max-w-5xl mx-auto flex justify-between items-center">
      <!-- 左侧导航 -->
      <div>
        <h1 class="text-2xl font-bold mb-2">复古论坛</h1>
        <div class="flex space-x-6 text-sm">
          <a href="/" class="hover:underline">首页</a>
          <a href="/newbie" class="hover:underline">新人指南</a>
          <a href="/rules" class="hover:underline">版规说明</a>
          <a href="/contact" class="hover:underline">联系我们</a>
        </div>
      </div>

      <!-- 右侧搜索区域（新增） -->
      <div class="flex items-center space-x-2 mt-2">
        <select v-model="searchType" class="bg-retro-postBg text-retro-text border border-gray-500 px-2 py-1 text-sm rounded">
          <option value="post">搜索帖子</option>
          <option value="user">搜索用户</option>
        </select>
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="输入关键词搜索..."
          class="bg-retro-postBg text-retro-text border border-gray-500 px-3 py-1 text-sm rounded w-48 focus:outline-none focus:border-blue-500"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="bg-blue-700 hover:bg-blue-800 text-white px-3 py-1 text-sm rounded">
          搜索
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchType = ref('post')  // 默认搜索帖子
const searchKeyword = ref('')  // 搜索关键词

// 处理搜索逻辑
const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    alert('请输入搜索关键词！')
    return
  }
  // 跳转到搜索结果页面，携带参数：关键词+搜索类型
  router.push({
    path: '/search',
    query: {
      keyword: keyword,
      type: searchType.value
    }
  })
  // 清空输入框（可选）
  searchKeyword.value = ''
}
</script>

<style scoped>
a {
  color: white;
  text-decoration: none;
}
/* 适配小屏幕（可选） */
/* @media (max-width: 768px) {
  .max-w-5xl {
    flex-direction: column;
    align-items: flex-start;
  }
  .flex.items-center.space-x-2 {
    margin-top: 1rem;
    width: 100%;
  }
  input.w-48 {
    flex: 1;
  }
} */
</style>