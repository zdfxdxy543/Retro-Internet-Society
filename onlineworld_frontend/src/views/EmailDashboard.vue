<template>
  <div class="email-dashboard">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="user-info">
        <h2>欢迎，{{ userInfo?.username || '用户' }}</h2>
        <p class="user-email">{{ userInfo?.email }}</p>
      </div>
      
      <nav class="nav-menu">
        <button 
          class="nav-item" 
          :class="{ active: activeTab === 'inbox' }" 
          @click="switchTab('inbox')"
        >
          <span class="nav-icon">📥</span>
          <span>收件箱</span>
          <span class="unread-count" v-if="unreadCount > 0">{{ unreadCount }}</span>
        </button>
        
        <button 
          class="nav-item" 
          :class="{ active: activeTab === 'sent' }" 
          @click="switchTab('sent')"
        >
          <span class="nav-icon">📤</span>
          <span>发件箱</span>
        </button>
        
        <button class="nav-item compose-btn" @click="navigateToCompose">
          <span class="nav-icon">✏️</span>
          <span>撰写邮件</span>
        </button>
      </nav>
      
      <div class="footer">
        <button class="logout-btn" @click="handleLogout">登出</button>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="content">
      <!-- 工具栏 -->
      <div class="toolbar">
        <h1>{{ activeTab === 'inbox' ? '收件箱' : '发件箱' }}</h1>
        <div class="toolbar-actions">
          <button class="refresh-btn" @click="loadEmails" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
          <button 
            class="compose-btn-header" 
            @click="navigateToCompose"
          >
            撰写邮件
          </button>
        </div>
      </div>
      
      <!-- 邮件列表 -->
      <div class="email-list" v-if="!loading">
        <div v-if="emails.length === 0" class="empty-state">
          <p>{{ activeTab === 'inbox' ? '没有新邮件' : '没有发送的邮件' }}</p>
        </div>
        
        <div 
          v-for="email in emails" 
          :key="email.id" 
          class="email-item" 
          :class="{ 'unread': !email.is_read }"
          @click="viewEmail(email.id)"
        >
          <div class="email-header">
            <span class="sender-name">
              {{ activeTab === 'inbox' ? email.sender_name : email.recipient_name }}
            </span>
            <span class="email-date">{{ formatDate(email.created_at) }}</span>
          </div>
          <div class="email-subject">{{ email.subject || '(无主题)' }}</div>
          <div class="email-preview">{{ truncateText(email.content, 100) }}</div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div class="loading-state" v-if="loading">
        <p>正在加载邮件...</p>
      </div>
      
      <!-- 错误提示 -->
      <div class="error-message" v-if="errorMessage">
        {{ errorMessage }}
        <button @click="clearError">关闭</button>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import emailService from '../api/email.js'

export default {
  name: 'EmailDashboard',
  setup() {
    // 状态管理
    const activeTab = ref('inbox')
    const loading = ref(false)
    const emails = ref([])
    const errorMessage = ref('')
    const userInfo = ref(null)
    const router = useRouter()
    
    // 计算未读邮件数量
    const unreadCount = computed(() => {
      return emails.value.filter(email => !email.is_read).length
    })
    
    // 加载用户信息
    const loadUserInfo = () => {
      const savedUserInfo = localStorage.getItem('userInfo')
      if (savedUserInfo) {
        try {
          userInfo.value = JSON.parse(savedUserInfo)
        } catch (e) {
          console.error('Failed to parse user info:', e)
        }
      }
    }
    
    // 检查登录状态
    const checkLoginStatus = async () => {
      try {
        // 调用API检查登录状态
        const response = await emailService.getStatus()
        // 登录状态由路由守卫统一处理，这里只需返回API的结果
        return response.data
      } catch (err) {
        console.error('检查登录状态失败:', err)
        // 不再清除localStorage，登录状态验证统一由路由守卫处理
        return { isLoggedIn: false }
      }
    }
    
    // 加载邮件列表
    const loadEmails = async () => {
      loading.value = true
      errorMessage.value = ''
      
      try {
        let response
        
        // 根据当前活动标签页选择加载收件箱或发件箱
        if (activeTab.value === 'inbox') {
          response = await emailService.getInbox()
        } else {
          response = await emailService.getOutbox()
        }
        
        emails.value = response.data.emails || []
      } catch (err) {
        console.error('加载邮件失败:', err)
        errorMessage.value = err.response?.data?.message || '加载邮件失败，请稍后重试'
        
        // 移除401错误处理，登录状态验证统一由路由守卫处理
      } finally {
        loading.value = false
      }
    }
    
    // 切换标签
    const switchTab = (tab) => {
      if (activeTab.value !== tab) {
        activeTab.value = tab
        loadEmails()
      }
    }
    
    // 查看邮件详情
    const viewEmail = (emailId) => {
      // 标记为已读（如果是收件箱的未读邮件）
      const email = emails.value.find(e => e.id === emailId)
      if (activeTab.value === 'inbox' && email && !email.is_read) {
        emailService.markAsRead(emailId).catch(err => {
          console.error('Failed to mark email as read:', err)
        })
        email.is_read = true
      }
      
      // 导航到邮件详情页
      router.push(`/email/view/${emailId}`)
    }
    
    // 跳转到撰写邮件页面
    const navigateToCompose = () => {
      router.push('/email/compose')
    }
    
    // 登出处理
    const handleLogout = async () => {
      try {
        await emailService.logout()
        localStorage.removeItem('userInfo')
        localStorage.removeItem('isLoggedIn')
        router.push('/email')
      } catch (error) {
        console.error('Logout error:', error)
        // 即使登出API调用失败，也清除本地存储并重定向
        localStorage.removeItem('userInfo')
        localStorage.removeItem('isLoggedIn')
        router.push('/email')
      }
    }
    
    // 清除错误消息
    const clearError = () => {
      errorMessage.value = ''
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      const now = new Date()
      const yesterday = new Date(now)
      yesterday.setDate(yesterday.getDate() - 1)
      
      // 同一天显示时间
      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      }
      
      // 昨天显示"昨天"
      if (date.toDateString() === yesterday.toDateString()) {
        return '昨天'
      }
      
      // 今年显示月日
      if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
      }
      
      // 其他情况显示完整日期
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
    }
    
    // 截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    // 组件挂载时执行
    onMounted(async () => {
      try {
        // 首先加载用户信息
        loadUserInfo();
        
        // 异步检查登录状态，但只记录错误，不执行重定向
        // 登录状态验证统一由路由守卫处理
        await checkLoginStatus().catch(err => {
          console.error('登录状态检查失败:', err);
        });
        
        // 只有在组件仍在dashboard页面时才加载邮件，避免跳转冲突
        if (router.currentRoute.value.path === '/email/dashboard') {
          await loadEmails();
        }
      } catch (err) {
        console.error('Dashboard初始化失败:', err);
      }
    });
    
    return {
      activeTab,
      loading,
      emails,
      errorMessage,
      userInfo,
      unreadCount,
      switchTab,
      loadEmails,
      viewEmail,
      navigateToCompose,
      handleLogout,
      clearError,
      formatDate,
      truncateText
    };
  }
}
</script>

<style scoped>
.email-dashboard {
  display: flex;
  height: calc(100vh - 80px); /* 减去导航栏高度 */
  background-color: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background-color: #fff;
  border-right: 1px solid #e1e4e8;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

.user-info {
  padding: 0 20px 20px;
  border-bottom: 1px solid #e1e4e8;
  margin-bottom: 10px;
}

.user-info h2 {
  margin: 0 0 5px;
  font-size: 18px;
  color: #333;
}

.user-email {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 10px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  border-radius: 0 20px 20px 0;
  transition: all 0.3s ease;
  font-size: 16px;
  color: #555;
  position: relative;
}

.nav-item:hover {
  background-color: #f0f4f8;
  color: #4a6bff;
}

.nav-item.active {
  background-color: #e6ebff;
  color: #4a6bff;
  font-weight: 500;
}

.nav-icon {
  margin-right: 12px;
  font-size: 18px;
}

.unread-count {
  margin-left: auto;
  background-color: #4a6bff;
  color: white;
  font-size: 12px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 12px;
  min-width: 20px;
  text-align: center;
}

.compose-btn {
  margin-top: 10px;
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  margin: 10px 20px;
}

.compose-btn:hover {
  background-color: #3a5aef;
}

.footer {
  padding: 20px;
  border-top: 1px solid #e1e4e8;
  margin-top: auto;
}

.logout-btn {
  width: 100%;
  padding: 10px;
  background-color: transparent;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background-color: #f8f9fa;
  color: #dc3545;
  border-color: #dc3545;
}

/* 主内容区样式 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
  background-color: white;
  border-bottom: 1px solid #e1e4e8;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.toolbar h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
}

.refresh-btn, .compose-btn-header {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.refresh-btn {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  color: #333;
}

.refresh-btn:hover {
  background-color: #e9ecef;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.compose-btn-header {
  background-color: #4a6bff;
  color: white;
  border: none;
}

.compose-btn-header:hover {
  background-color: #3a5aef;
}

/* 邮件列表样式 */
.email-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.email-item {
  display: flex;
  flex-direction: column;
  padding: 15px 25px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  background-color: white;
  transition: background-color 0.2s;
}

.email-item:hover {
  background-color: #f8f9fa;
}

.email-item.unread {
  background-color: #f0f4ff;
  font-weight: 500;
}

.email-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.sender-name {
  font-weight: 500;
  color: #333;
}

.email-date {
  font-size: 13px;
  color: #888;
}

.email-subject {
  margin-bottom: 5px;
  color: #333;
}

.email-preview {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 状态样式 */
.empty-state, .loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #888;
  font-size: 16px;
}

.error-message {
  margin: 20px;
  padding: 15px;
  background-color: #fff0f0;
  border: 1px solid #ffd6d6;
  border-radius: 4px;
  color: #d32f2f;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-message button {
  background: none;
  border: none;
  color: #d32f2f;
  cursor: pointer;
  font-size: 16px;
  margin-left: 10px;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .email-dashboard {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #e1e4e8;
  }
  
  .nav-menu {
    flex-direction: row;
    overflow-x: auto;
    padding: 10px;
  }
  
  .nav-item {
    padding: 10px 15px;
    border-radius: 20px;
    white-space: nowrap;
  }
  
  .compose-btn {
    margin: 10px;
  }
}
</style>







