import axios from 'axios'

/**
 * 下载网盘文件
 * @param {string} share_id - 分享号
 * @param {string} password - 密码
 * @returns {Promise<Object>} - 包含下载结果的Promise
 */
export const downloadDiskFile = async (share_id, password) => {
  try {
    // 设置响应类型为blob以处理二进制文件
    const response = await axios.post('/api/disk/download', {
      share_id,
      password
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      responseType: 'blob' // 明确设置响应类型为二进制数据
    })
    
    if (response.status === 200) {
      // 处理成功的文件下载响应
      const contentType = response.headers['content-type']
      const contentDisposition = response.headers['content-disposition']
      
      // 提取文件名
      let fileName = 'download_file'
      if (contentDisposition) {
        // 尝试匹配现代浏览器的文件名格式
        const fileNameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-8''|)([^;\r\n'"]+)['"]?/)
        if (fileNameMatch && fileNameMatch[1]) {
          fileName = decodeURIComponent(fileNameMatch[1])
        } else {
          // 尝试匹配传统格式
          const legacyMatch = contentDisposition.match(/filename=['"]([^'"]+)['"]/)
          if (legacyMatch && legacyMatch[1]) {
            fileName = legacyMatch[1]
          } else {
            // 匹配不带引号的格式
            const simpleMatch = contentDisposition.match(/filename=(.*)/)
            if (simpleMatch && simpleMatch[1]) {
              fileName = simpleMatch[1].trim()
            }
          }
        }
      }
      
      // 确保文件名有扩展名
      if (!fileName.includes('.')) {
        // 根据content-type猜测扩展名
        const extMap = {
          'text/plain': '.txt',
          'text/html': '.html',
          'application/pdf': '.pdf',
          'application/msword': '.doc',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
          'application/vnd.ms-excel': '.xls',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
          'application/vnd.ms-powerpoint': '.ppt',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
          'image/jpeg': '.jpg',
          'image/png': '.png',
          'image/gif': '.gif',
          'application/zip': '.zip',
          'application/x-rar-compressed': '.rar',
          'application/json': '.json'
        }
        
        const ext = extMap[contentType] || '.bin'
        fileName += ext
      }
      
      // 转换为Blob对象并创建下载URL
      const blob = new Blob([response.data], { type: contentType })
      const downloadUrl = window.URL.createObjectURL(blob)
      
      // 创建并触发下载链接
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = fileName
      link.style.display = 'none'  // 隐藏链接
      
      document.body.appendChild(link)
      link.click()
      
      // 清理资源 - 增加延迟时间，确保浏览器有足够时间处理下载
      setTimeout(() => {
        try {
          document.body.removeChild(link)
          window.URL.revokeObjectURL(downloadUrl)
        } catch (e) {
          console.error('清理下载资源时出错:', e)
        }
      }, 1000)
      
      return {
        success: true,
        message: '文件下载成功',
        fileName
      }
    } else {
      // 处理非200状态码的响应
      return new Promise((resolve) => {
        // 尝试将响应数据解析为JSON错误信息
        const reader = new FileReader()
        reader.onload = () => {
          try {
            const errorData = JSON.parse(reader.result)
            resolve({
              success: false,
              message: errorData.message || `下载失败：${response.status}`
            })
          } catch (e) {
            resolve({
              success: false,
              message: `下载失败：${response.status}`
            })
          }
        }
        reader.readAsText(response.data)
      })
    }
  } catch (error) {
    // 处理异常
    if (error.response) {
      // 服务器返回错误响应
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = () => {
          try {
            const errorData = JSON.parse(reader.result)
            resolve({
              success: false,
              message: errorData.message || '下载失败'
            })
          } catch (e) {
            resolve({
              success: false,
              message: `下载失败：${error.response.status}`
            })
          }
        }
        reader.readAsText(error.response.data)
      })
    } else if (error.request) {
      // 请求已发送但没有收到响应
      return {
        success: false,
        message: '网络错误，请检查网络连接'
      }
    } else {
      // 请求配置错误
      return {
        success: false,
        message: error.message || '下载失败'
      }
    }
  }
}