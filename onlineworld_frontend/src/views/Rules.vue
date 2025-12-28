<template>
  <div class="max-w-5xl mx-auto bg-retro-bg min-h-screen font-song">
    <Header />
    <div class="p-4">
      <div class="bg-retro-postBg border border-retro-border p-6 mt-4">
        <h1 class="text-2xl font-bold text-retro-header mb-6 border-b border-retro-border pb-3">复古论坛版规（2025年修订）</h1>
        
        <div class="text-retro-text space-y-4 text-line-height">
          <p class="text-red-600 font-bold">重要提示：以下版规适用于所有用户，违反将根据情节轻重给予警告、删帖、封号处理，望大家遵守！</p>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">第一章 总则</h2>
          <p>1. 本论坛旨在提供健康、文明的交流平台，所有用户需遵守《中华人民共和国网络安全法》《互联网信息服务管理办法》等相关法律法规；</p>
          <p>2. 用户注册/访问论坛即表示同意本版规，论坛管理员拥有最终解释权。</p>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">第二章 禁止发布的内容</h2>
          <ul class="list-disc pl-8 space-y-2">
            <li>政治敏感、色情、暴力、恐怖、迷信等违法违规内容；</li>
            <li>恶意攻击、辱骂、诽谤他人，侵犯他人隐私（如手机号、住址、照片等）；</li>
            <li>广告、推广、刷屏、灌水（无意义重复内容）、外链引流等无关内容；</li>
            <li>破解软件、盗版资源、翻墙工具等侵权或违规资源；</li>
            <li>伪造官方信息、散布谣言、误导他人的内容。</li>
          </ul>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">第三章 发帖/回帖规范</h2>
          <p>1. 帖子需发布到对应板块，禁止跨板块发帖、重复发帖；</p>
          <p>2. 标题需准确概括内容，禁止使用夸张、误导性标题；</p>
          <p>3. 回帖需与帖子主题相关，禁止无意义回复（如“顶”“沙发”“路过”等纯灌水内容）；</p>
          <p>4. 禁止使用侮辱性、攻击性昵称或签名档。</p>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">第四章 处罚规则</h2>
          <p>1. 首次违规：警告+删帖；</p>
          <p>2. 二次违规：7天封号；</p>
          <p>3. 三次及以上违规：永久封号；</p>
          <p>4. 严重违规（如发布违法内容、恶意攻击管理员）：永久封号+上报相关部门。</p>
          
          <h2 class="text-xl font-bold text-retro-header mt-6">第五章 申诉渠道</h2>
          <p>如对处罚有异议，可通过「联系我们」发送申诉邮件，需提供用户名、违规内容链接、申诉理由，管理员将在3个工作日内回复。</p>
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