import { createRouter, createWebHistory } from 'vue-router'
import Index from '../views/Index.vue'
import Board from '../views/Board.vue'
import Post from '../views/Post.vue'
import NewbieGuide from '../views/NewbieGuide.vue'
import Rules from '../views/Rules.vue'
import Contact from '../views/Contact.vue'
import DynamicPage from '../views/DynamicPage.vue'
import UserProfile from '../views/UserProfile.vue'
import SearchResult from '../views/SearchResult.vue'
// 导入公司网站视图组件
import CompanyIndex from '../views/CompanyIndex.vue'
import CompanyProducts from '../views/CompanyProducts.vue'
import CompanyProductDetail from '../views/CompanyProductDetail.vue'
import CompanyAbout from '../views/CompanyAbout.vue'
import CompanyContact from '../views/CompanyContact.vue'

const routes = [
  {
    path: '/',
    name: 'Index',
    component: Index,
    meta: { title: '复古论坛 - 首页' }
  },
  {
    path: '/board/:boardId',
    name: 'Board',
    component: Board,
    meta: { title: '复古论坛 - 板块' }
  },
  {
    path: '/post/:postId',
    name: 'Post',
    component: Post,
    meta: { title: '复古论坛 - 帖子详情' }
  },
  {
    path: '/user/:author',
    name: 'UserProfile',
    component: UserProfile,
    meta: { title: '复古论坛 - 个人主页' }
  },
  {
    path: '/search',
    name: 'SearchResult',
    component: SearchResult,
    meta: { title: '复古论坛 - 搜索结果' }
  },
  {
    path: '/newbie',
    name: 'NewbieGuide',
    component: NewbieGuide,
    meta: { title: '复古论坛 - 新人指南' }
  },
  {
    path: '/rules',
    name: 'Rules',
    component: Rules,
    meta: { title: '复古论坛 - 版规说明' }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: Contact,
    meta: { title: '复古论坛 - 联系我们' }
  },
  {
    path: '/page/:slug',
    name: 'DynamicPage',
    component: DynamicPage,
    meta: { title: '复古论坛 - 动态页面' }
  },
  // 公司网站路由
  {
    path: '/company',
    name: 'CompanyIndex',
    component: CompanyIndex,
    meta: { title: '未来科技有限公司 - 首页' }
  },
  {
    path: '/company/products',
    name: 'CompanyProducts',
    component: CompanyProducts,
    meta: { title: '未来科技有限公司 - 产品中心' }
  },
  {
    path: '/company/product/:productId',
    name: 'CompanyProductDetail',
    component: CompanyProductDetail,
    meta: { title: '未来科技有限公司 - 产品详情' }
  },
  {
    path: '/company/about',
    name: 'CompanyAbout',
    component: CompanyAbout,
    meta: { title: '未来科技有限公司 - 关于我们' }
  },
  {
    path: '/company/contact',
    name: 'CompanyContact',
    component: CompanyContact,
    meta: { title: '未来科技有限公司 - 联系我们' }
  },
  // AI地图路由
  { path: '/town-map',
    name: 'AIMapIndex',
    component: () => import('../views/AIMapIndex.vue'),
    meta: { title: '小镇地图' }
  },
  // 商城路由
  {
    path: '/shop',
    name: 'ShopIndex',
    component: () => import('../views/ShopIndex.vue'),
    meta: { title: '在线商城 - 首页' }
  },
  {
    path: '/shop/category/:categoryId',
    name: 'ShopCategory',
    component: () => import('../views/ShopCategory.vue'),
    meta: { title: '在线商城 - 商品分类' }
  },
  {
    path: '/shop/product/:id',
    name: 'ShopProductDetail',
    component: () => import('../views/ShopProductDetail.vue'),
    meta: { title: '在线商城 - 商品详情' }
  },
  {
    path: '/shop/merchant/:id',
    name: 'ShopMerchantDetail',
    component: () => import('../views/ShopMerchantDetail.vue'),
    meta: { title: '在线商城 - 商家详情' }
  }
]

// 删除重复的路由定义
// const companyRoutes = [
//   { path: '/company', component: () => import('@/views/company/CompanyIndex.vue') },
//   { path: '/company/products', component: () => import('@/views/company/ProductList.vue') },
//   { path: '/company/products/:id', component: () => import('@/views/company/ProductDetail.vue') },
//   { path: '/company/contact', component: () => import('@/views/company/Contact.vue') },
//   { path: '/company/about', component: () => import('@/views/company/About.vue') }
// ];

// const aiMapRoutes = [
//   { path: '/ai-map', component: () => import('@/views/ai_map/AIMapIndex.vue') },
//   { path: '/ai-map/region/:id', component: () => import('@/views/ai_map/AIMapRegionDetail.vue') },
//   { path: '/ai-map/ai/:id', component: () => import('@/views/ai_map/AIMapAIDetail.vue') }
// ];

// const routes = [...forumRoutes, ...companyRoutes, ...aiMapRoutes];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(){
    return {top:0}
  }
})

router.afterEach((to, from) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
})

export default router