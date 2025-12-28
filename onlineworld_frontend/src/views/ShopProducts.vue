<template>
  <div class="shop-products">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>商品列表</h1>
      <p v-if="searchKeyword">搜索结果: "{{ searchKeyword }}"</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input 
        v-model="localSearchKeyword" 
        type="text" 
        placeholder="搜索商品名称..."
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch" class="search-btn">搜索</button>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <!-- 分类筛选 -->
      <div class="filter-group">
        <label>分类:</label>
        <select v-model="selectedCategory" @change="applyFilters">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>

      <!-- 排序选项 -->
      <div class="filter-group">
        <label>排序:</label>
        <select v-model="sortBy" @change="applyFilters">
          <option value="create_time">最新上架</option>
          <option value="price_asc">价格从低到高</option>
          <option value="price_desc">价格从高到低</option>
          <option value="sales_count">销量优先</option>
          <option value="rating">评分优先</option>
        </select>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="product-grid" v-if="!loading">
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
          <div class="product-meta">
            <span class="price">¥{{ product.price.toFixed(2) }}</span>
            <span class="sales" v-if="product.sales_count">已售{{ product.sales_count }}件</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 无数据状态 -->
    <div v-if="!loading && products.length === 0" class="no-data">
      <p>{{ searchKeyword ? '没有找到匹配的商品' : '暂无商品信息' }}</p>
    </div>

    <!-- 分页 -->
    <div v-if="!loading && pagination.total > 0" class="pagination">
      <button 
        @click="changePage(currentPage - 1)" 
        :disabled="currentPage <= 1"
        class="page-btn"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ pagination.pages }} 页
      </span>
      
      <button 
        @click="changePage(currentPage + 1)" 
        :disabled="currentPage >= pagination.pages"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getProducts, getCategories } from '@/api/shop'

const router = useRouter()
const route = useRoute()

// 状态
const products = ref([])
const categories = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const localSearchKeyword = ref('')
const selectedCategory = ref('')
const sortBy = ref('create_time')
const currentPage = ref(1)
const pagination = ref({
  total: 0,
  page: 1,
  per_page: 20,
  pages: 0
})

// 获取分类列表
async function fetchCategories() {
  try {
    const response = await getCategories()
    if (response.success && Array.isArray(response.data)) {
      categories.value = response.data
    }
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 获取商品列表
async function fetchProducts() {
  loading.value = true
  try {
    // 构建请求参数
    const params = {
      page: currentPage.value,
      per_page: 20
    }

    // 添加筛选条件
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }

    // 添加排序条件
    if (sortBy.value === 'price_asc') {
      params.sort_by = 'price'
      params.sort_order = 'asc'
    } else if (sortBy.value === 'price_desc') {
      params.sort_by = 'price'
      params.sort_order = 'desc'
    } else if (sortBy.value !== 'create_time') {
      params.sort_by = sortBy.value
    }

    const response = await getProducts(params)
    if (response.success && response.data) {
      products.value = response.data
      pagination.value = {
        total: response.total || 0,
        page: response.page || 1,
        per_page: response.per_page || 20,
        pages: response.pages || 0
      }
    }
  } catch (error) {
    console.error('获取商品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理搜索
function handleSearch() {
  searchKeyword.value = localSearchKeyword.value
  currentPage.value = 1
  fetchProducts()
}

// 应用筛选
function applyFilters() {
  currentPage.value = 1
  fetchProducts()
}

// 分页切换
function changePage(page) {
  if (page >= 1 && page <= pagination.value.pages) {
    currentPage.value = page
    fetchProducts()
  }
}

// 跳转到商品详情
function goToProduct(productId) {
  router.push(`/shop/product/${productId}`)
}

// 监听路由参数变化
watch(
  () => route.query.keyword,
  (newKeyword) => {
    searchKeyword.value = newKeyword || ''
    localSearchKeyword.value = searchKeyword.value
    fetchProducts()
  },
  { immediate: true }
)

// 监听其他查询参数
watch(
  () => route.query,
  (newQuery) => {
    if (newQuery.category_id) {
      selectedCategory.value = newQuery.category_id
    }
    if (newQuery.sort) {
      sortBy.value = newQuery.sort
    }
  },
  { immediate: true, deep: true }
)

// 组件挂载时获取数据
onMounted(async () => {
  await fetchCategories()
  fetchProducts()
})
</script>

<style scoped>
.shop-products {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 16px;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #5a67d8;
}

/* 筛选区域 */
.filter-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #666;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
}

/* 商品列表 */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

/* 商品卡片 */
.product-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* 商品图片 */
.product-image {
  height: 200px;
  background: #f8f8f8;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 商品信息 */
.product-info {
  padding: 16px;
}

.product-info h3 {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.merchant-name {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 18px;
  font-weight: 600;
  color: #ff4757;
}

.sales {
  font-size: 12px;
  color: #999;
}

/* 加载状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 无数据状态 */
.no-data {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: #fff;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #ccc;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 10px;
  }
}
</style>
