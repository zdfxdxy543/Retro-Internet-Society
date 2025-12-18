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
