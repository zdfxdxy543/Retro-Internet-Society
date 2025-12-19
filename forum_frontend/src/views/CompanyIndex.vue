<template>
  <div class="container retro-container">
    <!-- 公司网站头部 -->
    <div class="bg-retro-header text-white py-6 px-4 mb-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">{{ companyInfo.name }}</h1>
        <p class="text-lg italic">{{ companyInfo.slogan }}</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <div class="bg-retro-postBg border border-retro-border py-2 px-4 mb-6">
      <div class="max-w-5xl mx-auto flex space-x-8 text-center">
        <router-link to="/company" class="nav-link active">首页</router-link>
        <router-link to="/company/products" class="nav-link">产品中心</router-link>
        <router-link to="/company/about" class="nav-link">关于我们</router-link>
        <router-link to="/company/contact" class="nav-link">联系我们</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 左侧：公司简介 -->
      <div class="md:col-span-2 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">公司简介</h2>
        <div class="retro-content">
          <!-- 添加低像素图片位置 -->
          <div class="mb-4 h-48 bg-gray-200 border border-retro-border overflow-hidden">
            <img src="https://via.placeholder.com/800x400?text=Company+Logo" alt="公司图片" class="w-full h-full object-cover filter blur-[0.3px]" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;">
          </div>
          <p>{{ companyInfo.description }}</p>
          <div class="mt-4 flex justify-between text-sm retro-meta">
            <p>成立年份：{{ companyInfo.founded_year }}</p>
            <p>地址：{{ companyInfo.address }}</p>
            <p>电话：{{ companyInfo.phone }}</p>
            <p>邮箱：{{ companyInfo.email }}</p>
          </div>
        </div>
      </div>
      
      <!-- 右侧：联系方式 -->
      <div class="bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">联系方式</h2>
        <div class="retro-content">
          <p class="mb-2"><strong>公司名称：</strong>{{ companyInfo.name }}</p>
          <p class="mb-2"><strong>地址：</strong>{{ companyInfo.address }}</p>
          <p class="mb-2"><strong>电话：</strong>{{ companyInfo.phone }}</p>
          <p class="mb-2"><strong>邮箱：</strong>{{ companyInfo.email }}</p>
          <p class="mb-2"><strong>网站：</strong>{{ companyInfo.website }}</p>
        </div>
      </div>
      
      <!-- 产品分类 -->
      <div class="md:col-span-1 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">产品分类</h2>
        <div class="retro-content">
          <ul class="space-y-2">
            <li v-for="category in categories" :key="category.id">
              <router-link :to="`/company/products/category/${category.id}`" class="block p-2 hover:bg-retro-bg rounded">
                <div class="font-bold">{{ category.name }}</div>
                <div class="text-sm text-retro-meta">{{ category.description }}</div>
                <div class="text-xs text-retro-text">{{ category.product_count }} 个产品</div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 最新产品 -->
      <div class="md:col-span-2 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">最新产品</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 retro-content">
          <div v-for="product in latestProducts" :key="product.id" class="border border-retro-border p-3 hover:shadow-md transition-shadow">
            <router-link :to="`/company/product/${product.id}`" class="block">
              <div class="mb-2 h-32 bg-gray-200 flex items-center justify-center">
                <span class="text-gray-500">{{ product.name }}</span>
              </div>
              <div class="font-bold mb-1">{{ product.name }}</div>
              <div class="text-sm text-retro-meta mb-2">{{ product.model }}</div>
              <div class="text-xs line-clamp-3 mb-2">{{ product.description }}</div>
              <div class="text-right font-bold text-retro-accent">{{ product.price ? '¥' + product.price.toFixed(2) : '价格面议' }}</div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import companyApi from '../api/company.js'
import Footer from '../components/Footer.vue'

// 数据
const companyInfo = ref({
  name: '未来科技有限公司',
  slogan: '科技创造未来，创新引领时代',
  description: '加载中...',
  founded_year: '',
  address: '',
  phone: '',
  email: '',
  website: ''
})

const categories = ref([])
const latestProducts = ref([])

// 加载数据
onMounted(() => {
  loadCompanyIndex()
})

const loadCompanyIndex = async () => {
  try {
    const response = await companyApi.getCompanyIndex()
    if (response.status === 'success' && response.data) {
      companyInfo.value = response.data.company
      categories.value = response.data.categories
      latestProducts.value = response.data.latest_products
    }
  } catch (error) {
    console.error('加载公司首页数据失败:', error)
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

.retro-meta {
  color: #666666;
}

.retro-accent {
  color: #cc0000;
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
</style>