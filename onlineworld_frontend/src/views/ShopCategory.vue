<template>
  <div class="shop-category">
    <!-- 分类详情 -->
    <div class="category-header">
      <div class="category-info">
        <h1>{{ category.name || '商品分类' }}</h1>
        <p>{{ category.description || '' }}</p>
      </div>
    </div>

    <!-- 商品列表 -->
    <section class="section">
      <div class="section-header">
        <h2>📦 分类商品</h2>
      </div>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="products.length === 0" class="empty-container">
        <p>该分类下暂无商品</p>
      </div>
      
      <div v-else class="product-grid">
        <div 
          v-for="product in products" 
          :key="product.id"
          class="product-card"
          @click="goToProduct(product.id)"
        >
          <div class="product-image">
            <img :src="product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="merchant-name">{{ product.merchant_name }}</p>
            <div class="product-bottom">
              <span class="price">¥{{ product.price.toFixed(2) }}</span>
              <span class="sales">已售{{ product.sales_count || 0 }}件</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getCategories, getCategoryProducts } from '@/api/shop'

const router = useRouter()
const route = useRoute()

// 数据
const category = ref({})
const products = ref([])
const categories = ref([])
const loading = ref(false)
const error = ref(null)

// 获取分类和商品数据
async function fetchData() {
  const categoryId = route.params.categoryId
  if (!categoryId) return
  
  loading.value = true
  error.value = null
  
  try {
    // 并行请求分类信息和分类商品
    const [categoriesRes, productsRes] = await Promise.allSettled([
      getCategories(),
      getCategoryProducts(categoryId, { limit: 20 })
    ])
    
    // 处理分类数据
    if (categoriesRes.status === 'fulfilled') {
      const categoriesData = categoriesRes.value
      if (categoriesData?.success && Array.isArray(categoriesData.data)) {
        categories.value = categoriesData.data
        // 找到当前分类
        const currentCategory = categoriesData.data.find(c => c.id === parseInt(categoryId))
        if (currentCategory) {
          category.value = currentCategory
          // 更新页面标题
          document.title = `在线商城 - ${currentCategory.name}`
        }
      }
    }
    
    // 处理商品数据
    if (productsRes.status === 'fulfilled') {
      const productsData = productsRes.value
      if (productsData?.success && Array.isArray(productsData.data)) {
        products.value = productsData.data
      }
    }
  } catch (err) {
    console.error('获取分类数据失败:', err)
    error.value = '获取数据失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 跳转到商品详情
function goToProduct(productId) {
  router.push(`/shop/product/${productId}`)
}

// 监听路由参数变化
watch(
  () => route.params.categoryId,
  (newId) => {
    if (newId) {
      fetchData()
    }
  }
)

// 页面加载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.shop-category {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 分类头部 */
.category-header {
  background: #fff;
  padding: 30px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.category-info {
  max-width: 1400px;
  margin: 0 auto;
}

.category-info h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.category-info p {
  font-size: 14px;
  color: #666;
}

/* 区块通用样式 */
.section {
  padding: 30px 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 24px;
  color: #333;
}

/* 商品网格 */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.product-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.product-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-info {
  padding: 15px;
}

.product-info h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-name {
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}

.product-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 20px;
  font-weight: bold;
  color: #e74c3c;
}

.sales {
  font-size: 12px;
  color: #999;
}

/* 加载状态 */
.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-container {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.empty-container p {
  color: #999;
  font-size: 16px;
}
</style>