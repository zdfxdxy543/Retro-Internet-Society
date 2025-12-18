<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-4 mt-4">
        <!-- 帖子头部导航 -->
        <div class="text-sm mb-4">
          <a href="/" class="text-retro-link hover:underline">首页</a>
          →
          <a :href="`/board/${post.board_id}`" class="text-retro-link hover:underline">
            {{ post.board_name }}
          </a>
          →
          <span class="text-retro-text">{{ post.title }}</span>
        </div>

        <!-- 帖子正文 -->
        <div class="border-b-2 border-retro-border pb-4 mb-4">
          <h1 class="text-2xl font-bold text-retro-header mb-3">{{ post.title }}</h1>
          <div class="flex justify-between items-center text-sm mb-3">
            <span class="font-bold text-retro-header">作者：<a :href="`/user/${post.author}`">{{ post.author }}</a></span>
            <span class="text-gray-500">发布时间：{{ post.create_time }}</span>
            <span class="text-gray-500">浏览量：{{ post.view_count }}</span>
          </div>
          <div class="text-retro-text whitespace-pre-line p-4 bg-retro-replyBg text-line-height">
            {{ post.content }}
          </div>
          <!-- 源码注释线索（拟真：查看源码时可见） -->
          <!-- 注释内容：<!-- 线索1：服务器门禁编号8A3F是解锁关键 --> -->
        </div>

        <!-- 回帖列表 -->
        <div class="mt-6">
          <h2 class="text-xl font-bold text-retro-header mb-3">回帖列表（{{ replies.length }} 条）</h2>
          <div 
            v-for="(reply, index) in replies" 
            :key="reply.id"
            class="border-b border-retro-border pb-3 mb-4 big-retro-postBg p-4"
          >
            <div class="flex justify-between text-sm mb-2">
              <span class="font-bold text-retro-header">
                地板 {{ index + 1 }} · <a :href="`/user/${reply.author}`">{{ reply.author }}</a>
              </span>
              <span class=  text-gray-500>{{ reply.create_time }}</span>
            </div>
            <div class="text-retro-text whitespace-pre-line p-3 bg-retro-replyBg mb-2 text-line-height">
              {{ reply.content }}
            </div>
            <!-- 签名档（可藏线索） -->
            <div v-if="reply.signature" class="signature-style">
              签名：{{ reply.signature }}
            </div>
          </div>
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
const postId = route.params.postId
const post = ref({
  title: '',
  content: '',
  author: '',
  create_time: '',
  view_count: 0,
  board_name: ''
})
const replies = ref([])

// 页面加载时请求帖子+回帖数据
onMounted(async () => {
  await new Promise(resolve => setTimeout(resolve, 200))  // 模拟加载延迟
  const res = await request.get(`/post/${postId}`)
  if (res.status === 'success') {
    post.value = res.data.post
    replies.value = res.data.replies
    document.title = res.data.title  // 从后端获取标题
  }
})
</script>

<style scoped>
a {
  text-decoration: none;
}
.whitespace-pre-line {
  white-space: pre-line;  /* 保留换行符 */
}
</style>