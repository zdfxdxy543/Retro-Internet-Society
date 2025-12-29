import request from './request.js'

// 公司网站API请求模块
export default {
  // 获取公司首页数据
  getCompanyIndex() {
    return request({
      url: '/api/company/',
      method: 'get'
    })
  },
  
  // 获取产品列表
  getProducts(categoryId = null) {
    let url = '/api/company/products'
    if (categoryId) {
      url += `/category/${categoryId}`
    }
    return request({
      url: url,
      method: 'get'
    })
  },
  
  // 获取产品详情
  getProductDetail(productId) {
    return request({
      url: `/api/company/product/${productId}`,
      method: 'get'
    })
  },
  
  // 获取关于我们信息
  getAbout() {
    return request({
      url: '/api/company/about',
      method: 'get'
    })
  },
  
  // 获取联系我们信息
  getContact() {
    return request({
      url: '/api/company/contact',
      method: 'get'
    })
  },
  
  // 生成产品DataSheet
  generateProductDatasheet(productId) {
    return request({
      url: `/api/datasheet/generate/${productId}`,
      method: 'post'
    })
  },
  
  // 下载产品DataSheet
  downloadProductDatasheet(productId) {
    return request({
      url: `/api/datasheet/download/${productId}`,
      method: 'get',
      responseType: 'blob'  // 重要：设置响应类型为blob，用于下载文件
    })
  }
}