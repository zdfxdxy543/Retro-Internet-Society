// 商城相关API
import request from './request'

// 获取商城首页数据
export function getShopIndex() {
  return request.get('/api/shop/home')
}

// 获取所有分类
export function getCategories() {
  return request.get('/api/shop/categories')
}

// 获取所有商家
export function getMerchants() {
  return request.get('/api/shop/merchants')
}

// 获取商家详情
export function getMerchantDetail(id) {
  return request.get(`/api/shop/merchants/${id}`)
}

// 获取商品列表
export function getProducts(params) {
  return request.get('/api/shop/products', { params })
}

// 获取商品详情
export function getProductDetail(id) {
  return request.get(`/api/shop/products/${id}`)
}



// 获取分类商品
export function getCategoryProducts(categoryId, params) {
  return request.get(`/api/shop/categories/${categoryId}/products`, { params })
}
