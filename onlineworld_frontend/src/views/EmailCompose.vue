<template>
  <div class="email-compose-container">
    <!-- 顶部导航栏 -->
    <div class="email-compose-header">
      <button class="back-btn" @click="goBack">
        <span class="back-arrow">←</span> {{ isReply ? '返回邮件' : '返回列表' }}
      </button>
      <h1 class="page-title">{{ isReply ? '回复邮件' : '撰写邮件' }}</h1>
      <button 
        class="send-btn" 
        @click="sendEmail"
        :disabled="sending || !isFormValid"
      >
        {{ sending ? '发送中...' : '发送' }}
      </button>
    </div>
    
    <!-- 邮件撰写表单 -->
    <form class="compose-form" @submit.prevent="sendEmail">
      <!-- 收件人 -->
      <div class="form-group">
        <label for="recipient">收件人 *</label>
        <input 
          type="email" 
          id="recipient" 
          v-model="email.recipient"
          placeholder="输入收件人邮箱地址"
          :class="{ 'error': errors.recipient }"
          @blur="validateField('recipient')"
        />
        <div v-if="errors.recipient" class="error-message">{{ errors.recipient }}</div>
      </div>
      
      <!-- 抄送 (可选功能) -->
      <div class="form-group optional-field">
        <label for="cc">抄送 (可选)</label>
        <input 
          type="text" 
          id="cc" 
          v-model="email.cc"
          placeholder="多个地址请用逗号分隔"
        />
      </div>
      
      <!-- 主题 -->
      <div class="form-group">
        <label for="subject">主题 *</label>
        <input 
          type="text" 
          id="subject" 
          v-model="email.subject"
          placeholder="输入邮件主题"
          :class="{ 'error': errors.subject }"
          @blur="validateField('subject')"
        />
        <div v-if="errors.subject" class="error-message">{{ errors.subject }}</div>
      </div>
      
      <!-- 正文 -->
      <div class="form-group">
        <label for="content">正文 *</label>
        <textarea 
          id="content" 
          v-model="email.content"
          placeholder="输入邮件内容"
          rows="12"
          :class="{ 'error': errors.content }"
          @blur="validateField('content')"
        ></textarea>
        <div v-if="errors.content" class="error-message">{{ errors.content }}</div>
      </div>
      
      <!-- 附件上传 (可选功能) -->
      <div class="form-group optional-field">
        <label for="attachment">附件 (可选)</label>
        <div class="attachment-container">
          <input 
            type="file" 
            id="attachment" 
            style="display: none"
            @change="handleFileSelect"
            multiple
          />
          <button 
            type="button" 
            class="attach-btn"
            @click="triggerFileUpload"
          >
            📎 添加附件
          </button>
          <p class="attach-hint">支持jpg, png, pdf, doc等格式，单文件最大20MB</p>
        </div>
        
        <!-- 已选附件列表 -->
        <div v-if="attachments.length > 0" class="attachment-list">
          <div 
            v-for="(file, index) in attachments" 
            :key="index" 
            class="attachment-item"
          >
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
            <button 
              type="button" 
              class="remove-btn"
              @click="removeAttachment(index)"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </form>
    
    <!-- 发送成功提示 -->
    <div v-if="showSuccess" class="success-modal">
      <div class="success-content">
        <div class="success-icon">✓</div>
        <h2>邮件已发送成功！</h2>
        <div class="success-actions">
          <button class="action-btn" @click="composeNew">写新邮件</button>
          <button class="action-btn primary" @click="goToSent">查看发件箱</button>
        </div>
      </div>
    </div>
    
    <!-- 错误提示对话框 -->
    <div v-if="errorDialog.show" class="error-dialog">
      <div class="dialog-content">
        <h3>发送失败</h3>
        <p>{{ errorDialog.message }}</p>
        <button class="ok-btn" @click="errorDialog.show = false">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import emailService from '../api/email.js'

export default {
  name: 'EmailCompose',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 状态管理
    const sending = ref(false)
    const showSuccess = ref(false)
    const attachments = ref([])
    
    // 邮件数据
    const email = ref({
      recipient: '',
      cc: '',
      subject: '',
      content: ''
    })
    
    // 错误信息
    const errors = ref({
      recipient: '',
      subject: '',
      content: ''
    })
    
    // 错误对话框
    const errorDialog = ref({
      show: false,
      message: ''
    })
    
    // 判断是否为回复邮件
    const isReply = computed(() => {
      return !!route.query.replyTo
    })
    
    // 表单验证
    const isFormValid = computed(() => {
      return (
        email.value.recipient.trim() && 
        email.value.subject.trim() && 
        email.value.content.trim() &&
        !errors.value.recipient && 
        !errors.value.subject && 
        !errors.value.content
      )
    })
    
    // 邮箱格式验证
    const isValidEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }
    
    // 验证单个字段
    const validateField = (fieldName) => {
      switch (fieldName) {
        case 'recipient':
          if (!email.value.recipient.trim()) {
            errors.value.recipient = '收件人不能为空'
          } else if (!isValidEmail(email.value.recipient.trim())) {
            errors.value.recipient = '请输入有效的邮箱地址'
          } else {
            errors.value.recipient = ''
          }
          break
          
        case 'subject':
          if (!email.value.subject.trim()) {
            errors.value.subject = '主题不能为空'
          } else {
            errors.value.subject = ''
          }
          break
          
        case 'content':
          if (!email.value.content.trim()) {
            errors.value.content = '邮件内容不能为空'
          } else {
            errors.value.content = ''
          }
          break
      }
    }
    
    // 验证整个表单
    const validateForm = () => {
      validateField('recipient')
      validateField('subject')
      validateField('content')
      
      // 如果有附件，验证文件大小
      for (const file of attachments.value) {
        if (file.size > 20 * 1024 * 1024) { // 20MB
          errorDialog.value = {
            show: true,
            message: `文件 "${file.name}" 超过了20MB的限制`
          }
          return false
        }
      }
      
      return isFormValid.value
    }
    
    // 处理路由参数，自动填充回复信息
    const handleRouteParams = () => {
      const { replyTo, replyToName, subject, content } = route.query
      
      if (replyTo) {
        email.value.recipient = replyTo
        // 如果有发件人名称，在收件人字段显示
        if (replyToName) {
          email.value.recipient = `${replyToName} <${replyTo}>`
        }
      }
      
      // 为回复邮件的主题添加"Re:"前缀
      if (subject) {
        // 避免重复添加Re:
        if (!subject.trim().toLowerCase().startsWith('re:')) {
          email.value.subject = `Re: ${subject}`
        } else {
          email.value.subject = subject
        }
        
        // 如果有原始内容，在正文中引用
        if (content) {
          const quotedContent = content.split('\n').map(line => `> ${line}`).join('\n')
          const now = new Date().toLocaleString()
          email.value.content = `\n\n--- 原始邮件 ---\n时间: ${now}\n发件人: ${replyToName || replyTo}\n主题: ${subject}\n\n${quotedContent}\n\n\n`
        }
      }
    }
    
    // 发送邮件
    const sendEmail = async () => {
      // 表单验证
      if (!validateForm()) return
      
      loading.value = true
      
      try {
        // 构建邮件数据
        const emailData = {
          recipient_email: emailForm.recipient,
          subject: emailForm.subject,
          content: emailForm.content,
          attachments: attachments.value
        }
        
        // 如果是回复邮件，添加回复信息
        if (replyInfo.value) {
          emailData.reply_to = replyInfo.value.reference
          emailData.reply_to_name = replyInfo.value.replyToName
        }
        
        // 调用发送邮件API
        await emailService.sendEmail(emailData)
        
        // 发送成功，保存当前标签页状态并重定向到邮件列表
        localStorage.setItem('emailLastTab', 'sent')
        
        // 显示成功提示
        successMessage.value = '邮件发送成功'
        
        // 延迟1秒后跳转
        setTimeout(() => {
          router.push('/email/dashboard?tab=sent')
        }, 1000)
      } catch (err) {
        console.error('发送邮件失败:', err)
        errorMessage.value = err.response?.data?.message || '发送邮件失败，请稍后重试'
        
        // 移除401错误处理，登录状态验证统一由路由守卫处理
      } finally {
        loading.value = false
      }
    }
    
    // 触发文件上传
    const triggerFileUpload = () => {
      document.getElementById('attachment').click()
    }
    
    // 处理文件选择
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      if (files.length > 0) {
        attachments.value = [...attachments.value, ...files]
        // 清空input以允许重复上传同一文件
        event.target.value = ''
      }
    }
    
    // 移除附件
    const removeAttachment = (index) => {
      attachments.value.splice(index, 1)
    }
    
    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    // 返回上一页
    const goBack = () => {
      if (isReply) {
        // 如果是回复，返回邮件详情
        router.back()
      } else {
        // 如果是新邮件，返回邮箱列表
        router.push('/email/dashboard')
      }
    }
    
    // 撰写新邮件
    const composeNew = () => {
      showSuccess.value = false
      email.value = {
        recipient: '',
        cc: '',
        subject: '',
        content: ''
      }
      attachments.value = []
      errors.value = {
        recipient: '',
        subject: '',
        content: ''
      }
    }
    
    // 跳转到发件箱
    const goToSent = () => {
      router.push('/email/dashboard?tab=sent')
    }
    
    // 监听路由参数变化
    watch(() => route.query, (newQuery) => {
      handleRouteParams()
    }, { immediate: true })
    
    // 组件挂载时
    onMounted(() => {
      handleRouteParams()
    })
    
    return {
      email,
      sending,
      showSuccess,
      attachments,
      errors,
      errorDialog,
      isReply,
      isFormValid,
      sendEmail,
      triggerFileUpload,
      handleFileSelect,
      removeAttachment,
      formatFileSize,
      goBack,
      composeNew,
      goToSent,
      validateField
    }
  }
}
</script>

<style scoped>
.email-compose-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 80px);
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

/* 顶部导航栏 */
.email-compose-header {
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

.send-btn {
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.send-btn:hover:not(:disabled) {
  background-color: #3a5aef;
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 表单样式 */
.compose-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4a6bff;
  box-shadow: 0 0 0 2px rgba(74, 107, 255, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 200px;
  line-height: 1.5;
  font-family: inherit;
}

.form-group input.error,
.form-group textarea.error {
  border-color: #e53935;
}

.error-message {
  color: #e53935;
  font-size: 13px;
  margin-top: 5px;
}

.optional-field {
  opacity: 0.9;
}

/* 附件样式 */
.attachment-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attach-btn {
  background-color: transparent;
  border: 1px solid #ddd;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
  width: fit-content;
}

.attach-btn:hover {
  background-color: #f5f5f5;
  border-color: #bbb;
}

.attach-hint {
  margin: 5px 0 0;
  font-size: 12px;
  color: #888;
}

.attachment-list {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e1e8ed;
}

.file-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.file-size {
  color: #888;
  font-size: 13px;
  margin-left: 8px;
}

.remove-btn {
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 16px;
  margin-left: 10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.remove-btn:hover {
  background-color: #ffebed;
  color: #e53935;
}

/* 成功提示对话框 */
.success-modal {
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

.success-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  text-align: center;
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

.success-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #4caf50;
  color: white;
  font-size: 32px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 20px;
}

.success-content h2 {
  margin-top: 0;
  color: #333;
}

.success-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
  justify-content: center;
}

.action-btn {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  min-width: 120px;
}

.action-btn:not(.primary) {
  background-color: transparent;
  border: 1px solid #ddd;
  color: #555;
}

.action-btn:not(.primary):hover {
  background-color: #f5f5f5;
}

.action-btn.primary {
  background-color: #4a6bff;
  color: white;
  border: none;
}

.action-btn.primary:hover {
  background-color: #3a5aef;
}

/* 错误对话框 */
.error-dialog {
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

.dialog-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog-content h3 {
  margin-top: 0;
  color: #e53935;
}

.ok-btn {
  background-color: #4a6bff;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.3s;
}

.ok-btn:hover {
  background-color: #3a5aef;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .email-compose-container {
    padding: 10px;
  }
  
  .email-compose-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .send-btn {
    width: 100%;
  }
  
  .form-group input,
  .form-group textarea {
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  .success-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>



