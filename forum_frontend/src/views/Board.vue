<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-4 mt-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-retro-header">
            {{ board.name }} - {{ board.description }}
          </h2>
          <a href="/" class="text-retro-link hover:underline text-sm">返回首页</a>
        </div>
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-retro-replyBg border-b border-retro-border">
              <th class="p-2 text-left w-2/3">帖子标题</th>
              <th class="p-2 text-left w-1/6">作者</th>
              <th class="p-2 text-left w-1/6">发布时间</th>
              <th class="p-2 text-left">浏览/回复</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="post in posts" 
              :key="post.id"
              class="border-b border-retro-border hover:bg-retro-replyBg cursor-pointer"
              @click="goToPost(post.id)"
            >
              <td class="p-3">
                <a :href="`/post/${post.id}`" class="text-retro-link hover:underline">
                  {{ post.title }}
                </a>
              </td>
              <td class="p-3 text-retro-text"><a :href="`/user/${post.author}`">{{ post.author }}</a></td>
              <td class="p-3 text-retro-text text-sm">{{ post.create_time }}</td>
              <td class="p-3 text-retro-text text-sm">
                {{ post.view_count }} / {{ post.reply_count }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import request from '../api/request'
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'

const router = useRouter()
const route = useRoute()
const boardId = route.params.boardId
const board = ref({ name: '', description: '' })
const posts = ref([])

// 页面加载时请求帖子数据
onMounted(async () => {
  await new Promise(resolve => setTimeout(resolve, 150))  // 模拟加载延迟
  const res = await request.get(`/board/${boardId}`)
  if (res.status === 'success') {
    board.value = res.data.board
    posts.value = res.data.posts
    document.title = res.data.title  // 从后端获取标题
  }
})

// 跳转到帖子详情页
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}
</script>

<style scoped>
table {
  border: 1px solid #cccccc;
}
a {
  text-decoration: none;
}
</style>