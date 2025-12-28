<template>
  <div class="merchant-detail" v-if="merchant">
    <!-- 商家头部信息 -->
    <div class="merchant-header">
      <div class="header-bg"></div>
      <div class="merchant-info">
        <img :src="merchant.logo_url || '/static/images/placeholder.png'" :alt="merchant.name" class="merchant-logo"/>
        <div class="merchant-main">
          <h1 class="merchant-name">{{ merchant.name }}</h1>
          <div class="merchant-meta">
            <span class="rating">
              ⭐ {{ merchant.rating || '5.0' }}
            </span>
            <span class="separator">|</span>
            <span>商品数: {{ merchant.product_count || 0 }}</span>
            <span class="separator">|</span>
            <span>已服务: {{ merchant.service_years || 1 }}年</span>
          </div>
          <p class="merchant-desc">{{ merchant.description }}</p>
          <div class="merchant-contact">
            <span v-if="merchant.address">📍 {{ merchant.address }}</span>
            <span v-if="merchant.phone">📞 {{ merchant.phone }}</span>
            <span v-if="merchant.email">✉️ {{ merchant.email }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button class="contact-btn" @click="contactMerchant">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
            联系商家
          </button>
        </div>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="filter-section">
      <div class="filter-tabs">
        <button 
          v-for="category in categories" 
          :key="category.id"
          :class="{ active: selectedCategory === category.id }"
          @click="selectedCategory = category.id"
        >
          {{ category.name }}
        </button>
        <button 
          :class="{ active: selectedCategory === null }"
          @click="selectedCategory = null"
        >
          全部商品
        </button>
      </div>
      <div class="filter-options">
        <select v-model="sortBy" @change="fetchProducts">
          <option value="default">默认排序</option>
          <option value="price_asc">价格从低到高</option>
          <option value="price_desc">价格从高到低</option>
          <option value="sales">销量排序</option>
          <option value="rating">评分排序</option>
        </select>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="products-section">
      <div class="section-header">
        <h2>商品列表</h2>
        <span class="count">共{{ filteredProducts.length }}件商品</span>
      </div>

      <div class="products-grid" v-if="filteredProducts.length > 0">
        <div 
          v-for="product in paginatedProducts" 
          :key="product.id"
          class="product-card"
          @click="goToProduct(product.id)"
        >
          <div class="product-image">
            <img :src="product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
            <div class="product-tags" v-if="product.is_featured">
              <span class="featured">精选</span>
            </div>
          </div>
          <div class="product-info">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-desc">{{ truncateText(product.description, 50) }}</p>
            <div class="product-meta">
              <span class="price">¥{{ product.price.toFixed(2) }}</span>
              <span class="sales" v-if="product.sales_count">已售{{ product.sales_count }}件</span>
            </div>
            <div class="product-rating">
              <span class="stars">⭐ {{ product.rating || '5.0' }}</span>
              <span class="reviews" v-if="product.review_count">{{ product.review_count }}评价</span>
            </div>
          </div>
        </div>
      </div>

      <div class="no-products" v-else>
        <p>该分类暂无商品</p>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          上一页
        </button>
        <span class="page-info">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 商家介绍 -->
    <div class="merchant-intro">
      <h2>商家介绍</h2>
      <div class="intro-content">
        <div class="intro-section">
          <h3>关于我们</h3>
          <p>{{ merchant.description }}</p>
        </div>
        <div class="intro-section" v-if="merchant.certifications">
          <h3>资质认证</h3>
          <ul>
            <li v-for="cert in parseJson(merchant.certifications)" :key="cert">{{ cert }}</li>
          </ul>
        </div>
        <div class="intro-section" v-if="merchant.services">
          <h3>服务保障</h3>
          <ul>
            <li v-for="service in parseJson(merchant.services)" :key="service">{{ service }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- 加载状态 -->
  <div class="loading" v-else-if="loading">
    <div class="spinner"></div>
    <p>加载中...</p>
  </div>

  <!-- 错误状态 -->
  <div class="error" v-else>
    <p>商家不存在或已被删除</p>
    <router-link to="/shop">返回商城首页</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMerchantDetail, getCategories, getProducts } from '@/api/shop'

const route = useRoute()
const router = useRouter()

// 状态
const merchant = ref(null)
const categories = ref([])
const products = ref([])
const loading = ref(false)
const selectedCategory = ref(null)
const sortBy = ref('default')
const currentPage = ref(1)
const pageSize = ref(12)

// 获取商家详情
async function fetchMerchant() {
  const merchantId = route.params.id;
  console.log('正在获取商家详情，ID:', merchantId);
  
  loading.value = true;
  merchant.value = null; // 重置商家数据，确保错误状态正确显示
  
  try {
    // 打印API调用信息
    console.log(`调用API: /api/shop/merchants/${merchantId}`);
    
    // 调用API获取商家详情
    const data = await getMerchantDetail(merchantId);
    
    // 打印原始返回数据，用于调试
    console.log('API返回原始数据:', JSON.stringify(data, null, 2));
    
    // 检查数据结构
    if (data && typeof data === 'object') {
      // 情况1: 如果data已经是完整的响应对象 (包含data属性)
      if (data.success && data.data?.merchant) {
        console.log('数据解析成功，找到商家信息');
        merchant.value = data.data.merchant;
        products.value = data.data.products || [];
      }
      // 情况2: 检查data中是否直接包含merchant字段
      else if (data.merchant) {
        console.log('找到直接包含merchant字段的数据');
        merchant.value = data.merchant;
        products.value = data.products || [];
      }
      // 情况3: 检查data本身是否就是商家对象
      else if (data.id && data.name) {
        console.log('data本身就是商家对象');
        merchant.value = data;
      }
      else {
        console.warn('商家不存在或数据格式不正确');
        merchant.value = null; // 确保错误状态显示
      }
    } else {
      console.error('返回数据格式错误，不是有效的JSON对象');
      merchant.value = null;
    }
  } catch (error) {
    console.error('获取商家详情失败:', error);
    merchant.value = null; // 确保错误状态显示
    
    // 增加用户提示
    alert(`获取商家信息失败: ${error.message || '未知错误'}`);
  } finally {
    loading.value = false;
    console.log('fetchMerchant函数执行完成，当前merchant状态:', merchant.value ? '已找到商家' : '未找到商家');
  }
}

// 获取商品列表
async function fetchProducts() {
  try {
    const params = {
      merchant_id: route.params.id,
      category_id: selectedCategory.value,
      sort: sortBy.value,
      limit: 100
    }
    
    // 现在使用后端API获取真实商品数据，而不是模拟数据
    // 由于拦截器已经返回response.data，所以直接使用返回的数据
    const data = await getProducts(params)
    if (data?.success) {
      products.value = data.data
    }
  } catch (error) {
    console.error('获取商品列表失败:', error)
  }
}

// 获取分类列表
async function fetchCategories() {
  try {
    // 由于拦截器已经返回response.data，所以直接使用返回的数据
    const data = await getCategories()
    if (data?.success) {
      categories.value = data.data
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

// 过滤商品
const filteredProducts = computed(() => {
  let filtered = products.value
  
  if (selectedCategory.value !== null) {
    filtered = filtered.filter(p => p.category_id === selectedCategory.value)
  }
  
  return filtered
})

// 排序商品
const sortedProducts = computed(() => {
  let sorted = [...filteredProducts.value]
  
  switch (sortBy.value) {
    case 'price_asc':
      sorted.sort((a, b) => a.price - b.price)
      break
    case 'price_desc':
      sorted.sort((a, b) => b.price - a.price)
      break
    case 'sales':
      sorted.sort((a, b) => (b.sales_count || 0) - (a.sales_count || 0))
      break
    case 'rating':
      sorted.sort((a, b) => (b.rating || 0) - (a.rating || 0))
      break
  }
  
  return sorted
})

// 分页商品
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sortedProducts.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(sortedProducts.value.length / pageSize.value)
})

// 截断文本
function truncateText(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 解析JSON
function parseJson(jsonStr) {
  if (!jsonStr) return []
  try {
    return JSON.parse(jsonStr)
  } catch {
    return []
  }
}

// 跳转到商品详情
function goToProduct(productId) {
  router.push(`/shop/product/${productId}`)
}

// 联系商家
function contactMerchant() {
  // TODO: 实现联系商家功能
  console.log('联系商家:', merchant.value.id)
}

// 监听分类变化，重置分页
watch(selectedCategory, () => {
  currentPage.value = 1
})

// 监听路由参数变化
watch(() => route.params.id, () => {
  fetchMerchant()
})

onMounted(() => {
  fetchMerchant()
  fetchCategories()
})
</script>

<style scoped>
.merchant-detail {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 商家头部 */
.merchant-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 40px 20px;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 20"><defs><pattern id="grain" width="100" height="20" patternUnits="userSpaceOnUse"><circle cx="20" cy="10" r="1" fill="white" opacity="0.1"/><circle cx="80" cy="10" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="5" r="0.5" fill="white" opacity="0.2"/><circle cx="50" cy="15" r="0.5" fill="white" opacity="0.2"/></pattern></defs><rect width="100" height="20" fill="url(%23grain)"/></svg>');
}

.merchant-info {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.merchant-logo {
  width: 120px;
  height: 120px;
  border-radius: 20px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.merchant-main {
  flex: 1;
}

.merchant-name {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.merchant-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 16px;
}

.separator {
  opacity: 0.7;
}

.merchant-desc {
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 15px;
  max-width: 600px;
  opacity: 0.9;
}

.merchant-contact {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 14px;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.contact-btn {
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.contact-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

/* 筛选区域 */
.filter-section {
  background: #fff;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.filter-tabs {
  display: flex;
  gap: 10px;
}

.filter-tabs button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.filter-tabs button.active {
  background: #667eea;
  color: #fff;
  border-color: #667eea;
}

.filter-options select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}

/* 商品区域 */
.products-section {
  padding: 30px 20px;
  max-width: 1200px;
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

.count {
  color: #999;
  font-size: 14px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
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

.product-tags {
  position: absolute;
  top: 10px;
  left: 10px;
}

.featured {
  padding: 5px 12px;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
  line-height: 1.4;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
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

.product-rating {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.stars {
  color: #ffc107;
}

/* 无商品 */
.no-products {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.pagination button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination button:hover:not(:disabled) {
  background: #667eea;
  color: #fff;
  border-color: #667eea;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
}

/* 商家介绍 */
.merchant-intro {
  background: #fff;
  padding: 30px 20px;
  margin: 20px;
  border-radius: 12px;
  max-width: 1200px;
}

.merchant-intro h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.intro-content {
  display: grid;
  gap: 30px;
}

.intro-section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.intro-section p {
  line-height: 1.8;
  color: #666;
}

.intro-section ul {
  padding-left: 20px;
}

.intro-section li {
  line-height: 2;
  color: #666;
}

/* 加载和错误状态 */
.loading,
.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  gap: 15px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error a {
  color: #667eea;
  text-decoration: none;
}

/* 响应式 */
@media (max-width: 768px) {
  .merchant-info {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .merchant-name {
    font-size: 28px;
  }
  
  .filter-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-tabs {
    overflow-x: auto;
    width: 100%;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
}
</style>