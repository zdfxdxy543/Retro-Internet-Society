import axios from 'axios'

// 邮箱系统API服务
const emailService = {
  // ===================== 认证相关 API =====================
  
  /**
   * 用户注册
   * @param {Object} userData 用户数据（username, email, password）
   * @returns {Promise}
   */
  register(userData) {
    return axios.post('/email/register', userData)
  },
  
  /**
   * 用户登录
   * @param {Object} credentials 登录凭据（username, password）
   * @returns {Promise}
   */
  login(credentials) {
    return axios.post('/email/login', credentials)
  },
  
  /**
   * 用户登出
   * @returns {Promise}
   */
  logout() {
    return axios.post('/email/logout')
  },
  
  /**
   * 获取当前用户登录状态
   * @returns {Promise}
   */
  getStatus() {
    return axios.get('/email/status')
  },
  
  // ===================== 邮件操作相关 API =====================
  
  /**
   * 发送邮件
   * @param {Object} mailData 邮件数据（recipient_email, subject, content）
   * @returns {Promise}
   */
  sendEmail(mailData) {
    return axios.post('/email/send', mailData)
  },
  
  /**
   * 获取收件箱邮件列表
   * @param {Object} params 查询参数（page, per_page, is_starred, is_read）
   * @returns {Promise}
   */
  getInbox(params = {}) {
    return axios.get('/email/inbox', { params })
  },
  
  /**
   * 获取发件箱邮件列表
   * @param {Object} params 查询参数（page, per_page）
   * @returns {Promise}
   */
  getOutbox(params = {}) {
    return axios.get('/email/outbox', { params })
  },
  
  /**
   * 获取邮件详情
   * @param {Number} mailId 邮件ID
   * @returns {Promise}
   */
  getEmailDetail(mailId) {
    return axios.get(`/email/${mailId}`)
  },
  
  /**
   * 标记邮件为已读
   * @param {Number} mailId 邮件ID
   * @returns {Promise}
   */
  markEmailRead(mailId) {
    return axios.put(`/email/${mailId}/mark-read`)
  },
  
  /**
   * 标记/取消标记邮件星标
   * @param {Number} mailId 邮件ID
   * @param {Boolean} isStarred 是否标记星标
   * @returns {Promise}
   */
  markEmailStarred(mailId, isStarred) {
    return axios.put(`/email/${mailId}/mark-starred`, { is_starred: isStarred })
  },
  
  /**
   * 删除邮件（软删除）
   * @param {Number} mailId 邮件ID
   * @returns {Promise}
   */
  deleteEmail(mailId) {
    return axios.delete(`/email/${mailId}/delete`)
  },
  
  // ===================== 用户信息相关 API =====================
  
  /**
   * 获取当前用户个人资料
   * @returns {Promise}
   */
  getProfile() {
    return axios.get('/email/user/profile')
  },
  
  /**
   * 更新用户个人资料
   * @param {Object} profileData 个人资料数据（display_name, avatar_url等）
   * @returns {Promise}
   */
  updateProfile(profileData) {
    return axios.put('/email/user/profile', profileData)
  },
  
  /**
   * 修改密码
   * @param {Object} passwordData 密码数据（old_password, new_password）
   * @returns {Promise}
   */
  changePassword(passwordData) {
    return axios.put('/email/user/change-password', passwordData)
  },
}

export default emailService
