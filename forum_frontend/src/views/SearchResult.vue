<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-6 mt-4">
        <!-- 搜索条件提示 -->
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-retro-header mb-2">
            搜索结果
          </h1>
          <p class="text-retro-text">
            关键词：<span class="text-red-600 font-bold">{{ keyword }}</span>
            · 搜索类型：<span class="text-blue-600 font-bold">{{ searchType === 'post' ? '帖子' : '用户' }}</span>
            · 找到 {{ totalCount }} 条结果
          </p>
        </div>

        <!-- 搜索结果列表 -->
        <div class="space-y-4">
          <!-- 帖子搜索结果 -->
          <div v-if="searchType === 'post'">
            <div v-if="results.length > 0" class="space-y-3">
              <div v-for="post in results" :key="post.id" class="p-4 border border-gray-200 rounded hover:bg-gray-50 transition-colors">
                <a :href="`/post/${post.id}`" class="text-retro-link hover:underline text-lg font-medium">
                  {{ post.title }}
                </a>
                <div class="text-sm text-gray-500 mt-1">
                  作者：<a :href="`/user/${post.author}`" class="hover:underline">{{ post.author }}</a>
                  · 板块：<a :href="`/board/${post.board_id}`" class="hover:underline">{{ post.board_name }}</a>
                  · 发布时间：{{ post.create_time }}
                  · 浏览：{{ post.view_count }} · 回复：{{ post.reply_count }}
                </div>
                <div class="text-retro-text text-sm mt-2 line-clamp-2">
                  {{ post.content }}
                </div>
              </div>
            </div>
            <div v-else class="text-gray-500 text-center py-8">
              未找到相关帖子，请更换关键词重试～
            </div>
          </div>

          <!-- 用户搜索结果 -->
          <div v-else-if="searchType === 'user'">
            <div v-if="results.length > 0" class="space-y-3">
              <div v-for="user in results" :key="user.author" class="p-4 border border-gray-200 rounded hover:bg-gray-50 transition-colors">
                <a :href="`/user/${user.author}`" class="text-retro-link hover:underline text-lg font-medium">
                  {{ user.author }}
                </a>
                <div class="text-sm text-gray-500 mt-1">
                  发帖数：{{ user.post_count }} · 回帖数：{{ user.reply_count }}
                </div>
                <div class="mt-2">
                  <button :href="`/user/${user.author}`" class="bg-blue-700 hover:bg-blue-800 text-white px-3 py-1 text-sm rounded">
                    访问个人主页
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="text-gray-500 text-center py-8">
              未找到相关用户，请更换关键词重试～
            </div>
          </div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import request from '../api/request'
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'

const route = useRoute()
const keyword = ref(route.query.keyword || '')
const searchType = ref(route.query.type || 'post')
const results = ref([])  // 搜索结果列表
const totalCount = computed(() => results.value.length)  // 结果总数

// 1. 提取搜索逻辑为独立函数（方便重复调用）
const fetchSearchResults = async () => {
  const currentKeyword = route.query.keyword || ''
  const currentType = route.query.type || 'post'
  
  // 更新组件内的关键词和类型（同步路由参数）
  keyword.value = currentKeyword
  searchType.value = currentType

  if (!currentKeyword) {
    results.value = []
    return
  }

  try {
    const res = await request.get('/api/search', {
      params: {
        keyword: currentKeyword,
        type: currentType
      }
    })
    if (res.status === 'success') {
      results.value = res.data.results
      document.title = `搜索结果 - ${currentKeyword} - 复古论坛`
    }
  } catch (error) {
    console.error('搜索失败：', error)
    results.value = []
  }
}

// 2. 首次加载时执行搜索
onMounted(() => {
  fetchSearchResults()
})

// 3. 监听路由参数变化（关键词/类型改变时，重新搜索）
watch(
  () => route.query,  // 监听路由查询参数对象
  () => {
    fetchSearchResults()  // 参数变化时重新调用搜索
  },
  { deep: true }  // 深度监听（对象内部属性变化也触发）
)
</script>

<style scoped>
a {
  text-decoration: none;
}
.space-y-3 > * {
  margin-bottom: 0.75rem;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.transition-colors {
  transition: background-color 0.2s ease;
}
</style>