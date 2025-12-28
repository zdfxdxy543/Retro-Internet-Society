<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-6 mt-4">
        <h1 class="text-2xl font-bold text-retro-header mb-6 border-b border-retro-border pb-3">联系我们</h1>
        
        <div class="text-retro-text space-y-6 text-line-height">
          <p>如果您在使用论坛过程中遇到问题、有建议或需要申诉，可通过以下方式联系我们：</p>
          
          <div class="pl-4 border-l-2 border-retro-border">
            <h2 class="text-xl font-bold text-retro-header">一、官方邮箱</h2>
            <p>投诉举报：<a href="#" class="text-retro-link hover:underline">reporttonoone@nottrue.com</a></p>
            <p>建议反馈：<a href="#" class="text-retro-link hover:underline">suggesttowho@nottrue.com</a></p>
            <p>申诉通道：<a href="#" class="text-retro-link hover:underline">appealiswrong@nottrue.com</a></p>
            <p class="text-gray-500 text-sm mt-2">邮件回复时间：1-3个工作日</p>
          </div>
          
          <div class="pl-4 border-l-2 border-retro-border">
            <h2 class="text-xl font-bold text-retro-header">二、注意事项</h2>
            <ul class="list-disc pl-8 space-y-2">
              <li>邮件主题请注明“投诉/建议/申诉+内容概要”，如“建议+新增搜索功能”；</li>
              <li>申诉需提供详细信息（用户名、违规链接、申诉理由），否则不予处理；</li>
              <li>禁止发送广告、垃圾邮件，否则将拉黑邮箱。</li>
            </ul>
          </div>
          
          <div class="pl-4 border-l-2 border-retro-border">
            <h2 class="text-xl font-bold text-retro-header">三、论坛信息</h2>
            <p>备案号：Having fun!</p>
            <p>运营主体：:)</p>
            <p>更新时间：2025年12月</p>
          </div>
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
.space-y-6 > * {
  margin-bottom: 1.5rem;
}
</style>