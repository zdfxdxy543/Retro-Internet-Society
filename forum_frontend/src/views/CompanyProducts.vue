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
        <router-link to="/company/products" class="nav-link active">产品中心</router-link>
        <router-link to="/company/about" class="nav-link">关于我们</router-link>
        <router-link to="/company/contact" class="nav-link">联系我们</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6">
      <!-- 左侧：产品分类筛选 -->
      <div class="md:col-span-1 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">产品分类</h2>
        <div class="retro-content space-y-2">
          <router-link 
            to="/company/products" 
            class="block p-2 hover:bg-retro-bg rounded"
            :class="{ 'bg-retro-bg': !currentCategoryId }"
          >
            全部产品
          </router-link>
          <router-link 
            v-for="category in categories" 
            :key="category.id"
            :to="`/company/products/category/${category.id}`"
            class="block p-2 hover:bg-retro-bg rounded"
            :class="{ 'bg-retro-bg': currentCategoryId == category.id }"
          >
            {{ category.name }} ({{ category.product_count }})
          </router-link>
        </div>
      </div>
      
      <!-- 右侧：产品列表 -->
      <div class="md:col-span-3 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">
          {{ currentCategory ? currentCategory + '产品' : '全部产品' }}
        </h2>
        
        <div v-if="products.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-6 retro-content">
          <div v-for="product in products" :key="product.id" class="border border-retro-border p-4 hover:shadow-md transition-shadow">
            <router-link :to="`/company/product/${product.id}`" class="block">
              <div class="mb-3 h-40 bg-gray-200 flex items-center justify-center">
                <span class="text-gray-500">{{ product.name }}</span>
              </div>
              <div class="font-bold mb-1 text-lg">{{ product.name }}</div>
              <div class="text-sm text-retro-meta mb-2">{{ product.model }}</div>
              <div class="text-xs line-clamp-4 mb-3">{{ product.description }}</div>
              <div class="text-right font-bold text-retro-accent text-lg">
                {{ product.price ? '¥' + product.price.toFixed(2) : '价格面议' }}
              </div>
              <div class="mt-3 text-right">
                <span class="text-xs bg-gray-200 px-2 py-1 rounded">{{ product.category_name }}</span>
              </div>
            </router-link>
          </div>
        </div>
        
        <div v-else class="text-center py-12 retro-content">
          <p class="text-lg">暂无产品数据</p>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import companyApi from '../api/company.js'
import Footer from '../components/Footer.vue'

// 路由参数
const route = useRoute()
const router = useRouter()

// 数据
const categories = ref([])
const products = ref([])

// 计算当前分类ID
const currentCategoryId = computed(() => {
  return route.params.categoryId ? Number(route.params.categoryId) : null
})

// 计算当前分类名称
const currentCategory = computed(() => {
  if (!currentCategoryId.value) return ''
  const category = categories.value.find(c => c.id === currentCategoryId.value)
  return category ? category.name : ''
})

// 加载产品数据
const loadProducts = async () => {
  try {
    const response = await companyApi.getProducts(currentCategoryId.value)
    if (response.status === 'success' && response.data) {
      categories.value = response.data.categories
      products.value = response.data.products
    }
  } catch (error) {
    console.error('加载产品数据失败:', error)
  }
}

// 监听分类ID变化，重新加载产品
watch(currentCategoryId, () => {
  loadProducts()
})

// 页面加载时初始化数据
onMounted(() => {
  loadProducts()
})
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