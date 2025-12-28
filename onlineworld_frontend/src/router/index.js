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

// 邮箱功能路由守卫
const emailAuthGuard = (to, from, next) => {
  // 检查用户是否已登录（通过localStorage中的isLoggedIn标志）
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  
  // 如果用户未登录且试图访问需要认证的页面，重定向到登录页
  if (!isLoggedIn && to.path !== '/email/auth') {
    next({ path: '/email/auth' });
  } else if (isLoggedIn && to.path === '/email/auth') {
    // 如果用户已登录且访问登录页，重定向到仪表盘
    next({ path: '/email/dashboard' });
  } else {
    // 其他情况正常访问
    next();
  }
};

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
    path: '/shop/merchants',
    name: 'ShopMerchants',
    component: () => import('../views/ShopMerchants.vue'),
    meta: { title: '在线商城 - 商家列表' }
  },
  {
    path: '/shop/products',
    name: 'ShopProducts',
    component: () => import('../views/ShopProducts.vue'),
    meta: { title: '在线商城 - 商品列表' }
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
  },
  // 邮箱系统路由
  {
    path: '/email',
    name: 'EmailIndex',
    // 修改为直接渲染EmailAuth组件而不是重定向，解决404问题
    component: () => import('../views/EmailAuth.vue'),
    meta: { title: '在线邮箱 - 登录/注册' },
    beforeEnter: emailAuthGuard
  },
  {
    path: '/email/auth',
    name: 'EmailAuth',
    component: () => import('../views/EmailAuth.vue'),
    meta: { title: '在线邮箱 - 登录/注册' },
    beforeEnter: emailAuthGuard
  },
  {
    path: '/email/dashboard',
    name: 'EmailDashboard',
    component: () => import('../views/EmailDashboard.vue'),
    meta: { title: '在线邮箱 - 收件箱' },
    beforeEnter: emailAuthGuard
  },
  {
    path: '/email/compose',
    name: 'EmailCompose',
    component: () => import('../views/EmailCompose.vue'),
    meta: { title: '在线邮箱 - 撰写邮件' },
    beforeEnter: emailAuthGuard
  },
  {
    path: '/email/detail/:id',
    name: 'EmailDetail',
    component: () => import('../views/EmailDetail.vue'),
    meta: { title: '在线邮箱 - 邮件详情' },
    beforeEnter: emailAuthGuard,
    props: true
  },
  // 添加重定向路由，解决No match found for location问题
  {
    path: '/email/inbox',
    name: 'EmailInbox',
    redirect: '/email/dashboard',
    beforeEnter: emailAuthGuard
  },
  {
    path: '/email/outbox',
    name: 'EmailOutbox',
    redirect: '/email/dashboard',
    beforeEnter: emailAuthGuard
  },
  // 修复组件中使用的view路由路径
  {
    path: '/email/view/:id',
    name: 'EmailView',
    redirect: to => ({ path: `/email/detail/${to.params.id}` }),
    beforeEnter: emailAuthGuard
  }
]

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