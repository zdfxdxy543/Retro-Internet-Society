<template>
  <div class="product-detail" v-if="product">
    <!-- 商品主图和基本信息 -->
    <div class="product-main">
      <!-- 商品图片 -->
      <div class="product-gallery">
        <div class="main-image">
          <img :src="currentImage || product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
        </div>
        <div class="thumbnail-list" v-if="product.images && product.images.length > 1">
          <div 
            v-for="(img, index) in product.images" 
            :key="index"
            class="thumbnail"
            :class="{ active: currentImage === img }"
            @click="currentImage = img"
          >
            <img :src="img" :alt="`商品图${index + 1}`"/>
          </div>
        </div>
      </div>

      <!-- 商品信息 -->
      <div class="product-info">
        <div class="breadcrumb">
          <router-link to="/shop">商城</router-link>
          <span>/</span>
          <router-link :to="`/shop/category/${product.category_id}`">{{ product.category_name }}</router-link>
          <span>/</span>
          <span>{{ product.name }}</span>
        </div>

        <h1 class="product-title">{{ product.name }}</h1>
        
        <div class="product-meta">
          <span class="sku">商品编号: {{ product.sku || product.id }}</span>
          <span class="category">分类: {{ product.category_name }}</span>
        </div>

        <div class="price-section">
          <span class="price-label">价格</span>
          <span class="price">¥{{ product.price.toFixed(2) }}</span>
          <span class="original-price" v-if="product.original_price">¥{{ product.original_price.toFixed(2) }}</span>
        </div>

        <div class="sales-info" v-if="product.sales_count">
          <span>累计销量 {{ product.sales_count }} 件</span>
          <span>库存 {{ product.stock }} 件</span>
        </div>

        <div class="merchant-info" @click="goToMerchant(product.merchant_id)">
          <img :src="product.merchant_logo || '/static/images/placeholder.png'" :alt="product.merchant_name"/>
          <div class="merchant-detail">
            <span class="merchant-label">店铺</span>
            <span class="merchant-name">{{ product.merchant_name }}</span>
          </div>
          <span class="go-shop">进店 ></span>
        </div>

        <div class="quantity-selector">
          <span class="label">数量</span>
          <div class="quantity-control">
            <button @click="decreaseQuantity" :disabled="quantity <= 1">-</button>
            <input type="number" v-model="quantity" min="1" :max="product.stock"/>
            <button @click="increaseQuantity" :disabled="quantity >= product.stock">+</button>
          </div>
          <span class="stock-tip" v-if="product.stock < 10">仅剩{{ product.stock }}件</span>
        </div>

        <div class="action-buttons">
          <button class="buy-now" @click="buyNow">立即购买</button>
          <button class="add-cart" @click="addToCart">加入购物车</button>
        </div>

        <div class="service-tags">
          <span class="tag">🔒 保障支付</span>
          <span class="tag">🚚 48小时发货</span>
          <span class="tag">📦 正品保障</span>
          <span class="tag">🔄 7天无理由</span>
        </div>
      </div>
    </div>

    <!-- 商品详情和评价 -->
    <div class="product-tabs">
      <div class="tab-header">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 商品介绍 -->
      <div class="tab-content" v-show="activeTab === 'description'">
        <div class="description-content">
          <h3>商品描述</h3>
          <p>{{ product.description }}</p>
          
          <h3 v-if="product.features">产品特点</h3>
          <ul v-if="product.features">
            <li v-for="(feature, index) in parseJson(product.features)" :key="index">{{ feature }}</li>
          </ul>

          <h3 v-if="product.specifications">规格参数</h3>
          <table class="specs-table" v-if="product.specifications">
            <tr v-for="(value, key) in parseJson(product.specifications)" :key="key">
              <td class="spec-key">{{ key }}</td>
              <td class="spec-value">{{ value }}</td>
            </tr>
          </table>
        </div>
      </div>

      <!-- 规格参数 -->
      <div class="tab-content" v-show="activeTab === 'specs'">
        <table class="specs-table full">
          <tr v-for="(value, key) in parseJson(product.specifications)" :key="key">
            <td class="spec-key">{{ key }}</td>
            <td class="spec-value">{{ value }}</td>
          </tr>
        </table>
      </div>

      <!-- 评价列表 -->
      <div class="tab-content" v-show="activeTab === 'reviews'">
        <div class="reviews-section">
          <div class="reviews-summary">
            <div class="rating">
              <span class="score">{{ product.rating || '5.0' }}</span>
              <span class="max">/5.0</span>
            </div>
            <div class="rating-stars">
              <span v-for="i in 5" :key="i" :class="{ filled: i <= Math.round(product.rating || 5) }">★</span>
            </div>
          </div>
          
          <div class="reviews-list" v-if="reviews.length > 0">
            <div class="review-item" v-for="review in reviews" :key="review.id">
              <div class="review-header">
                <img :src="review.avatar || '/static/images/default-avatar.png'" :alt="review.user_name"/>
                <span class="user-name">{{ review.user_name }}</span>
                <span class="review-date">{{ review.create_time }}</span>
              </div>
              <div class="review-content">{{ review.content }}</div>
              <div class="review-images" v-if="review.images">
                <img v-for="(img, index) in review.images" :key="index" :src="img" :alt="`评价图片${index + 1}`"/>
              </div>
            </div>
          </div>
          <div class="no-reviews" v-else>
            <p>暂无评价，期待您的购买体验！</p>
          </div>
        </div>
      </div>

      <!-- 推荐商品 -->
      <div class="tab-content" v-show="activeTab === 'recommend'">
        <div class="recommend-grid">
          <div 
            v-for="item in recommendedProducts" 
            :key="item.id"
            class="recommend-item"
            @click="goToProduct(item.id)"
          >
            <img :src="item.image_url || '/static/images/placeholder.png'" :alt="item.name"/>
            <h4>{{ item.name }}</h4>
            <span class="price">¥{{ item.price.toFixed(2) }}</span>
          </div>
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
    <p>商品不存在或已被删除</p>
    <router-link to="/shop">返回商城首页</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProductDetail } from '@/api/shop'

const route = useRoute()
const router = useRouter()

// 状态
const product = ref(null)
const loading = ref(false)
const error = ref(null)
const currentImage = ref('')
const quantity = ref(1)
const activeTab = ref('description')
const reviews = ref([])
const recommendedProducts = ref([])

// 标签页
const tabs = [
  { key: 'description', label: '商品介绍' },
  { key: 'specs', label: '规格参数' },
  { key: 'reviews', label: '评价' },
  { key: 'recommend', label: '为你推荐' }
]

// 获取商品详情
async function fetchProduct() {
  const productId = route.params.id
  loading.value = true
  error.value = null
  
  try {
    const response = await getProductDetail(productId)
    
    if (response.success) {
      product.value = response.data
      currentImage.value = product.value.image_url
      // 模拟评价和推荐数据
      reviews.value = product.value.reviews || []
      recommendedProducts.value = product.value.recommended_products || []
    } else {
      error.value = '商品不存在'
    }
  } catch (err) {
    console.error('获取商品详情失败:', err)
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
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

// 数量操作
function decreaseQuantity() {
  if (quantity.value > 1) quantity.value--
}

function increaseQuantity() {
  if (quantity.value < (product.value?.stock || 99)) quantity.value++
}

// 跳转到店铺
function goToMerchant(merchantId) {
  router.push(`/shop/merchant/${merchantId}`)
}

// 跳转到商品
function goToProduct(productId) {
  router.push(`/shop/product/${productId}`)
}

// 立即购买
function buyNow() {
  // TODO: 实现立即购买逻辑
  console.log('立即购买:', product.value.id, quantity.value)
}

// 加入购物车
function addToCart() {
  // TODO: 实现加入购物车逻辑
  console.log('加入购物车:', product.value.id, quantity.value)
}

// 监听路由参数变化
watch(() => route.params.id, () => {
  fetchProduct()
})

onMounted(() => {
  fetchProduct()
})
</script>

<style scoped>
.product-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
}

/* 商品主区域 */
.product-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}

/* 商品图片 */
.product-gallery {
  position: sticky;
  top: 20px;
}

.main-image {
  border-radius: 12px;
  overflow: hidden;
  background: #f8f8f8;
  margin-bottom: 15px;
}

.main-image img {
  width: 100%;
  height: 400px;
  object-fit: contain;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.thumbnail.active {
  border-color: #667eea;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 商品信息 */
.breadcrumb {
  display: flex;
  gap: 8px;
  font-size: 14px;
  color: #999;
  margin-bottom: 15px;
}

.breadcrumb a {
  color: #667eea;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.product-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 15px;
  line-height: 1.4;
}

.product-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #999;
  margin-bottom: 20px;
}

/* 价格区域 */
.price-section {
  background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.price-label {
  font-size: 14px;
  color: #999;
  margin-right: 10px;
}

.price {
  font-size: 36px;
  font-weight: bold;
  color: #e74c3c;
  margin-right: 15px;
}

.original-price {
  font-size: 18px;
  color: #999;
  text-decoration: line-through;
}

.sales-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

/* 商家信息 */
.merchant-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f8f8;
  border-radius: 12px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.merchant-info:hover {
  background: #f0f0f0;
}

.merchant-info img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.merchant-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.merchant-label {
  font-size: 12px;
  color: #999;
}

.merchant-name {
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.go-shop {
  color: #667eea;
  font-size: 14px;
}

/* 数量选择 */
.quantity-selector {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.quantity-selector .label {
  font-size: 14px;
  color: #666;
}

.quantity-control {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.quantity-control button {
  width: 40px;
  height: 40px;
  border: none;
  background: #f8f8f8;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.quantity-control button:hover:not(:disabled) {
  background: #667eea;
  color: #fff;
}

.quantity-control button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-control input {
  width: 60px;
  height: 40px;
  border: none;
  border-left: 1px solid #ddd;
  border-right: 1px solid #ddd;
  text-align: center;
  font-size: 16px;
}

.stock-tip {
  font-size: 12px;
  color: #e74c3c;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.action-buttons button {
  flex: 1;
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.buy-now {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.buy-now:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.add-cart {
  background: #fff;
  color: #667eea;
  border: 2px solid #667eea !important;
}

.add-cart:hover {
  background: #667eea;
  color: #fff;
}

/* 服务标签 */
.service-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.service-tags .tag {
  padding: 8px 15px;
  background: #f8f8f8;
  border-radius: 20px;
  font-size: 13px;
  color: #666;
}

/* 标签页 */
.product-tabs {
  border-top: 1px solid #f0f0f0;
  padding-top: 30px;
}

.tab-header {
  display: flex;
  border-bottom: 2px solid #f0f0f0;
  margin-bottom: 30px;
}

.tab-header button {
  padding: 15px 30px;
  border: none;
  background: none;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.tab-header button.active {
  color: #667eea;
  font-weight: 600;
}

.tab-header button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #667eea;
}

.tab-content {
  padding: 20px 0;
}

/* 描述内容 */
.description-content h3 {
  font-size: 18px;
  color: #333;
  margin: 25px 0 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.description-content h3:first-child {
  margin-top: 0;
}

.description-content p {
  line-height: 1.8;
  color: #666;
}

.description-content ul {
  padding-left: 20px;
}

.description-content li {
  line-height: 2;
  color: #666;
}

/* 规格表格 */
.specs-table {
  width: 100%;
  border-collapse: collapse;
}

.specs-table.full {
  max-width: 800px;
}

.specs-table tr {
  border-bottom: 1px solid #f0f0f0;
}

.specs-table td {
  padding: 12px 15px;
}

.spec-key {
  width: 150px;
  background: #f8f8f8;
  color: #666;
  font-weight: 500;
}

.spec-value {
  color: #333;
}

/* 评价区域 */
.reviews-summary {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #f8f8f8;
  border-radius: 12px;
  margin-bottom: 30px;
}

.rating {
  display: flex;
  align-items: baseline;
}

.rating .score {
  font-size: 48px;
  font-weight: bold;
  color: #e74c3c;
}

.rating .max {
  font-size: 18px;
  color: #999;
}

.rating-stars {
  font-size: 24px;
}

.rating-stars span {
  color: #ddd;
}

.rating-stars span.filled {
  color: #ffc107;
}

.review-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.review-header img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.review-date {
  color: #999;
  font-size: 14px;
}

.review-content {
  line-height: 1.6;
  color: #666;
  margin-bottom: 10px;
}

.review-images {
  display: flex;
  gap: 10px;
}

.review-images img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}

.no-reviews {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 推荐商品 */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.recommend-item {
  cursor: pointer;
  transition: all 0.3s;
}

.recommend-item:hover {
  transform: translateY(-5px);
}

.recommend-item img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 10px;
}

.recommend-item h4 {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-item .price {
  color: #e74c3c;
  font-weight: bold;
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
  .product-main {
    grid-template-columns: 1fr;
  }
  
  .product-gallery {
    position: static;
  }
  
  .main-image img {
    height: 300px;
  }
}
</style>
