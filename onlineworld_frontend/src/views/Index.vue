<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-4 mt-4">
        <h2 class="text-xl font-bold text-retro-header mb-4">论坛板块</h2>
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-retro-replyBg border-b border-retro-border">
              <th class="p-2 text-left">板块名称</th>
              <th class="p-2 text-left">板块描述</th>
              <th class="p-2 text-left">创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="board in boards" 
              :key="board.id"
              class="border-b border-retro-border hover:bg-retro-replyBg cursor-pointer"
              @click="goToBoard(board.id)"
            >
              <td class="p-3">
                <a :href="`/board/${board.id}`" class="text-retro-link hover:underline text-lg font-medium">
                  {{ board.name }}
                </a>
              </td>
              <td class="p-3 text-retro-text">{{ board.description }}</td>
              <td class="p-3 text-retro-text text-sm">{{ board.create_time }}</td>
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
import { useRouter } from 'vue-router'
import request from '../api/request'
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'

const router = useRouter()
const boards = ref([])

// 页面加载时请求板块数据
onMounted(async () => {
  // 模拟真实网页加载延迟（100ms）
  await new Promise(resolve => setTimeout(resolve, 100))
  const res = await request.get('/api/')
  if (res.status === 'success') {
    boards.value = res.data.boards
    document.title = res.data.title  // 从后端获取页面标题
  }
})

// 跳转到板块页面
const goToBoard = (boardId) => {
  router.push(`/board/${boardId}`)
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