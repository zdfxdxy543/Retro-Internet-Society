<template>
  <div class="container retro-container">
    <!-- 公司网站头部 -->
    <div class="bg-retro-header text-white py-6 px-4 mb-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">未来科技有限公司</h1>
        <p class="text-lg italic">科技创造未来，创新引领时代</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <div class="bg-retro-postBg border border-retro-border py-2 px-4 mb-6">
      <div class="max-w-5xl mx-auto flex space-x-8 text-center">
        <router-link to="/company" class="nav-link">首页</router-link>
        <router-link to="/company/products" class="nav-link">产品中心</router-link>
        <router-link to="/company/about" class="nav-link active">关于我们</router-link>
        <router-link to="/company/contact" class="nav-link">联系我们</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto bg-retro-postBg border border-retro-border p-6">
      <h2 class="text-2xl font-bold mb-6 retro-title">关于我们</h2>
      
      <div class="mb-8 retro-content">
        <h3 class="font-bold mb-3 text-lg">公司简介</h3>
        <p>{{ companyInfo.description }}</p>
      </div>
      
      <div class="mb-8 retro-content">
        <h3 class="font-bold mb-3 text-lg">公司历史</h3>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-year">2005年</div>
            <div class="timeline-content">
              <p>未来科技有限公司正式成立，专注于软件开发领域</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2010年</div>
            <div class="timeline-content">
              <p>扩展业务至硬件设计领域，推出首款自主研发的服务器产品</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2015年</div>
            <div class="timeline-content">
              <p>开始人工智能技术研发，成立AI研究中心</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2020年</div>
            <div class="timeline-content">
              <p>推出未来AI助手产品，进入智能服务领域</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2025年</div>
            <div class="timeline-content">
              <p>成为行业领先的科技解决方案提供商，服务全球客户</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mb-8 retro-content">
        <h3 class="font-bold mb-3 text-lg">公司价值观</h3>
        <ul class="list-disc pl-6 space-y-2">
          <li>创新：持续创新，引领技术发展</li>
          <li>质量：追求卓越，确保产品质量</li>
          <li>客户：以客户为中心，提供优质服务</li>
          <li>团队：协作共赢，共同成长</li>
          <li>责任：承担社会责任，推动行业发展</li>
        </ul>
      </div>
      
      <div class="retro-content">
        <h3 class="font-bold mb-3 text-lg">联系信息</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="mb-1"><strong>公司名称：</strong>{{ companyInfo.name }}</p>
            <p class="mb-1"><strong>成立年份：</strong>{{ companyInfo.founded_year }}</p>
            <p class="mb-1"><strong>地址：</strong>{{ companyInfo.address }}</p>
          </div>
          <div>
            <p class="mb-1"><strong>电话：</strong>{{ companyInfo.phone }}</p>
            <p class="mb-1"><strong>邮箱：</strong>{{ companyInfo.email }}</p>
            <p class="mb-1"><strong>网站：</strong>{{ companyInfo.website }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <CompanyFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import companyApi from '../api/company.js'
import CompanyFooter from '../components/CompanyFooter.vue'

// 数据
const companyInfo = ref({
  name: '未来科技有限公司',
  description: '未来科技有限公司成立于2005年，是一家专注于软件开发、硬件设计和人工智能技术的高科技企业。我们致力于为客户提供最先进的技术解决方案，帮助客户在数字化时代取得成功。',
  founded_year: 2005,
  address: '北京市海淀区中关村科技园区',
  phone: '010-12345678',
  email: 'contact@futuretech.com',
  website: 'www.futuretech.com',
  slogan: '科技创造未来，创新引领时代'
})

// 加载数据
onMounted(() => {
  loadAboutInfo()
})

const loadAboutInfo = async () => {
  try {
    const response = await companyApi.getAbout()
    if (response.status === 'success' && response.data) {
      companyInfo.value = response.data.company
    }
  } catch (error) {
    console.error('加载关于我们数据失败:', error)
  }
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.retro-container {
  background-color: #f0f0f0;
  color: #333333;
  font-family: SimSun, STSong, serif;
}

.retro-title {
  color: #333333;
  border-bottom: 2px solid #666666;
  padding-bottom: 4px;
  margin-bottom: 12px;
}

.retro-content {
  line-height: 1.8;
  font-size: 14px;
}

.nav-link {
  color: #333333;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #e0e0e0;
}

.nav-link.active {
  background-color: #cccccc;
  font-weight: bold;
}

/* 时间轴样式 */
.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #666666;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-year {
  position: absolute;
  left: -24px;
  background-color: #f0f0f0;
  padding-right: 8px;
  font-weight: bold;
  color: #cc0000;
}

.timeline-content {
  padding: 12px;
  border: 1px solid #666666;
  border-radius: 4px;
  background-color: #f8f8f8;
}
</style>