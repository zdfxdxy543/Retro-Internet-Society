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
        <router-link to="/company/about" class="nav-link">关于我们</router-link>
        <router-link to="/company/contact" class="nav-link">联系我们</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 左侧：产品图片 -->
      <div class="md:col-span-1 bg-retro-postBg border border-retro-border p-4">
        <!-- 正方形低像素产品图片 -->
        <div class="w-full aspect-square bg-gray-200 border border-retro-border overflow-hidden mb-4">
          <img 
            :src="product.image_url ? product.image_url : 'https://via.placeholder.com/400x400?text=Product+Image'" 
            :alt="product.name" 
            class="w-full h-full object-contain p-4 filter blur-[0.3px]" 
            style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"
          >
        </div>
        <div class="retro-content">
          <h3 class="font-bold mb-2">产品型号</h3>
          <p class="mb-4">{{ product.model }}</p>
          
          <h3 class="font-bold mb-2">价格</h3>
          <p class="text-retro-accent font-bold text-xl mb-4">
            {{ product.price ? '¥' + product.price.toFixed(2) : '价格面议' }}
          </p>
          
          <h3 class="font-bold mb-2">库存</h3>
          <p class="mb-4">{{ product.stock > 0 ? '有现货' : '缺货' }}</p>
          
          <!-- DataSheet下载 -->
          <div class="mt-6">
            <!-- 下载DataSheet按钮 -->
            <button 
              @click="downloadDatasheet" 
              class="block w-full bg-green-700 hover:bg-green-800 text-white text-center py-2 px-4 rounded transition-colors"
              :disabled="loading || !product.datasheet_url"
            >
              {{ loading ? '下载中...' : '下载产品DataSheet' }}
            </button>
            <p v-if="!product.datasheet_url" class="text-retro-meta text-center mt-2">暂无可用的DataSheet</p>
          </div>
        </div>
      </div>
      
      <!-- 右侧：产品详情 -->
      <div class="md:col-span-2 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-2xl font-bold mb-4 retro-title">{{ product.name }}</h2>
        
        <div class="mb-6 retro-content">
          <h3 class="font-bold mb-2 text-lg">产品描述</h3>
          <p>{{ product.description }}</p>
        </div>
        
        <div class="mb-6 retro-content">
          <h3 class="font-bold mb-2 text-lg">产品特性</h3>
          <ul class="list-disc pl-6 space-y-1">
            <li v-for="(feature, index) in product.features" :key="index">
              {{ feature }}
            </li>
          </ul>
        </div>
        
        <div class="mb-6 retro-content">
          <h3 class="font-bold mb-2 text-lg">产品规格</h3>
          <table class="w-full border-collapse">
            <tr v-for="(spec, index) in Object.keys(product.specifications)" :key="index">
              <td class="border border-retro-border px-3 py-2 font-bold w-1/3">{{ spec }}</td>
              <td class="border border-retro-border px-3 py-2">{{ product.specifications[spec] }}</td>
            </tr>
          </table>
        </div>
        
        <div class="retro-meta text-sm">
          <p>更新时间：{{ product.update_time }}</p>
          <p class="mt-2">
            <router-link to="/company/products" class="text-blue-700 hover:underline">
              返回产品列表
            </router-link>
          </p>
        </div>
      </div>
      
      <!-- 相关产品 -->
      <div class="md:col-span-3 bg-retro-postBg border border-retro-border p-4">
        <h2 class="text-xl font-bold mb-4 retro-title">相关产品</h2>
        
        <div v-if="relatedProducts.length > 0" class="grid grid-cols-1 sm:grid-cols-3 gap-4 retro-content">
          <div v-for="related in relatedProducts" :key="related.id" class="border border-retro-border p-3 hover:shadow-md transition-shadow">
            <router-link :to="`/company/product/${related.id}`" class="block">
              <div class="mb-2 h-32 bg-gray-200 flex items-center justify-center">
                <span class="text-gray-500">{{ related.name }}</span>
              </div>
              <div class="font-bold mb-1">{{ related.name }}</div>
              <div class="text-sm text-retro-meta mb-2">{{ related.model }}</div>
              <div class="text-xs line-clamp-3">{{ related.description }}</div>
            </router-link>
          </div>
        </div>
        
        <div v-else class="text-center py-6 retro-content">
          <p>暂无相关产品</p>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <CompanyFooter />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import companyApi from '../api/company.js'
import CompanyFooter from '../components/CompanyFooter.vue'

// 路由参数
const route = useRoute()
const router = useRouter()

// 数据
const product = ref({
  name: '',
  model: '',
  description: '',
  price: null,
  features: [],
  specifications: {},
  datasheet_url: '',
  stock: 0,
  update_time: ''
})

const relatedProducts = ref([])
const loading = ref(false) // 保留加载状态

// 加载产品详情
const loadProductDetail = async () => {
  const productId = route.params.productId
  try {
    const response = await companyApi.getProductDetail(productId)
    if (response.status === 'success' && response.data) {
      product.value = response.data.product
      relatedProducts.value = response.data.related_products
    }
  } catch (error) {
    console.error('加载产品详情失败:', error)
    // 如果产品不存在，重定向到产品列表页
    router.push('/company/products')
  }
}

// 下载DataSheet
const downloadDatasheet = async () => {
  const productId = route.params.productId
  loading.value = true
  try {
    const response = await companyApi.downloadProductDatasheet(productId)
    // 创建下载链接
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${product.value.name}_datasheet.pdf`
    document.body.appendChild(link)
    link.click()
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载DataSheet失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听路由变化，重新加载产品详情
watch(() => route.params.productId, () => {
  loadProductDetail()
})

// 页面加载时初始化数据
onMounted(() => {
  loadProductDetail()
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

/* 表格样式 */
table {
  border-collapse: collapse;
}

td {
  border: 1px solid #666666;
  padding: 8px;
}
</style>