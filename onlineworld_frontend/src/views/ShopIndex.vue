<template>
  <div class="shop-index">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchKeyword" 
          placeholder="搜索商品名称、描述..."
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch">
          <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          搜索
        </button>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <div 
        v-for="category in (categories.length > 0 ? categories : [
          { id: 1, name: '热门商品', image_url: '' },
          { id: 2, name: '新品上市', image_url: '' },
          { id: 3, name: '精选推荐', image_url: '' },
          { id: 4, name: '限时折扣', image_url: '' }
        ])" 
        :key="category.id"
        class="category-item"
        :class="{ active: selectedCategory === category.id }"
        @click="selectCategory(category.id)"
      >
        <img v-if="category.image_url" :src="category.image_url" :alt="category.name" class="category-icon"/>
        <span>{{ category.name }}</span>
      </div>
    </div>

    <!-- 横幅广告 -->
    <div class="banner-section" v-if="featuredProducts.length > 0">
      <div class="banner-slider">
        <div 
          v-for="(product, index) in featuredProducts" 
          :key="product.id"
          class="banner-item"
          :class="{ active: currentBanner === index }"
          @click="goToProduct(product.id)"
        >
          <img :src="product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
          <div class="banner-info">
            <h3>{{ product.name }}</h3>
            <p>{{ truncateText(product.description, 80) }}</p>
            <span class="price">¥{{ product.price.toFixed(2) }}</span>
          </div>
        </div>
      </div>
      <div class="banner-dots">
        <span 
          v-for="(product, index) in featuredProducts" 
          :key="index"
          :class="{ active: currentBanner === index }"
          @click="currentBanner = index"
        ></span>
      </div>
    </div>

    <!-- 热门商品 -->
    <section class="section" v-if="hotProducts.length > 0">
      <div class="section-header">
        <h2>🔥 热门商品</h2>
        <router-link to="/shop/products?sort=hot" class="more-link">查看更多 ></router-link>
      </div>
      <div class="product-grid">
        <div 
          v-for="product in hotProducts" 
          :key="product.id"
          class="product-card"
          @click="goToProduct(product.id)"
        >
          <div class="product-image">
            <img :src="product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
            <span class="hot-badge">热卖</span>
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

    <!-- 商家推荐 -->
    <section class="section" v-if="(merchants.length > 0 ? merchants : [
      { id: 1, name: '优质商家1', logo_url: '', description: '提供优质商品和服务', product_count: 20, rating: 4.8 },
      { id: 2, name: '优质商家2', logo_url: '', description: '品质保证，值得信赖', product_count: 15, rating: 4.7 },
      { id: 3, name: '优质商家3', logo_url: '', description: '新品不断，优惠多多', product_count: 30, rating: 4.9 },
      { id: 4, name: '优质商家4', logo_url: '', description: '专业服务，客户至上', product_count: 12, rating: 4.6 }
    ]).length > 0">
      <div class="section-header">
        <h2>🏪 推荐商家</h2>
        <router-link to="/shop/merchants" class="more-link">查看更多 ></router-link>
      </div>
      <div class="merchant-grid">
        <div 
          v-for="merchant in (merchants.length > 0 ? merchants : [
            { id: 1, name: '优质商家1', logo_url: '', description: '提供优质商品和服务', product_count: 20, rating: 4.8 },
            { id: 2, name: '优质商家2', logo_url: '', description: '品质保证，值得信赖', product_count: 15, rating: 4.7 },
            { id: 3, name: '优质商家3', logo_url: '', description: '新品不断，优惠多多', product_count: 30, rating: 4.9 },
            { id: 4, name: '优质商家4', logo_url: '', description: '专业服务，客户至上', product_count: 12, rating: 4.6 }
          ]).slice(0, 4)" 
          :key="merchant.id"
          class="merchant-card"
          @click="goToMerchant(merchant.id)"
        >
          <img :src="merchant.logo_url || '/static/images/placeholder.png'" :alt="merchant.name" class="merchant-logo"/>
          <div class="merchant-info">
            <h3>{{ merchant.name }}</h3>
            <p class="merchant-desc">{{ truncateText(merchant.description, 40) }}</p>
            <div class="merchant-stats">
              <span>商品数: {{ merchant.product_count || 0 }}</span>
              <span>评分: {{ merchant.rating || '5.0' }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 所有分类商品 -->
    <section class="section" v-for="category in categories" :key="category.id">
      <div class="section-header">
        <h2>📦 {{ category.name }}</h2>
        <router-link :to="`/shop/category/${category.id}`" class="more-link">查看更多 ></router-link>
      </div>
      <div class="product-grid">
        <div 
          v-for="product in getProductsByCategory(category.id)" 
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
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 新品推荐 -->
    <section class="section" v-if="newProducts.length > 0">
      <div class="section-header">
        <h2>🆕 新品上市</h2>
        <router-link to="/shop/products?sort=new" class="more-link">查看更多 ></router-link>
      </div>
      <div class="product-grid">
        <div 
          v-for="product in newProducts" 
          :key="product.id"
          class="product-card"
          @click="goToProduct(product.id)"
        >
          <div class="product-image">
            <img :src="product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
            <span class="new-badge">新品</span>
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="merchant-name">{{ product.merchant_name }}</p>
            <div class="product-bottom">
              <span class="price">¥{{ product.price.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 推荐商品 -->
    <section class="section" v-if="recommendedProducts.length > 0">
      <div class="section-header">
        <h2>🌟 推荐商品</h2>
        <router-link to="/shop/products?sort=recommended" class="more-link">查看更多 ></router-link>
      </div>
      <div class="product-grid">
        <div 
          v-for="product in recommendedProducts" 
          :key="product.id"
          class="product-card"
          @click="goToProduct(product.id)"
        >
          <div class="product-image">
            <img :src="product.image_url || '/static/images/placeholder.png'" :alt="product.name"/>
            <span class="hot-badge">推荐</span>
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="merchant-name">{{ product.merchant_name }}</p>
            <div class="product-bottom">
              <span class="price">¥{{ product.price.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getShopIndex, getCategories, getMerchants, getProducts } from '@/api/shop'

const router = useRouter()

// 数据
const categories = ref([])
const merchants = ref([])
const products = ref([])
const hotProducts = ref([])
const newProducts = ref([])
const featuredProducts = ref([])
const recommendedProducts = ref([])
const searchKeyword = ref('')
const selectedCategory = ref(null)
const currentBanner = ref(0)
const loading = ref(false)

// 获取商城数据
async function fetchData() {
  console.log('=== 开始加载商城数据 ===')
  loading.value = true
  try {
    // 并行请求所有数据，使用allSettled确保即使部分请求失败，其他请求仍然会执行
    console.log('1. 开始发起API请求...')
    const [indexRes, categoriesRes, merchantsRes, productsRes, hotRes, recommendRes] = await Promise.allSettled([
      getShopIndex(),
      getCategories(),
      getMerchants(),
      getProducts({ limit: 20 }),
      getProducts({ sort: 'hot', limit: 8 }),
      getProducts({ sort: 'recommended', limit: 4 })
    ])

    console.log('2. API请求完成，结果状态:', {
      indexRes: indexRes.status,
      categoriesRes: categoriesRes.status,
      merchantsRes: merchantsRes.status,
      productsRes: productsRes.status,
      hotRes: hotRes.status,
      recommendRes: recommendRes.status
    })
    
    // 详细记录每个请求的结果
    if (indexRes.status === 'fulfilled') {
      console.log('2.1 首页API响应数据:', indexRes.value)
    } else {
      console.error('2.1 首页API请求失败:', indexRes.reason)
    }
    
    if (categoriesRes.status === 'fulfilled') {
      console.log('2.2 分类API响应数据:', categoriesRes.value)
    } else {
      console.error('2.2 分类API请求失败:', categoriesRes.reason)
    }
    
    if (merchantsRes.status === 'fulfilled') {
      console.log('2.3 商家API响应数据:', merchantsRes.value)
    } else {
      console.error('2.3 商家API请求失败:', merchantsRes.reason)
    }

    // 处理首页数据 - 增加更健壮的错误处理
    console.log('3. 开始处理首页数据...')
    if (indexRes.status === 'fulfilled') {
      try {
        const indexData = indexRes.value
        console.log('3.1 首页API响应原始数据:', indexData)
        
        if (indexData?.success) {
          console.log('3.3 数据获取成功，开始提取各部分数据...')
          
          const data = indexData?.data
          console.log('3.2 首页API响应.data:', data)
          
          // 从首页数据中获取分类
          if (Array.isArray(data?.categories)) {
            categories.value = data.categories
            console.log('3.4.1 从首页数据获取分类:', categories.value)
          } else {
            console.log('3.4.1 首页数据中没有有效的分类信息:', data?.categories)
          }
          
          // 从首页数据中获取商家
          if (Array.isArray(data?.top_merchants)) {
            merchants.value = data.top_merchants
            console.log('3.4.2 从首页数据获取商家:', merchants.value)
          } else {
            console.log('3.4.2 首页数据中没有有效的商家信息:', data?.top_merchants)
          }
          
          // 从首页数据中获取商品
          if (Array.isArray(data?.latest_products)) {
            // 使用最新商品作为热门商品和新品
            hotProducts.value = data.latest_products.slice(0, 8)
            newProducts.value = data.latest_products.slice(0, 4)
            recommendedProducts.value = data.latest_products.slice(4, 8)
            products.value = data.latest_products
            console.log('3.4.3 从首页数据获取最新商品:', data.latest_products)
            console.log('3.4.3.1 设置热门商品:', hotProducts.value)
            console.log('3.4.3.2 设置新品:', newProducts.value)
            console.log('3.4.3.3 设置推荐商品:', recommendedProducts.value)
          } else {
            console.log('3.4.3 首页数据中没有有效的最新商品信息:', data?.latest_products)
          }
          
          // 从首页数据中获取精选商品
          if (Array.isArray(data?.featured_products)) {
            featuredProducts.value = data.featured_products
            console.log('3.4.4 从首页数据获取精选商品:', featuredProducts.value)
          } else {
            console.log('3.4.4 首页数据中没有有效的精选商品信息:', data?.featured_products)
          }
        } else {
          console.log('3.3 数据获取失败，success为false:', indexData?.success)
        }
      } catch (error) {
        console.error('3.5 处理首页数据失败:', error)
      }
    } else {
      console.log('3.0 首页API请求失败:', indexRes.reason)
    }

    // 处理分类数据 - 确保categories是数组
    if (categoriesRes.status === 'fulfilled') {
      try {
        const categoriesData = categoriesRes.value
        console.log('分类API数据:', categoriesData)
        if (categoriesData?.success && Array.isArray(categoriesData.data) && categoriesData.data.length > 0) {
          categories.value = categoriesData.data
          console.log('从分类API获取分类:', categories.value)
        } else {
          console.log('分类API返回的数据为空或格式不正确，保留原有分类数据:', categories.value)
        }
      } catch (error) {
        console.error('处理分类数据失败，保留原有分类数据:', error)
      }
    } else {
      console.log('分类API请求失败，保留原有分类数据:', categoriesRes.reason)
    }

    // 如果分类数据为空，添加默认分类
    console.log('检查分类数据:', categories.value)
    if (!Array.isArray(categories.value) || categories.value.length === 0) {
      console.log('分类数据为空，使用默认分类')
      categories.value = [
        { id: 1, name: '热门商品', image_url: '' },
        { id: 2, name: '新品上市', image_url: '' },
        { id: 3, name: '精选推荐', image_url: '' },
        { id: 4, name: '限时折扣', image_url: '' }
      ]
      console.log('设置默认分类:', categories.value)
    }

    // 处理商家数据 - 确保merchants是数组
    if (merchantsRes.status === 'fulfilled') {
      try {
        const merchantsData = merchantsRes.value
        console.log('商家API数据:', merchantsData)
        if (merchantsData?.success && Array.isArray(merchantsData.data)) {
          merchants.value = merchantsData.data
          console.log('从商家API获取商家:', merchants.value)
        }
      } catch (error) {
        console.error('处理商家数据失败:', error)
      }
    }

    // 如果商家数据为空，添加默认商家
    console.log('检查商家数据:', merchants.value)
    if (!Array.isArray(merchants.value) || merchants.value.length === 0) {
      console.log('商家数据为空，使用默认商家')
      merchants.value = [
        { id: 1, name: '优质商家1', logo_url: '', description: '提供优质商品和服务', product_count: 20, rating: 4.8 },
        { id: 2, name: '优质商家2', logo_url: '', description: '品质保证，值得信赖', product_count: 15, rating: 4.7 },
        { id: 3, name: '优质商家3', logo_url: '', description: '新品不断，优惠多多', product_count: 30, rating: 4.9 },
        { id: 4, name: '优质商家4', logo_url: '', description: '专业服务，客户至上', product_count: 12, rating: 4.6 }
      ]
      console.log('设置默认商家:', merchants.value)
    }

    // 处理商品数据 - 确保products是数组
    let allProducts = []
    if (productsRes.status === 'fulfilled') {
      try {
        const productsData = productsRes.value
        console.log('商品API数据:', productsData)
        if (productsData?.success && Array.isArray(productsData.data)) {
          allProducts = productsData.data
          products.value = productsData.data
          console.log('从商品API获取商品:', allProducts)
        }
      } catch (error) {
        console.error('处理商品数据失败:', error)
      }
    }

    // 如果商品数据为空，添加默认商品
    console.log('检查商品数据:', allProducts)
    if (!Array.isArray(allProducts) || allProducts.length === 0) {
      console.log('商品数据为空，使用默认商品')
      allProducts = [
        { id: 1, name: '示例商品1', price: 99.99, image_url: '', category_id: 1, merchant_name: '优质商家1', sales_count: 120 },
        { id: 2, name: '示例商品2', price: 199.99, image_url: '', category_id: 2, merchant_name: '优质商家2', sales_count: 80 },
        { id: 3, name: '示例商品3', price: 299.99, image_url: '', category_id: 3, merchant_name: '优质商家3', sales_count: 150 },
        { id: 4, name: '示例商品4', price: 399.99, image_url: '', category_id: 4, merchant_name: '优质商家4', sales_count: 60 },
        { id: 5, name: '示例商品5', price: 499.99, image_url: '', category_id: 1, merchant_name: '优质商家1', sales_count: 200 },
        { id: 6, name: '示例商品6', price: 599.99, image_url: '', category_id: 2, merchant_name: '优质商家2', sales_count: 90 },
        { id: 7, name: '示例商品7', price: 699.99, image_url: '', category_id: 3, merchant_name: '优质商家3', sales_count: 180 },
        { id: 8, name: '示例商品8', price: 799.99, image_url: '', category_id: 4, merchant_name: '优质商家4', sales_count: 70 },
        { id: 9, name: '示例商品9', price: 899.99, image_url: '', category_id: 1, merchant_name: '优质商家1', sales_count: 130 },
        { id: 10, name: '示例商品10', price: 999.99, image_url: '', category_id: 2, merchant_name: '优质商家2', sales_count: 110 }
      ]
      products.value = allProducts
      console.log('设置默认商品:', allProducts)
    }

    // 处理热门商品数据
    if (hotRes.status === 'fulfilled') {
      try {
        const hotData = hotRes.value
        console.log('热门商品API数据:', hotData)
        if (hotData?.success && Array.isArray(hotData.data)) {
          hotProducts.value = hotData.data
          console.log('从热门商品API获取热门商品:', hotProducts.value)
        }
      } catch (error) {
        console.error('处理热门商品数据失败:', error)
      }
    }

    // 如果没有获取到热门商品，从商品列表中取前几个作为热门
    console.log('检查热门商品数据:', hotProducts.value)
    if (!Array.isArray(hotProducts.value) || hotProducts.value.length === 0) {
      console.log('热门商品数据为空，从商品列表中取前几个作为热门')
      hotProducts.value = allProducts.slice(0, 8)
      console.log('设置热门商品:', hotProducts.value)
    }

    // 处理推荐商品数据
    if (recommendRes.status === 'fulfilled') {
      try {
        const recommendData = recommendRes.value
        console.log('推荐商品API数据:', recommendData)
        if (recommendData?.success && Array.isArray(recommendData.data)) {
          recommendedProducts.value = recommendData.data
          console.log('从推荐商品API获取推荐商品:', recommendedProducts.value)
        }
      } catch (error) {
        console.error('处理推荐商品数据失败:', error)
      }
    }

    // 如果没有获取到推荐商品，从商品列表中取前几个作为推荐
    console.log('检查推荐商品数据:', recommendedProducts.value)
    if (!Array.isArray(recommendedProducts.value) || recommendedProducts.value.length === 0) {
      console.log('推荐商品数据为空，从商品列表中取前几个作为推荐')
      recommendedProducts.value = allProducts.slice(0, 4)
      console.log('设置推荐商品:', recommendedProducts.value)
    }

    // 处理精选商品 - 如果没有获取到精选商品，从商品列表中取前几个作为精选
    console.log('检查精选商品数据:', featuredProducts.value)
    if (!Array.isArray(featuredProducts.value) || featuredProducts.value.length === 0) {
      console.log('精选商品数据为空，从商品列表中取前几个作为精选')
      featuredProducts.value = allProducts.slice(0, 3)
      console.log('设置精选商品:', featuredProducts.value)
    }

    // 处理新品数据
    console.log('检查新品数据:', newProducts.value)
    if (!Array.isArray(newProducts.value) || newProducts.value.length === 0) {
      console.log('新品数据为空，从商品列表中取前几个作为新品')
      newProducts.value = allProducts.slice(0, 4)
      console.log('设置新品:', newProducts.value)
    }
  } catch (error) {
    console.error('获取商城数据失败:', error)
    // 发生严重错误时，设置默认数据
    setDefaultData()
  } finally {
    loading.value = false
  }
}

// 设置默认数据，确保页面至少能显示一些内容
function setDefaultData() {
  console.log('开始设置默认数据')
  
  categories.value = [
    { id: 1, name: '热门商品', image_url: '' },
    { id: 2, name: '新品上市', image_url: '' },
    { id: 3, name: '精选推荐', image_url: '' },
    { id: 4, name: '限时折扣', image_url: '' }
  ]
  console.log('设置默认分类:', categories.value)

  merchants.value = [
    { id: 1, name: '优质商家1', logo_url: '', description: '提供优质商品和服务', product_count: 20, rating: 4.8 },
    { id: 2, name: '优质商家2', logo_url: '', description: '品质保证，值得信赖', product_count: 15, rating: 4.7 },
    { id: 3, name: '优质商家3', logo_url: '', description: '新品不断，优惠多多', product_count: 30, rating: 4.9 },
    { id: 4, name: '优质商家4', logo_url: '', description: '专业服务，客户至上', product_count: 12, rating: 4.6 }
  ]
  console.log('设置默认商家:', merchants.value)

  const defaultProducts = [
    { id: 1, name: '示例商品1', price: 99.99, image_url: '', category_id: 1, merchant_name: '优质商家1', sales_count: 120 },
    { id: 2, name: '示例商品2', price: 199.99, image_url: '', category_id: 2, merchant_name: '优质商家2', sales_count: 80 },
    { id: 3, name: '示例商品3', price: 299.99, image_url: '', category_id: 3, merchant_name: '优质商家3', sales_count: 150 },
    { id: 4, name: '示例商品4', price: 399.99, image_url: '', category_id: 4, merchant_name: '优质商家4', sales_count: 60 },
    { id: 5, name: '示例商品5', price: 499.99, image_url: '', category_id: 1, merchant_name: '优质商家1', sales_count: 200 },
    { id: 6, name: '示例商品6', price: 599.99, image_url: '', category_id: 2, merchant_name: '优质商家2', sales_count: 90 },
    { id: 7, name: '示例商品7', price: 699.99, image_url: '', category_id: 3, merchant_name: '优质商家3', sales_count: 180 },
    { id: 8, name: '示例商品8', price: 799.99, image_url: '', category_id: 4, merchant_name: '优质商家4', sales_count: 70 }
  ]

  products.value = defaultProducts
  hotProducts.value = defaultProducts.slice(0, 8)
  newProducts.value = defaultProducts.slice(0, 4)
  featuredProducts.value = defaultProducts.slice(0, 3)
  recommendedProducts.value = defaultProducts.slice(0, 4)
  
  console.log('设置默认商品:', defaultProducts)
  console.log('设置默认热门商品:', hotProducts.value)
  console.log('设置默认新品:', newProducts.value)
  console.log('设置默认精选商品:', featuredProducts.value)
  console.log('设置默认推荐商品:', recommendedProducts.value)
}

// 根据分类获取商品
function getProductsByCategory(categoryId) {
  return products.value
    .filter(p => p.category_id === categoryId)
    .slice(0, 4)
}

// 选择分类
function selectCategory(categoryId) {
  selectedCategory.value = categoryId
  router.push(`/shop/category/${categoryId}`)
}

// 搜索
function handleSearch() {
  if (searchKeyword.value.trim()) {
    router.push(`/shop/products?keyword=${encodeURIComponent(searchKeyword.value)}`)
  }
}

// 监控分类数据变化，用于调试
watch(categories, (newVal, oldVal) => {
  console.log('=== 分类数据变化监控 ===')
  console.log('旧分类数据:', oldVal)
  console.log('新分类数据:', newVal)
  console.log('分类数量:', newVal.length)
}, { deep: true })

// 跳转到商品详情
function goToProduct(productId) {
  router.push(`/shop/product/${productId}`)
}

// 跳转到商家详情
function goToMerchant(merchantId) {
  router.push(`/shop/merchant/${merchantId}`)
}

// 截断文本
function truncateText(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 自动轮播
let bannerInterval = null
onMounted(() => {
  fetchData()
  
  // 自动轮播
  bannerInterval = setInterval(() => {
    if (featuredProducts.value.length > 1) {
      currentBanner.value = (currentBanner.value + 1) % featuredProducts.value.length
    }
  }, 4000)
})
</script>

<style scoped>
.shop-index {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 搜索栏 */
.search-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px 20px;
}

.search-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 10px;
}

.search-container input {
  flex: 1;
  padding: 15px 20px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.search-container button {
  padding: 15px 30px;
  background: #fff;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.search-container button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.search-icon {
  width: 20px;
  height: 20px;
}

/* 分类导航 */
.category-nav {
  background: #fff;
  padding: 15px 20px;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.category-item {
  padding: 10px 20px;
  background: #f8f8f8;
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-item:hover {
  background: #667eea;
  color: #fff;
}

.category-item.active {
  background: #667eea;
  color: #fff;
}

.category-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

/* 横幅 */
.banner-section {
  margin: 20px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.banner-slider {
  position: relative;
  height: 300px;
}

.banner-item {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  opacity: 0;
  transition: opacity 0.5s;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.banner-item.active {
  opacity: 1;
}

.banner-item img {
  width: 50%;
  height: 100%;
  object-fit: cover;
}

.banner-info {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #fff;
}

.banner-info h3 {
  font-size: 28px;
  margin-bottom: 15px;
}

.banner-info p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
  line-height: 1.6;
}

.banner-info .price {
  font-size: 32px;
  font-weight: bold;
  color: #ffd700;
}

.banner-dots {
  position: absolute;
  bottom: 15px;
  right: 20px;
  display: flex;
  gap: 8px;
}

.banner-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
}

.banner-dots span.active {
  background: #fff;
  transform: scale(1.2);
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

.more-link {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.more-link:hover {
  text-decoration: underline;
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

.hot-badge,
.new-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
}

.hot-badge {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: #fff;
}

.new-badge {
  background: linear-gradient(135deg, #00b894, #00cec9);
  color: #fff;
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

/* 商家网格 */
.merchant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.merchant-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 15px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.merchant-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.merchant-logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.merchant-info h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
}

.merchant-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
  line-height: 1.4;
}

.merchant-stats {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}
</style>