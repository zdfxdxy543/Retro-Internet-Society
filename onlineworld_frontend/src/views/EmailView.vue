<template>
  <div class="email-view-container">
    <!-- 顶部导航栏 -->
    <div class="email-view-header">
      <button class="back-btn" @click="goBack">
        <span class="back-arrow">←</span> 返回列表
      </button>
      <div class="action-buttons">
        <button 
          class="action-btn" 
          @click="toggleStarred"
          :title="email.starred ? '取消星标' : '添加星标'"
        >
          {{ email.starred ? '★' : '☆' }}
        </button>
        <button 
          class="action-btn"
          @click="replyEmail"
          title="回复"
        >
          ↩️ 回复
        </button>
        <button 
          class="action-btn delete-btn"
          @click="confirmDelete"
          title="删除"
        >
          🗑️ 删除
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载邮件中...</div>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadEmail">重试</button>
    </div>
    
    <!-- 邮件内容 -->
    <div v-else class="email-content-container">
      <div class="email-meta-info">
        <h1 class="email-subject">{{ email.subject || '(无主题)' }}</h1>
        <div class="sender-info">
          <div class="sender-row">
            <span class="meta-label">发件人:</span>
            <span class="meta-value">{{ email.sender_name }} <{{ email.sender_email }}></span>
          </div>
          <div class="recipient-row">
            <span class="meta-label">收件人:</span>
            <span class="meta-value">{{ email.recipient_name }} <{{ email.recipient_email }}></span>
          </div>
          <div class="date-row">
            <span class="meta-label">日期:</span>
            <span class="meta-value">{{ formatFullDate(email.created_at) }}</span>
          </div>
        </div>
      </div>
      
      <div class="email-content">
        <div v-html="formatContent(email.content)"></div>
      </div>
      
      <!-- 附件区域 (可选功能) -->
      <div v-if="email.attachments && email.attachments.length > 0" class="attachments-section">
        <h3>附件:</h3>
        <ul class="attachment-list">
          <li v-for="(attachment, index) in email.attachments" :key="index" class="attachment-item">
            <span class="attachment-name">📎 {{ attachment.name }}</span>
            <span class="attachment-size">{{ formatFileSize(attachment.size) }}</span>
            <button class="download-btn">下载</button>
          </li>
        </ul>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="delete-modal">
      <div class="modal-content">
        <h3>确认删除</h3>
        <p>确定要删除这封邮件吗？此操作无法撤销。</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showDeleteConfirm = false">取消</button>
          <button class="confirm-btn" @click="deleteEmail">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import emailService from '../api/email.js'

export default {
  name: 'EmailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 状态管理
    const loading = ref(true)
    const errorMessage = ref('')
    const email = ref({
      id: null,
      sender_id: '',
      sender_name: '',
      sender_email: '',
      recipient_id: '',
      recipient_name: '',
      recipient_email: '',
      subject: '',
      content: '',
      is_read: false,
      starred: false,
      created_at: '',
      attachments: []
    })
    const showDeleteConfirm = ref(false)
    
    // 加载邮件详情
    const loadEmail = async () => {
      const emailId = route.params.id
      if (!emailId) {
        errorMessage.value = '无效的邮件ID'
        loading.value = false
        return
      }
      
      loading.value = true
      errorMessage.value = ''
      
      try {
        // 获取邮件详情
        const response = await emailService.getEmailDetail(emailId)
        
        // 如果邮件存在，则更新数据
        if (response.data && response.data.email) {
          email.value = response.data.email
          
          // 如果是未读邮件，则标记为已读
          if (!email.value.is_read) {
            await emailService.markAsRead(emailId)
            email.value.is_read = true
          }
        } else {
          errorMessage.value = '邮件不存在或已被删除'
        }
      } catch (err) {
        console.error('加载邮件失败:', err)
        errorMessage.value = err.response?.data?.message || '加载邮件失败，请稍后重试'
        
        // 移除401错误处理，登录状态验证统一由路由守卫处理
      } finally {
        loading.value = false
      }
    }
    
    // 切换星标状态
    const toggleStarred = async () => {
      try {
        await emailService.toggleStarred(email.value.id)
        // 本地更新星标状态
        email.value.starred = !email.value.starred
      } catch (err) {
        console.error('Failed to toggle starred status:', err)
        alert('更新星标状态失败')
      }
    }
    
    // 回复邮件
    const replyEmail = () => {
      // 跳转到撰写邮件页面，并带上回复信息
      router.push({
        path: '/email/compose',
        query: {
          replyTo: email.value.sender_email,
          replyToName: email.value.sender_name,
          subject: email.value.subject.startsWith('Re:') ? email.value.subject : `Re: ${email.value.subject}`,
          reference: email.value.id
        }
      })
    }
    
    // 确认删除对话框
    const confirmDelete = () => {
      showDeleteConfirm.value = true
    }
    
    // 删除邮件
    const deleteEmail = async () => {
      try {
        await emailService.deleteEmail(email.value.id)
        showDeleteConfirm.value = false
        // 删除成功后返回邮件列表
        goBack()
      } catch (err) {
        console.error('Failed to delete email:', err)
        alert('删除邮件失败')
        showDeleteConfirm.value = false
      }
    }
    
    // 返回邮件列表
    const goBack = () => {
      // 获取来源页面，优先返回之前的标签页状态
      const fromTab = localStorage.getItem('emailLastTab') || 'inbox'
      router.push(`/email/dashboard?tab=${fromTab}`)
    }
    
    // 格式化完整日期
    const formatFullDate = (dateString) => {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 格式化邮件内容（简单的HTML格式化）
    const formatContent = (content) => {
      if (!content) return ''
      
      // 将换行符转换为<br>
      // 简单处理链接和图片（这里仅做示例，实际应用中可能需要更复杂的处理）
      return content
        .replace(/\n/g, '<br>')
        .replace(/\n\n/g, '<p></p>')
    }
    
    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    // 监听路由参数变化，重新加载邮件
    watch(() => route.params.id, (newId) => {
      if (newId) {
        loadEmail()
      }
    })
    
    // 组件挂载时加载邮件
    onMounted(() => {
      loadEmail()
    })
    
    return {
      loading,
      errorMessage,
      email,
      showDeleteConfirm,
      loadEmail,
      toggleStarred,
      replyEmail,
      confirmDelete,
      deleteEmail,
      goBack,
      formatFullDate,
      formatContent,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.email-view-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 80px);
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

/* 头部导航 */
.email-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.back-btn {
  background-color: transparent;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.back-btn:hover {
  background-color: #f5f5f5;
  border-color: #bbb;
}

.back-arrow {
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-btn {
  background-color: transparent;
  border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.action-btn:hover {
  background-color: #f5f5f5;
}

.delete-btn:hover {
  background-color: #ffebee;
  color: #d32f2f;
  border-color: #ffcdd2;
}

/* 加载和错误状态 */
.loading-container,
.error-message {
  text-align: center;
  padding: 40px 0;
}

.error-message {
  color: #d32f2f;
}

.retry-btn {
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.retry-btn:hover {
  background-color: #3a5aef;
}

/* 邮件内容区域 */
.email-content-container {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.email-meta-info {
  margin-bottom: 30px;
}

.email-subject {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.sender-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 15px;
}

.sender-row,
.recipient-row,
.date-row {
  display: flex;
}

.meta-label {
  font-weight: 500;
  width: 80px;
  color: #666;
}

.meta-value {
  color: #333;
}

.email-content {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  padding: 20px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 30px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 附件区域 */
.attachments-section {
  margin-top: 30px;
}

.attachments-section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #555;
}

.attachment-list {
  list-style-type: none;
  padding: 0;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #f9f9f9;
}

.attachment-name {
  flex: 1;
  margin-left: 5px;
}

.attachment-size {
  font-size: 13px;
  color: #777;
  margin-right: 15px;
}

.download-btn {
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #3a5aef;
}

/* 删除确认对话框 */
.delete-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin-top: 0;
  color: #333;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn,
.confirm-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background-color: transparent;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  background-color: #f5f5f5;
}

.confirm-btn {
  background-color: #d32f2f;
  color: white;
  border: none;
}

.confirm-btn:hover {
  background-color: #c62828;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .email-view-container {
    padding: 10px;
  }
  
  .email-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .email-subject {
    font-size: 20px;
  }
  
  .meta-label {
    width: 70px;
    font-size: 14px;
  }
  
  .email-content {
    font-size: 15px;
  }
}
</style>




