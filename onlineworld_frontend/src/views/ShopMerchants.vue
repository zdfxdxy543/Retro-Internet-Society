<template>
  <div class="shop-merchants">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>所有商家</h1>
      <p>浏览我们平台上的所有优质商家</p>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="filter-section">
      <div class="search-bar">
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索商家名称..."
          @keyup.enter="searchMerchants"
        />
        <button @click="searchMerchants" class="search-btn">搜索</button>
      </div>
    </div>

    <!-- 商家列表 -->
    <div class="merchants-grid" v-if="!loading">
      <div 
        v-for="merchant in merchants" 
        :key="merchant.id" 
        class="merchant-card"
        @click="goToMerchantDetail(merchant.id)"
      >
        <!-- 商家Logo -->
        <div class="merchant-logo">
          <img :src="merchant.logo_url || defaultLogo" :alt="merchant.name" />
        </div>
        
        <!-- 商家信息 -->
        <div class="merchant-info">
          <h3 class="merchant-name">{{ merchant.name }}</h3>
          <p class="merchant-desc">{{ truncateText(merchant.description, 80) }}</p>
          
          <!-- 商家评分和销量 -->
          <div class="merchant-meta">
            <div class="rating">
              <span class="star">⭐</span>
              <span class="score">{{ merchant.rating }}</span>
            </div>
            <div class="sales">销量: {{ merchant.total_sales }}</div>
          </div>
          
          <!-- 认证标识 -->
          <div class="merchant-badges">
            <span v-if="merchant.is_verified" class="badge verified">认证商家</span>
            <span v-if="merchant.is_active" class="badge active">营业中</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else class="loading">
      <div class="spinner"></div>
      <p>正在加载商家列表...</p>
    </div>

    <!-- 无数据状态 -->
    <div v-if="!loading && merchants.length === 0" class="no-data">
      <p>{{ searchKeyword ? '没有找到匹配的商家' : '暂无商家信息' }}</p>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMerchants } from '@/api/shop'

const router = useRouter()

// 状态
const merchants = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pagination = ref({
  total: 0,
  page: 1,
  per_page: 20,
  pages: 0
})

// 默认Logo
const defaultLogo = '/assets/images/default-merchant-logo.png'

// 获取商家列表
async function fetchMerchants() {
  loading.value = true
  try {
    const response = await getMerchants()
    if (response.success && response.data) {
      merchants.value = response.data
      pagination.value = {
        total: response.total || 0,
        page: response.page || 1,
        per_page: response.per_page || 20,
        pages: response.pages || 0
      }
      currentPage.value = pagination.value.page
    }
  } catch (error) {
    console.error('获取商家列表失败:', error)
    // 可以添加错误提示
  } finally {
    loading.value = false
  }
}

// 搜索商家
async function searchMerchants() {
  loading.value = true
  currentPage.value = 1
  try {
    // 这里可以扩展搜索功能，目前使用现有的API
    const response = await getMerchants()
    if (response.success && response.data) {
      // 如果有搜索关键词，在前端进行过滤
      if (searchKeyword.value) {
        merchants.value = response.data.filter(merchant => 
          merchant.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
        )
      } else {
        merchants.value = response.data
      }
      
      pagination.value = {
        total: merchants.value.length,
        page: 1,
        per_page: 20,
        pages: Math.ceil(merchants.value.length / 20)
      }
    }
  } catch (error) {
    console.error('搜索商家失败:', error)
  } finally {
    loading.value = false
  }
}

// 分页切换
function changePage(page) {
  if (page >= 1 && page <= pagination.value.pages) {
    currentPage.value = page
    // 这里可以添加分页加载逻辑
  }
}

// 跳转到商家详情
function goToMerchantDetail(merchantId) {
  router.push(`/shop/merchant/${merchantId}`)
}

// 截断文本
function truncateText(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 组件挂载时获取数据
onMounted(() => {
  fetchMerchants()
})
</script>

<style scoped>
.shop-merchants {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 16px;
}

/* 搜索区域 */
.filter-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.search-bar {
  display: flex;
  gap: 10px;
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

/* 商家列表网格 */
.merchants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

/* 商家卡片 */
.merchant-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.merchant-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* 商家Logo */
.merchant-logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  border-radius: 50%;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.merchant-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 商家信息 */
.merchant-info {
  text-align: center;
}

.merchant-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.merchant-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

/* 商家元数据 */
.merchant-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.rating {
  display: flex;
  align-items: center;
  gap: 4px;
}

.star {
  font-size: 16px;
}

.score {
  font-weight: 600;
  color: #ff6b35;
}

/* 商家徽章 */
.merchant-badges {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge.verified {
  background: #4caf50;
  color: white;
}

.badge.active {
  background: #2196f3;
  color: white;
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
  .merchants-grid {
    grid-template-columns: 1fr;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 10px;
  }
}
</style>
