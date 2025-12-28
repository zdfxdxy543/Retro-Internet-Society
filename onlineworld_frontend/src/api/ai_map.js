import request from './request.js'

// AI地图API请求模块
export default {
  // 获取AI地图首页数据
  getMapIndex() {
    return request({
      url: '/api/ai-map/',
      method: 'get'
    })
  },
  
  // 获取区域详情
  getMapRegionDetail(regionId) {
    return request({
      url: `/api/ai-map/region/${regionId}`,
      method: 'get'
    })
  },
  
  // 获取AI详情
  getAIDetail(aiId) {
    return request({
      url: `/api/ai-map/ai/${aiId}`,
      method: 'get'
    })
  }
}
