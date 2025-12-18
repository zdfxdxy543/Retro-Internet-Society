<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-6 mt-4">
        <h1 class="text-2xl font-bold text-retro-header mb-6 border-b border-retro-border pb-3">新人指南 - 复古论坛使用须知</h1>
        
        <div class="text-retro-text space-y-4 text-line-height">
          <p>欢迎加入复古论坛！本论坛成立于2010年，是专注于技术交流、生活分享的综合性社区，为了让您快速上手，特整理以下指南：</p>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">一、论坛基本操作</h2>
          <ul class="list-disc pl-8 space-y-2">
            <li>浏览板块：首页展示所有板块，点击板块名称进入对应帖子列表；</li>
            <li>查看帖子：点击帖子标题进入详情页，可查看正文、回帖及签名档；</li>
            <li>搜索功能：暂不支持全局搜索，需手动浏览板块查找内容；</li>
            <li>查看源码：部分帖子线索可能藏在页面源码中（按F12打开开发者工具→Elements）。</li>
          </ul>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">二、发帖/回帖规则（当前仅浏览，后续开放）</h2>
          <ul class="list-disc pl-8 space-y-2">
            <li>注册用户可在对应板块发帖，匿名用户仅支持浏览；</li>
            <li>帖子标题需简洁明了，正文内容需与板块主题相关；</li>
            <li>回帖需文明用语，禁止灌水、刷屏、广告等无关内容。</li>
          </ul>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">三、社区氛围</h2>
          <p>本论坛倡导「互助、文明、复古」的交流氛围，禁止发布敏感内容、恶意攻击、侵犯隐私等违规信息，违规将被封号处理。</p>
          
          <p class="mt-8 text-gray-500 text-sm">最后，祝您在论坛交流愉快！如有疑问，可通过「联系我们」反馈～</p>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'
</script>

<style scoped>
a {
  text-decoration: none;
}
.space-y-4 > * {
  margin-bottom: 1rem;
}
</style>