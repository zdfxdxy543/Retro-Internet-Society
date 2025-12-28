<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-6 mt-4">
        <!-- 动态页面标题 -->
        <h1 class="text-2xl font-bold text-retro-header mb-6 border-b border-retro-border pb-3">
          {{ dynamicPage.title }}
        </h1>
        
        <!-- 渲染大模型生成的内容（支持HTML/Markdown） -->
        <div v-if="dynamicPage.content_type === 'html'" 
             class="text-retro-text text-line-height"
             v-html="dynamicPage.content">
        </div>
        
        <div v-else-if="dynamicPage.content_type === 'markdown'" 
             class="text-retro-text text-line-height">
          <!-- 若内容是Markdown，需引入Markdown渲染库（如marked） -->
          <div v-html="renderMarkdown(dynamicPage.content)"></div>
        </div>
        
        <!-- 生成时间 -->
        <div class="mt-6 text-gray-500 text-sm">
          生成时间：{{ dynamicPage.create_time }}
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
// // 若需要支持Markdown，安装marked：npm install marked，然后导入
// import { marked } from 'marked'

const route = useRoute()
const slug = route.params.slug  // 从路由获取slug
const dynamicPage = ref(null)

// Markdown渲染函数（可选）
const renderMarkdown = (content) => {
  return marked.parse(content)
}

// 加载动态页面数据
onMounted(async () => {
  await new Promise(resolve => setTimeout(resolve, 200))
  const res = await request.get(`/page/${slug}`)  // 调用通用动态路由
  if (res.status === 'success') {
    dynamicPage.value = res.data.dynamic_page
    document.title = res.data.title
  }
})
</script>

<style scoped>
a {
  text-decoration: none;
}
/* 适配大模型生成的HTML样式，保持复古风格 */
.v-html p {
  margin-bottom: 1rem;
}
.v-html h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #0066cc;
  margin: 1.5rem 0 0.5rem;
}
.v-html ul {
  list-style: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}
</style>