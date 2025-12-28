<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-6 mt-4">
        <!-- 个人信息头部 -->
        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold text-retro-header mb-2">
            {{ userInfo.author }} 的个人主页
          </h1>
          <div class="text-retro-text flex justify-center space-x-6">
            <span>发帖数：{{ userInfo.post_count }}</span>
            <span>回帖数：{{ userInfo.reply_count }}</span>
          </div>
        </div>

        <!-- 发布的帖子 -->
        <div class="mt-8">
          <h2 class="text-xl font-bold text-retro-header border-b border-retro-border pb-2">
            发布的帖子
          </h2>
          <div v-if="posts.length > 0" class="mt-4 space-y-3">
            <div v-for="post in posts" :key="post.id" class="p-3 border-b border-gray-200">
              <a :href="`/post/${post.id}`" class="text-retro-link hover:underline text-lg">
                {{ post.title }}
              </a>
              <div class="text-sm text-gray-500 mt-1">
                板块：<a :href="`/board/${post.board_id}`" class="hover:underline">{{ post.board_name }}</a>
                · 发布时间：{{ post.create_time }}
                · 浏览：{{ post.view_count }} · 回复：{{ post.reply_count }}
              </div>
            </div>
          </div>
          <div v-else class="mt-4 text-gray-500">暂无发布的帖子</div>
        </div>

        <!-- 回复的帖子 -->
        <div class="mt-8">
          <h2 class="text-xl font-bold text-retro-header border-b border-retro-border pb-2">
            回复的帖子
          </h2>
          <div v-if="replies.length > 0" class="mt-4 space-y-3">
            <div v-for="reply in replies" :key="reply.id" class="p-3 border-b border-gray-200">
              <div class="mb-1">
                回复了：<a :href="`/post/${reply.post_id}`" class="text-retro-link hover:underline">
                  {{ reply.post_title }}
                </a>
              </div>
              <div class="text-retro-text text-sm">
                {{ reply.content }}
              </div>
              <div v-if="reply.signature" class="text-sm text-gray-500 mt-1 italic">
                签名：{{ reply.signature }}
              </div>
              <div class="text-sm text-gray-500 mt-1">
                回复时间：{{ reply.create_time }}
              </div>
            </div>
          </div>
          <div v-else class="mt-4 text-gray-500">暂无回复的帖子</div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '../api/request'
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'

const route = useRoute()
const author = route.params.author  // 从路由获取用户名
const userInfo = ref({ author: '', post_count: 0, reply_count: 0 })
const posts = ref([])
const replies = ref([])

// 加载个人页面数据
onMounted(async () => {
  await new Promise(resolve => setTimeout(resolve, 200))
  try {
    const res = await request.get(`/api/user/${author}`)
    if (res.status === 'success') {
      userInfo.value = res.data.user_info
      posts.value = res.data.posts
      replies.value = res.data.replies
      document.title = res.data.title
    }
  } catch (error) {
    console.error('加载个人页面失败：', error)
  }
})
</script>

<style scoped>
a {
  text-decoration: none;
}
.space-y-3 > * {
  margin-bottom: 0.75rem;
}
</style>