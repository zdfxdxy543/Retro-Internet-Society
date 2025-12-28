<template>
  <div class="email-detail-container">
    <!-- 顶部导航栏 -->
    <div class="email-detail-header">
      <button class="back-btn" @click="goBack">
        <span class="back-arrow">←</span> 返回列表
      </button>
      <h1 class="page-title">邮件详情</h1>
      <div class="action-buttons">
        <button 
          class="action-btn reply"
          @click="replyEmail"
          :disabled="loading"
        >
          回复
        </button>
        <button 
          class="action-btn"
          @click="forwardEmail"
          :disabled="loading"
        >
          转发
        </button>
        <button 
          class="action-btn delete"
          @click="confirmDelete"
          :disabled="loading"
        >
          删除
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载邮件中...</div>
    </div>
    
    <!-- 邮件内容区域 -->
    <div v-else-if="email" class="email-content-wrapper">
      <div class="email-header-section">
        <div class="subject-line">
          <span v-if="email.starred" class="star-icon filled" @click="toggleStar">★</span>
          <span v-else class="star-icon" @click="toggleStar">☆</span>
          <h2 class="email-subject">{{ email.subject || '(无主题)' }}</h2>
        </div>
        
        <div class="meta-info">
          <div class="meta-item">
            <span class="meta-label">发件人:</span>
            <span class="meta-value">{{ email.sender_name || email.sender_email }}</span>
            <span class="meta-email"><{{ email.sender_email }}></span>
          </div>
          <div class="meta-item">
            <span class="meta-label">收件人:</span>
            <span class="meta-value">{{ email.recipient_name || email.recipient_email }}</span>
            <span class="meta-email"><{{ email.recipient_email }}></span>
          </div>
          <div class="meta-item" v-if="email.cc">
            <span class="meta-label">抄送:</span>
            <span class="meta-value">{{ email.cc }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">时间:</span>
            <span class="meta-value">{{ formatDate(email.created_at) }}</span>
          </div>
        </div>
        
        <div class="divider"></div>
      </div>
      
      <div class="email-body">
        <div v-html="formatEmailBody(email.content)"></div>
      </div>
      
      <!-- 附件区域 -->
      <div v-if="email.attachments && email.attachments.length > 0" class="email-attachments">
        <h3 class="attachments-title">附件 ({{ email.attachments.length }})</h3>
        <div class="attachments-list">
          <div 
            v-for="(attachment, index) in email.attachments" 
            :key="index"
            class="attachment-item"
          >
            <div class="attachment-icon">
              {{ getFileIcon(attachment.name) }}
            </div>
            <div class="attachment-info">
              <div class="attachment-name">{{ attachment.name }}</div>
              <div class="attachment-size">{{ formatFileSize(attachment.size) }}</div>
            </div>
            <button 
              class="download-btn"
              @click="downloadAttachment(attachment)"
            >
              下载
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-else class="error-container">
      <div class="error-icon">⚠️</div>
      <h3 class="error-title">无法加载邮件</h3>
      <p class="error-message">{{ errorMessage || '邮件可能已被删除或移动。' }}</p>
      <button class="primary-btn" @click="goBack">返回列表</button>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="confirm-dialog">
      <div class="confirm-content">
        <h3 class="confirm-title">确认删除此邮件？</h3>
        <p class="confirm-message">此操作无法撤销，邮件将被永久删除。</p>
        <div class="confirm-actions">
          <button class="cancel-btn" @click="closeConfirm">取消</button>
          <button 
            class="delete-btn" 
            @click="deleteEmail"
            :disabled="deleting"
          >
            {{ deleting ? '删除中...' : '删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import emailService from '../api/email.js';

export default {
  name: 'EmailDetail',
  props: {
    id: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    const loading = ref(true);
    const deleting = ref(false);
    const email = ref(null);
    const errorMessage = ref('');
    const showDeleteConfirm = ref(false);
    
    // 获取邮件ID
    const emailId = computed(() => {
      return props.id || route.params.id;
    });
    
    // 加载邮件详情
    const loadEmailDetail = async () => {
      if (!emailId.value) {
        errorMessage.value = '邮件ID无效';
        loading.value = false;
        return;
      }
      
      loading.value = true;
      errorMessage.value = '';
      
      try {
        // 加载邮件详情
        const response = await emailService.getEmailDetail(emailId.value);
        email.value = response;
        
        // 如果是未读邮件，自动标记为已读
        if (!email.value.read) {
          try {
            await emailService.markAsRead(emailId.value);
            email.value.read = true;
          } catch (error) {
            console.error('Failed to mark email as read:', error);
          }
        }
      } catch (error) {
        console.error('Failed to load email detail:', error);
        errorMessage.value = error.response?.data?.message || '加载邮件失败，请稍后重试';
      } finally {
        loading.value = false;
      }
    };
    
    // 处理星标状态
    const toggleStar = async () => {
      if (!email.value) return;
      
      try {
        await emailService.toggleStar(emailId.value);
        email.value.starred = !email.value.starred;
      } catch (error) {
        console.error('Failed to toggle star:', error);
      }
    };
    
    // 回复邮件
    const replyEmail = () => {
      if (!email.value) return;
      
      // 构建回复内容
      const replySubject = email.value.subject.startsWith('Re:') ? 
        email.value.subject : 
        `Re: ${email.value.subject}`;
      
      // 跳转到撰写邮件页面，并传递回复参数
      router.push({
        name: 'EmailCompose',
        query: {
          replyTo: email.value.sender_email,
          replyToName: email.value.sender_name || email.value.sender_email,
          subject: replySubject
        }
      });
    };
    
    // 转发邮件
    const forwardEmail = () => {
      if (!email.value) return;
      
      // 构建转发内容
      const forwardSubject = email.value.subject.startsWith('Fw:') ? 
        email.value.subject : 
        `Fw: ${email.value.subject}`;
      
      // 跳转到撰写邮件页面，并传递转发参数
      router.push({
        name: 'EmailCompose',
        query: {
          subject: forwardSubject
        }
      });
    };
    
    // 确认删除对话框
    const confirmDelete = () => {
      showDeleteConfirm.value = true;
    };
    
    // 关闭确认对话框
    const closeConfirm = () => {
      showDeleteConfirm.value = false;
    };
    
    // 删除邮件
    const deleteEmail = async () => {
      if (!emailId.value || deleting.value) return;
      
      deleting.value = true;
      
      try {
        await emailService.deleteEmail(emailId.value);
        // 删除成功后返回邮件列表
        router.push('/email/dashboard');
      } catch (error) {
        console.error('Failed to delete email:', error);
        showDeleteConfirm.value = false;
        // 显示错误提示
        alert('删除邮件失败，请稍后重试');
      } finally {
        deleting.value = false;
      }
    };
    
    // 下载附件
    const downloadAttachment = (attachment) => {
      // 这里应该调用API下载附件
      // 为简化示例，我们创建一个模拟下载功能
      alert(`下载附件: ${attachment.name}`);
    };
    
    // 返回列表
    const goBack = () => {
      router.back();
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      const now = new Date();
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
      
      // 根据时间差显示不同格式
      if (diffDays === 0) {
        // 今天
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      } else if (diffDays === 1) {
        // 昨天
        return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
      } else if (diffDays < 7) {
        // 一周内
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        return `${weekdays[date.getDay()]} ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
      } else {
        // 其他
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    };
    
    // 格式化邮件内容
    const formatEmailBody = (content) => {
      if (!content) return '';
      // 简单处理：将换行符转换为HTML换行
      return content.replace(/\n/g, '<br>');
    };
    
    // 获取文件图标
    const getFileIcon = (filename) => {
      const extension = filename.split('.').pop().toLowerCase();
      
      switch (extension) {
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
          return '🖼️';
        case 'pdf':
          return '📄';
        case 'doc':
        case 'docx':
          return '📝';
        case 'xls':
        case 'xlsx':
          return '📊';
        case 'zip':
        case 'rar':
          return '🗜️';
        default:
          return '📎';
      }
    };
    
    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (!bytes || bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // 组件挂载时加载邮件详情
    onMounted(() => {
      loadEmailDetail();
    });
    
    return {
      loading,
      email,
      errorMessage,
      showDeleteConfirm,
      deleting,
      toggleStar,
      replyEmail,
      forwardEmail,
      confirmDelete,
      closeConfirm,
      deleteEmail,
      downloadAttachment,
      goBack,
      formatDate,
      formatEmailBody,
      getFileIcon,
      formatFileSize
    };
  }
};
</script>

<style scoped>
.email-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 80px);
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

/* 顶部导航栏 */
.email-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 30px;
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

.page-title {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-btn {
  background-color: transparent;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.action-btn:hover {
  background-color: #f5f5f5;
  border-color: #bbb;
}

.action-btn.reply {
  background-color: #4a6bff;
  color: white;
  border-color: #4a6bff;
}

.action-btn.reply:hover {
  background-color: #3a5aef;
}

.action-btn.delete {
  border-color: #e53935;
  color: #e53935;
}

.action-btn.delete:hover {
  background-color: #ffebed;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4a6bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #666;
}

/* 邮件内容 */
.email-content-wrapper {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.email-header-section {
  margin-bottom: 24px;
}

.subject-line {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.star-icon {
  font-size: 20px;
  color: #ddd;
  cursor: pointer;
  margin-right: 8px;
}

.star-icon.filled {
  color: #ffcc00;
}

.email-subject {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: flex-start;
  font-size: 15px;
}

.meta-label {
  font-weight: 500;
  color: #666;
  min-width: 70px;
}

.meta-value {
  font-weight: 500;
  color: #333;
}

.meta-email {
  color: #666;
  margin-left: 5px;
}

.divider {
  height: 1px;
  background-color: #eee;
  margin: 20px 0;
}

.email-body {
  padding: 20px 0;
  line-height: 1.6;
  font-size: 16px;
  color: #333;
}

.email-body :deep(p) {
  margin-bottom: 16px;
}

/* 附件区域 */
.email-attachments {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.attachments-title {
  font-size: 16px;
  color: #666;
  margin-top: 0;
  margin-bottom: 15px;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e1e8ed;
  transition: all 0.3s;
}

.attachment-item:hover {
  background-color: #edf2f7;
  border-color: #cbd5e0;
}

.attachment-icon {
  font-size: 24px;
  margin-right: 12px;
}

.attachment-info {
  flex: 1;
  min-width: 0; /* 允许内容自动截断 */
}

.attachment-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.attachment-size {
  font-size: 13px;
  color: #666;
  margin-top: 2px;
}

.download-btn {
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #3a5aef;
}

/* 错误提示 */
.error-container {
  text-align: center;
  padding: 60px 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-title {
  font-size: 20px;
  color: #333;
  margin-top: 0;
  margin-bottom: 10px;
}

.error-message {
  color: #666;
  margin-bottom: 20px;
}

.primary-btn {
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.primary-btn:hover {
  background-color: #3a5aef;
}

/* 确认对话框 */
.confirm-dialog {
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

.confirm-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirm-title {
  margin-top: 0;
  color: #333;
  font-size: 18px;
}

.confirm-message {
  color: #666;
  margin-bottom: 20px;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background-color: #f5f5f5;
  border-color: #bbb;
}

.delete-btn {
  padding: 8px 16px;
  border: 1px solid #e53935;
  background-color: #e53935;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.delete-btn:hover {
  background-color: #c62828;
}

.delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .email-detail-container {
    padding: 10px;
  }
  
  .email-detail-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .action-buttons {
    justify-content: space-between;
  }
  
  .action-btn {
    flex: 1;
    font-size: 13px;
    padding: 8px 10px;
  }
  
  .meta-item {
    flex-direction: column;
    gap: 4px;
  }
  
  .meta-label {
    min-width: auto;
  }
  
  .attachment-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .download-btn {
    align-self: flex-end;
  }
  
  .confirm-actions {
    flex-direction: column-reverse;
  }
  
  .cancel-btn,
  .delete-btn {
    width: 100%;
  }
}
</style>



